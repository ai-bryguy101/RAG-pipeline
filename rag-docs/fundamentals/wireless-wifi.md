# Wireless Networking (Wi-Fi) — Reference Guide

## Wi-Fi Standards (IEEE 802.11)

### Standard Summary
802.11b (1999): 2.4 GHz, up to 11 Mbps. Legacy, rarely used.
802.11a (1999): 5 GHz, up to 54 Mbps. Better speed but shorter range.
802.11g (2003): 2.4 GHz, up to 54 Mbps. Backward compatible with 802.11b.
802.11n / Wi-Fi 4 (2009): 2.4 and 5 GHz, up to 600 Mbps. Introduced MIMO (multiple antennas).
802.11ac / Wi-Fi 5 (2014): 5 GHz only, up to 6.9 Gbps (theoretical). MU-MIMO, wider channels (80/160 MHz), beamforming.
802.11ax / Wi-Fi 6 (2020): 2.4 and 5 GHz, up to 9.6 Gbps. OFDMA for better efficiency in dense environments. Target Wake Time for IoT power savings.
802.11ax / Wi-Fi 6E (2021): Extends Wi-Fi 6 into the 6 GHz band. More channels, less interference.
802.11be / Wi-Fi 7 (2024): 2.4, 5, and 6 GHz, up to 46 Gbps. 320 MHz channels, Multi-Link Operation.

### 2.4 GHz vs 5 GHz vs 6 GHz
2.4 GHz: Longer range, better wall penetration. Only 3 non-overlapping channels (1, 6, 11). More crowded and interference-prone (microwaves, Bluetooth, other Wi-Fi).
5 GHz: Shorter range, less wall penetration. Many more non-overlapping channels. Less interference. Better throughput.
6 GHz (Wi-Fi 6E/7): Shortest range. Many wide channels available (320 MHz in Wi-Fi 7). Least interference (new, uncrowded spectrum). Requires Wi-Fi 6E or newer devices.

## Wi-Fi Security

### Security Protocols
WEP (Wired Equivalent Privacy): Completely broken. Never use. Can be cracked in minutes.
WPA (Wi-Fi Protected Access): Temporary fix for WEP. Uses TKIP encryption. Deprecated.
WPA2 (2004): Uses AES-CCMP encryption. Still widely used. Personal mode uses a pre-shared key (PSK). Enterprise mode uses 802.1X/RADIUS for per-user authentication.
WPA3 (2018): Uses SAE (Simultaneous Authentication of Equals) instead of PSK — resistant to offline dictionary attacks. Forward secrecy (compromising today's key doesn't decrypt past traffic). Protected Management Frames (PMF) mandatory. Enterprise mode uses 192-bit encryption suite.

### Wi-Fi Authentication Modes
Personal (PSK): Everyone uses the same password. Simple but less secure (shared secret). Suitable for home and small office.
Enterprise (802.1X): Each user has individual credentials. Uses a RADIUS server for authentication. Supports certificate-based authentication (EAP-TLS). Much better for organizations — individual accountability, can revoke access per user.

## Wi-Fi Troubleshooting

### Slow Wi-Fi Performance
Channel congestion: Use a Wi-Fi analyzer (e.g., WiFi Analyzer app, `iw dev wlan0 scan`) to see which channels are crowded. Switch to a less congested channel. On 2.4 GHz, stick to channels 1, 6, or 11 only (non-overlapping).
Co-channel interference: Too many APs on the same channel. Reduce AP power or use a proper channel plan.
Adjacent channel interference: APs on overlapping channels (e.g., channels 1 and 3 on 2.4 GHz). Worse than co-channel interference because devices can't coordinate.
Hidden node problem: Two clients can hear the AP but not each other. They collide when transmitting simultaneously. Mitigation: enable RTS/CTS, adjust AP placement.
Too far from AP: Signal strength below -70 dBm is marginal. Below -80 dBm is poor. Move closer or add another AP.
Legacy clients: A single 802.11b device forces the entire AP to use slower protection mechanisms. Disable 802.11b support if possible.

### Wi-Fi Signal Strength (RSSI)
-30 dBm: Excellent (very close to AP).
-50 dBm: Excellent.
-60 dBm: Good (reliable connection).
-67 dBm: Minimum for VoIP and streaming.
-70 dBm: Fair (web browsing OK, streaming may buffer).
-80 dBm: Poor (frequent disconnects).
-90 dBm: Unusable.

### Wi-Fi Connection Issues
Can't connect at all: Verify SSID and password. Check if the correct security protocol is selected. Verify the AP is broadcasting the SSID (or manually add hidden SSID). Check if MAC filtering is blocking the client. Check if the AP has hit its client limit.
Connects but no internet: Check if the client got an IP via DHCP. Check if DNS is working. Check if the AP's uplink is functional. Look for captive portal issues.
Intermittent disconnections: Check for interference (2.4 GHz is especially prone). Check AP logs for deauthentication reasons. Check if the client is roaming between APs poorly. Update Wi-Fi drivers on the client.

### Linux Wi-Fi Commands
`iw dev` — List wireless interfaces.
`iw dev wlan0 scan | grep -E "SSID|signal|freq"` — Scan for networks.
`iw dev wlan0 link` — Show current connection details.
`iw dev wlan0 station dump` — Show connected station statistics.
`iwconfig wlan0` — Legacy command, shows wireless config.
`nmcli device wifi list` — List available Wi-Fi networks.
`nmcli device wifi connect SSID password PASSWORD` — Connect to network.
`wavemon` — Terminal-based Wi-Fi signal monitor.
`hostapd` — Turn a Linux machine into a Wi-Fi access point.

## Wireless AP Placement Best Practices
Use a site survey tool to map coverage before installing APs. Aim for -65 dBm or better everywhere that needs coverage. Overlap AP coverage by 15-20% for seamless roaming. Mount APs on ceilings (antennas radiate downward/outward). Avoid placing APs near metal objects, elevators, or thick concrete. Use 5 GHz for high-density areas (more channels, less interference). Stagger channels to minimize co-channel interference. Consider heat maps and user density — conference rooms need more capacity than hallways.

## Wireless Controller Architectures
Autonomous APs: Each AP is independently configured. Simple for small deployments. Difficult to manage at scale.
Controller-Based: A central Wireless LAN Controller (WLC) manages all APs. Centralized configuration, monitoring, and RF management. AP tunnels traffic to the controller (capwap). Examples: Cisco WLC, Aruba Mobility Controller.
Cloud-Managed: APs managed via a cloud dashboard. Easy deployment and monitoring. Examples: Cisco Meraki, Aruba Central, Ubiquiti UniFi.
