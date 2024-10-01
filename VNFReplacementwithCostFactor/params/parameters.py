class param:

    numofCoreFacilities = 3
    multiplicityofCores = 2
    numofregionalFacilities = multiplicityofCores*numofCoreFacilities
    multiplicityofregional = 7
    numofnodalFacilities = numofregionalFacilities*multiplicityofregional
    numOfFacilities = numofCoreFacilities + multiplicityofCores*numofCoreFacilities + multiplicityofCores*multiplicityofregional*numofCoreFacilities
    numOfSFC = 5
    min_resource_server = 100
    max_resource_server = 150
    min_relaibility = 0.98
    max_relaibility = 0.995
    len_of_sfc = [3,4,5]
    distance_latency = [3,4,5]
    min_resource_vnf = 10
    max_resource_vnf = 40
    bias = 0.02
    failing_server_id = 2
    min_server_activation_cost = 100
    max_server_activation_cost = 200
    min_facility_activation_cost = 300
    max_facility_activation_cost = 400
    num_of_server_per_facility = 2
    


