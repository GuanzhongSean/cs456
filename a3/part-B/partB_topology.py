#!/usr/bin/python

"""Custom Topology with 3 hosts and 3 switches"""

from mininet.cli import CLI
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel


class CustomTopo(Topo):

    def __init__(self):
        "Create Custom Topology"

        # Initialize topology
        Topo.__init__(self)

        # Add hosts
        alice = self.addHost('alice')
        bob = self.addHost('bob')
        carol = self.addHost('carol')

        # Add switches
        r1 = self.addSwitch('r1')
        r2 = self.addSwitch('r2')
        r3 = self.addSwitch('r3')

        # Add links between hosts and switches
        self.addLink(alice, r1)
        self.addLink(bob, r2)
        self.addLink(carol, r3)

        # Add links between switches
        self.addLink(r1, r2, bw=100)
        self.addLink(r1, r3, bw=100)
        self.addLink(r2, r3, bw=100)


def run():
    "Create and configure network"
    topo = CustomTopo()
    net = Mininet(topo=topo, link=TCLink, controller=None)\

    # Set interface IP and MAC addresses for hosts
    alice = net.get('alice')
    alice.intf('alice-eth0').setIP('10.1.1.17', 24)
    alice.intf('alice-eth0').setMAC('aa:aa:aa:aa:aa:aa')

    bob = net.get('bob')
    bob.intf('bob-eth0').setIP('10.4.4.48', 24)
    bob.intf('bob-eth0').setMAC('b0:b0:b0:b0:b0:b0')

    carol = net.get('carol')
    carol.intf('carol-eth0').setIP('10.6.6.69', 24)
    carol.intf('carol-eth0').setMAC('cc:cc:cc:cc:cc:cc')

    net.start()

    # Add routing table entries for hosts
    alice.cmd('route add default gw 10.1.1.14 dev alice-eth0')
    bob.cmd('route add default gw 10.4.4.14 dev bob-eth0')
    carol.cmd('route add default gw 10.6.6.46 dev carol-eth0')

    # Add arp cache entries for hosts
    alice.cmd('arp -s 10.1.1.14 aa:aa:aa:aa:aa:00 -i alice-eth0')
    bob.cmd('arp -s 10.4.4.14 b0:b0:b0:b0:b0:00 -i bob-eth0')
    carol.cmd('arp -s 10.6.6.46 cc:cc:cc:cc:cc:00 -i carol-eth0')

    # Open Mininet Command Line Interface
    CLI(net)

    # Teardown and cleanup
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
