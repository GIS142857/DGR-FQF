class Packet:
    def __init__(self, src_node_id, des_node_id, packet_id, packet_type, flow_type, stage, priority, length, create_time):
        self.src_node_id = src_node_id
        self.des_node_id = des_node_id
        self.id = packet_id
        self.type = packet_type
        self.flow_type = flow_type
        self.stage = stage
        self.priority = priority
        self.length = length
        self.create_time = round(create_time, 2)
        self.arrival_time = dict()
        self.in_queue_time = dict()
        self.out_queue_time = dict()
        self.trans_path = [src_node_id]
