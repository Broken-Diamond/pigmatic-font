# Pigmatic

Pigmatic is a typeface based on the Pigpen cipher.

It uses a single alphabet: there is no distinction between uppercase and lowercase letters. The glyphs are intended to retain the visual structure of the Pigpen cipher while functioning as an ordinary installable font.

## Building

The repository contains the source artwork and everything needed to reproduce the generated font files.

The build system currently supports **Linux x86_64**. Windows builds are not supported directly; on Windows, use a Linux environment such as WSL.

macOS and other architectures are not supported yet.

### Requirements

- Python 3
- A Linux x86_64 environment
- A working internet connection when the required build tools are not already available locally

The build system will reuse suitable versions of FontForge and resvg already installed on the system. If they are not available, it will download the pinned build tools into `tools/`.

The downloaded tools are disposable and are not installed system-wide.

### Linux

```sh
./build/build.sh
```

On Windows, use WSL or another Linux environment and run the Linux build script from there.

The first build may download the required build tools. Subsequent builds reuse them.

A successful build produces output similar to:

```text
Building font and glyph SVGs...
FontForge build complete.
Rendering specimen.png...
resvg completed specimen.png.
Build complete.
```

To remove generated fonts and specimen files:

```sh
./build/clean.sh
```

To remove downloaded build tools:

```sh
./build/clean-tools.sh
```

The build tools can be downloaded again automatically by the next build.

## Repository layout

```text
Pigmatic/
├── artwork/
│   └── Pigmatic.sfd
├── specimen/
│   └── specimen.svg
├── build/
│   ├── build.py
│   ├── build.sh
│   ├── fontforge_build.py
│   ├── toolchain.toml
│   ├── clean.sh
│   └── clean-tools.sh
├── tools/
├── generated/
│   └── svg/
├── dist/
├── LICENSE
├── OFL.txt
└── README.md
```

`artwork/Pigmatic.sfd` is the source font artwork used by FontForge.

`specimen/specimen.svg` is the hand-authored specimen artwork. It is rendered to PNG during the build.

`generated/` and `dist/` contain build outputs and are not authoritative source files.

`tools/` contains locally bootstrapped build tools and may be deleted and recreated at any time.

## Generated files

A successful build produces:

```text
dist/
├── Pigmatic-Regular.ttf
├── Pigmatic-Regular.otf
├── Pigmatic-Regular.woff2
└── specimen.png
```

Individual glyphs are also exported as SVG files under:

```text
generated/svg/
```

These files are generated from the source font and should not be edited directly.

## Build tools

The build currently uses:

- **FontForge 20251009** to generate the font files and individual glyph SVGs.
- **resvg v0.48.1** to render the SVG specimen to PNG.

The build system downloads these versions automatically when suitable local installations are not available.

FontForge is distributed as an AppImage. The build extracts it locally rather than requiring AppImage/FUSE support from the host system.

FontForge also requires a small private runtime containing the Linux libraries it needs. These libraries are downloaded as Debian packages and extracted into `tools/fontforge/runtime/`; they are not installed system-wide.

The build does not require the host system to have FontForge or resvg installed.

## Source and reproducibility

The original design is maintained in the source artwork rather than in generated font files.

The build system pins its external build tools so that the same repository can be rebuilt without depending on whatever versions happen to be installed on a particular machine.

The build system also prefers existing suitable installations before downloading its own copies. This makes ordinary development convenient while keeping a clean, disposable build environment available when needed.

The build toolchain is self-contained within the repository's `tools/` directory. Removing `tools/` does not remove or modify system-wide software; the required tools will simply be bootstrapped again on the next build.

## Platform support

Current support:

- Linux x86_64
- Windows through WSL or another Linux environment

Not supported yet:

- Native Windows builds
- macOS
- Architectures other than x86_64

The build system is intentionally kept simple and reproducible while additional platforms are evaluated.

## License

The Pigmatic font is licensed under the SIL Open Font License, Version 1.1.

See [OFL.txt](OFL.txt) for the complete license.

The build scripts and other original software in this repository are licensed under the MIT License.

See [LICENSE](LICENSE) for the complete license.

Copyright © 2026 Mac.
