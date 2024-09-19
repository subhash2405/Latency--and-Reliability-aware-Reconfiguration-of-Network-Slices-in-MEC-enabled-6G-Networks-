import random
import os
import sys
from DeployedServers import Server
from VirtualNetworkFunction import VNF
from ServiceFunctionChain import SFC
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from params.parameters import param
from utility.distance import distances

random.seed(42)

output_file = open('simulation_output2.txt', 'w')
sys.stdout = output_file

# Initialize servers
servers = [Server(i, random.randint(param.min_resource_server, param.max_resource_server),
                random.uniform(param.min_relaibility, param.max_relaibility)) for i in range(param.numOfServers)]

# Initialize SFCs
sfcs = [SFC(i) for i in range(param.numOfSFC)]

# Create and assign VNFs to SFCs and Servers
vnf_id = 0
for sfc in sfcs:
    sfc_length = random.choice(param.len_of_sfc)
    serverslist = set()
    for _ in range(sfc_length):
        resources = random.randint(param.min_resource_vnf, param.max_resource_vnf)
        latency = random.randint(1, 5)
        
        server = None
        server_set = set()
        
        while len(server_set)!=param.numOfServers:
            srv = random.choice(servers)
            if srv in server_set:
                continue
            if srv.available_resources >= resources and srv not in serverslist:
                server = srv
                serverslist.add(srv)
                break
            else:
                server_set.add(srv)

        if server is not None:
            vnf = VNF(vnf_id, sfc.id, resources, latency, server.id)
            server.add_vnf(vnf)
            sfc.add_vnf(vnf)
            vnf_id += 1
        else:
            print(f"No available server found for VNF {vnf_id} with resources {resources}.")
            break

# Adding latency and reliability factors to each SFC
for sfc in sfcs:
    info = sfc.get_info()
    for i  in range(0,len(info['vnf_list'])-1):
        vnf1 = info['vnf_list'][i]
        vnf2 = info['vnf_list'][i+1]
        dist = distances[vnf1['server_id']][vnf2['server_id']]
        sfc.add_distance_latency(dist)
        relaible = servers[vnf1['server_id']].reliability
        sfc.add_relaibility(relaible)
    relaible = servers[vnf2['server_id']].reliability
    sfc.add_relaibility(relaible)

# Function to handle server failure and reassign VNFs
def handle_server_failure(failing_server_id):
    from stable_matching_relaibility import stable_matching_for_failed_server
    stable_matching_for_failed_server(failing_server_id)

# Call the function for a server expected to fail
failing_server_id = 2  # Example server ID to simulate failure
handle_server_failure(failing_server_id)

# Display final results after reconfiguration
print("\nServer Information:")
print("====================")
for server in servers:
    info = server.get_info()
    print(f"Server {info['id']}:")
    print(f"  Total Resources: {info['total_resources']}")
    print(f"  Reliability: {info['reliability']:.3f}")
    print(f"  Available Resources: {info['available_resources']}")
    print(f"  VNF Count: {info['vnf_count']}\n")

print("\nService Function Chains (SFC) Information:")
print("==========================================")
for sfc in sfcs:
    info = sfc.get_info()
    print(f"SFC {info['id']}:")
    for vnf in info['vnf_list']:
        print(f"  VNF {vnf['id']}:")
        print(f"    Resources: {vnf['resources']}")
        print(f"    Latency: {vnf['latency']}")
        print(f"    Deployed on Server: {vnf['server_id']}\n")
    print(f"  Total Resources: {info['total_resources']}")
    print(f"  Total Reliability: {info['total_relaibility']}")
    print(f"  Total Latency: {info['total_latency']}\n")

print("\nFinal Server Information:")
print("==========================")
for server in servers:
    info = server.get_info()
    print(f"Server {info['id']}:")
    print(f"  Available Resources: {info['available_resources']}")
    print(f"  VNFs Deployed: {info['vnf_list']}\n")

output_file.close()

# Reset stdout to default
sys.stdout = sys.__stdout__
