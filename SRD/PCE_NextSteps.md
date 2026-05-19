# PCE — next implementation steps (post–Phase 2 / M10)

**Purpose:** Track **near-term** work that stays closest to **Phase 2** scope after M1–M10 and **`PCE-USD/1`** ship.

**Parent docs:** [PCE_OTL_ProjectPlan_v2.md](PCE_OTL_ProjectPlan_v2.md) (exit criteria, Phase 6 boundary) · [PCE_Polish_And_Deferred_Work.md](PCE_Polish_And_Deferred_Work.md) (polish + deferrals index) · [PCE_Phase2_MilestoneTracker.md](PCE_Phase2_MilestoneTracker.md) · [PCE_Phase3_MilestoneTracker.md](PCE_Phase3_MilestoneTracker.md) (Layer 3 regimes) · [PCE_Phase4_MilestoneTracker.md](PCE_Phase4_MilestoneTracker.md) (Layer 4 signals + OTL) · [PCE_Phase5_MilestoneTracker.md](PCE_Phase5_MilestoneTracker.md) (Layer 5 portfolio) · [PCE_Phase6_MilestoneTracker.md](PCE_Phase6_MilestoneTracker.md) (PCE USD stage) · [PCE_FileFormat_And_Backends.md](PCE_FileFormat_And_Backends.md)

**Update:** edit this file when items start/finish; keep status honest (`Not started` / `In progress` / `Done`).

---

## A — Tightest fit (Phase 2 polish)

| ID | Item | Rationale | Status | Notes / owner |
| --- | --- | --- | --- | --- |
| **N1** | **A2 — File → PCE → Save/Open in MarketLab** | Natural follow-on to M10; users need UI, not only `PceGraphIO` in Python. | **Done** | `python/GafferUI/PceFileMenu.py` + `startup/gui/menus.py`. Default **`graphFormat="usd"`** when `Gaffer.usdAvailableForPce()`, else **`legacy`**. |
| **N2** | **Document save path** (`MarketLab.cmd` / app entry) | Checklist gap in file-format doc. | **Done** | [PCE_FileFormat_And_Backends.md](PCE_FileFormat_And_Backends.md) §A + test table. |
| **N3** | **Phase 2 exit “story” test** | Plan exit: data → `RollingReturnsNode` → `RealizedVolNode`, inspectable, **restore from `.pce`**. | **Done** | `python/GafferTest/Phase2ExitCriterionTest.py` — ``MarketLab.cmd test GafferTest.Phase2ExitCriterionTest`` (one method: **three** dots, e.g. ``…Phase2ExitCriterionTest.testCsvToRollingReturnsToRealizedVolAndPceRoundTrip``). |

---

## B — Same stack, more depth

| ID | Item | Rationale | Status | Notes |
| --- | --- | --- | --- | --- |
| **N4** | **ArcticDB beyond v1 read** | **`TimeSeriesStoreNode`** read path unchanged; **publish/discovery** for real store workflows. | **Done** | `ArcticBackend.write_series_for_store`, `append_series_for_store`, `list_libraries`, `list_symbols`; tests in `TimeSeriesStoreNodeTest`. No dedicated graph “writer” node yet (call from Python / future dispatch). |
| **N5** | **Live macro / factor APIs** | Same nodes (**`MarketVarNode`**, **`FactorSeriesNode`**) with **`httpcsv`** (CSV URL) + **`fred`** (FRED id + env key). | **Done** | `MarketDataIO.read_series_http_csv` / `read_series_fred_observations`; backends on both nodes. Key: **`PCE_FRED_API_KEY`** or **`FRED_API_KEY`**. Tests: local HTTP server (+ optional FRED smoke if key set). |

---

## C — Phase 2b / plan deferrals (larger types)

