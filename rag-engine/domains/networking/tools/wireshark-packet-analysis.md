# Wireshark and Packet Analysis

## Wireshark Basics

Wireshark is the most widely used network packet analyzer. It captures packets in real-time and displays them with detailed protocol decode. Wireshark uses the same capture engine (libpcap/npcap) as tcpdump.

### Capture Filters vs Display Filters
Capture filters: Applied BEFORE packets are captured (BPF syntax, same as tcpdump). Reduces the amount of data captured. Cannot be changed after capture starts. Use when you know exactly what you're looking for.
Display filters: Applied AFTER capture to filter what's shown. Much more powerful and flexible syntax. Can be changed at any time. Use for analysis and narrowing down results.

### Common Capture Filters (BPF Syntax)
`host 192.168.1.1` — Traffic to/from specific host.
`net 192.168.1.0/24` — Traffic to/from a subnet.
`port 80` — Traffic on port 80 (both TCP and UDP).
`tcp port 443` — Only TCP traffic on port 443.
`src host 10.0.0.1` — Only traffic from source 10.0.0.1.
`dst port 53` — Only traffic going to port 53.
`not port 22` — Exclude SSH traffic.
`host 10.0.0.1 and port 80` — Combine filters with and/or/not.
`icmp` — Only ICMP traffic.
`tcp[tcpflags] & (tcp-syn) != 0` — Only TCP SYN packets.

### Common Display Filters (Wireshark Syntax)
`ip.addr == 192.168.1.1` — Traffic to/from specific IP.
`ip.src == 192.168.1.1` — Traffic from specific source.
`ip.dst == 192.168.1.1` — Traffic to specific destination.
`tcp.port == 80` — TCP traffic on port 80.
`tcp.dstport == 443` — TCP traffic to port 443.
`udp.port == 53` — UDP traffic on port 53.
`http` — All HTTP traffic.
`dns` — All DNS traffic.
`tls` — All TLS traffic.
`tcp.flags.syn == 1 && tcp.flags.ack == 0` — TCP SYN packets only (new connections).
`tcp.flags.reset == 1` — TCP RST packets (connection resets).
`tcp.analysis.retransmission` — Retransmitted packets.
`tcp.analysis.zero_window` — Zero window conditions.
`tcp.analysis.duplicate_ack` — Duplicate ACKs.
`frame.time_delta > 1` — Packets with more than 1 second between them.
`http.response.code >= 400` — HTTP error responses.
`dns.flags.rcode != 0` — DNS error responses.
`!(arp or icmp or dns)` — Exclude common noise protocols.
`tcp.stream eq 5` — Follow specific TCP stream number 5.
`ip.addr == 192.168.1.0/24` — Traffic for entire subnet.
`eth.addr == 00:11:22:33:44:55` — Traffic for specific MAC.

### Display Filter Operators
`==` equal, `!=` not equal, `>` greater than, `<` less than, `>=` greater or equal, `<=` less or equal. `contains` — field contains string. `matches` — regex match. `&&` or `and` — logical AND. `||` or `or` — logical OR. `!` or `not` — logical NOT.

## TCP Analysis with Wireshark

### Analyzing the TCP Handshake
Filter: `tcp.flags.syn == 1`. Look for SYN → SYN-ACK → ACK sequence. If SYN is sent but no SYN-ACK returns: firewall blocking, service not running, or host unreachable. If SYN-ACK is sent but no final ACK: client-side firewall or network issue. If RST is returned instead of SYN-ACK: port is closed on the server.

### Identifying TCP Problems
Retransmissions (`tcp.analysis.retransmission`): Packets that were sent again because the original wasn't acknowledged. Indicates packet loss. If consistent, check for congestion, bad links, or buffer overflow.
Duplicate ACKs (`tcp.analysis.duplicate_ack`): Receiver got an out-of-order packet and is re-requesting the missing one. Three duplicate ACKs trigger Fast Retransmit. Occasional is normal; sustained indicates loss.
Zero Window (`tcp.analysis.zero_window`): Receiver's buffer is full, telling sender to stop. The sender pauses until a Window Update is received. Indicates the application is not reading data fast enough (slow application, not network issue).
Window Full (`tcp.analysis.window_full`): Sender has filled the receiver's advertised window. Similar to zero window but from the sender's perspective.
RST packets (`tcp.flags.reset == 1`): Abrupt connection termination. Could indicate: application crash, firewall killing the connection, port not open, or half-open connection cleanup.

### TCP Stream Reassembly
Right-click a packet → Follow → TCP Stream. Wireshark reassembles the entire conversation and shows the data exchanged. Color-coded: red = client to server, blue = server to client. Useful for seeing HTTP requests/responses, extracting files, or viewing application-layer data.

