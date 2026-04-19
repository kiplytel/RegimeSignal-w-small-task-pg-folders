# RTS Composite Score — Model Design Specification

**Version:** 1.0
**Date:** April 19, 2026
**For:** Kip / Cronus Market Intelligence, LLC
**Status:** Draft — pending Python model integration and backtest validation

---

## 1. Purpose

The RTS (Regime Transition Score) composite is a single number on a 0–100 scale that summarizes the output of the RTS model. It powers the headline display on the RTS Risk DNA page, the RTS Risk Terminal, and any page that references "RTS composite" or "RTS score."

**It does not exist in Kip's Python model yet.** This document defines how to build it.

---

## 2. Foundational Principle — The 84/16 Prior

The composite is designed around a structural asymmetry derived from S&P 500 historical data over the past 30 years (April 1996 – April 2026):

| Market condition | % of time | Instrument |
|---|---|---|
| Bull / recovery | ~84% | **RTS** — primary tool |
| Bear (20% drawdown) | ~16% | **MRS** — primary tool |

### Source data (30-year window, 360 months)

Bear markets (strict 20% peak-to-trough definition):
- Dot-com crash: Mar 2000 → Oct 2002 (~31 months)
- Global Financial Crisis: Oct 2007 → Mar 2009 (~17 months)
- COVID crash: Feb 2020 → Mar 2020 (~1 month)
- 2022 bear: Jan 2022 → Oct 2022 (~9 months)

**Total bear: ~58 months / 360 = 16.1%**
**Total bull/recovery: ~302 months / 360 = 83.9%**

### Why this matters to the composite design

1. **MRS already handles the 16%.** MRS is the bear-detection tool, validated at 7/7 non-black-swan bears called, 100% regime-driven accuracy, 5.6-month average lead. RTS does not need to duplicate this.
2. **RTS must earn its value during the 84%.** A symmetric 0–100 scale where "50 = neutral" wastes resolution. Most of the time we're in bull territory, and users need to distinguish Strong Bull from Marginal Bull — that distinction is where RTS adds value.
3. **Recovery moments are rare but high-value.** Roughly 5–6% of all time is "first few months after a trough" — but that's where the 79% / 86% / 1.8-month validated stats come from. The composite should spike meaningfully in those windows.
4. **The composite is a bull-cycle navigation tool**, not a bear alarm.

---

## 3. Input Architecture — 25 Factors, 70/30 Split

The RTS composite uses the same **Official Locked Weights** as MRS (25 factors total: 8 core at 70% / 17 sub-core at 30%). The weights were optimized across 566,280 combinations to maximize bear market calls for MRS. **RTS uses the same factor inputs but applies different math** to produce a forward-looking recovery/regime score rather than a current-state bear detection score.

### Core 8 (70.00%)

| Rank | Factor | Weight |
|---|---|---|
| 1 | Inflation | 18.00% |
| 2 | Corporate Earnings | 18.00% |
| 3 | Valuation (Fwd P/E) | 10.00% |
| 4 | Federal Reserve Policy | 8.00% |
| 5 | Consumer Sentiment | 4.00% |
| 6 | Economy (GDP/Employment/LEI) | 4.00% |
| 7 | Government Policy | 4.00% |
| 8 | Liquidity & Financial Conditions | 4.00% |

### Sub-core 17 (30.00%) — by theme

**Flow (6.50%)** — where money is moving
- Stock Market Net Inflows (2.50%)
- Futures Positioning (2.00%)
- Cash vs. Investment Allocation (2.00%)

**Structure (4.00%)** — how broad/concentrated is leadership
- Market Breadth (2.00%)
- Index Concentration (2.00%)

**Macro (5.50%)** — broader economic backdrop
- U.S. Dollar Dynamics (1.50%)
- Imports / Exports (Trade Activity) (1.00%)
- Money Velocity (1.00%)
- Housing Market Activity (1.00%)
- Labor Market Conditions (1.00%)

**Credit (13.00%)** — the heaviest sub-core theme
- Credit Spreads (4.00%)
- High Yield Price-to-Par (2.00%)
- Default Rates (Corporate) (2.00%)
- Downgrade-to-Upgrade Ratio (2.00%)
- Distressed Exchange Activity (1.00%)
- Consumer Credit Stress (Composite) (2.00%)

**Liquidity (1.00%)**
- Liquidity Conditions (TGA/RRP/Reserves) (1.00%)

**Key architectural insight:** Credit is the single heaviest sub-core theme at 13.00% — larger than any core factor except the top 3 (Inflation, Earnings, Valuation). This is material for RTS design: credit movement should carry meaningful weight in the recovery signal.

---

## 4. Scale Design — Asymmetric Bull-Weighted

