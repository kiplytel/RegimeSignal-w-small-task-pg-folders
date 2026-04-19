# RegimeSignal™ Navigation Restructure — Handoff Notes

**Product:** RegimeSignal™ — Cronus Market Intelligence, LLC
**Purpose:** Consolidate scattered tabs into a cleaner 6-tab structure. Build a Bloomberg-style default monitor experience with MRS (built) and RTS (mockup ready).
**Status:** Planning / pre-implementation. Full site file to be uploaded next session.

---

## Current decisions locked in

### Tab 1 naming
- **Chosen direction:** "RegimeSignal Terminal" (Bloomberg-style — one terminal, multiple monitors inside)
- Alternates considered: Risk Terminal, Market Monitor, Live Risk Terminal
- Rationale: brands the product, parallels "the Bloomberg Terminal," avoids MRS-vs-RTS naming fight

### Two-monitor architecture
- One Terminal tab containing both monitors
- MRS loads as default (flagship, already built)
- RTS accessible via toggle / tab-within-tab / split view (TBD based on mockup)
- Shared chrome — users should feel they're in ONE environment, not two sites
- **Open question:** do MRS and RTS share reusable panels (factor readout, news feed)? If yes, componentize before building RTS

### Tab 3 — Forecast gets promoted
- Previously buried under "25 Risk Factors" — now its own top-level tab
- Named "MRS/RTS Forecast" with sub-tabs for each
- Factor Architecture moves here as a sub-tab (it's the *input layer* to the forecasts)

### Tab 4 — "Risk DNA" branding
- Using "Risk DNA" as the evocative name for the 3-Layer Model tab
- Sub-tabs: AI Model · Algorithm Model · ERI Model

### Tab 5 — Track Record
- Open issue: News (Daily/Weekly) currently lives here but it's ongoing content, not past calls
- Options: (a) keep News under Track Record for now, (b) split News into its own tab later (would push to 7 tabs)
- Current choice: keep under Track Record to hold the 6-tab limit

---

## Proposed 6-tab structure

| # | Top Tab | Sub-tabs | Notes |
|---|---------|----------|-------|
| 1 | RegimeSignal Terminal | MRS Monitor · RTS Monitor | Bloomberg-style, MRS default |
| 2 | About | — | Standalone |
| 3 | MRS/RTS Forecast | MRS Forecast · RTS Forecast · Factor Architecture | Forecast promoted to top level |
| 4 | Risk DNA (3-Layer Model) | AI Model · Algorithm Model · ERI Model | "Risk DNA" as branded name |
| 5 | Track Record | Historical Calls · Bear Signals · Bull Signals · News (Daily/Weekly) | News placement still open |
| 6 | Subscribe | — | Standalone |

---

## Questions still open (resolve before build)

1. **MRS vs. RTS relationship** — are they separate products or two views of one system? Affects whether Terminal is singular or plural branding.
2. **RTS monitor layout** — does it mirror MRS or differ structurally? User has mockup to review next session.
3. **News placement** — keep under Track Record (6 tabs) or split out (7 tabs)?
4. **Forecast sub-tab depth** — should "Factor Architecture" stay a sub-tab of Forecast, or move elsewhere?
5. **Color coding** — user's original table had a color column left blank. Assign once structure is locked.

---

## What user plans to bring next session

- Full site file (couldn't load this session due to conversation limits)
- Snippet files covering existing sections
- RTS monitor mockup for review

## Next session action plan

1. Load the full site file
2. Map current tabs/pages → new 6-tab structure
3. Review RTS mockup, align with MRS monitor pattern
4. Identify shared components between MRS and RTS monitors
5. Decide final placement for News and Factor Architecture
6. Assign color coding per tab
7. Produce migration plan (what moves where, what gets renamed, what gets deprecated)

---

## Design principles to preserve

- **Consolidation over proliferation** — fewer tabs, grouped logically
- **Bloomberg-style terminal feel** — one environment, multiple monitors, consistent chrome
- **User journey flow** — Terminal (see it) → About (learn it) → Forecast (what it predicts) → Risk DNA (how it works) → Track Record (proof) → Subscribe (buy)
- **Forecast is a headline feature** — do not bury it
- **Brand the flagship experience** — "RegimeSignal Terminal" parallels "Bloomberg Terminal"
