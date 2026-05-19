# PCE — polish and deferred work (backlog)

**Purpose:** Single place for **near-term polish**, **explicit deferrals**, **plan deltas**, and **follow-ups** that are scattered across phase trackers and implementation notes. It does not replace milestone trackers; it **indexes** them.

**Parent:** [PCE_OTL_ProjectPlan_v2.md](PCE_OTL_ProjectPlan_v2.md) · [PCE_NextSteps.md](PCE_NextSteps.md) · phase trackers ([Phase 5](PCE_Phase5_MilestoneTracker.md), [Phase 6](PCE_Phase6_MilestoneTracker.md), [Phase 4](PCE_Phase4_MilestoneTracker.md)).

**Update:** Append rows to the change log when items ship or are re-scoped; keep bullets honest.

---

## 1. Human review gates (plan §12.6)

Before merging, **human review** is required regardless of tests passing:

| # | Area |
| --- | --- |
| 1 | Any new **C++ type registration** |
| 2 | Any change to the **OTL grammar** |
| 3 | Any change to **PCE stage serialisation** (e.g. **`PCE-USD/1`**, **`PCE-USD/2`**, `customLayerData` keys, prim layout) |
| 4 | Any **LiveDelegate** (or equivalent) code path that can **generate real orders** |

---

## 2. Polish (incremental improvements)

Items that **work today** but deserve tighter UX, consistency, or docs.

### 2.1 File / graph / stage IO

- **File → PCE → Save/Open:** Still saves the **node graph** only (`graphFormat=usd|legacy`). **Portfolio stage** (**`PCE-USD/2`**) is available via **`Gaffer.savePceGraphFile(..., portfolio=..., sublayerPaths=...)`** in Python; wiring **optional portfolio payload** from UI, script variables, or a dedicated dialog is polish.
- **Install vs repo:** Python modules (e.g. **`GafferTest`**) must be **copied or rebuilt** into the install prefix after edits; document in onboarding if teams hit stale-test confusion.
- **USDA assertions in tests:** On-disk text uses **`def Xform "Portfolio"`** etc., not always a literal **`/Portfolio`** substring; tests should stay aligned with **USD export** spelling.

### 2.2 Layer 5 portfolio

- **`instrumentIds` vs `signals` array length:** Aggregator should **validate, clamp, or warn** consistently when lengths diverge (see Phase 5 engineering notes).
- **`WeightVectorPlugValueWidget`:** Read-only table is v0.1; optional **edit / drag reorder**, **export**, or **colour** polish later.
- **Optimizers:** **`hrp`** path may use **inverse-vol on diagonal** as a stand-in when full hierarchical risk parity is not wired; **`Riskfolio` / full HRP** remain optional enhancements behind lazy imports.
- **`ArraySignalPlug` + mixed element types:** If **`ArrayPlug`** slots are not all **`SignalClosurePlug`**, **ID ↔ weight** pairing could deserialise; document or guard in aggregator.

### 2.3 Layer 6 USD stage

- **Prim representation:** v0.1 uses **`Scope` + `pce:*`** attributes. **Polish** = richer **metadata**, **kind-specific** optional attrs, or migration to **generated schemas** (see §3).
- **`open_pce_usda_stage`:** In-memory **`TransferContent`** path exists because **`.pce`** may not **`Usd.Stage.Open`** everywhere; surface in user-facing docs if needed.

### 2.4 OTL / Layer 4

- **OTL stdlib:** Stubs / param-only shaders; **series-backed** OTL and fuller library expansion per plan remain incremental polish on Track B.
- **`compile_otl_network_for_pce`:** Stub hook to **PCE stage** — tighten when stage semantics stabilise.

### 2.5 Phase 2 / data plane

- **Live data:** Broader vendors than **HTTP CSV + FRED** ([plan table § implementation status](PCE_OTL_ProjectPlan_v2.md)).
- **Arctic:** **On-graph** publish nodes (beyond **`ArcticBackend`** helpers).

### 2.6 Refactors (optional)

- Rewire **M8/M9**-era nodes (**`FamaFrenchLoadingsNode`**, **`CrossSectionNode`**, …) to prefer **`VectorPlug` / `MatrixPlug`** where it simplifies scripts ([PCE_NextSteps.md](PCE_NextSteps.md) § Immediate next).

---

## 3. Deferred work (larger slices)

Grouped by theme; many map to **Phase 7+** in the main plan.

### 3.1 USD / portfolio stage (Phase 6+)

- **`usdGenSchema`**-style **PCE API** types (**`PCE_EquityAsset`**, bond, futures, options, FX) instead of generic **`Scope` + `pce:*`**.
- **Composition** beyond root **`subLayerPaths`**: stronger/weaker layer ordering docs, references, **variant** sets, institution-specific patterns.
- **Hydra** “execution delegate” alignment with **real** preview/backtest/live engines (naming stub exists in **`PceExecutionDelegates.py`**).
- **Scene / hierarchy panel:** Repurpose or relabel **Gaffer SceneHierarchy** as a **PCE portfolio tree** for **`/Portfolio/...`**.
- **Timeline scrubbing (full exit):** **`PCE_CONTEXT_MARKET_TIME_NS`** is implemented; **editor / chart** wiring is **Phase 7** (see plan §9).

### 3.2 OTL / shading

- OTL grammar or **type system** extensions per **OTL v0.1** spec amendments (review gate applies).
- Richer **`.otl` stdlib** and **series** types in OTL where the spec allows.

### 3.3 Execution & integration (Phase 8–9)

- **BacktestDelegate**, **PaperDelegate**, **LiveDelegate:** Real **`evaluate(stage, context)`** and risk gates (**Phase 8**).
- **Node menu / palette**, **typed wire colours**, **OTL error panel**, **example `.pce` portfolios**, **shader library browser** (**Phase 9**).
- **Performance** budgets (chart redraw, backtest duration) per plan.

### 3.4 Plan-documented deltas (Phase 1 scope)

From [PCE_OTL_ProjectPlan_v2.md](PCE_OTL_ProjectPlan_v2.md) implementation table:

- **Not** shipping USD **per-sample `timeSamples`** on a single float vector as originally envisaged in one plan variant.
- **`MarketContext`**: implemented as a **plug type**, not a separate always-injected struct.

---

## 4. Resolved tech debt (historical)

- **Compound / `ValuePlug` acceptance:** **`ValuePlug::acceptsInput`** uses **`typeId()`** with **`Plug::acceptsInput`** first; see [PCE_NextSteps.md](PCE_NextSteps.md) § Tech debt note.

---

## 5. Suggested verification commands

| Area | Command |
| --- | --- |
| Phase 5 | `MarketLab.cmd test GafferTest.Phase5Test GafferTest.MarketDataPlugsTest` |
| Phase 6 + PCE IO | `MarketLab.cmd test GafferTest.Phase6Test GafferTest.PceGraphIOTest` (needs **pxr**) |
| Phase 2 story | `MarketLab.cmd test GafferTest.Phase2ExitCriterionTest` |

---

## 6. Change log

| Date | Change |
| --- | --- |
| 2026-05-18 | Initial backlog: human gates, polish (IO UI, L5/L6/OTL/data), deferred USD/OTL/Phase 7–9, plan deltas, verify commands. |
