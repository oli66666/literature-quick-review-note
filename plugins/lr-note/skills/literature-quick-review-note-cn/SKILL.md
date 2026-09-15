---
name: literature-quick-review-note-cn
description: "Build a condensed \"quick overview\" (速览) intensive-reading note for an academic paper as a WPS-compatible Word (.docx) file written in Chinese, with real margin comments grounded in genuine literature. Use when the user asks for a 文献速览/精读笔记 quick-overview version of a paper (as distinct from a full verbose 精读 note) AND either explicitly wants the note in Chinese, or names no output language and writes the request in Chinese. If the user explicitly asks for the note in English (in any request language, e.g. 做英文版速览笔记), use literature-quick-review-note-en instead."
metadata:
  version: 3.0.0
---

# 文献速览笔记 (Literature Quick-Overview Note, Chinese output)

This is a **condensed variant** of intensive-reading (精读) notes: the whole paper's framework and precise content, distilled — not a page-by-page translation. Use it when the user asks for a "速览" / "概括版" / "quick overview" style note, or references wanting "this version" of a note style they've approved before. If the user just says "精读" with no quick-overview signal, prefer a fuller methodology instead, if one is available.

**Output language, and which of the two sibling skills applies.** This skill writes the note in Chinese. Its sibling in the same plugin, `literature-quick-review-note-en`, produces the same note in English. Decide between them in this order: (1) if the user explicitly names an output language ("做英文版笔记", "write the note in Chinese"), follow it, whatever language the request itself is written in; (2) if they name none, follow the language of the request — Chinese request, this skill; English request, the `-en` sibling. If the user invoked one of the two by name, use that one and do not second-guess it.

This skill folder is self-contained: `scripts/` ships portable Node.js and Python utilities for the document pipeline (build helpers, the WPS compatibility fix, comment insertion, validation, rendering). The `SKILL.md` instruction format is directly usable by Claude and Codex when installed as a compatible skill; other AI systems may require adapting the instruction file to their own format. The scripts themselves can be run independently.

## Platform compatibility

- **Claude:** install or copy this folder into the location used by the Claude skill system.
- **Codex:** install or copy this folder into the location used by the Codex skill system. The workflow and scripts are the same, but the host must support `SKILL.md` skills.
- **Other AI systems:** use the scripts directly or adapt `SKILL.md`; automatic skill triggering is not guaranteed.

The skill does not require a personal filesystem path, a bundled paper PDF, or an API key. Any current citation-count, journal-metric, or literature lookup requires the host agent to have its own web or API access.

## Requirements

- **Node.js** with the `docx` npm package (`npm install docx`) — for building the .docx from scratch.
- **Python 3.8+**, standard library only, for `scripts/strip_highlightcs.py`, `scripts/insert_comments.py` and `scripts/validate_docx.py`. Optionally `pip install python-docx` for one extra smoke-test check inside `validate_docx.py` (it degrades gracefully without it).
- **LibreOffice** (`soffice` on PATH) and **poppler-utils** (`pdftoppm`) for `scripts/render_preview.sh`, the visual-spot-check step. Not required for the build/comment/validate steps themselves.

## If `scripts/` is missing

Some skill installations carry only this `SKILL.md` and not the `scripts/` folder alongside it (account-level skill sync, a partial copy, someone pasting just the instructions). **Check for `scripts/docx_helpers.js` before planning the build**, and if it is not there, recover in this order:

