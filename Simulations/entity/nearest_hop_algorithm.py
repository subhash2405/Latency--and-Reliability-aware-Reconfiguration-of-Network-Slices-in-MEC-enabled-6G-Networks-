from params.parameters import param
from utility.distance import distances
from VirtualNetworkFunction import VNF
import csv
import os
def nearest_hop(failing_server_id, servers, sfcs, server_facility):
    global count
    count = 0
    total_migration_cost = 0
    new_facility_activated = 0
    new_server_activated = 0

    # Creating a results file, it appends the output of every run to this file
    results_file = 'results.csv'
    headers = ['Servers failed', 'Num of facilities activated', 'Num of servers activated', 'vnfs failed to be placed','algorithm used', 'Overall Cost']
    
    if not os.path.isfile(results_file):
        with open(results_file, mode='w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(headers)


    vnfs_to_reassign = []  # Get all VNFs from the failing server
    
    for fail in failing_server_id:
        failing_server = servers[fail]
        vnfs_to_reassign += (failing_server.get_vnfs())

    vnf_preferences = {}

    for vnf in vnfs_to_reassign:
        vnf_preferences[vnf.id] = []
        current_sfc = next(sfc for sfc in sfcs if sfc.id == vnf.sfc_id) #finds the sfc corresponding to the particular vnf
        current_servers_deployed = current_sfc.get_deployed_server_list()
        current_server_facility = server_facility[servers[vnf.server_id].server_facility_id]

        # Implementing BFS to check if we have any eligible server after every hop

        priority_queue = [(current_server_facility,0)] # Keeps a list of tuples containing the server_facility and the present hop
        visited_facilities = set() # Keeps a track of the previously visited facilities
        prev_hop = 10000
        while priority_queue:
            srv_facility,hop = priority_queue.pop(0)
            # print("pq")
            # print(srv_facility.id, hop, prev_hop)
            if srv_facility in visited_facilities:
                continue

            visited_facilities.add(srv_facility)

            # If the current hop > prev hop => all the neighbors of the prev hop distance have been visited and if the vnf_list!=0 then break and choose the best server of the available ones
            if hop>prev_hop and len(vnf_preferences[vnf.id])!=0: 
                    break
            
            prev_hop = hop
            # Checking for the eligible servers and appending it to the vnf_prefernce list

            for server in srv_facility.deployed_servers:

                server_activation_cost =  0 # Keeping a track of the activation costs if deployed in that particular server
                facility_activation_cost = 0

                if server.id not in failing_server_id and server.available_resources >= vnf.resources and server.id not in current_servers_deployed:
                    distance_latency = 0
                    present_latency = 0

                    # Iterate over the VNFs in the current SFC to calculate distances
                    for other_vnf in range(len(current_sfc.vnf_list) - 1):
                        current_vnf_id = current_sfc.vnf_list[other_vnf].id
                        next_vnf_id = current_sfc.vnf_list[other_vnf + 1].id
                        
                        present_latency += distances[servers[current_sfc.vnf_list[other_vnf].server_id].server_facility_id][servers[current_sfc.vnf_list[other_vnf + 1].server_id].server_facility_id]
                        # Check if the current VNF or next VNF is not the one being placed
                        if current_vnf_id != vnf.id and next_vnf_id != vnf.id:
                            # Distance between two existing VNFs
                            distance_latency += distances[servers[current_sfc.vnf_list[other_vnf].server_id].server_facility_id][servers[current_sfc.vnf_list[other_vnf + 1].server_id].server_facility_id]
                        
                        # Case where the new server is placed between existing VNFs
                        elif current_vnf_id != vnf.id:
                            # Distance between the current VNF and the new server
                            distance_latency += distances[servers[current_sfc.vnf_list[other_vnf].server_id].server_facility_id][servers[server.id].server_facility_id]
                        else:
                            # Distance between the new server and the next VNF
                            distance_latency += distances[servers[server.id].server_facility_id][servers[current_sfc.vnf_list[other_vnf + 1].server_id].server_facility_id]
                    
                    # Add the server and its calculated distance_latency to the VNF's preference list
                    # Calculating the new relaibility and calculating the migration cost
                    new_relability = (current_sfc.total_relaibility - param.bias)/servers[vnf.server_id].reliability
                    new_relability*=server.reliability
                    new_relability+=param.bias
                    if distance_latency <= current_sfc.maxlatency and new_relability>=current_sfc.total_relaibility:
                        cost_of_migration = vnf.data*distances[servers[vnf.server_id].server_facility_id][server.server_facility_id]*param.vnf_migration_dealy
                        if len(server.vnf_list)==0:
                            cost_of_migration+=server.activation_cost
                            server_activation_cost = server.activation_cost

                        facility = server_facility[server.server_facility_id].get_info()
                        flag=0
                        for srv in facility['server_list']:
                            if len(srv['vnf_list'])!=0:
                                flag=1
                                break
                        if flag==0:
                            cost_of_migration+=facility['Facility_activation_cost']
                            facility_activation_cost = facility['Facility_activation_cost']
                        vnf_preferences[vnf.id].append((server,  distance_latency, cost_of_migration, new_relability,server.id, server_activation_cost, facility_activation_cost))

            # Adding the adjacent neighbors of the present server_facility
            for node in param.adj_matrix[srv_facility.id]:
                # print(srv_facility.id,node, hop)
                priority_queue.append((server_facility[node], hop+1))


        # Sort w.r.to objective : cost of migration 
        if len(vnf_preferences[vnf.id])==0:
            count+=1
            print(f"No matching found for SFC {current_sfc.id} whose vnf is {vnf.id}")

        else:
            vnf_preferences[vnf.id].sort(key=lambda x: x[2])
            # for i in range(len(vnf_preferences[vnf.id])):
            #     print(vnf_preferences[vnf.id][i][0].get_info())
            #     print(vnf_preferences[vnf.id][i])
            preferred_server, _, migration_cost, _, _, server_cost, facility_cost = vnf_preferences[vnf.id].pop(0)
            new_server_id = preferred_server.id

            cost_of_migration = migration_cost - server_cost - facility_cost
            new_server = servers[new_server_id]
            new_server_facility = server_facility[new_server.server_facility_id]

            facility = new_server_facility.get_info()
            # Adding the migration costs only if the server or facility has not been activated previously
            flag=0
            for srv in facility['server_list']:
                if len(srv['vnf_list'])!=0:
                    flag=1
                    break
            if flag==1:
                migration_cost-=facility_cost

            if len(new_server.vnf_list)!=0:
                migration_cost-=server_cost

            if migration_cost == cost_of_migration + param.server_activation_cost:
                new_server_activated+=1
            elif migration_cost > cost_of_migration + param.server_activation_cost:
                new_facility_activated+=1
                new_server_activated+=1


            # Deploying the vnf in the new server and passing the required information to its respective sfc and server
            vnf.change_server_id(new_server_id)
            new_server.add_vnf(vnf)
            current_sfc = next(sfc for sfc in sfcs if sfc.id == vnf.sfc_id)
            total_migration_cost+=migration_cost

            info = current_sfc.get_info()
        
            current_sfc.add_distance_latency(-1*(current_sfc.total_latency-current_sfc.vnf_latency))
            current_relaibility = current_sfc.total_relaibility
            current_sfc.total_relaibility = 1
            for i  in range(0,len(info['vnf_list'])-1):    
                vnf1 = info['vnf_list'][i]
                vnf2 = info['vnf_list'][i+1]
                dist = distances[servers[vnf1['server_id']].server_facility_id][servers[vnf2['server_id']].server_facility_id]
                current_sfc.add_distance_latency(dist)
                relaible = servers[vnf1['server_id']].reliability
                current_sfc.add_relaibility(relaible)
            relaible = servers[vnf2['server_id']].reliability
            current_sfc.add_relaibility(relaible)
            if current_relaibility>current_sfc.total_relaibility:
                count+=1
                print(f"Relaibility factor not satisfied for SFC {current_sfc.id} whose vnf {vnf.id} is deployed in server {new_server_id}")
    

            

    # Deleting the resources for the failed servers
    for fail in failing_server_id:
        failing_server = servers[fail]
        failing_server.server_fail()
    print(f"Total migration cost of vnfs is {total_migration_cost}")
    print(f"Total VNF's that failed realibility factor or latency requirement {count}")
    print(f"Stable matching completed. VNFs from server {failing_server_id} have been reassigned.")

    # writing the results to csv file
    with open(results_file, mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow([len(failing_server_id),new_facility_activated,new_server_activated,count, 'Nearest Hop algorithm', total_migration_cost])
