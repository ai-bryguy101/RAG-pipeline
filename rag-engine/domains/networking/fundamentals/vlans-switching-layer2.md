# VLANs, Switching, and Layer 2 Technologies

## VLANs (Virtual LANs)

VLANs logically segment a physical switch into multiple broadcast domains. Devices in different VLANs cannot communicate without a Layer 3 device (router or L3 switch).

### Why Use VLANs
Reduce broadcast domain size — fewer broadcasts mean better performance. Security — isolate sensitive traffic (e.g., management, finance, guest Wi-Fi). Flexibility — group users by function rather than physical location. Simplified management — move a user to a different VLAN without re-cabling.

### VLAN Types
Data VLAN: Carries user-generated traffic. Voice VLAN: Dedicated VLAN for VoIP traffic (separate QoS treatment). Management VLAN: Used for switch management traffic (SSH, SNMP, syslog). Native VLAN: Untagged VLAN on a trunk link (default is VLAN 1 — change this for security). Default VLAN: VLAN 1, where all ports start. Cannot be deleted.

### Access Ports vs Trunk Ports
Access Port: Belongs to a single VLAN. Frames are untagged. Used to connect end devices (PCs, printers, phones).
Trunk Port: Carries traffic for multiple VLANs. Frames are tagged with 802.1Q headers (4-byte tag inserted into the Ethernet frame containing the VLAN ID). Used between switches, or between a switch and a router.

### 802.1Q Tagging
The 802.1Q tag is inserted between the source MAC and EtherType fields. It contains: TPID (Tag Protocol Identifier, 0x8100), Priority (3 bits for QoS/CoS), DEI (Drop Eligible Indicator, 1 bit), VLAN ID (12 bits, allowing VLANs 0-4095). VLAN 0 is reserved, VLAN 1 is default, VLANs 1002-1005 are reserved for legacy protocols, VLAN 4095 is reserved. Usable range: 2-1001 (normal range) and 1006-4094 (extended range).

### VLAN Configuration (Cisco)
```
! Create VLANs
vlan 10
 name Engineering
vlan 20
 name Marketing
vlan 99
 name Management

! Configure access port
interface g0/1
 switchport mode access
 switchport access vlan 10

! Configure trunk port
interface g0/24
 switchport mode trunk
 switchport trunk encapsulation dot1q
 switchport trunk allowed vlan 10,20,99
 switchport trunk native vlan 99
 switchport nonegotiate
```

### Inter-VLAN Routing
Method 1 — Router on a Stick: A single router interface with subinterfaces, one per VLAN. Each subinterface has 802.1Q encapsulation and an IP in that VLAN's subnet. Limited by the single physical link's bandwidth.
Method 2 — Layer 3 Switch (SVI): Create Switch Virtual Interfaces (SVIs) for each VLAN on a Layer 3 switch. Each SVI has an IP address and acts as the default gateway for that VLAN. Enable `ip routing` on the switch. More scalable and faster than router-on-a-stick.

### VLAN Troubleshooting
Port not in correct VLAN: `show vlan brief` — verify port assignments. `show interfaces g0/1 switchport` — check mode and VLAN.
Trunk not passing VLANs: `show interfaces trunk` — check allowed VLANs on trunk. Verify both sides have the same allowed VLAN list. Check native VLAN matches on both sides (mismatch causes CDP warnings and connectivity issues).
DTP issues: Disable DTP with `switchport nonegotiate` on all trunk ports. DTP can be exploited in VLAN hopping attacks.

## Spanning Tree Protocol (STP)

STP prevents Layer 2 loops by blocking redundant paths. Without STP, a loop causes a broadcast storm that can crash the network in seconds.

### How STP Works
1. Root Bridge Election: The switch with the lowest Bridge ID (priority + MAC) becomes the root. Default priority is 32768.
2. Root Port Selection: Each non-root switch selects one root port — the port with the lowest cost path to the root bridge.
3. Designated Port Selection: On each segment, one port is selected as the designated port (lowest cost to root from that segment).
4. Blocking: All other redundant ports are placed in blocking state. They don't forward frames but listen for BPDUs.

### STP Port States (802.1D)
Blocking: Not forwarding. Receiving BPDUs only. (20 seconds max)
Listening: Processing BPDUs, participating in topology decisions. (15 seconds — Forward Delay)
Learning: Learning MAC addresses but not yet forwarding. (15 seconds — Forward Delay)
Forwarding: Normal operation, forwarding frames.
Disabled: Administratively disabled.
Total convergence time: Up to 50 seconds (20 + 15 + 15) for a topology change.

