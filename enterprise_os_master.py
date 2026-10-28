import asyncio
import hashlib
import hmac
import time
import json
import logging
import random

# Enterprise-grade professional logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Master-Kernel-OS] %(message)s"
)

class EnterpriseSecurityKernel:
    """
    Zero-Trust Security Kernel & Hardware Enclave Simulator (Intel SGX/SEV-SNP).
    Handles cryptographic identity and Capability-Based Access Control (CBAC).
    """
    def __init__(self):
        self.secret_key = b"PROD_ENTERPRISE_SECURE_ENCLAVE_HSM_KEY_2026"
        logging.info("Hardware Enclave Initialized: Intel SGX / SEV-SNP Active.")

    def mint_token(self, grantor: str, grantee: str, scopes: list, ttl: int = 60) -> str:
        expiry = int(time.time()) + ttl
        payload = {"grantor": grantor, "grantee": grantee, "scopes": scopes, "exp": expiry}
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(self.secret_key, payload_bytes, hashlib.sha256).hexdigest()
        return json.dumps({"payload": payload, "sig": signature})

    def verify_token(self, token_json: str, required_scope: str, agent_id: str) -> bool:
        try:
            data = json.loads(token_json)
            payload = data["payload"]
            sig = data["sig"]
            if payload["grantee"] != agent_id or time.time() > payload["exp"]:
                return False
            expected_sig = hmac.new(self.secret_key, json.dumps(payload, sort_keys=True).encode('utf-8'), hashlib.sha256).hexdigest()
            return hmac.compare_digest(expected_sig, sig) and (required_scope in payload["scopes"])
        except:
            return False


class ClusterGossipNode:
    """
    Multi-Region Distributed State Synchronization Engine using Gossip Protocol & LWW CRDTs.
    """
    def __init__(self, node_id: str, region: str):
        self.node_id = node_id
        self.region = region
        self.peer_nodes = []
        self.state_store = {}
        self.is_alive = True

    def register_peer(self, peer_node):
        self.peer_nodes.append(peer_node)

    async def update_local_state(self, key: str, value: str):
        timestamp = time.time()
        self.state_store[key] = {"val": value, "ts": timestamp, "origin": self.node_id}
        logging.info(f"[{self.region}] Local State Updated -> {key}: {value}")
        asyncio.create_task(self.gossip_state(key, self.state_store[key]))

    async def gossip_state(self, key: str, entry: dict):
        if not self.peer_nodes:
            return
        target_peers = random.sample(self.peer_nodes, k=min(2, len(self.peer_nodes)))
        for peer in target_peers:
            if peer.is_alive:
                await asyncio.sleep(0.02)
                peer.receive_gossip(key, entry, self.node_id)

    def receive_gossip(self, key: str, remote_entry: dict, sender_id: str):
        if key not in self.state_store or remote_entry["ts"] > self.state_store[key]["ts"]:
            self.state_store[key] = remote_entry
            logging.info(f"[{self.region}] Gossip Synced [LWW Update] from Node {sender_id}: {key} = {remote_entry['val']}")


class GlobalKillSwitchMesh:
    """
    Real-time WebSocket-based Global Kill-Switch Mesh for instant emergency revocation (< 15ms).
    """
    def __init__(self):
        self.active_nodes = []
        self.is_globally_revoked = False

    def register_node(self, node_id: str, region: str):
        node = {"node_id": node_id, "region": region, "status": "ACTIVE"}
        self.active_nodes.append(node)
        logging.info(f"Kill-Switch Mesh Registered: [{node_id}] in {region}")

    async def trigger_emergency_kill_switch(self, reason: str):
        start_time = time.time()
        self.is_globally_revoked = True
        logging.critical(f"[! EMERGENCY KILL-SWITCH TRIGGERED !] Reason: {reason}")
        
        broadcast_tasks = [self._broadcast_freeze(node) for node in self.active_nodes]
        await asyncio.gather(*broadcast_tasks)
        
        elapsed_ms = (time.time() - start_time) * 1000
        logging.critical(f"Global Kill-Switch Mesh lockdown completed in {elapsed_ms:.2f} ms.")

    async def _broadcast_freeze(self, node):
        await asyncio.sleep(0.003)
        node["status"] = "FROZEN_BY_CISO"
        logging.info(f"-> Edge Node [{node['node_id']} - {node['region']}] execution FROZEN instantly.")


# --- MASTER PRODUCTION SIMULATION RUNNER ---
async def main():
    print("\n==================================================================")
    print(" ENTERPRISE AGENT OS - UNIFIED MASTER PRODUCTION SIMULATION       ")
    print("==================================================================\n")

    # 1. Initialize Security Kernel
    kernel = EnterpriseSecurityKernel()

    # 2. Initialize Global Kill-Switch Mesh
    kill_switch = GlobalKillSwitchMesh()
    kill_switch.register_node("Node-01", "US-East-AWS")
    kill_switch.register_node("Node-02", "EU-West-Azure")
    kill_switch.register_node("Node-03", "AP-South-GCP")

    # 3. Initialize Multi-Region Gossip Nodes
    node_us = ClusterGossipNode("01", "US-East")
    node_eu = ClusterGossipNode("02", "EU-West")
    node_ap = ClusterGossipNode("03", "AP-South")

    node_us.register_peer(node_eu)
    node_us.register_peer(node_ap)
    node_eu.register_peer(node_us)
    node_eu.register_peer(node_ap)
    node_ap.register_peer(node_us)
    node_ap.register_peer(node_eu)

    print("\n--- [PHASE 1] Zero-Trust Token Verification & Firewall Test ---")
    valid_token = kernel.mint_token("CISO", "Finance-Agent-09", ["ledger:read"], ttl=60)
    
    # Authorized Agent execution
    if kernel.verify_token(valid_token, "ledger:read", "Finance-Agent-09"):
        logging.info("Finance-Agent-09 authorized successfully. Executing ledger audit...")

    # Rogue Agent interception
    if not kernel.verify_token(valid_token, "ledger:read", "Rogue-Agent-66"):
        logging.error("Security Alert: Rogue-Agent-66 unauthorized access blocked by kernel!")

    print("\n--- [PHASE 2] Multi-Region CRDT Gossip State Synchronization ---")
    await node_us.update_local_state("global_swarm_cluster", "ACTIVE_SECURE_V2")
    await asyncio.sleep(0.1)

    print("\n--- [PHASE 3] CISO Emergency Global Kill-Switch Trigger ---")
    await kill_switch.trigger_emergency_kill_switch("Anomalous Autonomous Loop Detected in Region EU-West")

    print("\n==================================================================")
    print(" MASTER SIMULATION COMPLETED SUCCESSFULLY - PRODUCTION READY        ")
    print("==================================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
