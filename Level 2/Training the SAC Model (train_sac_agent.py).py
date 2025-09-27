import gym
from gym import spaces
import numpy as np
from stable_baselines3 import SAC
from stable_baselines3.common.env_checker import check_env
import torch as th
import os

class FogOffloadEnv(gym.Env):
    """
    Custom Gym Environment for training a DRL agent for fog task offloading.
    This environment simulates the core decision problem: choosing a node based on system state.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(FogOffloadEnv, self).__init__()
        # Define action and observation space
        self.action_space = spaces.Discrete(3)  # Actions: 0=Fog1, 1=Fog2, 2=Cloud
        # State: [CPU_Load_Fog1, RAM_Fog1, CPU_Load_Fog2, RAM_Fog2, Task_Size_Normalized]
        self.observation_space = spaces.Box(low=0, high=1, shape=(5,), dtype=np.float32)
        
        self.state = None
        self.current_step = 0
        self.max_steps = 200

    def reset(self):
        # Reset the state of the environment to an initial random state
        self.state = np.random.rand(self.observation_space.shape[0]).astype(np.float32)
        self.current_step = 0
        return self.state

    def step(self, action):
        # Execute one time step within the environment
        self.current_step += 1
        done = self.current_step >= self.max_steps

        # 1. Apply the action (choose a node)
        chosen_node = action  # 0, 1, or 2

        # 2. Simulate the outcome and calculate reward
        # This is a simplified reward function. In a real setup, this would
        # be calculated by the simulator (YAFS) after running the decision.
        latency, energy = self._simulate_performance(chosen_node)
        
        # Reward is a combination of negative latency and negative energy
        # We want to maximize reward, which means minimizing latency and energy.
        reward = -latency - (0.1 * energy) 

        # 3. Generate a new random state for the next step
        self.state = np.random.rand(self.observation_space.shape[0]).astype(np.float32)

        # 4. Info dictionary for debugging
        info = {"latency": latency, "energy": energy, "node": chosen_node}
        
        return self.state, reward, done, info

    def _simulate_performance(self, node):
        """Simulates the performance (latency, energy) of choosing a node."""
        # Get the state components
        fog1_cpu, fog1_ram, fog2_cpu, fog2_ram, task_size = self.state
        # Base performance characteristics for each node
        if node == 0:  # Fog Node 1
            base_latency = 5
            base_energy = 0.5
            load_penalty = fog1_cpu * 10  # Penalty for high CPU load
        elif node == 1:  # Fog Node 2
            base_latency = 10
            base_energy = 0.4
            load_penalty = fog2_cpu * 10
        else:  # Cloud Node
            base_latency = 50  # High base latency due to distance
            base_energy = 0.1  # Low energy (from edge perspective)
            load_penalty = 0   # Assumed infinite cloud resources

        # Task size influences latency and energy
        task_effect = task_size * 20
        
        latency = base_latency + load_penalty + task_effect
        energy = base_energy + task_effect / 100
        
        return latency, energy

    def render(self, mode='human'):
        print(f"Step: {self.current_step}, State: {self.state}")

# Create environment
env = FogOffloadEnv()
# Check if the environment follows the Gym API (optional)
check_env(env)

# Define network architecture for the policy
policy_kwargs = dict(activation_fn=th.nn.ReLU,
                     net_arch=dict(pi=[64, 64], qf=[64, 64]))

# Create the SAC agent
model = SAC('MlpPolicy', 
            env, 
            policy_kwargs=policy_kwargs,
            verbose=1,          # Print training progress
            learning_rate=3e-4,
            batch_size=256,
            gamma=0.99,         # Discount factor
            tau=0.005,          # Target network update rate
            device='cpu')       # Use 'cuda' for GPU

# Train the agent
print("Starting training...")
model.learn(total_timesteps=50000) # Train for 50,000 steps

# Save the trained model
model_path = "sac_fog_offload"
model.save(model_path)
print(f"Model saved to {model_path}.zip")

print("Training finished. Testing the trained agent...")
# Test the trained agent
obs = env.reset()
for i in range(5):
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, done, info = env.step(action)
    env.render()
    print(f"Chose node: {info['node']}, Latency: {info['latency']:.2f}, Energy: {info['energy']:.2f}, Reward: {reward:.2f}")
    if done:
        obs = env.reset()