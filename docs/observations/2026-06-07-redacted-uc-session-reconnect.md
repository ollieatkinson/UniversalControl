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
  - payload burst count: 21
  - payload burst packet buckets: `1`=6, `2`=2, `21-100`=1, `3-5`=1, `>100`=11
  - payload burst byte buckets: `1-128`=7, `129-512`=2, `2049-16384`=3, `>16384`=9
  - payload burst duration buckets: `1-5s`=8, `10-100ms`=2, `100ms-1s`=5, `<10ms`=6
  - payload burst idle gap buckets: `1-5s`=8, `250ms-1s`=9, `5-15s`=3
  - payload burst direction patterns: `a_to_b_only`=11, `bidirectional`=10
  - payload burst length fingerprints: `82x1`=4, `122x111+93x84+55x2+82x2`=1, `122x105+93x84+55x2+82x1`=1, `122x64+93x36+55x2+82x2`=1, `122x168+107x34`=1, `122x89+93x73+55x2+82x1`=1, `122x462+93x379+55x4+82x2`=1, `48x2`=1
  - initial payload bursts: `#1:start=1.55s,end=2.64s,packets=201,bytes=21942,pattern=bidirectional,lengths=122x111+93x84+55x2+82x2`, `#2:start=3.14s,end=4.26s,packets=194,bytes=21128,pattern=bidirectional,lengths=122x105+93x84+55x2+82x1`, `#3:start=5.26s,end=5.26s,packets=1,bytes=82,pattern=a_to_b_only,lengths=82x1`, `#4:start=14.4s,end=15.1s,packets=106,bytes=11744,pattern=bidirectional,lengths=122x64+93x36+55x2+82x2`, `#5:start=16.3s,end=19.2s,packets=202,bytes=24134,pattern=a_to_b_only,lengths=122x168+107x34`, `#6:start=20.2s,end=21.2s,packets=167,bytes=18153,pattern=bidirectional,lengths=122x89+93x73+55x2+82x1`, `#7:start=23.4s,end=28.2s,packets=851,bytes=92623,pattern=bidirectional,lengths=122x462+93x379+55x4+82x2`, `#8:start=30.3s,end=30.3s,packets=1,bytes=82,pattern=a_to_b_only,lengths=82x1`, `#9:start=44.9s,end=45.0s,packets=2,bytes=96,pattern=bidirectional,lengths=48x2`, `#10:start=46.9s,end=48.8s,packets=231,bytes=26008,pattern=bidirectional,lengths=122x155+93x70+55x2+82x2`, `#11:start=49.3s,end=50.2s,packets=45,bytes=5460,pattern=a_to_b_only,lengths=122x43+107x2`, `#12:start=50.6s,end=50.6s,packets=1,bytes=122,pattern=a_to_b_only,lengths=122x1`
  - framing first-byte classes: `control`=2972
  - framing byte-class ratios: ascii=`10-49pct`=2955, `50-89pct`=17; high=`10-49pct`=1850, `50-89pct`=1122; zero=`1-9pct`=2972; control=`1-9pct`=921, `10-49pct`=2051
  - framing entropy buckets: `4-6bits`=48, `6-7bits`=2923, `7-8bits`=1
  - framing byte-diversity buckets: `129-256`=6, `17-64`=35, `65-128`=2931
  - framing length-prefix candidates: `none`=2972
  - framing TLS record-like reads: `no`=2972
  - framing TLS record length matches: `no`=2972
  - initial framing samples: `#1:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=50-89pct`, `#2:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#4:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#5:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=50-89pct`, `#6:first=control,len_prefix=none,tls=no,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#7:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#8:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#9:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=50-89pct,high=10-49pct`, `#10:first=control,len_prefix=none,tls=no,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#11:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#12:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=10-49pct`
