from yafs.core import Sim
import simpy

class SimpleMonitor:
    """A simple monitor to track and print the state of fog nodes periodically."""

    def deploy_monitor(self, sim: Sim, interval=100):
        """Deploys the monitor to run every `interval` time units."""
        self.sim = sim
        self.env = sim.env
        # Start the monitoring process
        self.action = sim.env.process(self.run(interval))

    def run(self, interval):
        """The monitoring process."""
        while True:
            yield self.env.timeout(interval) # Check every X time units
            self.monitor_nodes()

    def monitor_nodes(self):
        """Collects and prints state of fog nodes."""
        print(f"\n--- Monitor Report at Time {self.env.now} ---")
        fog_nodes = [10, 11] # IDs of our fog nodes

        for node_id in fog_nodes:
            # Get instances (tasks) running on this node
            instances = self.sim.get_DES_instances_list(node_id)
            workload = len(instances)
            node = self.sim.topology.get_node(node_id)
            print(f"Node {node_id} ({node['name']}): {workload} tasks in queue.")
        print("----------------------------------------")