from pdu import PDU
from model_config import *

class MacLayer:
    def __init__(self, node):
        self.layer_name = 'mac'
        self.node = node
        self.flow1_queue = []
        self.flow2_queue = []
        self.flow3_queue = []
        self.total_tx_broadcast = 0
        self.total_tx_unicast = 0
        self.total_rx_broadcast = 0
        self.total_rx_unicast = 0
        self.total_retransmit = 0
        self.total_ack = 0
        self.has_reces = []

    def addPdu(self, mac_pdu, flow_type):
        if flow_type == 'flow1':
            self.flow1_queue.append(mac_pdu)
        elif flow_type == 'flow2':
            self.flow2_queue.append(mac_pdu)
        else:
            self.flow3_queue.append(mac_pdu)

    def process_mac_queue(self):
        while len(self.flow1_queue) + len(self.flow2_queue) + len(self.flow3_queue) > 0:
            send_slot = self.node.time_slot
            wait_time = (self.node.sim.env.now - self.node.sim.start_time) % (self.node.sim.slot_duration * send_slot)
            interval = self.node.sim.slot_duration * send_slot - wait_time
            yield self.node.sim.env.timeout(interval)
            check_pdu_list = []
            if len(self.flow1_queue) > 0:
                check_pdu_list.append(self.flow1_queue[0])
            if len(self.flow2_queue) > 0:
                check_pdu_list.append(self.flow2_queue[0])
            if len(self.flow3_queue) > 0:
                check_pdu_list.append(self.flow3_queue[0])
            max_time = 5*UNIT
            trans_pdu = check_pdu_list[0]
            for pdu in check_pdu_list:
                remain_time = DEADLINE[pdu.payload.flow_type] - self.node.now + pdu.payload.create_time
                if remain_time < max_time:
                    max_time = remain_time
                    trans_pdu = pdu
            trans_pdu.payload.out_queue_time[self.node.node_id] = self.node.now
            self.node.phy.send_pdu(trans_pdu)
            yield self.node.sim.env.timeout(self.node.sim.slot_duration)

    def on_receive_pdu(self, pdu):
        if pdu.pdu_des == self.node.node_id:
            if pdu.payload.id in self.has_reces:
                return
            self.has_reces.append(pdu.payload.id)
            self.node.on_receive_packet(pdu.payload)
            last_node = pdu.pdu_src
            if pdu.payload.flow_type == 'flow1':
                if len(self.node.sim.nodes[last_node].mac.flow1_queue) > 0:
                    self.node.sim.nodes[last_node].mac.flow1_queue.pop(0)
            elif pdu.payload.flow_type == 'flow2':
                if len(self.node.sim.nodes[last_node].mac.flow2_queue) > 0:
                    self.node.sim.nodes[last_node].mac.flow2_queue.pop(0)
            else:
                if len(self.node.sim.nodes[last_node].mac.flow3_queue) > 0:
                    self.node.sim.nodes[last_node].mac.flow3_queue.pop(0)
