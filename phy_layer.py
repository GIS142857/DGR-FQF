from model_config import *
from utils import *
import random


class PhyLayer:
    def __init__(self, node):
        self.layer_name = 'phy'
        self.node = node
        self._current_rx_count = 0
        self._channel_busy_start = 0
        self.total_tx = 0
        self.total_rx = 0
        self.total_collision = 0
        self.total_error = 0
        self.total_bits_tx = 0
        self.total_bits_rx = 0
        self.total_channel_busy = 0
        self.total_channel_tx = 0

    def send_pdu(self, pdu):  # transmit a pdu
        tx_time = (pdu.nbits + PHY_HEADER_LENGTH) * BIT_TRANSMISSION_TIME
        next_node = self.node.sim.nodes[pdu.pdu_des]
        dist = distance(next_node.pos, self.node.pos)
        prop_time = dist * BIT_TRANSPORT_TIME + 1
        self.node.delayed_exec(prop_time, next_node.phy.on_rx_start, pdu)
        self.node.delayed_exec(prop_time + tx_time, next_node.phy.on_rx_end, pdu)

    def on_tx_start(self, pdu):
        pass

    def on_tx_end(self, pdu):
        pass

    def on_rx_start(self, pdu):
        pass

    def on_rx_end(self, pdu):
        prev_node = self.node.sim.nodes[pdu.pdu_src]
        interfere_dist = []
        slot_list = SLOT_LIST[FRAME_SLOT[prev_node.node_id]]
        for node_id in slot_list:
            if node_id == prev_node.node_id:
                continue
            interfere_dist.append(distance(self.node.sim.nodes[node_id].pos, self.node.pos))
        per = getPER(prev_node, self.node, TRANSMITTING_POWER, NOISE_STRENGTH, interfere_dist, BAND_WIDTH)
        # per = 0.2
        # print(per)
        # print(prev_node.node_id, self.node.node_id, dist, per)
        if per:
            self.node.mac.on_receive_pdu(pdu)
            self.total_rx += 1
        else:
            self.total_error += 1

    def on_collision(self, pdu):
        pass

    def cca(self):
        """Return True if the channel is clear"""
        return self._current_rx_count == 0
