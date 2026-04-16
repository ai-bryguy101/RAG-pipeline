# OSPF (Open Shortest Path First) — Quick Reference

## What is OSPF?
OSPF is a link-state interior gateway protocol (IGP) used for routing within an autonomous system. Unlike distance-vector protocols (like RIP), OSPF builds a complete map of the network topology and uses Dijkstra's algorithm to calculate the shortest path to every destination.

## Key Concepts

### Areas
OSPF divides networks into areas to reduce routing overhead:
- **Area 0 (Backbone):** All other areas must connect to Area 0. This is mandatory.
- **Stub Areas:** Don't receive external routes — reduces routing table size.
- **NSSA (Not-So-Stubby Area):** Like stub areas but can import limited external routes.

### Router Types
- **Internal Router:** All interfaces in one area
- **ABR (Area Border Router):** Connects two or more areas, always including Area 0
- **ASBR (AS Boundary Router):** Connects OSPF to external routing domains
- **DR/BDR (Designated/Backup Designated Router):** Elected on multi-access networks to reduce adjacency overhead

### OSPF Neighbor States
The OSPF neighbor state machine is critical for troubleshooting:

1. **Down** — No OSPF hello packets received
2. **Init** — Hello received but two-way communication not established
3. **2-Way** — Bidirectional communication confirmed (DR/BDR election happens here)
4. **ExStart** — Master/slave relationship established for database sync
5. **Exchange** — Database Description (DBD) packets exchanged
6. **Loading** — Link-State Requests sent for missing LSAs
7. **Full** — Databases synchronized — adjacency is complete

## Common OSPF Problems

### Stuck in EXSTART/EXCHANGE
**Most common cause:** MTU mismatch between neighbors.
- Verify: `show ip ospf interface` on both sides — MTU must match
- Fix: Set matching MTU or use `ip ospf mtu-ignore` (workaround, not ideal)
- Other causes: Duplicate router IDs, authentication mismatch

### Adjacency Not Forming
Check these match on both sides:
1. Hello/Dead intervals (`ip ospf hello-interval`, `ip ospf dead-interval`)
2. Area ID
3. Authentication type and key
4. Network type (broadcast vs point-to-point)
5. Subnet mask

### Routes Not Appearing
- Check OSPF is advertising the network: `show ip ospf database`
- Verify area configuration: `show ip ospf` 
- Check for route filtering: `show ip prefix-list`, `show route-map`
- Look for duplicate router IDs: `show ip ospf` on all routers

## Essential OSPF Commands (Cisco)
```
show ip ospf neighbor                    # Neighbor table and states
show ip ospf interface brief             # OSPF-enabled interfaces
show ip ospf database                    # Full LSDB
show ip route ospf                       # OSPF routes in routing table
debug ip ospf adj                        # Real-time adjacency debugging
clear ip ospf process                    # Reset OSPF (use cautiously!)
```

## Essential OSPF Commands (Linux/FRRouting)
```
vtysh -c "show ip ospf neighbor"         # Same concepts, different platform
vtysh -c "show ip ospf database"
vtysh -c "show ip ospf interface"
```

## OSPF Design Best Practices
- Keep Area 0 stable and well-connected
- Summarize routes at ABRs to keep routing tables small
- Use point-to-point network types on point-to-point links (avoids DR election)
- Set router-id explicitly — don't let OSPF pick it from an interface
- Use authentication on all OSPF interfaces in production
