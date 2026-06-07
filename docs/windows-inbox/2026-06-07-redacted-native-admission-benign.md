# Redacted Windows Native Admission Output Summary

## Source

- Transcript file: `artifacts/windows-native-admission-benign-20260607T101543Z.txt`
- Raw output: not included

## Command Result

- Cargo finished lines: 1
- AnyUniversalControl command executed: yes
- Error lines: 0
- Observer bind errors: 0

## Advertisement

- Advertised service: `_anyuniversalcontrol-probe._tcp.local.`
- Advertised port: 49152
- Advertised host length: 16
- Advertise duration: 15s

## TCP Observer

- Observer enabled: no
- Observer bind address class: none
- Observer port: unknown
- Observer duration: unknown
- Framing probe enabled: no
- Accepted connection summary: missing
- Accepted connection lines: 0
- Unique redacted peer count: 0
- Redacted peer classes: none
- Connection outcomes: none
- First-read byte counts: none
- First-read hex lengths: none
- Per-connection read counts: none
- Per-connection total byte counts: none
- Per-connection duration ms: none
- Read limit reached: no
- Closed by peer after data: no
- Additional-read hex lengths: none
- Read byte counts: none
- Read byte sequences: none
- Inter-read gap buckets: none
- Read burst count: 0
- Read burst read-count buckets: none
- Read burst byte buckets: none
- Read burst duration buckets: none
- Read burst idle gap buckets: none
- Read burst length fingerprints: none
- Initial read bursts: none
- Framing first-byte classes: none
- Framing entropy buckets: none
- Framing byte-diversity buckets: none
- Framing length-prefix candidates: none
- Framing TLS record-like reads: none
- Framing TLS record length matches: none
- Framing shape samples: none
- Apple AWDL small-flow length hits: 0
- Apple AWDL large-flow length hits: 0

## Interpretation

- macOS attempted advertised TCP port: no
- Apple AWDL length fingerprint overlap: no Apple-session length-family overlap observed
- Notes:
  - Inspect the raw transcript locally before deleting it.
  - New observer output records read lengths and timing only, not payload bytes.
  - Framing probe output, when enabled, records byte-class, entropy, diversity, length-prefix, and TLS hypotheses only.
  - Older transcripts may include local-only hex prefixes; this summary preserves only their hex-string lengths.
  - Compare read byte sequences and gap buckets with the Apple-to-Apple AWDL payload-length fingerprints before treating a TCP attempt as native Universal Control data-path progress.
  - Do not commit raw peer addresses, hostnames, or TCP payload bytes.
