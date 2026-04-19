# RTS Risk DNA — Project Notes &amp; Handoff
**File created:** April 19, 2026
**Purpose:** Capture everything decided about the RTS Risk DNA page so when Kip returns with the full Python model, Claude can pick up exactly where we left off and wire up the missing data values.

---

## WHAT WE BUILT

A standalone `RTS_Risk_DNA.html` page styled to match the MRS Risk DNA page, with Neutral regime styling (yellow/amber) because both MRS and RTS currently classify Neutral.

**File location after extraction:** `RTS_Risk_DNA/RTS_Risk_DNA.html`

---

## THE STRATEGIC FRAMING (NEW — not yet in the Python model)

The RTS Risk DNA page positions RTS differently than how it may currently be described in the model docs:

**Tagline (hero on the page):**
> "Given where we are now, where will we be in 30 days?"

**Role differentiation:**
- MRS tells you **when to defend** (bear detection)
- RTS tells you **when to re-enter** (bull recovery + regime classification)

**Methodology differentiation (critical — lead with this):**
> "RTS doesn't look at factor levels like MRS does. It measures bull recovery patterns and classifies current market regime across 5 validated stages. Entirely different math, entirely different purpose."

**This framing needs to be reflected in the Python model outputs** so the page values are genuinely sourced from the model, not narrative-only.

---

## VALIDATED STATS — DO NOT ALTER

These are hardcoded on the page and MUST match the About page exactly. Never recalculate or change these without coordinated updates across all materials:

| Stat | Value | Source |
|---|---|---|
| Bull recovery primary accuracy | **79%** | About page |
| Confirmed within 6 weeks | **86%** | About page |
| Average lead before trough | **1.8 months** | About page |
| Full 5-stage precision | **70%** | About page |
| 3-stage directional accuracy | **81%** | About page |
| Validation span | **432 months** | About page |

---

## PLACEHOLDERS ON THE PAGE (need real values from Python model)

These values are currently shown as `[RTS]` and `[&plusmn;X]` on the page. The Python model needs to output them:

### 1. `[RTS]` — Current RTS composite score
- **Type:** Number, likely 0&ndash;100 scale (to match MRS convention)
- **Appears:** 2 places on the page (score card huge number + nav tile badge)
- **Status:** Not currently calculated by existing Python model under this framing
- **What to do:** When Kip returns with the model, determine:
  - Does the model already output a single RTS composite? If yes, use that.
  - If no, design the composite formula based on RTS's stated purpose (bull recovery + 5-stage classification momentum)

### 2. `[&plusmn;X]` — 30-day change in RTS
- **Type:** Signed number (e.g., `+3`, `&minus;2`, `0`)
- **Appears:** Trend pill next to score
- **Status:** Requires 30-day historical RTS values
- **What to do:** Pull RTS from 30 days ago, subtract from today

### 3. Current 5-stage classification
- **Currently hardcoded:** "Neutral" (Stage 4)
- **Type:** One of: Strong Bull, Moderate Bull, Marginal Bull, Neutral, Bear
- **What to do:** Python should already output this &mdash; confirm the current stage matches what the page shows. Update if different.

### 4. Current 3-stage directional
- **Currently hardcoded:** "Neutral"
- **Type:** One of: Bull, Neutral, Bear
- **What to do:** Python should already output this &mdash; confirm and update if different.

### 5. Bull Recovery Signal status
- **Currently hardcoded:** "Pending"
- **Type:** One of: Active, Pending, N/A
- **What to do:** Based on whether RTS is currently flagging a bull recovery in progress. If in bear with RTS rising = Active. If in Neutral/Bull with no bear to recover from = Pending or N/A.

---

## THINGS THAT MIGHT NEED RECONCILING WHEN KIP RETURNS

When Kip brings back the full Python model, the following questions need answers &mdash; some may require extending the Python or adjusting the page:

### Q1: Does the current Python output a single RTS composite score?
- If **yes** &rarr; wire it into the page directly
- If **no** &rarr; need to design the composite. Likely candidates:
  - Weighted combination of 5-stage classification confidence + bull recovery signal strength + factor movement/velocity
  - Should map to 0&ndash;100 scale for user intuition consistency with MRS

### Q2: What's the actual scale/range of RTS?
- The page currently implies 0&ndash;100 (matches MRS)
- If the Python model uses a different scale, either:
  - Normalize to 0&ndash;100 for display
  - Or update the page to use the native scale

### Q3: How is "factor movement, divergence, and breach velocity" currently captured in Python?
- The About page language refers to these concepts (and we echoed them on the RTS DNA page)
- Need to confirm these are actually computed, or if this is conceptual framing that the Python needs to be extended to produce
- If extension needed: this is a model-development task, not just a display task

