# VPN and Tunneling Technologies

## VPN Fundamentals

A VPN (Virtual Private Network) creates a secure, encrypted tunnel over an untrusted network (typically the internet). VPNs provide confidentiality (encryption), integrity (hash verification), and authentication (identity verification).

### VPN Types
Site-to-Site VPN: Connects two networks (e.g., office to office). Traffic between the networks flows through the encrypted tunnel. End devices are unaware of the VPN. Typically uses IPsec.
Remote Access VPN: Connects individual clients to a network. Users install VPN client software. Commonly uses SSL/TLS (OpenVPN, AnyConnect) or IPsec (IKEv2).
Client-to-Client VPN: Peer-to-peer connections (e.g., WireGuard mesh). Each node connects directly to other nodes.

## IPsec (Internet Protocol Security)

IPsec is a suite of protocols that provides security at the network layer (Layer 3). It can protect any IP traffic, not just specific applications.

### IPsec Components
AH (Authentication Header): Provides authentication and integrity but NOT encryption. Protocol number 51. Rarely used alone because it doesn't encrypt.
ESP (Encapsulating Security Payload): Provides encryption, authentication, and integrity. Protocol number 50. This is what most IPsec deployments use.
IKE (Internet Key Exchange): Negotiates the security parameters and establishes the tunnel. IKEv1 uses UDP port 500 (and 4500 for NAT traversal). IKEv2 is the modern version — simpler, faster, more reliable.

### IPsec Modes
Transport Mode: Only encrypts the payload (data) of the IP packet. Original IP header remains intact. Used for host-to-host communication. Lower overhead.
Tunnel Mode: Encrypts the entire original IP packet and encapsulates it in a new IP packet. Used for site-to-site VPNs (hides the original source and destination). Higher overhead but more secure.

### IKE Phase 1 (IKE SA / ISAKMP SA)
Purpose: Establish a secure channel between the two VPN peers for negotiating Phase 2 parameters. Negotiates: encryption algorithm (AES), hash algorithm (SHA), authentication method (pre-shared key or certificates), Diffie-Hellman group (for key exchange), SA lifetime.
Main Mode: 6 messages exchanged, provides identity protection (more secure).
Aggressive Mode: 3 messages, faster but exposes identities (less secure).

### IKE Phase 2 (IPsec SA)
Purpose: Negotiate the actual IPsec tunnel parameters for encrypting data traffic. Negotiates: encryption and hash for data (can differ from Phase 1), transform set (ESP-AES, ESP-SHA), proxy identities / interesting traffic (what traffic to encrypt), SA lifetime, PFS (Perfect Forward Secrecy) Diffie-Hellman group.
Quick Mode: Uses the secure channel from Phase 1 to negotiate Phase 2 parameters.

