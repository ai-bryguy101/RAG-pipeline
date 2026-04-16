# Network Security — Threats, Defenses, and Hardening

## Common Network Attacks

### Layer 2 Attacks
ARP Spoofing/Poisoning: Attacker sends forged ARP replies, associating their MAC with the gateway's IP. All traffic for the gateway goes through the attacker (man-in-the-middle). Defense: Dynamic ARP Inspection (DAI), static ARP entries for critical hosts.
MAC Flooding: Attacker floods the switch with thousands of fake MAC addresses, filling the CAM table. Once full, the switch falls back to hub behavior (flooding all frames to all ports). Defense: Port security with a maximum MAC address limit.
VLAN Hopping: Attacker exploits DTP (Dynamic Trunking Protocol) to negotiate a trunk link, gaining access to all VLANs. Or uses double-tagging to send frames to a different VLAN than their own. Defense: Disable DTP (`switchport nonegotiate`), set all unused ports to access mode, change the native VLAN away from VLAN 1.
STP Manipulation: Attacker sends superior BPDUs to become the root bridge, allowing them to intercept traffic. Defense: Root Guard on ports where external switches should never be root, BPDU Guard on access ports.
DHCP Starvation: Attacker requests all available IP addresses from the DHCP server, preventing legitimate clients from getting an address. Defense: DHCP Snooping limits the rate of DHCP requests per port.
DHCP Spoofing (Rogue DHCP): Attacker runs a fake DHCP server, giving clients a malicious gateway or DNS server. Defense: DHCP Snooping — only trusted ports (uplinks to real DHCP server) can send DHCP offers.

### Layer 3/4 Attacks
IP Spoofing: Attacker forges the source IP address in packets. Used in DDoS reflection/amplification attacks. Defense: Ingress/egress filtering (BCP38/RFC 2827), uRPF (unicast Reverse Path Forwarding).
ICMP Attacks: Smurf attack (ICMP echo to broadcast address with spoofed source). Ping of death (oversized ICMP packets). ICMP redirect manipulation. Defense: Rate-limit ICMP, disable directed broadcasts, filter ICMP redirects.
TCP SYN Flood: Attacker sends many SYN packets with spoofed source IPs, exhausting the server's half-open connection table. Defense: SYN cookies, rate limiting, connection timeouts, dedicated DDoS mitigation.
DNS Amplification: Attacker sends DNS queries with a spoofed source IP to open resolvers. The large DNS responses overwhelm the target. Defense: Disable open recursion on DNS servers, implement BCP38.
BGP Hijacking: Attacker advertises more-specific prefixes for someone else's IP space, redirecting traffic. Defense: RPKI (Resource Public Key Infrastructure), ROA (Route Origin Authorization), BGP prefix filtering.

## Network Hardening

### Switch Hardening Checklist
Disable unused ports: `shutdown` on all unused interfaces. Put unused ports in a dedicated unused VLAN.
Change the native VLAN: Default VLAN 1 should not be used for any traffic. Set a dedicated native VLAN on all trunks.
Disable DTP: `switchport nonegotiate` on all trunk ports. Set all access ports explicitly: `switchport mode access`.
Enable Port Security: Limit MAC addresses per port. Use sticky MAC learning. Set violation mode to shutdown or restrict.
Enable DHCP Snooping: `ip dhcp snooping` globally, `ip dhcp snooping vlan 10,20`. Mark uplinks as trusted: `ip dhcp snooping trust`.
Enable Dynamic ARP Inspection: `ip arp inspection vlan 10,20`. Trust the uplinks.
Enable IP Source Guard: Prevents IP spoofing on access ports using the DHCP snooping binding table.
Enable BPDU Guard and Root Guard: BPDU Guard on all access ports (PortFast ports). Root Guard on ports facing non-core switches.
Use SSH instead of Telnet: Disable Telnet entirely. `transport input ssh` under VTY lines.
Enable logging: `logging buffered 16384`. Configure syslog to a central server.

### Router/Firewall Hardening
Disable unnecessary services: `no ip http server`, `no cdp run` (if not needed), `no ip source-route`, `no ip directed-broadcast`.
Implement ACLs: Filter traffic at network boundaries. Deny RFC 1918 addresses from the internet. Deny bogon address ranges.
Enable uRPF: `ip verify unicast source reachable-via rx` — drops packets with unreachable source IPs.
Secure management access: Use SSH only (no Telnet). Restrict management access by source IP using ACLs on VTY lines. Use RADIUS/TACACS+ for centralized authentication. Enable exec-timeout on console and VTY lines.
Implement control plane policing: Rate-limit traffic destined to the router itself (BGP, OSPF, SSH, SNMP) to prevent CPU exhaustion.

