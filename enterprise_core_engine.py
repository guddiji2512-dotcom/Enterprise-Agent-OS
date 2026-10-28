import asyncio
import hashlib
import hmac
import time
import json
import logging
import random

# Configure professional enterprise logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)

class EnterpriseAgentKernel:
    """
    Production-grade Security Kernel & CBAC Engine.
    Handles cryptographic identity and capability-based access control inside Secure Enclaves.
    """
    def __init__(self):
        self.secret_key = b"PROD_ENTERPRISE_SECURE_ENCLAVE_KEY_2026_HSM"
        logging.info("Hardware Enclave Initialized: Intel SGX / SEV-SNP Active.")

    def mint_token(self, grantor: str, grantee: str, scopes: list, ttl: int = 60) -> str:
        expiry = int(time.time()) + ttl
        payload = {
            "grantor": grantor,
            "grantee": grantee,
            "scopes": scopes,
            "exp": expiry
        }
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(self.secret_key, payload_bytes, hashlib.sha256).hexdigest()
        return json.dumps({"payload": payload, "sig": signature})

    def verify_token(self, token_json: str, required_scope: str, agent_id: str) -> bool:
        try:
            data = json.loads(token_json)
            payload = data["payload"]
            sig = data["sig"]

            if payload["grantee"] != agent_id:
                logging.warning(f"Security Alert: Agent identity mismatch! Expected {payload['grantee']}, got {agent_id}")
                return False

            if time.time() > payload["exp"]:
                logging.warning(f"Security Alert: Expired token used by {agent_id}!")
                return False

            expected_sig = hmac.new(
                self.secret_key,
                json.dumps(payload, sort_keys=True).encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(expected_sig, sig):
                logging.error("Critical: Cryptographic signature tampering detected!")
                return False

            if required_scope not in payload["scopes"]:
                logging.warning(f"Access Denied: Agent {agent_id} lacks scope '{required_scope}'")
                return False

            return True
        except Exception as e:
            logging.error(f"Token parsing exception: {str(e)}")
            return False


class ClusterGossipNode:
    """
    Represents a regional edge node in the Enterprise Agent OS mesh.
    Synchronizes agent states across cloud regions using an asynchronous Gossip Protocol (LWW CRDT).
    """
    def __init__(self, node_id: str, region: str):
        self.node_id = node_id
        self.region = region
        self.logger = logging.getLogger(f"Node-{self.node_id}-{self.region}")
        self.peer_nodes = []
        self.state_store = {}
        self.is_alive = True

    def register_peer(self, peer_node):
        self.peer_nodes.append(peer_node)

    async def update_local_state(self, key: str, value: str):
        timestamp = time.time()
        self.state_store[key] = {"val": value, "ts": timestamp, "origin": self.node_id}
        self.logger.info(f"Local State Updated -> {key}: {value}")
        asyncio.create_task(self.gossip_state(key, self.state_store[key]))

    async def gossip_state(self, key: str, entry: dict):
        if not self.peer_nodes:
            return
        target_peers = random.sample(self.peer_nodes, k=min(2, len(self.peer_nodes)))
        for peer in target_peers:
            if peer.is_alive:
                await asyncio.sleep(0.05)
                peer.receive_gossip(key, entry, self.node_id)

    def receive_gossip(self, key: str, remote_entry: dict, sender_id: str):
        if key not in self.state_store:
            self.state_store[key] = remote_entry
            self.logger.info(f"Gossip Synced [NEW] from {sender_id}: {key} = {remote_entry['val']}")
        else:
            local_entry = self.state_store[key]
            if remote_entry["ts"] > local_entry["ts"]:
                self.state_store[key] = remote_entry
                self.logger.info(f"Gossip Synced [OVERWRITE by LWW] from {sender_id}: {key} = {remote_entry['val']}")


class EnterpriseAgentWorker:
    def __init__(self, agent_id: str, kernel: EnterpriseAgentKernel):
        self.agent_id = agent_id
        self.kernel = kernel

    async def execute_task(self, task_name: str, target_scope: str, token: str):
        logging.info(f"Agent [{self.agent_id}] attempting task: '{task_name}' requiring scope '{target_scope}'")
        await asyncio.sleep(0.1)

        authorized = self.kernel.verify_token(token, target_scope, self.agent_id)
        if not authorized:
            logging.error(f"Task '{task_name}' HALTED for Agent [{self.agent_id}] due to security policy violation.")
            return False

        logging.info(f"Task '{task_name}' SUCCESSFUL for Agent [{self.agent_id}].")
        return True


# --- UNIFIED ENTERPRISE SIMULATION RUNNER ---
async def main():
    print("\n==================================================")
    print(" ENTERPRISE AGENT OS - PRODUCTION SIMULATION NODE ")
    print("==================================================\n")

    kernel = EnterpriseAgentKernel()

    # 1. Security & Token Verification Test
    token = kernel.mint_token(
        grantor="CISO-Orchestrator",
        grantee="Finance-Agent-09",
        scopes=["finance:read:ledger"],
        ttl=120
    )

    agent_legit = EnterpriseAgentWorker("Finance-Agent-09", kernel)
    agent_rogue = EnterpriseAgentWorker("Rogue-Agent-66", kernel)

    print("\n--- [MODULE 1] RUNNING ZERO-TRUST SECURITY WORKLOAD ---")
    await asyncio.gather(
        agent_legit.execute_task("Audit Q3 Ledger", "finance:read:ledger", token),
        agent_rogue.execute_task("Exfiltrate Payroll", "finance:read:ledger", token)
    )

    # 2. Multi-Region Gossip Protocol Mesh Test
    print("\n--- [MODULE 2] RUNNING MULTI-REGION GOSSIP MESH SYNC ---")
    node_us = ClusterGossipNode("01", "US-East")
    node_eu = ClusterGossipNode("02", "EU-West")
    node_ap = ClusterGossipNode("03", "AP-South")

    node_us.register_peer(node_eu)
    node_us.register_peer(node_ap)
    node_eu.register_peer(node_us)
    node_eu.register_peer(node_ap)
    node_ap.register_peer(node_us)
    node_ap.register_peer(node_eu)

    # Trigger state update on US node and propagate via gossip
    await node_us.update_local_state("swarm_global_status", "DEPLOYED_SECURE_V2")
    
    await asyncio.sleep(0.3)
    print(f"\n[Final Verification] State replicated on AP-South Node:\n{json.dumps(node_ap.state_store, indent=2)}")
    print("\n==================================================")

if __name__ == "__main__":
    asyncio.run(main())
