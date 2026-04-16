# DNS Troubleshooting Guide

## Overview
DNS (Domain Name System) translates human-readable domain names into IP addresses. When DNS fails, everything breaks — users can't reach websites, services can't find each other, and you'll hear "the internet is down" even though the network is fine.

## Common DNS Issues

### 1. Complete DNS Resolution Failure
**Symptoms:** `nslookup` or `dig` return "connection timed out; no servers could be reached"

**Troubleshooting Steps:**
1. Check if DNS server is reachable: `ping 8.8.8.8` (if this works, you have IP connectivity)
2. Check your configured DNS server: `cat /etc/resolv.conf`
3. Test with a known-good DNS server: `dig @8.8.8.8 example.com`
4. Check if the DNS service is running on your server: `systemctl status named` or `systemctl status systemd-resolved`

**Common Causes:**
- DNS server is down or unreachable
- Firewall blocking UDP/TCP port 53
- Incorrect DNS server configured in `/etc/resolv.conf` or DHCP
- NetworkManager overwriting `/etc/resolv.conf`

### 2. Slow DNS Resolution
**Symptoms:** Websites load slowly, `time dig example.com` shows >500ms

**Troubleshooting Steps:**
1. Compare resolution times: `time dig @8.8.8.8 example.com` vs `time dig @your-dns-server example.com`
2. Check for DNS forwarding chains: `dig +trace example.com`
3. Look for timeout entries in `/etc/resolv.conf` (options timeout:1 attempts:1)
4. Check if IPv6 DNS is failing and falling back to IPv4

**Common Causes:**
- DNS server is overloaded
- Long forwarding chains
- IPv6 DNS timeout before IPv4 fallback
- Network latency to DNS server

### 3. Intermittent DNS Failures
**Symptoms:** DNS works sometimes, fails other times. Usually the hardest to debug.

**Troubleshooting Steps:**
1. Run continuous DNS tests: `while true; do dig +short example.com; sleep 1; done`
2. Check DNS server logs for errors
3. Monitor with `tcpdump -i any port 53` to see actual DNS traffic
4. Check if you have multiple DNS servers with different states

### 4. NXDOMAIN for Internal Domains
**Symptoms:** External DNS works fine but internal domains return NXDOMAIN.

**Troubleshooting Steps:**
1. Check search domains: `cat /etc/resolv.conf` — look for `search` directive
2. Verify internal DNS zone: `dig @internal-dns-server internal.example.com`
3. Check split-horizon DNS configuration
4. Verify DNS zone transfers are working: `dig AXFR example.com @dns-server`

## Key DNS Commands
- `dig example.com` — Full DNS query with details
- `dig +short example.com` — Just the IP
- `dig @8.8.8.8 example.com` — Query specific server
- `dig +trace example.com` — Show full resolution path
- `nslookup example.com` — Simpler DNS lookup tool
- `host example.com` — Even simpler lookup
- `resolvectl status` — Show systemd-resolved config (modern Linux)
- `nmcli dev show | grep DNS` — Show NetworkManager DNS config

## DNS Configuration Files
- `/etc/resolv.conf` — System DNS resolver config
- `/etc/hosts` — Local hostname-to-IP mappings (checked before DNS)
- `/etc/nsswitch.conf` — Controls name resolution order
- `/etc/systemd/resolved.conf` — systemd-resolved configuration

## When to Escalate
- DNSSEC validation failures (check with `dig +dnssec`)
- DNS amplification attacks (unusual traffic volume on port 53)
- Zone transfer failures between primary and secondary DNS
- Split-horizon DNS inconsistencies across network segments
