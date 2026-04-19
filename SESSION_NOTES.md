# RegimeSignal Session Running Notes

**Session date:** April 19, 2026
**Purpose:** Track every decision made this session so nothing is lost. Load this file + the template folder next session to pick up instantly.

---

## 1. NAVIGATION RESTRUCTURE (earlier in session)

Consolidating scattered tabs into a cleaner structure. Bloomberg-style "one terminal" feel.

### Proposed 6-tab structure (status: draft)

| # | Top Tab | Sub-tabs |
|---|---|---|
| 1 | RegimeSignal Terminal | MRS Monitor · RTS Monitor |
| 2 | About | — |
| 3 | MRS/RTS Forecast | MRS Forecast · RTS Forecast · Factor Architecture |
| 4 | Risk DNA (3-Layer Model) | AI Model · Algorithm Model · ERI Model |
| 5 | Track Record | Historical Calls · Bear Signals · Bull Signals · News (Daily/Weekly) |
| 6 | Subscribe | — |

**Open questions:**
- MRS vs. RTS: separate products or two views of one system?
- Forecast: placement still debatable
- News: under Track Record or its own tab?

---

## 2. LOCKED ARCHITECTURE — 25 FACTORS, 70/30 SPLIT

**This is the official locked architecture.** 566,280 weight combinations tested. Do not modify without Kip's explicit sign-off.

### Core 8 factors (70.00% total)

| # | Factor | Weight |
|---|---|---|
| 1 | Inflation | 18.00% |
| 2 | Corporate Earnings | 18.00% |
| 3 | Valuation (Fwd P/E) | 10.00% |
| 4 | Federal Reserve Policy | 8.00% |
| 5 | Consumer Sentiment | 4.00% |
| 6 | Economy (GDP/Employment/LEI) | 4.00% |
| 7 | Government Policy | 4.00% |
| 8 | Liquidity & Financial Conditions | 4.00% |

### Sub-core 17 factors (30.00% total)

| # | Factor | Weight | Theme |
|---|---|---|---|
| 1 | Stock Market Net Inflows | 2.50% | Flow |
| 2 | Futures Positioning | 2.00% | Flow |
| 3 | Cash vs. Investment Allocation | 2.00% | Flow |
| 4 | Market Breadth | 2.00% | Structure |
| 5 | Index Concentration | 2.00% | Structure |
| 6 | U.S. Dollar Dynamics | 1.50% | Macro |
| 7 | Imports / Exports (Trade Activity) | 1.00% | Macro |
| 8 | Money Velocity | 1.00% | Macro |
| 9 | Housing Market Activity | 1.00% | Macro |
| 10 | Labor Market Conditions | 1.00% | Macro |
| 11 | Credit Spreads | 4.00% | Credit |
| 12 | High Yield Price-to-Par | 2.00% | Credit |
| 13 | Default Rates (Corporate) | 2.00% | Credit |
| 14 | Downgrade-to-Upgrade Ratio | 2.00% | Credit |
| 15 | Distressed Exchange Activity | 1.00% | Credit |
| 16 | Consumer Credit Stress (Composite) | 2.00% | Credit |
| 17 | Liquidity Conditions (TGA/RRP/Reserves) | 1.00% | Liquidity |

### Sub-core by theme

| Theme | Weight |
|---|---|
| Flow | 6.50% |
| Structure | 4.00% |
| Macro | 5.50% |
| **Credit** | **13.00%** (heaviest sub-core theme) |
| Liquidity | 1.00% |

### Bear Market Call Definition

- **Bear Alert:** MRS composite < 45 → strong bear call
- **Bear Warning:** MRS composite 45-54 → counts as bear call (caution warranted)
- **Bull threshold:** MRS composite ≥ 55

Under this definition: **7 of 7 non-black-swan bear markets correctly called = 100% regime-driven accuracy.**

### Old notes that were WRONG (corrected)

