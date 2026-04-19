"""
RegimeSignal Data Writer — Python Pipeline → JSON Contract
=============================================================
Kip's Python model imports this module and calls write_payload() at the
end of every run. The resulting regimesignal_data.json feeds all web
pages (MRS Terminal, MRS DNA, RTS Terminal, RTS DNA, etc.).

LOCKED ARCHITECTURE (DO NOT MODIFY WITHOUT SIGN-OFF):
  25 factors total, 70% core / 30% sub-core
  8 core factors with weights 18/18/10/8/4/4/4/4 = 70%
  17 sub-core factors with weights summing to 30%
  Optimized across 566,280 weight combinations
  7/7 non-black-swan bears called (100% regime-driven accuracy)

VALIDATED STATS (DO NOT MODIFY):
  79% bull recovery primary accuracy
  86% confirmed within 6 weeks
  1.8 months average lead
  70% full 5-stage precision
  81% 3-stage directional accuracy
  432 months validation span
  7/7 bears (MRS), 0 false positives, 5.6 mo avg lead
"""

import json
from datetime import datetime, timezone
from pathlib import Path


# =============================================================
# LOCKED CONSTANTS
# =============================================================

VALIDATED_STATS = {
    "_locked": True,
    "_warning": "DO NOT MODIFY WITHOUT EXPLICIT SIGN-OFF.",
    "bull_recovery_primary_pct": 79,
    "confirmed_within_6wk_pct": 86,
    "avg_lead_months": 1.8,
    "full_5stage_precision_pct": 70,
    "directional_3stage_pct": 81,
    "validation_months": 432,
    "mrs_bears_detected": "7/7",
    "mrs_bears_note": "7 of 7 non-black-swan bear markets (100% regime-driven accuracy)",
    "mrs_false_positives": 0,
    "mrs_avg_lead_months": 5.6,
    "bull_vs_bear_time_pct": "84 / 16",
    "bull_vs_bear_window": "S&P 500, April 1996 – April 2026 (30-year window, 360 months)",
}

# Official Locked Weights — 566,280 weight combinations tested
# Tuple format: (id, display_name, weight_pct, rank, note)
CORE_FACTOR_DEFS = [
    ("inflation",       "Inflation",                    18.00, 1, "HIGHEST INCREASE — most predictive single factor. Pre-bear inflation preceded 2000, 2022."),
    ("corporate_earn",  "Corporate Earnings",           18.00, 2, "Direct cause of bear markets. Forward EPS revision turning negative is clearest 3-6 month leading signal."),
    ("valuation",       "Valuation (Fwd P/E)",          10.00, 3, "Amplifies downside when combined with earnings compression. ERP is most useful component."),
    ("fed_policy",      "Federal Reserve Policy",        8.00, 4, "Fed acts AFTER conditions develop; liquidity/credit capture effects faster."),
    ("consumer_sent",   "Consumer Sentiment",            4.00, 5, "Contrarian/lagging. Extreme bearishness is BULLISH. Reduced to prevent false bearish signals."),
    ("economy",         "Economy (GDP/Employment/LEI)",  4.00, 6, "Coincident/lagging vs. stock market. Stocks lead economy by 6-9 months."),
    ("gov_policy",      "Government Policy",             4.00, 7, "Hard to quantify objectively. Already captured in Inflation, Earnings, Liquidity."),
    ("liquidity",       "Liquidity & Financial Cond.",   4.00, 8, "Heavily represented in sub-core credit spreads; core-level signal partially redundant."),
]

