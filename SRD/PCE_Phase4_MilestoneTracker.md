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
| **P4-M1** | **A** | **`SDFWeightNode` (Python)** | Avramov–He-style SDF projection. Inputs: **`VectorPlug`** **`ffLoadings`**, **`MatrixPlug`** **`connMatrix`**, **`VectorPlug`** **`factorRet`**. Output: **`SignalClosurePlug`**. Linear algebra in **`SignalNodeAlgo`** (no **scipy** requirement). | **Done** | `SDFWeightNode.py`, `SignalNodeAlgo.py`, `Phase4TrackATest`. |
| **P4-M2** | **A** | **`OptionsSdfNode` (Python)** | Luzzi et al. nonparametric SDF path. Inputs: **`SurfacePlug`** `iv_surface`, **`VolRegimePlug`** `vol_regime`. Output: **`SignalClosurePlug`**. Apply **U-shape** correction when **`VOL_HIGH`**. | **Done** | Skew heuristic + **`uShapeGain`**. |
| **P4-M3** | **A** | **`ESFuturesSignalNode` (Python)** | Reference ES futures Layer 4 node: composes **`SDFWeightNode`** (or substitute), **`KyleLambdaNode`**, **`AlphaHalflifeNode`** (or equivalent half-life source) into one **`SignalClosurePlug`** out. | **Done** | **`AlphaHalflifeNode`** (scalar half-life); **`ESFuturesSignalNode`** merges base SigC + λ + HL. |
| **P4-M4** | **A** | **`HJBoundValidator` (Python)** | Validates `|alpha_weight| * confidence <= 1.0` on **`SignalClosurePlug`**. Raises **OTL_HJ_VIOLATION** via **`Gaffer` `MessagePlug`** / message API; visible node warning / UI affordance. | **Done** | **`IECore.msg`(Warning)**; pass-through **`signalOut`**. |
| **P4-M5** | **B** | **OTL grammar (ANTLR4)** | ANTLR4 grammar for **`.otl`** matching OTL v0.1: shader declaration, typed parameters, output closure **signal**. Human-reviewed spec lock. | **Done** | **SRD/otl/OTL_v0.1.g4** (spec); shipped parser is pure Python (**`Gaffer.otl.parse`**). |
| **P4-M6** | **B** | **OTL parser + type-check (Python)** | ANTLR4 runtime → AST; type-check pass (parameter types, closure output, missing inputs). Errors: **OTL_MISSING_INPUT**, etc., at parse time. | **Done** | **`python/Gaffer/otl/`** (`parse`, `check`, `evaluate`, `errors`, `tree`); exceptions + **`IECore.msg`** hooks via call sites. |
| **P4-M7** | **B** | **`OTLShaderNode` (C++/Python)** | Node loads **`.otl`**; dynamic input plugs from shader parameters; output **`SignalClosurePlug`**; **hot-reload** on file change. | **Done** | **`python/Gaffer/OTLShaderNode.py`** (Python **`ComputeNode`**); dynamic plugs on **`reloadParameterPlugs`** / path change; hash includes mtime + params + **`refreshCount`**. |
| **P4-M8** | **B** | **OTL stdlib (`.otl` files)** | Library shaders: `momentum()`, `zscore()`, `carry()`, `frac_diff()`, `kyle_lambda()`, `vpin()`, `alpha_halflife()`, … backed by existing / new Python compute nodes. ~15 files. | **Done** | Seven v0.1 stubs under **`python/Gaffer/otl/stdlib/`** (param-only; series-backed shaders remain Python nodes until OTL gains **`series`** types). |
| **P4-M9** | **B** | **`OTLShadingSystem` (Python)** | Compile/evaluate OTL networks; **OTL_LAYER_VIOLATION** on bad layer ordering; schedule re-eval by **`half_life`**; connect to **PCE stage**. | **Done** | **`python/Gaffer/OTLShadingSystem.py`**: **`validate_otl_shader_network`**, **`OTL_LAYER_VIOLATION`**; **`compile_otl_network_for_pce`** stub for stage hook. |

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
| 2026-05-18 | **Track A (P4-M1–M4):** `SDFWeightNode`, `OptionsSdfNode`, `AlphaHalflifeNode`, `ESFuturesSignalNode`, `HJBoundValidator`, `SignalNodeAlgo`; `Phase4TrackATest`. |
| 2026-05-18 | **Track B (P4-M5–M9):** `SRD/otl/OTL_v0.1.g4`, **`Gaffer.otl`**, **`OTLShaderNode`**, **`OTLShadingSystem`**, stdlib **`.otl`**, `Phase4TrackBTest`. |