## DNS Analysis

### Filtering DNS
`dns` — All DNS traffic.
`dns.qry.name == "example.com"` — Queries for specific domain.
`dns.qry.type == 1` — A record queries.
`dns.qry.type == 28` — AAAA record queries.
`dns.flags.rcode == 3` — NXDOMAIN responses (name not found).
`dns.flags.rcode == 2` — SERVFAIL responses (server failure).
`dns.time > 0.5` — DNS responses taking more than 500ms.

### DNS Troubleshooting with Wireshark
Slow resolution: Filter DNS and check response times. Look for timeouts and retries. Check if IPv6 (AAAA) queries are timing out before IPv4 (A) queries succeed.
NXDOMAIN: The queried name doesn't exist. Check for typos, missing search domain, or wrong DNS zone configuration.
SERVFAIL: The DNS server encountered an error resolving the name. Often indicates DNSSEC validation failure or unreachable authoritative server.

## HTTP/HTTPS Analysis

### HTTP Filters
`http` — All HTTP traffic.
`http.request` — Only HTTP requests.
`http.response` — Only HTTP responses.
`http.request.method == "POST"` — Only POST requests.
`http.response.code == 200` — Successful responses.
`http.response.code >= 400` — Error responses.
`http.response.code == 404` — Not found.
`http.response.code == 500` — Internal server error.
`http.host == "example.com"` — Requests to specific host.
`http.request.uri contains "api"` — Requests with "api" in the URI.

### TLS/HTTPS Analysis
Since HTTPS is encrypted, you can't see the application data without the decryption key. What you CAN see: TLS Client Hello (includes SNI — Server Name Indication, showing which hostname the client requested), TLS version negotiation, cipher suite selection, certificate exchange. Filter: `tls.handshake.type == 1` for Client Hello, `tls.handshake.type == 2` for Server Hello.
Decryption: If you have the server's private key or the session's pre-master secret (via SSLKEYLOGFILE environment variable), Wireshark can decrypt TLS traffic. Set in Edit → Preferences → Protocols → TLS → (Pre)-Master-Secret log filename.

## ICMP Analysis

`icmp` — All ICMP traffic.
`icmp.type == 8` — Echo requests (pings sent).
`icmp.type == 0` — Echo replies (ping responses).
`icmp.type == 3` — Destination unreachable.
`icmp.type == 11` — Time exceeded (traceroute).
`icmp.type == 3 && icmp.code == 3` — Port unreachable.
`icmp.type == 3 && icmp.code == 4` — Fragmentation needed (MTU issues).

## ARP Analysis

`arp` — All ARP traffic.
`arp.opcode == 1` — ARP requests.
`arp.opcode == 2` — ARP replies.
`arp.duplicate-address-detected` — Wireshark's detection of IP conflicts.
Look for: Gratuitous ARP (same source and target IP — used for IP conflict detection and failover). ARP storms (excessive ARP traffic — possible ARP spoofing attack). Unanswered ARP requests (target host is down or unreachable on the LAN).

## Wireshark Statistics and Tools

### Conversations (Statistics → Conversations)
Shows all communication pairs with packet counts, bytes transferred, and duration. Useful for identifying top talkers and unusual communication patterns.

### Protocol Hierarchy (Statistics → Protocol Hierarchy)
Shows a breakdown of all protocols in the capture with percentages. Quick way to understand the traffic mix and spot unusual protocols.

### IO Graphs (Statistics → IO Graphs)
Plot traffic volume over time. Add multiple filters to compare different traffic types. Useful for identifying traffic spikes, patterns, and anomalies.

### Expert Information (Analyze → Expert Information)
Wireshark's built-in analysis of potential problems. Categorized by severity: Error, Warning, Note, Chat. Highlights retransmissions, RSTs, zero windows, checksum errors, and more.

### Flow Graph (Statistics → Flow Graph)
Visual representation of packet exchanges between hosts over time. Great for visualizing TCP handshakes, DNS queries, and protocol interactions.

## Practical Capture Tips
Capture on the right interface — make sure you're capturing where the traffic flows. Use capture filters for high-volume networks to avoid huge files. Save captures as .pcapng (supports more metadata than .pcap). Ring buffer: Capture → Options → Ring buffer — automatically rotate files to limit disk usage. Name captures descriptively (e.g., "dns_issue_2024-01-15.pcapng"). Capture with tcpdump on remote servers, transfer the .pcap, and analyze in Wireshark on your workstation. On switches, use SPAN/mirror ports to capture traffic not destined for your host.
