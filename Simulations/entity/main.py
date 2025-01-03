import random
import os
import csv
import sys
from DeployedServers import Server
from VirtualNetworkFunction import VNF
from ServiceFunctionChain import SFC
from ServerFacility import Facility
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from params.parameters import param
from utility.distance import distances

random.seed(42)

# Gives a detailed report of the reconfiguration for every run
output_file = open('simulation_output.txt', 'w')
sys.stdout = output_file

#Initialize Facility and deploy servers to their respective facilities

server_facility = [] # List of facilities containing all the info w.r.to that facility
servers = [] # List of servers containing all the info w.r.to that server

i = param.numOfFacilities-1
var = param.numOfFacilities-1

while i>=0:

    if i>=param.numofregionalFacilities + param.numofnodalFacilities:
        server_facility.append(Facility(i,1,param.facility_activation_cost))
        for j in range(param.num_of_server_per_core_facility):
            servers.append(Server((var-i)*param.num_of_server_per_core_facility+j,i, param.resource_per_server, param.even_server_relaibility if j%2==0 else param.odd_server_relaibility,param.server_activation_cost)) 
            facility = server_facility[-1]
            facility.add_server(servers[-1])

    elif i>=param.numofnodalFacilities:
        server_facility.append(Facility(i,2, param.facility_activation_cost))
        for j in range(param.num_of_server_per_regional_facility):
            servers.append(Server((var-i-param.numofCoreFacilities)*param.num_of_server_per_regional_facility + param.num_of_core_servers + j,i,param.resource_per_server, param.even_server_relaibility if j%2==0 else param.odd_server_relaibility,param.server_activation_cost))
            
            facility = server_facility[-1]
            facility.add_server(servers[-1])

    else:
        server_facility.append(Facility(i,3,param.facility_activation_cost))
        for j in range(param.num_of_server_per_nodal_facility):
            servers.append(Server((var-param.numofCoreFacilities-param.numofregionalFacilities-i)*param.num_of_server_per_nodal_facility+param.num_of_core_servers+param.num_of_regional_servers+j,i,param.resource_per_server, param.even_server_relaibility if j%2==0 else param.odd_server_relaibility,param.server_activation_cost))
            
            facility = server_facility[-1]
            facility.add_server(servers[-1])
    
    i-=1

print("Number of facilities:", len(server_facility))
print("Number of servers:", len(servers))


server_facility.reverse()

# Initialize SFCs 
sfcs = [SFC(i) for i in range(param.numOfSFC)]

# Create and assign VNFs to SFCs and Servers
vnf_id = 0
length = 0

# Setting the values of the sfc and vnfs w.r.to to the params file
for sfc in sfcs:
    sfc_length = param.vnfs_in_each_sfc[length]
    serverslist = set()
    server_id = 0
    sfc.max_latency(param.max_latency_in_each_sfc[length])
    servers_to_be_deployed = param.deployed_servers_per_sfc[length]
    for i in range(sfc_length):
        resources = param.resouces_in_each_sfc[length]
        latency = 0

        (server_id, node) = servers_to_be_deployed[i] 
        srv_facility = server_facility[node]
        server = srv_facility.deployed_servers[server_id]

        if server is not None:
            vnf = VNF(vnf_id, sfc.id, resources, latency, server.id, param.data_vnfs_per_sfc[length])
            server.add_vnf(vnf)
            sfc.add_vnf(vnf)
            vnf_id += 1
        else:
            print(f"No available server found for VNF {vnf_id} with resources {resources}.")
            break

    server_id+=1
    length+=1

# Adding latency and reliability factors to each SFC
for sfc in sfcs:
    info = sfc.get_info()
    print(info['vnf_list'])
    for i  in range(0,len(info['vnf_list'])-1):
        vnf1 = info['vnf_list'][i]
        srv1 = servers[vnf1['server_id']]
        vnf2 = info['vnf_list'][i+1]
        srv2 = servers[vnf2['server_id']]
        dist = distances[srv1.server_facility_id][srv2.server_facility_id]
        sfc.add_distance_latency(dist)
        relaible = servers[vnf1['server_id']].reliability
        sfc.add_relaibility(relaible)
    last_vnf = info['vnf_list'][len(info['vnf_list'])-1]  # Use the last VNF in the list here
    reliable = servers[last_vnf['server_id']].reliability
    sfc.add_relaibility(reliable)


# Printing the intial configuration of the given network architecture
# print("Intital Configuration")
# print("====================")
# for facility in server_facility:
#     info = facility.get_info()
#     print(f"Server_Facility {info['id']}")
#     print(f"Band : {info['Band']}")
#     print(f"Facility_activation_cost : {info['Facility_activation_cost']}")
#     print(f"Number of servers deployed : {info['server_count']}\n")

