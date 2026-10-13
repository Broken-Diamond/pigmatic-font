# Pigmatic

Pigmatic is a typeface based on the Pigpen cipher.

It uses a single alphabet: there is no distinction between uppercase and lowercase letters. The glyphs are intended to retain the visual structure of the Pigpen cipher while functioning as an ordinary installable font.

## Building

The repository contains the source artwork and everything needed to reproduce the generated font files.

The build system currently supports **Debian-based Linux x86_64 systems**. Ubuntu and Debian are supported. Other Linux distributions are not currently supported because the private FontForge runtime is assembled from Debian packages.

Windows builds are not supported directly; on Windows, use a Debian or Ubuntu environment such as WSL.

macOS and other architectures are not supported yet.

### Requirements

- Python 3
- Debian or Debian-based Linux
- x86_64 architecture
- A working internet connection when the required build tools are not already available locally

The build system will reuse suitable versions of FontForge and resvg already installed on the system. If they are not available, it will download the pinned build tools into `tools/`.

The downloaded tools are disposable and are not installed system-wide.

### Linux

```sh
./build/build.sh
```

On Windows, use WSL or another Debian-based Linux environment and run the Linux build script from there.

The first build may download the required build tools. Subsequent builds reuse them.

A successful build produces output similar to:

```text
Preparing build tools... done.
Building font and glyph SVGs... done.
Rendering specimen... done.

Build complete.
```

If the required Debian packages cannot be downloaded, the build will stop and ask you to update your package lists:

```text
Preparing build tools... failed

Could not download a required package.
Your package lists may be out of date.

Run "sudo apt update", then try again.
```

The build does not automatically modify the host system's package state.

To remove generated fonts and specimen files:

```sh
./build/clean.sh
```

To remove downloaded build tools:

```sh
./build/clean-tools.sh
```

The build tools can be downloaded again automatically by the next build.

## Creating a release

Release archives can be generated with:

```sh
./build/release.sh 1.0.0
```

The version number is used in the names of the generated archives.

The script first performs a normal build, then creates two release archives under `release/`:

```text
release/
├── Pigmatic-1.0.0-font.zip
└── Pigmatic-1.0.0-source.tar.gz
```

The font archive contains the ready-to-use font files, the generated specimen, and a copy of the font license:

```text
Pigmatic-Regular.ttf
Pigmatic-Regular.otf
Pigmatic-Regular.woff2
specimen.png
LICENSE.txt
```

`LICENSE.txt` is a copy of `OFL.txt`.

The source archive is generated from the committed Git repository state. It contains the source artwork, build system, documentation, and other tracked source files, but does not include untracked local files.

The release script creates the artifacts locally. Publishing a release to GitHub is a separate step.

For example, after creating and pushing a release tag:

```sh
git tag -a v1.0.0 -m "Pigmatic 1.0.0"
git push origin v1.0.0
```

the artifacts can be uploaded with GitHub CLI:

```sh
gh release create v1.0.0 \
    release/Pigmatic-1.0.0-font.zip \
    release/Pigmatic-1.0.0-source.tar.gz \
    --title "Pigmatic 1.0.0" \
    --generate-notes
```

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
│   ├── release.sh
│   ├── toolchain.toml
│   ├── clean.sh
│   └── clean-tools.sh
├── tools/
├── generated/
│   └── svg/
├── dist/
├── release/
├── LICENSE
├── OFL.txt
└── README.md
```

`artwork/Pigmatic.sfd` is the source font artwork used by FontForge.

`specimen/specimen.svg` is the hand-authored specimen artwork. It is rendered to PNG during the build.

`generated/`, `dist/`, and `release/` contain generated build or release files and are not authoritative source files.

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

Release archives are placed under:

```text
release/
```

They are generated from the source repository and build outputs.

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

Release source archives are generated from the committed Git repository state, making the source used for a release explicit and reproducible.

## Platform support

Current support:

- Debian
- Debian-based Linux distributions such as Ubuntu
- x86_64 architecture
- Windows through Debian or Ubuntu in WSL

Not supported yet:

- Native Windows builds
- macOS
- Other Linux distributions
- Architectures other than x86_64

The build system is intentionally kept simple and reproducible while additional platforms are evaluated.

## License

The Pigmatic font is licensed under the SIL Open Font License, Version 1.1.

See [OFL.txt](OFL.txt) for the complete license.

The build scripts and other original software in this repository are licensed under the MIT License.

See [LICENSE](LICENSE) for the complete license.

Copyright © 2026 Mac Musser.
