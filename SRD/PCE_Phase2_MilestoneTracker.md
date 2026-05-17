# Phase 2 — milestone tracker

**Parent:** [PCE_OTL_ProjectPlan_v2.md](PCE_OTL_ProjectPlan_v2.md) (§ Phase 2).  
**Early slice (done):** [PCE_Phase2a_Progress.md](PCE_Phase2a_Progress.md) — M1–M3 synthetic + transforms + realized vol.  
**`.pce` envelope & ArcticDB:** [PCE_FileFormat_And_Backends.md](PCE_FileFormat_And_Backends.md).

This document is the **working backlog** for the rest of Phase 2: Layer 1 data nodes, Layer 2 factor nodes, shared types, and exit criteria. Update status and log as work lands.

---

## Roadmap (ordered for dependency / risk)

| ID | Milestone | Layer | Goal | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| **M1–M3** | Synthetic + returns + vol | 2 | `SeriesPlug` compute patterns; `FloatPlug` scalar | **Done** | See Phase2a doc |
| **M4** | `SeriesCsvReaderNode` | 1 | `SeriesPlug` from CSV (times + values columns); hash includes path + mtime | **Done** | `python/Gaffer/SeriesCsvReaderNode.py`, `python/GafferTest/SeriesCsvReaderNodeTest.py` |
| **M5** | `TimeSeriesStoreNode` (stub) | 1 | Same plug surface as full store; **memory** or Parquet path backend; optional ArcticDB | **Done** | `python/Gaffer/MarketDataTimeseries.py`, `TimeSeriesStoreNode.py`, `GafferTest/TimeSeriesStoreNodeTest.py` |
| **M6** | `MarketVarNode` (minimal) | 1 | `SeriesPlug` for one macro series; pluggable backend / fixture data | **Done** | `MarketDataMacro` + memory/CSV/Parquet; `GafferTest/MarketPhase2ExtendedTest.py` |
| **M7** | `FactorSeriesNode` (file) | 1 | CSV/Parquet factor returns → `SeriesPlug` | **Done** | `MarketDataFactors` registry + same backends |
| **M8** | `VectorPlug` + `FamaFrenchLoadingsNode` | 2 | Rolling OLS; needs vector type or reuse existing plugs | **Done (no VectorPlug)** | Three `SeriesPlug` factor betas; `MarketMath.linear_least_squares` (no numpy/statsmodels) |
| **M9** | `MatrixPlug` + cross-section | 1–2 | `CrossSectionNode`, `ConnectionMatrixNode` prerequisites | **Done (no MatrixPlug)** | Panel = `rowTimes` + `valuesRowMajor` + `numColumns`; `ConnectionMatrixNode` I/O via `FloatVectorDataPlug` |
| **M10** | Phase 2 **integration** | — | Graph: data → `RollingReturnsNode` → `RealizedVolNode`; script/`.pce` round-trip | **Done** | **`PCE-USD/1`** default (`savePceGraphFile` USDA + `customLayerData`); legacy **`PCE-GRAPH/1`** via `graphFormat="legacy"`. See [`PCE_FileFormat_And_Backends.md`](PCE_FileFormat_And_Backends.md). |

**Deferred (Phase 2b / later):** `IVSurfaceNode` + `SurfacePlug`; `ScalarPlug` alias; `KyleLambdaNode`; full ArcticDB.

---

## Phase 2 exit criterion (from main plan)

> A complete Layer 1→2 pipeline in the node graph: **data** → `RollingReturnsNode` → `RealizedVolNode`; results inspectable; **serialisation** restores the graph.

Use **M4 + M10** as the first end-to-end story before M5–M9 depth.

---

## M4 checklist (`SeriesCsvReaderNode`)

- [x] `Gaffer::SeriesCsvReaderNode` registered; imported in `python/Gaffer/__init__.py`
- [x] Plugs: `filePath`, `hasHeader`, `timeColumn`, `valueColumn`, `delimiter`; `out` `SeriesPlug`
- [x] `hash` includes file mtime when present; `compute` fills `out["times"]` / `out["values"]`
- [x] Tests: temp CSV, pipeline to `RollingReturnsNode`, serialisation with fixed path

## M5 checklist (`TimeSeriesStoreNode` stub)

- [x] Plugs: `instrumentId`, `field`, `lookback`, `barType`, `adjust`, `backend`, `resourcePath`, `refreshCount`; `out` `SeriesPlug`
- [x] **memory**: `MarketDataTimeseries.registerSeries` / `getSeries`; `refreshCount` in hash (manual bump when registry changes)
- [x] **parquet**: `time` + value column (`field` or `value`); requires **pyarrow**; hash includes file mtime
- [x] **arcticdb**: **`ArcticBackend`** + `arcticLibrary` plug; requires PyPI `arcticdb`/`pandas`; optional `testArcticDbReadsLmdb`
- [x] Point-in-time: `MarketDataTimeseries.PCE_TIME_CONTEXT_KEY` on `Context` filters `time <=` value; included in hash
- [x] Tests: lookback, context, serialisation; parquet `skipUnless` pyarrow

---

## Update log

| Date | Change |
| --- | --- |
| 2026-05-16 | Tracker created; M4 = CSV reader implemented + tested. |
| 2026-05-16 | M5: `TimeSeriesStoreNode` stub (memory + optional Parquet + context PIT); `MarketDataTimeseries` registry. |
| 2026-05-16 | M6–M9: `MarketVarNode`, `FactorSeriesNode`, `CrossSectionNode`, `FamaFrenchLoadingsNode`, `ConnectionMatrixNode`; shared `MarketDataIO` / `MarketMath`. M10 script test only. |
| 2026-05-16 | **PceGraphIO** (`PCE-GRAPH/1`) + **ArcticDB** read on `TimeSeriesStoreNode` (`arcticLibrary`); tracker [`PCE_FileFormat_And_Backends.md`](PCE_FileFormat_And_Backends.md). |
| 2026-05-16 | **M10 closeout:** **`PCE-USD/1`** — `.pce` written as USDA (temp `.usda` + replace) with payload in root `customLayerData`; default when `pxr` available. |
