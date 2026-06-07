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
- TCP payload frame-shape packets by capture class: `awdl`=3042, `primary-network`=2819
- mDNS service mentions: `_airplay._tcp.local.`=12, `_airport._tcp.local.`=2, `_apple-mobdev._tcp.local.`=2, `_apple-mobdev2._tcp.local.`=30, `_apple-pairable._tcp.local.`=2, `_companion-link._tcp.local.`=20, `_googlecast._tcp.local.`=3, `_ipp._tcp.local.`=2, `_ipps._tcp.local.`=2, `_ippusb._tcp.local.`=2, `_pdl-datastream._tcp.local.`=2, `_printer._tcp.local.`=2, `_ptp._tcp.local.`=2, `_rdlink._tcp.local.`=11, `_remotepairing._tcp.local.`=20, `_scanner._tcp.local.`=2, `_universalcontrol._tcp.local.`=9, `_uscan._tcp.local.`=2, `_uscans._tcp.local.`=2
- pcap decode failures: 0
- pcap frame-shape decode failures: 0
- raw packet data: not included
- raw endpoints and dynamic ports: not included

### AWDL TCP Flow Shapes

- #1: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=5506 payload_bytes=329356 nonzero_payload_packets=2972 max_payload_bytes=174 flags=`ack-only`=2534, `push`=2972 first_offset=1.55s last_offset=72.8s span=71.2s
  - payload directions: `a_to_b` packets=2927 bytes=324932 top_lengths=`122`=1774, `93`=1034, `107`=74, `55`=16, `82`=12, `140`=8; `b_to_a` packets=45 bytes=4424 top_lengths=`55`=16, `82`=12, `140`=8, `174`=8, `48`=1
  - initial nonzero payload sequence: `a_to_b:140`, `a_to_b:93`, `a_to_b:122`, `a_to_b:174`, `a_to_b:122`, `b_to_a:55`, `a_to_b:122`, `a_to_b:122`, `b_to_a:82`, `b_to_a:55`, `a_to_b:122`, `a_to_b:122`, `a_to_b:122`, `a_to_b:122`, `a_to_b:122`, `a_to_b:122`, `a_to_b:122`, `a_to_b:93`, `a_to_b:122`, `a_to_b:93`, `a_to_b:122`, `a_to_b:93`, `a_to_b:122`, `a_to_b:93`
  - inter-payload gap buckets: `1-10ms`=1705, `10-100ms`=145, `100ms-1s`=33, `<1ms`=1077, `>=1s`=11
  - framing first-byte classes: `control`=2972
  - framing byte-class ratios: ascii=`10-49pct`=2955, `50-89pct`=17; high=`10-49pct`=1850, `50-89pct`=1122; zero=`1-9pct`=2972; control=`1-9pct`=921, `10-49pct`=2051
  - framing length-prefix candidates: `none`=2972
  - framing TLS record-like reads: `no`=2972
  - framing TLS record length matches: `no`=2972
  - initial framing samples: `#1:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#2:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#4:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#5:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#6:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#7:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#8:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#9:first=control,len_prefix=none,tls=no,ascii=50-89pct,high=10-49pct`, `#10:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#11:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#12:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`
