# Linux Networking Commands — Complete Reference

## Interface Management

### ip command (iproute2 — modern replacement for ifconfig)
`ip addr show` or `ip a` — Show all interfaces and their IP addresses.
`ip addr show dev eth0` — Show IP for specific interface.
`ip addr add 192.168.1.10/24 dev eth0` — Assign IP to interface.
`ip addr del 192.168.1.10/24 dev eth0` — Remove IP from interface.
`ip link show` — Show link-layer information (MAC, MTU, state).
`ip link set eth0 up` — Bring interface up.
`ip link set eth0 down` — Bring interface down.
`ip link set eth0 mtu 9000` — Set MTU (e.g., for jumbo frames).
`ip link set eth0 promisc on` — Enable promiscuous mode.
`ip -s link show eth0` — Show interface statistics (RX/TX packets, errors, drops).

### ifconfig (legacy, still common)
`ifconfig` — Show all active interfaces.
`ifconfig -a` — Show all interfaces including inactive.
`ifconfig eth0 192.168.1.10 netmask 255.255.255.0 up` — Configure interface.
`ifconfig eth0 down` — Disable interface.

### Network Manager (nmcli)
`nmcli device status` — Show all network devices and their state.
`nmcli connection show` — Show all connection profiles.
`nmcli connection show "Wired connection 1"` — Show details of a connection.
`nmcli connection modify "Wired connection 1" ipv4.addresses 192.168.1.10/24` — Set static IP.
`nmcli connection modify "Wired connection 1" ipv4.method manual` — Switch from DHCP to static.
`nmcli connection modify "Wired connection 1" ipv4.gateway 192.168.1.1` — Set gateway.
`nmcli connection modify "Wired connection 1" ipv4.dns "8.8.8.8 8.8.4.4"` — Set DNS.
`nmcli connection up "Wired connection 1"` — Activate connection.
`nmcli connection down "Wired connection 1"` — Deactivate connection.
`nmcli device wifi list` — Scan and list available Wi-Fi networks.
`nmcli device wifi connect SSID password PASSWORD` — Connect to Wi-Fi.

## Routing

### View and Manage Routes
`ip route show` or `ip r` — Show the routing table.
`ip route get 8.8.8.8` — Show which route would be used to reach 8.8.8.8.
`ip route add 10.0.0.0/8 via 192.168.1.1` — Add a static route.
`ip route add 10.0.0.0/8 via 192.168.1.1 dev eth0` — Add static route specifying interface.
`ip route add default via 192.168.1.1` — Set default gateway.
`ip route del 10.0.0.0/8` — Delete a route.
`ip route replace 10.0.0.0/8 via 192.168.1.254` — Replace existing route.
`ip route flush table main` — Flush all routes (careful!).

### Legacy route command
`route -n` — Display routing table (numeric, no DNS resolution).
`route add -net 10.0.0.0/8 gw 192.168.1.1` — Add route.
`route add default gw 192.168.1.1` — Set default gateway.
`route del -net 10.0.0.0/8` — Delete route.

### Policy Routing
`ip rule show` — Show policy routing rules.
`ip rule add from 192.168.1.0/24 table 100` — Route traffic from this subnet using table 100.
`ip route add default via 10.0.0.1 table 100` — Set default route in table 100.

## DNS Tools

### dig (DNS Information Groper)
`dig example.com` — Full DNS query with details.
`dig +short example.com` — Just the IP address(es).
`dig @8.8.8.8 example.com` — Query a specific DNS server.
`dig example.com MX` — Query MX (mail) records.
`dig example.com NS` — Query nameserver records.
`dig example.com AAAA` — Query IPv6 address records.
`dig example.com TXT` — Query TXT records (SPF, DKIM, etc.).
`dig +trace example.com` — Show the full resolution path from root.
`dig -x 8.8.8.8` — Reverse DNS lookup.
`dig example.com +noall +answer` — Clean output, just the answer section.
`dig example.com SOA` — Show Start of Authority record.
`dig axfr example.com @ns1.example.com` — Attempt DNS zone transfer.

### nslookup
`nslookup example.com` — Basic forward lookup.
`nslookup example.com 8.8.8.8` — Query specific DNS server.
`nslookup -type=MX example.com` — Query MX records.

### host
`host example.com` — Simple DNS lookup.
`host -t MX example.com` — Query MX records.
`host 8.8.8.8` — Reverse lookup.

### resolvectl (systemd-resolved)
`resolvectl status` — Show DNS configuration per interface.
`resolvectl query example.com` — Resolve a name.
`resolvectl statistics` — Show cache statistics.
`resolvectl flush-caches` — Flush DNS cache.