# print("====================")
# print("\nServer Information:")
# for server in servers:
#     info = server.get_info()
#     print(f"Server {info['id']}:")
#     print(f"  Total Resources: {info['total_resources']}")
#     print(f"  Reliability: {info['reliability']:.3f}")
#     print(f"  Available Resources: {info['available_resources']}")
#     print(f"  VNF Count: {info['vnf_count']}")
#     print(f"Activation cost for setup :{info['ActivationCost']}")
#     print(f"Deployed in facility : {info['DeployedinFacility']}\n")
    

# print("\nService Function Chains (SFC) Information:")
# print("==========================================")
# for sfc in sfcs:
#     info = sfc.get_info()
#     print(f"SFC {info['id']}:")
#     for vnf in info['vnf_list']:
#         print(f"  VNF {vnf['id']}:")
#         print(f"    Resources: {vnf['resources']}")
#         print(f"    Latency: {vnf['latency']}")
#         print(f"    Deployed on Server: {vnf['server_id']}\n")
#     print(f"  Total Resources: {info['total_resources']}")
#     print(f"  Total Reliability: {info['total_relaibility']}")
#     print(f"  Total Latency: {info['total_latency']}")
#     print(f"Max allowed latency : {info['max_sfc_latency']}\n")


# print("\n Server Information after initial deployment:")
# print("==========================")
# for server in servers:
#     info = server.get_info()
#     print(f"Server {info['id']}:")
#     print(f"  Available Resources: {info['available_resources']}")
#     print(f"  VNFs Deployed: {info['vnf_list']}\n")

# print("All Servers , SFC's have been setup!!!")

# Functions to handle server failure and reassign VNFs
def handle_server_failure(failing_server_id):
    from stable_matching_relaibility import stable_matching_for_failed_server
    stable_matching_for_failed_server(failing_server_id, servers, sfcs, server_facility)

def bestfit_algo_cost(failing_server_id):
    from best_fit_algortihm_cost import bestfit_algorithm_cost
    bestfit_algorithm_cost(failing_server_id, servers, sfcs, server_facility)

def bestfit_algo_resources(failing_server_id):
    from best_fit_algorithm_resources import bestfit_algorithm_resources
    bestfit_algorithm_resources(failing_server_id, servers, sfcs, server_facility)

def nearest_hop_algo(failing_server_id):
    from nearest_hop_algorithm import nearest_hop
    nearest_hop(failing_server_id, servers, sfcs, server_facility)

# Getting the info the servers that have failed 
failing_server_id = param.failing_server_id
failing_servers = []
for (srv_id, node) in failing_server_id:
    srv_facility = server_facility[node]
    server = srv_facility.deployed_servers[srv_id]
    failing_servers.append(server.id)

# Calling different algorithms for migration

handle_server_failure(failing_servers)
# bestfit_algo_cost(failing_servers)
# bestfit_algo_resources(failing_servers)
# nearest_hop_algo(failing_servers)


# Display final results after reconfiguration
# print("Final Configuration after the VNF's deployment")

# print("====================")
# for facility in server_facility:
#     info = facility.get_info()
#     print(f"Server_Facility {info['id']}")
#     print(f"Band : {info['Band']}")
#     print(f"Facility_activation_cost : {info['Facility_activation_cost']}")
#     print(f"Number of servers deployed : {info['server_count']}\n")


# print("\nServer Information:")
# print("====================")
# for server in servers:
#     info = server.get_info()
#     print(f"Server {info['id']}:")
#     print(f"  Total Resources: {info['total_resources']}")
#     print(f"  Reliability: {info['reliability']:.3f}")
#     print(f"  Available Resources: {info['available_resources']}")
#     print(f"  VNF Count: {info['vnf_count']}")
#     print(f"Activation cost for setup :{info['ActivationCost']}")
#     print(f"Deployed in facility : {info['DeployedinFacility']}\n")
    
    
# print("\nService Function Chains (SFC) Information:")
# print("==========================================")
# for sfc in sfcs:
#     info = sfc.get_info()
#     print(f"SFC {info['id']}:")
#     for vnf in info['vnf_list']:
#         print(f"  VNF {vnf['id']}:")
#         print(f"    Resources: {vnf['resources']}")
#         print(f"    Latency: {vnf['latency']}")
#         print(f"    Deployed on Server: {vnf['server_id']}\n")
#     print(f"  Total Resources: {info['total_resources']}")
#     print(f"  Total Reliability: {info['total_relaibility']}")
#     print(f"  Total Latency: {info['total_latency']}\n")
#     print(f"Max allowed latency : {info['max_sfc_latency']}\n")


# print("\nFinal Server Information:")
# print("==========================")
# for server in servers:
#     info = server.get_info()
#     print(f"Server {info['id']}:")
#     print(f"  Available Resources: {info['available_resources']}")
#     print(f"  VNFs Deployed: {info['vnf_list']}\n")

output_file.close()

# Reset stdout to default
sys.stdout = sys.__stdout__
