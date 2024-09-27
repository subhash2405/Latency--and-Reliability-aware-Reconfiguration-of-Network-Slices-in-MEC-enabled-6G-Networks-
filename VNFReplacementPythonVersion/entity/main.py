import random
import os
import csv
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

server_file = 'servers_info.csv'
sfc_file = 'sfc_info.csv'

# Headers for CSV files
server_csv_headers = ['Server ID', 'Total Resources', 'Reliability', 'Available Resources', 'VNF Count', 'VNF List']
sfc_csv_headers = ['SFC ID', 'Total Resources', 'Total Reliability', 'Total Latency', 'VNFs']

# Create and initialize CSV files with headers if they don't exist
for csv_file, headers in [(server_file, server_csv_headers), (sfc_file, sfc_csv_headers)]:
    if not os.path.isfile(csv_file):
        with open(csv_file, mode='w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(headers)

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

print("Intital Configuration")
print("\nServer Information:")
print("====================")
for server in servers:
    info = server.get_info()
    print(f"Server {info['id']}:")
    print(f"  Total Resources: {info['total_resources']}")
    print(f"  Reliability: {info['reliability']:.3f}")
    print(f"  Available Resources: {info['available_resources']}")
    print(f"  VNF Count: {info['vnf_count']}\n")
    
    with open(server_file, mode='a', newline='') as file:
        print("Starting to print server and SFC information...")
        csv_writer = csv.writer(file)
        csv_writer.writerow([info['id'], info['total_resources'], f"{info['reliability']:.3f}",
                             info['available_resources'], info['vnf_count'], info['vnf_list']])

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

    with open(sfc_file, mode='a', newline='') as file:
        print("Starting to print server and SFC information...")
        csv_writer = csv.writer(file)
        csv_writer.writerow([info['id'], info['total_resources'], info['total_relaibility'],
                             info['total_latency'], info['vnf_list']])

print("\n Server Information after initial deployment:")
print("==========================")
for server in servers:
    info = server.get_info()
    print(f"Server {info['id']}:")
    print(f"  Available Resources: {info['available_resources']}")
    print(f"  VNFs Deployed: {info['vnf_list']}\n")

print("All Servers , SFC's have been setup!!!")

# Function to handle server failure and reassign VNFs
def handle_server_failure(failing_server_id):
    from stable_matching_relaibility import stable_matching_for_failed_server
    stable_matching_for_failed_server(failing_server_id, servers, sfcs)

# Call the function for a server expected to fail
# failing_server_id = 2  # Example server ID to simulate failure
failing_server_id = param.failing_server_id
handle_server_failure(failing_server_id)

# Display final results after reconfiguration
print("Final Configuration after the VNF's deployment")
print("\nServer Information:")
print("====================")
for server in servers:
    info = server.get_info()
    print(f"Server {info['id']}:")
    print(f"  Total Resources: {info['total_resources']}")
    print(f"  Reliability: {info['reliability']:.3f}")
    print(f"  Available Resources: {info['available_resources']}")
    print(f"  VNF Count: {info['vnf_count']}\n")

    with open(server_file, mode='a', newline='') as file:
        print("Starting to print server and SFC information...")
        csv_writer = csv.writer(file)
        csv_writer.writerow([info['id'], info['total_resources'], f"{info['reliability']:.3f}",
                             info['available_resources'], info['vnf_count'], info['vnf_list']])

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

    with open(sfc_file, mode='a', newline='') as file:
        print("Starting to print server and SFC information...")
        csv_writer = csv.writer(file)
        csv_writer.writerow([info['id'], info['total_resources'], info['total_relaibility'],
                             info['total_latency'], info['vnf_list']])
        
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
