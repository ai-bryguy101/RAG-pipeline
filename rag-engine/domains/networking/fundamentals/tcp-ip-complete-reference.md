# TCP/IP Protocol Suite — Complete Reference

## The TCP/IP Model

The TCP/IP model is a four-layer conceptual framework for understanding network communication. It differs from the OSI model by combining some layers and being more practically oriented.

### Layer 1 — Network Access (Link Layer)
Handles the physical transmission of data over a specific medium (Ethernet, Wi-Fi, etc.). Responsible for framing, MAC addressing, and media access control. Key protocols include Ethernet (IEEE 802.3), Wi-Fi (IEEE 802.11), ARP (Address Resolution Protocol), and PPP (Point-to-Point Protocol).

### Layer 2 — Internet Layer
Handles logical addressing and routing of packets between networks. The primary protocol is IP (Internet Protocol). Also includes ICMP (Internet Control Message Protocol) for error reporting and diagnostics, and IGMP (Internet Group Management Protocol) for multicast group management.

### Layer 3 — Transport Layer
Provides end-to-end communication between applications. Two main protocols: TCP (Transmission Control Protocol) for reliable, ordered delivery and UDP (User Datagram Protocol) for fast, connectionless delivery.

### Layer 4 — Application Layer
Provides network services directly to user applications. Includes HTTP, HTTPS, FTP, SSH, DNS, DHCP, SMTP, SNMP, and many others.

## TCP (Transmission Control Protocol)

TCP provides reliable, ordered, error-checked delivery of data between applications. It is connection-oriented, meaning a connection must be established before data transfer.

### TCP Three-Way Handshake
The connection establishment process:
1. SYN: Client sends a SYN (synchronize) packet to the server with a random initial sequence number (ISN).
2. SYN-ACK: Server responds with SYN-ACK, acknowledging the client's ISN and sending its own ISN.
3. ACK: Client sends ACK acknowledging the server's ISN. Connection is now established.

### TCP Four-Way Teardown
The connection termination process:
1. FIN: Initiating side sends FIN (finish) flag.
2. ACK: Receiving side acknowledges the FIN.
3. FIN: Receiving side sends its own FIN when ready to close.
4. ACK: Initiating side acknowledges the final FIN. Connection closed after TIME_WAIT.

### TCP Flow Control
TCP uses a sliding window mechanism to control data flow. The receiver advertises a window size indicating how much data it can buffer. The sender must not send more data than the receiver's window allows. Window scaling (RFC 7323) allows window sizes larger than 65535 bytes.

### TCP Congestion Control
TCP implements several congestion control mechanisms: Slow Start begins with a small congestion window (cwnd) and doubles it each RTT. Congestion Avoidance increases cwnd linearly after reaching the slow start threshold (ssthresh). Fast Retransmit retransmits lost segments upon receiving three duplicate ACKs. Fast Recovery avoids going back to slow start after fast retransmit.

### TCP Flags
SYN — Initiates connection. ACK — Acknowledges received data. FIN — Initiates graceful connection close. RST — Abruptly resets connection. PSH — Push data to application immediately. URG — Urgent data pointer is valid.

### Common TCP Issues
Retransmissions indicate packet loss, typically caused by congestion, buffer overflow, or faulty links. Zero window means the receiver's buffer is full and it cannot accept more data. RST floods may indicate a port scan or application crash. High RTT (Round Trip Time) suggests network latency or congestion. Out-of-order packets suggest multiple paths or network instability.

## UDP (User Datagram Protocol)

UDP is connectionless and provides no guarantee of delivery, ordering, or duplicate protection. It has lower overhead than TCP and is used for time-sensitive applications.

### UDP Header
Source Port (16 bits), Destination Port (16 bits), Length (16 bits), Checksum (16 bits). Total header size is only 8 bytes compared to TCP's minimum 20 bytes.

### When to Use UDP vs TCP
Use UDP for: real-time streaming (audio/video), DNS queries, DHCP, SNMP, online gaming, VoIP. Use TCP for: web browsing (HTTP/HTTPS), email (SMTP/IMAP), file transfer (FTP/SFTP), SSH, database connections.

## IP Addressing (IPv4)

### IPv4 Address Structure
An IPv4 address is 32 bits, written as four octets in dotted decimal notation (e.g., 192.168.1.100). Each octet ranges from 0 to 255.

### Address Classes (Historical)
Class A: 1.0.0.0 to 126.255.255.255, default mask /8. Class B: 128.0.0.0 to 191.255.255.255, default mask /16. Class C: 192.0.0.0 to 223.255.255.255, default mask /24. Class D: 224.0.0.0 to 239.255.255.255, multicast. Class E: 240.0.0.0 to 255.255.255.255, experimental.

### Private IP Ranges (RFC 1918)
10.0.0.0/8 (10.0.0.0 — 10.255.255.255). 172.16.0.0/12 (172.16.0.0 — 172.31.255.255). 192.168.0.0/16 (192.168.0.0 — 192.168.255.255). These addresses are not routable on the public internet and require NAT for external communication.

### Special Addresses
127.0.0.0/8 — Loopback (localhost). 169.254.0.0/16 — Link-local / APIPA (auto-assigned when DHCP fails). 0.0.0.0 — Default route / unspecified address. 255.255.255.255 — Limited broadcast.

## Subnetting

### CIDR Notation
CIDR (Classless Inter-Domain Routing) uses a prefix length to define the network portion. For example, 192.168.1.0/24 means the first 24 bits are the network address, leaving 8 bits for host addresses (254 usable hosts).

