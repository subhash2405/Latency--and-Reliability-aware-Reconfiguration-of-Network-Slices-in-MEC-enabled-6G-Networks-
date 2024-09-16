class VNF:
    def __init__(self, id, sfc_id, resources, latency, server_id):
        self.id = id
        self.sfc_id = sfc_id
        self.resources = resources
        self.latency = latency
        self.server_id = server_id
    
    def get_info(self):
        return {
            'id': self.id,
            'sfc_id': self.sfc_id,
            'resources': self.resources,
            'latency': self.latency,
            'server_id': self.server_id
        }

    def change_server_id(self, server):
        self.server_id = server




# class VNF:
#     def __init__(self, id, sfc_id, resources, latency, server_id):
#         self.id = id
#         self.sfc_id = sfc_id
#         self.resources = resources
#         self.latency = latency
#         self.server_id = server_id
    
#     def get_info(self):
#         return {
#             'id': self.id,
#             'sfc_id': self.sfc_id,
#             'resources': self.resources,
#             'latency': self.latency,
#             'server_id': self.server_id
#         }

