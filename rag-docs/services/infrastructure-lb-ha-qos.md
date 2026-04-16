# Network Infrastructure — Load Balancing, HA, and QoS

## Load Balancing

Load balancing distributes traffic across multiple servers to improve availability, reliability, and performance.

### Load Balancing Algorithms
Round Robin: Distributes requests sequentially across servers. Simple but doesn't account for server load or capacity.
Weighted Round Robin: Like round robin but assigns more requests to higher-capacity servers. Server A (weight 3) gets 3 requests for every 1 request to Server B (weight 1).
Least Connections: Sends new requests to the server with the fewest active connections. Better for variable-length requests.
Weighted Least Connections: Combines least connections with server weights.
IP Hash: Uses a hash of the client's IP to determine which server to use. Ensures the same client always reaches the same server (session persistence without cookies).
Least Response Time: Routes to the server with the fastest response time. Requires active health monitoring.

### Layer 4 vs Layer 7 Load Balancing
Layer 4 (Transport): Makes decisions based on IP address and TCP/UDP port. Very fast (operates at the packet level). Cannot inspect application data. Examples: HAProxy TCP mode, Linux IPVS, AWS NLB.
Layer 7 (Application): Makes decisions based on application data (HTTP headers, URL path, cookies). Can do content-based routing (send /api to API servers, /static to CDN). Can modify requests/responses (add headers, rewrite URLs). More CPU-intensive. Examples: HAProxy HTTP mode, Nginx, AWS ALB, Envoy.

### Health Checks
Load balancers periodically check if backend servers are healthy. TCP check: Can a TCP connection be established? (basic, fast). HTTP check: Does the server return a 200 OK for a specific URL? (validates application health). Custom check: Application-specific health endpoint that checks database, disk, dependencies. Unhealthy servers are automatically removed from the pool and re-added when they recover.

### HAProxy Basic Configuration
```
frontend http_front
    bind *:80
    default_backend http_back

backend http_back
    balance roundrobin
    option httpchk GET /health
    server web1 192.168.1.10:80 check
    server web2 192.168.1.11:80 check
    server web3 192.168.1.12:80 check
```

### Session Persistence (Sticky Sessions)
Some applications require a client to consistently reach the same backend server (e.g., shopping carts, session state). Methods: Source IP affinity (all requests from same IP go to same server). Cookie-based persistence (load balancer inserts or reads a cookie). Application cookie (the application sets its own session cookie). Trade-off: persistence improves application correctness but reduces load distribution efficiency.

## High Availability (HA)

### VRRP (Virtual Router Redundancy Protocol)
Creates a virtual IP address shared between two or more routers. One router is the master (active), others are backup. If the master fails, a backup takes over the virtual IP within seconds. Clients use the virtual IP as their default gateway — failover is transparent. Cisco's implementation is HSRP (Hot Standby Router Protocol), which works similarly.

### HSRP (Hot Standby Router Protocol — Cisco)
`interface g0/0` → `standby 1 ip 192.168.1.1` — Virtual IP address.
`standby 1 priority 110` — Higher priority = preferred active router (default 100).
`standby 1 preempt` — Take over if this router has higher priority than current active.
`standby 1 track g0/1 20` — Reduce priority by 20 if g0/1 goes down (triggers failover).
`show standby` — Verify HSRP state and which router is active.

### Keepalived (Linux VRRP)
Configuration (`/etc/keepalived/keepalived.conf`):
```
vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass secretpass
    }
    virtual_ipaddress {
        192.168.1.1/24
    }
}
```
Manage: `systemctl start keepalived`. Monitor: `journalctl -u keepalived`.

### Link Aggregation for HA
Bonding multiple network interfaces provides both increased bandwidth and redundancy. Linux bonding modes: Mode 0 (balance-rr): Round-robin across interfaces. Mode 1 (active-backup): One active, one standby. Most common for HA. Mode 2 (balance-xor): XOR hash of source/destination MAC. Mode 4 (802.3ad/LACP): Dynamic link aggregation with switch support. Best for both bandwidth and HA. Mode 5 (balance-tlb): Adaptive transmit load balancing. Mode 6 (balance-alb): Adaptive load balancing (both TX and RX).

