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
- First connected offset: 7.33s
- First TargetConnect offset: 7.34s
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
- phase-window burst radius: +/-2.0s around redacted session phase offsets
- raw packet data: not included
- raw endpoints and dynamic ports: not included

### AWDL TCP Flow Shapes

- #1: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=10862 payload_bytes=658280 nonzero_payload_packets=5796 max_payload_bytes=178 flags=`ack-only`=5066, `push`=5796 first_offset=6.23s last_offset=230.4s span=224.2s
  - payload directions: `a_to_b` packets=5757 bytes=654444 top_lengths=`126`=3298, `97`=2281, `93`=99, `111`=40, `59`=14, `86`=10; `b_to_a` packets=39 bytes=3836 top_lengths=`55`=14, `82`=10, `140`=7, `174`=7, `48`=1
  - initial nonzero payload sequence: `a_to_b:52`, `b_to_a:48`, `a_to_b:144`, `a_to_b:178`, `a_to_b:126`, `a_to_b:126`, `b_to_a:55`, `b_to_a:82`, `b_to_a:55`, `a_to_b:126`, `a_to_b:126`, `a_to_b:126`, `a_to_b:126`, `a_to_b:126`, `a_to_b:97`, `a_to_b:126`, `a_to_b:97`, `a_to_b:126`, `a_to_b:97`, `a_to_b:126`, `a_to_b:97`, `a_to_b:126`, `a_to_b:97`, `a_to_b:126`
  - inter-payload gap buckets: `1-10ms`=3162, `10-100ms`=197, `100ms-1s`=56, `<1ms`=2369, `>=1s`=11
  - payload burst count: 25
  - payload burst packet buckets: `1`=3, `2`=1, `21-100`=4, `3-5`=2, `6-20`=2, `>100`=13
  - payload burst byte buckets: `1-128`=4, `129-512`=2, `2049-16384`=4, `513-2048`=2, `>16384`=13
  - payload burst duration buckets: `1-5s`=11, `10-100ms`=2, `100ms-1s`=7, `<10ms`=3, `>=5s`=2
  - payload burst idle gap buckets: `1-5s`=9, `250ms-1s`=13, `5-15s`=2
  - payload burst direction patterns: `a_to_b_only`=13, `bidirectional`=12
  - payload burst length fingerprints: `86x1`=3, `48x1+52x1`=1, `126x231+97x188+55x2+59x2`=1, `126x27+97x25+55x2+82x1`=1, `126x123+97x96+59x2+86x1`=1, `126x165+97x121+55x4+82x3`=1, `126x80+111x4`=1, `126x28+111x8`=1
  - initial payload bursts: `#1:start=6.23s,end=6.25s,packets=2,bytes=100,pattern=bidirectional,lengths=48x1+52x1`, `#2:start=8.10s,end=10.9s,packets=429,bytes=48374,pattern=bidirectional,lengths=126x231+97x188+55x2+59x2`, `#3:start=17.8s,end=18.0s,packets=57,bytes=6341,pattern=bidirectional,lengths=126x27+97x25+55x2+82x1`, `#4:start=18.4s,end=19.8s,packets=224,bytes=25328,pattern=bidirectional,lengths=126x123+97x96+59x2+86x1`, `#5:start=20.2s,end=22.2s,packets=302,bytes=34155,pattern=bidirectional,lengths=126x165+97x121+55x4+82x3`, `#6:start=22.5s,end=23.3s,packets=84,bytes=10524,pattern=a_to_b_only,lengths=126x80+111x4`, `#7:start=23.8s,end=24.8s,packets=36,bytes=4416,pattern=a_to_b_only,lengths=126x28+111x8`, `#8:start=25.4s,end=25.9s,packets=10,bytes=1054,pattern=a_to_b_only,lengths=111x6+97x4`, `#9:start=26.4s,end=26.5s,packets=3,bytes=378,pattern=a_to_b_only,lengths=126x3`, `#10:start=27.0s,end=28.9s,packets=292,bytes=33208,pattern=a_to_b_only,lengths=126x172+97x94+93x26`, `#11:start=29.2s,end=31.2s,packets=282,bytes=31383,pattern=a_to_b_only,lengths=126x149+93x73+97x60`, `#12:start=31.8s,end=32.0s,packets=26,bytes=3218,pattern=a_to_b_only,lengths=126x24+97x2`
  - phase-window payload bursts: `phase=first_connected,phase_offset=7.33s,burst=#1,start=6.23s,end=6.25s,packets=2,bytes=100,pattern=bidirectional,lengths=48x1+52x1`, `phase=first_connected,phase_offset=7.33s,burst=#2,start=8.10s,end=10.9s,packets=429,bytes=48374,pattern=bidirectional,lengths=126x231+97x188+55x2+59x2`, `phase=first_target_connect,phase_offset=7.34s,burst=#1,start=6.23s,end=6.25s,packets=2,bytes=100,pattern=bidirectional,lengths=48x1+52x1`, `phase=first_target_connect,phase_offset=7.34s,burst=#2,start=8.10s,end=10.9s,packets=429,bytes=48374,pattern=bidirectional,lengths=126x231+97x188+55x2+59x2`
  - framing first-byte classes: `control`=5796
  - framing byte-class ratios: ascii=`10-49pct`=5768, `50-89pct`=28; high=`10-49pct`=3623, `50-89pct`=2173; zero=`1-9pct`=5796; control=`1-9pct`=1591, `10-49pct`=4205
  - framing entropy buckets: `4-6bits`=45, `6-7bits`=5751
  - framing byte-diversity buckets: `129-256`=4, `17-64`=31, `65-128`=5761
  - framing length-prefix candidates: `none`=5796
  - framing TLS record-like reads: `no`=5796
  - framing TLS record length matches: `no`=5796
  - initial framing samples: `#1:first=control,len_prefix=none,tls=no,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#2:first=control,len_prefix=none,tls=no,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#4:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=50-89pct`, `#5:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=50-89pct`, `#6:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#7:first=control,len_prefix=none,tls=no,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#8:first=control,len_prefix=none,tls=no,entropy=4-6bits,diversity=65-128,ascii=10-49pct,high=50-89pct`, `#9:first=control,len_prefix=none,tls=no,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=50-89pct`, `#10:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#11:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=50-89pct`, `#12:first=control,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=50-89pct`
