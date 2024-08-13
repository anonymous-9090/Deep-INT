# Deep-INT: Towards Generic and Tunable In-band Network Telemetry Orchestration
## Overview of Deep-INT
![alt text](image-2.png)
## Requirements
- The development and testing environment for this project is based on [P4 tutorials](https://github.com/p4lang/tutorials/tree/master), which provides a series of P4 program examples and tools for learning and experimenting with the P4 language. Specifically, the project uses the following environment and tools:
  1. [P4 Compiler (p4c)](https://github.com/p4lang/p4c): Used to compile P4 programs into a format that the target device can understand.
  2. [Behavioral Model (BMv2)](https://github.com/p4lang/behavioral-model/blob/main/docs/simple_switch.md): A software P4 switch used for simulating and testing P4 programs. 
  3. [Mininet](https://github.com/mininet/mininet) supporting bmv2: Used to create and manage virtual network topologies for testing P4 programs in a simulated environment.
  4. [P4Runtime](https://p4.org/specs/): Used for runtime control of the behavior of P4 switches.
- Operating System: Linux Ubuntu 20.04
- Python Version: >= 3.8
## Code Architecture
```
-- DeepPlanner
	-- env/
        -- telemetry_a2c/
        -- telemetry_pg/
        -- telemetry_ppo/
        -- topo/
        -- dp_path.py
        -- telemetry_main_a2c.py
	-- telemetry_main_pg.py
	-- telemetry_main_ppo.py
-- PID
	-- control_interval.py
	-- no-control_interval.py
-- other_algo
	-- INT_balance.py
        -- dfs.py
        -- euler_balance.py
        -- euler_unbalance.py
-- system
        -- INT
		-- switch-config-Nsfnet/
	        -- topos/
                -- INT.p4
                -- header.p4
                -- parser.p4
                -- receiveint.py
                -- sendint.py
                -- Makefile
                -- bitmap.txt
	-- utils
                -- mininet/
                -- p4runtime_lib/
		-- run_int.py
		-- netstat.py
		-- p4_mininet.py
		-- p4apprunner.py
        	-- p4runtime_switch.py
                -- script_basic.sh
                -- Makefile
```
## other_algo
Comparison algorithms
## DeepPlanner
**env/**：The environment of DRL algorithm.

**telemetry_a2c/**：The policy of A2C algorithm.

**telemetry_pg/**：The policy of PG algorithm.

**telemetry_ppo/**：The policy of PPO algorithm.

**topo/**：The topologies used in this project.

**dp_path.py**：Generate probe paths input to the data plane.

## System

**INT/switch-config-Nsfnet/**：To configure flow tables of different switches.

**INT/topos/**：Topologies and related configuration files.

**INT/INT.p4**：Source routing and INT main procedure.

**INT/header.p4**：Define headers and metadatas.

**INT/parser.p4**：Define parser, deparser and checksum calculator.

**INT/receiveint.py**：Collect INT probe packets and store the collected telemetry data in the database.

**INT/sendint.py**：Send INT probe packets.

**INT/Makefile**：Set the topology configuration file for Mininet.

**utils/run_int.py**：To create a experimental Mininet environment and create specified probes.

**utils/script_basic.sh**:To configure the flow table information of the OVS switch.

**utils/Makefile**：Compile P4 programs and run the BMv2 simulator.

## Start DeepPlanner
### Activate Coding Environment
To create a new conda environment, execute the following command:
```
conda create --name deepint python==3.8
```
Activate the created environment with:
```
conda activate deepint
```
### Install Required Packages
The following package can be installed using pip:
```
sudo pip install tianshou==0.4.11
sudo pip install matplotlib==3.7.3
sudo pip install scipy==1.10.1
sudo pip install torch_geometric==2.5.3
```
### Start Training
```
cd DeepPlanner
sudo python3 telemetry_main_a2c.py
sudo python3 telemetry_main_pg.py
sudo python3 telemetry_main_ppo.py
```
## Start INT System
Start the system:
```
cd system/INT
sudo make run
```
Input probe paths:

For example(Nsfnet):
```
input: [[[17, 20, 22, 2, 16, 13, 29, 24, 21]], [[7, 27, 8, 3, 5, 0]], [[12, 10, 18]]]
```
The telemetry data can be found in the database like this:

![alt text](image.png)
## PID-tuner
You need to revise the sendint.py script to continuously send INT probes.
Start the INT system and run PID control script:
```
sudo python3 control_interval.py
```
Then the new sending interval will be set：
![alt text](image-1.png)
