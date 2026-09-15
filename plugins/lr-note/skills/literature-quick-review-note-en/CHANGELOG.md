# Changelog

All notable changes to this skill are recorded here. The version number lives
under `metadata.version` in `SKILL.md`'s frontmatter, and the two are expected to
match. It must not be a top-level frontmatter key: the skill format permits only
`name`, `description`, `license`, `allowed-tools`, `metadata` and `compatibility`
there, and an unexpected key fails validation on upload.

This project follows [Semantic Versioning](https://semver.org/) as applied to a
skill rather than a library:

- **MAJOR** — a change to the note's structure or to the output contract that
  makes new notes look or read differently from old ones.
- **MINOR** — a new capability, a new helper, or a new rule that constrains
  output without reshaping it.
- **PATCH** — a bug fix, a wording correction, or a documentation change.

## [1.1.0] — 2026-09-15

### Changed

- **A comment now highlights only its anchor text.** `insert_comments.py`
  used to wrap the whole run containing the anchor, and in a docx-js document
  the plain text of a paragraph is usually one run, so even a short anchor
  highlighted the entire paragraph. It now splits that run into before /
  anchor / after runs with the same formatting. A first real-paper test had six
  of nine comments covering whole paragraphs, which left the reader guessing
  what each remark referred to. Runs with an unusual structure are still
  anchored whole rather than guessed at.
- **Comment anchors must be specific**: the shortest unique phrase, number or
  term the comment discusses, and never the same anchor for two comments.
  `insert_comments.py` refuses duplicate anchors, and the verification pass
  checks both points. `test_scripts.py` covers the run splitting and the
  duplicate check (29 checks). The scripts stay identical to the
  Chinese-output skill's apart from the `--author` default.
- The placeholder example (`example_comments.json`, `docs/example.png`)
  demonstrates a short anchor; the screenshot is re-rendered at higher
  resolution in the same two-page layout as the Chinese skill's.

## [1.0.0] — 2026-09-15

First release of the English-output sibling, shipped in `lr-note` plugin
2.0.0. Forked from the Chinese-output skill v1.0.0 (then named
`literature-quick-review-note`, renamed
[`literature-quick-review-note-cn`](../literature-quick-review-note-cn/) in the
same plugin release), keeping every structural rule, visual-formatting value,
and pipeline step identical, and translating only the document's language and
the SKILL.md prose.

### What's different from the Chinese-output skill

- Note files are named after the paper with an `_EN` suffix
  (`Smith2024_EN.docx`); the Chinese skill uses `_CN`, so notes in both
  languages on one paper can sit in the same folder.
- The description spells out when this skill applies rather than the Chinese
  one: an output language the user names explicitly wins, whatever language
  the request is written in; otherwise the note follows the request language.

- Every section label, heading pattern and instruction in `SKILL.md` is in
  English, and the note it produces is written entirely in English regardless
  of the source paper's language (the Chinese sibling instead always writes
  in Chinese, regardless of the source paper's language).
- Body section numbering uses Arabic numerals (`1.`, `2.`, `3.`…) instead of
  Chinese numerals (一、二、三…).
- The bilingual-title convention is now conditional: a second, gray
  translation line under the title is added only when the paper's own title
  is not already in English, instead of always adding a Chinese translation
  line.
- `scripts/insert_comments.py`'s `--author` default changed from `"精读笔记"`
  to `"Quick-Overview Note"`, so margin-comment authorship reads sensibly in
  Word/WPS's reviewer list. This is the one functional (not just prose)
  difference between the two skills' script folders — every other script is
  shared verbatim, since `docx_helpers.js`, `strip_highlightcs.py`,
  `validate_docx.py` and `render_preview.sh` manipulate OOXML/markup
  mechanics rather than language content.
- `scripts/example_build.js` and `scripts/example_comments.json` were
  translated into an English placeholder example so a fresh reader copies an
  English template, not a Chinese one.

### Carried over unchanged

- The condensed "quick overview" note structure: real Word Heading 1/2/3
  styles, source-PDF page ranges on content headings, comparison tables,
  block quotes, and `**bold**` / `*italic*` / `==highlight==` inline markers.
- Genuine anchored Word margin comments, under the same three conditions for
  a cross-paper comparison to be admissible (real and checkable, actually
  known, grounded in a stated point of contact).
- The conceptual/review/theoretical-paper handling (the empirical-basis row
  collapses rather than being filled with invented method detail).
- The full build pipeline (build → strip WPS `highlightCs` → insert comments
  → validate → render) and the mandatory pre-delivery verification pass.
- The one-paper-at-a-time batch-mode protocol and its rationale.
- All exact visual-formatting values (fonts, sizes, hex colors, spacing,
  table shading and borders) — a note built by either skill should look
  identical apart from its language.
