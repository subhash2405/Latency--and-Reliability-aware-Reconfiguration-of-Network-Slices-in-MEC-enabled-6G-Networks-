class param:

    min_resource_server = 100
    max_resource_server = 150
    min_relaibility = 0.98
    max_relaibility = 0.995
    len_of_sfc = [3,4,5]
    distance_latency = [3,4,5]
    min_resource_vnf = 10
    max_resource_vnf = 40
    bias = 0.00
    failing_server_id = [(0,3),(0,2),(1,8),(0,6)]
    min_server_activation_cost = 100
    max_server_activation_cost = 200
    min_facility_activation_cost = 300
    max_facility_activation_cost = 400
    num_of_server_per_facility = 2
    

    numofCoreFacilities = 1
    multiplicityofCores = 3
    multiplicityofregional = 2
    numofregionalFacilities = multiplicityofCores*numofCoreFacilities
    numofnodalFacilities = numofregionalFacilities*multiplicityofregional
    numOfFacilities = numofCoreFacilities + multiplicityofCores*numofCoreFacilities + multiplicityofCores*multiplicityofregional*numofCoreFacilities

    num_of_server_per_core_facility = 16
    num_of_server_per_regional_facility = 8
    num_of_server_per_nodal_facility = 4

    num_of_core_servers = num_of_server_per_core_facility*numofCoreFacilities
    num_of_regional_servers = numofregionalFacilities*num_of_server_per_regional_facility
    num_of_nodal_servers = numofnodalFacilities*num_of_server_per_nodal_facility
    total_num_of_servers = num_of_core_servers+num_of_nodal_servers+num_of_regional_servers

    resource_per_server = 28
    even_server_relaibility = 0.8
    odd_server_relaibility = 0.9

    facility_activation_cost = 100
    server_activation_cost = 10

    numOfSFC = 10
    vnfs_in_each_sfc = [3,3,3,4,4,5,5,6,6,6]
    resouces_in_each_sfc = [4,4,4,8,8,12,12,16,16,16]
    max_latency_in_each_sfc = [2.05, 2.05,2.05,4.1, 4.1,6.2, 6.2, 10.2, 10.2, 10.2]
    data_vnfs_per_sfc = [20,20,20,50,50,70,70,100,100,100]

    vnf_migration_dealy = 0.001

    deployed_servers_per_sfc = {0 : [(0,3),(1,3),(2,3)], 1 : [(0,3),(1,3),(2,3)], 2 : [(0,3),(1,3),(2,3),(3,3)], 3 : [(0,3),(1,3),(2,3),(3,3)], 4 : [(0,3),(1,3),(2,3),(3,3)], 5 : [(3,3),(0,2),(1,2),(2,2),(3,2)], 6 : [(0,2),(1,2),(2,2),(3,2),(0,8)], 7 : [(0,8),(1,8),(2,8),(3,8),(4,8),(5,8)], 8 : [(6,8),(7,8),(0,6),(1,6),(2,6),(3,6)], 9 : [(4,6),(5,6),(6,6),(7,6),(0,9),(1,9)]}

    adj_matrix = [[1,5,6],[0,2,6],[1,3,7],[2,4,7],[3,5,8],[0,4,8],[0,1,8,7,9],[6,8,9,2,3],[4,5,6,7,9],[8,6,7]]
    


    # x-axis : number of servers failed
    # y-axis : cost 

    #number of facilities and servers activated || x : servers failed vs number of facilities activated
    # % of vnfs failed to be placed vs number of failed servers
    # penatly cost vs failed servers

