# Phase 3 — milestone tracker (Layer 3 regime shaders)

**Parent:** [PCE_OTL_ProjectPlan_v2.md](PCE_OTL_ProjectPlan_v2.md) §5 *Phase 3 — Layer 3 Regime Shader Nodes*.  
**Active branch:** `marketlab/phase3` (work starts after Phase 2 merged to `main`).  
**Depends on:** Phase 1 plugs (`SeriesPlug`, `ScalarPlug`, `MarketContextPlug`, …) and Phase 2 data/factor nodes (`MarketVarNode`, `RollingReturnsNode`, `RealizedVolNode`, …).  
**Precedes:** Phase 4 signal nodes + OTL runtime — [`PCE_Phase4_MilestoneTracker.md`](PCE_Phase4_MilestoneTracker.md) (plan §6).

This document is the **working backlog** for Layer 3: regime classification consuming Layer 1–2 outputs and driving later signal logic.

---

## Roadmap (dependency order)

| ID | Milestone | Goal | Status | Notes |
| --- | --- | --- | --- | --- |
| **P3-M1** | **`RegimePlug` (C++)** | String token (**RISK_ON**, **RISK_OFF**, **TRANSITION**, **ANY**, …) on child **`value`** `StringPlug`; bindings, serialiser, **`MarketDataAlgo`**, **`MarketDataMetadata`**, **`MarketDataPlugsTest`**. | **Done** | `include/Gaffer/RegimePlug.h`, `src/Gaffer/RegimePlug.cpp`, `RegimePlugTypeId` **118120**. |
| **P3-M2** | **`ThresholdRegimeNode` (Python)** | Inputs: `vixSeries`, `termSpreadSeries`, `creditSpreadSeries` (`SeriesPlug`). Params: `vixThreshold`, `creditThreshold`, `termThreshold`. Output: **`RegimePlug`**. | **Done** | `python/Gaffer/ThresholdRegimeNode.py`; PIT via `MarketDataTimeseries.PCE_TIME_CONTEXT_KEY`; `GafferTest.ThresholdRegimeNodeTest`. |
| **P3-M3** | **`VolRegimePlug` + `VolRegimeNode` (Python)** | **VOL_HIGH** / **VOL_NORMAL** / **VOL_LOW** / **ANY** from VIX vs realized vol (`SeriesPlug`); ratio thresholds. **`VolRegimePlug`** C++ TypeId **118121** (distinct from macro **`RegimePlug`**). | **Done** | **Build:** add `src/Gaffer/VolRegimePlug.cpp` to the `Gaffer` library. `VolRegimeNode.py`, `VolRegimeNodeTest`. |
| **P3-M4** | **`CPRegimeNode` (Python)** | Two tenor **`SeriesPlug`** inputs (`shortFwdSeries`, `longFwdSeries`); **`cpValue`** = long−short; **`RegimePlug`** vs `transitionBand`. | **Done** | `CPRegimeNode.py`, `CPRegimeNodeTest`. |
| **P3-M5** | **`HMMRegimeNode` (Python)** | Returns **`SeriesPlug`**; **Gaussian HMM** when `hmmlearn` installed, else **median** fallback; **`regimeOut`** + **`stateProbSeries`**. | **Done** | `HMMRegimeNode.py`, `HMMRegimeNodeTest`. |

---

## Exit criterion (from main plan)

> A **`ThresholdRegimeNode`** and **`VolRegimeNode`** appear in the node graph, connect to VIX and spread data nodes from Phase 2, and output a **stable regime classification**. Regime output visible in node tooltip on hover.

Stretch: **P3-M4** / **P3-M5** complete when product priority allows.

---

## Engineering notes

- **No new OTL signal logic** in Phase 3 — regimes are inputs to Phase 4 **`SignalClosurePlug`** generators.
- Reuse **Phase 2** patterns: `ComputeNode`, hash of upstream plugs + parameters, `GafferTest` module, optional **`.pce`** round-trip via existing **`PceGraphIO`**.
- **`VolRegimePlug`** is a separate **`TypeId`** (**118121**) from **`RegimePlug`** so **`OptionsSdfNode`** can wire vol regimes without ambiguity.

---

## Update log

| Date | Change |
| --- | --- |
| 2026-05-18 | **P3-M1:** `RegimePlug` (`value` string, default **ANY**); `MarketDataPlugsBinding`, `MarketDataAlgo` / metadata, tests. |
| 2026-05-18 | **P3-M3–M5:** `VolRegimePlug` (**118121**), `VolRegimeNode`, `CPRegimeNode`, `HMMRegimeNode` (+ `MarketRegimeAlgo`); tests and `MarketDataAlgo` / metadata / bindings updates. |
