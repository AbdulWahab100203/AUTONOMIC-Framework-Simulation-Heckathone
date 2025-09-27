# AUTONOMIC Framework Simulation Hackathon

This project implements an AUTONOMIC Framework simulation using Deep Reinforcement Learning (DRL) for intelligent task offloading in fog computing environments. The simulation uses YAFS (Yet Another Fog Simulator) as the core simulation engine and integrates SAC (Soft Actor-Critic) agents for autonomous decision-making.

## Project Overview

The simulation models a fog computing environment with:
- **IoT Devices**: Generate tasks that need processing
- **Fog Nodes**: Edge computing resources with limited capacity
- **Cloud Server**: High-capacity centralized computing resource
- **DRL Agent**: Makes intelligent offloading decisions based on system state

## Project Structure

```
AUTONOMIC Framework Simulation Hackathon/
├── simulation_main.py                    # Main simulation entry point
├── autonomic_drl_selector.py.py         # Basic heuristic selector
├── simple_monitor.py.py                 # Basic resource monitoring
├── Level 2/
│   ├── Enhanced AutonomicDRLSelector (autonomic_drl_selector.py).py  # DRL-based selector
│   ├── Training the SAC Model (train_sac_agent.py).py                # SAC agent training
│   ├── Guide.txt                                                        # Level 2 instructions
│   └── Level 3/
│       ├── Enhanced resource_monitor.py.py                             # Advanced monitoring
│       └── Guide.txt                                                   # Level 3 instructions
├── How to Run the Simulation.txt        # Basic execution guide
├── Next Steps for Experimentation.txt   # Future enhancements
└── README.md                           # This file
```

## Required Libraries and Dependencies

### ⚠️ Important: YAFS Installation Issue

**YAFS is NOT available on PyPI** and must be installed from GitHub. Additionally, YAFS requires Python 2.7, but this project uses Python 3.x libraries. Here are the solutions:

### Solution 1: Install YAFS from GitHub (Recommended)

```bash
# Clone YAFS repository
git clone https://github.com/acsicuib/YAFS.git
cd YAFS

# Install YAFS
pip install .
```

### Solution 2: Use Python 2.7 Environment (Alternative)

If you encounter Python version conflicts, you can create a Python 2.7 environment:

```bash
# Install virtualenv for Python 2.7
pip install virtualenv

# Create Python 2.7 environment
virtualenv -p python2.7 yafs_env

# Activate environment
# Windows:
yafs_env\Scripts\activate
# Linux/Mac:
source yafs_env/bin/activate

# Install YAFS
git clone https://github.com/acsicuib/YAFS.git
cd YAFS
pip install .
```

### Core Dependencies (Python 3.x)

```bash
# Deep Reinforcement Learning
pip install stable-baselines3[extra]
pip install torch

# Scientific Computing
pip install numpy
pip install pandas

# Additional utilities
pip install simpy
pip install gym
```

### Complete Installation Commands

**For Python 3.x (after installing YAFS from GitHub):**
```bash
pip install stable-baselines3[extra] torch numpy pandas simpy gym
```

**For Python 2.7 environment:**
```bash
# Note: Some packages may not be available for Python 2.7
pip install numpy pandas simpy
# For DRL: You may need to use older versions or alternative libraries
```

### Optional Dependencies (for advanced features)

```bash
# For GPU acceleration (if available)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For data visualization and analysis
pip install matplotlib seaborn

# For Jupyter notebook support
pip install jupyter notebook
```

## Installation Steps