# Sub-core: (id, display_name, weight_pct, theme)
SUBCORE_FACTOR_DEFS = [
    ("sm_net_inflows",      "Stock Market Net Inflows",                2.50, "Flow"),
    ("futures_positioning", "Futures Positioning",                     2.00, "Flow"),
    ("cash_vs_invest",      "Cash vs. Investment Allocation",          2.00, "Flow"),
    ("market_breadth",      "Market Breadth",                          2.00, "Structure"),
    ("index_concentration", "Index Concentration",                     2.00, "Structure"),
    ("usd_dynamics",        "U.S. Dollar Dynamics",                    1.50, "Macro"),
    ("trade_activity",      "Imports / Exports (Trade Activity)",      1.00, "Macro"),
    ("money_velocity",      "Money Velocity",                          1.00, "Macro"),
    ("housing_activity",    "Housing Market Activity",                 1.00, "Macro"),
    ("labor_conditions",    "Labor Market Conditions",                 1.00, "Macro"),
    ("credit_spreads",      "Credit Spreads",                          4.00, "Credit"),
    ("hy_price_to_par",     "High Yield Price-to-Par",                 2.00, "Credit"),
    ("default_rates",       "Default Rates (Corporate)",               2.00, "Credit"),
    ("downgrade_upgrade",   "Downgrade-to-Upgrade Ratio",              2.00, "Credit"),
    ("distressed_exchange", "Distressed Exchange Activity",            1.00, "Credit"),
    ("consumer_credit",     "Consumer Credit Stress (Composite)",      2.00, "Credit"),
    ("liquidity_tga_rrp",   "Liquidity Conditions (TGA/RRP/Reserves)", 1.00, "Liquidity"),
]

# Assertion: weights must sum to exactly 100%
assert abs(sum(f[2] for f in CORE_FACTOR_DEFS) - 70.00) < 0.001, "Core weights must sum to 70%"
assert abs(sum(f[2] for f in SUBCORE_FACTOR_DEFS) - 30.00) < 0.001, "Sub-core weights must sum to 30%"

# 5-stage classification anchors (midpoints of each range on the 0-100 asymmetric scale)
STAGE_ANCHORS = {
    "Bear":          12.5,
    "Neutral":       35.0,
    "Marginal Bull": 52.5,
    "Moderate Bull": 70.0,
    "Strong Bull":   90.0,
}

STAGE_RANGES = {
    "Bear":          (0,  25),
    "Neutral":       (25, 45),
    "Marginal Bull": (45, 60),
    "Moderate Bull": (60, 80),
    "Strong Bull":   (80, 100),
}

HISTORICAL_BEARS = [
    {"bear_start": "1990-07", "trough": "1990-10"},
    {"bear_start": "2000-03", "trough": "2002-10"},
    {"bear_start": "2007-10", "trough": "2009-03"},
    {"bear_start": "2018-09", "trough": "2018-12"},
    {"bear_start": "2020-02", "trough": "2020-03", "note": "COVID exogenous (black swan)"},
    {"bear_start": "2022-01", "trough": "2022-10"},
]


# =============================================================
# HELPERS
# =============================================================

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe(val, default=None):
    if val is None:
        return default
    try:
        import math
        if isinstance(val, float) and math.isnan(val):
            return default
    except ImportError:
        pass
    return val


def _clamp(val, lo, hi):
    return max(lo, min(hi, val))


# =============================================================
# RTS COMPOSITE CALCULATION — THE NEW FORMULA
# =============================================================

