/**
 * example_build.js
 *
 * Minimal end-to-end example of building a literature quick-overview note
 * (English output) with docx_helpers.js. Copy this file, replace the
 * placeholder content with real content distilled from the paper you're
 * reading, and run:
 *
 *   node example_build.js
 *
 * Requires: npm install docx   (run once, in this folder or a parent with
 * node_modules on the require path)
 */

const { Document, Packer, Paragraph, Table, WidthType } = require("docx");
const fs = require("fs");
const {
  P, Quote, BulletP, H, TitleLine, cellP, bibRow, themeRow, gridRow, TABLE_BORDERS, defaultStyles, FONT, BODY_SIZE, NOTE_SIZE, COLOR,
} = require("./docx_helpers");
const { TextRun } = require("docx");

// ---- Bibliographic Information --------------------------------------------

const authorValue = [
  cellP([new TextRun({ text: "· Author One (first author; conceptualization, methodology, data collection, analysis, original draft)", font: FONT, size: BODY_SIZE })]),
  cellP([new TextRun({ text: "· Author Two (corresponding author; supervision, review & editing)", font: FONT, size: BODY_SIZE })]),
  cellP([new TextRun({
    text: "Note: both authors are affiliated with Example University.",
    font: FONT, size: NOTE_SIZE, color: COLOR.GRAY,
  })]),
];

const bibRows = [
  ["Title", [
    cellP([new TextRun({ text: "Example Paper Title: A Study of Something Important", font: FONT, size: BODY_SIZE })]),
  ]],
  ["Authors", authorValue],
  ["Publication year", "2025"],
  ["Journal", "Author One, A. and Author Two, B. (2025) 'Example Paper Title', Journal of Examples, 1(1), pp. 1-20."],
  ["DOI", "10.0000/example.doi"],
  ["Field(s)", "Example field one, example field two, example field three."],
  ["Paper type", "Empirical, qualitative research article."],
  ["Theoretical framework", "Example Theory (Someone, 2000)."],
];

const themeRows = [
  ["Theme name", "Description", true],
  ["Example theme one", "Brief description of example theme one.", false],
  ["Example theme two", "Brief description of example theme two.", false],
];

// gridRow handles any number of columns — the first row here is the header.
const gridRows = [
  ["Dimension", "Example Group A", "Example Group B"],
  ["Sample size", "n = 16", "n = 11"],
  ["Employment status", "Mostly unemployed", "Mostly employed"],
];

const children = [];

children.push(TitleLine("Literature Summary: Example Paper — one-sentence summary of the core issue (pp. 1–20)"));

children.push(H("Bibliographic Information (p. 1)", 2));
children.push(new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, borders: TABLE_BORDERS, rows: bibRows.map(([l, v]) => bibRow(l, v)) }));
children.push(new Paragraph({ text: "", spacing: { after: 160 } }));

children.push(H("Impact Assessment", 2));
children.push(P("Citation performance: per Crossref, approximately N citations to date."));
children.push(P("Publication venue: journal profile and Scimago quartile information. ==This sentence can be the single highlighted takeaway for the whole document.=="));

children.push(H("1. Background and Research Questions (pp. 1–5)", 2));
children.push(H("1.1 Subheading (pp. 1–3)", 3));
children.push(P("**Core argument: one-sentence summary.** One to two sentences of elaboration, distilled from the original content rather than translated sentence by sentence. Only three inline markers are available: **bold**, *italic* (for terms or journal titles), and ==highlight==."));

children.push(H("2. Methods (pp. 5–8)", 2));
children.push(P("**Research design: name of the method.** Briefly explain why this method was chosen, along with the sample and data-collection approach."));

children.push(H("3. Findings (pp. 8–14)", 2));
children.push(P("The data yielded N themes; the definitions from the original Table X are reproduced below:"));
children.push(new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, borders: TABLE_BORDERS, rows: themeRows.map(([n, d, h]) => themeRow(n, d, h)) }));
children.push(new Paragraph({ text: "", spacing: { after: 160 } }));
children.push(H("3.1 Example theme one (pp. 8–10)", 3));
children.push(P("**Core mechanism: one-sentence summary of the mechanism.** One to two sentences of elaboration. Cap direct quotes at one for the entire document, set with Quote() as an indented block quote:"));
children.push(Quote("\"This is the one direct quote in the entire document, used only where a paraphrase would lose the force of the original wording.\" (Participant ID, identity label)"));

children.push(H("3.2 Multi-column comparison table (pp. 10–14)", 3));
children.push(P("When the content is itself comparative (two samples, multiple theories), use gridRow() to lay out a table with any number of columns:"));
children.push(new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  borders: TABLE_BORDERS,
  rows: gridRows.map((cells, i) => gridRow(cells, { header: i === 0 })),
}));
children.push(new Paragraph({ text: "", spacing: { after: 160 } }));

children.push(H("6. Critical Assessment & Citable Points", 2));
children.push(H("Key contributions", 3));
children.push(BulletP("Brief note on contribution one."));
children.push(BulletP("Brief note on contribution two."));
children.push(H("Limitations & citation caveats", 3));
children.push(BulletP("Brief note on limitation one."));

const doc = new Document({
  sections: [
    { properties: { page: { size: { width: 11906, height: 16838 } } }, children },
  ],
  styles: defaultStyles(),
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("example_note.docx", buf);
  console.log("saved example_note.docx");
});
