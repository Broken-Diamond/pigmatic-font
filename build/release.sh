#!/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 VERSION"
    echo "Example: $0 1.0.0"
    exit 1
fi

VERSION="$1"

DIST="$ROOT/dist"
RELEASE="$ROOT/release"
TEMP="$RELEASE/.tmp"

FONT_ARCHIVE="$RELEASE/Pigmatic-$VERSION-font.zip"
SOURCE_ARCHIVE="$RELEASE/Pigmatic-$VERSION-source.tar.gz"

echo "Building release $VERSION..."

"$ROOT/build/build.sh"

echo
echo "Preparing release files..."

rm -rf "$TEMP"
mkdir -p "$TEMP/font"

for file in \
    Pigmatic-Regular.ttf \
    Pigmatic-Regular.otf \
    Pigmatic-Regular.woff2 \
    specimen.png
do
    if [ ! -f "$DIST/$file" ]; then
        echo "Missing release file: dist/$file"
        exit 1
    fi

    cp "$DIST/$file" "$TEMP/font/$file"
done

if [ ! -f "$ROOT/OFL.txt" ]; then
    echo "Missing license file: OFL.txt"
    exit 1
fi

cp "$ROOT/OFL.txt" "$TEMP/font/LICENSE.txt"

rm -f "$FONT_ARCHIVE" "$SOURCE_ARCHIVE"

echo "Creating font archive..."
(
    cd "$TEMP/font"
    zip -q -r "$FONT_ARCHIVE" .
)

echo "Creating source archive..."
git -C "$ROOT" archive \
    --format=tar.gz \
    --prefix="pigmatic-font-$VERSION/" \
    -o "$SOURCE_ARCHIVE" \
    HEAD

rm -rf "$TEMP"

echo
echo "Release artifacts:"
echo "  $FONT_ARCHIVE"
echo "  $SOURCE_ARCHIVE"