- #2: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=94 payload_bytes=38884 nonzero_payload_packets=49 max_payload_bytes=1428 flags=`ack-only`=45, `ecn-cwr`=2, `push`=43 first_offset=6.16s last_offset=286.9s span=280.7s
  - payload directions: `a_to_b` packets=24 bytes=18417 top_lengths=`621`=15, `1428`=3, `912`=1, `978`=1, `941`=1, `641`=1; `b_to_a` packets=25 bytes=20467 top_lengths=`621`=14, `1428`=4, `1023`=1, `1153`=1, `978`=1, `940`=1
  - initial nonzero payload sequence: `a_to_b:1428`, `a_to_b:1428`, `a_to_b:912`, `a_to_b:1428`, `b_to_a:1428`, `b_to_a:1428`, `b_to_a:1023`, `b_to_a:1428`, `b_to_a:1428`, `b_to_a:1153`, `a_to_b:978`, `a_to_b:941`, `b_to_a:978`, `b_to_a:940`, `a_to_b:641`, `a_to_b:672`, `b_to_a:635`, `a_to_b:621`, `a_to_b:621`, `b_to_a:621`, `b_to_a:621`, `a_to_b:621`, `a_to_b:621`, `b_to_a:621`
  - inter-payload gap buckets: `1-10ms`=19, `10-100ms`=7, `100ms-1s`=3, `<1ms`=7, `>=1s`=12
  - payload burst count: 15
  - payload burst packet buckets: `2`=11, `3-5`=3, `6-20`=1
  - payload burst byte buckets: `2049-16384`=2, `513-2048`=12, `>16384`=1
  - payload burst duration buckets: `10-100ms`=2, `100ms-1s`=2, `<10ms`=11
  - payload burst idle gap buckets: `1-5s`=5, `250ms-1s`=2, `5-15s`=5, `>=15s`=2
  - payload burst direction patterns: `bidirectional`=15
  - payload burst length fingerprints: `621x2`=11, `1428x7+978x2+641x1+912x1`=1, `621x3+635x1+672x1`=1, `621x4`=1, `674x2+658x1`=1
  - initial payload bursts: `#1:start=6.16s,end=6.26s,packets=15,bytes=17562,pattern=bidirectional,lengths=1428x7+978x2+641x1+912x1`, `#2:start=8.04s,end=8.10s,packets=5,bytes=3170,pattern=bidirectional,lengths=621x3+635x1+672x1`, `#3:start=10.9s,end=10.9s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`, `#4:start=17.8s,end=17.8s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`, `#5:start=19.7s,end=19.7s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`, `#6:start=20.2s,end=20.2s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`, `#7:start=20.6s,end=20.7s,packets=4,bytes=2484,pattern=bidirectional,lengths=621x4`, `#8:start=36.6s,end=36.6s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`, `#9:start=45.7s,end=45.7s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`, `#10:start=53.4s,end=53.4s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`, `#11:start=57.0s,end=57.1s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`, `#12:start=64.9s,end=64.9s,packets=2,bytes=1242,pattern=bidirectional,lengths=621x2`
  - phase-window payload bursts: `phase=first_connected,phase_offset=7.33s,burst=#1,start=6.16s,end=6.26s,packets=15,bytes=17562,pattern=bidirectional,lengths=1428x7+978x2+641x1+912x1`, `phase=first_connected,phase_offset=7.33s,burst=#2,start=8.04s,end=8.10s,packets=5,bytes=3170,pattern=bidirectional,lengths=621x3+635x1+672x1`, `phase=first_target_connect,phase_offset=7.34s,burst=#1,start=6.16s,end=6.26s,packets=15,bytes=17562,pattern=bidirectional,lengths=1428x7+978x2+641x1+912x1`, `phase=first_target_connect,phase_offset=7.34s,burst=#2,start=8.04s,end=8.10s,packets=5,bytes=3170,pattern=bidirectional,lengths=621x3+635x1+672x1`
  - framing first-byte classes: `ascii`=2, `control`=43, `high`=4
  - framing byte-class ratios: ascii=`10-49pct`=49; high=`10-49pct`=26, `50-89pct`=23; zero=`1-9pct`=49; control=`1-9pct`=2, `10-49pct`=47
  - framing entropy buckets: `7-8bits`=49
  - framing byte-diversity buckets: `129-256`=49
  - framing length-prefix candidates: `none`=49
  - framing TLS record-like reads: `no`=49
  - framing TLS record length matches: `no`=49
  - initial framing samples: `#1:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#2:first=ascii,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#3:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#4:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#5:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#6:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#7:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#8:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#9:first=ascii,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#10:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#11:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#12:first=control,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`
