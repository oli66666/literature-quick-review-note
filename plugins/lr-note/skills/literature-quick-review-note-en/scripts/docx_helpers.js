/**
 * docx_helpers.js
 *
 * Reusable building blocks for a "literature quick-overview note" (文献速览笔记),
 * built on the `docx` npm package (docx-js). Require this from your own build
 * script instead of re-implementing paragraph/table formatting every time.
 *
 * Usage:
 *   const { P, BulletP, H, TitleLine, bibRow, themeRow, TABLE_BORDERS, FONT, COLOR }
 *     = require("./docx_helpers");
 *
 * See example_build.js in this same folder for a complete working document.
 */

const {
  Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, AlignmentType, ShadingType, BorderStyle,
} = require("docx");

// ---------------------------------------------------------------------------
// House-style constants (see SKILL.md "Visual formatting" for the rationale
// behind each value — these were reverse-engineered from a real reference
// note's underlying XML, not eyeballed from a screenshot).
// ---------------------------------------------------------------------------

const COLOR = {
  H12: "1F3864",   // Heading 1 / Heading 2 text color (dark navy)
  H3: "2E5496",    // Heading 3 text color (medium navy)
  GRAY: "808080",  // muted/secondary text (translated subtitle, affiliation note)
  BODY: "1A1A1A",  // default body text color (near-black, not pure #000)
};

const FILL_BLUE = "EDF2F9";   // table label/left-column shading
const FILL_HEADER = "1F3864"; // dark header row shading for a reproduced original-paper table

const FONT = {
  ascii: "Times New Roman",
  hAnsi: "Times New Roman",
  cs: "Times New Roman",
  eastAsia: "宋体", // SimSun
};

const BODY_SIZE = 21; // half-points = 10.5pt
const NOTE_SIZE = 18; // half-points = 9pt (affiliation "Note:" line)

const TABLE_BORDERS = {
  top: { style: BorderStyle.SINGLE, size: 4, color: "A6A6A6" },
  bottom: { style: BorderStyle.SINGLE, size: 4, color: "A6A6A6" },
  left: { style: BorderStyle.SINGLE, size: 4, color: "A6A6A6" },
  right: { style: BorderStyle.SINGLE, size: 4, color: "A6A6A6" },
  insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: "D0D0D0" },
  insideVertical: { style: BorderStyle.SINGLE, size: 2, color: "D0D0D0" },
};

// ---------------------------------------------------------------------------
// Inline markdown-lite: **bold**, *italic* and ==highlight==
//
// The alternation order below matters: `**bold**` is tried before `*italic*`,
// so a double-asterisk span is never mis-read as an italic span wrapping a
// stray asterisk. There is no marker for underline or strikethrough.
//
// Caveat: a single unmatched `*` in the text is left alone (it needs a closing
// `*` to pair with), but two unrelated lone asterisks in the SAME string will
// pair up and italicise everything between them. If a note must contain
// literal asterisks (e.g. a significance marker like `p < .05*`), keep them in
// separate strings or rephrase.
// ---------------------------------------------------------------------------

function parseRuns(text, extra = {}) {
  const runs = [];
  const re = /\*\*(.+?)\*\*|==(.+?)==|\*(.+?)\*/g;
  let last = 0;
  let m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) {
      runs.push(new TextRun({ text: text.slice(last, m.index), font: FONT, size: BODY_SIZE, ...extra }));
    }
    if (m[1] !== undefined) {
      runs.push(new TextRun({ text: m[1], bold: true, font: FONT, size: BODY_SIZE, ...extra }));
    } else if (m[2] !== undefined) {
      runs.push(new TextRun({ text: m[2], bold: true, highlight: "yellow", font: FONT, size: BODY_SIZE, ...extra }));
    } else if (m[3] !== undefined) {
      runs.push(new TextRun({ text: m[3], italics: true, font: FONT, size: BODY_SIZE, ...extra }));
    }
    last = re.lastIndex;
  }
  if (last < text.length) {
    runs.push(new TextRun({ text: text.slice(last), font: FONT, size: BODY_SIZE, ...extra }));
  }
  return runs;
}

// ---------------------------------------------------------------------------
// Paragraph-level helpers
// ---------------------------------------------------------------------------

function P(text, opts = {}) {
  return new Paragraph({
    children: parseRuns(text),
    alignment: AlignmentType.JUSTIFIED,
    spacing: { before: 60, after: 120, line: 320 },
    ...opts,
  });
}

function Quote(text) {
  return new Paragraph({
    children: parseRuns(text),
    alignment: AlignmentType.JUSTIFIED,
    spacing: { before: 60, after: 120, line: 320 },
    indent: { left: 480, right: 480 },
  });
}

function BulletP(text) {
  return new Paragraph({
    children: parseRuns(text),
    alignment: AlignmentType.JUSTIFIED,
    spacing: { before: 40, after: 80, line: 320 },
    bullet: { level: 0 },
  });
}

// level: 1 = document title, 2 = major section, 3 = subsection
function H(text, level) {
  const color = level === 1 || level === 2 ? COLOR.H12 : COLOR.H3;
  const headingLevel =
    level === 1 ? HeadingLevel.HEADING_1 : level === 2 ? HeadingLevel.HEADING_2 : HeadingLevel.HEADING_3;
  const spacing = level === 2 ? { before: 320, after: 140 } : { before: 200, after: 100 };
  return new Paragraph({
    heading: headingLevel,
    spacing,
    children: [new TextRun({ text, bold: true, color, font: FONT })],
  });
}

