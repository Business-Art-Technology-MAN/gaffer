# PCE / OTL

AI Agent Implementation Project Plan

Portfolio Collaboration Engine  ·  Open Trading Language

Based on: GafferHQ/gaffer fork  ·  OpenUSD  ·  OpenShadingLanguage

TOTAL ESTIMATED DURATION:  14–18 WEEKS

Single AI coding agent (Claude Code or equivalent) · Human architect oversight

## Implementation status (MarketLab / PCE fork)

**Snapshot: 2026-05-18.** Trackers: [`PCE_Phase2a_Progress.md`](PCE_Phase2a_Progress.md) (M1–M3), [`PCE_Phase2_MilestoneTracker.md`](PCE_Phase2_MilestoneTracker.md) (M4–M10), [`PCE_Phase3_MilestoneTracker.md`](PCE_Phase3_MilestoneTracker.md) (Layer 3 regimes), [`PCE_Phase4_MilestoneTracker.md`](PCE_Phase4_MilestoneTracker.md) (Layer 4), [`PCE_Phase5_MilestoneTracker.md`](PCE_Phase5_MilestoneTracker.md) (Layer 5), [`PCE_Phase6_MilestoneTracker.md`](PCE_Phase6_MilestoneTracker.md) (PCE USD stage), [`PCE_NextSteps.md`](PCE_NextSteps.md) (cross-phase backlog), [`PCE_Polish_And_Deferred_Work.md`](PCE_Polish_And_Deferred_Work.md) (polish + deferrals).

| Phase | Status | Summary |
| --- | --- | --- |
| **Phase 1** — OTL plugs | **Done (current scope)** | C++ **`SeriesPlug`**, **`ScalarPlug`**, **`VectorPlug`**, **`MatrixPlug`**, **`SurfacePlug`**, **`SignalClosurePlug`**, **`WeightVectorPlug`**, **`MarketContextPlug`**, **`RegimePlug`**, **`VolRegimePlug`** (string tokens); `GafferModule` bindings, serialisers, **`MarketDataMetadata`**, **`MarketDataAlgo`**, **`GafferTest/MarketDataPlugsTest`**. *Plan delta:* not USD per-sample `timeSamples` on one float vector; `MarketContext` is a plug type, not a separate injected struct. |
| **Phase 2** — Layer 1–2 nodes | **Substantially complete (script/UI)** | **Done:** prior rows + **`PceGraphIO`**: **`.pce` as USD layer** (**`PCE-USD/1`** — USDA on disk, script + JSON metadata in root `customLayerData`, `/PCE` defaultPrim when OpenUSD is available; **`PCE-USD/2`** adds `/Portfolio` + sublayers — Phase 6); legacy **`PCE-GRAPH/1`** text envelope via `graphFormat="legacy"`) + **ArcticDB read** on `TimeSeriesStoreNode`. **GUI:** **File → PCE → Save/Open** (`GafferUI/PceFileMenu`). Tracker: [`PCE_FileFormat_And_Backends.md`](PCE_FileFormat_And_Backends.md). **`KyleLambdaNode`** / **`RealizedVolNode`**: **`ScalarPlug`** `out` (**N8**). **`IVSurfaceNode`** + **`SurfacePlug`** (**N6**). **`PackMatrixNode`** + **`PCALoadingsNode`** + PCA in **`MarketMath`** (**N9**); dedicated **`VectorPlug`/`MatrixPlug`** (**N10**). **M8/M9** nodes may still use multi-`SeriesPlug` / raw panel plugs until refactored. **Still open:** broader live APIs than HTTP CSV + FRED. |
| **Phase 3** — Layer 3 regime nodes | **Done** (see §5 tracker) | **`RegimePlug`**, **`VolRegimePlug`**, **`ThresholdRegimeNode`**, **`VolRegimeNode`**, **`CPRegimeNode`**, **`HMMRegimeNode`** — [`PCE_Phase3_MilestoneTracker.md`](PCE_Phase3_MilestoneTracker.md). |
| **Phase 4 onward** | **Track A + B + Phases 5–6 v0.1** | **Phase 4:** [`PCE_Phase4_MilestoneTracker.md`](PCE_Phase4_MilestoneTracker.md). **Phase 5:** [`PCE_Phase5_MilestoneTracker.md`](PCE_Phase5_MilestoneTracker.md). **Phase 6:** [`PCE_Phase6_MilestoneTracker.md`](PCE_Phase6_MilestoneTracker.md) — **PCE-USD/2**, `/Portfolio` prims, sublayers, timeline metadata, delegate stubs. |

# 1  The Honest Estimate

Before the plan: a calibrated assessment of what an AI coding agent can and cannot do on this codebase, and where the real risks live.

## 1.1  What AI agents are genuinely good at here

- Reading and pattern-matching a large, consistent codebase — Gaffer's C++/Python patterns are highly regular. Every node follows the same ComputeNode template. An AI agent can read the existing nodes and generate new ones that follow the same patterns with very high fidelity.