- #2: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=128 payload_bytes=63336 nonzero_payload_packets=70 max_payload_bytes=1428 flags=`ack-only`=58, `ecn-cwr`=1, `push`=53 first_offset=1.54s last_offset=71.4s span=69.9s
  - payload directions: `a_to_b` packets=36 bytes=32979 top_lengths=`621`=17, `1428`=10, `978`=2, `1076`=1, `714`=1, `658`=1; `b_to_a` packets=34 bytes=30357 top_lengths=`621`=16, `1428`=11, `1255`=1, `867`=1, `1305`=1, `3`=1
  - initial nonzero payload sequence: `a_to_b:621`, `b_to_a:621`, `b_to_a:621`, `a_to_b:621`, `a_to_b:621`, `b_to_a:621`, `b_to_a:621`, `a_to_b:621`, `a_to_b:621`, `b_to_a:621`, `b_to_a:621`, `a_to_b:621`, `a_to_b:1428`, `a_to_b:1428`, `a_to_b:1076`, `a_to_b:1428`, `a_to_b:1428`, `b_to_a:1428`, `b_to_a:1428`, `b_to_a:1255`, `b_to_a:1428`, `a_to_b:714`, `b_to_a:867`, `a_to_b:658`
  - inter-payload gap buckets: `1-10ms`=21, `10-100ms`=10, `100ms-1s`=9, `<1ms`=18, `>=1s`=11
  - framing first-byte classes: `ascii`=7, `ascii-whitespace`=1, `control`=51, `high`=11
  - framing byte-class ratios: ascii=`10-49pct`=69, `50-89pct`=1; high=`10-49pct`=36, `50-89pct`=34; zero=`0pct`=2, `1-9pct`=68; control=`1-9pct`=6, `10-49pct`=64
  - framing length-prefix candidates: `none`=70
  - framing TLS record-like reads: `no`=70
  - framing TLS record length matches: `no`=70
  - initial framing samples: `#1:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#2:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#4:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#5:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#6:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#7:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#8:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#9:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#10:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#11:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#12:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`
- Raw endpoints, dynamic ports, and packet payloads: not included

### Primary Network TCP Flow Shapes

