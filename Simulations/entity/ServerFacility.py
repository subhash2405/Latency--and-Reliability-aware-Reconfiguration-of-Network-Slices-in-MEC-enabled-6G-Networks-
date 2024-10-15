import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from params.parameters import param

class Facility:
    def __init__(self, id, band, activation_cost):
        self.id = id
        self.band = band
        self.deployed_servers = []
        self.activation_cost = activation_cost

    def get_info(self):
        return {
            'id': self.id,
            'Band' : self.band,
            'Facility_activation_cost':self.activation_cost,
            'server_count': len(self.deployed_servers),
            'server_list': [server.get_info() for server in self.deployed_servers]
        }
    
    def add_server(self, server):
        self.deployed_servers.append(server)
        print(f"Server {server.id} assigned to Server Facility {self.id}.")

    def get_servers_and_facility_status(self, failing_servers):
        facility = 0
        activeserverlist = []
        inactiveserverlist = []
        for srv in self.deployed_servers:
            if srv.id in failing_servers:
                continue
            if len(srv.get_vnfs()) !=0 :
                facility = 1
                activeserverlist.append(srv)
            else:
                inactiveserverlist.append(srv)
        return facility, activeserverlist, inactiveserverlist


        
    # Bands : Core Band - 1 || Regional Band - 2 || Edge Band - 3