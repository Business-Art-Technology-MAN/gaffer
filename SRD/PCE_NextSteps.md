# PCE — next implementation steps (post–Phase 2 / M10)

**Purpose:** Track **near-term** work that stays closest to **Phase 2** scope after M1–M10 and **`PCE-USD/1`** ship.

**Parent docs:** [PCE_OTL_ProjectPlan_v2.md](PCE_OTL_ProjectPlan_v2.md) (exit criteria, Phase 6 boundary) · [PCE_Phase2_MilestoneTracker.md](PCE_Phase2_MilestoneTracker.md) · [PCE_FileFormat_And_Backends.md](PCE_FileFormat_And_Backends.md)

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

---

## D — Phase 6 boundary (do not confuse with M10)

**M10 / `PCE-USD/1`** = USD **layer** with graph payload in **`customLayerData`** and **`/PCE`** placeholder.

**Phase 6** = **portfolio** USD: PCE schemas, **`/Portfolio/...`** hierarchy, composition overrides, timeline — see [PCE_OTL_ProjectPlan_v2.md](PCE_OTL_ProjectPlan_v2.md) §8.

Track Phase 6 work in the main plan / a dedicated Phase 6 doc when that slice starts; **§A (N1–N3)** and **§B–§C (N4–N10)** are complete — next focus live-vendor hardening, optional refactors (e.g. rewiring **M8/M9** nodes onto **`VectorPlug`/`MatrixPlug`**), or Phase 6 prep.

---

## Suggested order

1. **N8–N10** shipped (**`ScalarPlug`**, **`VectorPlug`/`MatrixPlug`**, **`PackMatrixNode`**, **`PCALoadingsNode`**). Optional: connect **`CrossSectionNode` → `PackMatrixNode` → `PCALoadingsNode`** in examples or extend **M8/M9** to prefer the new plugs.

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
