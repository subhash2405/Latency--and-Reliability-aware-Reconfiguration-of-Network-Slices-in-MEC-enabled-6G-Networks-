class param:

    numofCoreServers = 3
    multiplicityofCores = 2
    numofregionalServers = multiplicityofCores*numofCoreServers
    multiplicityofregional = 7
    numofnodalServers = numofregionalServers*multiplicityofregional
    numOfServers = numofCoreServers + multiplicityofCores*numofCoreServers + multiplicityofCores*multiplicityofregional*numofCoreServers
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
    # connected_matrix = [[] for _ in range(numOfServers)]