1. **Look for a local copy first.** The user may already have the full skill folder or a zip of it somewhere reachable (a project folder, a downloads folder, a previous session's output directory). A quick search for `docx_helpers.js` costs one command and saves rebuilding everything.
2. **Fetch the published copy** if the user has one — this skill is distributed as a self-contained folder, so pointing at that folder or repository restores every script at once.
3. **Rebuild the helpers from this file.** This is a supported fallback, not a degraded one: the "Visual formatting" section below specifies every value the helpers encode — font names per script, exact half-point sizes, every hex colour, every spacing triple, table shading and border weights. Write a local `docx_helpers.js` implementing `P`, `Quote`, `BulletP`, `H`, `TitleLine`, `cellP`, `bibRow`, `gridRow`, `TABLE_BORDERS` and `defaultStyles()` to those values, plus a `parseRuns()` handling `**bold**` / `*italic*` / `==highlight==` in that alternation order. Do not improvise different colours or spacing because the reference file is absent — the whole point of writing them down here is that the output stays identical either way.
4. **The Python steps have no such fallback and must not be skipped or reimplemented casually.** `strip_highlightcs.py` (WPS compatibility) and `insert_comments.py` (real Word comments) each manipulate OOXML internals that are easy to get subtly wrong — `insert_comments.py` in particular creates the comments part, its content-type override and its relationship when none exists. If these are unavailable, say so plainly and deliver a note without margin comments rather than hand-rolling comment XML and shipping a file that Word or WPS may refuse to open.

Tell the user which route was taken. "Rebuilt the helpers because the skill's scripts folder wasn't present" is information they need — it is the difference between a reproducible build and a one-off.

## Non-negotiable structural rules

1. **No manual table of contents.** Use real Word `Heading 1/2/3` paragraph styles (not bold plain text) so Word's Navigation Pane / outline view works.
2. **Every content-bearing heading gets the original PDF's page range in parentheses**, e.g. `一、研究背景与研究问题(原文 pp.176–180)`. Look up real page numbers from the source PDF — never guess.
3. **No cross-paper comparison in the BODY of the note**, and no "与本项目其他文献的关联" section. The body reports what this one paper says and whom this one paper cites — nothing else.
   **Margin comments are the deliberate exception.** Placing the paper back into its literature — including alongside other papers the reader is working through — is precisely what comments are for. But every comparison made in a comment must meet all three of these conditions:
   - **Real and checkable.** The other work exists and its author, year, title and venue are correct. Never infer a work's argument from its title, and never cite from a vague memory of having seen it.
   - **Actually known.** You are comparing a specific claim, figure or methodological step that you know the other work makes — not a position reconstructed from its subject matter.
   - **Grounded, not asserted.** Say *on what point* the comparison holds — which proposition, which number, which step — and mark it clearly as the note-taker's addition. "Similar to X" or "contradicts Y" with no stated point of contact is a guess, not a comparison.
   If any of the three fails, leave the comparison out. One fewer comment always beats one fabricated connection.
4. **Body text is a distillation of the original, not a translation.** All content must be based on the real paper — never fabricate findings, citations, or numbers.

## Content style: summarize, don't translate

This is the part that distinguishes "quick overview" from a fuller note:

- Default pattern per point: **a bold short mechanism/key-phrase label**, followed by 1–2 concise sentences of elaboration — not a paragraph-length translation of the original. E.g. `**核心机制:climate for inclusion(包容氛围)削弱了 gender diversity(性别多元化)与 relationship conflict(关系冲突)之间的关联。** 在包容度高的单位中……`
- **Technical terms and core expressions: the paper's English original first, the Chinese in parentheses, at every occurrence.** Write `climate for inclusion(包容氛围)`, `diversity management(多元化管理)`, `inclusion(包容)`, `historically disadvantaged groups(弱势群体)` — every time the term appears, not only the first time. The reader works from the English paper and writes in English, so the exact English wording is what they will search for, quote and cite; the Chinese keeps the note readable. The rules:
  - **What counts:** constructs and variables, their dimensions, named theories, models and perspectives, methods and analytic techniques, and the author's core expressions (coined phrases, or words the paper puts in quotation marks). An everyday word used in its ordinary sense is not a term and stays Chinese-only.
  - **Where:** everywhere in the note — headings, body paragraphs, bold labels, bullets, table cells, 影响力评价, 评述与可引用点, and margin comments. Exceptions: the 题录信息 row labels, the gray Chinese title translation, the Harvard reference, names of authors and journals, statistical symbols and values (β, rwg, ICC1, p), and the one permitted direct quote, which is already English.
  - **Use the paper's own wording**, never a back-translation, and keep the Chinese rendering consistent: once `relationship conflict` is `关系冲突`, it stays `关系冲突` for the whole note. Where the paper uses an abbreviation, follow it: `CFA(验证性因子分析)`.
  - **Format:** half-width parentheses with no space before them, matching the page-range style: `climate for inclusion(包容氛围)`. Do not italicise the English term.
  - Because such terms repeat throughout the note, a bare term is rarely unique enough to serve as a comment anchor; see the Margin comments section.
- If a paper provides its own summary table (e.g. a themes/constructs table), reproduce it — that IS the concise summary; don't also re-narrate it at length afterward.
- Cap direct quotes at roughly **one for the entire document**, used only where a quote is genuinely more illustrative than a paraphrase ("只在非常必要的时候加入以佐证作者观点"). Paraphrase everything else.
- When it's genuinely hard to compress a point into a few words, just summarize it in full sentences rather than forcing an artificial short label — don't force-fit every sentence into the bold-label pattern.
- **Inline markers are limited to three: `**bold**`, `*italic*` and `==highlight==`, and they work in the document BODY only.** `parseRuns()` in `docx_helpers.js` recognises exactly these; anything else (`_underscore_`, `~~strike~~`, `__bold__`) is NOT parsed and its literal characters are printed into the document. `**bold**` is matched before `*italic*`, so the two never collide. Use italics sparingly and conventionally — a journal or book title — not as a second emphasis level; bold carries emphasis. The English terms in the `term(中文)` pattern above are not italicised. One caveat: a single unmatched `*` is left alone, but two unrelated lone asterisks in the SAME string will pair up and italicise everything between them, so keep literal asterisks (e.g. a significance marker like `p < .05*`) out of marked-up strings. **These markers do NOT work in margin comments** — see the Margin comments section.
- Section length should shrink a lot vs. a verbose note: condensing a background/methods/findings/discussion section from ~4-6 paragraphs each down to ~1-2 tight paragraphs per subsection is the right order of magnitude.

## Document structure (in order)

1. Title line (Heading 1): `文献总结:<paper short title / theme>(原文 pp.X–Y)`
2. `题录信息` (Heading 2) — a 2-column table, label column left, value column right:
   - 标题: English title, then Chinese translation on its own line **in gray text** (see Visual formatting)
   - 作者: bulleted list, one bullet per author with role/contribution in parentheses; then a `Note:` line with affiliation **in gray, ~2pt smaller than body** — no email addresses
   - 发表年份: year only (no volume/issue, no "advance online publication" sentence — that's redundant)
   - 发表期刊: a full **Harvard-style reference** (Author, A. (Year) 'Title', Journal, vol(issue), pp. x–y.) — journal-quality commentary (OA status, Scimago quartile/SJR/H-index) belongs in 影响力评价 instead, not duplicated here
   - DOI
   - 所属领域: **at most 3** most-relevant fields/keywords, chosen based on the paper's actual content, each in the `English(中文)` form, e.g. `diversity and inclusion(多元化与包容)`
   - 论文类型: in **English only** (e.g. "Empirical, qualitative research article.")
   - 研究范式 / 数据收集方法 / 抽样策略 / 样本构成 / 理论框架 / 伦理 — each a tight paragraph. In 理论框架, each theory is named in the `English(中文)` form with its citation, e.g. `status characteristics theory(地位特征理论; Ridgeway, 1991)`

   **Conceptual, review and theoretical papers.** The four empirical rows above (研究范式 / 数据收集方法 / 抽样策略 / 样本构成) assume a study with primary data. When the paper has none — a provocation paper, a narrative or systematic review, a purely theoretical piece — do not fill four rows with 不适用; that spends four rows of the table on zero information. Instead:
   - Collapse those four into a single row, `实证基础`, reading `不适用(无一手数据)` plus one sentence naming where the evidence actually comes from (e.g. 叙述式文献批判,证据来自既有实证研究、政策文件与咨询机构报告).
   - Give the reclaimed space to 理论框架: list every theory the paper applies OR stress-tests, since for this genre that list IS the substance.
   - Make 论文类型 explicit and unhedged: `Conceptual 'provocation paper'.` / `Narrative review article.` / `Systematic review.` / `Theoretical article.` — never leave it vague.
   - 伦理 reads `不适用(无一手数据)`, plus any conflict-of-interest or funding statement the paper does carry.
3. `影响力评价` (Heading 2) — bold-label bullets: 引用表现(via Crossref API lookup on the DOI) / 发表平台(via Scimago quartile/SJR/H-index lookup) / 2-4 核心贡献 items / 方法上的亮点 / 引用边界. One sentence may be `==highlighted==` (yellow) as the single standout takeaway — use sparingly, at most 1-2 per document.
4. Numbered body sections (一、二、三...) mirroring the paper's own structure (background/research questions → methods → findings → discussion → conclusion), each Heading 2 with a page range, subsections as Heading 3 with their own page ranges.
   **For a conceptual, review or theoretical paper, follow the paper's own argumentative structure instead** — do not force it into a methods/findings skeleton it does not have. Section the note the way the paper sections itself (e.g. diagnosis → what's missing on dimension A → what's missing on dimension B → research agenda → implications). Where such a paper stress-tests several theories in sequence, a `gridRow` table (theory / original premise / where it breaks) is usually a better rendering than four narrative paragraphs.
5. `六、评述与可引用点` (or next number) — 主要贡献 / 局限与引用时的注意 / 可直接引用的场景, all as concise bullets grounded in the paper's own self-reported limitations plus the note-taker's own assessment.

## Margin comments (real Word comments, not inline text)

- Add genuine analytical comments at core/key content points — your own analysis, connections to real literature (similar or contradictory views), or observations about the paper's structure/logic. **Every citation used in a comment must be real and verifiable — never fabricate a reference.** Comparisons with other papers belong here rather than in the body, under the three conditions in structural rule 3.
- **Anchor every comment to the exact words it discusses.** Use the shortest substring that is unique in the note and points at the specific number, term or claim the comment is about — `ICC2 = .64`, not the whole paragraph that contains it. Anchor to a full paragraph only when the comment genuinely addresses the paragraph as a whole. A paragraph-wide highlight leaves the reader guessing which sentence the remark refers to. **Never give two comments the same anchor**; `insert_comments.py` refuses it. If a short anchor is not unique (the script refuses that too), lengthen it by a few neighbouring characters rather than falling back to the whole paragraph. Terms written as `climate for inclusion(包容氛围)` recur throughout the note, so anchor to the term together with the words around it at the spot in question.
- When the user asks for comments across a specific section ("针对这一节选出3-5个地方加comments"), distribute 3-5 across that section, each anchored to a different specific sentence/phrase.
- Always hedge clearly that this is the note-taker's own addition, e.g. "这是精读笔记外加的理论标注;作者本身未提及……" — never blur it with what the paper itself argues.
- **Comment bodies are PLAIN TEXT — inline markers do not work in them.** `**bold**`, `*italic*` and `==highlight==` are parsed by `parseRuns()` in `docx_helpers.js`, which applies to the document BODY only; `insert_comments.py` writes comment text straight into `comments.xml` and never sees it. `scripts/insert_comments.py` strips any such markers (keeping the words) and prints a note saying how many it removed — so the output is clean either way, but the markers were still a mistake. For emphasis inside a comment, use wording ("关键在于……", "需要注意的是……") or quotation marks instead.
- **Always render with `--comments` when checking a note that has comments.** Without that flag the comments exist in the file but are invisible in the preview, so neither a misplaced anchor nor a formatting problem in the comment text can be seen. This is exactly how stray marker characters went unnoticed across several notes before the strip was added.
- Good sources for real, on-point citations: foundational methodology texts (e.g. Lincoln & Guba 1985 on trustworthiness, Braun & Clarke on thematic analysis and its later saturation/sample-size guidance), classic theory papers relevant to the topic (e.g. Crenshaw 1989 for intersectionality, Tajfel & Turner for social identity theory, Conger & Elder for the family stress model), and recruitment/methods critiques (e.g. systematic reviews on social-media recruitment bias). Pull from what you actually know to be real, or verify via web search — don't guess citation details.

## Visual formatting (exact values — match these, don't approximate from a screenshot when the real source file is reachable)

When the user points to a reference note (their own prior note, or one in their project folder) for style, **read that file's actual XML** (unzip the .docx, grep `word/document.xml` and `word/styles.xml`) to get exact hex colors, spacing and font names — don't eyeball a screenshot for exact values when the real file is available.

- Font: `Times New Roman` for ascii/hAnsi/cs, `宋体` (SimSun) for eastAsia, on every run. Also the document default color: `1A1A1A` (a near-black dark gray, not pure `000000`). `scripts/docx_helpers.js` already sets all of this up (`FONT`, `defaultStyles()`).
- Body text size: 21 half-points (10.5pt) on every body/bullet/table-cell run. Heading sizes come from docx-js's built-in Heading1/2/3 styles (32/26/24 half-points) — don't override size on headings, only bold + color + spacing.
- Heading colors (established house style — keep these, don't switch to docx-js's own defaults of 2E74B5/1F4D78): H1 and H2 = `1F3864` (dark navy), H3 = `2E5496` (medium navy).
- Paragraph spacing (twentieths of a point; `line` with no `lineRule` = auto/multiple, so 320 ≈ 1.33× line spacing):
  - Body paragraphs: `{ before: 60, after: 120, line: 320 }`, justified.
  - Bulleted paragraphs: `{ before: 40, after: 80, line: 320 }`, justified.
  - Table-cell paragraphs: `{ before: 20, after: 20, line: 280 }`, left-aligned.
  - Heading 2: `{ before: 320, after: 140 }`. Heading 3: `{ before: 200, after: 100 }`. Title (Heading 1): `{ before: 0, after: 240 }`.
  - Block quote (`Quote`): body spacing plus `indent: { left: 480, right: 480 }`.
- Table label/left column shading: `EDF2F9` (light blue) — this superseded an older gray `F2F2F2` convention; use blue in all new/updated notes. Header-row shading for a dark header: `1F3864` with white bold text. Table borders: outer `A6A6A6` single 4pt, inside `D0D0D0` single 2pt (soft gray, not black).
- Secondary/muted text (a translated subtitle, an affiliation "Note:" line): color `808080`, and for the Note line specifically drop the size ~2pt below body (e.g. 18 half-points vs 21).

All of the above is already implemented in `scripts/docx_helpers.js` — use its `P`, `Quote`, `BulletP`, `H`, `TitleLine`, `cellP`, `bibRow`, `themeRow`, `gridRow`, `TABLE_BORDERS`, `defaultStyles()` exports rather than reimplementing. Two of these are easy to miss:

- **`Quote(text)`** — the indented block-quote paragraph. This is what the one permitted direct quote goes in; a plain `P()` will not read as a quotation.
- **`gridRow(cells, opts)`** — a table row with ANY number of columns, for comparison tables the paper does not supply itself (two samples side by side, a theory/assumption/breaking-point grid). `themeRow` is the fixed 2-column special case; reach for `gridRow` for everything else rather than hand-rolling `TableRow`/`TableCell`. Pass `{ header: true }` for the header row; the first column is shaded as a label column by default (`{ labelFirst: false }` turns that off) and widths auto-size unless you pass `{ widths: [...] }`. Cell text goes through `parseRuns()`, so inline markers work inside cells.

`scripts/example_build.js` shows a complete working document built from these helpers, including `Quote` and `gridRow` in use — copy it and replace the placeholder content.

## Reading the source PDF (do this before building)

There are two ways to read the paper, and they differ by about an order of magnitude in cost. Choosing per-page rather than per-paper is both cheaper and *more accurate*, because each way is blind to something the other sees.

- **Page images** (the host's PDF reader, a page range at a time) show what a human sees: layout, column alignment inside a table, figures, formulas, running heads. Expensive.
- **Extracted text** (`pdftotext -layout`) pulls the characters out as plain text. An order of magnitude cheaper. It loses the content of figures entirely (a chart holds no characters) and scrambles complex tables; `-layout` uses whitespace to preserve simple column alignment, so plain 2–4 column tables usually survive readably. Never omit `-layout`.

**The procedure:**

1. **Read the first two pages as images.** Establish journal, volume/issue, page range, and above all the **page-number offset** between the PDF and the journal's own pagination — that has to be seen, not inferred. Also note whether the paper is typeset in one or two columns, which affects how well text extraction will hold up.
2. **Extract the whole paper as text** with `pdftotext -layout`. This gives you the full prose AND a map of where the tables and figures are, because their captions come through as text.
3. **Locate the tables cheaply.** Scanning per page for caption lines costs almost nothing and tells you exactly which pages need images:
   ```
   for p in $(seq 1 $NPAGES); do
     pdftotext -f $p -l $p -layout paper.pdf - | grep -qiE "^ *(table|figure) [0-9]" && echo "page $p has a table/figure"
   done
   ```
4. **Read only those pages as images**, and only where the text version actually failed. Judge each one: a clean 2–4 column table is fine as text; a wide correlation matrix, merged cells, multi-level headers or a rotated table needs the image.

**Three signals worth reacting to:**

- **Extraction returns nothing or gibberish** → the PDF is a scan with no text layer. Images are the only option (or OCR first).
- **A chart's values are printed as text labels beside it** (common in practitioner reports) → the text version already has every number; do not read that page as an image.
- **Captions use a non-standard label** ("Panel A", "表 1", no caption at all) → the scan in step 3 will miss them; skim the results section of the text version instead.

The payoff is not only cost. Extracted text shows **exact characters** — a misspelled author name in a footnote is obvious in text and easy to miss in an image. Images show **spatial structure** — which number sits in which cell. Use each for what it is good at.

## Build pipeline

1. **Build with docx-js (Node `docx` package)**, using `scripts/docx_helpers.js` (see `scripts/example_build.js` for a template). Support the `**bold**` / `*italic*` / `==highlight==` inline markers — `parseRuns()` in the helpers file already does this.
2. **Fix the WPS `highlightCs` bug**: docx-js emits both a valid `<w:highlight w:val="yellow"/>` and an invalid `<w:highlightCs .../>` for any highlighted run. Word tolerates the latter; WPS Office's stricter parser rejects it. Run this on every build before delivery, regardless of whether the user mentioned WPS:
   ```
   python3 scripts/strip_highlightcs.py mynote.docx
   ```
3. **Add real Word comments** with `scripts/insert_comments.py`. It is self-contained: if the file has no comments part yet it creates one (content-type override, relationship, and the part itself); if one already exists (e.g. scaffolded by docx-js) it appends to it. Write the comments as a small JSON file:
   ```json
   [
     {"id": 0, "anchor": "a short substring unique to one spot in the note", "text": "your analytical comment, citing a real source"},
     {"id": 1, "anchor": "...", "text": "..."}
   ]
   ```
   then run:
   ```
   python3 scripts/insert_comments.py mynote.docx comments.json
   ```
   **Anchor text must fall entirely within a single formatting run** — i.e. entirely inside one `**bold**` span, or entirely within a plain-text sentence with no inline markers in it. A substring straddling a bold/plain boundary won't match a single run, and the script will raise a clear error rather than silently misplacing the comment (it also errors loudly, rather than guessing, if the anchor text isn't unique in the document — pick a longer or more specific substring instead). **Only the anchor text itself is highlighted in Word**: the script splits the surrounding run into before / anchor / after pieces that keep their formatting, so a short anchor gives a short highlight. That is why the anchor should be the phrase or number the comment discusses, and it also means two comments may never share an anchor (the script refuses that as well). **The `text` field is plain text**: any inline markers in it are stripped and a count is printed — write comments without markers in the first place.
4. **Validate**:
   ```
   python3 scripts/validate_docx.py mynote.docx
   ```
   This checks the file is a well-formed zip/XML package, has the required parts, and — usefully for this workflow — that every comment anchor in `document.xml` has a matching body in `comments.xml` and vice versa. It is not a full OOXML schema validator, just a practical safety net for the mistakes this pipeline can actually introduce. Note what it does NOT check: the CONTENT of comment bodies. Only the rendered preview shows that.
5. **Render and visually spot-check** before delivering — don't just trust that validation passing means it looks right:
   ```
   bash scripts/render_preview.sh mynote.docx --comments
   ```
   (The `bash` prefix avoids depending on the script's executable bit, which does not always survive a clone or a zip round-trip. `--comments` renders the Word margin comments into the PDF margin — without it they exist in the file but are invisible in the preview, so you cannot see whether a comment landed on the sentence you meant. Drop the flag only when the file has no comments yet.)
   then actually look at a few of the resulting JPEGs (table colors, heading hierarchy, layout, and the comment balloons).
6. **Citation-count and journal-quality lookups**: Crossref API (`https://api.crossref.org/works/<DOI>`) for citation counts; Scimago (web search + fetch) for journal quartile/SJR/H-index. Use real, current data — don't estimate.
   **If a direct HTTP client (`curl`, `requests`, …) is refused, do not give up on the lookup — fetch the same URL with the agent's own web-fetch tool instead.** Many sandboxes route outbound traffic through an egress proxy that rejects raw CONNECT attempts while the agent's fetch tool is allowed through; the failure surfaces as a confusing JSON-decode error on empty output rather than as a clear network error. The same fallback applies to the Scimago lookup. If both routes fail, say so in 影响力评价 rather than estimating a number.
7. **Verify before delivering — this step is mandatory, not optional.** A note that reads fluently but misattributes a number is worse than no note, because the error is invisible at the point of use. Go back to the source PDF and check, in this order:
   - **Every page range in every heading** against the paper's real pagination. Journal page numbers (what goes in the note) are not PDF page indices (what you read) — confirm the offset once on the first page and re-derive, don't assume.
   - **Every figure that appears in the note**: sample sizes, subgroup counts, percentages, years of data collection, dates, citation count. Each must be traceable to a specific place in the paper.
   - **Author names, affiliations, journal, volume/issue, page range and DOI** in 题录信息, character by character against the paper's own front matter.
   - **Every citation inside every margin comment** — that it is a real work, that the author/year/venue are right, and that the paper itself does not already cite it (a comment framed as "the authors never engage with X" is wrong if they cite X on page 4).
   - **Where every cross-paper comparison sits, and what it rests on.** First scan the body: has a comparison with another paper slipped in? **This matters most in batch mode** — the paper you finished an hour ago is still vivid and gets written into the next note's body almost without noticing. Move any such passage into a margin comment or cut it. Then check each comment's comparisons against the three conditions in structural rule 3: real, actually known, and grounded in a stated point of contact.
   - **Every technical term and core expression** in the `English(中文)` form at every occurrence — scan headings, table cells, 影响力评价, 评述 and the margin comments, not only body paragraphs — using the paper's own English wording and one consistent Chinese rendering per term.
   - **Every comment anchor** — short and specific, sitting on the number, term or sentence the comment discusses, with no two comments sharing an anchor.
   - **Every claim attributed to the paper** that is actually your own inference. If the paper does not say it, it belongs in a hedged margin comment or in 评述, never in the body as if the authors argued it.
   Fix what the check surfaces, rebuild, and re-run validate. Then state in one line to the user what you verified — not a claim that it is perfect, but what was actually checked.
8. **Deliver** the file to the user. If there's a way to write into the same folder as the source PDF, do so under the **same filename as the literature, plus the suffix `_CN`** (e.g. `Smith2024.pdf` → `Smith2024_CN.docx`). The suffix is not optional: the English-output sibling writes `Smith2024_EN.docx` for the same paper, and without it a Chinese and an English note on one paper would overwrite each other. Notes made before this convention (skill v1.x) carry no suffix; if you find one for the same paper, tell the user rather than silently leaving an unsuffixed and a `_CN` version side by side. Check first whether that folder already has an established convention — for example existing notes sitting in a `文献总结/` subfolder rather than beside the PDFs — and follow it. If overwriting an existing note, check its current modification time first and guard the write against a conflicting concurrent edit — the user may have opened the file to leave comments since you last touched it.

## Batch mode: several papers in one request

When the user supplies more than one paper at once ("给这 10 篇都做速览笔记"), the rule is **strictly one paper at a time, start to finish, without pausing for permission between papers.**

**The protocol:**

1. Put the papers in an explicit queue and show it to the user up front (a task list if the host offers one), so they can see the order and how far along you are.
2. Take paper 1. Read it, build the note, run strip → comment → validate → render → the verification pass above, deliver the file, and report it in one or two sentences.
3. **Immediately begin paper 2. Do not wait for an instruction.** The user asked for all of them; asking "shall I continue?" after each one turns one request into ten.
4. Before reading the next paper, drop the previous paper's material from working attention — the note is already written and delivered, and nothing in paper N+1 should be informed by paper N.
5. Repeat to the end of the queue, then give one short closing summary listing the files produced and any paper that needed a judgement call (a missing DOI, an unavailable citation count, a paper whose genre changed the template).

**Why one at a time, and what goes wrong otherwise.** Reading several papers before writing any of them is the single most reliable way to produce a confidently wrong note: sample sizes, years, page ranges and findings migrate between papers, and the resulting sentence is fluent, specific and false. This failure is also hard for the user to catch, because nothing looks wrong. Sequential processing is a correctness measure, not a pacing preference — and it is what makes the body-level ban on cross-paper comparison (structural rule 3) actually hold rather than being a stylistic wish.

**Practical limits.** Each paper consumes a substantial slice of context (page images, the build script, the comment set). Because each note is verified and delivered while its paper is still fresh, later compaction of earlier papers is harmless — nothing needs to be recalled from them. Five to eight papers in one continuous conversation is comfortable; ten is workable but concentrates risk. Two things raise the risk and should lower the count: papers on closely overlapping topics (their details are the most confusable), and long papers (a 40-page paper costs about two short ones). For a long queue, prefer splitting across conversations. If the host cannot hold the whole queue, say so and deliver what fits rather than degrading quietly.

**A second kind of contamination, distinct from the first.** Mixing up numbers is a memory failure: the note says something false. Cross-paper comparison is different — the sentence may be entirely true, it is simply in the wrong place, because the previous paper was still in mind when the next note's body was written. Batch mode amplifies both, and the verification pass has to look for both: wrong figures, and correct observations that belong in a comment rather than the body.

**If a paper in the queue fails** — unreadable PDF, a scan with no text layer, a DOI that resolves to nothing — do not stop the run and do not silently skip it. Note the failure, move to the next paper, and list the failures in the closing summary.

## Reading the user's own embedded Word comments

When the user attaches a docx with their own review comments (e.g. from WPS), extract them structurally rather than guessing from a screenshot:

- Unzip; `word/comments.xml` holds each comment's text; `word/document.xml` holds `commentRangeStart`/`commentRangeEnd` markers — extract the text between them per id to see exactly what each comment is anchored to. (`scripts/validate_docx.py`'s `check_comment_consistency` function shows the regex patterns for this.)
- If a comment's instruction is itself general ("针对这一节选出3-5个地方加comments"), that's a section-level instruction, not a single-point one — plan several new comments across that section.
- If the user kept some of your prior comments and deleted others (compare anchor text against your last build), that's a signal about which of your comments they found valuable — keep the same ones (verbatim or lightly revised) in the rebuild, and don't restore ones they removed.

## Files in this skill

This skill is published as a Claude plugin marketplace, so the skill folder sits
a few levels down. The skill itself is the innermost folder — the one holding
`SKILL.md` — and is self-contained: copying just that folder installs everything.
The same plugin also carries `literature-quick-review-note-en`, the English-output
sibling: same rules, same formatting, same scripts (one CLI default differs).

```
<repository root>/
├── README.md                          — repository front page and install commands
├── LICENSE
├── .claude-plugin/marketplace.json    — makes the repo installable as a marketplace
└── plugins/lr-note/
    ├── .claude-plugin/plugin.json     — plugin manifest (name, version, author)
    ├── skills/literature-quick-review-note-en/   — English-output sibling
    └── skills/literature-quick-review-note-cn/   ← this skill folder
        ├── SKILL.md                   — this file
        ├── README.md                  — full documentation for users of the skill
        ├── CHANGELOG.md               — what changed in each version, and why
        ├── docs/example.png           — rendered screenshot of the placeholder example
        └── scripts/
            ├── docx_helpers.js        — reusable docx-js building blocks (fonts, colors, spacing, tables)
            ├── example_build.js       — complete working example; copy and adapt
            ├── example_comments.json  — sample comment file for the quickstart
            ├── strip_highlightcs.py   — WPS compatibility fix
            ├── insert_comments.py     — adds real Word margin comments, self-contained
            ├── validate_docx.py       — lightweight structural sanity check
            ├── test_scripts.py        — unit tests for the two OOXML scripts; run before/after editing them
            └── render_preview.sh      — .docx → PDF → JPEG-per-page, for visual spot-checking
```

The pipeline has been run end to end from a clean checkout (build → strip → comment → validate → render), and in batch across five real papers of different genres (empirical quantitative, practitioner report, empirical legal, scale development, foundational theory). Before publishing a release, run the same workflow in Codex if Codex compatibility is part of the release claim. The scripts do not depend on an AI vendor's internal tooling; they require only the listed external runtimes and packages.