# AnyKBFlow

Prototype software KVM for sharing a Keychron keyboard and mouse between macOS and Windows without relying on Logitech Flow or Bluetooth profile switching.

Current status: early daemon prototype. It has a TCP JSON-lines peer protocol, edge-crossing router, and a macOS/Windows native input backend based on `rdev` grab/simulate. Linux builds use a no-op backend so the shared code can be checked in this workspace.

See [docs/prototype.md](docs/prototype.md) for setup and current limitations.

