# Topic backlog

Candidate blog topics, newest first within each status. See
[README.md](README.md) for how this file gets populated and used.

**Status values:** `candidate` / `in-progress (post: <slug>)` /
`published (post: <slug>)`.

| Topic | Added | Source | Status | Why |
|---|---|---|---|---|
| LLM-guided residual correction vs. this repo's nearest-neighbor residual memory | 2026-10-16 | [literature/ctrl-2026.pdf](../literature/ctrl-2026.pdf) (CTRL, Kim et al. 2026) | candidate | Demo 2 already does retrieval-based residual correction without an LLM in the loop; CTRL's LLM-guided version is a natural point of comparison — does the LLM add anything the nearest-neighbor version doesn't, or just cost? |
| Does a forecasting foundation model know what it doesn't know, under intervention? | 2026-10-16 | [literature/excitation-2026.pdf](../literature/excitation-2026.pdf) (Amria et al. 2026, "Excitation") | candidate | A genuinely new angle for this repo: every demo so far evaluates passive forecasting accuracy. This paper's point — low forecast error doesn't mean the model has learned how the system *responds to actions* — doesn't obviously fit the existing demo format and would need real thought before committing to it. |

| Does Chronos-2 "collapse" to a flat forecast on SPY? | 2026-10-19 | [Forecast Collapse in TSFMs](https://arxiv.org/pdf/2608.14106) (Wan, Ma et al. 2026) | candidate | SPY is already this repo's low-signal series; measure forecast dispersion and directional accuracy vs naive/ARIMA with the existing harness. Single-series analogue only — the paper's cross-sectional stock-ranking claim isn't testable here. |
| Known-future covariates: TSFM vs. hand-built Fourier/calendar features on CISO | 2026-10-19 | [t0](https://arxiv.org/pdf/2609.24559) (The Forecasting Company 2026) | candidate | Natural follow-on to Demo 3: does a pretrained model using covariates beat a lag+Fourier learner, and at what runtime cost? |
| Coarse shape model + expensive refiner (coarse-to-fine hybrids) | 2026-10-19 | [SCALER](https://arxiv.org/pdf/2608.08675) (Le et al., KDD 2026) | candidate | Small analogue: seasonal-naive/Fourier shape plus Chronos or residual-memory refinement; accuracy vs compute is the story. Don't reproduce SCALER's LLM token refinement. |

<!-- Add rows above this line. The weekly digest routine appends here automatically; feel free to add your own. -->
