# Topic backlog

Candidate blog topics, newest first within each status. See
[README.md](README.md) for how this file gets populated and used.

**Status values:** `candidate` / `in-progress (post: <slug>)` /
`published (post: <slug>)`.

| Topic | Added | Source | Status | Why |
|---|---|---|---|---|
| LLM-guided residual correction vs. this repo's nearest-neighbor residual memory | 2026-10-16 | [literature/ctrl-2026.pdf](../literature/ctrl-2026.pdf) (CTRL, Kim et al. 2026) | candidate | Demo 2 already does retrieval-based residual correction without an LLM in the loop; CTRL's LLM-guided version is a natural point of comparison — does the LLM add anything the nearest-neighbor version doesn't, or just cost? |
| Does a forecasting foundation model know what it doesn't know, under intervention? | 2026-10-16 | [literature/excitation-2026.pdf](../literature/excitation-2026.pdf) (Amria et al. 2026, "Excitation") | candidate | A genuinely new angle for this repo: every demo so far evaluates passive forecasting accuracy. This paper's point — low forecast error doesn't mean the model has learned how the system *responds to actions* — doesn't obviously fit the existing demo format and would need real thought before committing to it. |

<!-- Add rows above this line. The weekly digest routine appends here automatically; feel free to add your own. -->
