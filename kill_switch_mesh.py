import asyncio
import json
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [KillSwitch-Mesh] %(message)s"
)

class GlobalKillSwitchMesh:
    """
    Simulates a real-time WebSocket-based Global Kill-Switch Mesh.
    Allows the CISO dashboard to broadcast an emergency cryptographic revocation signal 
    across all regional edge nodes instantly.
    """
    def __init__(self):
        self.active_nodes = []
        self.is_globally_revoked = False
        self.revocation_signature = None

    def register_node(self, node_id: str, region: str):
        node = {"node_id": node_id, "region": region, "status": "ACTIVE"}
        self.active_nodes.append(node)
        logging.info(f"Node Registered to Kill-Switch Mesh: [{node_id}] in {region}")

    async def trigger_emergency_kill_switch(self, reason: str):
        """
        Broadcasts instant revocation signal to all registered enterprise edge nodes.
        Target execution freeze time: < 15ms.
        """
        start_time = time.time()
        self.is_globally_revoked = True
        self.revocation_signature = f"SIG_REVOKE_{int(time.time())}_SECURE_HARDWARE"
        
        logging.critical(f"[! EMERGENCY KILL-SWITCH ACTIVATED !] Reason: {reason}")
        logging.critical(f"Broadcasting Revocation Token: {self.revocation_signature}")

        # Simulate concurrent broadcast to all edge nodes over WebSocket mesh
        broadcast_tasks = [self._broadcast_to_node(node) for node in self.active_nodes]
        await asyncio.gather(*broadcast_tasks)

        elapsed_ms = (time.time() - start_time) * 1000
        logging.critical(f"Global Kill-Switch propagation completed in {elapsed_ms:.2f} ms.")

    async def _broadcast_to_node(self, node):
        # Simulate network packet transmission time to edge nodes
        await asyncio.sleep(0.005) 
        node["status"] = "FROZEN_BY_KILL_SWITCH"
        logging.info(f"-> Node [{node['node_id']} - {node['region']}] acknowledged. Execution FROZEN.")


class EnterpriseEdgeWorkerNode:
    """
    Represents an edge worker checking the kill-switch mesh status before executing tasks.
    """
    def __init__(self, node_id: str, mesh: GlobalKillSwitchMesh):
        self.node_id = node_id
        self.mesh = mesh

    async def execute_agent_workload(self, task_name: str):
        logging.info(f"Node {self.node_id} checking security mesh before running task: '{task_name}'")
        
        # Check if global kill switch has been triggered
        if self.mesh.is_globally_revoked:
            logging.error(f"[BLOCKED] Node {self.node_id} rejected task '{task_name}'. Mesh is locked down!")
            return False
        
        logging.info(f"[SUCCESS] Node {self.node_id} executing task: '{task_name}'")
        return True


# --- RUNNING THE KILL-SWITCH SIMULATION ---
async def main():
    print("\n==================================================")
    print(" ENTERPRISE AGENT OS - GLOBAL KILL-SWITCH MESH     ")
    print("==================================================\n")

    mesh = GlobalKillSwitchMesh()

    # Register enterprise regional nodes
    mesh.register_node("Node-01", "US-East-AWS")
    mesh.register_node("Node-02", "EU-West-Azure")
    mesh.register_node("Node-03", "AP-South-GCP")

    node_us = EnterpriseEdgeWorkerNode("Node-01", mesh)

    print("\n--- PHASE 1: Normal Agent Execution (Pre-Emergency) ---")
    await node_us.execute_agent_workload("Fetch Q3 Inventory Analytics")

    print("\n--- PHASE 2: CISO Triggers Emergency Kill-Switch ---")
    # Simulating a runaway agent loop or security breach detection
    await mesh.trigger_emergency_kill_switch("Adversarial Prompt Injection Swarm Detected in Region EU-West")

    print("\n--- PHASE 3: Post-Lockdown Execution Attempt ---")
    await node_us.execute_agent_workload("Deploy Automated Code Patch")

    print("\n==================================================")

if __name__ == "__main__":
    asyncio.run(main())
