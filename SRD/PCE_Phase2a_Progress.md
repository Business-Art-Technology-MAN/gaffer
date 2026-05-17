# Phase 2a — incremental delivery tracker

Parent plan: [PCE_OTL_ProjectPlan_v2.md](PCE_OTL_ProjectPlan_v2.md) (Phase 2).

Phase 2 in the main document is large (stores, matrices, many nodes). **Phase 2a** is a minimal vertical slice: prove **Python `ComputeNode` → `SeriesPlug` output** (hash, compute, serialisation), add **`SeriesPlug` transforms**, then a **scalar volatility** node matching the Phase 2 plan — before ArcticDB or `.pce`. **Later Phase 2 work** is planned in [`PCE_Phase2_MilestoneTracker.md`](PCE_Phase2_MilestoneTracker.md).

| Milestone | Goal | Status | Notes / paths |
| --- | --- | --- | --- |
| **M1** | One Python node outputs a synthetic **constant** `SeriesPlug` (leaf compute on `times` / `values`). Tests: compute + script round-trip. | Done | `python/Gaffer/ConstantSeriesNode.py`, `python/GafferTest/ConstantSeriesNodeTest.py` |
| **M2** | `RollingReturnsNode`: `SeriesPlug` → `SeriesPlug` (log return over `window` bars). | Done | `python/Gaffer/RollingReturnsNode.py`, `python/GafferTest/RollingReturnsNodeTest.py` |
| **M3** | `RealizedVolNode`: **return** `SeriesPlug` → annualized vol (`FloatPlug`; `ScalarPlug` TBD). | Done | `python/Gaffer/RealizedVolNode.py`, `python/GafferTest/RealizedVolNodeTest.py` |

## M1 checklist

- [x] `Gaffer::ConstantSeriesNode` registered (`IECore.registerRunTimeTyped`)
- [x] Imported from `python/Gaffer/__init__.py`
- [x] `affects` / `hash` / `compute` for `out["times"]` and `out["values"]`
- [x] Unit tests: computed series, `ScriptNode.serialise()` / `execute()` round-trip

## M2 checklist

- [x] `Gaffer::RollingReturnsNode` registered and imported from `python/Gaffer/__init__.py`
- [x] `out[k] = log( values[k] / values[k-window] )`, timestamps aligned with end index `k`
- [x] Empty output when `len(in) <= window`; `hash` includes both `in` leaves and `window`
- [x] Tests: direct compute, wiring from `ConstantSeriesNode`, script round-trip

## M3 checklist

- [x] `Gaffer::RealizedVolNode` — trailing sample stdev of `in.values` (ddof=1) × `annualizationFactor`
- [x] `out` is `FloatPlug` until a dedicated `ScalarPlug` exists
- [x] `out == 0` when `len(values) < window` or `window < 2`
- [x] Tests: edge cases, pipeline with `RollingReturnsNode`, serialisation

## Decisions / constraints

- **Leaf outputs:** `SeriesPlug` is a compound `ValuePlug`; evaluation runs on **`times`** and **`values`** child plugs, not on the parent.
- **Inputs:** M1 uses scalar `IntPlug` / `FloatPlug` only (no store). `startTime` / `step` are `IntPlug` (see `NumericPlug<int>`); sufficient for tests; full nanosecond ranges can move to dedicated plugs later.

## Update log

| Date | Change |
| --- | --- |
| 2026-05-16 | M1 implemented: `ConstantSeriesNode`, tests, this tracker created. |
| 2026-05-16 | M2 implemented: `RollingReturnsNode` (pure `math.log`, no NumPy). |
| 2026-05-16 | M3 implemented: `RealizedVolNode` (sample stdev × annualization; `FloatPlug` out). |
| 2026-05-16 | Phase 2 milestone tracker added; **M4** `SeriesCsvReaderNode` (see tracker). |
| 2026-05-16 | **M5** `TimeSeriesStoreNode` stub: see [PCE_Phase2_MilestoneTracker.md](PCE_Phase2_MilestoneTracker.md). |
