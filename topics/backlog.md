# Topic backlog

Candidate blog topics, newest first within each status. See
[README.md](README.md) for how this file gets populated and used.

**Status values:** `candidate` / `in-progress (post: <slug>)` /
`published (post: <slug>)`.

| Topic | Added | Source | Status | Why |
|---|---|---|---|---|
| LLM-guided residual correction vs. this repo's nearest-neighbor residual memory | 2026-10-16 | [literature/ctrl-2026.pdf](../literature/ctrl-2026.pdf) (CTRL, Kim et al. 2026) | candidate | Demo 2 already does retrieval-based residual correction without an LLM in the loop; CTRL's LLM-guided version is a natural point of comparison — does the LLM add anything the nearest-neighbor version doesn't, or just cost? |
| Does a forecasting foundation model know what it doesn't know, under intervention? | 2026-10-16 | [literature/excitation-2026.pdf](../literature/excitation-2026.pdf) (Amria et al. 2026, "Excitation") | published (post: excitation-for-control) | Published as [Can Your Forecast Predict the Effect of a Decision?](https://medium.com/@eclow/can-your-forecast-predict-the-effect-of-a-decision-7205e481a0d9) Built on a synthetic toy system (no real series has a ground-truth counterfactual to score against); response gain ~0 under unexcited context regardless of context length, climbing to 0.7-0.8 only under excitation. |
| Excitation, but for inflation under central bank rate decisions | 2026-10-21 | Follow-up to [literature/excitation-2026.pdf](../literature/excitation-2026.pdf); bridges to the monetary-shock-identification literature (Romer & Romer 2004; Gürkaynak, Sack & Swanson 2005; Jarociński & Karadi 2020) | candidate | Searched 2026-10-21, found no existing work combining TSFM excitation with monetary policy causal identification — this would be new, not a reproduction. Conceptually transfers well (central bank rates are about as "unexcited"/rule-following a control signal as exists). Mechanically does not: you can't randomize real monetary policy to generate excited data, there's no simulator so no ground truth to score response gain against, sample size is tiny (~8 FOMC decisions/year, a handful of regimes since WWII) vs. thousands of control steps across 191 buildings, and rate surprises carry an "information effect" (revealing what the Fed believes) with no HVAC analog. The real angle, if pursued: test whether a TSFM conditioned on an identified monetary-shock series (econometrics' after-the-fact substitute for excitation) behaves differently than one conditioned on the raw endogenous rate — framed as illustrative/exploratory throughout, not as a clean evaluative test like Post 02. |

<!-- Add rows above this line. The weekly digest routine appends here automatically; feel free to add your own. -->
