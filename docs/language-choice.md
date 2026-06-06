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

## Why Not Swift For Everything

Swift is excellent for macOS-native code, but it is not the pragmatic choice for the full cross-platform app.

Risks:

- Windows Swift support exists but is not as mature as Rust for this kind of system daemon.
- Packaging and runtime expectations are less straightforward on Windows.
- Windows input hook and injection APIs are better served through Rust/C/C++/.NET than Swift.
- We would likely still need a separate Windows-native implementation, which weakens the value of using Swift as the core.

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

Do not rewrite the whole project in Swift unless the goal changes to macOS-only. If the Mac spike reports that `rdev` is not clean enough, replace only `src/platform/native.rs` on macOS with a Swift or direct CoreGraphics backend.

