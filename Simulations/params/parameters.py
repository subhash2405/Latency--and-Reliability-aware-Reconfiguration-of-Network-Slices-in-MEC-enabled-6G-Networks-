class param:

    min_resource_server = 100
    max_resource_server = 150
    min_relaibility = 0.98
    max_relaibility = 0.995
    len_of_sfc = [3,4,5]
    distance_latency = [3,4,5]
    min_resource_vnf = 10
    max_resource_vnf = 40
    bias = 0.02
    failing_server_id = [0,5]
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


    resource_per_server = 28
    even_server_relaibility = 0.8
    odd_server_relaibility = 0.9

    facility_activation_cost = 100
    server_activation_cost = 10

    numOfSFC = 5
    vnfs_in_each_sfc = [3,3,4,5,6]
    resouces_in_each_sfc = [4,4,8,12,16]
    max_latency_in_each_sfc = [2.05, 2.05, 4.1, 6.2, 10.2]
    data_vnfs_per_sfc = [20,20,50,70,100]

    vnf_migration_dealy = 0.001