### Step 1: Set up Python Environment

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv autonomic_env
   ```

2. **Activate the virtual environment**:
   - **Windows**:
     ```bash
     autonomic_env\Scripts\activate
     ```
   - **Linux/Mac**:
     ```bash
     source autonomic_env/bin/activate
     ```

### Step 2: Install Dependencies

**First, install YAFS from GitHub:**
```bash
git clone https://github.com/acsicuib/YAFS.git
cd YAFS
pip install .
cd ..  # Return to your project directory
```

**Then install other dependencies:**
```bash
pip install --upgrade pip
pip install stable-baselines3[extra] torch numpy pandas simpy gym
```

### Step 3: Verify Installation

```bash
python -c "import yafs, stable_baselines3, torch, numpy, pandas, simpy, gym; print('All dependencies installed successfully!')"
```

## How to Run the Simulation

### Basic Simulation (Level 1)

1. **Run the basic simulation with heuristic selector**:
   ```bash
   python simulation_main.py
   ```

   This will:
   - Create a fog computing topology
   - Generate tasks from IoT devices
   - Use heuristic-based task offloading
   - Generate `autonomic_simulation_results.csv` with results
   - Display monitoring reports every 100 time units

### Advanced Simulation with DRL (Level 2)

1. **Train the SAC agent**:
   ```bash
   python "Level 2/Training the SAC Model (train_sac_agent.py).py"
   ```
   
   This will:
   - Create a custom Gym environment for fog offloading
   - Train a SAC agent for 50,000 timesteps
   - Save the trained model as `sac_fog_offload.zip`

2. **Run simulation with DRL agent**:
   ```bash
   python simulation_main.py
   ```
   
   The enhanced selector will automatically load the trained model if available.

### Enhanced Monitoring (Level 3)

1. **Replace the simple monitor** with the enhanced resource monitor:
   - Copy `Level 2/Level 3/Enhanced resource_monitor.py.py` to your main directory
   - Update `simulation_main.py` to import and use `ResourceMonitor` instead of `SimpleMonitor`

## Step-by-Step Execution Guide

### Complete Workflow

1. **Environment Setup**:
   ```bash
   # Create and activate virtual environment
   python -m venv autonomic_env
   autonomic_env\Scripts\activate  # Windows
   
   # Install dependencies
   pip install yafs stable-baselines3[extra] torch numpy pandas simpy gym
   ```

2. **Basic Simulation Test**:
   ```bash
   python simulation_main.py
   ```
   
   Expected output:
   - Monitor reports every 100 time units
   - Simulation runs for 1000 time units
   - Results saved to `autonomic_simulation_results.csv`

3. **Train DRL Agent**:
   ```bash
   python "Level 2/Training the SAC Model (train_sac_agent.py).py"
   ```
   
   Expected output:
   - Training progress logs
   - Model saved as `sac_fog_offload.zip`

4. **Run Enhanced Simulation**:
   ```bash
   python simulation_main.py
   ```
   
   The system will now use the trained DRL agent for offloading decisions.

5. **Analyze Results**:
   - Open `autonomic_simulation_results.csv` in Excel or Python
   - Compare performance metrics between heuristic and DRL approaches

## Understanding the Output

### Monitor Reports
```
--- Monitor Report at Time 200 ---
Node 10 (Fog_Node_1): 2 tasks in queue.
Node 11 (Fog_Node_2): 1 tasks in queue.
----------------------------------------
```

### Results CSV File
The `autonomic_simulation_results.csv` contains:
- `time_created`: When the task was generated
- `time_started`: When processing began
- `time_ended`: When processing completed
- `source`: Source node ID
- `destination`: Destination node ID
- Additional simulation metrics

### Performance Metrics
- **Average Task Completion Time**: Calculated from the CSV results
- **Total Tasks Processed**: Number of completed tasks
- **Resource Utilization**: CPU and RAM usage per node

## Troubleshooting

### Common Issues

1. **YAFS Installation Errors**:
   ```bash
   # YAFS is not available on PyPI - must install from GitHub
   git clone https://github.com/acsicuib/YAFS.git
   cd YAFS
   pip install .
   
   # If you get Python version errors, try Python 2.7:
   virtualenv -p python2.7 yafs_env
   source yafs_env/bin/activate  # Linux/Mac
   # or yafs_env\Scripts\activate  # Windows
   ```

2. **Python Version Conflicts**:
   ```bash
   # If stable-baselines3 import fails
   pip install --upgrade stable-baselines3
   
   # If you need Python 2.7 compatibility, use older versions:
   pip install numpy==1.16.6 pandas==0.24.2
   ```

2. **Model Loading Errors**:
   - Ensure `sac_fog_offload.zip` exists in the project directory
   - Check that the model was trained successfully
   - The system will fall back to heuristic selection if model loading fails

3. **Memory Issues**:
   - Reduce simulation time: Change `s.run(until=1000)` to a smaller value
   - Reduce batch size in training: Modify `batch_size=256` to `batch_size=128`

### Performance Optimization

1. **GPU Acceleration**:
   - Install CUDA-compatible PyTorch for faster training
   - Modify `device='cpu'` to `device='cuda'` in training script

2. **Simulation Parameters**:
   - Adjust `interval` in monitor deployment for more/fewer reports
   - Modify topology parameters (CPU, RAM, bandwidth) for different scenarios

## Next Steps for Experimentation

1. **Baseline Comparison**: Implement and compare with random/round-robin selectors
2. **Real State Integration**: Connect DRL agent to actual resource monitoring data
3. **Fault Tolerance**: Add node failure simulation and self-healing capabilities
4. **Scalability Testing**: Test with larger topologies and more nodes
5. **Performance Metrics**: Implement additional metrics like energy consumption and latency

## Project Components

- **`simulation_main.py`**: Core simulation setup and execution
- **`autonomic_drl_selector.py.py`**: Basic heuristic-based task selector
- **`simple_monitor.py.py`**: Basic resource monitoring
- **Enhanced Components**: Advanced DRL-based selector and resource monitoring
- **Training Script**: SAC agent training environment

## Contributing

This project serves as a foundation for AUTONOMIC Framework research. Key areas for enhancement:
- Integration of real-time monitoring data
- Advanced reward function design
- Multi-objective optimization
- Fault tolerance and self-healing capabilities

## License

This project is part of academic research in AUTONOMIC computing frameworks.
