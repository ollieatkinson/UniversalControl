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
- TCP payload frame-shape packets by capture class: `awdl`=5845, `primary-network`=10647
- mDNS service mentions: `_airplay-p2p._tcp.local.`=66, `_airplay._tcp.local.`=92, `_airport._tcp.local.`=2, `_apple-mobdev._tcp.local.`=2, `_apple-mobdev2._tcp.local.`=19, `_apple-pairable._tcp.local.`=2, `_companion-link._tcp.local.`=45, `_googlecast._tcp.local.`=9, `_ipp._tcp.local.`=2, `_ipps._tcp.local.`=2, `_ippusb._tcp.local.`=2, `_pdl-datastream._tcp.local.`=2, `_printer._tcp.local.`=2, `_ptp._tcp.local.`=2, `_raop._tcp.local.`=85, `_rdlink._tcp.local.`=12, `_remotepairing._tcp.local.`=12, `_scanner._tcp.local.`=2, `_universalcontrol._tcp.local.`=14, `_uscan._tcp.local.`=2, `_uscans._tcp.local.`=2
- pcap decode failures: 0
- pcap frame-shape decode failures: 0
- raw packet data: not included
- raw endpoints and dynamic ports: not included

### AWDL TCP Flow Shapes

- #1: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=10862 payload_bytes=658280 nonzero_payload_packets=5796 max_payload_bytes=178 flags=`ack-only`=5066, `push`=5796 first_offset=6.23s last_offset=230.4s span=224.2s
  - payload directions: `a_to_b` packets=5757 bytes=654444 top_lengths=`126`=3298, `97`=2281, `93`=99, `111`=40, `59`=14, `86`=10; `b_to_a` packets=39 bytes=3836 top_lengths=`55`=14, `82`=10, `140`=7, `174`=7, `48`=1
  - initial nonzero payload sequence: `a_to_b:52`, `b_to_a:48`, `a_to_b:144`, `a_to_b:178`, `a_to_b:126`, `a_to_b:126`, `b_to_a:55`, `b_to_a:82`, `b_to_a:55`, `a_to_b:126`, `a_to_b:126`, `a_to_b:126`, `a_to_b:126`, `a_to_b:126`, `a_to_b:97`, `a_to_b:126`, `a_to_b:97`, `a_to_b:126`, `a_to_b:97`, `a_to_b:126`, `a_to_b:97`, `a_to_b:126`, `a_to_b:97`, `a_to_b:126`
  - inter-payload gap buckets: `1-10ms`=3162, `10-100ms`=197, `100ms-1s`=56, `<1ms`=2369, `>=1s`=11
  - framing first-byte classes: `control`=5796
  - framing byte-class ratios: ascii=`10-49pct`=5768, `50-89pct`=28; high=`10-49pct`=3623, `50-89pct`=2173; zero=`1-9pct`=5796; control=`1-9pct`=1591, `10-49pct`=4205
  - framing length-prefix candidates: `none`=5796
  - framing TLS record-like reads: `no`=5796
  - framing TLS record length matches: `no`=5796
  - initial framing samples: `#1:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#2:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#4:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#5:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#6:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#7:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#8:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#9:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#10:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#11:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#12:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`
- #2: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=94 payload_bytes=38884 nonzero_payload_packets=49 max_payload_bytes=1428 flags=`ack-only`=45, `ecn-cwr`=2, `push`=43 first_offset=6.16s last_offset=286.9s span=280.7s
  - payload directions: `a_to_b` packets=24 bytes=18417 top_lengths=`621`=15, `1428`=3, `912`=1, `978`=1, `941`=1, `641`=1; `b_to_a` packets=25 bytes=20467 top_lengths=`621`=14, `1428`=4, `1023`=1, `1153`=1, `978`=1, `940`=1
  - initial nonzero payload sequence: `a_to_b:1428`, `a_to_b:1428`, `a_to_b:912`, `a_to_b:1428`, `b_to_a:1428`, `b_to_a:1428`, `b_to_a:1023`, `b_to_a:1428`, `b_to_a:1428`, `b_to_a:1153`, `a_to_b:978`, `a_to_b:941`, `b_to_a:978`, `b_to_a:940`, `a_to_b:641`, `a_to_b:672`, `b_to_a:635`, `a_to_b:621`, `a_to_b:621`, `b_to_a:621`, `b_to_a:621`, `a_to_b:621`, `a_to_b:621`, `b_to_a:621`
  - inter-payload gap buckets: `1-10ms`=19, `10-100ms`=7, `100ms-1s`=3, `<1ms`=7, `>=1s`=12
  - framing first-byte classes: `ascii`=2, `control`=43, `high`=4
  - framing byte-class ratios: ascii=`10-49pct`=49; high=`10-49pct`=26, `50-89pct`=23; zero=`1-9pct`=49; control=`1-9pct`=2, `10-49pct`=47
  - framing length-prefix candidates: `none`=49
  - framing TLS record-like reads: `no`=49
  - framing TLS record length matches: `no`=49
  - initial framing samples: `#1:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#2:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#3:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#4:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#5:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#6:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#7:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#8:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#9:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#10:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#11:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#12:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`