| ID | Item | Rationale | Status | Notes |
| --- | --- | --- | --- | --- |
| **N6** | **`IVSurfaceNode` + `SurfacePlug`** | Layer 1 IV grid for options workflows. | **Done** | C++ `SurfacePlug` (`asOfTime`, `strikes`, `expiries`, `ivsRowMajor`); `IVSurfaceNode` **memory** + long CSV; `MarketDataSurfaces` registry; `MarketDataIO.read_iv_surface_long_csv`; tests: `GafferTest/MarketDataPlugsTest`, `GafferTest/IVSurfaceNodeTest`. |
| **N7** | **`KyleLambdaNode`** | Plan Layer 2 row. | **Done** | `python/Gaffer/KyleLambdaNode.py` + `MarketMath.rolling_kyle_lambda_proxy`. **`ScalarPlug`** `out` (since **N8**). Tests: ``MarketLab.cmd test GafferTest.KyleLambdaNodeTest``. |
| **N8** | **`ScalarPlug` alias** | Tracker “Phase 2b / later”. | **Done** | C++ `ScalarPlug` (`FloatPlug` subclass, own `TypeId`); `NumericPlug` accepts `ScalarPlug` as float input; **`RealizedVolNode`** / **`KyleLambdaNode`** use `out` = **`ScalarPlug`**. Tests: ``GafferTest.MarketDataPlugsTest.testScalarToFloatConnection``. |
| **N9** | **`PCALoadingsNode`** | Named in main plan deferred list. | **Done** | `python/Gaffer/PCALoadingsNode.py` + `MarketMath.pca_top_components_covariance`; **`PackMatrixNode`** builds **`MatrixPlug`** from panel plugs. Tests: class ``PCALoadingsNodeTest`` in `python/GafferTest/MarketDataPlugsTest.py` (run as ``GafferTest.PCALoadingsNodeTest``). |
| **N10** | **Dedicated `VectorPlug` / `MatrixPlug`** | Deferred; M8/M9 used multi–`SeriesPlug` / panels. | **Done** | C++ compound plugs: **`VectorPlug`** (`values` = `FloatVectorDataPlug`), **`MatrixPlug`** (`rowTimes`, `valuesRowMajor`, `numColumns`); `MarketDataPlugsBinding` serialisers; `MarketDataAlgo` dict interchange + `MarketDataMetadata` nodules. Tests: ``GafferTest.MarketDataPlugsTest`` (vec/mat + JSON). |
| **N11** | **Layer 5 — portfolio (`ArraySignalPlug`, `PortfolioAggregatorNode`, exposure caps)** | Plan [§7](PCE_OTL_ProjectPlan_v2.md). | **Done** | [PCE_Phase5_MilestoneTracker.md](PCE_Phase5_MilestoneTracker.md); **`WeightVectorPlug.halfLives`**; ``MarketLab.cmd test GafferTest.Phase5Test GafferTest.MarketDataPlugsTest`` (needs built **`bin/__private/gaffer.exe`**). |
| **N12** | **Layer 6 — `PCE-USD/2` portfolio stage** | Plan [§8](PCE_OTL_ProjectPlan_v2.md); **human review** for serialisation format changes. | **Done** | [PCE_Phase6_MilestoneTracker.md](PCE_Phase6_MilestoneTracker.md); ``MarketLab.cmd test GafferTest.Phase6Test GafferTest.PceGraphIOTest`` (USD via **pxr**). |

---

## Reference — rolling PCA graph

Wire a **panel** into a **`MatrixPlug`**, then PCA:

1. **Panel** → **`PackMatrixNode`**: assign **`panelRowTimes`**, **`panelValuesRowMajor`**, **`panelNumColumns`** (same semantics as **`CrossSectionNode`** outputs).
2. **`pack.out`** → **`PCALoadingsNode.in`** (`MatrixPlug` → `MatrixPlug`).
3. **`PCALoadingsNode`** outputs: **`loadings`** and **`varianceExplained`** (`VectorPlug`), **`pc1Scores`** (`SeriesPlug`, trailing-window PC1 score on the newest row).

---

## D — Phase 6 boundary (do not confuse with M10)

**M10 / `PCE-USD/1`** = USD **layer** with graph payload in **`customLayerData`** and **`/PCE`** placeholder.

**Phase 6** = **portfolio** USD: PCE schemas, **`/Portfolio/...`** hierarchy, composition overrides, timeline — see [PCE_OTL_ProjectPlan_v2.md](PCE_OTL_ProjectPlan_v2.md) §8.