- #3: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=4 payload_bytes=0 nonzero_payload_packets=0 max_payload_bytes=0 flags=`ack-only`=4 first_offset=110.5s last_offset=260.5s span=150.0s
  - payload directions: `a_to_b` packets=0 bytes=0 top_lengths=none; `b_to_a` packets=0 bytes=0 top_lengths=none
  - initial nonzero payload sequence: none
  - inter-payload gap buckets: none
  - payload burst count: 0
  - payload burst packet buckets: none
  - payload burst byte buckets: none
  - payload burst duration buckets: none
  - payload burst idle gap buckets: none
  - payload burst direction patterns: none
  - payload burst length fingerprints: none
  - initial payload bursts: none
  - phase-window payload bursts: none
  - framing first-byte classes: none
  - framing byte-class ratios: ascii=none; high=none; zero=none; control=none
  - framing entropy buckets: none
  - framing byte-diversity buckets: none
  - framing length-prefix candidates: none
  - framing TLS record-like reads: none
  - framing TLS record length matches: none
  - initial framing samples: none
- #4: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=4 payload_bytes=0 nonzero_payload_packets=0 max_payload_bytes=0 flags=`ack-only`=4 first_offset=110.5s last_offset=260.6s span=150.0s
  - payload directions: `a_to_b` packets=0 bytes=0 top_lengths=none; `b_to_a` packets=0 bytes=0 top_lengths=none
  - initial nonzero payload sequence: none
  - inter-payload gap buckets: none
  - payload burst count: 0
  - payload burst packet buckets: none
  - payload burst byte buckets: none
  - payload burst duration buckets: none
  - payload burst idle gap buckets: none
  - payload burst direction patterns: none
  - payload burst length fingerprints: none
  - initial payload bursts: none
  - phase-window payload bursts: none
  - framing first-byte classes: none
  - framing byte-class ratios: ascii=none; high=none; zero=none; control=none
  - framing entropy buckets: none
  - framing byte-diversity buckets: none
  - framing length-prefix candidates: none
  - framing TLS record-like reads: none
  - framing TLS record length matches: none
  - initial framing samples: none
