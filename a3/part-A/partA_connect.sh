#!/usr/bin/env bash

# Sets the protocols for all bridges
for switch in s0 s1 s2 s3 s4 s6; do
    ovs-vsctl set bridge $switch protocols=OpenFlow13
done

# Print the protocols that each switch supports
for switch in s0 s1 s2 s3 s4 s6; do
    protos=$(ovs-vsctl get bridge $switch protocols)
    echo "Switch $switch supports $protos"
done

# Avoid having to write "-O OpenFlow13" before all of your ovs-ofctl commands.
ofctl='ovs-ofctl -O OpenFlow13'

# OVS rules for h1 <-> h4
# s1 port3 to s2 port3
$ofctl add-flow s1 \
    in_port=1,ip,nw_src=10.0.1.2,nw_dst=10.0.4.2,actions=mod_dl_src:0A:00:0C:01:00:03,mod_dl_dst:0A:00:0D:01:00:03,output=3
# s1 port1 to h1
$ofctl add-flow s1 \
    in_port=3,ip,nw_src=10.0.4.2,nw_dst=10.0.1.2,actions=mod_dl_src:0A:00:01:01:00:01,mod_dl_dst:0A:00:01:02:00:00,output=1
# s2 port4 to s3 port2
$ofctl add-flow s2 \
    in_port=3,ip,nw_src=10.0.1.2,nw_dst=10.0.4.2,actions=mod_dl_src:0A:00:0C:FE:00:04,mod_dl_dst:0A:00:0D:FE:00:02,output=4
# s2 port3 to s1 port3
$ofctl add-flow s2 \
    in_port=4,ip,nw_src=10.0.4.2,nw_dst=10.0.1.2,actions=mod_dl_src:0A:00:0D:01:00:03,mod_dl_dst:0A:00:0C:01:00:03,output=3
# s3 port3 to s4 port2
$ofctl add-flow s3 \
    in_port=2,ip,nw_src=10.0.1.2,nw_dst=10.0.4.2,actions=mod_dl_src:0A:00:0E:01:00:03,mod_dl_dst:0A:00:0E:FE:00:02,output=3
# s3 port2 to s2 port4
$ofctl add-flow s3 \
    in_port=3,ip,nw_src=10.0.4.2,nw_dst=10.0.1.2,actions=mod_dl_src:0A:00:0D:FE:00:02,mod_dl_dst:0A:00:0C:FE:00:04,output=2
# s4 port1 to h4
$ofctl add-flow s4 \
    in_port=2,ip,nw_src=10.0.1.2,nw_dst=10.0.4.2,actions=mod_dl_src:0A:00:04:01:00:01,mod_dl_dst:0A:00:04:02:00:00,output=1
# s4 port2 to s3 port3
$ofctl add-flow s4 \
    in_port=1,ip,nw_src=10.0.4.2,nw_dst=10.0.1.2,actions=mod_dl_src:0A:00:0E:FE:00:02,mod_dl_dst:0A:00:0E:01:00:03,output=2

# OVS rules for h2 <-> h0
# s0 port1 to h0
$ofctl add-flow s0 \
    in_port=3,ip,nw_src=10.0.2.2,nw_dst=10.0.0.2,actions=mod_dl_src:0A:00:00:01:00:01,mod_dl_dst:0A:00:00:02:00:00,output=1
# s0 port3 to s2 port2
$ofctl add-flow s0 \
    in_port=1,ip,nw_src=10.0.0.2,nw_dst=10.0.2.2,actions=mod_dl_src:0A:00:0B:01:00:03,mod_dl_dst:0A:00:0B:FE:00:02,output=3
# s2 port2 to s0 port3
$ofctl add-flow s2 \
    in_port=1,ip,nw_src=10.0.2.2,nw_dst=10.0.0.2,actions=mod_dl_src:0A:00:0B:FE:00:02,mod_dl_dst:0A:00:0B:01:00:03,output=2
# s2 port1 to h2
$ofctl add-flow s2 \
    in_port=2,ip,nw_src=10.0.0.2,nw_dst=10.0.2.2,actions=mod_dl_src:0A:00:02:01:00:01,mod_dl_dst:0A:00:02:02:00:00,output=1

# OVS rules for h3 <-> h6
# s3 port4 to s6 port2
$ofctl add-flow s3 \
    in_port=1,ip,nw_src=10.0.3.2,nw_dst=10.0.6.2,actions=mod_dl_src:0A:00:0F:01:00:04,mod_dl_dst:0A:00:0F:FE:00:02,output=4
# s3 port1 to h3
$ofctl add-flow s3 \
    in_port=4,ip,nw_src=10.0.6.2,nw_dst=10.0.3.2,actions=mod_dl_src:0A:00:03:01:00:01,mod_dl_dst:0A:00:03:02:00:00,output=1
# s6 port1 to h6
$ofctl add-flow s6 \
    in_port=2,ip,nw_src=10.0.3.2,nw_dst=10.0.6.2,actions=mod_dl_src:0A:00:06:01:00:01,mod_dl_dst:0A:00:06:02:00:00,output=1
# s6 port2 to s3 port4
$ofctl add-flow s6 \
    in_port=1,ip,nw_src=10.0.6.2,nw_dst=10.0.3.2,actions=mod_dl_src:0A:00:0F:FE:00:02,mod_dl_dst:0A:00:0F:01:00:04,output=2

# Print the flows installed in each switch
for switch in s0 s1 s2 s3 s4 s6; do
    echo "Flows installed in $switch:"
    $ofctl dump-flows $switch
    echo ""
done
