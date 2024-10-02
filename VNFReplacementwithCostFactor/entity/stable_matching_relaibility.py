from params.parameters import param
from utility.distance import distances
from VirtualNetworkFunction import VNF
# global count
def stable_matching_for_failed_server(failing_server_id, servers, sfcs, server_facility):
    global count
    count = 0
    # from main import servers, sfcs

    failing_server = servers[failing_server_id]
    vnfs_to_reassign = failing_server.get_vnfs()  # Get all VNFs from the failing server

    vnf_preferences = {}
    server_preferences = {}

    for vnf in vnfs_to_reassign:
        vnf_preferences[vnf.id] = []
        current_sfc = next(sfc for sfc in sfcs if sfc.id == vnf.sfc_id) #finds the sfc corresponding to the particular vnf
        current_servers_deployed = current_sfc.get_deployed_server_list()
        for server in servers:
            if server.id != failing_server_id and server.available_resources >= vnf.resources and server.id not in current_servers_deployed:
                distance_latency = 0
                present_latency = 0
                
                # Iterate over the VNFs in the current SFC to calculate distances
                for other_vnf in range(len(current_sfc.vnf_list) - 1):
                    current_vnf_id = current_sfc.vnf_list[other_vnf].id
                    next_vnf_id = current_sfc.vnf_list[other_vnf + 1].id
                    
                    present_latency += distances[current_sfc.vnf_list[other_vnf].server_id][current_sfc.vnf_list[other_vnf + 1].server_id]
                    # Check if the current VNF or next VNF is not the one being placed
                    if current_vnf_id != vnf.id and next_vnf_id != vnf.id:
                        # Distance between two existing VNFs
                        distance_latency += distances[current_sfc.vnf_list[other_vnf].server_id][current_sfc.vnf_list[other_vnf + 1].server_id]
                    
                    # Case where the new server is placed between existing VNFs
                    elif current_vnf_id != vnf.id:
                        # Distance between the current VNF and the new server
                        distance_latency += distances[current_sfc.vnf_list[other_vnf].server_id][server.id]
                    else:
                        # Distance between the new server and the next VNF
                        distance_latency += distances[server.id][current_sfc.vnf_list[other_vnf + 1].server_id]
                
                # Add the server and its calculated distance_latency to the VNF's preference list
                new_relability = (current_sfc.total_relaibility - param.bias)/failing_server.reliability
                new_relability*=server.reliability
                new_relability+=param.bias
                if distance_latency <= present_latency and new_relability>=current_sfc.total_relaibility:
                    cost_of_migration = vnf.data*distances[failing_server.server_facility_id][server.server_facility_id]
                    if len(server.vnf_list)==0:
                        cost_of_migration+=server.activation_cost
                    facility = server_facility[server.server_facility_id]
                    flag=0
                    for srv in facility.server_list:
                        if len(srv.vnf_list)!=0:
                            flag=1
                            break
                    if flag==0:
                        cost_of_migration+=facility.activation_cost
                    vnf_preferences[vnf.id].append((server,  distance_latency, cost_of_migration, new_relability,server.id))


        # Sort the servers for each VNF by highest relaibility 
        # Sort w.r.to objective cost of instantiation only if its new data*cost
        if len(vnf_preferences[vnf.id])==0:
            count+=1
            print(f"No matching found for SFC {current_sfc.id} whose vnf is {vnf.id}")
        else:
        
            vnf_preferences[vnf.id].sort(key=lambda x: x[2])
    print("VNF Preferences", vnf_preferences)

    for server in servers:
        server_preferences[server.id] = []
        # Servers prefer VNFs that can fit into their available resources while maintaining reliability
        for vnf in vnfs_to_reassign:
            if server.available_resources >= vnf.resources:
                server_preferences[server.id].append(vnf)
        
        # Sort VNFs by their resource demand (higher order)
        server_preferences[server.id].sort(key=lambda v: v.resources, reverse=True)

    print("server prefrences", server_preferences)
    # Step 3: Stable Matching Algorithm (Gale-Shapley style)
    unassigned_vnfs = vnfs_to_reassign.copy()
    vnf_assignments = {}
    server_assignments = {server.id: [] for server in servers}

    while unassigned_vnfs:
        vnf = unassigned_vnfs.pop(0)
        vnf_id = vnf.id

        # VNF proposes to its most preferred server
        preferred_server, _, _, _, _ = vnf_preferences[vnf_id].pop(0)
        
        # If the server can accept the VNF, assign it
        if sum(v.resources for v in server_assignments[preferred_server.id]) + vnf.resources <= preferred_server.available_resources:
            server_assignments[preferred_server.id].append(vnf)
            vnf_assignments[vnf_id] = preferred_server.id
        else:
            # If the server is full, reject the least preferred VNF and try again
            rejected_vnf = sorted(server_assignments[preferred_server.id], key=lambda v: v.resources)[0]
            if rejected_vnf.resources > vnf.resources:
                unassigned_vnfs.append(rejected_vnf)
                server_assignments[preferred_server.id].remove(rejected_vnf)
                server_assignments[preferred_server.id].append(vnf)
                vnf_assignments[vnf_id] = preferred_server.id
            else:
                unassigned_vnfs.append(vnf)

    # Step 4: Redeploy the VNFs and update latency and reliability for the affected SFCs
    for vnf in vnfs_to_reassign:
        new_server_id = vnf_assignments[vnf.id]
        vnf.change_server_id(new_server_id)
        new_server = servers[new_server_id]
        new_server.add_vnf(vnf)
        current_sfc = next(sfc for sfc in sfcs if sfc.id == vnf.sfc_id)
        
        # Recalculate latency and reliability for the SFC
        
        info = current_sfc.get_info()
        
        current_sfc.add_distance_latency(-1*(current_sfc.total_latency-current_sfc.vnf_latency))
        current_relaibility = current_sfc.total_relaibility
        current_sfc.total_relaibility = 1
        for i  in range(0,len(info['vnf_list'])-1):    
            vnf1 = info['vnf_list'][i]
            vnf2 = info['vnf_list'][i+1]
            dist = distances[vnf1['server_id']][vnf2['server_id']]
            current_sfc.add_distance_latency(dist)
            relaible = servers[vnf1['server_id']].reliability
            current_sfc.add_relaibility(relaible)
        relaible = servers[vnf2['server_id']].reliability
        current_sfc.add_relaibility(relaible)
        if current_relaibility>current_sfc.total_relaibility:
            count+=1
            print(f"Relaibility factor not satisfied for SFC {current_sfc.id} whose vnf {vnf.id} is deployed in server {new_server_id}")
    failing_server.server_fail()
    print(f"Total SFC's that failed realibility factor or latency requirement {count}")
    print(f"Stable matching completed. VNFs from server {failing_server_id} have been reassigned.")
