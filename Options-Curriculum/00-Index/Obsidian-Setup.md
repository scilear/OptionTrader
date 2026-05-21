---
title: Obsidian Vault Setup Guide
tags: [meta, setup]
aliases: [Obsidian-Setup]
status: meta
related: [[Progress-Dashboard]]
---

# Obsidian Vault Setup Guide

This is a **meta note** for curriculum builders. Students do not need to read or configure these settings.

Before starting curriculum development, configure Obsidian with the plugins, settings, and view configurations listed below. This ensures that live queries, templates, and graph views work as intended throughout the vault.

---

## Core Plugins (Enable in Settings → Core plugins)

Enable the following built-in plugins:

| Plugin | Reason |
|--------|--------|
| **Templates** | Required for template folder and note generation workflow. Provides "Insert template" command. |
| **Search** | Essential for vault-wide search. Used during review and linking. |
| **Backlinks** | Shows all notes linking to the current note. Critical for curriculum coherence. |
| **Outgoing links** | Lists all links in the current note. Helps spot gaps and unlinked concepts. |
| **Tag pane** | Displays all tags in the vault. Useful for filtering by status (`status:draft`, `status:complete`, etc.) or topic. |
| **Word count** | Shows word count in status bar. Optional, but useful for curriculum sizing. |

---

## Community Plugins (Install via Settings → Community plugins)

### 1. Dataview
**Location in Community plugins:** Search for "Dataview" → install by Michael Brenan

**After install:**
- Open Settings → Community plugins → Dataview
- Enable "Enable JavaScript Queries" (required for `[[Progress-Dashboard]]` live queries)
- Enable "Enable Inline Queries" if using inline metrics

**Why:** Dataview powers the Progress Dashboard, which tracks curriculum completion across multiple dimensions (concept depth, playbook coverage, quiz readiness).

---

### 2. Templater
**Location in Community plugins:** Search for "Templater" → install by SilentVoid13

**After install:**
- Open Settings → Community plugins → Templater
- Set "Template folder location" to `Templates`
- Enable "Trigger Templater on new file creation"
- (Optional) Enable "Auto jump to cursor" to position cursor after template insertion

**Why:** Templater provides template variables (title, date, tags) and scripting for automated note generation. The vault includes standard templates in the Templates/ folder:
- `Strategy-Note-Template`
- `Concept-Note-Template`
- `Playbook-Note-Template`
- `Paper-Trade-Journal-Template`

---

### 3. Better Word Count (Optional)
**Location in Community plugins:** Search for "Better Word Count" → install by lynchjames

**After install:**
- Open Settings → Community plugins → Better Word Count
- No required configuration; word count appears in status bar

**Why:** Useful for tracking section lengths and ensuring notes stay concise (recommended: 200–500 words for concept notes, 800–1200 for playbooks).

---

## Graph View Configuration

The graph view is a powerful way to visualize curriculum structure and spot orphaned or under-linked concepts.

**Setup steps:**

1. Open Graph View: **Cmd+G** (Mac) or **Ctrl+G** (Windows/Linux)
2. Click the **gear icon** (lower left) to open graph settings
3. In the **Groups** section, add the following groups and colors:

| Filter | Color | Purpose |
|--------|-------|---------|
| `tag:#meta` | Gray | Meta notes (setup, index, progress tracking) |
| `status:complete` | Green | Finished sections; stable for linking |
| `status:draft` | Orange | Work-in-progress sections; may change |
| `status:stub` | Red | Placeholder stubs; needs content |

4. In **Display** options:
   - Set "Show orphans" to **off** (hides notes with no links; less visual clutter)
   - Enable "Show arrows" for link direction clarity
   - Adjust "Link distance" to 2–3 for readable clustering

**Use case:** Run the graph view weekly to identify notes that are:
- Disconnected from the curriculum (true orphans, often deletable)
- Isolated from their peer concepts (may need new links)
- Part of sparse clusters (may need cross-topic bridges)

---

## Linking Settings

Configure how Obsidian handles note locations and links.

**Settings → Files & Links:**
- **"Default location for new notes":** Set to the appropriate folder
  - For concept notes: `01-Foundations`, `02-Intermediate`, `03-Advanced`
  - For playbooks: `04-Playbooks`
  - For quizzes: `05-Quizzes`
  - For templates: `Templates`

- **"Use [[Wikilinks]]":** Enable (should be on by default). This ensures all cross-vault links use the `[[Note Title]]` format.

