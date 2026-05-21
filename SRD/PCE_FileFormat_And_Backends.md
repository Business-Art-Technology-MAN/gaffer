# PCE — file format & real backends

**Purpose:** Track work on **(A)** graph persistence beyond raw `ScriptNode.serialise()` and **(B)** production-ish data stores (ArcticDB first).  
**Parent docs:** [PCE_OTL_ProjectPlan_v2.md](PCE_OTL_ProjectPlan_v2.md) (Phase 2 exit / Phase 6 `.pce`), [PCE_Phase2_MilestoneTracker.md](PCE_Phase2_MilestoneTracker.md) (M10).  
**Code:** `python/Gaffer/PceGraphIO.py`, `python/GafferUI/PceFileMenu.py`, `python/Gaffer/ArcticBackend.py`, `python/GafferTest/PceGraphIOTest.py`, `python/GafferTest/Phase2ExitCriterionTest.py`.

---

## A — `.pce` / graph file format

| Stage | Goal | Status | Notes |
| --- | --- | --- | --- |
| **A0** | Versioned envelope + JSON metadata + embedded Gaffer script body | **Done** | Legacy: `PCE-GRAPH/1` UTF-8 text in `PceGraphIO` (`graphFormat="legacy"`) |
| **A0b** | **USD-native** layer (default when OpenUSD is available) | **Done** | **`PCE-USD/1`**: valid USDA on disk; `customLayerData` keys `pce:format`, `pce:metadataJson`, `pce:gafferSerialisedScript`; `/PCE` Xform defaultPrim |
| **A1** | Tests: round-trip `save` → new `ScriptNode` → `load` | **Done** | `GafferTest/PceGraphIOTest.py` (USD + legacy) |
| **A2** | GUI: **File → PCE → Save/Open** | **Done** | `python/GafferUI/PceFileMenu.py`; registered in `startup/gui/menus.py` (MarketLab gui). Uses `usd` when `usdAvailableForPce()`, else `legacy`. |
| **A3** | USD portfolio / diagrams (Phase 6): PCE schemas + prims beside `/PCE` | Not started | Builds on A0b; not required for M10 |

**App entry:** Launch the graph UI with **`MarketLab.cmd`** (Windows, repo `bin/`) or **`marketlab`** (Unix). **`.pce` save/load** lives under **File → PCE** (not the main **File → Save**, which remains **`.gfr`**).

**Install / repo sync:** Edits under `python/Gaffer/` or `python/GafferTest/` are not picked up by **`MarketLab.cmd test …`** until those trees are **copied or rebuilt** into the install prefix the launcher uses. If a new test module or method “does not exist”, re-sync before debugging the test itself.

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
| **ArcticDB** | `TimeSeriesStoreNode` (`backend == "arcticdb"`) + `ArcticBackend` helpers | **Read + write/append + catalog (N4)** | Read: `read_series_for_store`. **Publish:** `write_series_for_store`, `append_series_for_store`, `list_libraries`, `list_symbols`. Plug `arcticLibrary` (default `pce`). See §B contract. |
| **Live macro / factor APIs** | `MarketVarNode`, `FactorSeriesNode` | **N5 — `httpcsv` + `fred`** | **`httpcsv`:** `resourcePath` = `https://…` CSV (same column plugs as CSV). **`fred`:** FRED series id in `variableName` / `factorId`; key from **`PCE_FRED_API_KEY`** or **`FRED_API_KEY`** (not stored in graphs). Times: **YYYYMMDD** ints. Bust cache via **`refreshCount`**. |
| **Parquet** | Already supported | Done | pyarrow |

**ArcticDB contract (read + N4 publish):**

