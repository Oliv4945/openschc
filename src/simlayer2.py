

class SimulLayer2:
    mac_id = 0

    def __init__(self, sim):
        self.sim = sim
        self.protocol = None
        self.mac_id = SimulLayer2.__get_unique_mac_id()
        self.receive_function = None
        self.event_timeout = None
        self.counter = 1 # XXX: replace with is_transmitting?
        self.is_transmitting = False
        self.packet_queue = []

    def _set_protocol(self, protocol):
        self.protocol = protocol

    def set_receive_callback(self, receive_function):
        self.receive_function = receive_function

    def send_packet(self, packet, src_dev_id, dst_dev_id=None,
                    transmit_callback=None):
        self.packet_queue.append((packet, src_dev_id, dst_dev_id,
                                  transmit_callback))

        if not self.is_transmitting:
            self._send_packet_from_queue()

    def _send_packet_from_queue(self):
        assert not self.is_transmitting
        assert len(self.packet_queue) > 0
        (packet, src_dev_id, dst_dev_id, transmit_callback
        ) = self.packet_queue.pop(0)
        print(transmit_callback, "AAAAAAA")
        self.sim.send_packet(packet, dst_dev_id, None,
                             self._event_sent_callback, (transmit_callback,))
        #self.counter -= 1
        #if self.counter < 0:
        #    return
        #for other in self.link_list:
        #    self.scheduler.add_event(self.delay, other.event_receive_packet,
        #                             (other.mac_id, packet))

    def _event_sent_callback(self, transmit_callback):
        assert self.is_transmitting
        self.is_transmitting = False
        if transmit_callback != None:
            transmit_callback()

    def event_receive_packet(self, other_mac_id, packet):
        #if self.receive_function != None:
        #    self.receive_function(other_mac_id, packet)
        #else:
        #    self.node.log("%s SimulLayer2: %s->%s %s ".format(
        #        (self.scheduler.get_time(),
        #         self.mac_id, other_mac_id, packet)))
        # XXX: log and checks
        #XXX
        assert self.protocol != None
        self.protocol.event_receive_from_L2(other_mac_id, packet)

    def __get_unique_mac_id():
        result = SimulLayer2.mac_id
        SimulLayer2.mac_id += 1
        return result

    def get_mtu_size(self):
        return 56   # XXX
