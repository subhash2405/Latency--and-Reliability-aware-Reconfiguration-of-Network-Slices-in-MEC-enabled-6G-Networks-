class Server:
    def __init__(self, id,server_facility_id, total_resources, reliability, activation_cost):
        self.id = id
        self.server_facility_id = server_facility_id
        self.total_resources = total_resources
        self.available_resources = total_resources
        self.vnf_list = []
        self.reliability = reliability
        #cost of activating that server if vnf list = 0
        self.activation_cost = activation_cost
        

    def add_vnf(self, vnf):
        if vnf.resources <= self.available_resources:
            self.vnf_list.append(vnf)
            self.available_resources -= vnf.resources
            print(f"VNF {vnf.id} assigned to Server {self.id}. Available resources: {self.available_resources}")
        else:
            print(f"Error: Server {self.id} does not have enough resources for VNF {vnf.id}")
            # raise ValueError(f"Server {self.id} does not have enough resources to deploy VNF {vnf.id}")

    def get_info(self):
        return {
            'id': self.id,
            'DeployedinFacility' : self.server_facility_id,
            'ActivationCost' : self.activation_cost,
            'total_resources': self.total_resources,
            'reliability': self.reliability,
            'available_resources': self.available_resources,
            'vnf_count': len(self.vnf_list),
            'vnf_list': [vnf.get_info() for vnf in self.vnf_list]
        }

    def get_vnfs(self):
        return self.vnf_list
    
    def server_fail(self):
        self.available_resources = 0
        self.total_resources = 0
        self.vnf_list = []
        self.reliability = 0


# server ids
# cost of activating facility
# band it is in - nodal, regional , core
# 2 servers per facility


# class Server:
#     def __init__(self, id, total_resources, reliability):
#         self.id = id
#         self.total_resources = total_resources
#         self.available_resources = total_resources
#         self.vnf_list = []
#         self.reliability = reliability

#     def add_vnf(self, vnf):
#         if vnf.resources <= self.available_resources:
#             self.vnf_list.append(vnf)
#             self.available_resources -= vnf.resources
#         else:
#             raise ValueError(f"Server {self.id} does not have enough resources to deploy VNF {vnf.id}")

#     def get_info(self):
#         return {
#             'id': self.id,
#             'total_resources': self.total_resources,
#             'reliability': self.reliability,
#             'available_resources': self.available_resources,
#             'vnf_count': len(self.vnf_list),
#             'vnf_list': [vnf.get_info() for vnf in self.vnf_list]
#         }



