# RegimeSignal Integration Template — How It Works

**Created:** April 19, 2026
**Purpose:** One source of truth for how data flows from Kip's Python pipeline to every RegimeSignal web page.

---

## The One-Sentence Summary

**Python writes `regimesignal_data.json`. Every page reads from it. Adding a new page means adding new fields to the JSON — not rebuilding the integration.**

---

## The Architecture (data flow)

```
 ┌──────────────────────┐
 │  12 Data Sources     │   (Bloomberg, FRED, etc. — existing)
 └──────────┬───────────┘
            ↓
 ┌──────────────────────┐
 │  Python Pipeline     │   (Kip's existing model)
 │  25 factors → MRS    │
 │  25 factors → RTS    │
 └──────────┬───────────┘
            ↓
 ┌──────────────────────┐
 │  regimesignal_       │   ← THE CONTRACT (this file)
 │  writer.py           │     Python calls write_payload()
 └──────────┬───────────┘
            ↓
 ┌──────────────────────┐
 │  regimesignal_       │   ← Single source of truth
 │  data.json           │     (written atomically every run)
 └──────────┬───────────┘
            ↓ (fetched by loader)
 ┌──────────────────────┐
 │  regimesignal_       │   ← JS loader in every page
 │  loader.js           │     Finds data-rs="..." attributes
 └──────────┬───────────┘     and populates them automatically
            ↓
 ┌──────────────────────┐
 │  MRS Terminal        │
 │  MRS Risk DNA        │   ← Every page inherits the data
 │  RTS Terminal        │     No hardcoded values.
 │  RTS Risk DNA        │
 │  + any future page   │
 └──────────────────────┘
```

---

## The Three Files That Matter

### 1. `regimesignal_data.json` — the contract
The single source of truth. Lists every data field the pages need. When Python finishes a run, it overwrites this file. When a user loads any page, the JS loader fetches this file and populates the page.

**Anything that shows a number, label, or value on ANY page should be a field in this JSON.**

### 2. `regimesignal_loader.js` — the reader
Drop this `<script>` tag into any page. It does three things:
- Fetches `regimesignal_data.json`
- Finds every element with a `data-rs="path"` attribute
- Replaces the element's text with the value at that path in the JSON

No per-page code needed. No template engine. No build step. Just HTML attributes.

### 3. `regimesignal_writer.py` — the contract from Python's side
Python imports this module and calls `write_payload(...)` at the end of every model run. The writer validates the structure and writes atomically (no half-written files).

**Kip's real model replaces the stub `compute_*` calls but keeps the structure.**

---

## How to Use in Pages (data-rs attributes)

### Simple value binding
```html
<span data-rs="rts.composite">—</span>
<span data-rs="mrs.composite" data-rs-decimals="1">—</span>
```
The `—` is a fallback shown if the JSON fails to load. The loader replaces it with the actual value.

### Signed numbers (shows + or −)
```html
<span data-rs="rts.change_30d" data-rs-signed="true">—</span>
```
Displays `+3.2` or `-1.5` automatically.

### Suffixes and prefixes
```html
<span data-rs="validated_stats.bull_recovery_primary_pct"
      data-rs-suffix="%">—</span>
<!-- renders: 79% -->

<span data-rs="oil_price" data-rs-prefix="$">—</span>
<!-- renders: $101 -->
```

### Zone coloring (adds CSS class automatically)
```html
<div class="zone-badge" data-rs-color="mrs.zone_color">...</div>
<!-- adds rs-zone-yellow, rs-zone-red, etc. -->
```
Define your zone colors in CSS:
```css
.rs-zone-green  { background: #166534; }
.rs-zone-yellow { background: #92400E; }
.rs-zone-red    { background: #991B1B; }
```

### Conditional display
```html
<div data-rs-show-if="rts.bull_recovery_signal" data-rs-equals="Active">
    Recovery signal active — monitor for re-entry.
</div>
```
Hidden unless the RTS signal flips to "Active".

### Repeating lists (factor rows, history tables)
```html
<tbody data-rs-repeat="sub_core_factors" data-rs-template="factor-row-tmpl"></tbody>

<template id="factor-row-tmpl">
    <tr>
        <td>{{name}}</td>
        <td>{{score}}</td>
        <td class="dir-{{direction}}">{{direction}}</td>
    </tr>
</template>
```
Loops through the JSON array, renders the template once per entry.

---

## Adding a New Page (future scenario)

Say you want to add a "Weekly Brief" page that shows the MRS composite, top 3 declining factors, and the week's change.

**Step 1:** Check if the fields exist in the JSON.
- `mrs.composite` ✓ exists
- `mrs.change_week_text` ✓ exists
- Top 3 declining factors — not a direct field, but `core_factors` array is sorted; use JS to filter top 3