def compute_rts_composite(
    stage_5: str,
    sub_core_scores: dict,
    bull_recovery_signal: str,
    core_direction_net: float,
    sub_core_direction_net: float,
    flows_accelerating: bool = False,
) -> dict:
    """
    Compute the RTS composite score using the asymmetric bull-weighted formula.

    Formula:
        RTS = Stage_anchor + Velocity_adj + Recovery_bonus + Divergence_penalty
        (clamped to stage's range)

    Args:
        stage_5: One of "Strong Bull", "Moderate Bull", "Marginal Bull", "Neutral", "Bear"
        sub_core_scores: dict of {factor_id: {"direction": int}} where direction ∈ {-1, 0, +1}
        bull_recovery_signal: "Active", "Pending", or "N/A"
        core_direction_net: net core direction (sum of weighted core directions, range -70 to +70)
        sub_core_direction_net: net sub-core direction (range -30 to +30)
        flows_accelerating: whether Flow-theme sub-core factors are accelerating bullish

    Returns:
        dict with composite score and component breakdowns
    """
    if stage_5 not in STAGE_ANCHORS:
        raise ValueError(f"Invalid stage_5: {stage_5}")

    stage_anchor = STAGE_ANCHORS[stage_5]
    stage_lo, stage_hi = STAGE_RANGES[stage_5]

    # --- Velocity component: weighted sub-core direction ---
    # Build weighted sum using actual sub-core weights
    weight_lookup = {f[0]: f[2] for f in SUBCORE_FACTOR_DEFS}
    weighted_sum = 0.0
    total_weight = 0.0
    for fid, data in (sub_core_scores or {}).items():
        w = weight_lookup.get(fid, 0)
        direction = data.get("direction", 0) if isinstance(data, dict) else 0
        # Convert string directions to numeric if needed
        if isinstance(direction, str):
            direction = {"bullish": 1, "neutral": 0, "bearish": -1}.get(direction, 0)
        weighted_sum += w * direction
        total_weight += w
    # Normalize to ±10 point adjustment
    if total_weight > 0:
        velocity_adj = (weighted_sum / 30.0) * 10.0
    else:
        velocity_adj = 0.0

    # --- Recovery bonus ---
    if bull_recovery_signal == "Active":
        recovery_bonus = 12.0
    elif bull_recovery_signal == "Pending" and flows_accelerating:
        recovery_bonus = 4.0
    else:
        recovery_bonus = 0.0

    # --- Divergence penalty ---
    core_bull = core_direction_net > 0
    core_bear = core_direction_net < 0
    sub_bull = sub_core_direction_net > 0
    sub_bear = sub_core_direction_net < 0

    if core_bear and sub_bull:
        divergence_penalty = -3.0  # Early recovery forming
    elif core_bull and sub_bear:
        divergence_penalty = -5.0  # Late-cycle warning (the dangerous one)
    else:
        divergence_penalty = 0.0

    # --- Compose and clamp ---
    raw = stage_anchor + velocity_adj + recovery_bonus + divergence_penalty
    clamped = _clamp(raw, stage_lo, stage_hi)

    return {
        "composite": round(clamped, 1),
        "raw_before_clamp": round(raw, 2),
        "components": {
            "stage_anchor": stage_anchor,
            "velocity_adj": round(velocity_adj, 2),
            "recovery_bonus": recovery_bonus,
            "divergence_penalty": divergence_penalty,
        },
        "stage_range": [stage_lo, stage_hi],
    }


# =============================================================
# BUILDERS — map real Python outputs to JSON contract
# =============================================================

def build_mrs(mrs_outputs: dict) -> dict:
    mo = mrs_outputs or {}
    return {
        "composite":           _safe(mo.get("composite")),
        "change_week_text":    _safe(mo.get("change_week_text"), "No change this week"),
        "regime":              _safe(mo.get("regime")),
        "regime_label":        _safe(mo.get("regime_label")),
        "zone_badge_title":    _safe(mo.get("zone_badge_title")),
        "zone_badge_range":    _safe(mo.get("zone_badge_range")),
        "zone_color":          _safe(mo.get("zone_color")),
        "velocity":            _safe(mo.get("velocity")),
        "ssi":                 _safe(mo.get("ssi")),
        "ci_low":              _safe(mo.get("ci_low")),
        "ci_high":             _safe(mo.get("ci_high")),
        "core8_score":         _safe(mo.get("core8_score")),
        "subcore17_score":     _safe(mo.get("subcore17_score")),
        "posture":             _safe(mo.get("posture")),
        "bear_threshold_text": _safe(mo.get("bear_threshold_text"), "Score ≤ 44"),
        "score_description":   _safe(mo.get("score_description")),
        "downgrade_note":      _safe(mo.get("downgrade_note")),
        "downgrade_context":   _safe(mo.get("downgrade_context")),
        "change_30d":          _safe(mo.get("change_30d")),
        "updated_at":          _now_iso(),
        "bear_call_definition": {
            "_note": "ANY MRS composite score below 55 = Bear Market Called",
            "bear_alert_threshold": 45,
            "bear_warning_range": "45-54",
            "bull_threshold": 55,
        },
    }


