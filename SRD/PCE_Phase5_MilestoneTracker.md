# Phase 5 — milestone tracker (Layer 5 portfolio aggregator)

**Parent:** [PCE_OTL_ProjectPlan_v2.md](PCE_OTL_ProjectPlan_v2.md) §7 *Phase 5 — Layer 5 Portfolio Aggregator*.  
**Active branch:** `marketlab/phase5`.  
**Depends on:** Phase 1 **`SignalClosurePlug`**, **`WeightVectorPlug`**; Phase 4 Layer 4 signal nodes / OTL path.  
**Precedes:** [PCE_Phase6_MilestoneTracker.md](PCE_Phase6_MilestoneTracker.md) (Layer 6 USD stage) — plan [§8](PCE_OTL_ProjectPlan_v2.md).

Working backlog for **Layer 5**: typed multi-instrument signal input, aggregation into **`WeightVectorPlug`**, constraint messaging, optional optimizer backends, and **WeightVector** UI.

---

## Roadmap (dependency order)

| ID | Milestone | Goal | Status | Notes |
| --- | --- | --- | --- | --- |
| **P5-M1** | **`ArraySignalPlug` (C++)** | Compound plug: **`instrumentIds`** (`StringVectorDataPlug`) + **`signals`** (`ArrayPlug` of **`SignalClosurePlug`**), dynamic length. | **Done** | `ArraySignalPlug` subclasses **`Plug`** (ArrayPlug is not **`ValuePlug`**). |
| **P5-M2** | **`WeightVectorPlug` half-lives** | Per-instrument **`halfLives`** vector on **`WeightVectorPlug`** for portfolio UI / risk timers. | **Done** | New child between **`confidences`** and **`grossExposure`**; **`MarketDataAlgo`** dict keys updated. |
| **P5-M3** | **`PortfolioConstrainer` (Python)** | Testable helpers: single-name cap, gross/net targets, min confidence; **`OTL_EXPOSURE_VIOLATION`** via **`IECore.msg`**. | **Done** | `python/Gaffer/PortfolioConstrainer.py`. |
| **P5-M4** | **`PortfolioAggregatorNode` (Python)** | **`ComputeNode`**: inputs **`instrumentSignals`** + risk params + **`constructionMethod`**; output **`WeightVectorPlug`**. | **Done** | Core methods: `equal_weight`, `alpha_proportional`; optional **`hrp`** / **`max_sharpe`** / **`risk_parity`** via lazy imports. |
| **P5-M5** | **Optimizer backends (optional deps)** | **`PyPortfolioOpt`** (HRP, max Sharpe), **`Riskfolio-Lib`** (risk parity) behind **`try`/`ImportError`**. | **Done** | `python/Gaffer/PortfolioOptimizerBackends.py`; graceful degradation in tests. |
| **P5-M6** | **`WeightVectorPlugValueWidget` (GafferUI)** | Read-only table: instrument, weight, confidence, half-life; live updates. | **Done** | Registers on **`WeightVectorPlug`**. |

---

## Exit criterion (from main plan)

> A three-instrument portfolio (**ES1!**, **ZN1!**, **EURUSD**) aggregator node produces a **`weight_vector`** visible in the inspector panel. Changing **`construction_method`** updates weights in real time. **`OTL_EXPOSURE_VIOLATION`** fires when constraints are breached.

**v0.1 scope:** tests use scripted plugs (no full **ES1!** pipeline required); UI widget registers for **`WeightVectorPlug`** on any node.

---

## Engineering notes

- **Array length:** **`instrumentIds`** length and **`signals`** array size should match; aggregator clamps / warns on mismatch.
- **Optimizers:** Do not add hard **pip** deps to Gaffer core; optional imports only.
- **UI:** Inspector follows **NodeEditor** / **PlugValueWidget** patterns; read-only table avoids fighting vector plug serialisation.

---

## Update log

| Date | Change |
| --- | --- |
| 2026-05-18 | **Exit verified:** `MarketLab.cmd test GafferTest.Phase5Test GafferTest.MarketDataPlugsTest` — **18 tests OK** (construction-method + exposure-message cases). **Build:** `ArraySignalPlug.cpp` uses `IECore/VectorTypedData.h` (not missing `StringVectorData.h`). **Runtime:** `PortfolioAggregatorNode` calls imported `PortfolioConstrainer` helpers (fixes worker `NameError`). **Tests:** `testConstructionMethodChangesWeights` sets `maxSingleName=1.0` so default 0.6 cap does not raise unexpected `OTL_EXPOSURE_VIOLATION` during method comparison. |
| 2026-05-19 | Initial tracker + **P5-M1–M6** implementation (aggregator, constrainer, backends stub, UI, tests). |
