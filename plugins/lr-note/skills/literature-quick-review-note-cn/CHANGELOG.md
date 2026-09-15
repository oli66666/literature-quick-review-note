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

## [2.0.0] — 2026-09-15

A major version because two things users rely on change: how the skill is
invoked, and what the note file is called. The note's content and formatting
are unchanged.

### Changed

- **Renamed** from `literature-quick-review-note` to
  `literature-quick-review-note-cn`, because the plugin now also ships an
  English-output sibling, `literature-quick-review-note-en`. The Claude Code
  invocation becomes `/lr-note:literature-quick-review-note-cn`. An account
  skill uploaded under the old name is not renamed by this release; upload the
  new ZIP and remove the old skill, or both will trigger.
- **Note filenames now carry a `_CN` suffix** (`Smith2024.pdf` →
  `Smith2024_CN.docx`), matching the sibling's `_EN`, so a Chinese and an
  English note on the same paper cannot overwrite each other. Notes made with
  1.x have no suffix; the skill now points such a file out instead of silently
  writing a second one beside it.
- **The description states when this skill applies versus the English one**:
  an output language the user names explicitly wins, otherwise the note follows
  the language of the request. Before, a Chinese request for an English note
  had nothing to route it away from this skill.

## [1.0.0] — 2026-09-14

First public release. The skill had been in private use for some time; this
entry records the state it is published in, not a list of changes against an
earlier public version.

### The note itself

- Condensed "quick overview" (速览) note structure with real Word Heading 1/2/3
  styles, source-PDF page ranges on content headings, comparison tables, block
  quotes, and `**bold**` / `*italic*` / `==highlight==` inline markers.
- Genuine anchored Word margin comments — comments that Word and WPS both show
  in the margin, attached to a specific span of text, which most `.docx`
  libraries cannot write at all.
- Conceptual papers (provocation pieces, reviews, purely theoretical articles)
  are handled explicitly: the 实证基础 row collapses rather than being filled
  with invented method detail.

### Rules that took the longest to settle

- **Comment bodies are plain text.** Inline markers work in the document body,
  because the body is built through `parseRuns()`; comments are written straight
  into `comments.xml` and never pass through it. Rather than leave this as a
  rule the author has to remember, `insert_comments.py` now strips the markers
  itself, keeps the words, and prints a note saying it did so. A lone asterisk
  that is content — a significance marker such as `p < .05*` — survives
  untouched.
- **No cross-paper comparison in the body; comparison is allowed in comments.**
  A note's body should stand on its own paper. A comparison is a judgement, and
  judgements belong in the margin. The exception carries three conditions: the
  compared work must be real and verifiable, the comparison must rest on
  something actually stated in both, and the comment must say it is the note's
  addition rather than the paper's argument.
- **Batch mode delivers one paper at a time.** The skill finishes, verifies and
  delivers each note before reading the next paper, and does not wait for a new
  instruction between papers. Holding several papers in context at once is how a
  sample size from paper 3 ends up in the note for paper 5. Two distinct
  contamination modes are checked for: a number migrating between papers (a
  false statement) and a cross-paper comparison in the body (a true statement in
  the wrong place).
- **Verification is a mandatory step, not a suggestion.** Step 7 of the build
  pipeline re-reads the finished note against the paper before delivery.

### Reading strategy

- Documented two-method reading: `pdftotext -layout` for the whole paper, page
  images only where they earn their cost. The procedure establishes the
  page-number offset from the first two pages as images, extracts the text, runs
  a cheap per-page caption scan to locate tables and figures, and reads only
  those pages as images. On a 22-page paper this was 7 image reads instead of
  19, with no loss of fidelity.
- Three signals the extraction step should react to: a scan with no text layer,
  chart values printed as text labels, and non-standard captions.

### Scripts

- `docx_helpers.js` — build helpers, including `Quote` and `gridRow` (an
  N-column table row with optional header and label column).
- `strip_highlightcs.py` — removes the invalid `<w:highlightCs/>` that docx-js
  emits alongside every valid `<w:highlight/>`. Word tolerates it; WPS refuses
  to open the file.
- `insert_comments.py` — anchored comment insertion. An anchor that is missing,
  ambiguous, or straddles two runs fails loudly rather than silently attaching
  the comment to the wrong sentence.
- `validate_docx.py` — structural validation.
- `render_preview.sh` — renders to PDF for a visual check; `--comments` puts the
  margin comments into the rendered margin.
- `test_scripts.py` — 21 unit checks over the two OOXML scripts. This is not the
  same thing as running the skill on a real paper: that proves the pipeline
  works today, this proves it still works after someone edits a script.

### Packaging

- Published as a Claude plugin marketplace (`.claude-plugin/marketplace.json` at
  the repository root, `plugin.json` per plugin), so the skill installs with one
  command instead of a manual folder copy. The skill folder itself stays
  self-contained, so copying it by hand still works.

### Documentation

- A `scripts/`-missing fallback: the Visual formatting section specifies every
  font, size, colour and spacing value the JavaScript helpers encode, so a
  skill system that syncs only `SKILL.md` can rebuild them and get byte-identical
  formatting. The Python scripts have no such fallback, so a scripts-less
  install should deliver a note without comments rather than improvise comment
  XML.
- A fallback for Crossref lookups when a direct request is refused by an egress
  proxy: use the agent's own web-fetch tool against the same URL.
- An example screenshot built from placeholder text, never from a real paper.