def build_rts(rts_outputs: dict) -> dict:
    ro = rts_outputs or {}
    probs = ro.get("stage_transition_probs", {}) or {}
    return {
        "composite":                     _safe(ro.get("composite")),
        "change_30d":                    _safe(ro.get("change_30d")),
        "recovery_velocity":             _safe(ro.get("recovery_velocity")),
        "recovery_velocity_label":       _safe(ro.get("recovery_velocity_label")),
        "factor_divergence":             _safe(ro.get("factor_divergence")),
        "sub_core_bullish_count":        _safe(ro.get("sub_core_bullish_count")),
        "ci_low":                        _safe(ro.get("ci_low")),
        "ci_high":                       _safe(ro.get("ci_high")),
        "stage_5":                       _safe(ro.get("stage_5")),
        "stage_3":                       _safe(ro.get("stage_3")),
        "bull_recovery_signal":          _safe(ro.get("bull_recovery_signal")),
        "zone_color":                    _safe(ro.get("zone_color")),
        "classification_confidence_pct": _safe(ro.get("classification_confidence_pct")),
        "neutral_persistence_pct":       _safe(ro.get("neutral_persistence_pct")),
        "bullish_transition_30d_pct":    _safe(ro.get("bullish_transition_30d_pct")),
        "bearish_transition_30d_pct":    _safe(ro.get("bearish_transition_30d_pct")),
        "score_description":             _safe(ro.get("score_description")),
        "updated_at":                    _now_iso(),
        "stage_transition_probs": {
            "strong_bull":   _safe(probs.get("strong_bull")),
            "moderate_bull": _safe(probs.get("moderate_bull")),
            "marginal_bull": _safe(probs.get("marginal_bull")),
            "neutral":       _safe(probs.get("neutral")),
            "bear":          _safe(probs.get("bear")),
        },
    }


def build_core_factors(scores_dict: dict) -> list:
    """scores_dict: {factor_id: {"score": <num>, "direction": <str>}}"""
    out = []
    scores_dict = scores_dict or {}
    for fid, name, weight, rank, note in CORE_FACTOR_DEFS:
        row = scores_dict.get(fid, {})
        out.append({
            "id": fid,
            "name": name,
            "weight_pct": weight,
            "score": _safe(row.get("score")),
            "direction": _safe(row.get("direction")),
            "rank": rank,
            "note": note,
        })
    return out


def build_sub_core_factors(scores_dict: dict) -> list:
    out = []
    scores_dict = scores_dict or {}
    for fid, name, weight, theme in SUBCORE_FACTOR_DEFS:
        row = scores_dict.get(fid, {})
        out.append({
            "id": fid,
            "name": name,
            "weight_pct": weight,
            "theme": theme,
            "score": _safe(row.get("score")),
            "direction": _safe(row.get("direction")),
        })
    return out


def build_historical_confirmations(backtest_results: dict) -> list:
    backtest_results = backtest_results or {}
    out = []
    for bear in HISTORICAL_BEARS:
        key = bear["bear_start"]
        r = backtest_results.get(key, {})
        row = {
            "bear_start":         bear["bear_start"],
            "trough":             bear["trough"],
            "rts_confirmed":      _safe(r.get("rts_confirmed")),
            "lead_months":        _safe(r.get("lead_months")),
            "signal":             _safe(r.get("signal")),
            "sp_12mo_return_pct": _safe(r.get("sp_12mo_return_pct")),
            "note":               bear.get("note"),
        }
        out.append(row)
    return out


# =============================================================
# TOP-LEVEL WRITER
# =============================================================