- `resourcePath`: Arctic URI (e.g. `lmdb://C:/data/my_store` or LMDB directory per [ArcticDB docs](https://docs.arcticdb.io/)).
- `arcticLibrary` plug: library name (default `pce`).
- `instrumentId`: symbol key passed to `library.read(instrumentId)`.
- `field`: column name for values; if missing, tries `value`, then first numeric column.
- Index: `DatetimeIndex` → int64 **nanoseconds** epoch for `times`; integer index → used as bar ids.
- Hash: URI, library, symbol, field, `refreshCount`, `lookback`, bar metadata, PIT context key (no LMDB mtime — use `refreshCount` to bust cache after writes).

**N4 — publishing & discovery** (`python/Gaffer/ArcticBackend.py`), for scripts / tools / future nodes:

- `write_series_for_store(uri, library, symbol, times, values, valueColumn, createLibrary=True)` — `library.write`.
- `append_series_for_store(uri, library, symbol, times, values, valueColumn)` — `library.append` (symbol must exist; index must continue per ArcticDB rules).
- `list_libraries(uri)`, `list_symbols(uri, library)` — sorted names.

**CI:** Tests that need ArcticDB use `unittest.skipUnless(arcticdb_available, ...)` so default CI stays green without the package.

---

## Checklists

### A0–A1 / A0b

- [x] `PceGraphIO.save` / `load` helpers + constants (`PCE-GRAPH/1`, **`PCE-USD/1`**)
- [x] Unit test round-trip (legacy + USD when `pxr` available)
- [x] Document `MarketLab.cmd` / **File → PCE** for `.pce` (main **File → Save** stays `.gfr`)
- [x] A2 UI hook (`GafferUI.PceFileMenu` + `startup/gui/menus.py`)

### ArcticDB v1 + N4

- [x] `ArcticBackend.read_series_for_store`
- [x] `ArcticBackend.write_series_for_store` / `append_series_for_store` / `list_libraries` / `list_symbols`
- [x] `TimeSeriesStoreNode` plugs + `compute` integration (`arcticLibrary`)
- [x] Test: import missing → clear error
- [x] Test: optional LMDB read / write / append / list (`skipUnless` `arcticdb`)

### N5 — live series (macro + factors)

- [x] `MarketDataIO.read_series_http_csv` / `read_series_fred_observations` / `fred_api_key_from_environ`
- [x] `MarketVarNode` / `FactorSeriesNode` backends **`httpcsv`**, **`fred`**
- [x] Tests: loopback HTTP CSV; FRED smoke `skipUnless` key; FRED empty-key error

---

## Running unit tests (`MarketLab` / `gaffer test`)

Names are passed to `unittest.TestLoader.loadTestsFromName` — use **full dotted paths**.

| Goal | Command |
| --- | --- |
| Whole `TimeSeriesStoreNode` tests | `MarketLab.cmd test GafferTest.TimeSeriesStoreNodeTest` |
| One method | `MarketLab.cmd test GafferTest.TimeSeriesStoreNodeTest.testArcticDbRequiresUriOrPackage` |
| PCE graph envelope | `MarketLab.cmd test GafferTest.PceGraphIOTest` |
| Phase 2 exit story (whole class) | `MarketLab.cmd test GafferTest.Phase2ExitCriterionTest` |
| Phase 2 exit story (one method) | `MarketLab.cmd test GafferTest.Phase2ExitCriterionTest.testCsvToRollingReturnsToRealizedVolAndPceRoundTrip` |
| N5 HTTP / FRED backends | `MarketLab.cmd test GafferTest.MarketPhase2ExtendedTest` |
| Phase 5 portfolio / plugs | `MarketLab.cmd test GafferTest.Phase5Test GafferTest.MarketDataPlugsTest` |
| Phase 6 PCE-USD/2 stage | `MarketLab.cmd test GafferTest.Phase6Test GafferTest.PceGraphIOTest` |

**`AttributeError: type object 'SomeTest' has no attribute 'SomeTest'`** on a **four-part** name like ``GafferTest.FooTest.FooTest.test_bar`` almost always means **`FooTest` was already resolved to the class** (see ``GafferTest/__init__.py`` re-exports). Use **three** segments: ``GafferTest.FooTest.test_bar``. If **import** of the module actually failed, you get a different error — re-sync/rebuild so ``python/GafferTest/FooTest.py`` is in the install.

---

## Update log

| Date | Change |
| --- | --- |
| 2026-05-16 | A0/A1 shipped (`PceGraphIO`, tests). ArcticDB LMDB read + `arcticLibrary` plug + optional integration test. |
| 2026-05-16 | **A2 / N1 / N2 / N3:** `GafferUI/PceFileMenu.py` (**File → PCE**); Phase 2 exit test `GafferTest/Phase2ExitCriterionTest.py`; docs updated. |
| 2026-05-16 | **N4:** `ArcticBackend` write/append + `list_libraries` / `list_symbols`; `TimeSeriesStoreNodeTest` LMDB coverage. |
| 2026-05-16 | **N5:** `httpcsv` / `fred` on `MarketVarNode` + `FactorSeriesNode`; `MarketPhase2ExtendedTest` + `MarketDataN5Test`. |
