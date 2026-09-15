#!/usr/bin/env python3
"""
strip_highlightcs.py

Fixes a real WPS Office compatibility bug in documents produced by the
`docx` npm package (docx-js): for any run with a text highlight, docx-js
emits BOTH the valid `<w:highlight w:val="yellow"/>` element AND an
invalid `<w:highlightCs .../>` element in the same <w:rPr>. Microsoft Word
silently ignores the invalid element; WPS Office's stricter OOXML parser
rejects it, and the highlighted run (or sometimes the whole file) fails to
open correctly in WPS.

This script removes every `<w:highlightCs .../>` element from
word/document.xml (and, for good measure, headers/footers/footnotes/
endnotes/comments if present) while leaving the valid `<w:highlight/>`
element untouched, then re-zips the file.

Usage:
    python3 strip_highlightcs.py input.docx [-o output.docx]

If -o/--output is omitted, the input file is overwritten in place.

Pure standard library (zipfile, re, shutil, tempfile) — no third-party
dependencies.
"""
import argparse
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

HIGHLIGHTCS_RE = re.compile(r"<w:highlightCs\b[^/]*/>")

# Parts that can plausibly contain runs with highlighting.
CANDIDATE_PARTS = [
    "word/document.xml",
    "word/comments.xml",
    "word/footnotes.xml",
    "word/endnotes.xml",
]
# header1.xml, header2.xml, ... footer1.xml, footer2.xml, ... are handled by pattern below.
HEADER_FOOTER_RE = re.compile(r"^word/(header|footer)\d+\.xml$")


def strip_highlightcs(input_path: Path, output_path: Path) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        with zipfile.ZipFile(input_path) as zin:
            names = zin.namelist()
            zin.extractall(tmp)

        total_removed = 0
        targets = set(CANDIDATE_PARTS) | {n for n in names if HEADER_FOOTER_RE.match(n)}
        for rel_name in targets:
            part_path = tmp / rel_name
            if not part_path.exists():
                continue
            xml = part_path.read_text(encoding="utf-8")
            new_xml, n = HIGHLIGHTCS_RE.subn("", xml)
            if n:
                part_path.write_text(new_xml, encoding="utf-8")
                total_removed += n

        # Re-zip preserving the original member order (matters for some
        # strict OOXML consumers, and keeps diffs minimal).
        if output_path.exists():
            output_path.unlink()
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for name in names:
                zout.write(tmp / name, arcname=name)

        return total_removed


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path, help="Input .docx file")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Output .docx path (default: overwrite input)")
    args = ap.parse_args()

    output_path = args.output or args.input
    if args.output is None:
        # Overwrite-in-place: write to a temp file first, then replace.
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tf:
            tmp_out = Path(tf.name)
        removed = strip_highlightcs(args.input, tmp_out)
        shutil.move(str(tmp_out), str(args.input))
    else:
        removed = strip_highlightcs(args.input, output_path)

    print(f"Removed {removed} <w:highlightCs/> element(s). Output: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
