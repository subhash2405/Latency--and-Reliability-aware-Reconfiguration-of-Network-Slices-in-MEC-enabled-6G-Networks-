from params.parameters import param
from utility.distance import distances
from VirtualNetworkFunction import VNF
import csv
import os

total_migration_cost = 0
count = 0
def stable_matching_for_failed_server(failing_server_id, servers, sfcs, server_facility):
    global count
    global total_migration_cost
    global new_server_activated
    global new_facility_activated
    new_facility_activated = 0
    new_server_activated = 0
    total_migration_cost = 0
    # Creating a results.csv file to keep track of the final results after every run
    results_file = 'results.csv'
    headers = ['Servers failed', 'Num of facilities activated', 'Num of servers activated', 'vnfs failed to be placed','algorithm used', 'Overall Cost']

    if not os.path.isfile(results_file):
        with open(results_file, mode='w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(headers)


    vnfs_to_reassign = []  # Get all VNFs from the failing server
    
    activeserverlist = []
    inactiveserverlist = []
    inactive_facility_serverlist = []
    for fail in failing_server_id:
        failing_server = servers[fail]
        vnfs_to_reassign += (failing_server.get_vnfs())

    for srv_facility in server_facility:
        check, activeservers, inactiveservers = srv_facility.get_servers_and_facility_status(failing_server_id)
        if check == 1: # if check == 1 => facility is active so keep track of active and inactive servers in that particular facility
            activeserverlist+=activeservers
            inactiveserverlist+=inactiveservers
        else: 
            inactive_facility_serverlist+=inactiveservers

    vnf_preferences = {}
    vnfs_to_be_deployed_in_inactiveservers = []
    server_preferences = {}

#STEP 1 !!! ===> Check if deployment is possible in active servers
    for vnf in vnfs_to_reassign:
        vnf_preferences[vnf.id] = []
        current_sfc = next(sfc for sfc in sfcs if sfc.id == vnf.sfc_id) #finds the sfc corresponding to the particular vnf
        current_servers_deployed = current_sfc.get_deployed_server_list()
        for server in activeserverlist:  # check only active servers
            server_activation_cost =  0
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


        # Sort the servers for each VNF by highest relaibility 
        # Sort w.r.to objective cost of instantiation only if its new data*cost

        if len(vnf_preferences[vnf.id])==0:
            # count+=1
            vnfs_to_be_deployed_in_inactiveservers.append(vnf)
            print(f"No matching found for SFC {current_sfc.id} whose vnf is {vnf.id} in any of the active servers")
        else:
            vnf_preferences[vnf.id].sort(key=lambda x: x[2])

    vnfs_tobe_assigned_activeservers = list(set(vnfs_to_reassign.copy()) - set(vnfs_to_be_deployed_in_inactiveservers.copy()))
    # for server in servers:
    for server in activeserverlist:
        if server.id not in failing_server_id:
            server_preferences[server.id] = []
            # Servers prefer VNFs that can fit into their available resources while maintaining reliability
            for vnf in vnfs_tobe_assigned_activeservers:
                if server.available_resources >= vnf.resources:
                    server_preferences[server.id].append(vnf)
            
            # Sort VNFs by their resource demand (higher order)
            server_preferences[server.id].sort(key=lambda v: v.resources, reverse=True)


    print("VNF Preferences", vnf_preferences)
    print("server prefrences", server_preferences)
    # unassigned_vnfs = vnfs_to_reassign.copy()
    unassigned_vnfs = vnfs_tobe_assigned_activeservers.copy()
    vnf_assignments = {}
    server_assignments = {server.id: [] for server in activeserverlist}
    # server_assignments = {server.id: [] for server in servers}

        
    while unassigned_vnfs:
        vnf = unassigned_vnfs.pop(0)
        vnf_id = vnf.id

        # VNF proposes to its most preferred server
        
        if len(vnf_preferences[vnf_id]) == 0:
            vnfs_to_be_deployed_in_inactiveservers.append(vnf)
            vnfs_tobe_assigned_activeservers.remove(vnf)
            continue
        preferred_server, _, migration_cost, _, _, server_cost, facility_cost = vnf_preferences[vnf_id].pop(0)
        # print(server_assignments[preferred_server.id])
        # If the server can accept the VNF, assign it
        if sum(v.resources for v in server_assignments[preferred_server.id]) + vnf.resources <= preferred_server.available_resources:
            server_assignments[preferred_server.id].append(vnf)
            vnf_assignments[vnf_id] = [preferred_server.id, migration_cost, server_cost, facility_cost] 
        else:
            # If the server is full, reject the least preferred VNF and try again
            rejected_vnf = sorted(server_assignments[preferred_server.id], key=lambda v: v.resources)[0]
            if rejected_vnf.resources < vnf.resources:
                unassigned_vnfs.append(rejected_vnf)
                server_assignments[preferred_server.id].remove(rejected_vnf)
                server_assignments[preferred_server.id].append(vnf)
                vnf_assignments[vnf_id] = [preferred_server.id, migration_cost, server_cost, facility_cost]
            else:
                unassigned_vnfs.append(vnf)
     

    # check_for_inactive_servers()
    vnfs_to_be_deployed_in_inactivefacility = []
    def check_for_inactive_servers(): # If no deployment possible in the inactive servers then we try and deploy in the inactive facilities
        global total_migration_cost
        global new_server_activated
        global new_facility_activated
        for vnf in vnfs_to_be_deployed_in_inactiveservers:
            vnf_preferences[vnf.id] = []
            current_sfc = next(sfc for sfc in sfcs if sfc.id == vnf.sfc_id) #finds the sfc corresponding to the particular vnf
            current_servers_deployed = current_sfc.get_deployed_server_list()
            for server in inactiveserverlist:  # check only active servers
                server_activation_cost =  0
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
                        server.add_pref()  # Keeping a track of the priority of the server
                        vnf_preferences[vnf.id].append((server,  distance_latency, server.get_pref(),cost_of_migration, new_relability,server.id, server_activation_cost, facility_activation_cost))


        # Sort the servers for each VNF by highest relaibility 
        # Sort w.r.to objective cost of instantiation only if its new data*cost

            if len(vnf_preferences[vnf.id])==0:
                vnfs_to_be_deployed_in_inactivefacility.append(vnf)
                print(f"No matching found for SFC {current_sfc.id} whose vnf is {vnf.id} in any of the active servers")
            else:
                vnf_preferences[vnf.id].sort(key=lambda x: x[2])
                flag = 0
                while len(vnf_preferences[vnf.id])!=0:
                    preferred_server, _, _, migration_cost, _, _, server_cost, facility_cost = vnf_preferences[vnf.id].pop()
                    
                    if preferred_server.available_resources>=vnf.resources:
                        if preferred_server.available_resources == preferred_server.total_resources:
                            new_server_activated+=1
                        vnf.change_server_id(preferred_server.id)
                        preferred_server.add_vnf(vnf)
                        preferred_server.add_pref()
                        current_sfc = next(sfc for sfc in sfcs if sfc.id == vnf.sfc_id)
                        total_migration_cost+=migration_cost
                        # Recalculate latency and reliability for the SFC
                        
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
                        flag = 1
                        break
                
                if flag == 0:
                    vnfs_to_be_deployed_in_inactivefacility.append(vnf)

    check_for_inactive_servers()

    def check_for_inactive_facilities():
        global count
        global new_server_activated
        global new_facility_activated
        global total_migration_cost
        for vnf in vnfs_to_be_deployed_in_inactivefacility:
            vnf_preferences[vnf.id] = []
            current_sfc = next(sfc for sfc in sfcs if sfc.id == vnf.sfc_id) #finds the sfc corresponding to the particular vnf
            current_servers_deployed = current_sfc.get_deployed_server_list()
            for server in inactive_facility_serverlist:  # check only active servers
                server_activation_cost =  0
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
                        server.add_pref()
                        vnf_preferences[vnf.id].append((server,  distance_latency, server.get_pref(), cost_of_migration, new_relability,server.id, server_activation_cost, facility_activation_cost))


            if len(vnf_preferences[vnf.id])==0:
                count+=1
                print(f"No matching found for SFC {current_sfc.id} whose vnf is {vnf.id} in any of the servers")
            else:
                vnf_preferences[vnf.id].sort(key=lambda x: x[2])
                while len(vnf_preferences[vnf.id])!=0:
                    preferred_server, _, _, migration_cost, _, _, server_cost, facility_cost = vnf_preferences[vnf.id].pop()

                    if preferred_server.available_resources>=vnf.resources:

                        if preferred_server.available_resources == preferred_server.total_resources:
                            new_server_activated+=1
                        new_server_facility = server_facility[preferred_server.server_facility_id]
                        facility = new_server_facility.get_info()
                        flag=0
                        for srv in facility['server_list']:
                            if len(srv['vnf_list'])!=0:
                                flag=1
                                break
                        if flag==0:
                            new_facility_activated+=1

                        vnf.change_server_id(preferred_server.id)
                        preferred_server.add_vnf(vnf)
                        preferred_server.add_pref()
                        current_sfc = next(sfc for sfc in sfcs if sfc.id == vnf.sfc_id)
                        total_migration_cost+=migration_cost
                        # Recalculate latency and reliability for the SFC
                        
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
                        break

        
        

    check_for_inactive_facilities()

    # print("VNF Preferences", vnf_preferences)
    # print("server prefrences", server_preferences)
    # # unassigned_vnfs = vnfs_to_reassign.copy()
    # unassigned_vnfs = vnfs_tobe_assigned_activeservers.copy()
    # vnf_assignments = {}
    # server_assignments = {server.id: [] for server in activeserverlist}
    # # server_assignments = {server.id: [] for server in servers}

        
    # while unassigned_vnfs:
    #     vnf = unassigned_vnfs.pop(0)
    #     vnf_id = vnf.id

    #     # VNF proposes to its most preferred server
        
    #     if len(vnf_preferences[vnf_id]) == 0:
    #         vnfs_to_be_deployed_in_inactiveservers.append(vnf)
    #         vnfs_tobe_assigned_activeservers.remove(vnf)
    #         continue
    #     preferred_server, _, migration_cost, _, _, server_cost, facility_cost = vnf_preferences[vnf_id].pop(0)
    #     # print(server_assignments[preferred_server.id])
    #     # If the server can accept the VNF, assign it
    #     if sum(v.resources for v in server_assignments[preferred_server.id]) + vnf.resources <= preferred_server.available_resources:
    #         server_assignments[preferred_server.id].append(vnf)
    #         vnf_assignments[vnf_id] = [preferred_server.id, migration_cost, server_cost, facility_cost] 
    #     else:
    #         # If the server is full, reject the least preferred VNF and try again
    #         rejected_vnf = sorted(server_assignments[preferred_server.id], key=lambda v: v.resources)[0]
    #         if rejected_vnf.resources < vnf.resources:
    #             unassigned_vnfs.append(rejected_vnf)
    #             server_assignments[preferred_server.id].remove(rejected_vnf)
    #             server_assignments[preferred_server.id].append(vnf)
    #             vnf_assignments[vnf_id] = [preferred_server.id, migration_cost, server_cost, facility_cost]
    #         else:
    #             unassigned_vnfs.append(vnf)
        

    # Step 4: Redeploy the VNFs and update latency and reliability for the affected SFCs
    for vnf in vnfs_tobe_assigned_activeservers:
        new_server_id, migration_cost, server_cost, facility_cost = vnf_assignments[vnf.id]

        cost_of_migration = migration_cost - server_cost - facility_cost
        new_server = servers[new_server_id]
        new_server_facility = server_facility[new_server.server_facility_id]

        
        vnf.change_server_id(new_server_id)
        new_server.add_vnf(vnf)
        current_sfc = next(sfc for sfc in sfcs if sfc.id == vnf.sfc_id)
        total_migration_cost+=migration_cost
        # Recalculate latency and reliability for the SFC
        
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

    
    
    for fail in failing_server_id:
        failing_server = servers[fail]
        failing_server.server_fail()
    print(f"Total migration cost of vnfs is {total_migration_cost}")
    print(f"Total VNF's that failed realibility factor or latency requirement {count}")
    print(f"Stable matching completed. VNFs from server {failing_server_id} have been reassigned.")

    with open(results_file, mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow([len(failing_server_id),new_facility_activated,new_server_activated,count, 'Stable Matching Count Algortihm', total_migration_cost])