- "25 factors" — actually correct (I temporarily thought it was 15 or 16 — it's 25)
- "69.01 / 30.99" split — **WRONG. Real split is clean 70.00 / 30.00**
- "17 sub-core factors" — correct number, but the LIST in the old notes had wrong factor names (it had VIX, Yield Curve, HY Spreads, Put/Call, etc. — those are key indicators, not the sub-core composite factors)
- "8/8 bears detected" — **WRONG. Real stat is 7/7 non-black-swan bears** (COVID excluded as exogenous)

---

## 3. THE 84/16 HISTORICAL PRIOR

**S&P 500, April 1996 – April 2026 (30-year window, 360 months):**

Bear markets (20% peak-to-trough): ~58 months
- Dot-com (2000-2002): ~31 months
- GFC (2007-2009): ~17 months
- COVID (2020): ~1 month
- 2022 bear: ~9 months

**Bull/recovery time: ~84%**
**Bear time: ~16%**

### Design implication

RTS is the bull-cycle tool. MRS is the bear tool. RTS composite scale is asymmetric bull-weighted.

---

## 4. RTS COMPOSITE FORMULA (NEW — doesn't exist in Python yet)

### Scale design (asymmetric)

| Range | Stage | Width | Rationale |
|---|---|---|---|
| 0–25 | Bear | 25pt | Compressed — MRS handles bear detail |
| 25–45 | Neutral | 20pt | Meaningful diagnostic zone |
| 45–60 | Marginal Bull | 15pt | Narrow transition state |
| 60–80 | Moderate Bull | 20pt | Most common state (~30% of time) |
| 80–100 | Strong Bull | 20pt | 85+ is late-cycle euphoria |

### Formula

```
RTS = Stage_anchor + Velocity_adj + Recovery_bonus + Divergence_penalty
      (clamped to stage's [lo, hi] range)
```

**Stage anchors (midpoints):**
- Bear = 12.5 · Neutral = 35 · Marginal Bull = 52.5 · Moderate Bull = 70 · Strong Bull = 90

**Velocity_adj:** Weighted sub-core direction, normalized to ±10 pts. Credit's 13% weight dominates this component.

**Recovery_bonus:**
- Active recovery signal: +12
- Pending + flows accelerating: +4
- Otherwise: 0

**Divergence_penalty:**
- Core bearish + sub-core bullish: −3 (early recovery forming)
- Core bullish + sub-core bearish: **−5 (late-cycle warning — the dangerous one)**
- Otherwise: 0

### Validation smoke test

Current state (Neutral stage, sub-core mildly bearish, no recovery, no divergence):
**RTS = 33.8** (sits in Neutral range 25-45, slightly below midpoint because velocity is negative)

✓ Formula produces sensible output.

---

## 5. FILES IN TEMPLATE PACKAGE

| File | Purpose |
|---|---|
| `regimesignal_data.json` | Canonical data contract (25 factors, locked weights) |
| `regimesignal_loader.js` | JS auto-populates pages via `data-rs` attributes |
| `regimesignal_writer.py` | Python writer + RTS composite calculation |
| `RTS_Risk_DNA.html` | Proof page using the loader (unchanged since earlier) |
| `RTS_COMPOSITE_DESIGN.md` | Formal RTS composite spec |
| `INTEGRATION_GUIDE.md` | How the whole pipeline works |
| `SESSION_NOTES.md` | This file |

---

## 6. OPEN QUESTIONS FOR KIP / PYTHON TEAM

1. **Does RTS actually exist as independent math, or is it currently derived from MRS?** Positioning depends on this.
2. **5-stage classifier — already in Python?** The 70% / 81% stats imply yes, but need to confirm output format (class label? probabilities?).
3. **Bull Recovery Signal — separate Python output or derived from stage + velocity?**
4. **Velocity window — 20 trading days? 30 calendar days? Quarterly?** Pick one.
5. **Where does Python run?** Laptop / server / developer machine.
6. **How does a daily run deploy to the live site today?** That's the hook for writing the new JSON.
7. **Is 432 months of factor-level data available for backtest?** Affects how thoroughly we can validate the formula.

---

## 7. VALIDATED STATS (LOCKED — DO NOT MODIFY)

Copy-paste these exact values for any reference to RegimeSignal performance:

- 79% bull recovery primary accuracy
- 86% confirmed within 6 weeks
- 1.8 months average lead before trough
- 70% full 5-stage precision
- 81% 3-stage directional accuracy
- 432 months validated
- 7/7 non-black-swan bears called
- 0 false positives (MRS)
- 5.6 months average MRS lead
- 84 / 16 bull/bear time split (30-year window)

---

## 8. WHAT TO DO NEXT SESSION

1. Load this file + the template folder
2. Ask Kip to answer the 7 open questions above
3. Get the Python pipeline code (or its outputs) to wire real values into the JSON
4. Backtest the RTS composite formula across 432 months, verify the 84/16 distribution holds
5. Convert MRS Terminal, MRS DNA, RTS Terminal pages to use the loader (same pattern as RTS DNA)
6. Resolve the navigation restructure (6 tabs vs 7, Forecast placement, News placement)

---

**End of running notes.**
