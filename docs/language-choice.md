# Language Choice

Date: 2026-06-06

## Recommendation

Use Rust for the shared daemon, protocol, routing, networking, Windows backend, packaging glue, and long-term cross-platform core.

Use Swift only if the macOS input backend needs to become a first-class native helper after the spike proves the required Quartz/EventTap behavior.

## Why Rust For The Core

Rust is the better default for this project because the final product must run on both macOS and Windows.

Strengths:

- Strong Windows support.
- Strong macOS support.
- Mature async/networking ecosystem.
- Easy single-binary daemon shape.
- Good fit for a small low-latency input router.
- Easier to share one protocol/router implementation across platforms.
- Easier to later add a Windows service, tray app, updater, or installer.

This keeps the Universal Control-like behavior in one codebase instead of maintaining separate Swift and Windows implementations that can drift.

Current platform support evidence:

- Rust treats `aarch64-apple-darwin`, `x86_64-pc-windows-msvc`, and `aarch64-pc-windows-msvc` as Tier 1 targets with host tools.
- Tier 1 with host tools means the target can be used as a native development platform, with `rustc` and `cargo` running on that target and with automated testing for the tools.
- This matches our current build matrix: local Linux development plus macOS and Windows target checks.

## Why Not Swift For Everything

Swift is excellent for macOS-native code, and Swift on Windows is real. Swift.org documents Windows as a supported development and deployment platform, with SwiftPM and SourceKit-LSP support, WinGet installation, official Windows toolchains, and a Windows workgroup focused on improving Windows API bridging and packaging.

That makes Swift viable for cross-platform command-line tools. It does not make Swift the best fit for this project as a whole.

Current Swift evidence:

- Swift.org lists Windows installation through the official toolchain and `winget install --id Swift.Toolchain -e`.
- The Swift Windows Workgroup announcement says Windows has been officially supported since 2020 and is focused on improving the official Windows distribution.
- Swift 6.3 Windows toolchains are published on Swift.org as of the 2026 install page.

Risks:

- Windows Swift support exists, but the Windows low-level input surface is still more naturally served through Rust/C/C++/.NET.
- Windows input capture and injection will need Win32 APIs such as low-level hooks, Raw Input, and `SendInput`; Rust has a mature path for direct FFI to those APIs and for packaging a small daemon.
- Swift would be strongest on the Mac side, but weaker on the Windows service/tray/input-driver-adjacent side.
- A Swift-first implementation would likely still accumulate Windows-specific glue or a separate Windows-native layer, which weakens the value of using Swift as the shared core.
- The Universal Control native-compatibility investigation is mostly protocol, discovery, crypto/session, topology, and HID routing work. Those pieces do not benefit enough from Swift to justify a rewrite.

## Where Swift Could Be Better

Swift may be the right language for the macOS platform module if `rdev` is too leaky or unreliable.

Good Swift candidate responsibilities:

- `CGEventTapCreate` capture.
- Returning `nil` from the event tap to suppress local delivery.
- `CGEventPost` injection.
- Accessibility/Input Monitoring permission diagnostics.
- Native modifier/scancode mapping.

That Swift helper could communicate with the Rust daemon over stdio, a Unix domain socket, or a small C ABI. The Rust daemon would still own routing, peer state, networking, and config.

## Current Decision

Keep the prototype in Rust.

Do not rewrite the whole project in Swift unless the goal changes to macOS-only.

The strongest architecture is:

- Rust daemon: protocol, discovery, routing, config, pairing, encryption, Windows backend, shared tests.
- macOS native backend: start in Rust for the spike; replace with Swift or direct CoreGraphics/IOKit bindings only if the Mac evidence shows `rdev` cannot provide clean capture, suppression, injection, or permission diagnostics.
- Windows native backend: keep Rust and call Win32 APIs directly.

## Sources

- Swift platform support: https://www.swift.org/platform-support/
- Swift Windows install/toolchain: https://www.swift.org/install/windows/
- Swift Windows workgroup: https://www.swift.org/blog/announcing-windows-workgroup/
- Rust platform support: https://doc.rust-lang.org/stable/rustc/platform-support.html
