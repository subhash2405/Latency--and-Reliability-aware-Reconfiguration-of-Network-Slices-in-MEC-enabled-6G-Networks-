
# output_file = open('../entity/simulation_output.txt', 'w')

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from params.parameters import param


# Cost matrix - Given - Facility to Facility
# Propogation Delay - Given



# adj_matrix = [
#     [(1, 2), (3, 2)],
#     [(0, 2), (2, 2), (3, 3), (4, 2), (5, 3)],
#     [(1, 2), (5, 2)],
#     [(0, 2), (1, 3), (4, 2)],
#     [(1, 2), (3, 2), (5, 2), (7, 2)],
#     [(1, 3), (2, 2), (4, 2), (7, 3), (8, 2)],
#     [(3, 2), (7, 2)],
#     [(3, 3), (4, 2), (5, 3), (6, 2), (8, 2)],
#     [(7, 2), (5, 2)]
# ]
adj_matrix = [[] for _ in range(param.numOfFacilities)]

core_servers = param.numofCoreFacilities
regional_servers = param.numofregionalFacilities
nodal_servers = param.numofnodalFacilities

# Start indices for regional and nodal servers
regional_start_index = core_servers
nodal_start_index = core_servers + regional_servers

# Connect core servers to regional servers
for core in range(core_servers):
    for reg in range(param.multiplicityofCores):
        regional_index = regional_start_index + core * param.multiplicityofCores + reg

        # Append the connection to both core and regional server
        adj_matrix[core].append((regional_index, 1))
        adj_matrix[regional_index].append((core, 1))

        # Connect regional servers to nodal servers
        for nod in range(param.multiplicityofregional):
            nodal_index = nodal_start_index + core * param.multiplicityofCores * param.multiplicityofregional + reg * param.multiplicityofregional + nod
            
            # Append the connection to both regional and nodal server
            adj_matrix[regional_index].append((nodal_index, 1))
            adj_matrix[nodal_index].append((regional_index, 1))

# return adj_matrix
for i in range(core_servers-1):
    adj_matrix[i].append((i+1,1))
    adj_matrix[i+1].append((i,1))

adj_matrix[core_servers-1].append((0,1))
adj_matrix[0].append((core_servers-1,1))

for reg in range(core_servers, core_servers+regional_servers-1):
    adj_matrix[reg].append((reg+1,1))
    adj_matrix[reg+1].append((reg,1))

adj_matrix[regional_servers+core_servers-1].append((core_servers,1))
adj_matrix[core_servers].append((regional_servers+core_servers-1,1))

for node in range(core_servers+regional_servers, core_servers+regional_servers+ nodal_servers-1):
    adj_matrix[node].append((node+1,1))
    adj_matrix[node+1].append((node,1))

adj_matrix[core_servers+regional_servers+ nodal_servers-1].append((core_servers+regional_servers,1))
adj_matrix[core_servers+regional_servers].append((core_servers+regional_servers+ nodal_servers-1,1))

print(adj_matrix)

num_nodes = len(adj_matrix)


def floyd_warshall(adj_matrix, num_nodes):

    dist = [[float('inf')] * num_nodes for _ in range(num_nodes)]

    for i in range(num_nodes):
        dist[i][i] = 0

    for i in range(num_nodes):
        for neighbor, weight in adj_matrix[i]:
            dist[i][neighbor] = weight

    for k in range(num_nodes):
        for i in range(num_nodes):
            for j in range(num_nodes):
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist


# distances = floyd_warshall(adj_matrix, num_nodes)
distances = [
    [0.05, 2, 4, 6, 4, 2, 2, 4, 4, 10],
    [2, 0.05, 2, 4, 6, 4, 2, 4, 4, 10],
    [4, 2, 0.05, 2, 4, 6, 4, 2, 4, 10],
    [6, 4, 2, 0.05, 2, 4, 4, 2, 4, 10],
    [4, 6, 4, 2, 0.05, 2, 4, 4, 2, 10],
    [2, 4, 6, 4, 2, 0.05, 4, 4, 2, 10],
    [2, 2, 4, 4, 4, 4, 0.05, 2, 2, 8],
    [4, 4, 2, 2, 4, 4, 2, 0.05, 2, 8],
    [4, 4, 4, 4, 2, 2, 2, 2, 0.05, 8],
    [10, 10, 10, 10, 10, 10, 8, 8, 8, 0.05]
]


for i in range(num_nodes):
    print(f"Shortest distances from node {i}: {distances[i]}")

# output_file.close()