- #2: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=128 payload_bytes=63336 nonzero_payload_packets=70 max_payload_bytes=1428 flags=`ack-only`=58, `ecn-cwr`=1, `push`=53 first_offset=1.54s last_offset=71.4s span=69.9s
  - payload directions: `a_to_b` packets=36 bytes=32979 top_lengths=`621`=17, `1428`=10, `978`=2, `1076`=1, `714`=1, `658`=1; `b_to_a` packets=34 bytes=30357 top_lengths=`621`=16, `1428`=11, `1255`=1, `867`=1, `1305`=1, `3`=1
  - initial nonzero payload sequence: `a_to_b:621`, `b_to_a:621`, `b_to_a:621`, `a_to_b:621`, `a_to_b:621`, `b_to_a:621`, `b_to_a:621`, `a_to_b:621`, `a_to_b:621`, `b_to_a:621`, `b_to_a:621`, `a_to_b:621`, `a_to_b:1428`, `a_to_b:1428`, `a_to_b:1076`, `a_to_b:1428`, `a_to_b:1428`, `b_to_a:1428`, `b_to_a:1428`, `b_to_a:1255`, `b_to_a:1428`, `a_to_b:714`, `b_to_a:867`, `a_to_b:658`
  - inter-payload gap buckets: `1-10ms`=21, `10-100ms`=10, `100ms-1s`=9, `<1ms`=18, `>=1s`=11
  - payload burst count: 16
  - payload burst packet buckets: `2`=11, `21-100`=1, `3-5`=2, `6-20`=2
  - payload burst byte buckets: `2049-16384`=3, `513-2048`=12, `>16384`=1
  - payload burst duration buckets: `10-100ms`=3, `100ms-1s`=3, `<10ms`=10
  - payload burst idle gap buckets: `1-5s`=6, `250ms-1s`=4, `5-15s`=5
  - payload burst direction patterns: `bidirectional`=16
  - payload burst length fingerprints: `621x2`=11, `1428x7+658x1+714x1+867x1`=1, `1428x14+641x2+978x2+3x1`=1, `621x1+635x1+672x1`=1, `621x6`=1, `621x4`=1
  - initial payload bursts: `#1:start=1.54s,end=1.55s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`, `#2:start=4.22s,end=4.23s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`, `#3:start=14.4s,end=14.4s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`, `#4:start=21.1s,end=21.1s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`, `#5:start=23.4s,end=23.4s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`, `#6:start=28.2s,end=28.2s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`, `#7:start=41.9s,end=42.3s,packets=12,bytes=14566,pattern=bidirectional,lengths=1428x7+658x1+714x1+867x1`, `#8:start=44.6s,end=45.0s,packets=23,bytes=26970,pattern=bidirectional,lengths=1428x14+641x2+978x2+3x1`, `#9:start=45.7s,end=45.7s,packets=3,bytes=1928,pattern=bidirectional,lengths=621x1+635x1+672x1`, `#10:start=46.9s,end=46.9s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`, `#11:start=57.9s,end=57.9s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`, `#12:start=67.5s,end=67.5s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`
  - framing first-byte classes: `ascii`=7, `ascii-whitespace`=1, `control`=51, `high`=11
  - framing byte-class ratios: ascii=`10-49pct`=69, `50-89pct`=1; high=`10-49pct`=36, `50-89pct`=34; zero=`0pct`=2, `1-9pct`=68; control=`1-9pct`=6, `10-49pct`=64
  - framing entropy buckets: `0-2bits`=1, `2-4bits`=1, `7-8bits`=68
  - framing byte-diversity buckets: `129-256`=68, `2-4`=1, `5-16`=1
  - framing length-prefix candidates: `none`=70
  - framing TLS record-like reads: `no`=70
  - framing TLS record length matches: `no`=70
  - initial framing samples: `#1:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#2:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#4:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#5:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#6:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#7:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#8:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#9:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#10:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#11:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#12:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`
- Raw endpoints, dynamic ports, and packet payloads: not included

### Primary Network TCP Flow Shapes

