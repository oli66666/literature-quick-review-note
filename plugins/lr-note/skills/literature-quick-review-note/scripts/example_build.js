/**
 * example_build.js
 *
 * Minimal end-to-end example of building a literature quick-overview note
 * with docx_helpers.js. Copy this file, replace the placeholder content with
 * real content distilled from the paper you're reading, and run:
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

// ---- 题录信息 -------------------------------------------------------------

const authorValue = [
  cellP([new TextRun({ text: "· Author One(第一作者;概念化、方法设计、资料收集、分析、初稿撰写)", font: FONT, size: BODY_SIZE })]),
  cellP([new TextRun({ text: "· Author Two(通讯作者;督导、审阅与修订)", font: FONT, size: BODY_SIZE })]),
  cellP([new TextRun({
    text: "Note:均任职于示例大学(Example University)。",
    font: FONT, size: NOTE_SIZE, color: COLOR.GRAY,
  })]),
];

const bibRows = [
  ["标题", [
    cellP([new TextRun({ text: "Example Paper Title: A Study of Something Important", font: FONT, size: BODY_SIZE })]),
    cellP([new TextRun({ text: "(示例论文标题:一项重要议题的研究)", font: FONT, size: BODY_SIZE, color: COLOR.GRAY })]),
  ]],
  ["作者", authorValue],
  ["发表年份", "2025"],
  ["发表期刊", "Author One, A. and Author Two, B. (2025) 'Example Paper Title', Journal of Examples, 1(1), pp. 1-20."],
  ["DOI", "10.0000/example.doi"],
  ["所属领域", "示例领域一(example field one)、示例领域二(example field two)、示例领域三(example field three)。"],
  ["论文类型", "Empirical, qualitative research article."],
  ["理论框架", "示例理论(Example Theory; Someone, 2000)。"],
];

const themeRows = [
  ["主题名称", "描述", true],
  ["示例主题一", "对示例主题一的简要描述。", false],
  ["示例主题二", "对示例主题二的简要描述。", false],
];

// gridRow handles any number of columns — the first row here is the header.
const gridRows = [
  ["维度", "示例组 A", "示例组 B"],
  ["样本量", "n = 16", "n = 11"],
  ["就业状况", "失业为主", "在业为主"],
];

const children = [];

children.push(TitleLine("文献总结:示例论文 — 一句话概括核心议题(原文 pp.1–20)"));

children.push(H("题录信息(原文 p.1)", 2));
children.push(new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, borders: TABLE_BORDERS, rows: bibRows.map(([l, v]) => bibRow(l, v)) }));
children.push(new Paragraph({ text: "", spacing: { after: 160 } }));

children.push(H("影响力评价", 2));
children.push(P("引用表现: 据 Crossref 统计,截至目前约获 N 次引用。"));
children.push(P("发表平台: 期刊简介与 Scimago 分区信息。==这一句可以是全文唯一的高亮重点。=="));

children.push(H("一、研究背景与研究问题(原文 pp.1–5)", 2));
children.push(H("1.1 子标题(原文 pp.1–3)", 3));
children.push(P("**核心论点:一句话概括。** 一到两句话的展开说明,基于原文内容进行提炼,而不是逐句翻译。行内可用的标记只有三种:**加粗**、*斜体*(用于术语或期刊名)、==高亮==。"));

children.push(H("二、研究方法(原文 pp.5–8)", 2));
children.push(P("**研究设计:方法名称。** 简要说明为何采用该方法、样本与数据收集方式。"));

children.push(H("三、研究发现(原文 pp.8–14)", 2));
children.push(P("数据共生成 N 个主题,原文表 X 的界定复制如下:"));
children.push(new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, borders: TABLE_BORDERS, rows: themeRows.map(([n, d, h]) => themeRow(n, d, h)) }));
children.push(new Paragraph({ text: "", spacing: { after: 160 } }));
children.push(H("3.1 示例主题一(原文 pp.8–10)", 3));
children.push(P("**核心机制:一句话概括机制。** 一到两句话展开。全文至多保留一条直接引用,用 Quote() 排成缩进引文块:"));
children.push(Quote("「这里是全文唯一的一条直接引用,只在转述会损失原话力量时才使用。」(受访者代号,身份标签)"));

children.push(H("3.2 多列对照表(原文 pp.10–14)", 3));
children.push(P("当内容本身是比较性的(两组样本、多个理论),用 gridRow() 排任意列数的表:"));
children.push(new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  borders: TABLE_BORDERS,
  rows: gridRows.map((cells, i) => gridRow(cells, { header: i === 0 })),
}));
children.push(new Paragraph({ text: "", spacing: { after: 160 } }));

children.push(H("六、评述与可引用点", 2));
children.push(H("主要贡献", 3));
children.push(BulletP("贡献一的简要说明。"));
children.push(BulletP("贡献二的简要说明。"));
children.push(H("局限与引用时的注意", 3));
children.push(BulletP("局限一的简要说明。"));

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
