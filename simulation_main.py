#!/usr/bin/env python3
"""
Main simulation file for the AUTONOMIC Framework.
Run this file to execute the simulation and generate results.
"""

import logging
import random
import numpy as np
from yafs.core import Sim
from yafs.application import Application, Message
from yafs.topology import Topology
from yafs.population import Population
from yafs.distribution import deterministic_distribution, exponentialDistribution
from yafs.placement import Placement
from autonomic_drl_selector import AutonomicDRLSelector  # Our custom selector
from simple_monitor import SimpleMonitor  # Our custom monitor

def create_application():
    """Defines the application model with its services and messages."""
    app = Application(name="AutonomicFogApp")
    
    # (s)ensor, (p)rocessing
    app.add_service_module(name="SensorService", 
                          instructions=20 * 10^6,  # 20 Million Instructions
                          bytes=1000)              # 1 KB input data
    app.add_service_module(name="ProcessingService", 
                          instructions=50 * 10^6,  # 50 MI
                          bytes=2000)              # 2 KB output data

    # Message from Sensor -> Processing
    m_sensor_processing = Message(name="M_Sensor_Processing", 
                                     source="SensorService", 
                                     destination="ProcessingService",
                                     bytes=1000, # Message size is 1KB
                                     instructions=50 * 10^6) # Instructions for the Processing service
    app.add_message(m_sensor_processing)
    
    return app

def create_topology():
    """Creates a JSON representation of the fog network topology."""
    topology_json = {
        "entities": [
            # IoT Devices (Source of tasks)
            {"id": 0, "model": "device", "name": "IoT_Sensor_1", "ip": "10.0.0.1"},
            {"id": 1, "model": "device", "name": "IoT_Sensor_2", "ip": "10.0.0.2"},
            # Fog Nodes (Where processing happens)
            {"id": 10, "model": "fog-node", "name": "Fog_Node_1", "ip": "192.168.1.10", "mytag":"fog", "CPU": 8000, "RAM": 4000}, # 8 GHz, 4 GB
            {"id": 11, "model": "fog-node", "name": "Fog_Node_2", "ip": "192.168.1.11", "mytag":"fog", "CPU": 4000, "RAM": 2000}, # 4 GHz, 2 GB
            # Cloud Node
            {"id": 20, "model": "cloud-node", "name": "Cloud_Server", "ip": "10.10.1.1", "mytag":"cloud", "CPU": 32000, "RAM": 64000}, # 32 GHz, 64 GB
        ],
        "links": [
            # Devices connect to Fog Nodes
            {"source": 0, "destination": 10, "bandwidth": 100, "delay": 2}, # 100 Mbps, 2ms
            {"source": 1, "destination": 10, "bandwidth": 100, "delay": 2},
            {"source": 0, "destination": 11, "bandwidth": 100, "delay": 5}, # 100 Mbps, 5ms
            {"source": 1, "destination": 11, "bandwidth": 100, "delay": 5},
            # Fog Nodes connect to Cloud
            {"source": 10, "destination": 20, "bandwidth": 1000, "delay": 50}, # 1 Gbps, 50ms
            {"source": 11, "destination": 20, "bandwidth": 1000, "delay": 50},
        ]
    }
    t = Topology()
    t.load(topology_json)
    return t

class CustomPopulation(Population):
    """Generates the initial requests from IoT devices."""
    def __init__(self, **kwargs):
        super(CustomPopulation, self).__init__(**kwargs)
        # Create a exponential distribution for inter-arrival times (lambda = 1/10 sec)
        self.dist = exponentialDistribution(100, name="Exponential", seed=None)

    def run(self, sim):
        # For all IoT device nodes (id 0 and 1)
        for node in self.src_entities:
            app_name = "AutonomicFogApp"
            app = sim.apps[app_name]
            # Get the SensorService module
            service = "SensorService"
            msg = app.get_message(service)
            # Create the initial message from the sensor
            sim.insert_event(sim.create_event(
                time = next(self.dist), 
                node = node, 
                app_name = app_name,
                module = app.get_module(service), 
                msg = msg, 
                dst = None # The DRL selector will decide the destination
            ))

def main():
    # Set a random seed for reproducibility
    random.seed(42)
    np.random.seed(42)

    logging.basicConfig(level=logging.INFO) # Use DEBUG for more detailed output

    # Create the simulation core
    s = Sim()

    # Create and deploy the application
    app = create_application()
    s.deploy_app(app)

    # Load the topology
    t = create_topology()
    s.set_topology(t)

    # --- Define Allocation Policies ---
    # PLACEMENT: Where services are initially deployed (static)
    # We place the "ProcessingService" on all fog and cloud nodes (ids 10, 11, 20)
    placement = Placement("PlacementFixed")
    placement.scale_service({"ProcessingService": [10, 11, 20]})

    # SELECTION: Where to send the next message (DYNAMIC - uses our DRL agent)
    selector = AutonomicDRLSelector("AutonomicDRLSelector")

    # POPULATION: How tasks are generated (from devices 0 and 1)
    pop = CustomPopulation(name="IoT_Population", src_entities=[0, 1])

    # DEPLOY ALL
    s.deploy(pop, placement, selector)

    # --- Deploy our Custom Monitor to collect node states ---
    monitor = SimpleMonitor()
    monitor.deploy_monitor(s) # Deploys the monitor to track fog nodes 10 & 11

    # Run the simulation
    s.run(until=1000) # Run for 1000 simulated time units
    print("\nSimulation finished.")

    # --- Export Results ---
    results = s.controller.get_results()
    results.to_csv("autonomic_simulation_results.csv", index=False)
    print("Results saved to 'autonomic_simulation_results.csv'")

    # --- Print some basic stats ---
    avg_time = results['time_ended'] - results['time_created']
    print(f"\nAverage Task Completion Time: {avg_time.mean():.2f} time units")
    print(f"Total Tasks Processed: {len(results)}")

if __name__ == '__main__':
    main()