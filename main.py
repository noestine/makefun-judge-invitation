"""Entry program: validate letter.png against the competition gate and
write it to /output/entry.png.

Gate (RULES.txt): /output/entry.png must be a whole PNG or JPEG, at most
1 MiB (1,048,576 bytes) and at most 1024 by 1024 pixels.

Standard library only, deterministic, offline. The invitation image is
rendered in-session by render_letter.py and shipped as letter.png next
to this file; this program only validates it and copies it byte-for-byte.

Usage:
    python3 main.py [--input letter.png] [--output /output/entry.png]

Defaults are the graded paths. Any failure exits non-zero with a clean
one-line error on stderr and no traceback.
"""
import argparse
import os
import shutil
import struct
import sys

MAX_BYTES = 1_048_576
MAX_DIMENSION = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class EntryError(Exception):
    """A gate failure: reported cleanly, never as a traceback."""


def read_png_dimensions(path):
    """Return (width, height) of a PNG, or raise EntryError."""
    try:
        with open(path, "rb") as f:
            head = f.read(33)
    except OSError as exc:
        raise EntryError("cannot read %s: %s" % (path, exc.strerror or exc))
    if len(head) < 33:
        raise EntryError("%s is truncated (%d bytes)" % (path, len(head)))
    if head[:8] != PNG_MAGIC:
        raise EntryError("%s is not a PNG file" % path)
    if head[12:16] != b"IHDR":
        raise EntryError("%s has no IHDR chunk" % path)
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def validate(path):
    """Check the gate. Returns (width, height); raises EntryError."""
    try:
        size = os.path.getsize(path)
    except OSError as exc:
        raise EntryError("cannot read %s: %s" % (path, exc.strerror or exc))
    if size > MAX_BYTES:
        raise EntryError(
            "%s is %d bytes, over the 1 MiB gate (%d)" % (path, size, MAX_BYTES))
    width, height = read_png_dimensions(path)
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise EntryError(
            "%s is %dx%d, over the 1024x1024 gate" % (path, width, height))
    if width == 0 or height == 0:
        raise EntryError("%s has a zero dimension" % path)
    return width, height


def run(input_path, output_path):
    width, height = validate(input_path)
    out_dir = os.path.dirname(output_path)
    if out_dir:
        try:
            os.makedirs(out_dir, exist_ok=True)
        except OSError as exc:
            raise EntryError("cannot create %s: %s" % (out_dir, exc.strerror or exc))
        if not os.path.isdir(out_dir):
            raise EntryError("%s is not a directory" % out_dir)
    try:
        shutil.copyfile(input_path, output_path)
    except OSError as exc:
        raise EntryError("cannot write %s: %s" % (output_path, exc.strerror or exc))
    # Verify the written bytes match the source exactly.
    with open(input_path, "rb") as f:
        source = f.read()
    with open(output_path, "rb") as f:
        written = f.read()
    if written != source:
        raise EntryError("%s does not match %s after copy" % (output_path, input_path))
    print("wrote %s (%dx%d, %d bytes)" % (output_path, width, height, len(source)))


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=os.path.join(here, "letter.png"),
                        help="source PNG (default: letter.png next to main.py)")
    parser.add_argument("--output", default="/output/entry.png",
                        help="destination path (default: /output/entry.png)")
    args = parser.parse_args(argv)
    try:
        run(args.input, args.output)
    except EntryError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
