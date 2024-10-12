from collections import defaultdict
class param:

    # Data structures to hold the extracted information
    sfc_list = []
    vnf_list = []
    server_status = {}
    migration_requests = []

    # Data of the architecture setup
    data = """
    SFC 0 has 4 VNFs with max allowed delay of 4.1 and migration data size of VNFs is 1000 megabits
    VNF 0 of SFC 0 requires 8 cores is placed in server 0 of node 13
    VNF 1 of SFC 0 requires 8 cores is placed in server 1 of node 13
    VNF 2 of SFC 0 requires 8 cores is placed in server 2 of node 13
    VNF 3 of SFC 0 requires 8 cores is placed in server 3 of node 13
    SFC 1 has 4 VNFs with max allowed delay of 4.1 and migration data size of VNFs is 1000 megabits
    VNF 0 of SFC 1 requires 8 cores is placed in server 0 of node 13
    VNF 1 of SFC 1 requires 8 cores is placed in server 1 of node 13
    VNF 2 of SFC 1 requires 8 cores is placed in server 2 of node 13
    VNF 3 of SFC 1 requires 8 cores is placed in server 3 of node 13
    SFC 2 has 4 VNFs with max allowed delay of 4.1 and migration data size of VNFs is 1000 megabits
    VNF 0 of SFC 2 requires 8 cores is placed in server 0 of node 13
    VNF 1 of SFC 2 requires 8 cores is placed in server 1 of node 13
    VNF 2 of SFC 2 requires 8 cores is placed in server 2 of node 13
    VNF 3 of SFC 2 requires 8 cores is placed in server 3 of node 13
    SFC 3 has 6 VNFs with max allowed delay of 10.2 and migration data size of VNFs is 1500 megabits
    VNF 0 of SFC 3 requires 16 cores is placed in server 0 of node 25
    VNF 1 of SFC 3 requires 16 cores is placed in server 1 of node 25
    VNF 2 of SFC 3 requires 16 cores is placed in server 2 of node 25
    VNF 3 of SFC 3 requires 16 cores is placed in server 3 of node 25
    VNF 4 of SFC 3 requires 16 cores is placed in server 4 of node 25
    VNF 5 of SFC 3 requires 16 cores is placed in server 5 of node 25
    SFC 4 has 6 VNFs with max allowed delay of 10.2 and migration data size of VNFs is 1500 megabits
    VNF 0 of SFC 4 requires 16 cores is placed in server 6 of node 25
    VNF 1 of SFC 4 requires 16 cores is placed in server 7 of node 25
    VNF 2 of SFC 4 requires 16 cores is placed in server 8 of node 25
    VNF 3 of SFC 4 requires 16 cores is placed in server 9 of node 25
    VNF 4 of SFC 4 requires 16 cores is placed in server 10 of node 25
    VNF 5 of SFC 4 requires 16 cores is placed in server 11 of node 25
    Activated servers in node with residual capacity are:
    13 0 4.0, 13 1 4.0, 13 2 4.0, 13 3 4.0, 25 0 12.0, 25 1 12.0, 25 2 12.0, 25 3 12.0, 25 4 12.0, 25 5 12.0, 25 6 12.0, 25 7 12.0, 25 8 12.0, 25 9 12.0, 25 10 12.0, 25 11 12.0,
    VNFs placed in server 0 of node 13 are to be migratied for req 0
    VNFs placed in server 0 of node 25 are to be migrated for req 1

    """

    # Parsing the data
    lines = data.strip().split('\n')

    # Temporary dictionary to hold current SFC details
    current_sfc = {}
    for line in lines:
        line = line.strip()
        if line.startswith("SFC"):
            # Extract SFC details
            parts = line.split()
            sfc_id = int(parts[1])
            vnfs_count = int(parts[3])
            max_delay = float(parts[10])
            migration_size = int(parts[-2])
            current_sfc = {
                "id": sfc_id,
                "vnfs_count": vnfs_count,
                "max_delay": max_delay,
                "migration_size": migration_size,
                "vnfs": []
            }
            sfc_list.append(current_sfc)

        elif line.startswith("VNF "):
            # Extract VNF details
            parts = line.split()
            vnf_id = int(parts[1])
            sfc_id = int(parts[4])
            cores_required = int(parts[6])
            server_id = int(parts[12])
            node_id = int(parts[-1])

            # Debugging check to ensure correct SFC reference

            vnf_details = {
                "vnf_id": vnf_id,
                "sfc_id": sfc_id,
                "cores_required": cores_required,
                "server_id": server_id,
                "node_id": node_id
            }
            sfc_list[-1]["vnfs"].append(vnf_details)
            vnf_list.append(vnf_details)


        elif line.startswith("Activated servers"):
            # Extract activated servers and their residual capacities
            servers = line.split(":")[1].split(",")
            for server in servers:
                if server.strip():
                    node_id, server_id, capacity = server.strip().split()
                    node_id = int(node_id)
                    server_id = int(server_id)
                    capacity = float(capacity)
                    if node_id not in server_status:
                        server_status[node_id] = {}
                    server_status[node_id][server_id] = capacity
        elif line.startswith("VNFs placed"):
            # Extract migration requests
            parts = line.split()
            server_id = int(parts[4])
            node_id = int(parts[7])
            req_id = int(parts[-1])
            migration_requests.append({
                "server_id": server_id,
                "node_id": node_id,
                "req_id": req_id
            })

    bias = 0.00
    # Chooses between network topology 1 (10 server facilities) or 2 (27 facilities) 
    network_configuration = 2

    numofCoreFacilities = 3
    multiplicityofCores = 2
    multiplicityofregional = 3
    num_of_server_per_core_facility = 16
    num_of_server_per_regional_facility = 8
    num_of_server_per_nodal_facility = 4

    resource_per_server = 28
    even_server_relaibility = 0.8
    odd_server_relaibility = 0.9

    facility_activation_cost = 100
    server_activation_cost = 10

    vnf_migration_dealy = 0.001

    numofregionalFacilities = multiplicityofCores*numofCoreFacilities
    numofnodalFacilities = numofregionalFacilities*multiplicityofregional
    numOfFacilities = numofCoreFacilities + multiplicityofCores*numofCoreFacilities + multiplicityofCores*multiplicityofregional*numofCoreFacilities

    num_of_core_servers = num_of_server_per_core_facility*numofCoreFacilities
    num_of_regional_servers = numofregionalFacilities*num_of_server_per_regional_facility
    num_of_nodal_servers = numofnodalFacilities*num_of_server_per_nodal_facility
    total_num_of_servers = num_of_core_servers+num_of_nodal_servers+num_of_regional_servers

    numOfSFC = len(sfc_list)
    vnfs_in_each_sfc = [sfc['vnfs_count'] for sfc in sfc_list]
    resouces_in_each_sfc = [sfc['vnfs'][0]['cores_required'] for sfc in sfc_list]
    max_latency_in_each_sfc = [sfc['max_delay'] for sfc in sfc_list]
    data_vnfs_per_sfc = [sfc['migration_size'] for sfc in sfc_list]
    deployed_servers_per_sfc = {sfc['id']: [(vnf['server_id'], vnf['node_id']) for vnf in sfc['vnfs']] for sfc in sfc_list}
    failing_server_id = [(req['server_id'], req['node_id']) for req in migration_requests]


    if network_configuration == 1:
        adj_matrix = [[1,5,6],[0,2,6],[1,3,7],[2,4,7],[3,5,8],[0,4,8],[0,1,8,7,9],[6,8,9,2,3],[4,5,6,7,9],[8,6,7]]
    elif network_configuration == 2:
        adj_matrix =  [[1, 17, 19], [0, 2, 19], [1, 3, 19], [2, 4, 20], [3, 5, 20], [4, 6, 20], [5, 7, 21], [6, 8, 21], [7, 9, 21], [8, 10, 22], [9, 11, 22], [10, 12, 22], [11, 13, 23], [12, 14, 23], [13, 15, 23], [14, 16, 18], [15, 17, 18], [17, 0, 18], [24, 23, 19, 15, 16, 17], [25, 20, 18, 0, 1, 2], [25, 19, 21, 3, 4, 5], [26, 20, 22, 6, 7, 8], [26, 21, 23, 9, 10, 11], [24, 18, 22, 12, 13, 14], [25, 26, 23, 18], [24, 26, 19, 20], [24, 25, 21, 22]]
    else:
        print("ERROR : Network Configuration unavailable !!!")


    # x-axis : number of servers failed
    # y-axis : cost 

    #number of facilities and servers activated || x : servers failed vs number of facilities activated
    # % of vnfs failed to be placed vs number of failed servers
    # penatly cost vs failed servers