function TitleLine(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 0, after: 240 },
    children: [new TextRun({ text, bold: true, color: COLOR.H12, size: 32, font: FONT })],
  });
}

// ---------------------------------------------------------------------------
// Table helpers
// ---------------------------------------------------------------------------

function cellP(children) {
  return new Paragraph({
    children,
    alignment: AlignmentType.LEFT,
    spacing: { before: 20, after: 20, line: 280 },
  });
}

// bibRow(label, value): value is either a plain string (split on \n into
// paragraphs) or an array of Paragraph objects for custom layout (e.g. a
// bulleted author list — see example_build.js).
function bibRow(label, value) {
  const valueChildren = Array.isArray(value)
    ? value
    : value.split("\n").map((line) => cellP(parseRuns(line)));
  return new TableRow({
    children: [
      new TableCell({
        width: { size: 18, type: WidthType.PERCENTAGE },
        shading: { type: ShadingType.CLEAR, fill: FILL_BLUE },
        children: [cellP([new TextRun({ text: label, bold: true, font: FONT, size: BODY_SIZE })])],
      }),
      new TableCell({
        width: { size: 82, type: WidthType.PERCENTAGE },
        children: valueChildren,
      }),
    ],
  });
}

// themeRow: for reproducing a paper's own summary table (e.g. a themes/
// constructs table). Pass header=true for the header row.
function themeRow(name, desc, header) {
  return new TableRow({
    children: [
      new TableCell({
        width: { size: 28, type: WidthType.PERCENTAGE },
        shading: { type: ShadingType.CLEAR, fill: header ? FILL_HEADER : FILL_BLUE },
        children: [cellP([new TextRun({ text: name, bold: true, color: header ? "FFFFFF" : undefined, font: FONT, size: BODY_SIZE })])],
      }),
      new TableCell({
        width: { size: 72, type: WidthType.PERCENTAGE },
        shading: { type: ShadingType.CLEAR, fill: header ? FILL_HEADER : "FFFFFF" },
        children: [cellP([new TextRun({ text: desc, bold: !!header, color: header ? "FFFFFF" : undefined, font: FONT, size: BODY_SIZE })])],
      }),
    ],
  });
}

// gridRow: a row of ANY number of columns — use this for comparison tables the
// paper itself does not provide (e.g. "维度 | 样本A | 样本B", or
// "理论 | 原有前提 | 失效点"). `themeRow` above is the fixed 2-column special
// case kept for backwards compatibility; prefer `gridRow` for everything else.
//
//   cells    array of cell strings; each is run through parseRuns(), so
//            **bold** / *italic* / ==highlight== work inside a cell.
//   opts.header      true for the table's header row: dark fill, white bold text.
//   opts.labelFirst  default true — shade the first column like a label column
//                    (light blue, bold). Pass false for an all-plain grid.
//   opts.widths      array of column width percentages, same length as `cells`.
//                    Omit to auto-size: with labelFirst, the first column takes
//                    ~20% and the rest split the remainder evenly; otherwise all
//                    columns are equal.
//
// Example:
//   const rows = [
//     ["维度", "样本 A", "样本 B"],
//     ["就业状况", "失业 11、在业 5", "失业 1、在业 10"],
//   ];
//   new Table({
//     width: { size: 100, type: WidthType.PERCENTAGE },
//     borders: TABLE_BORDERS,
//     rows: rows.map((cells, i) => gridRow(cells, { header: i === 0 })),
//   });
function gridRow(cells, opts = {}) {
  const { header = false, labelFirst = true, widths = null } = opts;
  const n = cells.length;

  let cols = widths;
  if (!cols) {
    if (labelFirst && n > 1) {
      const first = 20;
      const rest = (100 - first) / (n - 1);
      cols = [first, ...Array(n - 1).fill(rest)];
    } else {
      cols = Array(n).fill(100 / n);
    }
  }

  return new TableRow({
    children: cells.map((text, i) => {
      const isLabel = header || (labelFirst && i === 0);
      const fill = header ? FILL_HEADER : (labelFirst && i === 0 ? FILL_BLUE : "FFFFFF");
      return new TableCell({
        width: { size: cols[i], type: WidthType.PERCENTAGE },
        shading: { type: ShadingType.CLEAR, fill },
        children: [cellP(parseRuns(String(text), {
          bold: isLabel ? true : undefined,
          color: header ? "FFFFFF" : undefined,
        }))],
      });
    }),
  });
}

// Document-level default styles — pass as the `styles` option of `new Document({...})`.
function defaultStyles() {
  return {
    default: {
      document: {
        run: { font: FONT, size: 22, color: COLOR.BODY },
      },
    },
  };
}

module.exports = {
  COLOR, FILL_BLUE, FILL_HEADER, FONT, BODY_SIZE, NOTE_SIZE, TABLE_BORDERS,
  parseRuns, P, Quote, BulletP, H, TitleLine, cellP, bibRow, themeRow, gridRow, defaultStyles,
};