- #5: ip=ipv6 endpoints=`link-local-v6`<->`link-local-v6` ports=`dynamic`<->`dynamic` packets=4 payload_bytes=0 nonzero_payload_packets=0 max_payload_bytes=0 flags=`ack-only`=4 first_offset=111.0s last_offset=261.1s span=150.0s
  - payload directions: `a_to_b` packets=0 bytes=0 top_lengths=none; `b_to_a` packets=0 bytes=0 top_lengths=none
  - initial nonzero payload sequence: none
  - inter-payload gap buckets: none
  - payload burst count: 0
  - payload burst packet buckets: none
  - payload burst byte buckets: none
  - payload burst duration buckets: none
  - payload burst idle gap buckets: none
  - payload burst direction patterns: none
  - payload burst length fingerprints: none
  - initial payload bursts: none
  - phase-window payload bursts: none
  - framing first-byte classes: none
  - framing byte-class ratios: ascii=none; high=none; zero=none; control=none
  - framing entropy buckets: none
  - framing byte-diversity buckets: none
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
  - payload burst count: 2
  - payload burst packet buckets: `21-100`=1, `>100`=1
  - payload burst byte buckets: `>16384`=2
  - payload burst duration buckets: `100ms-1s`=1, `<10ms`=1
  - payload burst idle gap buckets: `>=15s`=1
  - payload burst direction patterns: `bidirectional`=2
  - payload burst length fingerprints: `1388x869+1440x2+6x1+45x1`=1, `1440x35+1398x9+1272x3+1356x3`=1
  - initial payload bursts: `#1:start=145.1s,end=145.2s,packets=878,bytes=1210794,pattern=bidirectional,lengths=1388x869+1440x2+6x1+45x1`, `#2:start=196.2s,end=196.2s,packets=56,bytes=74784,pattern=bidirectional,lengths=1440x35+1398x9+1272x3+1356x3`
  - phase-window payload bursts: none
  - framing first-byte classes: `ascii`=313, `ascii-whitespace`=8, `control`=138, `high`=473, `zero`=2
  - framing byte-class ratios: ascii=`0pct`=1, `10-49pct`=933; high=`0pct`=1, `10-49pct`=486, `50-89pct`=447; zero=`0pct`=10, `1-9pct`=921, `10-49pct`=3; control=`1-9pct`=49, `10-49pct`=884, `50-89pct`=1
  - framing entropy buckets: `0-2bits`=1, `4-6bits`=5, `6-7bits`=1, `7-8bits`=927
  - framing byte-diversity buckets: `129-256`=927, `17-64`=4, `2-4`=1, `65-128`=2
  - framing length-prefix candidates: `none`=934
  - framing TLS record-like reads: `no`=907, `yes`=27
  - framing TLS record length matches: `no`=920, `yes`=14
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#2:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#3:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#4:first=ascii,len_prefix=none,tls=no,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#5:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#6:first=control,len_prefix=none,tls=yes,entropy=0-2bits,diversity=2-4,ascii=0pct,high=0pct`, `#7:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=50-89pct`, `#8:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#9:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#10:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#11:first=ascii,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#12:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`
- #2: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=2172 payload_bytes=1282913 nonzero_payload_packets=1391 max_payload_bytes=1440 flags=`ack-only`=781, `ecn-cwr`=1, `push`=597 first_offset=3.01s last_offset=315.7s span=312.7s
  - payload directions: `a_to_b` packets=355 bytes=105131 top_lengths=`162`=83, `161`=67, `172`=33, `24`=32, `332`=31, `1440`=24; `b_to_a` packets=1036 bytes=1177782 top_lengths=`1388`=770, `28`=33, `188`=33, `32`=16, `237`=9, `483`=9
  - initial nonzero payload sequence: `b_to_a:28`, `a_to_b:24`, `a_to_b:332`, `b_to_a:188`, `b_to_a:188`, `a_to_b:172`, `a_to_b:320`, `b_to_a:176`, `a_to_b:160`, `a_to_b:28`, `b_to_a:32`, `b_to_a:28`, `a_to_b:24`, `a_to_b:332`, `b_to_a:188`, `a_to_b:172`, `a_to_b:1440`, `a_to_b:1440`, `a_to_b:622`, `b_to_a:237`, `b_to_a:483`, `a_to_b:161`, `a_to_b:161`, `a_to_b:161`
  - inter-payload gap buckets: `1-10ms`=108, `10-100ms`=122, `100ms-1s`=130, `<1ms`=958, `>=1s`=72
  - payload burst count: 122
  - payload burst packet buckets: `1`=27, `2`=40, `21-100`=6, `3-5`=38, `6-20`=10, `>100`=1
  - payload burst byte buckets: `1-128`=41, `129-512`=29, `2049-16384`=13, `513-2048`=33, `>16384`=6
  - payload burst duration buckets: `1-5s`=3, `10-100ms`=11, `100ms-1s`=60, `<10ms`=48
  - payload burst idle gap buckets: `1-5s`=49, `250ms-1s`=49, `5-15s`=23
  - payload burst direction patterns: `a_to_b_only`=28, `b_to_a_only`=11, `bidirectional`=83
  - payload burst length fingerprints: `172x1+188x1+332x1`=21, `24x1+28x1`=20, `24x1`=7, `28x1`=6, `28x1+32x1`=5, `161x2`=4, `188x1+332x1`=4, `172x1`=4
  - initial payload bursts: `#1:start=3.01s,end=3.18s,packets=2,bytes=52,pattern=bidirectional,lengths=24x1+28x1`, `#2:start=4.75s,end=4.93s,packets=4,bytes=880,pattern=bidirectional,lengths=188x2+172x1+332x1`, `#3:start=5.99s,end=6.00s,packets=2,bytes=496,pattern=bidirectional,lengths=176x1+320x1`, `#4:start=6.38s,end=6.38s,packets=1,bytes=160,pattern=a_to_b_only,lengths=160x1`, `#5:start=12.7s,end=12.7s,packets=2,bytes=60,pattern=bidirectional,lengths=28x1+32x1`, `#6:start=13.0s,end=13.2s,packets=2,bytes=52,pattern=bidirectional,lengths=24x1+28x1`, `#7:start=14.5s,end=14.8s,packets=3,bytes=692,pattern=bidirectional,lengths=172x1+188x1+332x1`, `#8:start=19.1s,end=19.2s,packets=5,bytes=4222,pattern=bidirectional,lengths=1440x2+237x1+483x1+622x1`, `#9:start=19.8s,end=19.8s,packets=3,bytes=483,pattern=a_to_b_only,lengths=161x3`, `#10:start=23.0s,end=23.2s,packets=2,bytes=52,pattern=bidirectional,lengths=24x1+28x1`, `#11:start=24.6s,end=24.8s,packets=3,bytes=692,pattern=bidirectional,lengths=172x1+188x1+332x1`, `#12:start=32.9s,end=33.0s,packets=3,bytes=88,pattern=bidirectional,lengths=28x2+32x1`
  - phase-window payload bursts: `phase=first_connected,phase_offset=7.33s,burst=#3,start=5.99s,end=6.00s,packets=2,bytes=496,pattern=bidirectional,lengths=176x1+320x1`, `phase=first_connected,phase_offset=7.33s,burst=#4,start=6.38s,end=6.38s,packets=1,bytes=160,pattern=a_to_b_only,lengths=160x1`, `phase=first_target_connect,phase_offset=7.34s,burst=#3,start=5.99s,end=6.00s,packets=2,bytes=496,pattern=bidirectional,lengths=176x1+320x1`, `phase=first_target_connect,phase_offset=7.34s,burst=#4,start=6.38s,end=6.38s,packets=1,bytes=160,pattern=a_to_b_only,lengths=160x1`
  - framing first-byte classes: `ascii`=294, `ascii-whitespace`=7, `control`=677, `high`=410, `zero`=3
  - framing byte-class ratios: ascii=`1-9pct`=1, `10-49pct`=1382, `50-89pct`=8; high=`10-49pct`=749, `50-89pct`=642; zero=`0pct`=45, `1-9pct`=1346; control=`0pct`=1, `1-9pct`=76, `10-49pct`=1314
  - framing entropy buckets: `2-4bits`=3, `4-6bits`=99, `6-7bits`=243, `7-8bits`=1046
  - framing byte-diversity buckets: `129-256`=1085, `17-64`=99, `5-16`=3, `65-128`=204
  - framing length-prefix candidates: `none`=1391
  - framing TLS record-like reads: `no`=811, `yes`=580
  - framing TLS record length matches: `no`=898, `yes`=493
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#2:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#4:first=control,len_prefix=none,tls=yes,entropy=6-7bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#5:first=control,len_prefix=none,tls=yes,entropy=6-7bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#6:first=control,len_prefix=none,tls=yes,entropy=6-7bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#7:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#8:first=control,len_prefix=none,tls=yes,entropy=6-7bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#9:first=control,len_prefix=none,tls=yes,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#10:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=50-89pct`, `#11:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#12:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`
- #3: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=4644 payload_bytes=1030568 nonzero_payload_packets=2752 max_payload_bytes=1440 flags=`ack-only`=1890, `ecn-cwr`=7, `push`=2134, `syn`=2 first_offset=126.6s last_offset=322.5s span=195.9s
  - payload directions: `a_to_b` packets=2360 bytes=508383 top_lengths=`50`=357, `51`=297, `49`=278, `1440`=250, `52`=192, `48`=189; `b_to_a` packets=392 bytes=522185 top_lengths=`1388`=370, `32`=9, `238`=1, `80`=1, `654`=1, `184`=1
  - initial nonzero payload sequence: `b_to_a:238`, `a_to_b:1440`, `a_to_b:1440`, `a_to_b:217`, `b_to_a:80`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:654`, `b_to_a:1388`, `a_to_b:1440`, `a_to_b:251`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`
  - inter-payload gap buckets: `1-10ms`=424, `10-100ms`=1036, `100ms-1s`=109, `<1ms`=1154, `>=1s`=28
  - payload burst count: 53
  - payload burst packet buckets: `1`=9, `2`=6, `21-100`=17, `3-5`=1, `6-20`=15, `>100`=5
  - payload burst byte buckets: `1-128`=7, `129-512`=1, `2049-16384`=18, `513-2048`=12, `>16384`=15
  - payload burst duration buckets: `1-5s`=6, `10-100ms`=10, `100ms-1s`=12, `<10ms`=24, `>=5s`=1
  - payload burst idle gap buckets: `1-5s`=19, `250ms-1s`=24, `5-15s`=7, `>=15s`=2
  - payload burst direction patterns: `a_to_b_only`=34, `b_to_a_only`=4, `bidirectional`=15
  - payload burst length fingerprints: `28x1+32x1`=6, `914x1`=2, `1388x266+1440x3+80x1+184x1`=1, `1440x17+117x1+525x1`=1, `930x1`=1, `50x11+51x7+48x4+47x3`=1, `51x9+50x6+53x4+46x3`=1, `1440x9+71x2+189x1`=1
  - initial payload bursts: `#1:start=126.8s,end=127.4s,packets=276,bytes=375443,pattern=bidirectional,lengths=1388x266+1440x3+80x1+184x1`, `#2:start=129.5s,end=129.6s,packets=19,bytes=25122,pattern=a_to_b_only,lengths=1440x17+117x1+525x1`, `#3:start=132.8s,end=132.8s,packets=1,bytes=930,pattern=a_to_b_only,lengths=930x1`, `#4:start=142.3s,end=143.6s,packets=39,bytes=5153,pattern=a_to_b_only,lengths=50x11+51x7+48x4+47x3`, `#5:start=144.1s,end=144.3s,packets=45,bytes=4649,pattern=a_to_b_only,lengths=51x9+50x6+53x4+46x3`, `#6:start=144.6s,end=144.6s,packets=12,bytes=13291,pattern=a_to_b_only,lengths=1440x9+71x2+189x1`, `#7:start=147.2s,end=147.2s,packets=2,bytes=60,pattern=bidirectional,lengths=28x1+32x1`, `#8:start=167.2s,end=167.2s,packets=2,bytes=60,pattern=bidirectional,lengths=28x1+32x1`, `#9:start=187.3s,end=187.3s,packets=2,bytes=60,pattern=bidirectional,lengths=28x1+32x1`, `#10:start=196.7s,end=196.7s,packets=26,bytes=35086,pattern=b_to_a_only,lengths=1388x25+386x1`, `#11:start=197.0s,end=197.0s,packets=19,bytes=24616,pattern=a_to_b_only,lengths=1440x16+525x2+526x1`, `#12:start=198.1s,end=198.1s,packets=1,bytes=931,pattern=a_to_b_only,lengths=931x1`
  - phase-window payload bursts: none
  - framing first-byte classes: `ascii`=250, `ascii-whitespace`=6, `control`=2191, `high`=302, `zero`=3
  - framing byte-class ratios: ascii=`10-49pct`=2699, `50-89pct`=53; high=`10-49pct`=1876, `50-89pct`=876; zero=`0pct`=18, `1-9pct`=2733, `10-49pct`=1; control=`0pct`=1, `1-9pct`=161, `10-49pct`=2590
  - framing entropy buckets: `2-4bits`=1, `4-6bits`=1948, `6-7bits`=113, `7-8bits`=690
  - framing byte-diversity buckets: `129-256`=699, `17-64`=1931, `5-16`=1, `65-128`=121
  - framing length-prefix candidates: `none`=2752
  - framing TLS record-like reads: `no`=624, `yes`=2128
  - framing TLS record length matches: `no`=679, `yes`=2073
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#2:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#3:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#4:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#5:first=control,len_prefix=none,tls=yes,entropy=6-7bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#6:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#7:first=ascii,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#8:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#9:first=ascii,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#10:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#11:first=ascii,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#12:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`
- #4: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=5164 payload_bytes=366010 nonzero_payload_packets=2962 max_payload_bytes=1440 flags=`ack-only`=2202, `ecn-cwr`=1, `push`=2817 first_offset=18.3s last_offset=322.5s span=304.3s
  - payload directions: `a_to_b` packets=2894 bytes=297631 top_lengths=`50`=482, `51`=401, `49`=395, `48`=283, `52`=242, `47`=157; `b_to_a` packets=68 bytes=68379 top_lengths=`1388`=48, `32`=16, `551`=1, `277`=1, `214`=1, `201`=1
  - initial nonzero payload sequence: `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `a_to_b:28`, `b_to_a:32`, `b_to_a:1388`
  - inter-payload gap buckets: `1-10ms`=473, `10-100ms`=1516, `100ms-1s`=123, `<1ms`=832, `>=1s`=17
  - payload burst count: 34
  - payload burst packet buckets: `1`=3, `2`=10, `21-100`=6, `3-5`=3, `6-20`=8, `>100`=4
  - payload burst byte buckets: `1-128`=12, `129-512`=1, `2049-16384`=9, `513-2048`=5, `>16384`=7
  - payload burst duration buckets: `1-5s`=2, `10-100ms`=5, `100ms-1s`=7, `<10ms`=17, `>=5s`=3
  - payload burst idle gap buckets: `1-5s`=3, `250ms-1s`=16, `5-15s`=3, `>=15s`=11
  - payload burst direction patterns: `a_to_b_only`=14, `b_to_a_only`=1, `bidirectional`=19
  - payload burst length fingerprints: `28x1+32x1`=10, `28x2+32x1`=2, `916x1`=2, `1388x10+261x1+551x1`=1, `1440x16+1088x1+1090x1`=1, `50x9+48x7+49x7+51x6`=1, `51x13+49x10+48x7+50x7`=1, `1440x9+213x1+620x1`=1
  - initial payload bursts: `#1:start=18.3s,end=18.3s,packets=3,bytes=88,pattern=bidirectional,lengths=28x2+32x1`, `#2:start=38.4s,end=38.4s,packets=2,bytes=60,pattern=bidirectional,lengths=28x1+32x1`, `#3:start=58.6s,end=58.6s,packets=2,bytes=60,pattern=bidirectional,lengths=28x1+32x1`, `#4:start=78.8s,end=78.8s,packets=2,bytes=60,pattern=bidirectional,lengths=28x1+32x1`, `#5:start=98.9s,end=98.9s,packets=2,bytes=60,pattern=bidirectional,lengths=28x1+32x1`, `#6:start=119.0s,end=119.0s,packets=2,bytes=60,pattern=bidirectional,lengths=28x1+32x1`, `#7:start=139.1s,end=139.1s,packets=2,bytes=60,pattern=bidirectional,lengths=28x1+32x1`, `#8:start=159.2s,end=159.2s,packets=2,bytes=60,pattern=bidirectional,lengths=28x1+32x1`, `#9:start=179.3s,end=179.3s,packets=2,bytes=60,pattern=bidirectional,lengths=28x1+32x1`, `#10:start=199.4s,end=199.4s,packets=2,bytes=60,pattern=bidirectional,lengths=28x1+32x1`, `#11:start=219.5s,end=219.5s,packets=2,bytes=60,pattern=bidirectional,lengths=28x1+32x1`, `#12:start=219.8s,end=220.0s,packets=12,bytes=14692,pattern=bidirectional,lengths=1388x10+261x1+551x1`
  - phase-window payload bursts: none
  - framing first-byte classes: `ascii`=42, `ascii-whitespace`=3, `control`=2835, `high`=81, `zero`=1
  - framing byte-class ratios: ascii=`10-49pct`=2906, `50-89pct`=56; high=`10-49pct`=2184, `50-89pct`=778; zero=`0pct`=10, `1-9pct`=2952; control=`1-9pct`=171, `10-49pct`=2791
  - framing entropy buckets: `4-6bits`=2714, `6-7bits`=76, `7-8bits`=172
  - framing byte-diversity buckets: `129-256`=177, `17-64`=2701, `65-128`=84
  - framing length-prefix candidates: `none`=2962
  - framing TLS record-like reads: `no`=146, `yes`=2816
  - framing TLS record length matches: `no`=166, `yes`=2796
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=50-89pct`, `#2:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#3:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=50-89pct`, `#4:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#5:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#6:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#7:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#8:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=50-89pct`, `#9:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#10:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#11:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#12:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`
- #5: ip=ipv4 endpoints=`private-v4`<->`public-v4` ports=`dynamic`<->`https` packets=380 payload_bytes=311546 nonzero_payload_packets=235 max_payload_bytes=1440 flags=`ack-only`=143, `ecn-cwr`=1, `push`=16, `syn`=2 first_offset=170.0s last_offset=320.2s span=150.1s
  - payload directions: `a_to_b` packets=10 bytes=8248 top_lengths=`1398`=3, `1440`=2, `202`=1, `51`=1, `301`=1, `311`=1; `b_to_a` packets=225 bytes=303298 top_lengths=`1388`=217, `45`=2, `174`=1, `75`=1, `6`=1, `428`=1
  - initial nonzero payload sequence: `b_to_a:174`, `a_to_b:1440`, `a_to_b:1440`, `a_to_b:202`, `b_to_a:75`, `b_to_a:6`, `b_to_a:45`, `b_to_a:45`, `a_to_b:51`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`, `b_to_a:1388`
  - inter-payload gap buckets: `1-10ms`=6, `10-100ms`=9, `100ms-1s`=1, `<1ms`=216, `>=1s`=2
  - payload burst count: 3
  - payload burst packet buckets: `21-100`=3
  - payload burst byte buckets: `>16384`=3
  - payload burst duration buckets: `10-100ms`=2, `100ms-1s`=1
  - payload burst idle gap buckets: `>=15s`=2
  - payload burst direction patterns: `bidirectional`=3
  - payload burst length fingerprints: `1388x74+45x2+1440x2+6x1`=1, `1388x68+311x1+628x1+1398x1`=1, `1388x75+309x1+701x1+1398x1`=1
  - initial payload bursts: `#1:start=170.0s,end=170.3s,packets=86,bytes=108317,pattern=bidirectional,lengths=1388x74+45x2+1440x2+6x1`, `#2:start=230.0s,end=230.1s,packets=71,bytes=96721,pattern=bidirectional,lengths=1388x68+311x1+628x1+1398x1`, `#3:start=290.0s,end=290.1s,packets=78,bytes=106508,pattern=bidirectional,lengths=1388x75+309x1+701x1+1398x1`
  - phase-window payload bursts: none
  - framing first-byte classes: `ascii`=79, `ascii-whitespace`=2, `control`=47, `high`=106, `zero`=1
  - framing byte-class ratios: ascii=`0pct`=1, `10-49pct`=234; high=`0pct`=1, `10-49pct`=119, `50-89pct`=115; zero=`0pct`=1, `1-9pct`=231, `10-49pct`=3; control=`1-9pct`=17, `10-49pct`=217, `50-89pct`=1
  - framing entropy buckets: `0-2bits`=1, `4-6bits`=5, `6-7bits`=1, `7-8bits`=228
  - framing byte-diversity buckets: `129-256`=229, `17-64`=4, `2-4`=1, `65-128`=1
  - framing length-prefix candidates: `none`=235
  - framing TLS record-like reads: `no`=219, `yes`=16
  - framing TLS record length matches: `no`=224, `yes`=11
  - initial framing samples: `#1:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=65-128,ascii=10-49pct,high=10-49pct`, `#2:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#3:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#4:first=ascii,len_prefix=none,tls=no,entropy=6-7bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#5:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#6:first=control,len_prefix=none,tls=yes,entropy=0-2bits,diversity=2-4,ascii=0pct,high=0pct`, `#7:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#8:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#9:first=control,len_prefix=none,tls=yes,entropy=4-6bits,diversity=17-64,ascii=10-49pct,high=10-49pct`, `#10:first=control,len_prefix=none,tls=yes,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`, `#11:first=ascii,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=10-49pct`, `#12:first=high,len_prefix=none,tls=no,entropy=7-8bits,diversity=129-256,ascii=10-49pct,high=50-89pct`
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
  - Phase-window payload bursts are correlation hints within +/-2s of redacted session phase offsets; they are not decoded messages.
  - The action timeline includes pointer movement, scrolling, and harmless key activity; interpret input/action counters and packet bursts as mixed input activity, not pointer-only traffic. Literal typed text is intentionally not recorded.
  - Do not paste raw hostnames, addresses, TXT values, interface identifiers, packet payloads, typed text, or unified-log lines.
