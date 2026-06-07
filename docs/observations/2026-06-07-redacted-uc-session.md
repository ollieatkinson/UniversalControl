# Redacted macOS Universal Control Session Summary

## Source

- Artifact: `mac-uc-session-20260607T072939Z`
- Created: 20260607T072939Z
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

- Total captured lines: 44707
- UniversalControl lines: 29815
- rapportd lines: 485
- mDNSResponder lines: 13429
- nearbyd lines: 115
- wifip2pd lines: 448
- Discovery keyword lines: 3255
- Session/control keyword lines: 6503
- Input/action keyword lines: 9132
- Error/rejection keyword lines: 724
- UniversalControl/rapportd discovery keyword lines: 77
- UniversalControl/rapportd session/control keyword lines: 6365
- UniversalControl/rapportd input/action keyword lines: 6154
- UniversalControl/rapportd error/rejection keyword lines: 96
- Native stream keyword lines: 0
- Native target/input keyword lines: 60
- Native sync/layout keyword lines: 96
- Proximity/ranging keyword lines: 156
- Native/proximity-process proximity keyword lines: 156
- Wi-Fi peer-to-peer/AWDL keyword lines: 6142
- Native/transport-process Wi-Fi P2P keyword lines: 6083
- Raw log lines: not included

## Session Phase Signals

- Connected event lines: 27
- Disconnect event lines: 0
- Connected-link empty transitions: 1
- Connected-link present transitions: 1
- Sync connected-devices updates: 1
- Target begin events: 21
- Target ready events: 21
- Target accept/reply events: 14
- TargetConnect message lines: 1
- Pointer focus move lines: 7
- Keyboard focus move lines: 3
- Remote pointing reset lines: 14
- Remote keyboard reset lines: 6
- First disconnect offset: unknown
- First reconnect-after-disconnect offset: unknown
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
- total pcap bytes: 8978962
- pcap byte sizes: `1844495`=1, `7134467`=1
- pcap capture classes: `awdl`=1, `primary-network`=1
- tcpdump packet decode: ok
- decoded packet lines: 29534
- packet counts by capture class: `awdl`=11020, `primary-network`=18514
- IP version counts: `ipv4`=18444, `ipv6`=11090
- transport counts: `tcp`=29335, `udp`=199
- protocol-relevant port hits: `3722`=9, `5353`=190
- TCP flow counts by capture class: `awdl`=5, `primary-network`=125
- TCP payload bytes by capture class: `awdl`=697164, `primary-network`=5571956
- mDNS service mentions: `_airplay-p2p._tcp.local.`=66, `_airplay._tcp.local.`=92, `_airport._tcp.local.`=2, `_apple-mobdev._tcp.local.`=2, `_apple-mobdev2._tcp.local.`=19, `_apple-pairable._tcp.local.`=2, `_companion-link._tcp.local.`=45, `_googlecast._tcp.local.`=9, `_ipp._tcp.local.`=2, `_ipps._tcp.local.`=2, `_ippusb._tcp.local.`=2, `_pdl-datastream._tcp.local.`=2, `_printer._tcp.local.`=2, `_ptp._tcp.local.`=2, `_raop._tcp.local.`=85, `_rdlink._tcp.local.`=12, `_remotepairing._tcp.local.`=12, `_scanner._tcp.local.`=2, `_universalcontrol._tcp.local.`=14, `_uscan._tcp.local.`=2, `_uscans._tcp.local.`=2
- pcap decode failures: 0
- raw packet data: not included
- raw endpoints and dynamic ports: not included

### AWDL TCP Flow Shapes

- #1: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=10862 payload_bytes=658280 nonzero_payload_packets=5796 max_payload_bytes=178 flags=`ack-only`=5066, `push`=5796 first_offset=6.23s last_offset=230.4s span=224.2s
- #2: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=94 payload_bytes=38884 nonzero_payload_packets=49 max_payload_bytes=1428 flags=`ack-only`=45, `ecn-cwr`=2, `push`=43 first_offset=6.16s last_offset=286.9s span=280.7s
- #3: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=4 payload_bytes=0 nonzero_payload_packets=0 max_payload_bytes=0 flags=`ack-only`=4 first_offset=110.5s last_offset=260.5s span=150.0s
- #4: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=4 payload_bytes=0 nonzero_payload_packets=0 max_payload_bytes=0 flags=`ack-only`=4 first_offset=110.5s last_offset=260.6s span=150.0s
- #5: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=4 payload_bytes=0 nonzero_payload_packets=0 max_payload_bytes=0 flags=`ack-only`=4 first_offset=111.0s last_offset=261.1s span=150.0s
- Raw endpoints, dynamic ports, and packet payloads: not included

### Primary Network TCP Flow Shapes

- #1: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=1346 payload_bytes=1285578 nonzero_payload_packets=934 max_payload_bytes=1440 flags=`ack-only`=407, `ecn-cwr`=1, `fin`=3, `push`=28, `syn`=2 first_offset=145.1s last_offset=196.2s span=51.2s
- #2: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=2172 payload_bytes=1282913 nonzero_payload_packets=1391 max_payload_bytes=1440 flags=`ack-only`=781, `ecn-cwr`=1, `push`=597 first_offset=3.01s last_offset=315.7s span=312.7s
- #3: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=4644 payload_bytes=1030568 nonzero_payload_packets=2752 max_payload_bytes=1440 flags=`ack-only`=1890, `ecn-cwr`=7, `push`=2134, `syn`=2 first_offset=126.6s last_offset=322.5s span=195.9s
- #4: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=5164 payload_bytes=366010 nonzero_payload_packets=2962 max_payload_bytes=1440 flags=`ack-only`=2202, `ecn-cwr`=1, `push`=2817 first_offset=18.3s last_offset=322.5s span=304.3s
- #5: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=380 payload_bytes=311546 nonzero_payload_packets=235 max_payload_bytes=1440 flags=`ack-only`=143, `ecn-cwr`=1, `push`=16, `syn`=2 first_offset=170.0s last_offset=320.2s span=150.1s
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
  - The old capture script left `dns-sd`, `log stream`, and `tcpdump` children running after it printed `Wrote`; those orphaned capture processes were stopped before this summary was generated.
  - Treat the packet and unified-log counts as a useful active-session signal shape, not as an exact 120 second total.
  - The operator attempted short benign text entry on both machines during the run, so input/action counters and packet payload bursts should be interpreted as mixed pointer, scroll, and keyboard activity rather than pointer-only traffic.
  - The run had no `_companion-link._tcp` or `_universalcontrol._tcp` browse rows, but packet decode did see mDNS mentions for both service types while native UniversalControl/Rapport target, sync/layout, proximity, Wi-Fi P2P, and TCP-heavy packet-shape counters were active.
  - The strongest packet clue is the dominant AWDL IPv6 link-local dynamic-port TCP flow: it starts near the beginning of the active window, carries most AWDL payload bytes, and lasts through most of the capture. A Windows native probe that reaches native admission should be compared against this AWDL high-port flow shape before chasing generic primary-network HTTPS traffic.
  - Do not paste raw hostnames, addresses, TXT values, interface identifiers, packet payloads, or unified-log lines.
