from collections import defaultdict
class param:

    # Data structures to hold the extracted information
    sfc_list = []
    vnf_list = []
    server_status = {}
    migration_requests = []

    # Sample data
    data = """
    SFC 0 has 3 VNFs with max allowed delay of 2.05 and migration data size of VNFs is 20 megabits
    VNF 0 of SFC 0 requires 4 cores is placed in server 0 of node 10
    VNF 1 of SFC 0 requires 4 cores is placed in server 1 of node 10
    VNF 2 of SFC 0 requires 4 cores is placed in server 2 of node 10
    SFC 1 has 5 VNFs with max allowed delay of 6.2 and migration data size of VNFs is 70 megabits
    VNF 0 of SFC 1 requires 12 cores is placed in server 0 of node 10
    VNF 1 of SFC 1 requires 12 cores is placed in server 1 of node 10
    VNF 2 of SFC 1 requires 12 cores is placed in server 2 of node 10
    VNF 3 of SFC 1 requires 12 cores is placed in server 3 of node 10
    VNF 4 of SFC 1 requires 12 cores is placed in server 0 of node 21
    SFC 2 has 5 VNFs with max allowed delay of 6.2 and migration data size of VNFs is 70 megabits
    VNF 0 of SFC 2 requires 12 cores is placed in server 0 of node 10
    VNF 1 of SFC 2 requires 12 cores is placed in server 1 of node 10
    VNF 2 of SFC 2 requires 12 cores is placed in server 2 of node 10
    VNF 3 of SFC 2 requires 12 cores is placed in server 3 of node 10
    VNF 4 of SFC 2 requires 12 cores is placed in server 0 of node 21
    SFC 3 has 6 VNFs with max allowed delay of 10.2 and migration data size of VNFs is 100 megabits
    VNF 0 of SFC 3 requires 16 cores is placed in server 1 of node 21
    VNF 1 of SFC 3 requires 16 cores is placed in server 2 of node 21
    VNF 2 of SFC 3 requires 16 cores is placed in server 3 of node 21
    VNF 3 of SFC 3 requires 16 cores is placed in server 4 of node 21
    VNF 4 of SFC 3 requires 16 cores is placed in server 5 of node 21
    VNF 5 of SFC 3 requires 16 cores is placed in server 6 of node 21
    SFC 4 has 6 VNFs with max allowed delay of 10.2 and migration data size of VNFs is 100 megabits
    VNF 0 of SFC 4 requires 16 cores is placed in server 7 of node 21
    VNF 1 of SFC 4 requires 16 cores is placed in server 0 of node 8
    VNF 2 of SFC 4 requires 16 cores is placed in server 1 of node 8
    VNF 3 of SFC 4 requires 16 cores is placed in server 2 of node 8
    VNF 4 of SFC 4 requires 16 cores is placed in server 3 of node 8
    VNF 5 of SFC 4 requires 16 cores is placed in server 0 of node 23
    Activated servers in node with residual capacity are:
    8 0 12.0, 8 1 12.0, 8 2 12.0, 8 3 12.0, 10 0 0.0, 10 1 0.0, 10 2 0.0, 10 3 4.0, 21 0 4.0, 21 1 12.0, 21 2 12.0, 21 3 12.0, 21 4 12.0, 21 5 12.0, 21 6 12.0, 21 7 12.0, 23 0 12.0,
    VNFs placed in server 0 of node 10 are to be migratied for req 0
    VNFs placed in server 1 of node 21 are to be migrated for req 1
    """

    # Parsing the data
    lines = data.strip().split('\n')

    # Temporary dictionary to hold current SFC details
    current_sfc = {}
    for line in lines:
        if line.startswith("SFC"):
            # Extract SFC details
            parts = line.split()
            sfc_id = int(parts[1])
            vnfs_count = int(parts[3])
            max_delay = float(parts[8])
            migration_size = int(parts[-2])
            current_sfc = {
                "id": sfc_id,
                "vnfs_count": vnfs_count,
                "max_delay": max_delay,
                "migration_size": migration_size,
                "vnfs": []
            }
            sfc_list.append(current_sfc)
        elif line.startswith("VNF"):
            # Extract VNF details
            parts = line.split()
            vnf_id = int(parts[1])
            sfc_id = int(parts[4])
            cores_required = int(parts[6])
            server_id = int(parts[9])
            node_id = int(parts[12])
            vnf_details = {
                "vnf_id": vnf_id,
                "sfc_id": sfc_id,
                "cores_required": cores_required,
                "server_id": server_id,
                "node_id": node_id
            }
            current_sfc["vnfs"].append(vnf_details)
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


    network_configuration = 2

    numofCoreFacilities = 1
    multiplicityofCores = 3
    multiplicityofregional = 2
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
    resouces_in_each_sfc = [sfc['cores_required'] for sfc in sfc_list]
    max_latency_in_each_sfc = [sfc['max_delay'] for sfc in sfc_list]
    data_vnfs_per_sfc = [sfc['migration_size'] for sfc in sfc_list]
    deployed_servers_per_sfc = defaultdict(list, {sfc['id']: [(vnf['server_id'], vnf['node_id']) for vnf in sfc['vnfs']] for sfc in sfc_list})
    failing_server_id = [(req['server_id'], req['node_id']) for req in migration_requests]

    # failing_server_id = [(0,3),(0,2),(1,8),(0,6)]

        # vnfs_in_each_sfc.append(sfc['vnfs_count'])
        # resouces_in_each_sfc.append(sfc['cores_required'])
        # max_latency_in_each_sfc.append(sfc['max_delay'])
        # data_vnfs_per_sfc.append(sfc['migration_size'])


    if network_configuration == 1:
        adj_matrix = [[1,5,6],[0,2,6],[1,3,7],[2,4,7],[3,5,8],[0,4,8],[0,1,8,7,9],[6,8,9,2,3],[4,5,6,7,9],[8,6,7]]
    elif network_configuration == 2:
        adj_matrix =  [[1, 17, 19], [0, 2, 19], [1, 3, 19], [2, 4, 20], [3, 5, 20], [4, 6, 20], [5, 7, 21], [6, 8, 21], [7, 9, 21], [8, 10, 22], [9, 11, 22], [10, 12, 22], [11, 13, 23], [12, 14, 23], [13, 15, 23], [14, 16, 18], [15, 17, 18], [17, 0, 18], [24, 23, 19, 15, 16, 17], [25, 20, 18, 0, 1, 2], [25, 19, 21, 3, 4, 5], [26, 20, 22, 6, 7, 8], [26, 21, 23, 9, 10, 11], [24, 18, 22, 12, 13, 14], [25, 26, 23, 18], [24, 26, 19, 20], [24, 25, 21, 22]]
    else:
        print("ERROR : Network Configuration unavailable !!!")

    # vnfs_in_each_sfc = [3,3,3,4,4,5,5,6,6,6]
    # resouces_in_each_sfc = [4,4,4,8,8,12,12,16,16,16]
    # max_latency_in_each_sfc = [2.05, 2.05,2.05,4.1, 4.1,6.2, 6.2, 10.2, 10.2, 10.2]
    # data_vnfs_per_sfc = [20,20,20,50,50,70,70,100,100,100]
    # deployed_servers_per_sfc = {0 : [(0,3),(1,3),(2,3)], 1 : [(0,3),(1,3),(2,3)], 2 : [(0,3),(1,3),(2,3),(3,3)], 3 : [(0,3),(1,3),(2,3),(3,3)], 4 : [(0,3),(1,3),(2,3),(3,3)], 5 : [(3,3),(0,2),(1,2),(2,2),(3,2)], 6 : [(0,2),(1,2),(2,2),(3,2),(0,8)], 7 : [(0,8),(1,8),(2,8),(3,8),(4,8),(5,8)], 8 : [(6,8),(7,8),(0,6),(1,6),(2,6),(3,6)], 9 : [(4,6),(5,6),(6,6),(7,6),(0,9),(1,9)]}

    # x-axis : number of servers failed
    # y-axis : cost 

    #number of facilities and servers activated || x : servers failed vs number of facilities activated
    # % of vnfs failed to be placed vs number of failed servers
    # penatly cost vs failed servers