### Linux Server Hardening
Firewall: Use iptables/nftables/ufw. Default policy should be DROP for INPUT and FORWARD. Only allow necessary services. Use connection tracking (state ESTABLISHED,RELATED).
SSH hardening: Disable root login. Disable password authentication (use keys only). Change default port (optional, defense in depth). Use fail2ban to block brute force attempts.
Minimize attack surface: Disable and remove unnecessary services. Keep software updated (`apt update && apt upgrade`). Use `ss -tlnp` to audit what's listening.
Network parameters (sysctl): `net.ipv4.conf.all.rp_filter = 1` — Enable reverse path filtering. `net.ipv4.conf.all.accept_redirects = 0` — Ignore ICMP redirects. `net.ipv4.conf.all.send_redirects = 0` — Don't send ICMP redirects. `net.ipv4.icmp_echo_ignore_broadcasts = 1` — Ignore broadcast pings. `net.ipv4.tcp_syncookies = 1` — Enable SYN cookies for SYN flood protection.

## AAA (Authentication, Authorization, Accounting)

### RADIUS (Remote Authentication Dial-In User Service)
Uses UDP ports 1812 (authentication) and 1813 (accounting). Encrypts only the password in the access-request. Widely used for network access control (802.1X, VPN, Wi-Fi). Combines authentication and authorization in one step.

### TACACS+ (Terminal Access Controller Access-Control System Plus)
Uses TCP port 49. Encrypts the entire packet body (more secure than RADIUS). Cisco proprietary (but supported by many vendors). Separates authentication, authorization, and accounting (more granular control). Preferred for device administration (router/switch management access).

### 802.1X (Port-Based Network Access Control)
Provides authentication before granting network access. Three roles: Supplicant (client), Authenticator (switch), Authentication Server (RADIUS). The switch blocks all traffic on the port until the client authenticates successfully. If authentication fails, the port can be assigned to a guest VLAN. Commonly uses EAP (Extensible Authentication Protocol) methods: EAP-TLS (certificate-based, most secure), PEAP (password with server certificate), EAP-FAST.

## SNMP (Simple Network Management Protocol)

SNMP is used for monitoring and managing network devices. Uses UDP ports 161 (queries) and 162 (traps).

### SNMP Versions
SNMPv1: Community-based authentication (plaintext). No encryption. Deprecated.
SNMPv2c: Same community strings but adds bulk operations for efficiency. Still no encryption. Widely used despite being insecure.
SNMPv3: Adds authentication (username/password with HMAC) and encryption (AES/DES). Three security levels: noAuthNoPriv, authNoPriv, authPriv (use authPriv for security).

### SNMP Components
MIB (Management Information Base): Hierarchical database of manageable objects on a device. OIDs (Object Identifiers) reference specific data points.
GET: Manager requests a specific OID value from an agent.
SET: Manager changes a value on the agent.
TRAP: Agent sends an unsolicited alert to the manager (link down, high CPU, etc.).
WALK: Manager requests all OIDs in a subtree.

### SNMP Security Best Practices
Use SNMPv3 with authPriv wherever possible. If stuck with v2c, use a long, random community string. Restrict SNMP access by source IP using ACLs. Use read-only community strings for monitoring (no SET access). Change community strings from the default "public" and "private" immediately.

## Syslog

Syslog is the standard for logging system messages across network devices and servers. Uses UDP port 514 (or TCP 514 for reliable delivery).

### Syslog Severity Levels
0 — Emergency: System is unusable. 1 — Alert: Immediate action needed. 2 — Critical: Critical conditions. 3 — Error: Error conditions. 4 — Warning: Warning conditions. 5 — Notice: Normal but significant. 6 — Informational: Informational messages. 7 — Debug: Debug-level messages.
Memory aid: "Every Alley Cat Eats Worthless Noodles In Doors"

### Syslog Best Practices
Send logs to a central syslog server (rsyslog, syslog-ng, Graylog, ELK). Use TCP or TLS for reliable delivery. Set appropriate severity levels (avoid debug in production — too verbose). Include timestamps with timezone. Synchronize time with NTP across all devices.
