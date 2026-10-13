#!/usr/bin/env python3

from pathlib import Path
import sys

import fontforge


if len(sys.argv) != 3:
    print(
        f"Usage: {Path(sys.argv[0]).name} FONT_FILE OUTPUT_DIRECTORY",
        file=sys.stderr,
    )
    raise SystemExit(2)


FONT_PATH = Path(sys.argv[1])
OUT_DIR = Path(sys.argv[2])
DIST = OUT_DIR.parent.parent / "dist"

font = fontforge.open(str(FONT_PATH))
OUT_DIR.mkdir(parents=True, exist_ok=True)
DIST.mkdir(parents=True, exist_ok=True)


# Export each glyph that produces visible output as an individual SVG.
for glyph in font.glyphs():
    if glyph.glyphname == ".notdef":
        continue

    if not glyph.isWorthOutputting():
        continue

    glyph.export(
        str(OUT_DIR / f"{glyph.glyphname}.svg"),
        format="svg",
    )


# Generate the installable font formats.
for extension in ("ttf", "otf", "woff2"):
    font.generate(
        str(DIST / f"Pigmatic-Regular.{extension}")
    )