- **"Automatically update internal links":** **Disable this.** Bulk note generation can cause automatic link rewrites, which may corrupt custom links. Manage renames manually.

- **"New note filename format":** Leave as default (note title). Custom formats can break template generation.

---

## Templates Folder

The vault includes a `Templates/` folder with four standard templates. Builders extend these as needed.

**Settings → Templates:**
- Set **"Template folder location"** to `Templates`

**Standard templates included:**
- `[[Strategy-Note-Template]]` — For trading strategies (edge, regime filter, entry/exit rules, position sizing)
- `[[Concept-Note-Template]]` — For theoretical concepts (Greeks, volatility, implied vs realized)
- `[[Playbook-Note-Template]]` — For structured trade ideas (watch list, setup checklist, trade journal)
- `[[Paper-Trade-Journal-Template]]` — For mock trading entries (entry, exit, P&L, reflection)

**To insert a template:**
1. Create a new note (Cmd+N or Ctrl+N)
2. Open Command Palette (Cmd+P or Ctrl+P)
3. Type "Templater: Open Insert Template modal"
4. Select the desired template

Templates auto-fill the title, date, and frontmatter tags; customize content after insertion.

---

## Reading vs Editing Mode

Obsidian offers two note views: **Editing mode** (markdown source) and **Reading mode** (rendered HTML).

**Recommendation:**
- **Default to Reading mode** for finished notes (`status: complete`). This is cleaner for students and reduces accidental edits.
- **Use Live Preview mode** (default when editing). Split-pane editors can show both source and preview simultaneously.
- Toggle with **Cmd+E** (Mac) or **Ctrl+E** (Windows/Linux)

**Tip:** For long curriculum notes, use Reading mode to spot formatting issues and ensure proper heading hierarchy.

---

## Useful Hotkeys

Keep these shortcuts handy during curriculum development:

| Action | Mac | Windows/Linux |
|--------|-----|---------------|
| New note | Cmd+N | Ctrl+N |
| Command palette | Cmd+P | Ctrl+P |
| Toggle edit/preview | Cmd+E | Ctrl+E |
| Open graph view | Cmd+G | Ctrl+G |
| Open backlinks pane | Cmd+\ | Ctrl+\ |
| Search vault | Cmd+F | Ctrl+F |
| Quick switcher | Cmd+O | Ctrl+O |
| Insert template | (via Command Palette) | (via Command Palette) |
| Pin pane | Click pin icon in pane header | Click pin icon in pane header |

---

## Callout Style Reference

The curriculum uses four standardized callout types. Use them consistently for student safety and clarity.

```markdown
> [!warning]
> Financial risk of loss — explains downside, margin calls, or max loss scenarios.

> [!danger]
> Unsuitable for beginners — advanced concepts or strategies beyond the target audience.

> [!tip]
> Best practice — actionable guidance, backtesting evidence, or proven techniques.

> [!note]
> Definition or context — supporting information, formula, or historical background.
```

**Example usage:**

```markdown
> [!warning]
> Selling naked calls is exposed to unlimited loss if the underlying rallies past your strike.

> [!tip]
> Always pair skew-selling trades with VIX > 20 to ensure regime-appropriate setup.

> [!note]
> Implied volatility (IV) is the market's estimate of future realized volatility, priced into option premiums.

> [!danger]
> Do not attempt calendar spreads until you understand theta decay curves and VIX term structure.
```

---

## Setup Checklist

- [ ] Enable all Core plugins listed above
- [ ] Install Dataview and enable JavaScript queries
- [ ] Install Templater and set template folder to `Templates`
- [ ] (Optional) Install Better Word Count
- [ ] Configure graph view groups (meta, draft, complete, stub)
- [ ] Disable "Automatically update internal links" in Settings → Files & Links
- [ ] Verify [[Templates/Strategy-Note-Template]] and other templates are present
- [ ] Test note creation: create a new note, insert a template, verify frontmatter is populated
- [ ] Open [[Progress-Dashboard]] and verify Dataview queries render

---

## Next Steps

Once setup is complete, open **[[Progress-Dashboard]]** to track curriculum build progress. The dashboard displays:
- Total notes by status (complete, draft, stub)
- Coverage by section (Foundations, Intermediate, Advanced, Playbooks)
- Orphaned notes and linking gaps
- Estimated reading time per section

Happy building!
