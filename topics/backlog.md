# Topic backlog

Candidate blog topics, newest first within each status. See
[README.md](README.md) for how this file gets populated and used.

**Status values:** `candidate` / `in-progress (post: <slug>)` /
`published (post: <slug>)`.

| Topic | Added | Source | Status | Why |
|---|---|---|---|---|
| Do "equally accurate" models forecast the same trajectory? | 2026-10-16 | [Rashomon sets](https://arxiv.org/abs/2605.05218); [Temporal Predictive Multiplicity](https://arxiv.org/abs/2610.09994) (title only) | candidate | Models tied on MASE can still disagree on forecast paths at longer horizons; the existing harness can measure that disagreement directly on CISO/SPY. |
| Delay-aware test-time adaptation: what can you update on, and when? | 2026-10-16 | [Training on the Future](https://arxiv.org/abs/2610.12232) (title only); [TAFAS](https://arxiv.org/html/2501.04970v1) | candidate | Small causal online correction using only targets already revealed at each origin, compared against a leaky variant — a natural no-lookahead test. |
| Contamination and covariates: how much of a zero-shot win is real? | 2026-10-16 | [Pan & Ezzat 2026](https://arxiv.org/abs/2607.02623) | candidate | Re-examine Post 01's zero-shot vs. local result with/without covariates and on a likely-uncontaminated period. |
| Retrieval at the input vs. retrieval at the residual | 2026-10-16 | [SteerCast](https://arxiv.org/abs/2610.11229); [ROAR](https://arxiv.org/abs/2605.24911) (both title only) | candidate | Contrasts Demo 2's residual memory with retrieval-as-context for a foundation model; check abstracts before committing. |
| LLM-guided residual correction vs. this repo's nearest-neighbor residual memory | 2026-10-16 | [literature/ctrl-2026.pdf](../literature/ctrl-2026.pdf) (CTRL, Kim et al. 2026) | candidate | Demo 2 already does retrieval-based residual correction without an LLM in the loop; CTRL's LLM-guided version is a natural point of comparison — does the LLM add anything the nearest-neighbor version doesn't, or just cost? |
| Does a forecasting foundation model know what it doesn't know, under intervention? | 2026-10-16 | [literature/excitation-2026.pdf](../literature/excitation-2026.pdf) (Amria et al. 2026, "Excitation") | candidate | A genuinely new angle for this repo: every demo so far evaluates passive forecasting accuracy. This paper's point — low forecast error doesn't mean the model has learned how the system *responds to actions* — doesn't obviously fit the existing demo format and would need real thought before committing to it. |

<!-- Add rows above this line. The weekly digest routine appends here automatically; feel free to add your own. -->
