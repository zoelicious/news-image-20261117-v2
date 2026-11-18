#!/usr/bin/env python3
"""news-image-20261117-v2 entrypoint (stdlib-only).

The rendered front page is committed as entry.png (1024x1024 RGB,
rendered earlier offline). The grading server runs Python 3.13
stdlib-only, so this entrypoint does NOT draw anything and does NOT
import any third-party imaging library: it simply copies the
committed entry.png to the grader's output directory.

Resolves the output directory exactly like the previous version:
MAKEFUN_OUTPUT_DIR, default /output.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    src = Path(__file__).resolve().parent / "entry.png"
    if not src.is_file():
        print(f"error: entry.png not found next to main.py: {src}", file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = Path(out_dir) / "entry.png"
    shutil.copyfile(src, dst)
    print(f"wrote {dst} ({dst.stat().st_size} bytes)")
    print(f"sha256: {sha256_file(dst)}")
    print(f"source sha256: {sha256_file(src)} (match: {sha256_file(src) == sha256_file(dst)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
