from statistics import pvariance
from other_algo.dfs import get_dfs_path
from other_algo.euler_unbalance import get_eulerun_path
from other_algo.euler_balance import get_euler_path
from other_algo.INT_balance import get_intbalance_path
from env.network_env import TelemetryEnv
import pandas as pd
import openpyxl
from openpyxl import Workbook

G = 'topo/Nsfnet.graphml'
env = TelemetryEnv(G)

print("deepint--------------------------------")
probe =[[17, 19, 20, 23, 22, 1, 2, 15, 16, 14, 13, 28, 29, 25, 24, 21], [7, 26, 27, 9, 8, 4, 3, 6, 5, 0], [12, 11, 10, 18]]     #get from deepplanner
probe_dp = env.handle_probe(probe)              #probe paths input to the data plane
print(probe_dp)

print("dfs------------------------------------")
probe_euler0a = get_dfs_path(G)
probe_euler0 = env.handle_sw(probe_euler0a)    #convert the probe paths composed of switch nodes into those composed of ports
probe_euler_dp0 = env.handle_probe(probe_euler0)  
print(probe_euler_dp0)

print("eulerun--------------------------------")
probe_eulera =get_eulerun_path(G)
probe_euler = env.handle_sw(probe_eulera)    
probe_euler_dp = env.handle_probe(probe_euler)  
print(probe_euler_dp)


print("euler----------------------------------")
probe_euler1a = get_euler_path(G)
probe_euler1 = env.handle_sw(probe_euler1a)    
probe_euler_dp1 = env.handle_probe(probe_euler1)  
print(probe_euler_dp1)

print("intbalance-----------------------------")
probe_euler2a = get_intbalance_path(G)
probe_euler2 = env.handle_sw(probe_euler2a)   
probe_euler_dp2 = env.handle_probe(probe_euler2)  
print(probe_euler_dp2)