def build_payload(
    mrs_outputs=None,
    rts_outputs=None,
    tri_panel=None,
    core_factor_scores=None,
    subcore_factor_scores=None,
    market_indices=None,
    backtest_results=None,
    news_ticker=None,
    composite_date=None,
    updated_text="Updated just now",
) -> dict:
    return {
        "_meta": {
            "schema_version": "2.0",
            "generated_at": _now_iso(),
            "generator": "regimesignal_writer.py",
            "composite_date": composite_date or datetime.now().strftime("%B %-d, %Y"),
            "updated_text": updated_text,
            "architecture_version": "Official Locked Weights — 566,280 combinations tested",
            "factor_count": 25,
            "core_count": 8,
            "subcore_count": 17,
            "weighting_split": "70.00% core / 30.00% sub-core",
        },
        "mrs": build_mrs(mrs_outputs),
        "rts": build_rts(rts_outputs),
        "tri_panel": tri_panel or {},
        "validated_stats": VALIDATED_STATS,
        "core_factors":     build_core_factors(core_factor_scores),
        "sub_core_factors": build_sub_core_factors(subcore_factor_scores),
        "market_indices": market_indices or {},
        "historical_recovery_confirmations": build_historical_confirmations(backtest_results),
        "news_ticker": news_ticker or {},
    }


def write_payload(output_path: str, **kwargs) -> Path:
    payload = build_payload(**kwargs)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2))
    tmp.replace(out)
    return out


# =============================================================
# SMOKE TEST
# =============================================================

if __name__ == "__main__":
    # Demo RTS composite calculation for current Neutral state
    rts_calc = compute_rts_composite(
        stage_5="Neutral",
        sub_core_scores={
            "credit_spreads":   {"direction": "bearish"},
            "hy_price_to_par":  {"direction": "bearish"},
            "default_rates":    {"direction": "neutral"},
            "market_breadth":   {"direction": "bearish"},
            "sm_net_inflows":   {"direction": "bullish"},
            "cash_vs_invest":   {"direction": "bullish"},
            "money_velocity":   {"direction": "neutral"},
        },
        bull_recovery_signal="Pending",
        core_direction_net=-30,     # Core mostly bearish
        sub_core_direction_net=-5,  # Sub-core slightly bearish
        flows_accelerating=False,
    )

    print("=" * 60)
    print("RTS COMPOSITE SMOKE TEST")
    print("=" * 60)
    print(f"Current stage:     Neutral (anchor 35, range 25-45)")
    print(f"Raw composite:     {rts_calc['raw_before_clamp']}")
    print(f"Clamped composite: {rts_calc['composite']}")
    print(f"Components:")
    for k, v in rts_calc['components'].items():
        print(f"   {k:20s} {v}")
    print()

    # Write the full JSON
    out = write_payload(
        output_path="/tmp/regimesignal_data.json",
        composite_date="April 19, 2026",
        updated_text="Updated 2 min ago",
        mrs_outputs={
            "composite": 47.3,
            "velocity": -5.9,
            "ssi": "6/17",
            "ci_low": 44.1,
            "ci_high": 49.7,
            "regime": "Neutral",
            "regime_label": "Cautionary Zone",
            "zone_badge_title": "NEUTRAL — CAUTIONARY ZONE",
            "zone_badge_range": "Score range: 45–54",
            "zone_color": "yellow",
            "core8_score": 45.5,
            "subcore17_score": 49.5,
            "posture": "Balanced",
            "change_30d": -2.1,
        },
        rts_outputs={
            "composite": rts_calc["composite"],
            "stage_5": "Neutral",
            "stage_3": "Neutral",
            "bull_recovery_signal": "Pending",
            "zone_color": "yellow",
            "sub_core_bullish_count": 6,
        },
        core_factor_scores={
            "inflation":       {"score": -22, "direction": "bearish"},
            "corporate_earn":  {"score":  -7, "direction": "bullish"},
            "valuation":       {"score": -16, "direction": "bearish"},
            "fed_policy":      {"score": -18, "direction": "bearish"},
            "consumer_sent":   {"score": -14, "direction": "bearish"},
            "economy":         {"score":  -8, "direction": "neutral"},
            "gov_policy":      {"score": -18, "direction": "bearish"},
            "liquidity":       {"score": -10, "direction": "bullish"},
        },
    )
    print(f"Wrote JSON payload to: {out}")
