# Redacted macOS Universal Control Session Summary

## Source

- Artifact: `mac-uc-session-20260607T083028Z`
- Created: 20260607T083028Z
- Duration: 120s
- tcpdump enabled: 1
- tcpdump interface count: 2
- Raw output: not included

## Action Timeline

- Timeline source: artifact README
- Idle before edge push: expected
- Edge push: expected
- Pointer movement on target: expected
- Harmless key press: expected
- Scroll: expected
- Return to local: expected
- Idle after return: expected

## DNS-SD Browse

### _companion-link._tcp

- Events: none observed

### _universalcontrol._tcp

- Events: none observed

## Unified Log

- Total captured lines: 20917
- UniversalControl lines: 15916
- rapportd lines: 78
- mDNSResponder lines: 4081
- nearbyd lines: 53
- wifip2pd lines: 317
- Discovery keyword lines: 926
- Session/control keyword lines: 3404
- Input/action keyword lines: 4316
- Error/rejection keyword lines: 348
- UniversalControl/rapportd discovery keyword lines: 6
- UniversalControl/rapportd session/control keyword lines: 3332
- UniversalControl/rapportd input/action keyword lines: 3361
- UniversalControl/rapportd error/rejection keyword lines: 69
- Native stream keyword lines: 0
- Native target/input keyword lines: 70
- Native sync/layout keyword lines: 114
- Proximity/ranging keyword lines: 28
- Native/proximity-process proximity keyword lines: 28
- Wi-Fi peer-to-peer/AWDL keyword lines: 3068
- Native/transport-process Wi-Fi P2P keyword lines: 3068
- Raw log lines: not included

## Session Phase Signals

- Connected event lines: 33
- Disconnect event lines: 5
- Connected-link empty transitions: 2
- Connected-link present transitions: 1
- Sync connected-devices updates: 2
- Target begin events: 24
- Target ready events: 24
- Target accept/reply events: 16
- TargetConnect message lines: 1
- Pointer focus move lines: 8
- Keyboard focus move lines: 4
- Remote pointing reset lines: 16
- Remote keyboard reset lines: 8
- First disconnect offset: 43.9s
- First reconnect-after-disconnect offset: 44.1s
- Raw session IDs, device IDs, and log lines: not included

## Network Snapshot

### Before

- Entries: 8
- rapportd entries: 8
- UniversalControl entries: 0
- TCP entries: 6
- UDP entries: 2
- TCP states: `ESTABLISHED`=4, `LISTEN`=2
- Known Apple ports seen: `3722`=2
- Raw endpoints and dynamic ports: not included

### After

- Entries: 8
- rapportd entries: 8
- UniversalControl entries: 0
- TCP entries: 6
- UDP entries: 2
- TCP states: `ESTABLISHED`=4, `LISTEN`=2
- Known Apple ports seen: `3722`=2
- Raw endpoints and dynamic ports: not included

## Packet Capture

- pcap files: 2
- total pcap bytes: 2850469
- pcap byte sizes: `1883025`=1, `967444`=1
- pcap capture classes: `awdl`=1, `primary-network`=1
- tcpdump packet decode: ok
- decoded packet lines: 10739
- packet counts by capture class: `awdl`=5634, `primary-network`=5105
- IP version counts: `ipv4`=5096, `ipv6`=5643
- transport counts: `tcp`=10677, `udp`=62
- protocol-relevant port hits: `3722`=3, `5353`=59
- TCP flow counts by capture class: `awdl`=2, `primary-network`=76
- TCP payload bytes by capture class: `awdl`=392692, `primary-network`=1450160
- mDNS service mentions: `_airplay._tcp.local.`=12, `_airport._tcp.local.`=2, `_apple-mobdev._tcp.local.`=2, `_apple-mobdev2._tcp.local.`=30, `_apple-pairable._tcp.local.`=2, `_companion-link._tcp.local.`=20, `_googlecast._tcp.local.`=3, `_ipp._tcp.local.`=2, `_ipps._tcp.local.`=2, `_ippusb._tcp.local.`=2, `_pdl-datastream._tcp.local.`=2, `_printer._tcp.local.`=2, `_ptp._tcp.local.`=2, `_rdlink._tcp.local.`=11, `_remotepairing._tcp.local.`=20, `_scanner._tcp.local.`=2, `_universalcontrol._tcp.local.`=9, `_uscan._tcp.local.`=2, `_uscans._tcp.local.`=2
- pcap decode failures: 0
- raw packet data: not included
- raw endpoints and dynamic ports: not included

