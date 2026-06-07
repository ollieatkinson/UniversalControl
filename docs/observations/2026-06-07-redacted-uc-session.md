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
- transport counts: `tcp`=29335, `udp`=9
- protocol-relevant port hits: `3722`=9, `5353`=190
- pcap decode failures: 0
- raw packet data: not included
- raw endpoints and dynamic ports: not included

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
  - The run had no `_companion-link._tcp` or `_universalcontrol._tcp` browse rows, but it did produce native UniversalControl/Rapport target, sync/layout, proximity, Wi-Fi P2P, and TCP-heavy packet-shape counters.
  - Do not paste raw hostnames, addresses, TXT values, interface identifiers, packet payloads, or unified-log lines.
