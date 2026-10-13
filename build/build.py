#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tarfile
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

BUILD = ROOT / "build"
TOOLS = ROOT / "tools"
GENERATED = ROOT / "generated"
GLYPHS = GENERATED / "svg"
DIST = ROOT / "dist"

SFD = ROOT / "artwork" / "Pigmatic.sfd"
SPECIMEN = ROOT / "specimen" / "specimen.svg"

FONTFORGE_DIR = TOOLS / "fontforge"
FONTFORGE_EXTRACTED = FONTFORGE_DIR / "squashfs-root"
FONTFORGE_RUNTIME = FONTFORGE_DIR / "runtime"
FONTFORGE_SCRIPT = BUILD / "fontforge_build.py"

FONTFORGE_RUNTIME_PACKAGES = [
    "libfreetype6",
    "libharfbuzz0b",
    "libfribidi0",
    "libfontconfig1",
    "libwayland-client0",
    "libgpg-error0",
    "fontconfig-config",
    "libbrotli1",
    "libgraphite2-3",
    "libx11-6",
    "libxcb1",
    "libxau6",
    "libxdmcp6",
]

# Useful when debugging bootstrap failures. Normally temporary files are removed.
KEEP_TEMP = os.environ.get("PIGMATIC_KEEP_TEMP") == "1"

FONTFORGE_VERSION = "20251009"
RESVG_VERSION = "v0.48.1"


def die(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(
    command: list[str],
    *,
    show_command: bool = True,
    quiet: bool = False,
    **kwargs,
) -> None:
    if show_command:
        print("$", " ".join(command))

    if quiet:
        kwargs.setdefault("stdout", subprocess.DEVNULL)
        kwargs.setdefault("stderr", subprocess.DEVNULL)

    subprocess.run(command, check=True, **kwargs)


def sha256(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)

    return h.hexdigest()


def find_fontforge() -> Path | None:
    local = FONTFORGE_EXTRACTED / "usr" / "bin" / "fontforge"
    if local.exists():
        return local

    found = shutil.which("fontforge")
    if found:
        return Path(found)

    return None


def find_resvg() -> Path | None:
    local = TOOLS / "resvg" / "resvg"

    if local.exists():
        return local

    found = shutil.which("resvg")
    if found:
        return Path(found)

    return None


def github_release(repo: str, tag: str) -> dict:
    url = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Pigmatic-build",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)

    except urllib.error.HTTPError as exc:
        die(
            f"Could not query GitHub for {repo} {tag} "
            f"(HTTP {exc.code}). Check your network connection and release tag."
        )

    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        die(
            "Could not reach GitHub while bootstrapping a build tool.\n"
            "The build requires network access only when a required tool is "
            "not already installed locally.\n"
            f"Network error: {exc}"
        )


def download_asset(
    repo: str,
    tag: str,
    predicate,
    destination: Path,
) -> Path:
    release = github_release(repo, tag)
    assets = release.get("assets", [])

    matches = [asset for asset in assets if predicate(asset["name"])]

    if len(matches) != 1:
        names = "\n  ".join(asset["name"] for asset in assets)

        die(
            "Could not uniquely select a release asset.\n"
            f"Available assets:\n  {names}"
        )

    asset = matches[0]
    url = asset["browser_download_url"]
    expected = asset.get("digest", "")

    if expected.startswith("sha256:"):
        expected = expected.split(":", 1)[1]

    destination.parent.mkdir(parents=True, exist_ok=True)

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Pigmatic-build"},
    )

    try:
        with (
            urllib.request.urlopen(request, timeout=120) as response,
            destination.open("wb") as output,
        ):
            shutil.copyfileobj(response, output)

    except urllib.error.HTTPError as exc:
        destination.unlink(missing_ok=True)
        die(f"Download failed for {asset['name']} (HTTP {exc.code}).")

    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        destination.unlink(missing_ok=True)

        die(
            f"Could not download {asset['name']}.\n"
            f"Network error: {exc}"
        )

    if expected:
        actual = sha256(destination)

        if actual.lower() != expected.lower():
            destination.unlink(missing_ok=True)
            die(f"SHA-256 mismatch for {asset['name']}.")

    return destination


def extract_archive(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)

    if not tarfile.is_tarfile(archive):
        die(f"Do not know how to extract {archive.name}.")

    with tarfile.open(archive) as tar:
        tar.extractall(destination)


def bootstrap_fontforge() -> None:
    FONTFORGE_DIR.mkdir(parents=True, exist_ok=True)

    appimage = FONTFORGE_DIR / "FontForge.AppImage"

    download_asset(
        "fontforge/fontforge",
        FONTFORGE_VERSION,
        lambda name: name.lower().endswith(".appimage"),
        appimage,
    )

    appimage.chmod(
        appimage.stat().st_mode
        | stat.S_IXUSR
        | stat.S_IXGRP
        | stat.S_IXOTH
    )

    fontforge = FONTFORGE_EXTRACTED / "usr" / "bin" / "fontforge"

    if not fontforge.exists():

        run(
            [str(appimage), "--appimage-extract"],
            cwd=FONTFORGE_DIR,
        )

    if not fontforge.exists():
        die(
            "FontForge AppImage extraction failed: "
            f"{fontforge} was not created."
        )


