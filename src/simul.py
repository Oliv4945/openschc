
from base_import import *
from simsched import SimulScheduler as Scheduler
from simlayer2 import SimulLayer2

import schc

Link = namedtuple("Link", "from_id to_id delay")


SimulNode = SimulLayer2

class SimulLayer3:
    def __init__(self, sim):
        self.sim = sim
        self.protocol = None

    def send_later(self, rel_time, packet):
        self.sim.scheduler.add_event(
            rel_time, self.protocol.event_receive_from_L3, (packet,))

    def _set_protocol(self, protocol): # called by [New]SCHCProtocol
        self.protocol = protocol


class SimulNode: # object
    pass

class SimulSCHCNode(SimulNode):
    def __init__(self, sim, extra_config={}):
        self.sim = sim
        self.config = sim.simul_config.get("node-config", {}).copy()
        self.config.update(extra_config)

        self.layer2 = SimulLayer2(sim)
        self.layer3 = SimulLayer3(sim)
        self.protocol = schc.NewSCHCProtocol(
            self.config, sim.scheduler, self.layer2, self.layer3)
        self.id = self.layer2.mac_id
        self.sim._add_node(self)

    def event_receive(self, sender_id, packet):
        self.layer2.event_receive_packet(sender_id, packet)


class SimulNullNode(SimulNode):
    pass


class Simul:
    def __init__(self, simul_config = {}):
        self.simul_config = simul_config
        self.node_table = {}
        self.link_set = set()
        self.event_id = 0
        self.scheduler = Scheduler()
        self.log_file = None

    def set_log_file(self, filename):
        self.log_file = open(filename, "w")

    def log(self, name, message): # XXX: put Soichi type of logging
        if not self.simul_config.get("log", False):
            return
        line = "{} [{}] ".format(self.scheduler.get_time(), name) + message
        print(line)
        if self.log_file != None:
            self.log_file.write(line+"\n")

    # XXX:optimize
    def get_link_by_id(self, src_id=None, dst_id=None):
        result = []
        for link in sorted(self.link_set):
            if (     ((src_id is None) or (link.from_id == src_id))
                 and ((dst_id is None) or (link.to_id == dst_id))):
                result.append(link)
        return result

    def send_packet(self, packet, src_id, dst_id=None,
                    callback=None, callback_args=tuple() ):
        self.log("simul", "send packet {}->{}".format(src_id, dst_id))
        # if dst_id == None, it is a broadcast
        link_list = self.get_link_by_id(src_id, dst_id)
        count = 0
        for link in link_list:
            count += self.send_packet_on_link(link, packet)
        if callback != None:
            args = callback_args+(count,)
            callback(*args)
        return count

    def send_packet_on_link(self, link, packet):
        node_to = self.node_table[link.to_id]
        node_to.event_receive(link.from_id, packet)
        return 1   # 1 -> one packet was sent

    def add_link(self, from_node, to_node, delay=1):
        """Create a link from from_id to to_id.
        Transmitted packets on the link will have a the specified delay
        before being received"""
        assert (from_node.id in self.node_table
                and to_node.id in self.node_table)
        link = Link(from_id=from_node.id, to_id=to_node.id, delay=delay)
        # XXX: check not another link there with same from_id, same to_id
        self.link_set.add(link)

    def add_sym_link(self, from_node, to_node, delay=1):
        """Create a symmetrical link between the two nodes, by creating two
        unidirectional links"""
        self.add_link(from_node, to_node, delay)
        self.add_link(to_node, from_node, delay)

    # don't call: automatically called by Node(...)
    def _add_node(self, node):
        """Internal: add a node in the node_table
        (automatically called by Node constructor)"""
        assert node.id not in self.node_table
        self.node_table[node.id] = node

    def run(self):
        self.scheduler.run()

#---------------------------------------------------------------------------
