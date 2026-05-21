# PCE — polish & backlog work stream (active tracker)

**Purpose:** Executable backlog derived from [PCE_Polish_And_Deferred_Work.md](PCE_Polish_And_Deferred_Work.md). Each row is a **PB-M*** milestone with status; deep deferrals stay in the parent doc §3.

**Parent:** [PCE_OTL_ProjectPlan_v2.md](PCE_OTL_ProjectPlan_v2.md) · [PCE_NextSteps.md](PCE_NextSteps.md) · [PCE_Polish_And_Deferred_Work.md](PCE_Polish_And_Deferred_Work.md).

**Principles:** Prefer **small PR-sized** items; **no** new C++ types here unless a separate review; **PCE-USD/2** menu saves use existing format (review gate §12.6 item 3 if extending `customLayerData` keys beyond current **PCE-USD/2**).

---

## Roadmap (polish stream)

| ID | Theme | Deliverable | Status | Notes / owner |
| --- | --- | --- | --- | --- |
| **PB-M1** | Plan hygiene | Refresh [PCE_NextSteps.md](PCE_NextSteps.md) **Immediate next** now that Phase 4–6 v0.1 are shipped; point primary path to Phase 7 + verification. | **Done** | This work stream. |
| **PB-M2** | Layer 5 | **`PortfolioAggregatorNode`**: warn on **`instrumentIds`** length ≠ **`SignalClosurePlug`** count; warn on non-SigC array slots (skipped). Context **`OTL_PORTFOLIO_INPUT`**. | **Done** | `PortfolioAggregatorNode.py`; test in `Phase5Test`. |
| **PB-M3** | File / IO | **File → PCE**: optional **Save Graph As (PCE-USD/2 portfolio shell…)** — writes graph + empty **`PcePortfolioStagePayload`** so `/Portfolio` exists (requires **pxr**). | **Done** | `PceFileMenu.py`. |
| **PB-M4** | Docs | [PCE_FileFormat_And_Backends.md](PCE_FileFormat_And_Backends.md): short **install / repo sync** note for Python tests. | **Done** | |
| **PB-M5** | Index | Link this tracker from polish doc + plan snapshot line. | **Done** | |

---

## Next up (not started — pull into PB-M6+)

| Candidate | Source |
| --- | --- |
| **WeightVectorPlugValueWidget** editing / export | Polish §2.2 |
| **File → PCE** load/store portfolio metadata on script variables | Polish §2.1 |
| **M8/M9** refactor to **`VectorPlug`/`MatrixPlug`** | NextSteps optional |
| **Arctic** on-graph publish node | Polish §2.5 |
| **usdGenSchema** / Hydra / hierarchy panel | Polish §3.1 |
| **GafferPCEChart** Phase 7 | Plan §9 |

---

## Update log

| Date | Change |
| --- | --- |
| 2026-05-18 | **PB-M1–M5** initial: tracker file, NextSteps, aggregator warnings, PCE menu shell save, FileFormat note, cross-links. |
| 2026-05-18 | Confirmed implementation: `OTL_PORTFOLIO_INPUT` + `Phase5Test.testPortfolioInputMismatchWarning`; **File → PCE** shell save in `PceFileMenu.saveGraphAsUsdShell`. |
