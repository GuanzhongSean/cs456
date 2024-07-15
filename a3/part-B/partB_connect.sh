#!/usr/bin/env bash

# Sets the protocols for all bridges
for switch in r1 r2 r3; do
    ovs-vsctl set bridge $switch protocols=OpenFlow13
done

# Print the protocols that each switch supports
for switch in r1 r2 r3; do
    protos=$(ovs-vsctl get bridge $switch protocols)
    echo "Switch $switch supports $protos"
done

# Avoid having to write "-O OpenFlow13" before all of your ovs-ofctl commands.
ofctl='ovs-ofctl -O OpenFlow13'

# OVS rules for alice <-> bob
$ofctl add-flow r1 "ip,nw_src=10.1.1.17,nw_dst=10.4.4.48,actions=output:2"
$ofctl add-flow r1 "ip,nw_src=10.4.4.48,nw_dst=10.1.1.17,actions=mod_dl_dst:aa:aa:aa:aa:aa:aa,output=1"

$ofctl add-flow r2 "ip,nw_src=10.1.1.17,nw_dst=10.4.4.48,actions=mod_dl_dst:b0:b0:b0:b0:b0:b0,output=1"
$ofctl add-flow r2 "ip,nw_src=10.4.4.48,nw_dst=10.1.1.17,actions=output:2"

# OVS rules for bob <-> carol
$ofctl add-flow r2 "ip,nw_src=10.4.4.48,nw_dst=10.6.6.69,actions=output:3"
$ofctl add-flow r2 "ip,nw_src=10.6.6.69,nw_dst=10.4.4.48,actions=mod_dl_dst:b0:b0:b0:b0:b0:b0,output=1"

$ofctl add-flow r3 "ip,nw_src=10.4.4.48,nw_dst=10.6.6.69,actions=mod_dl_dst:cc:cc:cc:cc:cc:cc,output=1"
$ofctl add-flow r3 "ip,nw_src=10.6.6.69,nw_dst=10.4.4.48,actions=output:3"

# Ensure alice and carol disconnect
$ofctl add-flow r1 "ip,nw_src=10.1.1.17,nw_dst=10.6.6.69,actions=drop"
$ofctl add-flow r3 "ip,nw_src=10.6.6.69,nw_dst=10.1.1.17,actions=drop"

# Print the flows installed in each switch
for switch in r1 r2 r3; do
    echo "Flows installed in $switch:"
    $ofctl dump-flows $switch
    echo ""
done