- Writing Python extensions — the Layer 2–5 financial logic (factor shaders, regime classifiers, portfolio aggregator) is pure Python plugging into Gaffer's existing Python API. This is the AI agent's strongest surface.

- Writing typed plugs and compute nodes in C++ — these are formulaic. SeriesPlug, SignalClosurePlug, WeightVectorPlug, and MarketContextPlug all follow the same docstring-to-implementation pattern.

- Writing OTL shader files (.otl) — once the grammar is defined, generating standard library shader implementations is highly parallelisable and well-suited to an AI agent.

- Writing tests — Gaffer has a comprehensive test framework. Generating test coverage for new nodes follows existing test file patterns exactly.

## 1.2  Where the real risks are

- Gaffer build system complexity: Gaffer uses SCons with a bespoke dependency system. Getting it to build from scratch on a new machine is the single highest-risk task in the entire project. Budget 3–5 days for this alone, with a human in the loop.

- C++ template metaprogramming: Gaffer's plug type system uses heavy C++ templates. An AI agent can follow existing patterns but will make subtle errors in novel type registrations. Every new C++ type needs human review before merge.

- The chart viewport: Replacing GafferImage's viewer with a financial chart viewport requires writing a custom GadgetWidget in Gaffer's Qt/OpenGL layer. This is the most novel UI work and has no direct Gaffer template to follow. Highest creative risk.

- OSL extension for SigC: Extending OSL's closure type system requires modifying the OSL compiler's type checker. This is the deepest C++ work in the project. It should be isolated to a thin wrapper layer rather than touching OSL internals directly.

- Context switching cost: An AI agent loses context across long sessions. Each phase should produce a self-contained, tested, compilable increment. Never leave a phase in a broken build state.

## 1.3  Summary estimate

| Component | Optimistic | Realistic | Risk |
| --- | --- | --- | --- |
| Phase 0 — Gaffer build + orientation | 3 days | 5 days | Medium |
| Phase 1 — Core data types (C++) | 4 days | 7 days | Medium |
| Phase 2 — Layer 1–2 nodes (Python/C++) | 5 days | 8 days | Low |
| Phase 3 — Layer 3 regime nodes (Python) | 3 days | 5 days | Low |
| Phase 4 — Layer 4 signal + OTL (Python/OSL) | 6 days | 10 days | High |
| Phase 5 — Layer 5 aggregator (Python) | 4 days | 6 days | Low |
| Phase 6 — PCE Stage / usd-core backend | 5 days | 8 days | Medium |
| Phase 7 — GafferPCEChart plugin (Stage 1) | 3 days | 5 days | Low |
| Phase 7b — OpenGL gadget (Stage 2, optional) | 5 days | 8 days | High |
| Phase 8 — Execution delegates (Python) | 4 days | 6 days | Low |
| Phase 9 — Integration + polish | 5 days | 8 days | Medium |
| TOTAL (Stage 1 only) | 42 days / ~8.5 wks | 68 days / ~14 wks |  |
| TOTAL (with Stage 2) | 47 days / ~9.5 wks | 76 days / ~15 wks |  |

> Recommended working mode Human architect reviews and merges each phase before the next begins. The AI agent works within a phase in fast iteration loops (implement → build → test → fix). Never ask the AI agent to jump across phases. Context is money.

# 2  Phase 0 — Foundation: Gaffer Fork and Build

**Phase 0 — Gaffer Fork, Build, and Orientation** · *3–5 days*


The most important phase. Nothing else can start until Gaffer builds cleanly and the AI agent has oriented itself in the codebase. Do not skip or rush this.

