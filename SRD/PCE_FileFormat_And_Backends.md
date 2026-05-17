# PCE — file format & real backends

**Purpose:** Track work on **(A)** graph persistence beyond raw `ScriptNode.serialise()` and **(B)** production-ish data stores (ArcticDB first).  
**Parent docs:** [PCE_OTL_ProjectPlan_v2.md](PCE_OTL_ProjectPlan_v2.md) (Phase 2 exit / Phase 6 `.pce`), [PCE_Phase2_MilestoneTracker.md](PCE_Phase2_MilestoneTracker.md) (M10).  
**Code:** `python/Gaffer/PceGraphIO.py`, `python/Gaffer/ArcticBackend.py`, `python/GafferTest/PceGraphIOTest.py`.

---

## A — `.pce` / graph file format

| Stage | Goal | Status | Notes |
| --- | --- | --- | --- |
| **A0** | Versioned envelope + JSON metadata + embedded Gaffer script body | **Done** | Legacy: `PCE-GRAPH/1` UTF-8 text in `PceGraphIO` (`graphFormat="legacy"`) |
| **A0b** | **USD-native** layer (default when OpenUSD is available) | **Done** | **`PCE-USD/1`**: valid USDA on disk; `customLayerData` keys `pce:format`, `pce:metadataJson`, `pce:gafferSerialisedScript`; `/PCE` Xform defaultPrim |
| **A1** | Tests: round-trip `save` → new `ScriptNode` → `load` | **Done** | `GafferTest/PceGraphIOTest.py` (USD + legacy) |
| **A2** | GUI / app: **File → Save .pce** (calls A0) | Not started | Wire in MarketLab UI when shell exists |
| **A3** | USD portfolio / diagrams (Phase 6): PCE schemas + prims beside `/PCE` | Not started | Builds on A0b; not required for M10 |

**Design (legacy — A0):**

- Line 1: format id `PCE-GRAPH/1`.
- Line 2: single-line JSON object (e.g. `app`, `created`, `tags`); may be `{}`.
- Line 3: separator `---`.
- Remainder: Python source produced by `ScriptNode.serialise()` (same as today’s graphs).

**Design (USD — A0b):**

- On disk the file is **USDA** (written via a temporary `.usda` then `os.replace` to `*.pce` because USD picks readers by extension).
- Root layer **`customLayerData`**: `pce:format` = `PCE-USD/1`, `pce:metadataJson` = same JSON as legacy line 2, `pce:gafferSerialisedScript` = `serialise()` body.
- Stage includes **`/PCE`** `Xform` as **defaultPrim** as a placeholder for future portfolio prims (A3).

**API:** `savePceGraphFile(..., graphFormat="usd"|"legacy")`. Default **`usd`** raises **`RuntimeError`** if `pxr` is not importable (no-USD builds must pass **`graphFormat="legacy"`**). `loadPceGraphFile` tries USD first, then legacy envelope.

---

## B — Real backends

| Backend | Node(s) | Status | Notes |
| --- | --- | --- | --- |
| **ArcticDB** | `TimeSeriesStoreNode` (`backend == "arcticdb"`) | **v1 read done** | `ArcticBackend.read_series_for_store`; plug `arcticLibrary` (default `pce`) |
| **Live macro / factor APIs** | `MarketVarNode`, `FactorSeriesNode` | Not started | Needs creds, vendor choice |
| **Parquet** | Already supported | Done | pyarrow |

**ArcticDB contract (v1):**

- `resourcePath`: Arctic URI (e.g. `lmdb://C:/data/my_store` or LMDB directory per [ArcticDB docs](https://docs.arcticdb.io/)).
- `arcticLibrary` plug: library name (default `pce`).
- `instrumentId`: symbol key passed to `library.read(instrumentId)`.
- `field`: column name for values; if missing, tries `value`, then first numeric column.
- Index: `DatetimeIndex` → int64 **nanoseconds** epoch for `times`; integer index → used as bar ids.
- Hash: URI, library, symbol, field, `refreshCount`, `lookback`, bar metadata, PIT context key (no LMDB mtime — use `refreshCount` to bust cache after writes).

**CI:** Tests that need ArcticDB use `unittest.skipUnless(arcticdb_available, ...)` so default CI stays green without the package.

---

## Checklists

### A0–A1 / A0b

- [x] `PceGraphIO.save` / `load` helpers + constants (`PCE-GRAPH/1`, **`PCE-USD/1`**)
- [x] Unit test round-trip (legacy + USD when `pxr` available)
- [ ] Document `MarketLab.cmd` / app entry for save path
- [ ] A2 UI hook

### ArcticDB v1

- [x] `ArcticBackend.read_series_for_store`
- [x] `TimeSeriesStoreNode` plugs + `compute` integration (`arcticLibrary`)
- [x] Test: import missing → clear error
- [x] Test: optional write/read LMDB (skip if no `arcticdb`)

---

## Running unit tests (`MarketLab` / `gaffer test`)

Names are passed to `unittest.TestLoader.loadTestsFromName` — use **full dotted paths**.

| Goal | Command |
| --- | --- |
| Whole `TimeSeriesStoreNode` tests | `MarketLab.cmd test GafferTest.TimeSeriesStoreNodeTest` |
| One method | `MarketLab.cmd test GafferTest.TimeSeriesStoreNodeTest.TimeSeriesStoreNodeTest.testArcticDbRequiresUriOrPackage` |
| PCE graph envelope | `MarketLab.cmd test GafferTest.PceGraphIOTest` |

**`AttributeError: type object 'TimeSeriesStoreNodeTest' has no attribute 'TimeSeriesStoreNodeTest'`** on the one-method form almost always means **`import GafferTest.TimeSeriesStoreNodeTest` failed** in the installed tree, so the loader fell back to the `GafferTest` package and treated one extra `TimeSeriesStoreNodeTest` as a nested attribute. Re-sync **`python/GafferTest/`** and **`python/Gaffer/`** into your install (e.g. rebuild / copy into `gaffer-build-…`), then verify `import GafferTest.TimeSeriesStoreNodeTest` works from a shell that loads the same `GAFFER_ROOT` / `PYTHONPATH` as `MarketLab.cmd`.

---

## Update log

| Date | Change |
| --- | --- |
| 2026-05-16 | A0/A1 shipped (`PceGraphIO`, tests). ArcticDB LMDB read + `arcticLibrary` plug + optional integration test. |
| 2026-05-16 | **A0b / M10:** `PCE-USD/1` default save path; legacy retained; `usdAvailableForPce()` exported from `Gaffer`. |
