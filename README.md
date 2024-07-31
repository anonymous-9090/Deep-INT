# Deep-INT
## Project Description

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
-- PID
	-- control_interval.py
	-- no-control_interval.py

-- DeepPlanner
	-- env/
        -- temetry_a2c/
        -- temetry_pg/
        -- temetry_ppo/
        -- topo/
        -- telemetry_main_a2c.py
	-- telemetry_main_pg.py
	-- telemetry_main_ppo.py
-- other_algo
-- Syetem
	-- utils
                -- mininet/
                -- p4runtime_lib/
		-- run_exercise.py
		-- netstat.py
		-- p4_mininet.py
        	-- p4runtime_switch.py
                -- script_basic.sh
                -- Makefile
	-- INT
	        -- topos/
	        -- switch-config/
                -- app.p4
                -- header.p4
                -- parser.p4
                -- receivenew.py
                -- sendint.py
                -- Makefile

```
### other_algo
Comparison algorithms
### DeepPlanner/env/
The environment of DRL algorithm
### DeepPlanner/temetry_a2c/
The policy of A2C algorithm
### other_algo/temetry_pg/
The policy of PG algorithm
### other_algo/temetry_ppo/
The policy of PPO algorithm
### other_algo/topo/
The topologies used in this project
### other_algo/telemetry_main_a2c.py
Strat training A2C
### other_algo/telemetry_main_pg.py
Strat training PG
### other_algo/telemetry_main_ppo.py
Strat training PPO
### System/utils/mininet/
Originally created by Bob Lantz, Mininet is a very complete network emulation tool. Using Mininet, a user can quickly deploy a full network in minutes
### System/utils/p4runtime_lib/
To abstract a P4-enabled switch, the P4Runtime library is used. Using the P4RuntimeSwitch abstraction, the switch can be emulated within Mininet
### System/utils/run_int.py
Used to create a experimental Mininet environment and create specified probes
### System/utils/p4runtime_switch.py
The documentation P4Runtime is available at https://p4.org/specs/
### System/utils/netstat.py
Used to obtain information about network connections and determines if the specified port is in a listening state by checking these connections
### System/utils/p4_mininet.py
Used to define custom P4 switch and host classes for Mininet, primarily aiming to create and manage P4 switches and hosts in the Mininet experimental environment
### System/utils/script_basic.sh
Used to configure flow table information of OVS switch
### System/utils/Makefile
Used to compile P4 programs and run the BMv2 simulator
### System/INT/topos/
All topologies used in the experiment
### Sytem/INT/switch-config/
Used to configure flow tables of different switches
### System/INT/INT.p4
Used to do source routing and INT
### System/INT/header.p4
Used to define Headers and Metadatas
### System/INT/parser.p4
Used to define parser, deparser and checksum calculator
### System/INT/receiveint.py
Used to collect INT probe packets and storing the collected network information in the database
### System/INT/sendint.py
Used to send INT probe packets
### System/INT/Makefile
This Makefile sets the BMv2 switch executable to simple_switch_grpc and specifies the default topology file as topos/Nsfnet.json, including common utility Makefile settings

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
pip install tianshou==0.4.11
pip install matplotlib==3.7.3
pip install scipy==1.10.1
```
### Start Training
```
cd DeepPlanner
sudo python3 telemetry_main_a2c.py
sudo python3 telemetry_main_pg.py
sudo python3 telemetry_main_ppo.py
```
## Start INT
Start the system:
```
cd System/INT
sudo make run
```
Input INT paths:
For example(Nsfnet):
```
input: [[[17, 20, 22, 2, 16, 13, 29, 24, 21]], [[7, 27, 8, 3, 5, 0]], [[12, 10, 18]]]
```
The INT information can be found in your database like this:

![alt text](image.png)