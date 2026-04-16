# Network Services — DHCP, DNS, NTP, NAT

## DHCP (Dynamic Host Configuration Protocol)

DHCP automatically assigns IP addresses and network configuration to devices on a network. It uses UDP ports 67 (server) and 68 (client).

### DHCP DORA Process
1. Discover: Client broadcasts a DHCPDISCOVER message (source 0.0.0.0, destination 255.255.255.255) looking for a DHCP server.
2. Offer: Server responds with a DHCPOFFER containing an available IP address, subnet mask, gateway, DNS servers, and lease duration.
3. Request: Client broadcasts a DHCPREQUEST accepting the offered address (broadcast so other servers know to release their offers).
4. Acknowledge: Server responds with a DHCPACK confirming the lease. The client can now use the IP address.

### DHCP Lease Lifecycle
At 50% of lease time (T1): Client sends unicast DHCPREQUEST to renew with the same server. At 87.5% of lease time (T2): If renewal failed, client broadcasts DHCPREQUEST to any server. At lease expiration: Client must stop using the IP and start DORA again. DHCPRELEASE: Client voluntarily releases its IP before lease expires. DHCPDECLINE: Client rejects an offered IP (e.g., detected duplicate via ARP).

### DHCP Relay (ip helper-address)
DHCP uses broadcast, which doesn't cross router boundaries. When the DHCP server is on a different subnet, a DHCP relay agent forwards broadcasts as unicast to the server.
Cisco: `interface g0/1` then `ip helper-address 10.0.0.5` — Forward DHCP broadcasts from this interface to server 10.0.0.5.
Linux: Install and configure `dhcp-relay` or use `dhcrelay`.

### DHCP Server Configuration (Linux — ISC DHCP)
Configuration file: `/etc/dhcp/dhcpd.conf`
```
subnet 192.168.1.0 netmask 255.255.255.0 {
    range 192.168.1.100 192.168.1.200;
    option routers 192.168.1.1;
    option domain-name-servers 8.8.8.8, 8.8.4.4;
    option domain-name "example.local";
    default-lease-time 600;
    max-lease-time 7200;
}
host printer {
    hardware ethernet 00:11:22:33:44:55;
    fixed-address 192.168.1.50;
}
```
Manage: `systemctl start isc-dhcp-server`. View leases: `cat /var/lib/dhcp/dhcpd.leases`.

### DHCP Server Configuration (Cisco)
`ip dhcp pool LAN` — Create a DHCP pool.
`network 192.168.1.0 255.255.255.0` — Define the subnet.
`default-router 192.168.1.1` — Set default gateway.
`dns-server 8.8.8.8` — Set DNS server.
`lease 0 8` — Set lease to 0 days, 8 hours.
`ip dhcp excluded-address 192.168.1.1 192.168.1.99` — Reserve addresses.

### DHCP Troubleshooting
Client not getting an IP: Is the DHCP server running? Is there a DHCP relay if the server is remote? Is the client's port in the correct VLAN? Check `tcpdump -i eth0 port 67 or port 68` to see if DHCP messages are flowing. Check DHCP server logs for errors.
Client getting wrong IP/settings: Check DHCP pool configuration. Check for rogue DHCP servers on the network (`nmap --script broadcast-dhcp-discover`). Verify DHCP reservations.
IP conflicts: Enable DHCP conflict detection (Cisco: `ip dhcp ping packets 2`). Check for static IPs conflicting with the DHCP pool. Review DHCP leases for duplicates.

## DNS (Domain Name System)

DNS translates domain names to IP addresses and vice versa. It uses a hierarchical, distributed database system. DNS primarily uses UDP port 53 for queries and TCP port 53 for zone transfers and large responses.

### DNS Record Types
A Record: Maps hostname to IPv4 address (example.com → 93.184.216.34).
AAAA Record: Maps hostname to IPv6 address.
CNAME Record: Alias pointing to another hostname (www.example.com → example.com).
MX Record: Mail server for a domain, includes priority (lower = preferred).
NS Record: Authoritative nameserver for a domain.
PTR Record: Reverse DNS — maps IP to hostname (used in reverse zones).
SOA Record: Start of Authority — contains zone metadata (serial, refresh, retry, expire, TTL).
TXT Record: Arbitrary text, commonly used for SPF, DKIM, and domain verification.
SRV Record: Service location (used by Active Directory, SIP, etc.).
CAA Record: Certificate Authority Authorization — which CAs can issue certs for this domain.