## QoS (Quality of Service)

QoS prioritizes certain types of traffic over others when network resources are constrained.

### Why QoS Matters
Voice (VoIP) requires latency under 150ms and jitter under 30ms. Video conferencing needs consistent bandwidth with minimal packet loss. Bulk file transfers can tolerate delay but shouldn't starve interactive traffic. Without QoS, all traffic is treated equally and voice/video quality degrades during congestion.

### QoS Mechanisms
Classification: Identifying traffic types. Methods include DSCP (Differentiated Services Code Point) markings in the IP header, ACLs matching source/destination/port, NBAR (Network Based Application Recognition) for deep packet inspection.
Marking: Tagging packets with priority values. Layer 2: CoS (Class of Service) in 802.1Q tag (3 bits, values 0-7). Layer 3: DSCP in IP header (6 bits, values 0-63).
Queuing: Multiple queues with different priorities. Strict Priority Queue (SPQ): High-priority queue is always served first. Can starve lower queues. Weighted Fair Queuing (WFQ): Allocates bandwidth proportionally. Class-Based WFQ (CBWFQ): Administrator-defined classes with guaranteed bandwidth. Low-Latency Queuing (LLQ): CBWFQ with a strict priority queue for voice. Most common enterprise QoS model.
Policing and Shaping: Policing drops or re-marks traffic that exceeds a rate limit (hard enforcement). Shaping buffers excess traffic and sends it when bandwidth is available (smooth, but adds latency).

### Common DSCP Values
EF (Expedited Forwarding, 46): Voice traffic. Highest priority, low latency. AF41 (34): Video conferencing. AF31 (26): Streaming video. AF21 (18): Transactional data (database, ERP). CS1 (8): Scavenger/bulk (backups, software updates). BE/CS0 (0): Best effort (default, everything else).

### QoS Troubleshooting
`show policy-map interface g0/0` (Cisco) — See QoS policy statistics per class.
`tc -s qdisc show dev eth0` (Linux) — Show traffic control queue statistics.
`tc -s class show dev eth0` (Linux) — Show per-class statistics.
Look for: Drops in priority queues (queue too small). Police drops (traffic exceeding rate limits). Queue depth growing (congestion building).

## Network Monitoring

### Key Metrics to Monitor
Bandwidth utilization: How full are your links? >70% sustained = plan for upgrades. Latency: Round-trip time between key points. Baseline and alert on deviations. Packet loss: Any sustained loss above 0.1% affects quality. Jitter: Variation in latency. Critical for voice/video. Error rates: CRC errors, frame errors, collisions indicate physical issues. CPU/memory on network devices: High utilization can cause packet drops.

### Monitoring Tools
SNMP-based: Zabbix, PRTG, LibreNMS, Cacti. Poll devices via SNMP for interface stats, CPU, memory. Flow-based: NetFlow, sFlow, IPFIX. Analyze traffic patterns, top talkers, application usage. Tools: ntopng, Elastiflow, SolarWinds. Ping-based: Smokeping (latency and loss trending), Nagios/Icinga (up/down monitoring). Log-based: ELK stack (Elasticsearch, Logstash, Kibana), Graylog. Centralize syslog, firewall logs, application logs for correlation.

### SNMP Monitoring Commands
`snmpwalk -v2c -c public 192.168.1.1 ifDescr` — List interfaces on a device.
`snmpwalk -v2c -c public 192.168.1.1 ifInOctets` — Inbound byte counters.
`snmpwalk -v2c -c public 192.168.1.1 ifOutOctets` — Outbound byte counters.
`snmpget -v2c -c public 192.168.1.1 sysUpTime.0` — Device uptime.