- #3: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=4 payload_bytes=0 nonzero_payload_packets=0 max_payload_bytes=0 flags=`ack-only`=4 first_offset=110.5s last_offset=260.5s span=150.0s
  - payload directions: `a_to_b` packets=0 bytes=0 top_lengths=none; `b_to_a` packets=0 bytes=0 top_lengths=none
  - initial nonzero payload sequence: none
  - inter-payload gap buckets: none
  - framing first-byte classes: none
  - framing byte-class ratios: ascii=none; high=none; zero=none; control=none
  - framing length-prefix candidates: none
  - framing TLS record-like reads: none
  - framing TLS record length matches: none
  - initial framing samples: none
- #4: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=4 payload_bytes=0 nonzero_payload_packets=0 max_payload_bytes=0 flags=`ack-only`=4 first_offset=110.5s last_offset=260.6s span=150.0s
  - payload directions: `a_to_b` packets=0 bytes=0 top_lengths=none; `b_to_a` packets=0 bytes=0 top_lengths=none
  - initial nonzero payload sequence: none
  - inter-payload gap buckets: none
  - framing first-byte classes: none
  - framing byte-class ratios: ascii=none; high=none; zero=none; control=none
  - framing length-prefix candidates: none
  - framing TLS record-like reads: none
  - framing TLS record length matches: none
  - initial framing samples: none
- #5: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=4 payload_bytes=0 nonzero_payload_packets=0 max_payload_bytes=0 flags=`ack-only`=4 first_offset=111.0s last_offset=261.1s span=150.0s
  - payload directions: `a_to_b` packets=0 bytes=0 top_lengths=none; `b_to_a` packets=0 bytes=0 top_lengths=none
  - initial nonzero payload sequence: none
  - inter-payload gap buckets: none
  - framing first-byte classes: none
  - framing byte-class ratios: ascii=none; high=none; zero=none; control=none
  - framing length-prefix candidates: none
  - framing TLS record-like reads: none
  - framing TLS record length matches: none
  - initial framing samples: none
- Raw endpoints, dynamic ports, and packet payloads: not included

### Primary Network TCP Flow Shapes