### DNS Configuration Files
`/etc/resolv.conf` — Primary DNS resolver configuration. Contains nameserver entries and search domains.
`/etc/hosts` — Local host-to-IP mappings, checked before DNS.
`/etc/nsswitch.conf` — Controls name resolution order (files, dns, mdns, etc.).
`/etc/systemd/resolved.conf` — Configuration for systemd-resolved.

## Connection Testing

### ping
`ping 8.8.8.8` — Test connectivity (ICMP echo).
`ping -c 5 8.8.8.8` — Send exactly 5 pings.
`ping -i 0.2 8.8.8.8` — Ping every 0.2 seconds (needs root for < 0.2).
`ping -s 1472 -M do 8.8.8.8` — Test MTU (1472 + 28 byte header = 1500).
`ping -I eth0 8.8.8.8` — Ping from a specific interface.
`ping -W 2 8.8.8.8` — Set 2-second timeout for each reply.
`ping6 ::1` — Ping IPv6 address.

### traceroute / tracepath
`traceroute 8.8.8.8` — Show the path packets take (uses UDP by default on Linux).
`traceroute -I 8.8.8.8` — Use ICMP instead of UDP.
`traceroute -T -p 443 8.8.8.8` — Use TCP SYN on port 443 (bypasses firewalls that block UDP/ICMP).
`traceroute -n 8.8.8.8` — Don't resolve hostnames (faster).
`tracepath 8.8.8.8` — Similar to traceroute, also discovers MTU along the path. Does not require root.
`mtr 8.8.8.8` — Combines ping and traceroute in real-time. Shows packet loss and latency at each hop.
`mtr -r -c 100 8.8.8.8` — Generate a report after 100 cycles.

## Socket and Connection Inspection

### ss (socket statistics — modern replacement for netstat)
`ss -tlnp` — Show TCP listening sockets with process names and numeric ports.
`ss -ulnp` — Show UDP listening sockets.
`ss -tunap` — Show all TCP/UDP connections with process info.
`ss -s` — Show socket summary statistics.
`ss state established` — Show only established connections.
`ss dst 10.0.0.1` — Filter by destination address.
`ss sport = :443` — Filter by source port 443.
`ss -o state time-wait` — Show TIME_WAIT sockets with timer info.

### netstat (legacy, still widely used)
`netstat -tlnp` — TCP listening ports with programs.
`netstat -ulnp` — UDP listening ports with programs.
`netstat -tunap` — All connections.
`netstat -r` — Routing table (same as route -n).
`netstat -s` — Protocol statistics.
`netstat -i` — Interface statistics.

### lsof (list open files, including network)
`lsof -i :80` — What process is using port 80?
`lsof -i tcp` — Show all TCP connections.
`lsof -i -P -n` — Show all network connections (numeric, no resolution).
`lsof -i @192.168.1.1` — Connections to/from specific host.

## Packet Capture and Analysis

### tcpdump
`tcpdump -i eth0` — Capture all traffic on eth0.
`tcpdump -i any` — Capture on all interfaces.
`tcpdump -i eth0 -w capture.pcap` — Save capture to file (open in Wireshark).
`tcpdump -r capture.pcap` — Read a saved capture file.
`tcpdump -i eth0 port 80` — Capture only port 80 traffic.
`tcpdump -i eth0 host 192.168.1.1` — Capture traffic to/from specific host.
`tcpdump -i eth0 src 192.168.1.1` — Capture traffic from specific source.
`tcpdump -i eth0 dst port 443` — Capture traffic going to port 443.
`tcpdump -i eth0 tcp` — Capture only TCP traffic.
`tcpdump -i eth0 icmp` — Capture only ICMP (ping) traffic.
`tcpdump -i eth0 'tcp[tcpflags] & (tcp-syn) != 0'` — Capture only SYN packets.
`tcpdump -i eth0 -n -v` — Verbose output, no DNS resolution.
`tcpdump -i eth0 -c 100` — Capture exactly 100 packets then stop.
`tcpdump -i eth0 net 192.168.1.0/24` — Capture traffic for entire subnet.
`tcpdump -i eth0 'port 80 or port 443'` — Capture HTTP and HTTPS.
`tcpdump -i eth0 -A` — Print packet payload in ASCII.
`tcpdump -i eth0 -X` — Print packet payload in hex and ASCII.

