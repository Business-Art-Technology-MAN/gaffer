# Phase 3 — milestone tracker (Layer 3 regime shaders)

**Parent:** [PCE_OTL_ProjectPlan_v2.md](PCE_OTL_ProjectPlan_v2.md) §5 *Phase 3 — Layer 3 Regime Shader Nodes*.  
**Active branch:** `marketlab/phase3` (work starts after Phase 2 merged to `main`).  
**Depends on:** Phase 1 plugs (`SeriesPlug`, `ScalarPlug`, `MarketContextPlug`, …) and Phase 2 data/factor nodes (`MarketVarNode`, `RollingReturnsNode`, `RealizedVolNode`, …).  
**Precedes:** Phase 4 signal nodes + OTL runtime (same plan §6).

This document is the **working backlog** for Layer 3: regime classification consuming Layer 1–2 outputs and driving later signal logic.

---

## Roadmap (dependency order)

| ID | Milestone | Goal | Status | Notes |
| --- | --- | --- | --- | --- |
| **P3-M1** | **`RegimePlug` (C++)** | Enum/string serialisation: e.g. **RISK_ON**, **RISK_OFF**, **TRANSITION**, **ANY** (exact set TBD vs plan table). Bindings + serialiser + `MarketDataMetadata` / tests alongside other OTL plugs. | Not started | Plan: *Low* complexity. |
| **P3-M2** | **`ThresholdRegimeNode` (Python)** | Inputs: `vix_series`, `term_spread_series`, `credit_spread_series` (`SeriesPlug`). Params: thresholds. Output: **`RegimePlug`**. | Not started | Uses existing macro series from Phase 2. |
| **P3-M3** | **`VolRegimePlug` + `VolRegimeNode` (Python)** | VOL_HIGH / VOL_NORMAL / VOL_LOW from VIX `SeriesPlug` vs realized vol / thresholds. Options-signal path per plan. | Not started | May require **`RealizedVolNode`** or parallel vol series. |
| **P3-M4** | **`CPRegimeNode` (Python)** | Cochrane–Piazzesi-style classifier; yield curve via `SeriesPlug`; outputs **`RegimePlug`** + **`ScalarPlug`** `cp_value`. | Not started | Plan: *Medium*; may stub **RatesStore** or use CSV/memory like other stores. |
| **P3-M5** | **`HMMRegimeNode` (Python)** | N-state HMM (`hmmlearn` optional dep). Input: returns `SeriesPlug`. Output: **`RegimePlug`** + probability / state series. | Not started | Defer if dependency weight is too high for v1. |

---

## Exit criterion (from main plan)

> A **`ThresholdRegimeNode`** and **`VolRegimeNode`** appear in the node graph, connect to VIX and spread data nodes from Phase 2, and output a **stable regime classification**. Regime output visible in node tooltip on hover.

Stretch: **P3-M4** / **P3-M5** complete when product priority allows.

---

## Engineering notes

- **No new OTL signal logic** in Phase 3 — regimes are inputs to Phase 4 **`SignalClosurePlug`** generators.
- Reuse **Phase 2** patterns: `ComputeNode`, hash of upstream plugs + parameters, `GafferTest` module, optional **`.pce`** round-trip via existing **`PceGraphIO`**.
- **`VolRegimePlug`** may be a separate `TypeId` or a tagged subset of **`RegimePlug`**; decide in **P3-M1** design pass to avoid type churn.

---

## Update log

| Date | Change |
| --- | --- |
| 2026-05-18 | Tracker created on `marketlab/phase3`; milestones **P3-M1…P3-M5** aligned to plan §5. |
