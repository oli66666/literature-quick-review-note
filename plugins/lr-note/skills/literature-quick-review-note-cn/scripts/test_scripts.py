#!/usr/bin/env python3
"""
test_scripts.py

Fast, dependency-free checks for the two Python scripts that manipulate OOXML
internals. These are the parts of the pipeline where a one-line mistake can
produce a .docx that Word or WPS refuses to open, or that silently puts a
margin comment on the wrong sentence — failures that `validate_docx.py` does
NOT catch, because it only checks structure, never content.

This is a unit test, not an acceptance test. Running the full skill on a real
paper proves the pipeline works today; this proves it still works after you
edit a script. Run it before and after touching anything in scripts/.

    python3 scripts/test_scripts.py

Exits 0 on success, 1 on the first failure, with a diff-style report.
No third-party packages required.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILURES: list[str] = []
CHECKS = 0


def load(name: str):
    """Import a sibling script as a module without needing a package."""
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check(label: str, got, want) -> None:
    global CHECKS
    CHECKS += 1
    if got != want:
        FAILURES.append(f"{label}\n      got:  {got!r}\n      want: {want!r}")


def check_raises(label: str, fn, needle: str) -> None:
    """Assert fn() raises, and that the message mentions `needle`."""
    global CHECKS
    CHECKS += 1
    try:
        fn()
    except Exception as exc:  # noqa: BLE001 - any loud failure is acceptable
        if needle.lower() not in str(exc).lower():
            FAILURES.append(f"{label}\n      raised, but message lacked {needle!r}: {exc}")
        return
    FAILURES.append(f"{label}\n      expected an exception, none was raised")


# ---------------------------------------------------------------------------
# 1. insert_comments.strip_inline_markers
#
# Comment bodies are plain text. Markers must be removed (words kept) so the
# balloon never shows literal asterisks — while a lone asterisk that is part
# of the content (a significance marker) must survive untouched.
# ---------------------------------------------------------------------------

def test_strip_inline_markers(ic) -> None:
    f = ic.strip_inline_markers

    check("plain text is unchanged",
          f("普通文字,没有标记。"), ("普通文字,没有标记。", 0))

    check("**bold** is stripped, words kept",
          f("这里**很重要**,请注意。"), ("这里很重要,请注意。", 1))

    check("*italic* is stripped, words kept",
          f("用 *斜体* 标术语。"), ("用 斜体 标术语。", 1))

    check("==highlight== is stripped, words kept",
          f("并 ==高亮== 一句。"), ("并 高亮 一句。", 1))

    check("all three in one string are counted separately",
          f("三种都有:**粗** *斜* ==亮==。"), ("三种都有:粗 斜 亮。", 3))

    # The regression that motivated this test: a significance marker is content,
    # not markup, and must not be eaten.
    check("a lone trailing asterisk survives",
          f("显著性 p < .05* 这样的孤立星号应保留。"),
          ("显著性 p < .05* 这样的孤立星号应保留。", 0))

    check("an unpaired asterisk mid-sentence survives",
          f("Table 2* 见下页。"), ("Table 2* 见下页。", 0))

    check("markers spanning a newline are still handled",
          f("前半**跨\n行加粗**后半"), ("前半跨\n行加粗后半", 1))

    check("bold is matched before italic (no mis-pairing)",
          f("**A** 与 **B**"), ("A 与 B", 2))


# ---------------------------------------------------------------------------
# 2. insert_comments.find_run_span
#
# A comment anchor must resolve to exactly one <w:r> run. The three loud
# failures below are the only thing standing between a typo'd anchor and a
# comment attached to the wrong sentence.
# ---------------------------------------------------------------------------

RUN = '<w:r><w:rPr/><w:t xml:space="preserve">{}</w:t></w:r>'
DOC = "<w:body><w:p>{}</w:p></w:body>"


def test_find_run_span(ic) -> None:
    f = ic.find_run_span

    xml = DOC.format(RUN.format("一段普通的正文句子。") + RUN.format("另一段不同的文字。"))

    start, end = f(xml, "普通的正文")
    check("a unique anchor resolves to the run containing it",
          xml[start:end].count("<w:r>"), 1)
    CHECKS_OK = "普通的正文" in xml[start:end]
    check("the returned span actually contains the anchor", CHECKS_OK, True)

    check_raises("a missing anchor raises",
                 lambda: f(xml, "这段文字并不存在"), "not found")

    dup = DOC.format(RUN.format("重复的句子。") + RUN.format("重复的句子。"))
    check_raises("a non-unique anchor raises",
                 lambda: f(dup, "重复的句子"), "unique")

    # An anchor straddling two runs (i.e. crossing a bold/plain boundary in the
    # source markup) must fail loudly rather than silently mis-anchoring.
    split = DOC.format(RUN.format("前半部分") + RUN.format("后半部分"))
    check_raises("an anchor straddling two runs raises",
                 lambda: f(split, "前半部分后半部分"), "")


# ---------------------------------------------------------------------------
# 3. strip_highlightcs.strip_highlightcs
#
# docx-js emits an invalid <w:highlightCs/> alongside every valid <w:highlight/>.
# Word tolerates it; WPS refuses to open the file. The fix must remove every
# highlightCs, keep every highlight, and leave a still-valid zip package.
# ---------------------------------------------------------------------------

MINIMAL_DOC = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    "<w:body><w:p><w:r><w:rPr>"
    '<w:highlight w:val="yellow"/><w:highlightCs w:val="yellow"/>'
    "</w:rPr><w:t>甲</w:t></w:r><w:r><w:rPr>"
    '<w:highlight w:val="yellow"/><w:highlightCs w:val="yellow"/>'
    "</w:rPr><w:t>乙</w:t></w:r></w:p></w:body></w:document>"
)

CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-'
    'officedocument.wordprocessingml.document.main+xml"/></Types>'
)


def test_strip_highlightcs(sh, tmp: Path) -> None:
    src, dst = tmp / "in.docx", tmp / "out.docx"
    with zipfile.ZipFile(src, "w") as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("word/document.xml", MINIMAL_DOC)

    removed = sh.strip_highlightcs(src, dst)
    check("both highlightCs elements are reported removed", removed, 2)

    with zipfile.ZipFile(dst) as z:
        names = set(z.namelist())
        out = z.read("word/document.xml").decode("utf-8")

    check("no highlightCs survives", "highlightCs" in out, False)
    check("the valid highlight is untouched", out.count('<w:highlight w:val="yellow"/>'), 2)
    check("the text content is untouched", ("甲" in out and "乙" in out), True)
    check("every part is carried over", names, {"[Content_Types].xml", "word/document.xml"})

    # A file with nothing to fix must still be produced, unchanged.
    clean_src, clean_dst = tmp / "clean.docx", tmp / "clean_out.docx"
    with zipfile.ZipFile(clean_src, "w") as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("word/document.xml", re.sub(r"<w:highlightCs[^/]*/>", "", MINIMAL_DOC))
    check("a clean file reports zero removals", sh.strip_highlightcs(clean_src, clean_dst), 0)
    check("a clean file is still written", clean_dst.exists(), True)


def test_check_distinct_anchors(ic) -> None:
    f = ic.check_distinct_anchors
    distinct = [{"id": 0, "anchor": "ICC2 = .64"}, {"id": 1, "anchor": "r = .79"}]
    check("distinct anchors pass", f(distinct), None)
    same = [{"id": 0, "anchor": "同一段文字"}, {"id": 1, "anchor": "同一段文字 "}]
    check_raises("two comments on the same anchor raise", lambda: f(same), "same anchor")


def test_split_run_at_anchor(ic) -> None:
    f = ic.split_run_at_anchor
    bold = '<w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">{}</w:t></w:r>'

    pre, mid, post = f(bold.format("前半部分ICC2 = .64后半部分"), "ICC2 = .64")
    check("middle split: the anchor run holds only the anchor", mid, bold.format("ICC2 = .64"))
    check("middle split: text before the anchor keeps its formatting", pre, bold.format("前半部分"))
    check("middle split: text after the anchor keeps its formatting", post, bold.format("后半部分"))

    pre, mid, post = f(RUN.format("整段文字"), "整段文字")
    check("an anchor equal to the whole run needs no split", (pre, post), ("", ""))

    pre, mid, post = f(RUN.format("开头就是锚点,后面还有"), "开头就是锚点")
    check("an anchor at the start leaves no empty run before it", pre, "")

    odd = '<w:r><w:t>甲</w:t><w:tab/><w:t>乙</w:t></w:r>'
    check("an unusual run is anchored whole rather than guessed at", f(odd, "甲"), ("", odd, ""))


# ---------------------------------------------------------------------------

def main() -> int:
    import tempfile

    ic = load("insert_comments")
    sh = load("strip_highlightcs")

    test_strip_inline_markers(ic)
    test_find_run_span(ic)
    test_check_distinct_anchors(ic)
    test_split_run_at_anchor(ic)
    with tempfile.TemporaryDirectory() as d:
        test_strip_highlightcs(sh, Path(d))

    if FAILURES:
        print(f"FAILED {len(FAILURES)} of {CHECKS} checks:\n")
        for i, f in enumerate(FAILURES, 1):
            print(f"  {i}. {f}\n")
        return 1

    print(f"OK — {CHECKS} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
