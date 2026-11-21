#!/usr/bin/env python3
"""news-image-20261121 — entrypoint (standard library only).

The poster for Saturday 21 November 2026 was drawn once by render_poster.py
(a Pillow program) and committed to this repository as entry.png. The
make.fun runner installs nothing before it runs, so this entrypoint must
not depend on Pillow: it simply copies the committed poster bytes to the
output directory, verbatim and deterministically.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
"""

import hashlib
import os
import shutil
import sys

MAX_BYTES = 1024 * 1024  # competition cap: at most 1 MiB
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_poster(path: str) -> None:
    """Fail loudly unless the committed poster is a PNG within the cap."""
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        raise ValueError(f"poster is {size} bytes, over the 1 MiB cap")
    with open(path, "rb") as fh:
        magic = fh.read(len(PNG_MAGIC))
    if magic != PNG_MAGIC:
        raise ValueError("poster does not start with the PNG magic bytes")


def source_path() -> str:
    """Absolute path of the committed poster beside this file."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "entry.png")


def output_path() -> str:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return os.path.join(out_dir, "entry.png")


def main() -> int:
    src = source_path()
    dst = output_path()

    if not os.path.isfile(src):
        print(f"error: committed poster not found: {src}", file=sys.stderr)
        return 1

    try:
        validate_poster(src)
    except ValueError as exc:
        print(f"error: invalid committed poster: {exc}", file=sys.stderr)
        return 1

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)

    # Read-back check: the written bytes must be identical to the source,
    # so a truncated or corrupted copy can never pass silently.
    src_sha = sha256_of(src)
    dst_sha = sha256_of(dst)
    if dst_sha != src_sha:
        print(
            f"error: output sha256 {dst_sha} != source sha256 {src_sha}",
            file=sys.stderr,
        )
        return 1

    print(f"wrote {dst} ({os.path.getsize(dst)} bytes, sha256 {dst_sha})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
