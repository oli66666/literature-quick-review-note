# literature-quick-review-note

A skill for Claude (and Codex) that turns an academic paper into a condensed
Chinese reading note (文献速览笔记) as a WPS-compatible Word file, with real
anchored Word margin comments.

This repository is packaged as a Claude plugin marketplace, so it can be
installed with one command. The skill itself, with its full documentation,
lives in
[`plugins/lr-note/skills/literature-quick-review-note/`](plugins/lr-note/skills/literature-quick-review-note/)
— start with [its README](plugins/lr-note/skills/literature-quick-review-note/README.md).

![Example output](plugins/lr-note/skills/literature-quick-review-note/docs/example.png)

*Placeholder content — no real paper is involved.*

## Install

In Claude Code:

```
/plugin install lr-note@oli66666/literature-quick-review-note
```

The skill is then invoked as `/lr-note:literature-quick-review-note`, or simply by
asking for a 速览笔记 with a paper attached.

Prefer to install it by hand, or not using a host that supports plugins? Copy the
skill folder — the innermost one, containing `SKILL.md` — into `~/.claude/skills/`.
Copy the **whole folder**, not just `SKILL.md`: the Python scripts that write the
margin comments live in its `scripts/` subfolder and the skill cannot produce
comments without them.

## Requirements

Node.js with the `docx` package, Python 3.8+, and — only for the optional visual
check — LibreOffice and Poppler. No API key, no bundled paper, no personal paths.

## License

MIT. See [`LICENSE`](LICENSE). Copyright (c) 2026 Oli L.
