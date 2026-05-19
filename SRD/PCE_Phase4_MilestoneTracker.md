# Phase 4 — milestone tracker (Layer 4 signal nodes + OTL runtime)

**Parent:** [PCE_OTL_ProjectPlan_v2.md](PCE_OTL_ProjectPlan_v2.md) §6 *Phase 4 — Layer 4 Signal Nodes and OTL Runtime*.  
**Active branch:** `marketlab/phase4` (fork after Phase 3 is merged to `main`).  
**Depends on:** Phase 1 plugs (especially **`SignalClosurePlug`**, **`VectorPlug`**, **`MatrixPlug`**, **`SurfacePlug`**, **`VolRegimePlug`**, **`SeriesPlug`**, **`ScalarPlug`**), Phase 2–3 data/regime nodes, and **`PceGraphIO`** for scripted graphs.  
**Precedes:** Phase 5 portfolio aggregator ([§7](PCE_OTL_ProjectPlan_v2.md)) — **`ArraySignalPlug`**, **`PortfolioAggregatorNode`**, etc.

This document is the **working backlog** for Layer 4: **Track A** — Python nodes that emit **`SignalClosurePlug`**; **Track B** — OTL grammar, parser, **`OTLShaderNode`**, stdlib shaders, and shading system.

---

## Roadmap (dependency order)

| ID | Track | Milestone | Goal | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| **P4-M1** | **A** | **`SDFWeightNode` (Python)** | Avramov–He-style SDF projection. Inputs: **`VectorPlug`** `ff_loadings`, **`MatrixPlug`** `conn_matrix`, **`VectorPlug`** `factor_ret`. Output: **`SignalClosurePlug`**. Uses **scipy** for projection. | Not started | Unit tests + optional `.pce` round-trip. |
| **P4-M2** | **A** | **`OptionsSdfNode` (Python)** | Luzzi et al. nonparametric SDF path. Inputs: **`SurfacePlug`** `iv_surface`, **`VolRegimePlug`** `vol_regime`. Output: **`SignalClosurePlug`**. Apply **U-shape** correction when **`VOL_HIGH`**. | Not started | Depends on Phase 3 **`VolRegimeNode`** / **`VolRegimePlug`**. |
| **P4-M3** | **A** | **`ESFuturesSignalNode` (Python)** | Reference ES futures Layer 4 node: composes **`SDFWeightNode`** (or substitute), **`KyleLambdaNode`**, **`AlphaHalflifeNode`** (or equivalent half-life source) into one **`SignalClosurePlug`** out. | Not started | Plan cites **`AlphaHalflifeNode`** — stub or precede with a minimal half-life node if missing. |
| **P4-M4** | **A** | **`HJBoundValidator` (Python)** | Validates `|alpha_weight| * confidence <= 1.0` on **`SignalClosurePlug`**. Raises **OTL_HJ_VIOLATION** via **`Gaffer` `MessagePlug`** / message API; visible node warning / UI affordance. | Not started | Use **`GafferTest`** + a graph that deliberately breaches the bound. |
| **P4-M5** | **B** | **OTL grammar (ANTLR4)** | ANTLR4 grammar for **`.otl`** matching OTL v0.1: shader declaration, typed parameters, output closure **signal**. Human-reviewed spec lock. | Not started | High complexity; blocks parser and **`OTLShaderNode`** contract. |
| **P4-M6** | **B** | **OTL parser + type-check (Python)** | ANTLR4 runtime → AST; type-check pass (parameter types, closure output, missing inputs). Errors: **OTL_MISSING_INPUT**, etc., at parse time. | Not started | Depends on **P4-M5**. |
| **P4-M7** | **B** | **`OTLShaderNode` (C++/Python)** | Node loads **`.otl`**; dynamic input plugs from shader parameters; output **`SignalClosurePlug`**; **hot-reload** on file change. | Not started | Depends on **P4-M6**; may parallelise **P4-M8** once AST is stable. |
| **P4-M8** | **B** | **OTL stdlib (`.otl` files)** | Library shaders: `momentum()`, `zscore()`, `carry()`, `frac_diff()`, `kyle_lambda()`, `vpin()`, `alpha_halflife()`, … backed by existing / new Python compute nodes. ~15 files. | Not started | Lower per-file complexity; needs naming + import story with **P4-M7**. |
| **P4-M9** | **B** | **`OTLShadingSystem` (Python)** | Compile/evaluate OTL networks; **OTL_LAYER_VIOLATION** on bad layer ordering; schedule re-eval by **`half_life`**; connect to **PCE stage**. | Not started | Highest integration complexity; closes Track B. |

---

## Exit criterion (from main plan)

> A complete **Layer 1→2→3→4** pipeline in the node graph produces a **`SignalClosurePlug`** for **ES futures**. An **`.otl`** shader file can be loaded as a node and evaluated. The **HJ bound** validator fires correctly on an **over-confident** closure.

Use this tracker to mark **Track A** and **Track B** slices independently until both meet the combined exit criterion above.

---

## Engineering notes

- **Parallel tracks:** Track A ships value without OTL; Track B enables user-authored **`.otl`**. Prefer **small PRs** per milestone ID.
- Reuse **Phase 2–3** idioms: **`ComputeNode`**, plug **hash** + PIT context (**`MarketDataTimeseries.PCE_TIME_CONTEXT_KEY`** where relevant), **`GafferTest`**, **`MarketDataMetadata`** / **`MarketDataAlgo`** only when a new plug type appears (Phase 4 mostly reuses **`SignalClosurePlug`**).
- **Dependencies:** **`scipy`** (P4-M1), optional heavy deps only behind lazy imports where possible.
- **Alpha / half-life:** If **`AlphaHalflifeNode`** does not exist, record a **P4-M3a** spike or fold a minimal **`HalfLifeNode`** into P4-M3 scope in the update log.

---

## Update log

| Date | Change |
| --- | --- |
| 2026-05-18 | Initial tracker: **P4-M1…P4-M9** (Track A + B) aligned with plan §6. |
