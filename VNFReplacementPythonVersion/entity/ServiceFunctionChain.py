class SFC:
    def __init__(self, id):
        self.id = id
        self.vnf_list = []  
        self.total_resources = 0  
        self.total_latency = 0  
        self.total_relaibility = 1

    def add_vnf(self, vnf):
        self.vnf_list.append(vnf)
        self.total_resources += vnf.resources
        self.total_latency += vnf.latency
        print(f"VNF {vnf.id} added to SFC {self.id}. Total resources: {self.total_resources}, Total latency: {self.total_latency}")

    def add_distance_latency(self, dist):
        self.total_latency += dist

    def add_total_relaibility(self, relaibilty):
        self.total_relaibility*=relaibilty
    
    def get_info(self):
        return {
            'id': self.id,
            'vnf_count': len(self.vnf_list),
            'total_resources': self.total_resources,
            'total_latency': self.total_latency,
            'vnf_list': [vnf.get_info() for vnf in self.vnf_list]
        }








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



