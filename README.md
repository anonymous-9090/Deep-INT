# Deep-INT
## Project Description
Briefly describe the purpose, functionality, and features of the project.
## Requirements
- Mininet supporting bmv2 (https://github.com/nsg-ethz/p4-learning)
- Operating System: Linux Ubuntu 20.04
- Python Version: >= 3.8
## Code Architecture
```
-- control plane
	-- PID
		-- control_interval.py
		-- no-control_interval.py
	-- 
		-- .py(the class of soft DT, which supports tree distillation)
		-- .py(the original DT)
		-- .py(include the load-data function)
		
-- data plane
	-- utils
                -- mininet/
                -- p4runtime_lib/
		-- run_exercise.py
		-- netstat.py
		-- p4_mininet.py
        	-- p4runtime_switch.py
                -- script_basic.sh
                -- Makefile
	-- Deep-INT
	        -- topos/
	        -- switch-config/
                -- app.p4
                -- header.p4
                -- parser.p4
                -- receivenew.py
                -- sendint.py
                -- Makefile

```

### data plane/utils/mininet/
```
Originally created by Bob Lantz, [Mininet](https://github.com/mininet/mininet) is a very complete network emulation tool. Using Mininet, a user can quickly deploy a full network in minutes. 
```
### data plane/utils/p4runtime_lib/
```
To abstract a P4-enabled switch, the [P4Runtime](https://pypi.org/project/p4runtime/) library is used. Using the P4RuntimeSwitch abstraction, the switch can be emulated within Mininet.

The documentation P4Runtime is available [here](https://p4.org/specs/)
```
### data plane/utils/run_exercise.py
```
Used to create a experimental Mininet environment and for creating specified probes.
```
### data plane/utils/p4runtime_switch.py
```
The documentation P4Runtime is available [here](https://p4.org/specs/)
```
### data plane/utils/netstat.py
```
Used to obtain information about network connections and determines if the specified port is in a listening state by checking these connections.
```
### data plane/utils/p4_mininet.py
```
Used to define custom P4 switch and host classes for Mininet, primarily aiming to create and manage P4 switches and hosts in the Mininet experimental environment.
```
### data plane/utils/script_basic.sh
```
Used to configure flow table information of OVS switch.
```
### data plane/utils/Makefile
```
Used to compile P4 programs and run the BMv2 simulator.
```
### data plane/Deep-INT/topos/
```'
All topologies used in the experiment.
```
### data plane/Deep-INT/switch-config/
```
Used to configure flow tables of different switches.
```
### data plane/Deep-INT/app.p4
```
Used to do source routing and INT.
```
### data plane/Deep-INT/header.p4
```
Used to define Headers and Metadatas.

```
### data plane/Deep-INT/parser.p4
```
Used to define parser, deparser and checksum calculator.
```
### data plane/Deep-INT/receivenew.py
```
Used to collect INT probe packets and storing the collected network information in the database.
```
### data plane/Deep-INT/sendint.py
```
Used to send INT probe packets.
```
### data plane/Deep-INT/Makefile
```
This Makefile sets the BMv2 switch executable to simple_switch_grpc and specifies the default topology file as topos/Nsfnet.json, including common utility Makefile settings.
```
### 