- #1: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=2369 payload_bytes=647964 nonzero_payload_packets=1434 max_payload_bytes=1440 flags=`ack-only`=935, `ecn-cwr`=1, `push`=1057 first_offset=0.000s last_offset=116.5s span=116.5s
  - payload directions: `a_to_b` packets=1309 bytes=487442 top_lengths=`1440`=273, `50`=166, `51`=162, `49`=132, `48`=90, `52`=85; `b_to_a` packets=125 bytes=160522 top_lengths=`1388`=108, `32`=6, `1092`=1, `1051`=1, `497`=1, `1304`=1
  - initial nonzero payload sequence: `a_to_b:47`, `a_to_b:50`, `a_to_b:52`, `a_to_b:49`, `a_to_b:48`, `a_to_b:50`, `a_to_b:48`, `a_to_b:44`, `a_to_b:47`, `a_to_b:170`, `a_to_b:51`, `a_to_b:52`, `a_to_b:50`, `a_to_b:50`, `a_to_b:51`, `a_to_b:50`, `a_to_b:52`, `a_to_b:51`, `a_to_b:51`, `a_to_b:53`, `a_to_b:51`, `a_to_b:48`, `a_to_b:51`, `a_to_b:51`
  - inter-payload gap buckets: `1-10ms`=230, `10-100ms`=452, `100ms-1s`=72, `<1ms`=653, `>=1s`=26
  - framing first-byte classes: `ascii`=131, `ascii-whitespace`=5, `control`=1086, `high`=210, `zero`=2
  - framing byte-class ratios: ascii=`10-49pct`=1415, `50-89pct`=19; high=`10-49pct`=971, `50-89pct`=463; zero=`0pct`=10, `1-9pct`=1424; control=`1-9pct`=91, `10-49pct`=1343
  - framing length-prefix candidates: `none`=1434
  - framing TLS record-like reads: `no`=391, `yes`=1043
  - framing TLS record length matches: `no`=439, `yes`=995
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#2:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#4:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#5:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#6:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#7:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#8:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#9:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#10:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#11:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#12:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`
- #2: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=215 payload_bytes=201475 nonzero_payload_packets=148 max_payload_bytes=1398 flags=`ack-only`=67, `push`=7 first_offset=1.43s last_offset=106.7s span=105.2s
  - payload directions: `a_to_b` packets=4 bytes=3401 top_lengths=`1398`=2, `299`=1, `306`=1; `b_to_a` packets=144 bytes=198074 top_lengths=`1388`=142, `430`=1, `548`=1
  - initial nonzero payload sequence: `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`
  - inter-payload gap buckets: `10-100ms`=2, `100ms-1s`=1, `<1ms`=143, `>=1s`=1
  - framing first-byte classes: `ascii`=52, `ascii-whitespace`=1, `control`=27, `high`=68
  - framing byte-class ratios: ascii=`10-49pct`=148; high=`10-49pct`=79, `50-89pct`=69; zero=`0pct`=1, `1-9pct`=147; control=`1-9pct`=6, `10-49pct`=142
  - framing length-prefix candidates: `none`=148
  - framing TLS record-like reads: `no`=142, `yes`=6
  - framing TLS record length matches: `no`=144, `yes`=4
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#2:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#4:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#5:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#6:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#7:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#8:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#9:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#10:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#11:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#12:first=control,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`
- #3: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=493 payload_bytes=91808 nonzero_payload_packets=330 max_payload_bytes=499 flags=`ack-only`=163, `push`=330 first_offset=0.702s last_offset=117.0s span=116.3s
  - payload directions: `a_to_b` packets=246 bytes=69605 top_lengths=`499`=123, `57`=67, `80`=21, `81`=15, `58`=7, `65`=3; `b_to_a` packets=84 bytes=22203 top_lengths=`185`=31, `347`=13, `184`=12, `350`=10, `346`=9, `348`=8
  - initial nonzero payload sequence: `b_to_a:348`, `a_to_b:80`, `a_to_b:499`, `a_to_b:58`, `a_to_b:499`, `b_to_a:185`, `a_to_b:58`, `a_to_b:499`, `b_to_a:347`, `a_to_b:82`, `a_to_b:499`, `a_to_b:65`, `a_to_b:499`, `b_to_a:185`, `a_to_b:57`, `a_to_b:499`, `b_to_a:348`, `a_to_b:81`, `a_to_b:499`, `a_to_b:57`, `a_to_b:499`, `b_to_a:185`, `a_to_b:57`, `a_to_b:499`
  - inter-payload gap buckets: `1-10ms`=120, `10-100ms`=79, `100ms-1s`=8, `<1ms`=85, `>=1s`=37
  - framing first-byte classes: `control`=330
  - framing byte-class ratios: ascii=`10-49pct`=327, `50-89pct`=3; high=`10-49pct`=199, `50-89pct`=131; zero=`0pct`=34, `1-9pct`=296; control=`1-9pct`=25, `10-49pct`=305
  - framing length-prefix candidates: `none`=330
  - framing TLS record-like reads: `yes`=330
  - framing TLS record length matches: `yes`=330
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#2:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#3:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#4:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#5:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#6:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#7:first=control,len_prefix=none,tls=yes,ascii=50-89pct,high=10-49pct`, `#8:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#9:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#10:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#11:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#12:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`
- #4: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=41 payload_bytes=18249 nonzero_payload_packets=22 max_payload_bytes=1440 flags=`ack-only`=13, `ecn-cwr`=2, `fin`=2, `push`=14, `rst`=2, `syn`=2 first_offset=7.98s last_offset=39.0s span=31.0s
  - payload directions: `a_to_b` packets=11 bytes=10036 top_lengths=`1440`=4, `303`=2, `1216`=1, `626`=1, `903`=1, `901`=1; `b_to_a` packets=11 bytes=8213 top_lengths=`1408`=4, `126`=1, `80`=1, `452`=1, `682`=1, `457`=1
  - initial nonzero payload sequence: `b_to_a:1408`, `b_to_a:126`, `a_to_b:1440`, `a_to_b:1440`, `a_to_b:1216`, `a_to_b:1440`, `a_to_b:1440`, `a_to_b:626`, `b_to_a:80`, `b_to_a:452`, `b_to_a:1408`, `b_to_a:682`, `a_to_b:303`, `a_to_b:303`, `a_to_b:903`, `b_to_a:457`, `b_to_a:1408`, `b_to_a:760`, `b_to_a:1408`, `a_to_b:901`, `a_to_b:24`, `b_to_a:24`
  - inter-payload gap buckets: `1-10ms`=4, `10-100ms`=2, `100ms-1s`=3, `<1ms`=11, `>=1s`=1
  - framing first-byte classes: `ascii`=2, `control`=14, `high`=6
  - framing byte-class ratios: ascii=`10-49pct`=22; high=`10-49pct`=14, `50-89pct`=8; zero=`1-9pct`=22; control=`1-9pct`=1, `10-49pct`=21
  - framing length-prefix candidates: `none`=22
  - framing TLS record-like reads: `no`=8, `yes`=14
  - framing TLS record length matches: `no`=14, `yes`=8
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#2:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#4:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#5:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#6:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#7:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#8:first=ascii,len_prefix=none,tls=no,ascii=10-49pct,high=50-89pct`, `#9:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#10:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#11:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#12:first=high,len_prefix=none,tls=no,ascii=10-49pct,high=10-49pct`
- #5: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=44 payload_bytes=15764 nonzero_payload_packets=25 max_payload_bytes=1161 flags=`ack-only`=19, `push`=25 first_offset=42.2s last_offset=45.4s span=3.25s
  - payload directions: `a_to_b` packets=12 bytes=3016 top_lengths=`77`=4, `79`=2, `422`=2, `429`=2, `424`=2; `b_to_a` packets=13 bytes=12748 top_lengths=`1161`=3, `811`=3, `810`=2, `1159`=1, `1041`=1, `1160`=1
  - initial nonzero payload sequence: `a_to_b:77`, `a_to_b:79`, `a_to_b:77`, `b_to_a:1159`, `b_to_a:1041`, `b_to_a:1161`, `b_to_a:1161`, `a_to_b:422`, `a_to_b:429`, `a_to_b:424`, `b_to_a:811`, `b_to_a:811`, `b_to_a:810`, `a_to_b:77`, `a_to_b:79`, `a_to_b:77`, `b_to_a:1160`, `a_to_b:422`, `b_to_a:1161`, `a_to_b:424`, `b_to_a:1040`, `a_to_b:429`, `b_to_a:812`, `b_to_a:810`
  - inter-payload gap buckets: `1-10ms`=13, `10-100ms`=2, `100ms-1s`=1, `<1ms`=7, `>=1s`=1
  - framing first-byte classes: `control`=25
  - framing byte-class ratios: ascii=`10-49pct`=25; high=`10-49pct`=8, `50-89pct`=17; zero=`0pct`=1, `1-9pct`=24; control=`1-9pct`=3, `10-49pct`=22
  - framing length-prefix candidates: `none`=25
  - framing TLS record-like reads: `yes`=25
  - framing TLS record length matches: `yes`=25
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#2:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#4:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#5:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#6:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#7:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#8:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#9:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#10:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=50-89pct`, `#11:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`, `#12:first=control,len_prefix=none,tls=yes,ascii=10-49pct,high=10-49pct`
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
  - Redacted phase counters show disconnect activity followed by reconnect/focus activity, so this run is useful for comparing Windows reconnect-state behavior.
  - The strongest packet clue is the dominant AWDL IPv6 link-local dynamic-port TCP flow. A Windows native probe that reaches admission should be compared against this flow's payload-length frequencies, initial length sequence, and gap buckets before chasing generic primary-network HTTPS traffic.
  - Native UniversalControl/Rapport target or sync/layout counters are active, so packet bursts should be interpreted together with focus, target-ready, and layout state rather than as raw pointer traffic alone.
  - The action timeline includes pointer movement, scrolling, and harmless key activity; interpret input/action counters and packet bursts as mixed input activity, not pointer-only traffic. Literal typed text is intentionally not recorded.
  - Do not paste raw hostnames, addresses, TXT values, interface identifiers, packet payloads, typed text, or unified-log lines.
