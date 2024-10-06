import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from params.parameters import param
class SFC:
    def __init__(self, id):
        self.id = id
        self.vnf_list = []  
        self.total_resources = 0  
        self.total_latency = 0   # remove vnf latency
        self.total_relaibility = 1
        self.vnf_latency = 0 # remove
        self.maxlatency = 0

    def add_vnf(self, vnf):
        self.vnf_list.append(vnf)
        self.total_resources += vnf.resources
        self.total_latency += vnf.latency
        self.vnf_latency += vnf.latency
        print(f"VNF {vnf.id} added to SFC {self.id}. Total resources: {self.total_resources}, Total latency: {self.total_latency}")

    def add_distance_latency(self, dist):
        self.total_latency += dist

    def max_latency(self, latency):
        self.maxlatency = latency

    def add_relaibility(self, relaibilty):
        self.total_relaibility*=relaibilty
    
    def get_info(self):
        return {
            'id': self.id,
            'vnf_count': len(self.vnf_list),
            'total_resources': self.total_resources,
            'total_latency': self.total_latency,
            'vnf_latency' : self.vnf_latency,
            'max_sfc_latency' : self.maxlatency,
            'total_relaibility' : self.total_relaibility + param.bias,
            'vnf_list': [vnf.get_info() for vnf in self.vnf_list]
        }

    def get_deployed_server_list(self):
        servers = []
        for vnf in self.vnf_list:
            servers.append(vnf.server_id)
        return servers






# class SFC:
#     def __init__(self, id):
#         self.id = id
#         self.vnf_list = []  
#         self.total_resources = 0  
#         self.total_latency = 0  

#     def add_vnf(self, vnf):
#         self.vnf_list.append(vnf)
#         self.total_resources += vnf.resources
#         self.total_latency += vnf.latency
    
#     def get_info(self):
#         return {
#             'id': self.id,
#             'vnf_count': len(self.vnf_list),
#             'total_resources': self.total_resources,
#             'total_latency': self.total_latency,
#             'vnf_list': [vnf.get_info() for vnf in self.vnf_list]
#         }