**Step 2:** Write the HTML with `data-rs` attributes:
```html
<script src="regimesignal_loader.js" defer></script>

<h1>Weekly Brief</h1>
<p>MRS Composite: <span data-rs="mrs.composite">—</span></p>
<p data-rs="mrs.change_week_text">—</p>
<p data-rs="mrs.score_description">—</p>
```

**Step 3:** Deploy. The page will update automatically every time Python runs.

**No Python changes needed** unless you want new fields that don't exist yet.

---

## Adding a New Field (scenario: Kip adds a new metric)

Say Kip adds a "regime momentum" metric to RTS.

**Step 1:** Add to `regimesignal_data.json` schema:
```json
"rts": {
  ...
  "regime_momentum": null
}
```

**Step 2:** Add to `regimesignal_writer.py` `build_rts()`:
```python
"regime_momentum": _safe(ro.get("regime_momentum")),
```

**Step 3:** Use it in any page:
```html
<span data-rs="rts.regime_momentum">—</span>
```

**Step 4:** When Python writes a new JSON, all pages with that tag display the new value. No rebuild, no deploy gymnastics.

---

## Locked Blocks — DO NOT MODIFY

The `validated_stats` block contains numbers that appear across all marketing materials. **Never recalculate or change these without explicit sign-off from Kip**, because:

- They're printed in the About page
- They're printed on the DNA pages
- They're printed on the Terminal pages
- They're in the marketing collateral
- Changing one requires coordinating updates across all of the above

Locked values:
- `bull_recovery_primary_pct: 79`
- `confirmed_within_6wk_pct: 86`
- `avg_lead_months: 1.8`
- `full_5stage_precision_pct: 70`
- `directional_3stage_pct: 81`
- `validation_months: 432`
- `mrs_bears_detected: "8/8"`
- `mrs_false_positives: 0`
- `mrs_avg_lead_months: 5.6`

---

## Deployment Checklist

When Python produces a new run, these files need to be accessible from the web server:

| File | Deploy? | Who writes it |
|---|---|---|
| `regimesignal_data.json` | Yes — overwrites every run | Python pipeline |
| `regimesignal_loader.js` | Yes — static, rarely changes | One-time deploy |
| `*.html` (page files) | Yes — static, rarely changes | One-time deploy per page |

On `cronusmarketintelligence.com`, all four files sit in the same directory (or the loader needs the JSON URL updated in `regimesignal_loader.js` line 25).

---

## Open Questions When Kip Returns with Python

These need answers before full integration (pulled from earlier handoff notes):

1. **Does the current Python output a single RTS composite score?** If no, we need to design the composite formula.
2. **Scale of RTS** — 0-100 (like MRS) or something else? If different, normalize in `build_rts()`.
3. **Factor movement/divergence/velocity** — are these actually computed in Python today, or conceptual framing that needs to be added?
4. **MRS vs RTS independence** — is RTS actually independent or derived from MRS? (Positioning depends on this.)
5. **Bull Recovery Signal** — separate Python output, or needs to be computed from the RTS trajectory?
6. **Where does the Python run?** Kip's laptop, server, or developer's system?
7. **Current deploy flow** — how does a new daily run make it to the live site today? That's the hook point for writing the new JSON.

---

## What's in This Package

| File | Purpose |
|---|---|
| `regimesignal_data.json` | The canonical data contract (sample, matches screenshot values) |
| `regimesignal_loader.js` | JS that auto-populates any page with `data-rs` attributes |
| `regimesignal_writer.py` | Python stub showing how the pipeline writes the JSON |
| `RTS_Risk_DNA.html` | **RTS DNA page converted to use the loader (proof of concept)** |
| `INTEGRATION_GUIDE.md` | This file |

---

## What's NOT in This Package (by design)

- MRS Terminal, MRS DNA, RTS Terminal HTML files were NOT converted. They still have hardcoded values. This was intentional — the pattern is proven on RTS DNA first. Once Kip reviews and signs off, the same conversion pattern applies to the other three pages in ~1 hour each.

- Real Python model code. The writer stub shows the shape; Kip's real model plugs in by replacing the `compute_*` calls.

---

## The Two Things This Solves

**Problem 1: Scattered hardcoded values.** Before this pattern, each page had `47.3` and `Neutral` and `6/17` typed in by hand. Change the model, change every HTML file. With this pattern, the JSON updates, every page updates.

**Problem 2: Integration sprawl.** Before, every new page meant designing a new integration with the Python model. With this pattern, new pages inherit the existing data automatically. You just pick which fields to show.

---

**End of guide.**