### IPsec Troubleshooting
Phase 1 not establishing: Mismatched encryption/hash/DH group parameters. Pre-shared key mismatch. Wrong peer IP address. Firewall blocking UDP 500 or protocol 50/51. NAT between peers without NAT-T (NAT traversal, UDP 4500).
Phase 2 not establishing: Mismatched transform sets. Proxy identity / interesting traffic ACL mismatch (the traffic selectors don't match on both sides). PFS DH group mismatch.
Tunnel up but no traffic flowing: Interesting traffic ACL not matching actual traffic. Routing issue — traffic not being directed through the tunnel. MTU issues — IPsec adds overhead (typically 50-70 bytes), causing fragmentation.

### IPsec Configuration (Cisco — Site-to-Site)
```
! Phase 1
crypto isakmp policy 10
 encryption aes 256
 hash sha256
 authentication pre-share
 group 14
 lifetime 86400
crypto isakmp key SECRETKEY address 203.0.113.2

! Phase 2
crypto ipsec transform-set MYSET esp-aes 256 esp-sha256-hmac
 mode tunnel

! Interesting traffic
access-list 100 permit ip 192.168.1.0 0.0.0.255 10.0.0.0 0.0.0.255

! Crypto map
crypto map MYMAP 10 ipsec-isakmp
 set peer 203.0.113.2
 set transform-set MYSET
 match address 100

! Apply to interface
interface g0/1
 crypto map MYMAP
```

### IPsec Troubleshooting Commands (Cisco)
`show crypto isakmp sa` — Phase 1 SA status (QM_IDLE = healthy).
`show crypto ipsec sa` — Phase 2 SA status, packet counts.
`show crypto isakmp policy` — Configured Phase 1 policies.
`show crypto map` — Crypto map configuration.
`debug crypto isakmp` — Real-time Phase 1 debug.
`debug crypto ipsec` — Real-time Phase 2 debug.
`clear crypto isakmp` — Clear Phase 1 SAs.
`clear crypto sa` — Clear Phase 2 SAs.

## WireGuard

WireGuard is a modern, lightweight VPN protocol that aims to be simpler and faster than IPsec and OpenVPN. It is built into the Linux kernel since version 5.6.

### WireGuard Characteristics
Uses UDP (single port, typically 51820). Minimal attack surface (~4000 lines of code vs ~100,000 for OpenVPN). Uses modern cryptography: ChaCha20 (encryption), Poly1305 (authentication), Curve25519 (key exchange), BLAKE2s (hashing). Roaming-friendly — works seamlessly when client IP changes. Stateless — no connection state to maintain.

### WireGuard Configuration (Linux)
Server configuration (`/etc/wireguard/wg0.conf`):
```
[Interface]
PrivateKey = SERVER_PRIVATE_KEY
Address = 10.0.0.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
PublicKey = CLIENT_PUBLIC_KEY
AllowedIPs = 10.0.0.2/32
```

Client configuration:
```
[Interface]
PrivateKey = CLIENT_PRIVATE_KEY
Address = 10.0.0.2/24
DNS = 8.8.8.8

[Peer]
PublicKey = SERVER_PUBLIC_KEY
Endpoint = vpn.example.com:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```

Commands: `wg-quick up wg0` — Start VPN. `wg-quick down wg0` — Stop VPN. `wg show` — Show tunnel status and peer info. `wg genkey | tee privatekey | wg pubkey > publickey` — Generate key pair.

## OpenVPN

OpenVPN is a mature, widely-deployed SSL/TLS-based VPN. It operates in userspace and can use either UDP (preferred, faster) or TCP (fallback, works through more firewalls) on any port.

### OpenVPN Modes
TUN mode: Layer 3 VPN — routes IP packets through the tunnel. More common, lower overhead.
TAP mode: Layer 2 VPN — bridges Ethernet frames through the tunnel. Used when you need broadcast/multicast or non-IP protocols.

### OpenVPN Troubleshooting
Connection fails: Check if the server is reachable on the configured port (`nc -zv server 1194`). Verify certificates are valid and not expired. Check if the TLS handshake completes (look for TLS errors in logs). Try switching from UDP to TCP if UDP is being blocked.
Connected but no traffic: Check routing — does the client have routes to the remote network? Check if IP forwarding is enabled on the server. Check server-side firewall and NAT rules.
Log files: Server: `/var/log/openvpn/openvpn.log` or `journalctl -u openvpn`. Client: varies by platform.

## GRE (Generic Routing Encapsulation)

GRE creates point-to-point tunnels that can encapsulate a wide variety of protocols. GRE itself provides no encryption — it is often combined with IPsec for secure tunnels.

### GRE Characteristics
Protocol number: 47. Adds 24 bytes of overhead (20-byte IP header + 4-byte GRE header). Supports multicast (unlike IPsec alone), which is why OSPF and other routing protocols can run over GRE tunnels. Often used as GRE-over-IPsec to get both multicast support and encryption.

### GRE Configuration (Cisco)
```
interface Tunnel0
 ip address 10.0.0.1 255.255.255.252
 tunnel source g0/1
 tunnel destination 203.0.113.2
 tunnel mode gre ip
```

### GRE Troubleshooting
`show interface Tunnel0` — Check tunnel status (line protocol up/down).
`show ip route` — Verify routes through the tunnel.
Tunnel up but traffic not flowing: Check routing on both sides. Check if the tunnel destination is reachable via the underlay network. MTU issues (GRE + IPsec overhead can exceed 1500 bytes). Set `ip mtu 1400` and `ip tcp adjust-mss 1360` on tunnel interfaces.

## SSH (Secure Shell)

SSH provides encrypted remote access to network devices and servers. Uses TCP port 22.

### SSH Configuration (Linux Server)
Config file: `/etc/ssh/sshd_config`. Key settings: `Port 22` (change for security-through-obscurity). `PermitRootLogin no` (disable root SSH login). `PasswordAuthentication no` (force key-based auth). `PubkeyAuthentication yes` (enable key-based auth). `AllowUsers admin operator` (restrict which users can SSH).

### SSH Key Management
`ssh-keygen -t ed25519` — Generate a modern, secure key pair.
`ssh-copy-id user@server` — Copy public key to server's authorized_keys.
`ssh -i ~/.ssh/mykey user@server` — Connect using a specific key.
`ssh -L 8080:localhost:80 user@server` — Local port forwarding (access server's port 80 via local port 8080).
`ssh -R 8080:localhost:80 user@server` — Remote port forwarding.
`ssh -D 1080 user@server` — Dynamic SOCKS proxy.
`ssh -J jumphost user@target` — Connect through a jump host (ProxyJump).

### SSH Troubleshooting
Connection refused: SSH service not running. Wrong port. Firewall blocking port 22.
Permission denied: Wrong username or password. Key not in authorized_keys. Key file permissions too open (must be 600 for private key, 700 for .ssh directory).
Connection timeout: Host unreachable. Firewall dropping (not rejecting) packets. Wrong IP address.
Host key verification failed: Server was reinstalled or key changed. Remove old key: `ssh-keygen -R hostname`.
