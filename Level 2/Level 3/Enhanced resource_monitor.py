from yafs.core import Sim
import simpy
import numpy as np

class ResourceMonitor:
    """
    A advanced monitor to track REAL-TIME resource utilization (CPU, RAM)
    of computational nodes in the simulation.
    """

    def __init__(self):
        self.sim = None
        self.env = None
        # Dictionary to store current utilization for each node
        # Format: {node_id: {'cpu_used': 0, 'ram_used': 0, 'cpu_total': 0, 'ram_total': 0}}
        self.node_utilization = {}
        self.utilization_history = []  # Optional: for logging history

    def deploy_monitor(self, sim: Sim, interval=50):
        """Deploys the monitor to run every `interval` time units."""
        self.sim = sim
        self.env = sim.env
        self.initialize_utilization_dict(sim)
        # Start the monitoring process
        self.action = sim.env.process(self.run(interval))

    def initialize_utilization_dict(self, sim):
        """Initializes the utilization dictionary with node capacities."""
        # Nodes we want to monitor: Fog nodes (10, 11) and Cloud (20)
        nodes_to_monitor = [10, 11, 20]
        for node_id in nodes_to_monitor:
            node = sim.topology.get_node(node_id)
            # Get CPU and RAM capacity from the topology definition
            cpu_total = node.get('CPU', 1000)  # Default fallback
            ram_total = node.get('RAM', 1000)  # Default fallback
            self.node_utilization[node_id] = {
                'cpu_used': 0,
                'ram_used': 0,
                'cpu_total': cpu_total,
                'ram_total': ram_total,
                'cpu_utilization': 0.0,  # cpu_used / cpu_total
                'ram_utilization': 0.0   # ram_used / ram_total
            }

    def run(self, interval):
        """The monitoring process. Runs periodically to update resource states."""
        while True:
            yield self.env.timeout(interval)
            self.update_resource_utilization()
            self.log_status()

    def update_resource_utilization(self):
        """Calculates the current CPU and RAM usage for all monitored nodes."""
        # First, reset the used resources for all nodes
        for node_id in self.node_utilization:
            self.node_utilization[node_id]['cpu_used'] = 0
            self.node_utilization[node_id]['ram_used'] = 0

        # Iterate through ALL service instances in the simulation
        for des_id, des_instance in self.sim.des_instances.items():
            node_id = des_instance['node']  # Node where this instance is running
            if node_id not in self.node_utilization:
                continue  # Skip nodes we aren't monitoring

            # Get the application and module (service) details
            app_name = des_instance['app_name']
            module_name = des_instance['module_name']
            app = self.sim.apps[app_name]
            service_instructions = app.get_module_instructions(module_name)
            service_bytes = app.get_module_bytes(module_name)

            # Check if the instance is currently busy (executing a task)
            # 'idle' key in YAFS typically indicates if the DES is free
            if not des_instance.get('idle', True):
                # If the DES is busy, add its resource consumption to the node's total
                self.node_utilization[node_id]['cpu_used'] += service_instructions
                self.node_utilization[node_id]['ram_used'] += service_bytes

        # Calculate utilization percentages
        for node_id, metrics in self.node_utilization.items():
            total_cpu = metrics['cpu_total']
            total_ram = metrics['ram_total']
            used_cpu = metrics['cpu_used']
            used_ram = metrics['ram_used']

            # Avoid division by zero
            metrics['cpu_utilization'] = used_cpu / total_cpu if total_cpu > 0 else 0
            metrics['ram_utilization'] = used_ram / total_ram if total_ram > 0 else 0

            # Cap utilization at 100% for clarity
            metrics['cpu_utilization'] = min(metrics['cpu_utilization'], 1.0)
            metrics['ram_utilization'] = min(metrics['ram_utilization'], 1.0)

    def log_status(self):
        """Prints the current resource utilization of all monitored nodes."""
        print(f"\n--- Resource Monitor Report at Time {self.env.now} ---")
        for node_id, metrics in self.node_utilization.items():
            cpu_percent = metrics['cpu_utilization'] * 100
            ram_percent = metrics['ram_utilization'] * 100
            print(f"Node {node_id}: CPU: {cpu_percent:5.1f}% | RAM: {ram_percent:5.1f}%")
        print("------------------------------------------------------")

    def get_node_utilization(self, node_id):
        """Public method to get the current utilization of a specific node."""
        # Returns normalized CPU and RAM utilization (values between 0.0 and 1.0)
        if node_id in self.node_utilization:
            metrics = self.node_utilization[node_id]
            return metrics['cpu_utilization'], metrics['ram_utilization']
        else:
            # Return a high utilization for unknown nodes (penalize selection)
            return 1.0, 1.0  # 100% utilization