| Task | AI Agent Action | Complexity |
| --- | --- | --- |
| Fork GafferHQ/gaffer | Create PCE fork. Rename application entry point from 'gaffer' to 'pce'. Strip renderer-specific build targets (Arnold, RenderMan) to reduce build surface. | Medium |
| Dependency installation | Run installDependencies.sh. Verify all pre-built deps resolve. Document any platform-specific issues encountered. Target: Linux first (Gaffer's primary platform). | Medium |
| Clean build | SCons full build to verify baseline. All existing Gaffer tests must pass before any modification. This is the zero-line-changed baseline. | Medium |
| Codebase orientation | AI agent reads: GafferScene/ScenePlug.h, GafferOSL/OSLShader.h, GafferUI/NodeGraph.h, Gaffer/ComputeNode.h. Produces a written summary of patterns to follow. Human reviews. | Low |
| Strip 3D rendering UI | Remove GafferScene viewer, GafferImage viewer from the application shell. Replace with placeholder panels. Verify app still launches. | Low |
| Rename namespaces | GafferScene → GafferPCE throughout. GafferOSL → GafferOTL throughout. SCons build still passes. | Low |

> Phase 0 exit criterion The forked application builds cleanly, launches, shows the node graph editor with no 3D viewport, and all core Gaffer tests pass. The AI agent has produced a written codebase orientation document.

# 3  Phase 1 — Core OTL Data Types

**Phase 1 — New Typed Plugs: SeriesPlug, SignalClosurePlug, WeightVectorPlug, MarketContextPlug** · *4–7 days*


Four C++ compound typed plugs (including OTL market context) are the structural foundation of the OTL pipeline; subsequent phases connect to these. They must be correct before anything else is built.

| Task | AI Agent Action | Complexity |
| --- | --- | --- |
| SeriesPlug (C++) | Follow FloatVectorDataPlug pattern. Wraps IECore::FloatVectorData with a time index. Supports timeSamples (USD-style). Python bindings via GafferBindings pattern. | Medium |
| SignalClosurePlug (C++) | New plug type carrying the SigC struct: alpha_weight, confidence, half_life, max_impact_frac, regime_condition, side_bet. Serialises to/from JSON for USD layer storage. | Medium |
| WeightVectorPlug (C++) | New plug type carrying the weight_vector struct: instrument_ids[], target_weights[], confidences[], gross_exposure, net_exposure, active_regime, evaluated_at. | Medium |
| MarketContext struct (C++) | Read-only evaluation context struct. Injected by PCE ShadingSystem. Carries: t (nanosecond timestamp), macro_regime, vix_level, term_spread, credit_spread. Python-accessible. | Medium |
| Type registration | Register all new types with Gaffer's TypeRegistry and IECore's RunTimeTyped system. Python bindings. Verify serialisation round-trip. | High |
| Unit tests | Test serialisation, default values, connection type-checking (SeriesPlug rejects SignalClosurePlug connections), Python API. Follow GafferTest patterns exactly. | Low |

> Phase 1 exit criterion Core OTL plug types build, serialise cleanly, have Python bindings, and pass unit tests. The type-checking system rejects incorrect connections at the UI layer.

**Implementation (2026-05-16):** Exit criterion met for **`SeriesPlug`**, **`SignalClosurePlug`**, **`WeightVectorPlug`**, and **`MarketContextPlug`** (fourth compound plug added for OTL context). **2026 extensions:** **`SurfacePlug`** (**N6**), **`ScalarPlug`** (**N8**), **`VectorPlug`/`MatrixPlug`** (**N10**). Build + **`GafferTest/MarketDataPlugsTest`** on CI / local install.

# 4  Phase 2 — Layer 1 and 2 Nodes

**Phase 2 — Data Shaders and Factor Shaders** · *5–8 days*

Incremental delivery for the thin **Phase 2a** slice (compound `SeriesPlug` compute first, stores later) is tracked in [`SRD/PCE_Phase2a_Progress.md`](PCE_Phase2a_Progress.md). The **full Phase 2 backlog** (M4+) lives in [`SRD/PCE_Phase2_MilestoneTracker.md`](PCE_Phase2_MilestoneTracker.md).


The first nodes that appear in the PCE node graph. All Layer 1 nodes output SeriesPlug. All Layer 2 nodes consume SeriesPlugs and output SeriesPlugs or floats. No signal logic appears here.

### Layer 1 — Data Shader Nodes

| Task | AI Agent Action | Complexity |
| --- | --- | --- |
| TimeSeriesStoreNode (Python) | Gaffer Python node. Wraps ArcticDB (pip install) as the default backend. Parameters: instrument_id, field, lookback, bar_type, adjust. Outputs: SeriesPlug. Point-in-time filter in BacktestContext. | Low |
| MarketVarNode (Python) | Fetches scalar market variables (VIX, T10Y2Y, credit spread) via MacroStore backend. Output: SeriesPlug. | Low |
| IVSurfaceNode (Python) | **`SurfacePlug`** output; **memory** registry (`MarketDataSurfaces`) + long-format **CSV** (`strike`,`expiry`,`iv`). Live/history SurfaceStore deferred. | Medium |
| CrossSectionNode (Python) | Fetches matrix of returns across instrument universe. Output: new MatrixPlug type. Required for Avramov-He connection matrix. | Medium |
| FactorSeriesNode (Python) | Fetches Fama-French / AQR factor return series from FactorStore. Backed by Ken French data library download or local Parquet. | Low |

**As of 2026-05-16:** **`ConstantSeriesNode`** (synthetic `SeriesPlug`) and **`SeriesCsvReaderNode`** (CSV → `SeriesPlug`; Windows path handling uses **`NoSubstitutions`** on path plugs) are implemented in addition to the stub **`TimeSeriesStoreNode`** above. **`MarketVarNode`** (macro registry / CSV / Parquet) and **`FactorSeriesNode`** (factor registry / CSV / Parquet) extend Layer 1; **`CrossSectionNode`** outputs a numeric panel via **`rowTimes`**, **`valuesRowMajor`**, **`numColumns`**; **`IVSurfaceNode`** outputs an options IV grid via **`SurfacePlug`** (memory + CSV).

### Layer 2 — Factor Shader Nodes

| Task | AI Agent Action | Complexity |
| --- | --- | --- |
| RollingReturnsNode (Python) | Log returns from SeriesPlug price input. Window parameter. Output: SeriesPlug. | Low |
| RealizedVolNode (Python) | Annualised stddev from returns SeriesPlug. Window parameter. Output: float (scalar via ScalarPlug). | Low |
| FamaFrenchLoadingsNode (Python) | Rolling OLS via statsmodels. Inputs: asset_returns, mkt_ret, smb_ret, hml_ret SeriesPlugs. Output: VectorPlug [beta_mkt, beta_smb, beta_hml]. | Low |
| PCALoadingsNode (Python) | Rolling PCA (power iteration + deflation in **`MarketMath`**, no sklearn). Input: **`MatrixPlug`**. Outputs: **`VectorPlug`** loadings / variance explained + **`SeriesPlug`** `pc1Scores`. | Low |
| KyleLambdaNode (Python) | Rolling Kyle λ **proxy** from returns + dollar volume `SeriesPlug`s. Output: **`ScalarPlug`**. | Low |
| ConnectionMatrixNode (Python) | Avramov-He cross-asset OLS. Input: MatrixPlug universe_returns. Output: MatrixPlug lambda_mat. Most compute-intensive Layer 2 node. | Medium |

> Phase 2 exit criterion A complete Layer 1→2 pipeline builds in the node graph: a TimeSeriesStoreNode fetching AAPL close prices flows through RollingReturnsNode and RealizedVolNode. Results visible in the Python console. All nodes serialise and restore from a .pce file.

**Implementation (2026-05-16, updated):** **M10** met for **`.pce`** persistence: **`PceGraphIO`** round-trips **`ScriptNode.serialise()`** / **`execute`** with **`PCE-USD/1`** (default when `pxr` is available) or legacy **`PCE-GRAPH/1`**, with unit tests in **`GafferTest/PceGraphIOTest`**. **MarketLab UI:** **File → PCE → Save Graph As / Open Graph** (`GafferUI/PceFileMenu`). **Exit story test:** **`GafferTest/Phase2ExitCriterionTest`** (CSV → **`RollingReturnsNode`** → **`RealizedVolNode`** + `.pce` round-trip). **TimeSeriesStoreNode** remains a **stub** for live feeds: **memory + Parquet + optional ArcticDB read** (v1); not full Arctic write/catalog semantics. **`SeriesCsvReaderNode`** covers file-based Layer 1 data for dev **until** store/backends are complete. **Layer 1–2 extensions:** **`MarketVarNode`** / **`FactorSeriesNode`** / **`CrossSectionNode`**; rolling FF **three-`SeriesPlug`** betas + **`ConnectionMatrixNode`** on row-major panels (no dedicated **MatrixPlug** type yet).

# 5  Phase 3 — Layer 3 Regime Shader Nodes

**Phase 3 — Regime Classification Nodes** · *3–5 days*

**Milestone tracker:** [`PCE_Phase3_MilestoneTracker.md`](PCE_Phase3_MilestoneTracker.md) · **branch:** `marketlab/phase3`.

Regime nodes consume Layer 1–2 outputs and produce a regime enum output. One regime node per portfolio — they are the global lighting layer. Three reference implementations; additional regimes are user-authored OTL shaders in Phase 4.

| Task | AI Agent Action | Complexity |
| --- | --- | --- |
| RegimePlug (C++) | String-valued regime token (**RISK_ON**, **RISK_OFF**, …) as **`RegimePlug`** with **`value`** `StringPlug`; bindings + tests (**done** in Phase 3 branch). | Low |
| ThresholdRegimeNode (Python) | Explicit threshold classifier. Inputs: **`vixSeries`**, **`termSpreadSeries`**, **`creditSpreadSeries`** (`SeriesPlug`). Parameters: **`vixThreshold`**, **`creditThreshold`**, **`termThreshold`**. Output: **`RegimePlug`** (**done**). | Low |
| VolRegimePlug (C++) + VolRegimeNode (Python) | **`VolRegimePlug`** (**VOL_HIGH** / **VOL_NORMAL** / **VOL_LOW** / **ANY**). **`VolRegimeNode`**: `vixSeries`, `realizedVolSeries`, ratio thresholds → **`VolRegimePlug`** (**done**). | Low |
| CPRegimeNode (Python) | Short/long forward or yield **`SeriesPlug`**; **`cpValue`** **`ScalarPlug`**; **`RegimePlug`** vs band (**done**). | Medium |
| HMMRegimeNode (Python) | `hmmlearn` when available; returns **`SeriesPlug`** in; **`regimeOut`** + **`stateProbSeries`** (**done**). | Medium |

> Phase 3 exit criterion A ThresholdRegimeNode and VolRegimeNode appear in the node graph, connect to VIX and spread data nodes from Phase 2, and output a stable regime classification. Regime output visible in node tooltip on hover.

# 6  Phase 4 — Layer 4 Signal Nodes and OTL Runtime

**Phase 4 — Signal Shaders, OTL Grammar, and SigC Evaluation** · *6–10 days*

**Milestone tracker:** [`PCE_Phase4_MilestoneTracker.md`](PCE_Phase4_MilestoneTracker.md) · **branch:** `marketlab/phase4`.


The most technically demanding phase. Two parallel tracks: (A) Python signal nodes that produce SignalClosurePlugs directly, and (B) the OTL shader runtime that allows .otl files to be loaded as nodes. Track A delivers value immediately. Track B is the language layer.

### Track A — Python Signal Nodes

| Task | AI Agent Action | Complexity |
| --- | --- | --- |
| SDFWeightNode (Python) | Avramov-He SDF projection. Inputs: **`ffLoadings`**, **`connMatrix`**, **`factorRet`**. Output: **`SignalClosurePlug`**. Linear algebra in **`SignalNodeAlgo`** (**done**). | Low |
| OptionsSdfNode (Python) | IV skew tilt from **`SurfacePlug`** + **`VolRegimePlug`**; U-shape gain when **VOL_HIGH** (**done**). | Medium |
| ESFuturesSignalNode + AlphaHalflifeNode (Python) | Merge base SigC + **Kyle λ** + half-life scalar (**done**). | Low |
| HJBoundValidator (Python) | HJ check; **`IECore.msg`** context **OTL_HJ_VIOLATION** (**done**). | Low |

### Track B — OTL Language Runtime

| Task | AI Agent Action | Complexity |
| --- | --- | --- |
| OTL grammar (ANTLR4) | Write ANTLR4 grammar for .otl files. Models OSL syntax: shader declaration, typed parameters, output closure signal. AI generates grammar from OTL v0.1 spec. Human reviews. | High |
| OTL parser (Python) | Python ANTLR4 runtime parses .otl source → AST. Type-check pass validates parameter types, closure output, missing inputs. Raises OTL_MISSING_INPUT etc. at parse time. | High |
| OTLShaderNode (C++/Python) | Gaffer node that loads a .otl file. Dynamically generates input plugs from shader parameters. Output: SignalClosurePlug. Reloads and re-evaluates on file change (hot-reload). | High |
| OTL stdlib (.otl files) | Implement momentum(), zscore(), carry(), frac_diff(), kyle_lambda(), vpin(), alpha_halflife() as .otl shader files using Python compute nodes as backends. ~15 files. | Low |
| OTL ShadingSystem (Python) | Manages compilation and evaluation of OTL shader networks. Validates layer ordering (OTL_LAYER_VIOLATION). Schedules re-evaluation based on half_life. Connects to PCE stage. | High |

> Phase 4 exit criterion A complete Layer 1→2→3→4 pipeline in the node graph produces a SignalClosurePlug output for ES futures. An .otl shader file can be loaded as a node and evaluated. The HJ bound validator fires correctly on an over-confident closure.

# 7  Phase 5 — Layer 5 Portfolio Aggregator

**Phase 5 — Portfolio Aggregator Node and weight_vector** · *4–6 days*


The compositor layer. One aggregator node per portfolio stage. Consumes all Layer 4 SignalClosurePlugs simultaneously via an ArrayPlug input and produces a WeightVectorPlug. Portfolio construction methods are pluggable.

| Task | AI Agent Action | Complexity |
| --- | --- | --- |
| ArraySignalPlug (C++) | New plug type: an array of SignalClosurePlugs with matching string IDs. Used as the instrument_signals input to the aggregator. Dynamic — grows as instruments are added. | Medium |
| PortfolioAggregatorNode (Python) | Primary Layer 5 node. Parameters: max_gross_exposure, max_net_exposure, max_single_name, max_factor_beta, drawdown_gate, min_confidence, construction_method. Output: WeightVectorPlug. | Low |
| HRP construction (Python) | PyPortfolioOpt HierarchicalRiskParity. Called by PortfolioAggregatorNode when construction_method='hrp'. | Low |
| MaxSharpe construction (Python) | PyPortfolioOpt EfficientFrontier + expected_returns from SigC alpha_weights. Called when construction_method='max_sharpe'. | Low |
| RiskParity construction (Python) | Riskfolio-Lib equal risk contribution. Called when construction_method='risk_parity'. | Low |
| Constraint enforcement (Python) | cap_single_name(), cap_factor_exposure(), enforce_net_exposure(), drawdown_gate_apply(). Each as a separate testable function. OTL_EXPOSURE_VIOLATION raised as MessagePlug. | Low |
| WeightVector inspector panel | Gaffer UI panel showing the weight_vector output as a table: instrument, weight, confidence, half_life. Updates live as graph evaluates. | Medium |

> Phase 5 exit criterion A three-instrument portfolio (ES1!, ZN1!, EURUSD) aggregator node produces a weight_vector visible in the inspector panel. Changing the construction_method parameter updates weights in real time. OTL_EXPOSURE_VIOLATION fires when constraints are breached.

# 8  Phase 6 — PCE Stage: OpenUSD Backend

**Phase 6 — Portfolio Prim Hierarchy via usd-core** · *5–8 days*


Gaffer already has USD import/export support. **Phase 2 (M10)** already stores the **node graph** inside a real USD **layer** as **`.pce`** (**`PCE-USD/1`**: embedded Gaffer script + metadata in root **`customLayerData`**, placeholder **`/PCE`** prim). **Phase 6** extends that into the **full portfolio stage**: typed **PCE instrument prims**, hierarchy under **`/Portfolio/...`**, **composition layers** for risk overrides, and **timeline / TimeCode** behaviour — i.e. USD-native *portfolio* semantics, not only the graph payload.

| Task | AI Agent Action | Complexity |
| --- | --- | --- |
| PCE schema definition | Define PCE USD schemas: EquityAsset, BondAsset, FuturesAsset, OptionsAsset, FXForward prims. Each has typed attributes matching OTL InstrumentContext fields. usdGenSchema. | Medium |
| PCE Stage serialisation | Extend **`.pce`** beyond **M10** (`customLayerData` script blob): shader/network and layout as first-class USD attributes/metadata on root **and** instrument prims; **layer stacks** for overrides. Round-trip tested. | High |
| Portfolio prim hierarchy | /Portfolio/Equities/ES1!, /Portfolio/Rates/ZN1!, /Portfolio/FX/EURUSD — typed PCE prims. Visible in Gaffer's SceneHierarchy panel (repurposed as PCE hierarchy panel). | Medium |
| Layer-based overrides | Risk manager can apply a USD layer override on top of a quant's base strategy layer — non-destructively adjusting max_gross_exposure without touching the base .pce file. | High |
| TimeCode mapping | USD TimeCode maps to market time (nanosecond epoch). PCE stage evaluates at ctx.t — scrubbing the timeline evaluates the shader network at different market timestamps. | High |
| USD Hydra → Execution Delegate | USD's Hydra render delegate pattern maps to PCE execution delegates. BacktestDelegate, PaperDelegate, LiveDelegate registered as named delegates in the PCE stage. | Medium |

> Phase 6 exit criterion A .pce file saves and restores the complete portfolio stage including node graph, instrument prims, and layer-based risk overrides. Scrubbing the timeline re-evaluates the shader network at different market dates.

# 9  Phase 7 — GafferPCEChart Plugin

**Phase 7 — Chart Plugin — Stage 1: matplotlib  ·  Stage 2: OpenGL Gadget** · *3–5 + 5–8 days*


Phase 7 is split into two independent stages. Stage 1 delivers the lookdev interaction model using a pure Python matplotlib backend — no C++, no build system changes, developed entirely as a Gaffer plugin. Stage 2 replaces the rendering surface with a C++ OpenGL gadget only if Stage 1 proves too slow for the interaction model. Stage 2 may never be needed.

> Plugin architecture GafferPCEChart is a standalone Gaffer plugin — a Python package in python/GafferPCEChart/ within the PCE repository. It registers new editor panels and node types via Gaffer's Python API. No SCons changes. No C++ compilation cycle. Pure Python development against Gaffer's stable API. This is the fastest possible path to a working chart viewer.

### Stage 1 — matplotlib Plugin (3–5 days)  ·  Pure Python

| Task | AI Agent Action | Complexity |
| --- | --- | --- |
| GafferPCEChart package | Create python/GafferPCEChart/__init__.py. Register chart editor panel via GafferUI.EditorWidget. Add to application startup. Verify panel appears docked in PCE layout. | Low |
| MatplotlibChartEditor (Python) | GafferUI.Widget subclass embedding a matplotlib FigureCanvas in a Gaffer editor panel. Dockable, resizable. Follows Gaffer's existing PythonEditor pattern. | Low |
| SeriesPlug auto-connection | Subscribe to GraphEditor selection signal. When a SeriesPlug output is selected, extract float[] data from plug and redraw matplotlib figure. Multiple series overlay with distinct colours. | Low |
| SigCDecompose node (Python) | New OTL node: takes SignalClosurePlug input, outputs alpha_weight, confidence, half_life as separate SeriesPlugs. Keeps chart plugin ignorant of SigC internals. Essential for lookdev. | Low |
| Technical indicator nodes | RSI, Bollinger Bands, MACD, EMA as Python OTL Layer 2 nodes — each outputs a SeriesPlug. Chart displays them identically to price series. ~8 nodes, each ~20 lines of Python. | Low |
| Timeline scrubber | QSlider widget below the chart panel. Dragging changes ctx.t on the active Gaffer Context, triggering upstream re-evaluation. Chart redraws on dirty signal. Lookdev moment. | Medium |
| SignalClosure overlay | When SignalClosurePlug selected: price chart top panel, alpha_weight middle panel (confidence as opacity), half_life decay indicator bottom panel. Three-panel matplotlib layout. | Medium |
| WeightVector bar chart | When WeightVectorPlug selected: horizontal bar chart of target_weights. Gross/net exposure as text annotations. Colour-coded long (teal) / short (coral). Matplotlib barh(). | Low |
| Progressive redraw | Show loading spinner during upstream re-evaluation. Chart updates progressively — fast matplotlib preview renders immediately, full SDF evaluation result updates when ready. | Medium |

> Stage 1 exit criterion Selecting a SeriesPlug in the node graph displays the series in the chart panel. Dragging the timeline scrubber re-evaluates the upstream OTL network and redraws the chart. Technical indicator nodes (RSI, MACD, Bollinger) overlay on the price chart. SigC alpha_weight displays in a sub-panel. This is the lookdev moment — achieved entirely in Python.

### Stage 2 — OpenGL Gadget (5–8 days)  ·  C++  ·  Only if Stage 1 is too slow

Stage 2 replaces the matplotlib rendering surface with a C++ Gaffer::Gadget drawing directly in OpenGL. The Python plugin architecture, node connections, and timeline scrubber are unchanged — only the rendering surface is replaced. Trigger this stage only if matplotlib redraw latency measurably breaks the lookdev interaction model for the target data sizes.

| Task | AI Agent Action | Complexity |
| --- | --- | --- |
| ChartGadget (C++) | New Gaffer::Gadget subclass. Receives float[] series data via a thin Python→C++ bridge. Draws line charts in immediate-mode OpenGL. Pan and zoom via mouse. <2ms redraw for 252-bar series. | High |
| ChartEditor (C++/Python) | Gaffer::Editor subclass hosting the ChartGadget. Replaces MatplotlibChartEditor. Subscribes to the same selection signal — Python plugin wiring unchanged. | High |
| Series data bridge | Thin Python→C++ data transfer: SeriesPlug float[] → C++ std::vector<float> via pybind11. One transfer per redraw, then GPU upload. No per-frame Python overhead. | Medium |
| Multi-panel layout | C++ layout manager for stacked chart panels (price / signal / weight). Proportional resize on panel drag. Matches Stage 1 visual layout exactly. | Medium |
| Performance regression tests | Automated tests: chart redraws in <2ms for 252 bars, <16ms for 5,000 bars. Backtest result curve (10,000 points) renders at 60fps. | Low |

> Stage 2 decision criterion Run Stage 1 with 500-instrument universe, 252-bar lookback, 60fps timeline scrub. If matplotlib redraws complete in under 100ms, Stage 2 is not needed. If redraw latency breaks the interaction feel, proceed to Stage 2. Most daily-bar use cases will not require Stage 2.

# 10  Phase 8 — Execution Delegates

**Phase 8 — Backtest, Paper, and Live Execution Delegates** · *4–6 days*


Execution delegates are Gaffer render backends in disguise. The same portfolio stage, evaluated by a different delegate. BacktestDelegate is the offline render; PaperDelegate is the fast preview; LiveDelegate is production.

| Task | AI Agent Action | Complexity |
| --- | --- | --- |
| ExecutionDelegate base class (Python) | Abstract base: evaluate(stage, ctx) → fills. Registers with PCE stage as a named delegate. Mirrors Gaffer's IECoreScene::Renderer abstraction. | Low |
| BacktestDelegate (Python) | Wraps NautilusTrader's backtest engine (pip install). Feeds WeightVectorPlug output as target allocations. Returns fills, P&L, drawdown, Sharpe as a BacktestResult object. | Medium |
| PaperDelegate (Python) | Simulated execution with no broker connection. Fast: evaluates the shader network forward in time at daily frequency. Used for strategy preview before full backtest. | Low |
| LiveDelegate (Python) | NautilusTrader live execution. WeightVectorPlug → order generation → broker API. Regime gate enforced before any order is emitted. Requires explicit user activation. | Medium |
| BacktestResult viewer (Python) | Gaffer panel showing backtest P&L curve as SeriesPlug (feeds back into ChartEditor). Drawdown, Sharpe, factor attribution as tabular output. One-click re-run. | Low |

> Phase 8 exit criterion Right-clicking the portfolio aggregator node and selecting 'Run Backtest' runs a full backtest of the ES futures strategy from 2015–2024 and displays the P&L curve in the chart panel alongside the signal series. A Sharpe ratio and max drawdown appear in the result panel.

# 11  Phase 9 — Integration and Polish

**Phase 9 — End-to-End Integration, Testing, and Developer Experience** · *5–8 days*


The phase that turns a collection of working components into a coherent tool. Primarily Python and UI work — the AI agent's most comfortable surface.

| Task | AI Agent Action | Complexity |
| --- | --- | --- |
| Node menu and palette | PCE node creation menu: Data Shaders, Factor Shaders, Regime Shaders, Signal Shaders, Portfolio Aggregator. Searchable. Follows GafferSceneUI menu pattern. | Low |
| Connection type validation UI | Wrong connections show red wire + tooltip with OTL error code (OTL_TYPE_MISMATCH). Correct connections show typed colour: teal=Series, purple=SigC, coral=WeightVector. | Medium |
| OTL error panel | Dedicated panel showing all OTL compile-time and runtime errors. Clicking an error highlights the responsible node. Follows Gaffer's MessageWidget pattern. | Low |
| Example portfolios | Three reference .pce files: (1) ES futures momentum, (2) ES+ZN two-asset, (3) full ES+ZN+EURUSD with options overlay. Each opens and runs correctly. | Low |
| OTL shader library browser | A panel listing all available .otl shaders with docstrings visible. Double-click creates an OTLShaderNode. Searchable by layer and asset class. | Medium |
| Performance regression tests | Automated tests ensuring ChartEditor redraws in <16ms, backtest evaluation completes in <30s for 252 bars, shader network compile in <1s. | Medium |
| Documentation and README | Update Gaffer's README to PCE. Document the five-layer pipeline, OTL grammar, and getting started guide. AI agent writes first draft from this spec document. | Low |

> Phase 9 exit criterion A new user can open PCE, drag three nodes from the node menu, connect them following the typed wire colours, view results in the chart panel, and run a backtest — all without reading documentation. The three example portfolios open and run correctly.

# 12  Working Principles for AI Agent Implementation

## 12.1  One phase at a time

The AI agent must not start Phase N+1 until Phase N's exit criterion is met and the build is green. Gaffer's build system is unforgiving — a broken build at the start of a new phase means the AI agent is working against stale assumptions.

## 12.2  Follow existing patterns exactly

Every new node, plug, and UI panel should be a systematic variation of an existing Gaffer equivalent. The AI agent should always ask: what is the closest existing Gaffer component to what I am building? Write it as a direct analog, then modify. Never invent novel architectural patterns within Gaffer.

## 12.3  Python first, C++ only when necessary

Gaffer's Python API is the right place for all financial logic — Layers 1–5 computations, OTL shader evaluation, portfolio construction, execution delegates, and the Stage 1 chart plugin. C++ is only required for the three new plug types (Phase 1), the OTLShaderNode dynamic plug generation (Phase 4), and optionally the Stage 2 OpenGL chart gadget (Phase 7) if matplotlib proves too slow. Resist the temptation to push financial logic into C++.

## 12.4  Context documents

At the end of each phase, the AI agent writes a one-page context document: what was built, what patterns were established, what decisions were made, and what Phase N+1 should know. This document is fed back to the agent at the start of the next session. Without this, context degrades across long gaps between sessions.

## 12.5  The OTL spec is the source of truth

When the AI agent is unsure what a node should do, it refers to the OTL v0.1 (rev 4) specification document. The spec defines the interface; the implementation follows. Any deviation from the spec is a proposed spec amendment, not an undocumented implementation decision.

## 12.6  Human review gates

Four tasks require human review before merging regardless of test passage: (1) any new C++ type registration, (2) any modification to the OTL grammar, (3) any change to PCE Stage serialisation format, and (4) any LiveDelegate code that generates real orders. These are the seams where AI errors propagate furthest.

# 13  Summary — What Gets Built and When

| Ph. | Deliverable | Exit Milestone | Duration | Primary Risk |
| --- | --- | --- | --- | --- |
| 0 | Gaffer fork — builds, launches, tests pass | Green build, stripped app | 3–5d | Build system |
| 1 | SeriesPlug, SignalClosurePlug, WeightVectorPlug | Type-checked connections | 4–7d | C++ templates |
| 2 | Layer 1–2 data and factor nodes | Live price→returns→vol pipeline | 5–8d | Low |
| 3 | Regime classifier nodes | Regime output in node tooltip | 3–5d | Low |
| 4 | Signal nodes + OTL runtime | .otl shader loads as node | 6–10d | OTL grammar |
| 5 | Portfolio aggregator + weight_vector | 3-asset weight table updates live | 4–6d | Low |
| 6 | PCE Stage / usd-core backend | .pce file round-trips, timeline scrubs | 5–8d | USD schema |
| 7 | GafferPCEChart plugin (Stage 1 + optional Stage 2) | Chart viewer, timeline scrubber, TA nodes working | 3–5d (+5–8d opt) | Low (Stage 1) / High (Stage 2) |
| 8 | Execution delegates | Backtest P&L in ChartEditor | 4–6d | Low |
| 9 | Integration + polish | New user completes workflow unaided | 5–8d | Medium |

| Optimistic total | Realistic total |
| --- | --- |
| 45 working days  ·  ~9 weeks | 73 working days  ·  ~15 weeks |

> The most honest summary This is achievable by an AI coding agent. Phase 7 Stage 1 (matplotlib chart plugin) is now the lowest-risk phase in the plan — pure Python, no build system changes, immediate value. The realistic risk remains in Phase 0 (Gaffer build), Phase 4 (OTL grammar), and Phase 7 Stage 2 (optional OpenGL gadget — only if Stage 1 proves too slow). A human architect spending 1–2 hours per phase reviewing and unblocking is the difference between 8.5 and 14 weeks.

— End of PCE/OTL Implementation Project Plan —
