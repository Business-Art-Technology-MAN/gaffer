# Phase 6 — milestone tracker (PCE USD portfolio stage)



**Parent:** [PCE_OTL_ProjectPlan_v2.md](PCE_OTL_ProjectPlan_v2.md) §8 *Phase 6 — PCE Stage: OpenUSD Backend*.  

**Active branch:** `marketlab/phase6`.  

**Depends on:** **PCE-USD/1** (`.pce` as USDA + `customLayerData`), **Phase 5** portfolio nodes.  

**Precedes:** Phase 7 chart plugin ([§9](PCE_OTL_ProjectPlan_v2.md)).



v0.1 focuses on **Python-first** stage IO and **typed portfolio prims** without **usdGenSchema** (generated API schemas deferred). Instrument types use `Scope` + `pce:*` attributes; `PCE-USD/2` is backward-compatible with **PCE-USD/1** readers that ignore extra `customLayerData` keys.



---



## Roadmap (dependency order)



| ID | Milestone | Goal | Status | Notes |

| --- | --- | --- | --- | --- |

| **P6-M1** | **`PCE-USD/2` file format** | Extend :func:`Gaffer.savePceGraphFile` / :func:`Gaffer.loadPceGraphFile`: `pce:format` **PCE-USD/2** when portfolio or sublayers present; inject `pcePortfolioStage`, `pceSublayerPaths`, `pceTimeLine` into loaded metadata. | **Done** | `python/Gaffer/PceGraphIO.py`. |

| **P6-M2** | **`/Portfolio` prim hierarchy** | Paths like `/Portfolio/Futures/ES1_`, `/Portfolio/Rates/ZN1_`, `/Portfolio/FX/EURUSD`; kinds: EquityAsset, BondAsset, FuturesAsset, OptionsAsset, FXForward. | **Done** | `python/Gaffer/PcePortfolioStage.py` |

| **P6-M3** | **Layer stack (risk overrides)** | Root `subLayerPaths` + JSON mirror in `customLayerData` for tools that do not walk USD. | **Done** | `savePceGraphFile(..., sublayerPaths=[...])` |

| **P6-M4** | **TimeCode ↔ market time** | `PceTimeSample`, `pce:timeLineJson`; Gaffer `Context` variable **:data:`Gaffer.PCE_CONTEXT_MARKET_TIME_NS`** for timeline scrubbing (Phase 7 wires UI). | **Done** | `apply_market_time_to_context` |

| **P6-M5** | **Execution delegate registry (stub)** | Named **Backtest** / **Paper** / **Live** hooks (Hydra-style naming); Phase 8 implements `evaluate`. | **Done** | `python/Gaffer/PceExecutionDelegates.py` |

| **P6-M6** | **Tests** | Round-trip graph + three-name portfolio; sublayer path; v1 default unchanged. | **Done** | `Phase6Test`, `PceGraphIOTest.testUsdV1FormatWhenGraphOnly` |



---



## Exit criterion (from main plan)



> A .pce file saves and restores the complete portfolio stage including node graph, instrument prims, and layer-based risk overrides. Scrubbing the timeline re-evaluates the shader network at different market dates.



**v0.1:** round-trip **proven in tests** for graph + instruments + sublayer list + timeline JSON; **scrubbing** = context variable documented and tested (editor integration = Phase 7).



---



## Deferred (human review / later)



Consolidated polish / backlog: [PCE_Polish_And_Deferred_Work.md](PCE_Polish_And_Deferred_Work.md) §3.1.

- **usdGenSchema** PCE API (`PCE_EquityAsset`, …) and Composition arcs beyond `subLayerPaths`.

- **Hydra** render-delegate binding to real execution engines.

- **SceneHierarchy** panel re-label as PCE portfolio tree (UI).



---



## Update log



| Date | Change |

| --- | --- |

| 2026-05-18 | Initial **PCE-USD/2** + `PcePortfolioStage` + delegate stubs + `Phase6Test`. |

