from yafs.selection import Selection
import numpy as np
import random

class AutonomicDRLSelector(Selection):
    """
    A custom YAFS selection policy that mimics an intelligent offloading decision.
    This version uses a simple heuristic based on node load.
    A full DRL integration would replace the `select_node` logic.
    """

    def __init__(self, name):
        super(AutonomicDRLSelector, self).__init__(name)
        # In a full implementation, we would load a trained DRL model here
        # self.model = SAC.load("sac_autonomic_fog.zip")
        print("AutonomicDRLSelector initialized (Heuristic mode).")

    def get_path(self, sim, app_name, message, source_node, dest_node, alloc_module, alloc_service):
        """
        This is the main function called by YAFS to decide where to send a message.
        """
        # Get all candidate nodes that host the alloc_service (ProcessingService)
        candidate_nodes = sim.alloc_DES[alloc_service] # e.g., [10, 11, 20]

        # --- Simple Heuristic: Choose the node with the shortest queue ---
        # This is a placeholder for the DRL agent's complex decision
        chosen_node = self.select_node(sim, candidate_nodes)

        # Get the shortest path from the source to the chosen node
        path = sim.topology.get_shortest_path(source_node, chosen_node)
        # print(f"DEBUG: Routing message from {source_node} to {chosen_node} via path {path}")
        return path

    def select_node(self, sim, candidate_nodes):
        """
        A simple heuristic selector. Replace this with a call to a DRL model.
        Objective: Choose the node with the least current workload (simplest metric).
        """
        best_node = None
        min_workload = float('inf')

        for node_id in candidate_nodes:
            # Get the current workload of the node (number of tasks in its queue)
            # This is a simplistic metric. A real state would include CPU, RAM, etc.
            node = sim.topology.get_node(node_id)
            current_workload = len(sim.get_DES_instances_list(node_id)) # Approx. queue length

            # Simple cost function: Prefer nodes with less workload
            # Cloud (id 20) has more power but higher latency, so we might penalize it
            cost = current_workload
            if node_id == 20: # Cloud node
                cost += 5 # Add a latency penalty

            if cost < min_workload:
                min_workload = cost
                best_node = node_id

        # print(f"DEBUG: Selected node {best_node} with estimated cost {min_workload}")
        return best_node