### Subnet Mask Quick Reference
/8 = 255.0.0.0 (16,777,214 hosts). /16 = 255.255.0.0 (65,534 hosts). /24 = 255.255.255.0 (254 hosts). /25 = 255.255.255.128 (126 hosts). /26 = 255.255.255.192 (62 hosts). /27 = 255.255.255.224 (30 hosts). /28 = 255.255.255.240 (14 hosts). /29 = 255.255.255.248 (6 hosts). /30 = 255.255.255.252 (2 hosts, used for point-to-point links). /31 = 255.255.255.254 (2 hosts, RFC 3021, no broadcast). /32 = 255.255.255.255 (host route).

### How to Subnet
To determine the network address: perform a bitwise AND of the IP address and subnet mask. To determine the broadcast address: set all host bits to 1. To determine the usable host range: the network address + 1 is the first host, the broadcast address - 1 is the last host.

### Subnetting Example
Given 192.168.10.0/24, create 4 subnets: Borrow 2 bits from the host portion, giving /26. Subnet 1: 192.168.10.0/26 (hosts .1 — .62, broadcast .63). Subnet 2: 192.168.10.64/26 (hosts .65 — .126, broadcast .127). Subnet 3: 192.168.10.128/26 (hosts .129 — .190, broadcast .191). Subnet 4: 192.168.10.192/26 (hosts .193 — .254, broadcast .255).

## IPv6

### IPv6 Address Format
128-bit addresses written as eight groups of four hexadecimal digits separated by colons. Example: 2001:0db8:85a3:0000:0000:8a2e:0370:7334. Leading zeros in each group can be omitted. Consecutive groups of all zeros can be replaced with :: (once per address).

### IPv6 Address Types
Global Unicast: 2000::/3 — Routable on the internet (like public IPv4). Link-Local: fe80::/10 — Automatically assigned, used for local communication only. Unique Local: fc00::/7 — Similar to RFC 1918 private addresses. Multicast: ff00::/8 — One-to-many communication. Loopback: ::1/128 — Equivalent to 127.0.0.1 in IPv4.

### IPv6 Neighbor Discovery Protocol (NDP)
NDP replaces ARP in IPv6. Router Solicitation (RS): Hosts request router information. Router Advertisement (RA): Routers announce their presence and network configuration. Neighbor Solicitation (NS): Used to resolve IPv6 addresses to MAC addresses. Neighbor Advertisement (NA): Response to NS with MAC address. Redirect: Routers inform hosts of a better first hop.

### IPv6 Autoconfiguration (SLAAC)
Stateless Address Autoconfiguration allows hosts to configure their own IPv6 address without DHCP. The host combines the network prefix from Router Advertisements with its own interface identifier (typically derived from the MAC address using EUI-64 or a random privacy address per RFC 4941).

## ARP (Address Resolution Protocol)

ARP resolves IPv4 addresses to MAC addresses on a local network segment. When a host needs to send a frame to an IP address on its subnet, it broadcasts an ARP request asking "who has this IP?" The host with that IP responds with its MAC address.

### ARP Process
1. Host checks its ARP cache for the destination MAC.
2. If not found, host sends an ARP Request broadcast (destination MAC ff:ff:ff:ff:ff:ff).
3. The target host responds with an ARP Reply (unicast) containing its MAC address.
4. The requesting host caches the result (typically for 60-300 seconds).

### ARP Table Commands
Linux: `ip neigh show` or `arp -a` to view, `ip neigh flush all` to clear. Windows: `arp -a` to view, `arp -d *` to clear. Cisco: `show arp` to view, `clear arp` to clear.

### ARP Security Concerns
ARP Spoofing/Poisoning: An attacker sends fake ARP replies to associate their MAC address with another host's IP, enabling man-in-the-middle attacks. Mitigation includes Dynamic ARP Inspection (DAI) on switches, static ARP entries for critical hosts, and network segmentation.

## ICMP (Internet Control Message Protocol)

ICMP provides error reporting and diagnostic functions for IP. It is used by ping and traceroute.

### Common ICMP Types
Type 0: Echo Reply (ping response). Type 3: Destination Unreachable (with various codes — network unreachable, host unreachable, port unreachable, fragmentation needed, etc.). Type 5: Redirect (router tells host to use a different gateway). Type 8: Echo Request (ping). Type 11: Time Exceeded (TTL expired, used by traceroute).

### ICMP Destination Unreachable Codes
Code 0: Network unreachable. Code 1: Host unreachable. Code 2: Protocol unreachable. Code 3: Port unreachable. Code 4: Fragmentation needed but DF (Don't Fragment) bit set — important for Path MTU Discovery.

## Common Port Numbers

### Well-Known Ports (0-1023)
20/21 TCP — FTP (data/control). 22 TCP — SSH. 23 TCP — Telnet. 25 TCP — SMTP. 53 TCP/UDP — DNS. 67/68 UDP — DHCP (server/client). 69 UDP — TFTP. 80 TCP — HTTP. 110 TCP — POP3. 123 UDP — NTP. 143 TCP — IMAP. 161/162 UDP — SNMP. 389 TCP — LDAP. 443 TCP — HTTPS. 514 UDP — Syslog. 636 TCP — LDAPS.

### Registered Ports (1024-49151)
1433 TCP — Microsoft SQL Server. 1521 TCP — Oracle DB. 3306 TCP — MySQL. 3389 TCP — RDP. 5432 TCP — PostgreSQL. 5900 TCP — VNC. 6379 TCP — Redis. 8080 TCP — HTTP alternate. 8443 TCP — HTTPS alternate. 27017 TCP — MongoDB.
