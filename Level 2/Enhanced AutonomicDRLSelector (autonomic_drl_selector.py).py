from yafs.selection import Selection
import numpy as np
from stable_baselines3 import SAC
import torch as th

class AutonomicDRLSelector(Selection):
    """
    A custom YAFS selection policy that uses a pre-trained SAC DRL agent
    to make intelligent offloading decisions.
    """

    def __init__(self, name, model_path="sac_fog_offload.zip"):
        super(AutonomicDRLSelector, self).__init__(name)
        self.model = None
        self.model_path = model_path
        self.load_model()  # Load the pre-trained model during initialization

    def load_model(self):
        """Loads the pre-trained SAC model from disk."""
        try:
            # It's crucial to define the same policy architecture as during training
            policy_kwargs = dict(activation_fn=th.nn.ReLU,
                                 net_arch=dict(pi=[64, 64], qf=[64, 64]))
            # Load the model
            self.model = SAC.load(self.model_path, policy_kwargs=policy_kwargs)
            print(f"[SUCCESS] Loaded pre-trained DRL model from {self.model_path}")
        except Exception as e:
            print(f"[ERROR] Could not load model from {self.model_path}. Error: {e}")
            print("Falling back to heuristic selection.")
            self.model = None

    def get_path(self, sim, app_name, message, source_node, dest_node, alloc_module, alloc_service):
        candidate_nodes = sim.alloc_DES[alloc_service] # e.g., [10, 11, 20]

        # Get the DRL agent's decision
        chosen_node_id = self.select_node(sim, candidate_nodes)

        # Map the agent's action (0,1,2) to the actual node ID in the topology
        # This mapping must be consistent with the training environment!
        # Action 0 -> Fog Node 10, Action 1 -> Fog Node 11, Action 2 -> Cloud Node 20
        node_id_map = {0: 10, 1: 11, 2: 20}
        chosen_node = node_id_map[chosen_node_id]

        path = sim.topology.get_shortest_path(source_node, chosen_node)
        # print(f"DRL Agent chose action {chosen_node_id} -> Node {chosen_node}. Path: {path}")
        return path

    def select_node(self, sim, candidate_nodes):
        """
        The core method. Constructs the state observation and queries the DRL model.
        """
        if self.model is None:
            # Fallback to heuristic if model failed to load
            return self._heuristic_fallback(sim, candidate_nodes)

        # 1. CONSTRUCT THE STATE VECTOR
        # This must match the observation space defined in FogOffloadEnv!
        # State: [CPU_Load_Fog1, RAM_Fog1, CPU_Load_Fog2, RAM_Fog2, Task_Size_Normalized]
        
        # -- Placeholder: Get state from simulator --
        # In a real implementation, you would query the Monitor for these values.
        # For this example, we use random values. INTEGRATING REAL MONITORING DATA IS YOUR NEXT KEY STEP.
        fog1_cpu = np.random.rand()
        fog1_ram = np.random.rand()
        fog2_cpu = np.random.rand()
        fog2_ram = np.random.rand()
        
        # Get the current task size from the message and normalize it (e.g., between 0-1)
        # Assuming max task size is 2000 KB for normalization
        task_size = sim.msg[message]['bytes'] / 2000.0 
        task_size = min(task_size, 1.0) # Cap at 1.0

        state = np.array([fog1_cpu, fog1_ram, fog2_cpu, fog2_ram, task_size], dtype=np.float32)

        # 2. GET AN ACTION FROM THE DRL AGENT
        # The `deterministic=True` argument uses the best-known policy, not random exploration.
        action, _states = self.model.predict(state, deterministic=True)

        return int(action)

    def _heuristic_fallback(self, sim, candidate_nodes):
        """Fallback heuristic if the DRL model is not available."""
        best_node = None
        min_workload = float('inf')
        for node_id in candidate_nodes:
            current_workload = len(sim.get_DES_instances_list(node_id))
            cost = current_workload
            if node_id == 20: # Cloud node
                cost += 5
            if cost < min_workload:
                min_workload = cost
                best_node = node_id
        # Map node ID back to action for consistency (reverse of node_id_map)
        action_map = {10: 0, 11: 1, 20: 2}
        return action_map.get(best_node, 0) # Default to action 0 if mapping fails