### RSTP (Rapid Spanning Tree — 802.1w)
Much faster convergence (typically under 1 second). Port roles: Root, Designated, Alternate (backup root port), Backup (backup designated port). Port states simplified to: Discarding, Learning, Forwarding. Uses proposal/agreement mechanism for fast transitions. Backwards compatible with STP.

### STP Best Practices
Set the root bridge explicitly — don't leave it to chance. Use `spanning-tree vlan 1 root primary` or set a low priority (e.g., 4096). Enable PortFast on access ports (skips listening/learning, goes straight to forwarding). Enable BPDU Guard on PortFast ports (shuts port down if a switch is connected, preventing loops). Enable Root Guard on ports that should never become the root path (prevents rogue switches). Use RSTP (rapid-pvst) instead of legacy STP for faster convergence.

### STP Troubleshooting
`show spanning-tree` — View root bridge, port roles, and states.
`show spanning-tree vlan 10` — STP details for VLAN 10.
`show spanning-tree interface g0/1` — STP state for specific port.
Unexpected root bridge: Check bridge priorities. A new switch with default priority and lower MAC becomes root.
Port stuck in blocking: Could be normal (redundant path). Check if root bridge is correct. Check for unidirectional link failures (use UDLD).

## EtherChannel (Link Aggregation)

EtherChannel bundles multiple physical links into one logical link, increasing bandwidth and providing redundancy.

### EtherChannel Protocols
LACP (Link Aggregation Control Protocol — IEEE 802.3ad): Industry standard. Modes: Active (initiates negotiation) and Passive (responds only). Best practice: use Active on both sides.
PAgP (Port Aggregation Protocol): Cisco proprietary. Modes: Desirable (initiates) and Auto (responds).
Static (mode on): No negotiation protocol. Both sides must be configured identically. Less flexible but works when LACP/PAgP is not supported.

### EtherChannel Requirements
All member ports must have: Same speed and duplex. Same VLAN configuration (access or trunk with same allowed VLANs). Same STP configuration. Same port type (all access or all trunk). Up to 8 active links per EtherChannel (LACP can have 8 active + 8 standby).

### EtherChannel Load Balancing
Traffic is distributed across member links using a hash. Hash inputs can be: src-mac, dst-mac, src-dst-mac, src-ip, dst-ip, src-dst-ip, src-port, dst-port. Choose a method that provides good distribution for your traffic patterns. Check with `show etherchannel load-balance`.

### EtherChannel Troubleshooting
`show etherchannel summary` — Quick status of all EtherChannels (flags: P = bundled, I = standalone, s = suspended, D = down).
`show etherchannel port-channel` — Detailed per-member info.
Channel not forming: Verify both sides use compatible modes (Active/Active, Active/Passive, Desirable/Desirable, etc.). Check that all member port configurations match exactly. Review `show etherchannel detail` for negotiation issues.

## MAC Address Table

### How Switches Learn MAC Addresses
When a frame arrives on a port, the switch records the source MAC address and the port it arrived on. This is stored in the MAC address table (also called CAM table). When forwarding a frame, the switch looks up the destination MAC in its table. If found (unicast), it forwards to that specific port. If not found (unknown unicast), it floods to all ports in the VLAN.

### MAC Table Management
`show mac address-table` — View the entire table.
`show mac address-table dynamic` — Only dynamically learned entries.
`show mac address-table address 0011.2233.4455` — Find a specific MAC.
`show mac address-table interface g0/1` — MACs learned on a specific port.
`clear mac address-table dynamic` — Flush all dynamic entries.
MAC address aging time is typically 300 seconds (5 minutes) by default.

## Port Security

Port security restricts which MAC addresses can use a switch port, preventing unauthorized devices from connecting.

### Port Security Configuration
```
interface g0/1
 switchport mode access
 switchport port-security
 switchport port-security maximum 2
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
```

### Violation Modes
Protect: Drops frames from unauthorized MACs silently. No log, no alert.
Restrict: Drops frames and increments violation counter. Generates SNMP trap and syslog message.
Shutdown: Puts port in err-disabled state. Must be manually re-enabled (`shutdown` then `no shutdown`) or auto-recovered.

### Port Security Troubleshooting
`show port-security` — Overview of all ports with security enabled.
`show port-security interface g0/1` — Detailed info including violation count.
`show port-security address` — All secure MAC addresses.
`show errdisable recovery` — Check if auto-recovery is configured.