```
Bear        Neutral     Marginal Bull  Moderate Bull   Strong Bull
┌──────┬──────────┬──────────────┬──────────────┬──────────────┐
0      25         45             60             80            100
│ 25pt │  20pt    │    15pt      │    20pt      │    20pt      │
│ 16%  │  15%     │   20%        │    30%       │    20%       │
│ time │  time    │   time       │    time      │    time      │
└──────┴──────────┴──────────────┴──────────────┴──────────────┘
```

### Range allocation rationale

- **Bear (0–25, 25 points wide):** Compressed. Not meant for fine-grained bear diagnostics — MRS handles that. A composite value here means "recovery has not yet formed; wait for signal."
- **Neutral (25–45, 20 points wide):** Meaningful diagnostic zone — the "uncertain between defense and re-entry" range. ~15% of time historically.
- **Marginal Bull (45–60, 15 points wide):** Narrow. Typically a transition state.
- **Moderate Bull (60–80, 20 points wide):** Middle of the bull cycle. ~30% of time — most common state.
- **Strong Bull (80–100, 20 points wide):** Top of the cycle. 85+ is late-cycle euphoria territory.

### Implied historical distribution (testable claim)

If the model is calibrated correctly, over a 432-month backtest the composite values should distribute approximately:

| Range | Label | Expected frequency |
|---|---|---|
| 0–25 | Bear | 16% |
| 25–45 | Neutral | 15% |
| 45–60 | Marginal Bull | 20% |
| 60–80 | Moderate Bull | 30% |
| 80–100 | Strong Bull | 20% |

**If the backtest distribution doesn't match, tune weights — do not tune ranges.** Ranges come from the historical prior and should stay fixed.

---

## 5. Composite Formula

```
RTS_composite = w1 × Stage_score
              + w2 × Velocity_score
              + w3 × Recovery_bonus
              + w4 × Divergence_penalty
```

### Component definitions

**1. Stage_score (50% weight) — base anchor**

Maps the current 5-stage classification to the midpoint of its scale range:

| Stage | Midpoint score |
|---|---|
| Bear | 12.5 |
| Neutral | 35 |
| Marginal Bull | 52.5 |
| Moderate Bull | 70 |
| Strong Bull | 90 |

This is the foundation. Everything else modulates around it within the stage's range.

**2. Velocity_score (25% weight) — sub-core factor movement**

Measures rate of change across the 17 sub-core factors over the trailing window (suggested: 20 trading days).

For each sub-core factor *i* with weight *wᵢ*:
- Compute rate of change over the trailing window
- Classify as bullish / neutral / bearish velocity
- Score contribution: `wᵢ × velocity_direction_i`, where direction ∈ {+1, 0, −1}

Then normalize to a ±10 point adjustment:
```
velocity_score = (Σ weighted_directions / 30.00) × 10
```

(Division by 30.00 because sub-core total weight is 30%.)

Rationale: when all 17 sub-core factors move bullish, +10. All bearish, −10. This component is where **credit movement earns its 13% outsized weight** — credit deterioration or easing will drive this component more than any other theme.

**3. Recovery_bonus (15% weight) — situational**

Fires only when `bull_recovery_signal == "Active"`:

- If Active: +12 points
- If Pending + sub-core flow factors accelerating: +4 points
- Otherwise: 0

Rationale: Recovery formation is rare (5–6% of time) but carries the 79% / 86% / 1.8-month validated stats. The bonus lifts the composite decisively above the stage anchor when a recovery signal fires.

**4. Divergence_penalty (10% weight) — warning of instability**

Measures disagreement between core 8 direction and sub-core 17 direction:

- Both themes agreeing bullish: 0 penalty (healthy)
- Both agreeing bearish: 0 penalty (MRS territory — expected)
- **Core bearish + sub-core bullish: −3 points** (early recovery forming before fundamentals confirm)
- **Core bullish + sub-core bearish: −5 points** (late-cycle warning — fundamentals still fine but positioning/credit deteriorating)

Note the asymmetry: core-bullish-but-sub-core-bearish is the dangerous divergence (pre-2008, pre-2022) and gets a larger penalty.

---

## 6. Reference Formula (worked example)

Current state (from JSON contract, April 19, 2026):
- Stage_5: Neutral → Stage_score = 35
- Sub-core velocity: 6/17 bullish, rest mixed → ~−0.8 weighted → Velocity_score ≈ −3
- Bull Recovery Signal: Pending, flows not accelerating → Recovery_bonus = 0
- Core bearish, sub-core mixed → Divergence_penalty ≈ −2

```
RTS = 0.50 × 35 + 0.25 × (−3) + 0.15 × 0 + 0.10 × (−2)
    = 17.5 − 0.75 + 0 − 0.20
    = 16.55
```

Wait — that gives 16.55 which is in Bear range. But we said stage is Neutral. Something's off with the formula arithmetic — the weights should apply differently. Let me reformulate:

### Corrected formula (weights apply to adjustments, not the full stage score)

