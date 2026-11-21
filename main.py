#!/usr/bin/env python3
"""Entrypoint for the news-image-20261121 make.fun entry.

The artwork for Saturday 21 November 2026 lives in this repository as
``entry.png``. It was produced ahead of time by ``render_poster.py`` (a
Pillow script that only ever runs on the author's machine), because the
grading environment provides nothing beyond the Python standard library.
This module therefore does exactly one job: place a byte-for-byte copy of
the committed poster at ``entry.png`` inside the output directory.

The output directory is ``$MAKEFUN_OUTPUT_DIR`` when that variable is set
and ``/output`` otherwise. The copy is verified by hashing both files, so
a partial or corrupted write fails the run instead of submitting quietly.
"""

from hashlib import sha256
from os import environ, makedirs, path
from shutil import copyfile
from sys import exit as sys_exit
from sys import stderr

LIMIT_BYTES = 1_048_576  # entries may not exceed one mebibyte
PNG_SIGNATURE = bytes((0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A))


def digest_of(filename):
    """Streaming SHA-256 of a file, read in 64 KiB blocks."""
    hasher = sha256()
    with open(filename, "rb") as handle:
        block = handle.read(65_536)
        while block:
            hasher.update(block)
            block = handle.read(65_536)
    return hasher.hexdigest()


def poster_file():
    """Locate the committed poster next to this source file."""
    folder = path.dirname(path.abspath(__file__))
    return path.join(folder, "entry.png")


def destination_file():
    """Where the grader expects the finished image to appear."""
    folder = environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return path.join(folder, "entry.png")


def check_poster(filename):
    """Reject a poster that is oversized or not really a PNG."""
    with open(filename, "rb") as handle:
        head = handle.read(len(PNG_SIGNATURE))
    if head != PNG_SIGNATURE:
        raise ValueError("committed file lacks the PNG signature")
    if path.getsize(filename) > LIMIT_BYTES:
        raise ValueError("committed poster exceeds the 1 MiB limit")


def run():
    source = poster_file()
    target = destination_file()

    if not path.isfile(source):
        print(f"missing committed poster: {source}", file=stderr)
        return 1

    try:
        check_poster(source)
    except (OSError, ValueError) as problem:
        print(f"unusable committed poster: {problem}", file=stderr)
        return 1

    makedirs(path.dirname(target), exist_ok=True)
    copyfile(source, target)

    if digest_of(target) != digest_of(source):
        print("copy verification failed: hashes differ", file=stderr)
        return 1

    size = path.getsize(target)
    print(f"delivered {target}: {size} bytes, sha256 {digest_of(target)}")
    return 0


if __name__ == "__main__":
    sys_exit(run())