def bootstrap_fontforge_runtime() -> None:
    FONTFORGE_RUNTIME.mkdir(parents=True, exist_ok=True)

    runtime_debs = FONTFORGE_RUNTIME / "packages"
    runtime_debs.mkdir(parents=True, exist_ok=True)

    for package in FONTFORGE_RUNTIME_PACKAGES:
        run(
            ["apt-get", "download", package],
            cwd=runtime_debs,
            show_command=False,
            quiet=True,
        )

    for deb in runtime_debs.glob("*.deb"):
        run(
            [
                "dpkg-deb",
                "-x",
                str(deb),
                str(FONTFORGE_RUNTIME),
            ],
            show_command=False,
        )


def filter_fontforge_output(text: str) -> list[str]:
    filtered = []
    skip_warning = False

    for line in text.splitlines():
        if line.startswith(
            "sys:1: UserWarning: pkg_resources is deprecated"
        ):
            skip_warning = True
            continue

        if skip_warning:
            if line.startswith("pkg_resources"):
                continue

            skip_warning = False

        if line.startswith("Compressed "):
            continue

        if line in {
            "PythonUI_Init()",
            "copyUIMethodsToBaseTable()",
            "Program root: /usr",
        }:
            continue

        filtered.append(line)

    return filtered


def run_fontforge(
    fontforge: Path,
    args: list[str],
) -> None:
    env = os.environ.copy()

    private_fontforge = FONTFORGE_EXTRACTED / "usr" / "bin" / "fontforge"

    if fontforge == FONTFORGE_EXTRACTED / "usr" / "bin" / "fontforge":
        env["LD_LIBRARY_PATH"] = str(
            FONTFORGE_RUNTIME / "usr" / "lib" / "x86_64-linux-gnu"
        )
        env["PYTHONHOME"] = str(FONTFORGE_EXTRACTED)
        env["PYTHONPATH"] = ":".join(
            [
                str(FONTFORGE_EXTRACTED / "usr" / "lib" / "python3.10"),
                str(FONTFORGE_EXTRACTED / "usr" / "local" / "lib" / "python3.10"),
                str(
                    FONTFORGE_EXTRACTED
                    / "usr"
                    / "lib"
                    / "python3.10"
                    / "dist-packages"
                ),
            ]
        )
    print("Building font and glyph SVGs...", end="", flush=True)

    command = [str(fontforge), "-quiet", *args]

    result = subprocess.run(
        command,
        check=False,
        env=env,
        text=True,
        capture_output=True,
    )

    for line in filter_fontforge_output(result.stdout):
        print(line)

    for line in filter_fontforge_output(result.stderr):
        print(line, file=sys.stderr)

    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            command,
            output=result.stdout,
            stderr=result.stderr,
        )

    print(" done.")


def bootstrap_resvg() -> None:
    target = TOOLS / "resvg"
    tools_existed = TOOLS.exists()

    TOOLS.mkdir(parents=True, exist_ok=True)

    # Download into a temporary location so a failed bootstrap does not
    # leave a partially installed resvg directory.
    temp_dir = TOOLS / ".bootstrap-tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    archive = temp_dir / "resvg-download"

    try:
        download_asset(
            "linebender/resvg",
            RESVG_VERSION,
            lambda name: name.lower() == "resvg-linux-x86_64.tar.gz",
            archive,
        )

        target.mkdir(parents=True, exist_ok=True)
        extract_archive(archive, target)

    finally:
        if not KEEP_TEMP:
            archive.unlink(missing_ok=True)

            if temp_dir.exists() and not any(temp_dir.iterdir()):
                temp_dir.rmdir()

            if not tools_existed and TOOLS.exists() and not any(TOOLS.iterdir()):
                TOOLS.rmdir()


def run_resvg(resvg: Path) -> None:
    output = DIST / "specimen.png"

    print("Rendering specimen...", end="", flush=True)

    run(
        [
            str(resvg),
            str(SPECIMEN),
            str(output),
        ],
        show_command=False,
    )

    print(" done.")


def ensure_tools() -> tuple[Path, Path]:
    prep = False
    ff = find_fontforge()
    resvg = find_resvg()

    need_fontforge = ff is None
    need_resvg = resvg is None

    private_fontforge = (
        FONTFORGE_EXTRACTED / "usr" / "bin" / "fontforge"
    )

    need_runtime = (
        ff is not None
        and ff.resolve() == private_fontforge.resolve()
        and not (
            FONTFORGE_RUNTIME
            / "usr"
            / "lib"
            / "x86_64-linux-gnu"
        ).exists()
    )

    if need_fontforge or need_runtime or need_resvg:
        prep = True
        print("Preparing build tools...", end="", flush=True)

    if need_fontforge:
        bootstrap_fontforge()
        ff = find_fontforge()
        if ff is None:
            die("FontForge bootstrap failed.")

        need_runtime = True

    if need_runtime:
        bootstrap_fontforge_runtime()

    if need_resvg:
        bootstrap_resvg()
        resvg = find_resvg()
        if resvg is None:
            die("resvg bootstrap failed.")

    if prep:
        print(" done.")

    return ff, resvg


def main() -> None:
    if not SFD.exists():
        die(f"Missing source font: {SFD}")

    if not SPECIMEN.exists():
        die(f"Missing specimen: {SPECIMEN}")

    ff, rv = ensure_tools()

    GLYPHS.mkdir(parents=True, exist_ok=True)
    DIST.mkdir(parents=True, exist_ok=True)

    run_fontforge(
        ff,
        [
            "-script",
            str(FONTFORGE_SCRIPT),
            str(SFD),
            str(GLYPHS),
        ],
    )

    run_resvg(rv)

    print("\nBuild complete.")


if __name__ == "__main__":
    main()