```
RTS_composite = Stage_anchor + w1×Velocity_adj + w2×Recovery_bonus + w3×Divergence_penalty

where:
  Stage_anchor   = stage midpoint (12.5, 35, 52.5, 70, 90)
  Velocity_adj   = ±10 based on sub-core velocity weighted average
  Recovery_bonus = 0 to +12
  Divergence_penalty = 0 to −5

Scaling weights:
  w1 = 1.0   (full velocity adjustment applied)
  w2 = 1.0   (full recovery bonus applied)
  w3 = 1.0   (full divergence penalty applied)
```

With the current state:
```
RTS = 35 + (−3) + 0 + (−2) = 30
```

**RTS = 30** puts us in the Neutral range (25–45), consistent with Stage_5 = Neutral but leaning toward the lower end because velocity is bearish and there's core/sub-core divergence. That's the correct behavior.

### Constraints (prevent stage boundary violations)

After computing raw RTS, clamp within stage's range:
- If stage is Neutral (anchor 35), clamp to [25, 45]
- If stage is Moderate Bull (anchor 70), clamp to [60, 80]
- Etc.

This keeps the 5-stage classification authoritative while letting velocity/recovery/divergence add *texture* within the stage.

---

## 7. What Python Needs to Compute

For the RTS composite to work, the Python pipeline must produce the following outputs (these go in the `rts` block of `regimesignal_data.json`):

| Field | Type | Source |
|---|---|---|
| `stage_5` | string | 5-stage classifier (already exists?) |
| `stage_3` | string | 3-stage classifier (already exists?) |
| `bull_recovery_signal` | "Active" / "Pending" / "N/A" | Recovery detector |
| `composite` | 0–100 number | **NEW — computed via formula above** |
| `change_30d` | signed number | RTS(today) − RTS(30 days ago) |
| `recovery_velocity` | number | Quarterly rate of change of composite |
| `factor_divergence` | "X/17" | Count of sub-core factors in bullish velocity |
| `ci_low` / `ci_high` | numbers | Classification confidence interval |
| `sub_core_bullish_count` | integer | How many of 17 are currently bullish |
| `stage_transition_probs` | dict | 30-day transition probabilities per stage |
| `score_description` | string | Auto-generated prose summary |

### Likely already computed

Classifier outputs (`stage_5`, `stage_3`) almost certainly exist if MRS/RTS was ever validated on 432 months of data. The 5-stage and 3-stage accuracy stats (70% / 81%) imply they're already there.

### Likely NEW

The composite formula, change_30d series, divergence count, transition probabilities, and confidence intervals probably don't exist yet. These require writing new functions in the pipeline.

---

## 8. Backtest Validation Checklist

Before treating the composite as official, the Python team should:

1. **Run the formula over 432 months** with historical stage classifications and sub-core scores
2. **Check distribution matches prior:** Bear 16%, Neutral 15%, Marg Bull 20%, Mod Bull 30%, Strong Bull 20%
3. **Verify recovery-bonus windows:** In each of the 4 non-black-swan recoveries (1990, 2001, 2009, 2022), RTS should have risen ≥15 points in the 1.8-month window leading into the trough
4. **Verify late-cycle warnings:** In the 3 months before each bear, RTS should show divergence penalty firing (core bullish + sub-core bearish)
5. **Verify stage boundary integrity:** RTS should never be below 25 if stage is Neutral, never above 80 if stage is Moderate Bull, etc.
6. **Sanity check against MRS:** When MRS is below 45 (Bear Alert), RTS should be ≤ 35 most of the time (exceptions allowed if bull recovery is forming)

If any of these fail, tune weights within the formula — do not change the stage ranges or the 84/16 prior.

---

## 9. Open Questions for Python Team

Before full implementation, confirm:

1. Does the 5-stage classifier produce a confidence/probability, or just a class label? (Needed for `ci_low/ci_high` and `stage_transition_probs`.)
2. Is the Bull Recovery Signal a separate Python output, or does it need to be derived from stage + sub-core velocity?
3. Where does Python currently run? (Laptop / server / developer machine — determines deployment path.)
4. What's the trailing window for "velocity" — 20 trading days? 30 calendar days? Quarterly? (Pick one and document it.)
5. Is 432 months of validated factor-level data available for backtest, or only composite-level? (Affects how thoroughly we can validate the formula.)

---

## 10. Summary

**RTS composite is a bull-cycle navigation instrument with a compressed bear floor.** It uses the same 25-factor architecture as MRS but applies stage-classification-anchored math to produce a forward-looking recovery/regime score.

Formula: `Stage_anchor + Velocity_adj + Recovery_bonus + Divergence_penalty`, clamped within stage range.

Distribution should match the 84/16 historical prior when backtested.

Credit gets outsized influence through the 13% sub-core credit weight, which is architecturally correct — credit deterioration and easing are the cleanest recovery/stress signals we have.

---

**End of spec.**