### nmap (network scanner)
`nmap 192.168.1.1` — Scan common ports on a host.
`nmap -sn 192.168.1.0/24` — Ping sweep (host discovery, no port scan).
`nmap -p 1-65535 192.168.1.1` — Scan all ports.
`nmap -p 22,80,443 192.168.1.1` — Scan specific ports.
`nmap -sV 192.168.1.1` — Detect service versions.
`nmap -O 192.168.1.1` — Detect operating system.
`nmap -sU 192.168.1.1` — UDP port scan.
`nmap -sS 192.168.1.1` — TCP SYN scan (stealthy, default with root).
`nmap -A 192.168.1.1` — Aggressive scan (OS detection, version, scripts, traceroute).
`nmap --script vuln 192.168.1.1` — Run vulnerability detection scripts.

## Bandwidth and Performance Testing

### iperf3
`iperf3 -s` — Start iperf server.
`iperf3 -c server_ip` — Run TCP bandwidth test to server.
`iperf3 -c server_ip -u -b 100M` — UDP test at 100 Mbps.
`iperf3 -c server_ip -R` — Reverse test (server sends to client).
`iperf3 -c server_ip -P 4` — Parallel streams (4 threads).
`iperf3 -c server_ip -t 30` — Run test for 30 seconds.

### Other Performance Tools
`ethtool eth0` — Show NIC settings (speed, duplex, driver).
`ethtool -S eth0` — Show NIC statistics (errors, drops).
`ethtool -i eth0` — Show driver information.
`nethogs` — Show bandwidth usage per process (like top for network).
`iftop -i eth0` — Show real-time bandwidth usage per connection.
`bmon` — Bandwidth monitor with graph output.
`nload eth0` — Real-time incoming/outgoing bandwidth graph.
`vnstat` — Network traffic accounting (tracks daily/monthly usage).

## Firewall (iptables / nftables)

### iptables (traditional)
`iptables -L -n -v` — List all rules with packet counts.
`iptables -L -n -v --line-numbers` — With rule numbers for deletion.
`iptables -A INPUT -p tcp --dport 22 -j ACCEPT` — Allow SSH inbound.
`iptables -A INPUT -p tcp --dport 80 -j ACCEPT` — Allow HTTP inbound.
`iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT` — Allow return traffic.
`iptables -A INPUT -j DROP` — Drop everything else (append to end).
`iptables -D INPUT 3` — Delete rule number 3 from INPUT chain.
`iptables -F` — Flush all rules (careful in production!).
`iptables -t nat -L -n` — Show NAT table rules.
`iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE` — Enable NAT/masquerading.
`iptables-save > /etc/iptables/rules.v4` — Save rules persistently.
`iptables-restore < /etc/iptables/rules.v4` — Restore saved rules.

### nftables (modern replacement)
`nft list ruleset` — Show all rules.
`nft add table inet filter` — Create a table.
`nft add chain inet filter input { type filter hook input priority 0 \; }` — Create input chain.
`nft add rule inet filter input tcp dport 22 accept` — Allow SSH.
`nft add rule inet filter input ct state established,related accept` — Allow return traffic.
`nft flush ruleset` — Clear all rules.

### firewalld (RHEL/CentOS/Fedora)
`firewall-cmd --state` — Check if running.
`firewall-cmd --list-all` — Show current zone configuration.
`firewall-cmd --add-port=8080/tcp --permanent` — Open port 8080.
`firewall-cmd --add-service=http --permanent` — Allow HTTP service.
`firewall-cmd --reload` — Apply changes.
`firewall-cmd --list-ports` — Show opened ports.

### ufw (Ubuntu)
`ufw status verbose` — Show firewall status and rules.
`ufw enable` — Enable firewall.
`ufw allow 22/tcp` — Allow SSH.
`ufw allow from 192.168.1.0/24` — Allow traffic from subnet.
`ufw deny 23/tcp` — Block telnet.
`ufw delete allow 22/tcp` — Remove a rule.

## Network Configuration Files (Linux)

### Debian/Ubuntu
`/etc/network/interfaces` — Legacy interface configuration.
`/etc/netplan/*.yaml` — Modern netplan configuration (Ubuntu 18.04+).
`/etc/hostname` — System hostname.

### RHEL/CentOS
`/etc/sysconfig/network-scripts/ifcfg-eth0` — Interface configuration.
`/etc/sysconfig/network` — Hostname and default gateway.

### Universal
`/etc/hosts` — Static hostname-to-IP mappings.
`/etc/resolv.conf` — DNS resolver configuration.
`/etc/nsswitch.conf` — Name resolution order.
`/etc/services` — Port-to-service name mappings.
`/etc/protocols` — Protocol number mappings.
`/proc/sys/net/ipv4/ip_forward` — IP forwarding toggle (1=enabled, 0=disabled).

### Enable IP Forwarding
Temporary: `echo 1 > /proc/sys/net/ipv4/ip_forward`
Permanent: Add `net.ipv4.ip_forward = 1` to `/etc/sysctl.conf`, then run `sysctl -p`.