### DNS Resolution Process
1. Client checks its local DNS cache.
2. Client queries its configured recursive resolver (e.g., 8.8.8.8, your ISP's DNS).
3. Recursive resolver checks its cache. If not cached, it queries the root nameservers.
4. Root nameserver responds with the TLD (Top-Level Domain) nameserver for .com, .org, etc.
5. TLD nameserver responds with the authoritative nameserver for the specific domain.
6. Authoritative nameserver responds with the actual DNS record.
7. Recursive resolver caches the result and returns it to the client.

### DNS Server Types
Recursive Resolver: Handles the full resolution process on behalf of clients. Caches results. Examples: 8.8.8.8 (Google), 1.1.1.1 (Cloudflare), your ISP's DNS.
Authoritative Server: Holds the actual DNS records for a domain. Responds to queries for its zones.
Forwarder: Passes queries to another DNS server instead of resolving recursively itself.

### DNS Configuration (BIND on Linux)
Main config: `/etc/named.conf` or `/etc/bind/named.conf`.
Zone files: Contain the actual DNS records for a domain.
Forward zone example in zone file:
```
$TTL 86400
@   IN  SOA  ns1.example.com. admin.example.com. (
            2024010101  ; Serial
            3600        ; Refresh
            900         ; Retry
            604800      ; Expire
            86400 )     ; Minimum TTL
@   IN  NS   ns1.example.com.
@   IN  NS   ns2.example.com.
@   IN  A    93.184.216.34
www IN  CNAME @
mail IN A    93.184.216.35
@   IN  MX   10 mail.example.com.
```

### DNS Troubleshooting
Resolution failure: Check `/etc/resolv.conf` for correct nameserver entries. Test with `dig @8.8.8.8 example.com` to bypass local DNS. Check if DNS port 53 is blocked by firewall. Verify the DNS service is running on the server.
Slow resolution: Compare `time dig @local-server` vs `time dig @8.8.8.8`. Check for long forwarding chains. IPv6 DNS timeout falling back to IPv4 (common issue).
Stale records: Check TTL values — low TTL = frequent lookups, high TTL = stale cache. Flush local cache: Linux (`resolvectl flush-caches`), macOS (`sudo dscacheutil -flushcache`), Windows (`ipconfig /flushdns`).
NXDOMAIN for internal names: Check search domain in `/etc/resolv.conf`. Verify internal DNS zones are configured correctly. Check split-horizon DNS configuration.

## NAT (Network Address Translation)

NAT translates private IP addresses to public IP addresses, allowing multiple devices to share a single public IP.

### NAT Types
Static NAT (SNAT): One-to-one mapping between a private IP and a public IP. Used for servers that need to be reachable from the internet.
Dynamic NAT: Maps private IPs to a pool of public IPs. First come, first served. When the pool is exhausted, new connections are dropped.
PAT (Port Address Translation) / NAT Overload: Many-to-one mapping. Multiple private IPs share a single public IP, differentiated by port numbers. This is what your home router does.

### NAT Configuration (Cisco)
```
! Define inside and outside interfaces
interface g0/0
 ip nat inside
interface g0/1
 ip nat outside

! Static NAT
ip nat inside source static 192.168.1.10 203.0.113.10

! Dynamic NAT with pool
ip nat pool PUBLIC 203.0.113.1 203.0.113.10 netmask 255.255.255.0
access-list 1 permit 192.168.1.0 0.0.0.255
ip nat inside source list 1 pool PUBLIC

! PAT (overload)
ip nat inside source list 1 interface g0/1 overload
```

### NAT Configuration (Linux iptables)
`iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE` — PAT using the outgoing interface's IP.
`iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 192.168.1.10:80` — Port forwarding.
`iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o eth0 -j SNAT --to-source 203.0.113.1` — Static SNAT.

### NAT Troubleshooting
Cisco: `show ip nat translations` — View active translations. `show ip nat statistics` — View NAT hit counts and pool usage. `debug ip nat` — Real-time NAT debug (use cautiously). `clear ip nat translation *` — Clear all NAT translations.
Common issues: Inside/outside interfaces incorrectly assigned. ACL not matching traffic that should be translated. NAT pool exhausted (all public IPs in use). Return traffic not matching existing translation (asymmetric routing).

## NTP (Network Time Protocol)

NTP synchronizes clocks across network devices. Accurate time is critical for logging, authentication (Kerberos), certificate validation, and forensics. Uses UDP port 123.

### NTP Stratum Levels
Stratum 0: Atomic clocks, GPS receivers (reference clocks). Stratum 1: Servers directly connected to Stratum 0 sources. Stratum 2: Synchronized to Stratum 1 servers. And so on down to Stratum 15. Stratum 16 means unsynchronized.

### NTP Configuration
Linux: Edit `/etc/ntp.conf` or `/etc/chrony/chrony.conf`.
`chronyc tracking` — Show current time sync status.
`chronyc sources -v` — Show configured NTP sources and their status.
`timedatectl status` — Show system time and NTP sync status (systemd).
`timedatectl set-ntp true` — Enable NTP synchronization.

Cisco: `ntp server 10.0.0.1` — Configure NTP server. `show ntp status` — Check sync status. `show ntp associations` — View NTP peers.
