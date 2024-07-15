## OVS Rule Explanation

```bash
$ofctl add-flow s0 \
    in_port=1,ip,nw_src=10.0.0.2,nw_dst=10.0.1.2,actions=mod_dl_src:0A:00:0A:01:00:02,mod_dl_dst:0A:00:0A:FE:00:02,output=2
```

#### Field Explanations

1. **`s0`**: Specifies that the flow rule will be added to the switch `s0`.

2. **`in_port=1`**: Specifies that the flow rule should match packets entering the switch on port 1.

3. **`ip`**: Indicates that the rule applies to IP packets.

4. **`nw_src=10.0.0.2`**: Specifies the source IP address to match.

5. **`nw_dst=10.0.1.2`**: Specifies the destination IP address to match.

6. **`actions=mod_dl_src:0A:00:0A:01:00:02,mod_dl_dst:0A:00:0A:FE:00:02`**:
    - **`mod_dl_src`**: Specifies the source MAC address of the packet.
    - **`mod_dl_dst`**: Specifies the destination MAC address of the packet.

7. **`output=2`**: Specifies the output port.
