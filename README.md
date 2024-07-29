# Deep-INT
## Project Description
Briefly describe the purpose, functionality, and features of the project.
## Requirements
- The environment of this project is baed on [P4 tutorials](https://github.com/p4lang/tutorials/tree/master), please follow the instructions of P4 tutorials to set up the environment
- [Mininet](https://github.com/mininet/mininet) supporting bmv2 (https://github.com/nsg-ethz/p4-learning)
- Operating System: Linux Ubuntu 20.04
- Python Version: >= 3.8
## Code Architecture
```
-- PID
	-- control_interval.py
	-- no-control_interval.py
-- DeepPlanner
	-- .py(the class of soft DT, which supports tree distillation)
	-- .py(the original DT)
	-- .py(include the load-data function)
		
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

### System/utils/mininet/
```
Originally created by Bob Lantz, Mininet is a very complete network emulation tool. Using Mininet, a user can quickly deploy a full network in minutes. 
```
### System/utils/p4runtime_lib/
```
To abstract a P4-enabled switch, the P4Runtime library is used. Using the P4RuntimeSwitch abstraction, the switch can be emulated within Mininet.

```
### System/utils/run_exercise.py
```
Used to create a experimental Mininet environment and for creating specified probes.
```
### System/utils/p4runtime_switch.py
```
The documentation P4Runtime is available at https://p4.org/specs/
```
### System/utils/netstat.py
```
Used to obtain information about network connections and determines if the specified port is in a listening state by checking these connections.
```
### System/utils/p4_mininet.py
```
Used to define custom P4 switch and host classes for Mininet, primarily aiming to create and manage P4 switches and hosts in the Mininet experimental environment.
```
### System/utils/script_basic.sh
```
Used to configure flow table information of OVS switch.
```
### System/utils/Makefile
```
Used to compile P4 programs and run the BMv2 simulator.
```
### System/INT/topos/
```'
All topologies used in the experiment.
```
### Sytem/INT/switch-config/
```
Used to configure flow tables of different switches.
```
### System/INT/app.p4
```
Used to do source routing and INT.
```
### System/INT/header.p4
```
Used to define Headers and Metadatas.

```
### System/INT/parser.p4
```
Used to define parser, deparser and checksum calculator.
```
### System/INT/receivenew.py
```
Used to collect INT probe packets and storing the collected network information in the database.
```
### System/INT/sendint.py
```
Used to send INT probe packets.
```
### System/INT/Makefile
```
This Makefile sets the BMv2 switch executable to simple_switch_grpc and specifies the default topology file as topos/Nsfnet.json, including common utility Makefile settings.
```

## Start DeepPlanner

## Start INT
Start the system:
```
cd System/INT
sudo make run
```
Input int paths:
For example(Nsfnet):
```
input: [[[17, 20, 22, 2, 16, 13, 29, 24, 21]], [[7, 27, 8, 3, 5, 0]], [[12, 10, 18]]]
```
The INT information can be found in your database like this:

![alt text](image.png)