- #1: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=2369 payload_bytes=647964 nonzero_payload_packets=1434 max_payload_bytes=1440 flags=`ack-only`=935, `ecn-cwr`=1, `push`=1057 first_offset=0.000s last_offset=116.5s span=116.5s
  - payload directions: `a_to_b` packets=1309 bytes=487442 top_lengths=`1440`=273, `50`=166, `51`=162, `49`=132, `48`=90, `52`=85; `b_to_a` packets=125 bytes=160522 top_lengths=`1388`=108, `32`=6, `1092`=1, `1051`=1, `497`=1, `1304`=1
  - initial nonzero payload sequence: `a_to_b:47`, `a_to_b:50`, `a_to_b:52`, `a_to_b:49`, `a_to_b:48`, `a_to_b:50`, `a_to_b:48`, `a_to_b:44`, `a_to_b:47`, `a_to_b:170`, `a_to_b:51`, `a_to_b:52`, `a_to_b:50`, `a_to_b:50`, `a_to_b:51`, `a_to_b:50`, `a_to_b:52`, `a_to_b:51`, `a_to_b:51`, `a_to_b:53`, `a_to_b:51`, `a_to_b:48`, `a_to_b:51`, `a_to_b:51`
  - inter-payload gap buckets: `1-10ms`=230, `10-100ms`=452, `100ms-1s`=72, `<1ms`=653, `>=1s`=26
  - payload burst count: 56
  - payload burst packet buckets: `1`=6, `2`=6, `21-100`=16, `6-20`=25, `>100`=3
  - payload burst byte buckets: `1-128`=5, `129-512`=1, `2049-16384`=30, `513-2048`=8, `>16384`=12
  - payload burst duration buckets: `1-5s`=4, `10-100ms`=11, `100ms-1s`=16, `<10ms`=25
  - payload burst idle gap buckets: `1-5s`=23, `250ms-1s`=29, `5-15s`=3
  - payload burst direction patterns: `a_to_b_only`=39, `b_to_a_only`=10, `bidirectional`=7
  - payload burst length fingerprints: `28x1+32x1`=5, `914x1`=4, `51x23+49x21+48x20+50x19`=1, `1440x9+84x2+189x1+603x1`=1, `1388x9+1092x1`=1, `1440x16+526x1+529x1`=1, `51x17+50x14+47x9+49x8`=1, `1440x9+119x2+206x1`=1
  - initial payload bursts: `#1:start=0.000s,end=2.18s,packets=145,bytes=7147,pattern=a_to_b_only,lengths=51x23+49x21+48x20+50x19`, `#2:start=2.62s,end=2.62s,packets=13,bytes=13920,pattern=a_to_b_only,lengths=1440x9+84x2+189x1+603x1`, `#3:start=3.08s,end=3.10s,packets=10,bytes=13584,pattern=b_to_a_only,lengths=1388x9+1092x1`, `#4:start=3.45s,end=3.49s,packets=18,bytes=24095,pattern=a_to_b_only,lengths=1440x16+526x1+529x1`, `#5:start=4.19s,end=4.19s,packets=1,bytes=914,pattern=a_to_b_only,lengths=914x1`, `#6:start=14.3s,end=14.3s,packets=2,bytes=60,pattern=bidirectional,lengths=28x1+32x1`, `#7:start=28.9s,end=29.9s,packets=97,bytes=12415,pattern=a_to_b_only,lengths=51x17+50x14+47x9+49x8`, `#8:start=30.3s,end=30.4s,packets=12,bytes=13404,pattern=a_to_b_only,lengths=1440x9+119x2+206x1`, `#9:start=30.9s,end=30.9s,packets=10,bytes=13543,pattern=b_to_a_only,lengths=1388x9+1051x1`, `#10:start=31.5s,end=31.5s,packets=18,bytes=24098,pattern=a_to_b_only,lengths=1440x16+529x2`, `#11:start=34.4s,end=34.4s,packets=2,bytes=60,pattern=bidirectional,lengths=28x1+32x1`, `#12:start=38.9s,end=38.9s,packets=25,bytes=13604,pattern=a_to_b_only,lengths=1440x8+37x2+44x2+46x2`
  - framing first-byte classes: `ascii`=131, `ascii-whitespace`=5, `control`=1086, `high`=210, `zero`=2
  - framing byte-class ratios: ascii=`10-49pct`=1415, `50-89pct`=19; high=`10-49pct`=971, `50-89pct`=463; zero=`0pct`=10, `1-9pct`=1424; control=`1-9pct`=91, `10-49pct`=1343
  - framing entropy buckets: `2-4bits`=1, `4-6bits`=912, `6-7bits`=70, `7-8bits`=451
  - framing byte-diversity buckets: `129-256`=461, `17-64`=900, `5-16`=1, `65-128`=72
  - framing length-prefix candidates: `none`=1434
  - framing TLS record-like reads: `no`=391, `yes`=1043
  - framing TLS record length matches: `no`=439, `yes`=995
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=50-89pct`, `#2:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#4:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#5:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#6:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=50-89pct`, `#7:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=50-89pct`, `#8:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=50-89pct`, `#9:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#10:first=control,len_prefix=none,tls=yes,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#11:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#12:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`
- #2: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=215 payload_bytes=201475 nonzero_payload_packets=148 max_payload_bytes=1398 flags=`ack-only`=67, `push`=7 first_offset=1.43s last_offset=106.7s span=105.2s
  - payload directions: `a_to_b` packets=4 bytes=3401 top_lengths=`1398`=2, `299`=1, `306`=1; `b_to_a` packets=144 bytes=198074 top_lengths=`1388`=142, `430`=1, `548`=1
  - initial nonzero payload sequence: `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`
  - inter-payload gap buckets: `10-100ms`=2, `100ms-1s`=1, `<1ms`=143, `>=1s`=1
  - payload burst count: 2
  - payload burst packet buckets: `21-100`=2
  - payload burst byte buckets: `>16384`=2
  - payload burst duration buckets: `10-100ms`=1, `100ms-1s`=1
  - payload burst idle gap buckets: `>=15s`=1
  - payload burst direction patterns: `bidirectional`=2
  - payload burst length fingerprints: `1388x75+299x1+430x1+1398x1`=1, `1388x67+306x1+548x1+1398x1`=1
  - initial payload bursts: `#1:start=1.43s,end=1.62s,packets=78,bytes=106227,pattern=bidirectional,lengths=1388x75+299x1+430x1+1398x1`, `#2:start=61.4s,end=61.5s,packets=70,bytes=95248,pattern=bidirectional,lengths=1388x67+306x1+548x1+1398x1`
  - framing first-byte classes: `ascii`=52, `ascii-whitespace`=1, `control`=27, `high`=68
  - framing byte-class ratios: ascii=`10-49pct`=148; high=`10-49pct`=79, `50-89pct`=69; zero=`0pct`=1, `1-9pct`=147; control=`1-9pct`=6, `10-49pct`=142
  - framing entropy buckets: `7-8bits`=148
  - framing byte-diversity buckets: `129-256`=148
  - framing length-prefix candidates: `none`=148
  - framing TLS record-like reads: `no`=142, `yes`=6
  - framing TLS record length matches: `no`=144, `yes`=4
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#2:first=ascii,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#4:first=ascii,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#5:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#6:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#7:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#8:first=ascii,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#9:first=ascii,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#10:first=ascii,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#11:first=ascii,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#12:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`
- #3: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=493 payload_bytes=91808 nonzero_payload_packets=330 max_payload_bytes=499 flags=`ack-only`=163, `push`=330 first_offset=0.702s last_offset=117.0s span=116.3s
  - payload directions: `a_to_b` packets=246 bytes=69605 top_lengths=`499`=123, `57`=67, `80`=21, `81`=15, `58`=7, `65`=3; `b_to_a` packets=84 bytes=22203 top_lengths=`185`=31, `347`=13, `184`=12, `350`=10, `346`=9, `348`=8
  - initial nonzero payload sequence: `b_to_a:348`, `a_to_b:80`, `a_to_b:499`, `a_to_b:58`, `a_to_b:499`, `b_to_a:185`, `a_to_b:58`, `a_to_b:499`, `b_to_a:347`, `a_to_b:82`, `a_to_b:499`, `a_to_b:65`, `a_to_b:499`, `b_to_a:185`, `a_to_b:57`, `a_to_b:499`, `b_to_a:348`, `a_to_b:81`, `a_to_b:499`, `a_to_b:57`, `a_to_b:499`, `b_to_a:185`, `a_to_b:57`, `a_to_b:499`
  - inter-payload gap buckets: `1-10ms`=120, `10-100ms`=79, `100ms-1s`=8, `<1ms`=85, `>=1s`=37
  - payload burst count: 42
  - payload burst packet buckets: `3-5`=3, `6-20`=39
  - payload burst byte buckets: `2049-16384`=39, `513-2048`=3
  - payload burst duration buckets: `10-100ms`=25, `100ms-1s`=17
  - payload burst idle gap buckets: `1-5s`=37, `250ms-1s`=4
  - payload burst direction patterns: `bidirectional`=42
  - payload burst length fingerprints: `499x3+57x2+80x1+185x1`=10, `499x3+57x2+81x1+185x1`=8, `499x3+57x2+80x1+184x1`=5, `499x3+58x2+80x1+185x1`=3, `499x3+57x2+150x1+185x1`=2, `499x3+57x1+65x1+81x1`=2, `499x3+59x1+60x1+81x1`=2, `499x3+57x1+65x1+82x1`=1
  - initial payload bursts: `#1:start=0.702s,end=0.735s,packets=8,bytes=2226,pattern=bidirectional,lengths=499x3+58x2+80x1+185x1`, `#2:start=4.06s,end=4.23s,packets=8,bytes=2233,pattern=bidirectional,lengths=499x3+57x1+65x1+82x1`, `#3:start=7.58s,end=7.62s,packets=8,bytes=2225,pattern=bidirectional,lengths=499x3+57x2+81x1+185x1`, `#4:start=8.57s,end=8.58s,packets=3,bytes=764,pattern=bidirectional,lengths=81x1+184x1+499x1`, `#5:start=11.0s,end=11.0s,packets=8,bytes=2223,pattern=bidirectional,lengths=499x3+57x2+80x1+185x1`, `#6:start=14.3s,end=14.4s,packets=8,bytes=2228,pattern=bidirectional,lengths=499x3+58x1+59x1+81x1`, `#7:start=16.8s,end=16.8s,packets=3,bytes=768,pattern=bidirectional,lengths=85x1+184x1+499x1`, `#8:start=17.7s,end=17.9s,packets=8,bytes=2293,pattern=bidirectional,lengths=499x3+57x2+150x1+185x1`, `#9:start=21.2s,end=21.2s,packets=8,bytes=2224,pattern=bidirectional,lengths=499x3+57x2+80x1+185x1`, `#10:start=24.6s,end=24.7s,packets=8,bytes=2224,pattern=bidirectional,lengths=499x3+57x2+81x1+185x1`, `#11:start=28.1s,end=28.1s,packets=8,bytes=2225,pattern=bidirectional,lengths=499x3+57x2+81x1+185x1`, `#12:start=31.4s,end=31.5s,packets=8,bytes=2226,pattern=bidirectional,lengths=499x3+57x2+80x1+185x1`
  - framing first-byte classes: `control`=330
  - framing byte-class ratios: ascii=`10-49pct`=327, `50-89pct`=3; high=`10-49pct`=199, `50-89pct`=131; zero=`0pct`=34, `1-9pct`=296; control=`1-9pct`=25, `10-49pct`=305
  - framing entropy buckets: `4-6bits`=94, `6-7bits`=71, `7-8bits`=165
  - framing byte-diversity buckets: `129-256`=194, `17-64`=86, `65-128`=50
  - framing length-prefix candidates: `none`=330
  - framing TLS record-like reads: `yes`=330
  - framing TLS record length matches: `yes`=330
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#2:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=65-128,ascii=10-49pct,high=50-89pct`, `#3:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#4:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#5:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#6:first=control,len_prefix=none,tls=yes,entropy=6-7bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#7:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=50-89pct,high=10-49pct`, `#8:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#9:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#10:first=control,len_prefix=none,tls=yes,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#11:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#12:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`
- #4: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=41 payload_bytes=18249 nonzero_payload_packets=22 max_payload_bytes=1440 flags=`ack-only`=13, `ecn-cwr`=2, `fin`=2, `push`=14, `rst`=2, `syn`=2 first_offset=7.98s last_offset=39.0s span=31.0s
  - payload directions: `a_to_b` packets=11 bytes=10036 top_lengths=`1440`=4, `303`=2, `1216`=1, `626`=1, `903`=1, `901`=1; `b_to_a` packets=11 bytes=8213 top_lengths=`1408`=4, `126`=1, `80`=1, `452`=1, `682`=1, `457`=1
  - initial nonzero payload sequence: `b_to_a:1408`, `b_to_a:126`, `a_to_b:1440`, `a_to_b:1440`, `a_to_b:1216`, `a_to_b:1440`, `a_to_b:1440`, `a_to_b:626`, `b_to_a:80`, `b_to_a:452`, `b_to_a:1408`, `b_to_a:682`, `a_to_b:303`, `a_to_b:303`, `a_to_b:903`, `b_to_a:457`, `b_to_a:1408`, `b_to_a:760`, `b_to_a:1408`, `a_to_b:901`, `a_to_b:24`, `b_to_a:24`
  - inter-payload gap buckets: `1-10ms`=4, `10-100ms`=2, `100ms-1s`=3, `<1ms`=11, `>=1s`=1
  - payload burst count: 3
  - payload burst packet buckets: `2`=2, `6-20`=1
  - payload burst byte buckets: `1-128`=1, `513-2048`=1, `>16384`=1
  - payload burst duration buckets: `100ms-1s`=1, `<10ms`=2
  - payload burst idle gap buckets: `250ms-1s`=1, `>=15s`=1
  - payload burst direction patterns: `b_to_a_only`=1, `bidirectional`=2
  - payload burst length fingerprints: `126x1+1408x1`=1, `1440x4+1408x3+303x2+80x1`=1, `24x2`=1
  - initial payload bursts: `#1:start=8.12s,end=8.12s,packets=2,bytes=1534,pattern=b_to_a_only,lengths=126x1+1408x1`, `#2:start=8.39s,end=8.74s,packets=18,bytes=16667,pattern=bidirectional,lengths=1440x4+1408x3+303x2+80x1`, `#3:start=38.9s,end=38.9s,packets=2,bytes=48,pattern=bidirectional,lengths=24x2`
  - framing first-byte classes: `ascii`=2, `control`=14, `high`=6
  - framing byte-class ratios: ascii=`10-49pct`=22; high=`10-49pct`=14, `50-89pct`=8; zero=`1-9pct`=22; control=`1-9pct`=1, `10-49pct`=21
  - framing entropy buckets: `4-6bits`=3, `6-7bits`=1, `7-8bits`=18
  - framing byte-diversity buckets: `129-256`=18, `17-64`=3, `65-128`=1
  - framing length-prefix candidates: `none`=22
  - framing TLS record-like reads: `no`=8, `yes`=14
  - framing TLS record length matches: `no`=14, `yes`=8
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#2:first=ascii,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#4:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#5:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#6:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#7:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#8:first=ascii,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#9:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#10:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#11:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#12:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`
- #5: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=44 payload_bytes=15764 nonzero_payload_packets=25 max_payload_bytes=1161 flags=`ack-only`=19, `push`=25 first_offset=42.2s last_offset=45.4s span=3.25s
  - payload directions: `a_to_b` packets=12 bytes=3016 top_lengths=`77`=4, `79`=2, `422`=2, `429`=2, `424`=2; `b_to_a` packets=13 bytes=12748 top_lengths=`1161`=3, `811`=3, `810`=2, `1159`=1, `1041`=1, `1160`=1
  - initial nonzero payload sequence: `a_to_b:77`, `a_to_b:79`, `a_to_b:77`, `b_to_a:1159`, `b_to_a:1041`, `b_to_a:1161`, `b_to_a:1161`, `a_to_b:422`, `a_to_b:429`, `a_to_b:424`, `b_to_a:811`, `b_to_a:811`, `b_to_a:810`, `a_to_b:77`, `a_to_b:79`, `a_to_b:77`, `b_to_a:1160`, `a_to_b:422`, `b_to_a:1161`, `a_to_b:424`, `b_to_a:1040`, `a_to_b:429`, `b_to_a:812`, `b_to_a:810`
  - inter-payload gap buckets: `1-10ms`=13, `10-100ms`=2, `100ms-1s`=1, `<1ms`=7, `>=1s`=1
  - payload burst count: 2
  - payload burst packet buckets: `6-20`=2
  - payload burst byte buckets: `2049-16384`=2
  - payload burst duration buckets: `100ms-1s`=2
  - payload burst idle gap buckets: `1-5s`=1
  - payload burst direction patterns: `bidirectional`=2
  - payload burst length fingerprints: `77x2+811x2+1161x2+79x1`=1, `77x2+79x1+422x1+424x1`=1
  - initial payload bursts: `#1:start=42.2s,end=42.4s,packets=13,bytes=8462,pattern=bidirectional,lengths=77x2+811x2+1161x2+79x1`, `#2:start=45.3s,end=45.4s,packets=12,bytes=7302,pattern=bidirectional,lengths=77x2+79x1+422x1+424x1`
  - framing first-byte classes: `control`=25
  - framing byte-class ratios: ascii=`10-49pct`=25; high=`10-49pct`=8, `50-89pct`=17; zero=`0pct`=1, `1-9pct`=24; control=`1-9pct`=3, `10-49pct`=22
  - framing entropy buckets: `4-6bits`=6, `7-8bits`=19
  - framing byte-diversity buckets: `129-256`=19, `65-128`=6
  - framing length-prefix candidates: `none`=25
  - framing TLS record-like reads: `yes`=25
  - framing TLS record length matches: `yes`=25
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#2:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#4:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#5:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#6:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#7:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#8:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#9:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#10:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#11:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#12:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`
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