### AWDL TCP Flow Shapes

- #1: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=5506 payload_bytes=329356 nonzero_payload_packets=2972 max_payload_bytes=174 flags=`ack-only`=2534, `push`=2972 first_offset=1.55s last_offset=72.8s span=71.2s
- #2: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=128 payload_bytes=63336 nonzero_payload_packets=70 max_payload_bytes=1428 flags=`ack-only`=58, `ecn-cwr`=1, `push`=53 first_offset=1.54s last_offset=71.4s span=69.9s
- Raw endpoints, dynamic ports, and packet payloads: not included

### Primary Network TCP Flow Shapes

- #1: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=2369 payload_bytes=647964 nonzero_payload_packets=1434 max_payload_bytes=1440 flags=`ack-only`=935, `ecn-cwr`=1, `push`=1057 first_offset=0.000s last_offset=116.5s span=116.5s
- #2: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=215 payload_bytes=201475 nonzero_payload_packets=148 max_payload_bytes=1398 flags=`ack-only`=67, `push`=7 first_offset=1.43s last_offset=106.7s span=105.2s
- #3: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=493 payload_bytes=91808 nonzero_payload_packets=330 max_payload_bytes=499 flags=`ack-only`=163, `push`=330 first_offset=0.702s last_offset=117.0s span=116.3s
- #4: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=41 payload_bytes=18249 nonzero_payload_packets=22 max_payload_bytes=1440 flags=`ack-only`=13, `ecn-cwr`=2, `fin`=2, `push`=14, `rst`=2, `syn`=2 first_offset=7.98s last_offset=39.0s span=31.0s
- #5: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=44 payload_bytes=15764 nonzero_payload_packets=25 max_payload_bytes=1161 flags=`ack-only`=19, `push`=25 first_offset=42.2s last_offset=45.4s span=3.25s
- Raw endpoints, dynamic ports, and packet payloads: not included

## Launchd

- UniversalControl before: state=active runs=1
- UniversalControl after: state=active runs=1
- rapportd before: state=active runs=1
- rapportd after: state=active runs=1

## Interpretation

- CompanionLink browse observed: no
- Universal Control DNS-SD browse observed: no
- UniversalControl/rapportd session signal: stream or sync/layout signal in redacted counts; inspect raw local artifacts
- Target/input negotiation signal: target/input negotiation signal in redacted counts; inspect raw local artifacts
- Proximity or Wi-Fi P2P side-channel signal: possible proximity or Wi-Fi peer-to-peer signal in redacted counts
- Notes:
  - Captured after native Universal Control was restored enough to connect, disconnect, and reconnect in the same 120 second run.
  - The operator attempted the same short benign text-entry action on both machines before and after reconnect; the literal text is intentionally not included.
  - Redacted phase counters show disconnect activity followed by reconnect/focus activity: disconnect event lines and connected-link empty transitions appear, then reconnect-after-disconnect is observed shortly afterward, with later target ready, target accept/reply, pointer focus, and keyboard focus lines.
  - The packet shape again points at AWDL IPv6 link-local dynamic-port TCP as the native session data path: two AWDL TCP flows carried payload, while primary-network traffic was mostly generic private-to-public HTTPS noise.
  - This is the best current baseline for Windows native-admission comparison because it contains both the steady-state input path and the reconnect state-machine path in one artifact.
  - Do not paste raw hostnames, addresses, TXT values, interface identifiers, packet payloads, or unified-log lines.
