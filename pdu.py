class PDU:
    def __init__(self, layer, nbits, packet_type, pdu_src, pdu_des, payload):
        self.layer = layer
        self.nbits = nbits
        self.type = packet_type
        self.pdu_src = pdu_src
        self.pdu_des = pdu_des
        self.payload = payload