# Network Troubleshooting Methodology — Systematic Approach

## The Bottom-Up Approach

Always troubleshoot from the bottom of the TCP/IP stack upward. This prevents you from wasting time debugging application issues when the problem is actually a bad cable. Work through each layer systematically and verify before moving up.

## Layer 1 — Physical Layer Checks

### Cable and Hardware Verification
Check if the link light is on. No link light means either a bad cable, wrong port, or dead NIC. Try a different cable. Try a different port on the switch. Check if the NIC is recognized by the OS: `lspci | grep -i net` or `ip link show`. Look for CRC errors or excessive collisions in `ip -s link show eth0` — these indicate physical layer problems.

### Common Physical Layer Problems
Cable is disconnected or damaged. SFP/transceiver is bad or incompatible. Speed/duplex mismatch between NIC and switch port. NIC driver not loaded or misconfigured. PoE not providing power to the device. Patch panel wired incorrectly.

### Speed and Duplex
Check with `ethtool eth0`. Both sides must agree on speed and duplex. Auto-negotiation usually works, but mismatches happen when one side is hard-coded and the other is auto. A duplex mismatch causes late collisions, poor performance, and intermittent connectivity. Fix: set both sides to auto-negotiate, or hard-code both to the same values.

## Layer 2 — Data Link Layer Checks

### ARP and MAC Address Verification
Can you reach hosts on the same subnet? `ping` the default gateway. If pinging the gateway fails but the link is up, check ARP: `ip neigh show`. If ARP entries are incomplete or missing, the issue is at Layer 2. Check if the switch has the correct MAC address in its table. Check for VLAN misconfiguration — are you in the right VLAN?

### Common Layer 2 Problems
VLAN mismatch — port is in the wrong VLAN. STP blocking — port is in blocking state due to spanning tree. MAC address table overflow or CAM table exhaustion. Duplicate MAC addresses on the network. 802.1Q trunk misconfiguration — allowed VLANs don't match. Broadcast storms caused by loops without STP.

### Switch Troubleshooting
`show mac address-table` — See which MACs are learned on which ports. `show vlan brief` — Verify VLAN assignments. `show spanning-tree` — Check STP port states. `show interfaces status` — Quick view of port state, speed, duplex, VLAN.

## Layer 3 — Network Layer Checks

### IP Configuration Verification
Is the IP address correct? `ip addr show`. Is the subnet mask correct? Wrong mask = can't reach some hosts. Is the default gateway set and correct? `ip route show`. Is the gateway reachable? `ping` the gateway IP. Can you reach hosts on other subnets? If local works but remote fails, it's a routing issue.

### Routing Troubleshooting
`ip route show` — Is there a route to the destination? `ip route get 10.0.0.1` — What path will traffic take to reach 10.0.0.1? `traceroute 10.0.0.1` — Where does the traffic stop? Common issues: missing default route, asymmetric routing (traffic goes out one path, returns another), black hole routes (route exists but next hop is unreachable), route summarization hiding specific routes.

### Common Layer 3 Problems
Wrong IP address or subnet mask configured. Default gateway missing or incorrect. Static route pointing to wrong next hop. Routing protocol not advertising networks. ACL or firewall blocking traffic. MTU issues causing fragmentation or black holes. NAT misconfiguration (inside/outside interfaces swapped, pool exhausted).

### MTU and Fragmentation
Standard Ethernet MTU is 1500 bytes. VPN tunnels reduce effective MTU (IPsec overhead, GRE overhead). Test MTU: `ping -s 1472 -M do 8.8.8.8` — if this fails with "message too long" decrease the size until it works. The working size + 28 (IP + ICMP headers) = your path MTU. Common fix: lower interface MTU or enable MSS clamping for TCP.

## Layer 4 — Transport Layer Checks

### Service Verification
Is the service running? `systemctl status nginx` or `ps aux | grep nginx`. What port is it listening on? `ss -tlnp | grep nginx`. Is it listening on the right address? `0.0.0.0` means all interfaces, `127.0.0.1` means localhost only. Can you connect locally? `curl localhost:80` or `nc -zv localhost 80`.

### Firewall Checks
Is the firewall allowing traffic? `iptables -L -n -v` or `nft list ruleset`. Check for DROP or REJECT rules matching your traffic. Check both INPUT chain (for traffic to this host) and FORWARD chain (for routed traffic). Don't forget: host firewall AND network firewall both need to allow the traffic. Temporarily disable the firewall to test: `iptables -F` (dangerous in production — re-enable immediately).

### Port Connectivity Testing
From the client: `nc -zv server_ip 80` — Test if TCP port 80 is reachable. `telnet server_ip 80` — Also tests TCP connectivity. `nmap -p 80 server_ip` — Port scan with more detail. From the server: `tcpdump -i eth0 port 80` — Watch if packets are arriving at all.

### Common Layer 4 Problems
Service not running or crashed. Service listening on wrong IP/port. Firewall blocking the port. TCP connection timeout (SYN sent but no SYN-ACK returned). Connection refused (RST returned — port not open). SELinux blocking the service (check `audit.log`).

## Layer 7 — Application Layer Checks

### Web Service Testing
`curl -v https://example.com` — Verbose HTTP request showing headers, TLS handshake, response. `curl -I https://example.com` — HEAD request, shows response headers only. `curl -k https://example.com` — Ignore SSL certificate errors (for testing only). Check application logs: `/var/log/nginx/error.log`, `/var/log/apache2/error.log`, application-specific logs.

### TLS/SSL Troubleshooting
`openssl s_client -connect example.com:443` — Test TLS handshake and view certificate details. Check for: expired certificates, wrong hostname on certificate, missing intermediate CA certificates, weak cipher suites, TLS version incompatibility. `openssl x509 -in cert.pem -text -noout` — Inspect a certificate file.

### DNS as an Application Issue
Application can't resolve hostnames even though `dig` works — check `/etc/nsswitch.conf` order. Application using wrong DNS server — check if it has its own DNS config. DNS TTL caching stale records — flush DNS cache on the client.

### Common Application Layer Problems
Misconfigured application (wrong database host, wrong API endpoint). Authentication failure (expired credentials, wrong certificates). DNS resolution failure (works from CLI but not from application). Permission issues (application user can't read config files, SELinux). Resource exhaustion (too many connections, out of memory, disk full).

## Troubleshooting Decision Tree

1. Can you ping your own loopback (127.0.0.1)? No → TCP/IP stack broken, check NIC driver.
2. Can you ping your own IP? No → Interface down or IP misconfigured.
3. Can you ping the default gateway? No → Layer 1/2 issue (cable, VLAN, switch port).
4. Can you ping a remote IP (like 8.8.8.8)? No → Routing or firewall issue.
5. Can you resolve DNS names? No → DNS misconfiguration.
6. Can you reach the service by IP? No → Firewall or service not running.
7. Can you reach the service by name? No → DNS issue for that specific name.
8. Service responds but with errors? → Application layer issue, check logs.

## Useful Quick Diagnostics
`ip a` — Check IPs on all interfaces.
`ip r` — Check routing table.
`ping -c 3 gateway_ip` — Test gateway reachability.
`ping -c 3 8.8.8.8` — Test internet connectivity.
`dig google.com` — Test DNS resolution.
`ss -tlnp` — What's listening?
`iptables -L -n` — What's the firewall doing?
`dmesg | tail -20` — Recent kernel messages (NIC errors, etc.).
`journalctl -u service_name --since "5 minutes ago"` — Recent service logs.