Track Phase 6 work in **`PCE_Phase6_MilestoneTracker.md`** (N12); **§A (N1–N3)** and **§B–§C (N4–N12)** are complete — **Phase 3** regime milestones are complete (`PCE_Phase3_MilestoneTracker.md`); Layer 5 portfolio is **`PCE_Phase5_MilestoneTracker.md`** (N11); **PCE-USD/2** stage v0.1 is N12; next focus **Phase 4** backlog, optional refactors, or **Phase 7** §9 chart plugin.

---

## Immediate next

1. **Phase 4 (branch `marketlab/phase4`):** Follow [`PCE_Phase4_MilestoneTracker.md`](PCE_Phase4_MilestoneTracker.md) — Track A signal nodes (**`SDFWeightNode`**, **`OptionsSdfNode`**, **`ESFuturesSignalNode`**, **`HJBoundValidator`**) and Track B OTL runtime (**grammar → parser → `OTLShaderNode` → stdlib → shading system**) per plan §6 exit criterion.
2. **Phase 5–6 verification:** Run ``MarketLab.cmd test GafferTest.Phase5Test GafferTest.MarketDataPlugsTest`` (N11) and ``MarketLab.cmd test GafferTest.Phase6Test GafferTest.PceGraphIOTest`` (N12, needs **pxr**).
3. **Phase 7:** [`PCE_OTL_ProjectPlan_v2.md`](PCE_OTL_ProjectPlan_v2.md) §9 — **GafferPCEChart** Stage 1 (matplotlib).
4. **Optional refactor:** Rewire **M8/M9** nodes (**`FamaFrenchLoadingsNode`**, **`CrossSectionNode`**, etc.) to prefer **`VectorPlug`/`MatrixPlug`** where it simplifies scripts.
5. **Backlog:** Arctic **on-graph** publish nodes (beyond **`ArcticBackend`** helpers), richer **live vendors** than HTTP CSV + FRED, **usdGenSchema** upgrades for Phase 6.

---

## Tech debt note (compound connections)

**Resolved:** `ValuePlug::acceptsInput` uses **`typeId()`** (not `ValuePlug::staticTypeId()`), with **`Plug::acceptsInput`** as the first check in numeric/string/`TypedObjectPlug` specialisations so promotions still work. No additional **`Plug::acceptsInputInternal`** child-count symmetry was required once that landed.

---

## Change log

| Date | Change |
| --- | --- |
| 2026-05-16 | Initial backlog from Phase 2/M10 closeout discussion (A2, story test, Arctic depth, live APIs, 2b deferrals, Phase 6 boundary). |
| 2026-05-16 | **N1–N3 shipped:** `GafferUI/PceFileMenu`, `Phase2ExitCriterionTest`, SRD updates. |
| 2026-05-16 | **N5:** `httpcsv` + `fred` backends on `MarketVarNode` / `FactorSeriesNode` (`MarketDataIO`); tests in `MarketPhase2ExtendedTest`. |
| 2026-05-16 | **N7:** `KyleLambdaNode` + `MarketMath.rolling_kyle_lambda_proxy`; `KyleLambdaNodeTest`. |
| 2026-05-16 | **N6:** `SurfacePlug` + `IVSurfaceNode` (memory + CSV), `MarketDataSurfaces`, `MarketDataIO.read_iv_surface_long_csv`. |
| 2026-05-18 | **N8–N10:** `ScalarPlug`; `VectorPlug` / `MatrixPlug` + bindings; `PackMatrixNode`, `PCALoadingsNode`, `MarketMath` PCA helpers; `MarketDataPlugsTest` (incl. `PCALoadingsNodeTest`); `RealizedVolNode` / `KyleLambdaNode` `out` = `ScalarPlug`. |
| 2026-05-18 | **Reference graph:** § rolling PCA (`PackMatrixNode` → `PCALoadingsNode`); § immediate next (merge/CI, optional M8/M9 refactor, backlog); § tech debt note on `ValuePlug::acceptsInput`. |
| 2026-05-18 | **Phase 3:** [`PCE_Phase3_MilestoneTracker.md`](PCE_Phase3_MilestoneTracker.md) + `marketlab/phase3`; OTL status table + §5 tracker link; immediate next points at P3 milestones. |
| 2026-05-18 | **Phase 4:** [`PCE_Phase4_MilestoneTracker.md`](PCE_Phase4_MilestoneTracker.md); §6 plan link + **Immediate next** → P4; parent docs + Phase D blurb. |
