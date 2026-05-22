---
title: Progress Dashboard
tags: [meta, dashboard]
aliases: []
status: meta
related: ["[[Obsidian-Setup]]", "[[WikiLink-Map]]"]
---

# Progress Dashboard

> Requires Dataview plugin — see [[Obsidian-Setup]].

---

## Incomplete Notes

```dataview
TABLE status, tags
FROM ""
WHERE status != "complete"
SORT status ASC
```

---

## Progress Summary

```dataviewjs
const pages = dv.pages('""');
const total = pages.length;
const complete = pages.filter(p => p.status === "complete").length;
const draft = pages.filter(p => p.status === "draft").length;
const stub = pages.filter(p => p.status === "stub").length;
const meta = pages.filter(p => p.status === "meta").length;
const other = total - complete - draft - stub - meta;

const barWidth = 30;
const filled = Math.round((complete / total) * barWidth);
const bar = "█".repeat(filled) + "░".repeat(barWidth - filled);

dv.paragraph(`**Progress:** [${bar}] ${complete}/${total} complete`);
dv.paragraph(
  `Complete: **${complete}** | Draft: **${draft}** | Stub: **${stub}** | Meta: **${meta}** | Other: **${other}**`
);
```

---

## Notes Missing `related` Field

```dataview
LIST
FROM ""
WHERE !related
SORT file.name ASC
```

---

## Chart Script Status

These Python scripts live outside the Obsidian vault and have no frontmatter — track them manually.

| Script | Status |
|---|---|
| `pnl_diagrams.py` | ☐ |
| `iv_charts.py` | ☐ |
| `timing_charts.py` | ☐ |
| `risk_charts.py` | ☐ |
| `earnings_charts.py` | ☐ |
