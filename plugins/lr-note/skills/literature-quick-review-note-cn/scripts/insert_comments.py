#!/usr/bin/env python3
"""
insert_comments.py

Adds real Word margin comments (the kind that show up in Word's/WPS's
Review pane, anchored to a specific span of text) to a .docx file — fully
self-contained: if the file has no comments part yet, this script creates
one (registers the content-type override and the document relationship);
if it already has one (e.g. because it was built with docx-js, which
scaffolds an empty comments.xml automatically), it appends to it.

Each comment is anchored by a short, literal substring of the visible text
that must fall entirely within a single run in word/document.xml (i.e. it
must not straddle a bold/plain formatting boundary, since a run break
happens exactly at those boundaries). The script verifies the substring is
unique in the document before using it, and fails loudly (rather than
silently anchoring to the wrong spot) if it is not found or not unique.

The comment range covers exactly the anchor text, not the whole run around
it: the run is split into before / anchor / after runs that keep the same
formatting, so a short anchor such as "ICC2 = .64" highlights just that
phrase in Word. A run with an unusual structure (more than one text element,
tabs, breaks) is left whole and the entire run is anchored instead.

Usage:
    python3 insert_comments.py input.docx comments.json [-o output.docx] [--author NAME]

comments.json is a JSON array of objects:
    [
      {"id": 0, "anchor": "exact substring to find", "text": "comment body"},
      {"id": 1, "anchor": "...", "text": "...", "author": "override author", "initials": "X"}
    ]

`id` must be a non-negative integer, unique within the file (across any
pre-existing comments too). `anchor` and `text` are required per entry.

Comment bodies are PLAIN TEXT. Any `**bold**`, `*italic*` or `==highlight==`
markers in `text` are stripped (words kept) with a note on stderr/stdout —
those markers only work in the document body, via docx_helpers.js.
`author`/`initials`/`date` are optional per entry and fall back to the
--author/--initials CLI flags (default author: "精读笔记"), and to the
current UTC time for date.

Pure standard library (zipfile, re, json, argparse, datetime,
xml.sax.saxutils) — no third-party dependencies.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

RUN_OPEN_RE = re.compile(r"<w:r(?:\s[^>]*)?>")
RUN_CLOSE = "</w:r>"

COMMENTS_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"
COMMENTS_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"

EMPTY_COMMENTS_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"></w:comments>'
)


def find_run_span(xml: str, needle: str) -> tuple[int, int]:
    """Return (start, end) of the <w:r>...</w:r> run containing `needle`,
    raising if `needle` is missing, not unique, or not confined to one run."""
    idx = xml.find(needle)
    if idx == -1:
        raise RuntimeError(f"anchor text not found: {needle!r}")
    if xml.find(needle, idx + 1) != -1:
        raise RuntimeError(f"anchor text is not unique in the document: {needle!r}")

    opens = list(RUN_OPEN_RE.finditer(xml, 0, idx))
    if not opens:
        raise RuntimeError(f"could not find an enclosing <w:r> run before anchor: {needle!r}")
    run_start = opens[-1].start()

    run_end = xml.find(RUN_CLOSE, idx)
    if run_end == -1:
        raise RuntimeError(f"could not find a closing </w:r> after anchor: {needle!r}")
    run_end += len(RUN_CLOSE)

    # Sanity check: the run's own text content must actually contain the
    # anchor in full (guards against the anchor accidentally spanning past
    # a nested element boundary in unusual documents).
    run_xml = xml[run_start:run_end]
    if needle not in run_xml:
        raise RuntimeError(
            f"anchor {needle!r} does not fall entirely within a single run — "
            "it likely straddles a formatting boundary (e.g. half in a bold "
            "span, half in plain text). Pick a substring fully inside one "
            "formatted span instead."
        )
    return run_start, run_end


RUN_PARTS_RE = re.compile(
    r"^(<w:r(?:\s[^>]*)?>)((?:<w:rPr>.*?</w:rPr>|<w:rPr/>)?)(<w:t(?:\s[^>]*)?>)([^<]*)</w:t></w:r>$",
    re.S,
)


def split_run_at_anchor(run_xml: str, needle: str) -> tuple[str, str, str]:
    """Split one run into (before, anchor, after) runs so a comment range can
    cover exactly `needle` instead of the whole run.

    Each piece keeps the run's own properties. Pieces with no text are
    returned as empty strings. If the run is not the simple
    <w:r><w:rPr/>?<w:t>text</w:t></w:r> shape, or `needle` is not inside its
    text, the run is returned unsplit as the middle element (the previous,
    whole-run behaviour)."""
    m = RUN_PARTS_RE.match(run_xml)
    if not m:
        return "", run_xml, ""
    r_open, rpr, _t_open, text = m.group(1), m.group(2), m.group(3), m.group(4)
    idx = text.find(needle)
    if idx == -1:
        return "", run_xml, ""

    def piece(t: str) -> str:
        if not t:
            return ""
        return f'{r_open}{rpr}<w:t xml:space="preserve">{t}</w:t></w:r>'

    return piece(text[:idx]), piece(needle), piece(text[idx + len(needle):])


def ensure_comments_infrastructure(parts: dict) -> None:
    """Mutates `parts` (path -> str content) in place so the document has a
    valid, registered word/comments.xml, creating it if necessary."""
    if "word/comments.xml" not in parts:
        parts["word/comments.xml"] = EMPTY_COMMENTS_XML

    ct_path = "[Content_Types].xml"
    ct = parts[ct_path]
    if "/word/comments.xml" not in ct:
        override = '<Override PartName="/word/comments.xml" ContentType="%s"/>' % COMMENTS_CONTENT_TYPE
        parts[ct_path] = ct.replace("</Types>", override + "</Types>")

    rels_path = "word/_rels/document.xml.rels"
    if rels_path not in parts:
        parts[rels_path] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            "</Relationships>"
        )
    rels = parts[rels_path]
    if COMMENTS_REL_TYPE not in rels:
        existing_ids = [int(m) for m in re.findall(r'Id="rId(\d+)"', rels)]
        next_id = max(existing_ids, default=0) + 1
        rel = '<Relationship Id="rId%d" Type="%s" Target="comments.xml"/>' % (next_id, COMMENTS_REL_TYPE)
        parts[rels_path] = rels.replace("</Relationships>", rel + "</Relationships>")


SELF_CLOSING_COMMENTS_ROOT_RE = re.compile(r"(<w:comments\b[^>]*)/>")


def normalize_comments_root(xml: str) -> str:
    """Some tools (e.g. the docx npm package) scaffold an EMPTY comments
    part as a self-closing root element: <w:comments .../> with no
    children. That has no literal "</w:comments>" to splice new comments
    before, so normalize it to an explicit open/close pair first."""
    return SELF_CLOSING_COMMENTS_ROOT_RE.sub(r"\1></w:comments>", xml, count=1)


# Comment bodies are PLAIN TEXT. The `**bold**` / `*italic*` / `==highlight==`
# markers understood by parseRuns() in docx_helpers.js apply to the DOCUMENT
# BODY only — they never reach this script, which writes straight into
# comments.xml. Left alone, the marker characters are printed literally into
# the margin balloon. Rather than fail or silently ship them, strip them and
# say so, so the author learns the rule without the reader seeing the damage.
_MARKER_RE = re.compile(r"\*\*(.+?)\*\*|==(.+?)==|(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", re.S)


def strip_inline_markers(text: str) -> tuple[str, int]:
    """Remove **bold** / *italic* / ==highlight== markers, keeping the words.

    Returns (cleaned_text, number_of_markers_removed).
    """
    count = 0

    def _sub(m):
        nonlocal count
        count += 1
        return next(g for g in m.groups() if g is not None)

    cleaned = _MARKER_RE.sub(_sub, text)
    return cleaned, count


def build_comment_xml(cid: int, author: str, initials: str, date: str, text: str) -> str:
    para_id = uuid.uuid4().hex[:8].upper()
    return (
        f'<w:comment w:id="{cid}" w:author="{xml_escape(author)}" w:date="{date}" w:initials="{xml_escape(initials)}">'
        f'<w:p w14:paraId="{para_id}" w14:textId="77777777">'
        f'<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:annotationRef/></w:r>'
        f'<w:r><w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r>'
        f"</w:p></w:comment>"
    )


def check_distinct_anchors(comments: list) -> None:
    """Refuse two comments that share the same anchor text.

    Two comments on one identical span give the reader no way to tell which
    remark belongs to which point, and almost always mean the anchors were
    chosen too broadly (a whole paragraph instead of the phrase or number a
    comment is about). Fail loudly so the anchors get narrowed.
    """
    seen: dict[str, int] = {}
    for c in comments:
        anchor = c["anchor"].strip()
        if anchor in seen:
            raise RuntimeError(
                f"comments {seen[anchor]} and {c['id']} use the same anchor {anchor[:40]!r} — "
                "anchor each comment to the specific phrase or number it discusses"
            )
        seen[anchor] = c["id"]


def insert_comments(input_path: Path, comments: list, output_path: Path, default_author: str, default_initials: str) -> None:
    check_distinct_anchors(comments)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        with zipfile.ZipFile(input_path) as zin:
            names = zin.namelist()
            zin.extractall(tmp)

        # Load the handful of parts we might touch as strings; keep
        # everything else as raw bytes to round-trip untouched.
        text_parts = {}
        for rel in ("[Content_Types].xml", "word/_rels/document.xml.rels", "word/comments.xml", "word/document.xml"):
            p = tmp / rel
            if p.exists():
                text_parts[rel] = p.read_text(encoding="utf-8")

        if "word/document.xml" not in text_parts:
            raise RuntimeError("word/document.xml not found — is this a valid .docx?")

        ensure_comments_infrastructure(text_parts)
        if "word/_rels/document.xml.rels" not in names and "word/_rels/document.xml.rels" in text_parts:
            names.append("word/_rels/document.xml.rels")
        if "word/comments.xml" not in names:
            names.append("word/comments.xml")

        doc_xml = text_parts["word/document.xml"]
        comments_xml = normalize_comments_root(text_parts["word/comments.xml"])

        existing_ids = {int(m) for m in re.findall(r'<w:comment w:id="(\d+)"', comments_xml)}
        new_comment_bodies = []

        total_stripped = 0
        for c in comments:
            cid = int(c["id"])
            if cid in existing_ids:
                raise RuntimeError(f"comment id {cid} already exists in this document")
            existing_ids.add(cid)

            anchor = c["anchor"]
            text, stripped = strip_inline_markers(c["text"])
            if stripped:
                total_stripped += stripped
            author = c.get("author", default_author)
            initials = c.get("initials", default_initials)
            date = c.get("date") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            run_start, run_end = find_run_span(doc_xml, anchor)
            before, run_xml, after = doc_xml[:run_start], doc_xml[run_start:run_end], doc_xml[run_end:]
            pre_run, run_xml, post_run = split_run_at_anchor(run_xml, anchor)
            before, after = before + pre_run, post_run + after
            range_start = f'<w:commentRangeStart w:id="{cid}"/>'
            range_end = (
                f'<w:commentRangeEnd w:id="{cid}"/>'
                f'<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="{cid}"/></w:r>'
            )
            doc_xml = before + range_start + run_xml + range_end + after
            new_comment_bodies.append(build_comment_xml(cid, author, initials, date, text))
            print(f"inserted comment {cid}: anchor={anchor[:40]!r}...")

        if total_stripped:
            print(
                f"note: stripped {total_stripped} inline marker(s) (**bold** / *italic* / ==highlight==) "
                "from comment text — comment bodies are plain text; the words were kept."
            )

        comments_xml = comments_xml.replace("</w:comments>", "".join(new_comment_bodies) + "</w:comments>")

        text_parts["word/document.xml"] = doc_xml
        text_parts["word/comments.xml"] = comments_xml

        for rel, content in text_parts.items():
            (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp / rel).write_text(content, encoding="utf-8")

        if output_path.exists():
            output_path.unlink()
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for name in names:
                zout.write(tmp / name, arcname=name)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("comments_json", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=None)
    ap.add_argument("--author", default="精读笔记")
    ap.add_argument("--initials", default="")
    args = ap.parse_args()

    comments = json.loads(args.comments_json.read_text(encoding="utf-8"))
    output_path = args.output or args.input

    if args.output is None:
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tf:
            tmp_out = Path(tf.name)
        insert_comments(args.input, comments, tmp_out, args.author, args.initials)
        shutil.move(str(tmp_out), str(args.input))
    else:
        insert_comments(args.input, comments, output_path, args.author, args.initials)

    print(f"Done. {len(comments)} comment(s) inserted. Output: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
