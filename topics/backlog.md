# Topic backlog

Candidate blog topics, newest first within each status. See
[README.md](README.md) for how this file gets populated and used.

**Status values:** `candidate` / `in-progress (post: <slug>)` /
`published (post: <slug>)`.

| Topic | Added | Source | Status | Why |
|---|---|---|---|---|
| LLM-guided residual correction vs. this repo's nearest-neighbor residual memory | 2026-10-16 | [literature/ctrl-2026.pdf](../literature/ctrl-2026.pdf) (CTRL, Kim et al. 2026) | candidate | Demo 2 already does retrieval-based residual correction without an LLM in the loop; CTRL's LLM-guided version is a natural point of comparison — does the LLM add anything the nearest-neighbor version doesn't, or just cost? |
| Does a forecasting foundation model know what it doesn't know, under intervention? | 2026-10-16 | [literature/excitation-2026.pdf](../literature/excitation-2026.pdf) (Amria et al. 2026, "Excitation") | published (post: excitation-for-control) | Published as [Can Your Forecast Predict the Effect of a Decision?](https://medium.com/@eclow/can-your-forecast-predict-the-effect-of-a-decision-7205e481a0d9) Built on a synthetic toy system (no real series has a ground-truth counterfactual to score against); response gain ~0 under unexcited context regardless of context length, climbing to 0.7-0.8 only under excitation. |

<!-- Add rows above this line. The weekly digest routine appends here automatically; feel free to add your own. -->