### Q4: What's the relationship between MRS and RTS outputs?
- Currently we state "both models concurrently classify Neutral"
- Need to confirm the Python actually has RTS doing its own classification (not just reading MRS's stage)
- If RTS is currently derived from MRS, that undermines the "two independent models" positioning

### Q5: Bull Recovery Signal &mdash; where does it come from?
- Is this a separate output from the Python, or does it need to be computed from the RTS trajectory?
- Suggested logic: Bull Recovery = Active when previous MRS was bear AND RTS is trending up AND RTS crosses recovery threshold
- Needs definition before implementation

---

## DECISIONS WE MADE (for context when returning)

1. **Kept the 5-stage model** &mdash; did not expand to 7 stages (which would invalidate the published 70% precision)
2. **Used yellow/amber styling** for Neutral regime to match MRS visual language when both models agree
3. **Placed the "how RTS differs from MRS" message EARLY** on the page (in the methodology summary) and EXPANDED on it at the end
4. **Featured the tagline** ("Given where we are now, where will we be in 30 days?") prominently as page hero
5. **Validated track record** displayed prominently in its own green-bordered banner section
6. **Kept all MRS validated stats** (8/8 bears, 0 false positives, 5.6 mo lead) in the MRS vs RTS comparison

---

## WHAT KIP NEEDS TO BRING BACK

When returning to continue this work, bring:

1. **The full Python model file(s)** &mdash; so Claude can see what's actually being computed today
2. **Sample output / recent run results** &mdash; what values does the model currently produce, and in what structure?
3. **Any documentation on RTS methodology** beyond the About page text
4. **Confirmation on the 5 questions above** (Q1&ndash;Q5)

With those, Claude can:
- Identify which page values map directly to existing Python outputs
- Flag which values require Python extension/new code
- Write the Python extensions if needed
- Wire the page to consume live model data (rather than hardcoded placeholders)

---

## FILES IN THIS PACKAGE

```
RTS_Risk_DNA/
&#9500;&#9472; RTS_Risk_DNA.html            &larr; the standalone page (open in browser to preview)
&#9492;&#9472; NOTES_RTS_Risk_DNA.md        &larr; this file
```

---

## THE 3 CONVERSATION PRINCIPLES FOR NEXT TIME

When Kip returns with the full model, Claude should:

1. **Do not alter validated stats** (79%, 86%, 70%, 81%, 1.8mo, 432 months) under any circumstance without Kip's explicit sign-off
2. **Distinguish what exists in Python today vs. what's new framing** &mdash; don't assume the model already computes the DNA-page values. Ask first.
3. **Keep MRS and RTS as two independent models** in both code and messaging &mdash; don't let RTS become a derivative of MRS

---

---

## UPDATE &mdash; RTS RISK TERMINAL (new scope, added same session)

After completing the RTS Risk DNA page, Kip shared a screenshot of the full **MRS Risk Terminal** page showing it's FAR richer than a simple dashboard. The MRS Terminal includes:

- MRS Composite panel (score, Velocity, SSI, 90% CI)
- QUANT / AI / ERI Risk tri-panel (Cautionary, 6.1/10, 4.9)
- Factor triangle visualization (Liquidity, Earnings, etc.)
- Multi-year history chart (2020-2026)
- 8 Core Factor Movers (with bars for each factor)
- Market Indices Today (SPX, Nasdaq, Dow, 10Y, US Bonds + MTD/YTD/1YR/3YR)
- Key indicators grid (Oil, Fed Funds, CPI, ISM, Forward P/E, HY Spreads, VIX, Yield Curve, Copper/Gold, Earnings Beat, Put/Call, S&amp;P vs 200MA)
- Bottom ticker (Macro / Market / Spreads / ERI)

Kip raised the question: **should RTS have its own equivalent Terminal page?**

### Decision: YES &mdash; but it must be DIFFERENT, not a copy

**Justification:**
1. Parallel product architecture &mdash; MRS and RTS are marketed as "two independent institutional-grade models." MRS having a full Terminal while RTS only has a DNA page makes RTS look secondary, undermining the "two-for-one value" positioning.
2. Different data story &mdash; MRS Terminal shows factor LEVELS because MRS reads current factor states. RTS needs to show factor MOVEMENT, DIVERGENCE, and VELOCITY because that's what RTS actually measures.
3. Different decision focus &mdash; MRS Terminal answers "are we heading into a bear?"; RTS Terminal answers "are we recovering into a bull?" / "what stage are we in?"
4. Different user decisions &mdash; defending (MRS) vs re-entering (RTS) are separate decisions requiring separate tools.

### Proposed RTS Risk Terminal structure (distinct from MRS)

**Top strip (analogous to MRS Composite, but RTS-focused):**
- RTS Composite score
- Recovery Velocity (how fast RTS is moving up &mdash; is recovery accelerating?)
- Factor Divergence (Core vs Sub-Core disagreement level)
- Confidence CI (how confident is the stage classification?)
- Stage Position Bar (Strong Bull &larr; &rarr; Bear with current position marked)

**Tri-panel (analogous to QUANT/AI/ERI, but RTS-specific):**
- 5-Stage Classification (current stage + precision %)
- 3-Stage Directional (Bull/Neutral/Bear + 81% accuracy)
- Bull Recovery Signal (Active/Pending/N/A + 79% accuracy)

**Main content area (different from MRS):**
- Stage Transition Map (visual showing likely next-stage moves &mdash; Markov-style)
- Recovery Lead-Time Tracker (1.8 mo avg &mdash; shows how far ahead RTS called each past recovery)
- 17 Sub-Core Factor Movers (sub-core is RTS's velocity layer &mdash; different from MRS's 8 core)
- Historical Recovery Confirmations (past bears + when RTS called the bottom)

**Bottom (shared style, RTS content):**
- Ticker with RTS-specific signals ("Sub-core SSI: 6/17", "Recovery velocity: stable", etc.)

### What Kip will bring back

Kip proposed to **"cut out and just get the python for that page"** &mdash; meaning: extract the Python code that currently generates the MRS Risk Terminal, plus any existing RTS-related calculations.

With that Python, Claude will be able to:
- See what values are already being computed (MRS side has a lot of this infrastructure)
- Identify which RTS Terminal panels can reuse existing Python outputs
- Flag which new Python calculations need to be added (likely: Recovery Velocity, Factor Divergence metric, Stage Transition probabilities)
- Write the new RTS Risk Terminal page that consumes those values

### Order of operations for next session

1. **First:** Review the Python Kip brings back
2. **Second:** Map existing outputs to both RTS Risk DNA page values AND RTS Risk Terminal panels
3. **Third:** Identify gaps &mdash; what new Python is needed
4. **Fourth:** Build the RTS Risk Terminal page as a matching companion to MRS Risk Terminal
5. **Fifth:** Wire both the RTS DNA and RTS Terminal to consume live model data

### IMPORTANT: Validated stats still locked

All validated stats (79% / 86% / 70% / 81% / 1.8 mo / 432 months) apply to the RTS Risk Terminal too. Any new panels or metrics added are OVERLAYS, not replacements for validated components. Same principle as RTS DNA.

---

---

## UPDATE 2 &mdash; CLARIFICATION ON PYTHON PIPELINE ARCHITECTURE

**Correction from earlier in session:** Claude initially was unsure whether values were hardcoded or Python-driven. The About page clearly states the architecture:

> "75+ real-time macro, market, sentiment, and geopolitical data series across **12 Institutional-Grade Sources**, feeding a **Python-based computational pipeline** that scores 25 factors against validated thresholds and recomputes the composite signal using the model's 69.01 / 30.99 Core / Sub-Core weighting structure."

### Architecture confirmed:

**12 institutional-grade data sources &rarr; Python pipeline &rarr; 25 factor scores &rarr; Composite (MRS &amp; RTS) &rarr; Page display**

The MRS Risk Terminal page is **data-driven**, not hardcoded. Values like 47.3, -22, -20, 6/17 SSI, -5.9 velocity, 90% CI bands are all computed by the Python pipeline from live feeds.

### What this means for RTS Risk Terminal

RTS Risk Terminal must hook into the **same Python pipeline** as MRS Terminal &mdash; just pulling RTS-specific outputs instead of MRS-specific ones. It cannot be a standalone static page if it's to match the product quality of MRS Terminal.

### What Grok can and CANNOT help with

- **CAN help:** Visual design / HTML layout reference
- **CANNOT help:** The Python pipeline code. Grok did not build Kip's Python model.

Grok-generated HTML files with hardcoded values should not be mistaken for the Python source. They are mockups.

### What's needed when Kip returns

For a real, data-driven RTS Terminal (not just a mockup), Claude needs:

1. **The Python pipeline code** &mdash; or at least the RTS-relevant portions &mdash; so Claude can see what's already computed and what new calculations RTS Terminal needs
2. **The output format** &mdash; does Python write to JSON? Push to database? Inject values into HTML templates via Jinja or similar? How does data flow from pipeline to webpage?
3. **The deployment flow** &mdash; how does a new daily run make it to cronusmarketintelligence.com?

With these three, RTS Terminal can plug into existing infrastructure instead of being another orphaned mockup.

### Where the Python pipeline lives (open question for Kip to verify)

Possibilities:
- **On Kip's computer** &mdash; in `OneDrive &rarr; Documents &rarr; Montecito Capital Mgt &rarr; RegimeSignal AI Quant Model` folder (look for `.py` files)
- **On a server** &mdash; runs in cloud, produces output deployed to cronusmarketintelligence.com
- **With a developer** &mdash; they maintain the code, Kip sees the output

**This must be confirmed before building.**

---

---

## UPDATE 3 &mdash; RTS RISK TERMINAL MOCKUP BUILT

Session continued. Kip asked Claude to build the RTS Risk Terminal layout/structure now (before Python arrives) so it's ready for integration when the Python pipeline can be reviewed.

### File created: `RTS_Risk_Terminal.html`

Full mockup of RTS Risk Terminal, matching MRS Risk Terminal visual style. Panels in order:

**1. Top RTS Composite Strip** (equivalent to MRS Composite panel)
- RTS Composite score `[RTS]`
- Regime label: "Neutral" with 5-stage/3-stage sub-labels
- Recovery Velocity `[&plusmn;X.X]` pts/quarter
- Factor Divergence `[X/17]` sub-core bullish
- 90% CI `[X.X&ndash;X.X]`
- 5-Stage Position Bar (visual: Strong Bull &larr; &rarr; Bear with NOW marker)

**2. Tri-Panel** (equivalent to MRS QUANT/AI/ERI tri-panel)
- 5-Stage Classification: NEUTRAL &middot; 70% precision
- 3-Stage Directional: NEUTRAL &middot; 81% accuracy
- Bull Recovery Signal: PENDING &middot; 79% primary / 86% within 6wk

**3. Header + Nav** (matching MRS, RTS tile active/highlighted)

**4. Stage Transition Map** (NEW &mdash; unique to RTS)
- 30-day probability of reaching each of 5 stages
- Shows transition matrix from current Neutral
- Warning note with bearish transition probability

**5. Recovery Lead-Time Tracker** (NEW &mdash; unique to RTS)
- Historical bars showing months RTS confirmed recovery before each trough
- 5 bears listed: 1990, 2001, 2008, 2018, 2022 (with illustrative lead times)
- 1.8-month average summary callout

**6. 17 Sub-Core Factor Movers** (different from MRS's 8 Core)
- Two-column grid of all 17 sub-core factors
- Bullish/bearish/neutral bars (centered at zero, extending left/right)
- Placeholder values `[&plusmn;X]` for Python to fill
- Factor names from About page (VIX Regime, Yield Curve Slope, HY Spreads, Put/Call, Advance-Decline, Momentum, Copper/Gold, S&amp;P vs 200MA, etc.)

**7. Historical Confirmations Table** (NEW &mdash; unique to RTS)
- Validated track record table: Bear Market, Actual Trough, RTS Confirmation, Lead Time, Signal, S&amp;P 12mo Return
- 6 rows covering 1990, 2001, 2008, 2018, 2020 (COVID exogenous note), 2022
- Footnote on COVID exogenous caveat

**8. Market Indices** (matching MRS, same 5 indices with MTD/YTD/1YR/3YR)

**9. Bottom Ticker** (3 rows)
- RTS Sub-Core Live status
- Stage Transition 30D
- Recovery Track Record

### Placeholders in the Terminal (all need Python wiring)

| Placeholder | Location | Source needed |
|---|---|---|
| `[RTS]` | Top strip composite, nav tile, position bar label | Main composite calculation |
| `[&plusmn;X.X]` | Recovery Velocity | New calc: RTS quarterly change rate |
| `[X/17]` | Factor Divergence | Count of bullish sub-core factors |
| `[X.X&ndash;X.X]` | 90% CI | Classification confidence interval |
| `[%]` &times;5 | Stage Transition Map | New calc: transition probabilities per stage |
| `[&plusmn;X]` &times;17 | Sub-Core Factor Movers | Individual sub-core factor scores |
| Recovery lead times | Historical panel | Likely already in Python (backtest results) |
| Market indices | Index panel | Existing feeds (can share with MRS) |

### What the Terminal demonstrates

Even without real data yet, this mockup shows:
- How RTS Terminal will be **visually equivalent but content-distinct** from MRS Terminal
- What **new Python calculations** need to be added (Recovery Velocity, Factor Divergence metric, Stage Transition probabilities)
- What **existing Python outputs** can be reused (classification stage, 432-month validation stats, index data)
- How the page will consume that data once wired

### Illustrative historical data in the table

Bear market dates (1990, 2001, 2008, 2018, 2022) and trough dates are real historical dates. The "RTS Confirmation" dates and lead times (2.1, 1.5, 2.3, 1.2, 1.9 mo averaging ~1.8 mo) are **placeholders that align with the 1.8-month stated average** &mdash; Python/backtest results should replace these with actual validated numbers.

### Files now in the package

```
RTS_Risk_DNA/
&#9500;&#9472; RTS_Risk_DNA.html             &larr; the DNA methodology page
&#9500;&#9472; RTS_Risk_Terminal.html        &larr; the full Terminal page (NEW)
&#9492;&#9472; NOTES_RTS_Risk_DNA.md         &larr; these notes
```

---

**End of notes.**