- #1: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=1346 payload_bytes=1285578 nonzero_payload_packets=934 max_payload_bytes=1440 flags=`ack-only`=407, `ecn-cwr`=1, `fin`=3, `push`=28, `syn`=2 first_offset=145.1s last_offset=196.2s span=51.2s
  - payload directions: `a_to_b` packets=59 bytes=77875 top_lengths=`1440`=37, `1398`=9, `1356`=3, `1272`=3, `558`=2, `191`=1; `b_to_a` packets=875 bytes=1207703 top_lengths=`1388`=869, `171`=1, `75`=1, `6`=1, `45`=1, `1203`=1
  - initial nonzero payload sequence: `b_to_a:171`, `a_to_b:1440`, `a_to_b:1440`, `a_to_b:191`, `b_to_a:75`, `b_to_a:6`, `b_to_a:45`, `a_to_b:51`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`
  - inter-payload gap buckets: `1-10ms`=25, `10-100ms`=3, `<1ms`=904, `>=1s`=1
  - framing first-byte classes: `ascii`=313, `ascii-whitespace`=8, `control`=138, `high`=473, `zero`=2
  - framing byte-class ratios: ascii=`0pct`=1, `10-49pct`=933; high=`0pct`=1, `10-49pct`=486, `50-89pct`=447; zero=`0pct`=10, `1-9pct`=921, `10-49pct`=3; control=`1-9pct`=49, `10-49pct`=884, `50-89pct`=1
  - framing length-prefix candidates: `none`=934
  - framing TLS record-like reads: `no`=907, `yes`=27
  - framing TLS record length matches: `no`=920, `yes`=14
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#2:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#3:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#4:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#5:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#6:first=control,len_prefix=none,tls=yes,ascii=0pct,high=0pct`, `#7:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#8:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#9:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#10:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#11:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#12:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`
- #2: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=2172 payload_bytes=1282913 nonzero_payload_packets=1391 max_payload_bytes=1440 flags=`ack-only`=781, `ecn-cwr`=1, `push`=597 first_offset=3.01s last_offset=315.7s span=312.7s
  - payload directions: `a_to_b` packets=355 bytes=105131 top_lengths=`162`=83, `161`=67, `172`=33, `24`=32, `332`=31, `1440`=24; `b_to_a` packets=1036 bytes=1177782 top_lengths=`1388`=770, `28`=33, `188`=33, `32`=16, `237`=9, `483`=9
  - initial nonzero payload sequence: `b_to_a:28`, `a_to_b:24`, `a_to_b:332`, `b_to_a:188`, `b_to_a:188`, `a_to_b:172`, `a_to_b:320`, `b_to_a:176`, `a_to_b:160`, `a_to_b:28`, `b_to_a:32`, `b_to_a:28`, `a_to_b:24`, `a_to_b:332`, `b_to_a:188`, `a_to_b:172`, `a_to_b:1440`, `a_to_b:1440`, `a_to_b:622`, `b_to_a:237`, `b_to_a:483`, `a_to_b:161`, `a_to_b:161`, `a_to_b:161`
  - inter-payload gap buckets: `1-10ms`=108, `10-100ms`=122, `100ms-1s`=130, `<1ms`=958, `>=1s`=72
  - framing first-byte classes: `ascii`=294, `ascii-whitespace`=7, `control`=677, `high`=410, `zero`=3
  - framing byte-class ratios: ascii=`1-9pct`=1, `10-49pct`=1382, `50-89pct`=8; high=`10-49pct`=749, `50-89pct`=642; zero=`0pct`=45, `1-9pct`=1346; control=`0pct`=1, `1-9pct`=76, `10-49pct`=1314
  - framing length-prefix candidates: `none`=1391
  - framing TLS record-like reads: `no`=811, `yes`=580
  - framing TLS record length matches: `no`=898, `yes`=493
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#2:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#4:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#5:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#6:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#7:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#8:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#9:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#10:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#11:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#12:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`
- #3: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=4644 payload_bytes=1030568 nonzero_payload_packets=2752 max_payload_bytes=1440 flags=`ack-only`=1890, `ecn-cwr`=7, `push`=2134, `syn`=2 first_offset=126.6s last_offset=322.5s span=195.9s
  - payload directions: `a_to_b` packets=2360 bytes=508383 top_lengths=`50`=357, `51`=297, `49`=278, `1440`=250, `52`=192, `48`=189; `b_to_a` packets=392 bytes=522185 top_lengths=`1388`=370, `32`=9, `238`=1, `80`=1, `654`=1, `184`=1
  - initial nonzero payload sequence: `b_to_a:238`, `a_to_b:1440`, `a_to_b:1440`, `a_to_b:217`, `b_to_a:80`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:654`, `b_to_a:1388`, `a_to_b:1440`, `a_to_b:251`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`
  - inter-payload gap buckets: `1-10ms`=424, `10-100ms`=1036, `100ms-1s`=109, `<1ms`=1154, `>=1s`=28
  - framing first-byte classes: `ascii`=250, `ascii-whitespace`=6, `control`=2191, `high`=302, `zero`=3
  - framing byte-class ratios: ascii=`10-49pct`=2699, `50-89pct`=53; high=`10-49pct`=1876, `50-89pct`=876; zero=`0pct`=18, `1-9pct`=2733, `10-49pct`=1; control=`0pct`=1, `1-9pct`=161, `10-49pct`=2590
  - framing length-prefix candidates: `none`=2752
  - framing TLS record-like reads: `no`=624, `yes`=2128
  - framing TLS record length matches: `no`=679, `yes`=2073
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#2:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#3:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#4:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#5:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#6:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#7:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#8:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#9:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#10:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#11:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#12:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`
- #4: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=5164 payload_bytes=366010 nonzero_payload_packets=2962 max_payload_bytes=1440 flags=`ack-only`=2202, `ecn-cwr`=1, `push`=2817 first_offset=18.3s last_offset=322.5s span=304.3s
  - payload directions: `a_to_b` packets=2894 bytes=297631 top_lengths=`50`=482, `51`=401, `49`=395, `48`=283, `52`=242, `47`=157; `b_to_a` packets=68 bytes=68379 top_lengths=`1388`=48, `32`=16, `551`=1, `277`=1, `214`=1, `201`=1
  - initial nonzero payload sequence: `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `b_to_a:1388`
  - inter-payload gap buckets: `1-10ms`=473, `10-100ms`=1516, `100ms-1s`=123, `<1ms`=832, `>=1s`=17
  - framing first-byte classes: `ascii`=42, `ascii-whitespace`=3, `control`=2835, `high`=81, `zero`=1
  - framing byte-class ratios: ascii=`10-49pct`=2906, `50-89pct`=56; high=`10-49pct`=2184, `50-89pct`=778; zero=`0pct`=10, `1-9pct`=2952; control=`1-9pct`=171, `10-49pct`=2791
  - framing length-prefix candidates: `none`=2962
  - framing TLS record-like reads: `no`=146, `yes`=2816
  - framing TLS record length matches: `no`=166, `yes`=2796
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#2:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#4:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#5:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#6:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#7:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#8:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#9:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#10:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#11:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#12:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`
- #5: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=380 payload_bytes=311546 nonzero_payload_packets=235 max_payload_bytes=1440 flags=`ack-only`=143, `ecn-cwr`=1, `push`=16, `syn`=2 first_offset=170.0s last_offset=320.2s span=150.1s
  - payload directions: `a_to_b` packets=10 bytes=8248 top_lengths=`1398`=3, `1440`=2, `202`=1, `51`=1, `301`=1, `311`=1; `b_to_a` packets=225 bytes=303298 top_lengths=`1388`=217, `45`=2, `174`=1, `75`=1, `6`=1, `428`=1
  - initial nonzero payload sequence: `b_to_a:174`, `a_to_b:1440`, `a_to_b:1440`, `a_to_b:202`, `b_to_a:75`, `b_to_a:6`, `b_to_a:45`, `b_to_a:45`, `a_to_b:51`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`
  - inter-payload gap buckets: `1-10ms`=6, `10-100ms`=9, `100ms-1s`=1, `<1ms`=216, `>=1s`=2
  - framing first-byte classes: `ascii`=79, `ascii-whitespace`=2, `control`=47, `high`=106, `zero`=1
  - framing byte-class ratios: ascii=`0pct`=1, `10-49pct`=234; high=`0pct`=1, `10-49pct`=119, `50-89pct`=115; zero=`0pct`=1, `1-9pct`=231, `10-49pct`=3; control=`1-9pct`=17, `10-49pct`=217, `50-89pct`=1
  - framing length-prefix candidates: `none`=235
  - framing TLS record-like reads: `no`=219, `yes`=16
  - framing TLS record length matches: `no`=224, `yes`=11
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#2:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#3:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#4:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#5:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#6:first=control,len_prefix=none,tls=yes,ascii=0pct,high=0pct`, `#7:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#8:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#9:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#10:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#11:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#12:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`
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
  - Packet flow summaries are length/timing evidence only: direction labels are arbitrary within each flow, and raw endpoints, dynamic ports, TCP payloads, TXT values, interface identifiers, and unified-log lines are not included.
  - Decoded pcap timing exceeds the requested capture duration; treat packet and unified-log counts as active-session signal shape rather than an exact bounded window.
  - The strongest packet clue is the dominant AWDL IPv6 link-local dynamic-port TCP flow. A Windows native probe that reaches admission should be compared against this flow's payload-length frequencies, initial length sequence, and gap buckets before chasing generic primary-network HTTPS traffic.
  - Native UniversalControl/Rapport target or sync/layout counters are active, so packet bursts should be interpreted together with focus, target-ready, and layout state rather than as raw pointer traffic alone.
  - The action timeline includes pointer movement, scrolling, and harmless key activity; interpret input/action counters and packet bursts as mixed input activity, not pointer-only traffic. Literal typed text is intentionally not recorded.
  - Do not paste raw hostnames, addresses, TXT values, interface identifiers, packet payloads, typed text, or unified-log lines.
