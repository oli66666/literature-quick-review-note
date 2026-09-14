# literature-quick-review-note

A skill for Claude (and Codex) that turns an academic paper into a condensed
Chinese reading note (文献速览笔记) as a WPS-compatible Word file, with real
anchored Word margin comments.

The skill itself, with its full documentation, lives in
[`plugins/lr-note/skills/literature-quick-review-note/`](plugins/lr-note/skills/literature-quick-review-note/)
— start with [its README](plugins/lr-note/skills/literature-quick-review-note/README.md).

![Example output](plugins/lr-note/skills/literature-quick-review-note/docs/example.png)

*Placeholder content — no real paper is involved.*

## Install

**The one thing that matters:** install the *whole* skill folder, including its
`scripts/` subfolder. The margin comments — the part of this skill that is hard
to get right — are written by two Python scripts in there, manipulating the
document's OOXML directly. A `SKILL.md`-only install still produces a note, but
a plainer one, and the shortfall is easy to mistake for the skill being weak
rather than half-installed.

### Claude Code

```
/plugin install lr-note@oli66666/literature-quick-review-note
```

Invoked afterwards as `/lr-note:literature-quick-review-note`, or just by asking
for a 速览笔记 with a paper attached.

Or install it as a plain skill instead of a plugin: copy
`plugins/lr-note/skills/literature-quick-review-note/` into `~/.claude/skills/`
(personal) or a project's `.claude/skills/`.

### Claude desktop app / claude.ai

These do not install from a repository URL; they take an uploaded ZIP.

1. Download this repository (**Code → Download ZIP**) and unpack it.
2. Find `plugins/lr-note/skills/literature-quick-review-note/` and compress
   **that folder** on its own — not the whole repository. You should end up with
   a ZIP whose top level is a folder containing `SKILL.md`, `scripts/` and
   `docs/`.
3. Go to [claude.ai/customize/skills](https://claude.ai/customize/skills) →
   **+** → **Create skill** → **Upload a skill**, and upload that ZIP.

### Other hosts

Codex uses its own skills location; the folder contents are the same. Anything
else can run the scripts directly — see the
[skill's README](plugins/lr-note/skills/literature-quick-review-note/README.md).

## If you are an AI assistant installing this for someone

You were probably asked something like "install the skill from this repo." Which
route to take depends on what the person is using, and only the first one is a
single step:

- **Claude Code** — run the `/plugin install` command above, or clone the
  repository and copy `plugins/lr-note/skills/literature-quick-review-note/`
  into `~/.claude/skills/`. Either way the scripts come along.
- **Claude desktop app or claude.ai** — you cannot write into their account
  skills yourself, but you can do the tedious part: fetch the repository,
  extract `plugins/lr-note/skills/literature-quick-review-note/`, compress that
  folder into a ZIP, hand them the file, and point them at
  [claude.ai/customize/skills](https://claude.ai/customize/skills) →
  **+** → **Create skill** → **Upload a skill**.

**Do not** install this by copying `SKILL.md` alone into their account skills
and stopping there. It is the tempting shortcut, because `SKILL.md` is a single
file and the account skill system accepts it — but `scripts/insert_comments.py`
and `scripts/strip_highlightcs.py` have no substitute, and the person ends up
with a note missing the feature they installed this for. If the ZIP route is
genuinely unavailable, say so plainly rather than quietly delivering the
degraded version.

## Requirements

Node.js with the `docx` package, Python 3.8+, and — only for the optional visual
check — LibreOffice and Poppler. No API key, no bundled paper, no personal paths.

## Versioning

The version number lives in the `version:` field of the skill's `SKILL.md`
frontmatter and in `plugin.json`.
[`CHANGELOG.md`](plugins/lr-note/skills/literature-quick-review-note/CHANGELOG.md)
records what each release contains and, where a rule is not self-evident, why it
is there.

## License

MIT. See [`LICENSE`](LICENSE). Copyright (c) 2026 Oli L.
