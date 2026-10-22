# Literature index

A running backlog of papers worth reading — candidates for future demos, not
necessarily things already used. For papers actually cited by a post, see
that post's section in the root [README.md](../README.md) instead; this
index is the superset.

Drop PDFs directly in this folder as you find them (`slug-year.pdf`), then
add a row here. The weekly digest routine (see
[topics/README.md](../topics/README.md)) also adds rows here for promising
papers it finds, without downloading the PDF — those rows link out instead
of naming a local file.

| File / Link | Title | Authors / Venue | Added | Status | Notes |
|---|---|---|---|---|---|
| [ctrl-2026.pdf](ctrl-2026.pdf) | CTRL: Control-Based Time Series Forecasting with LLM-Guided Residual Learning | Kim, Ji, Lee, Kim, Jang — Yonsei University | 2026-09-28 | unread | LLM-guided residual correction — close cousin of Demo 2's residual-memory mechanism; worth comparing approaches. |
| [excitation-2026.pdf](excitation-2026.pdf) | Time-series Foundation Models for Predictive Control: The Role of Excitation | Amria, Hoffmann, Bordne, Rothenhäusler, Frison, Walnum, Gros, Bödecker — U. Freiburg / NTNU | 2026-10-15 | used-in-02-excitation-for-control | Full paper read. Core mechanism (response gain, excited vs. unexcited context) reproduced on a small synthetic system in `notebooks/02-excitation-for-control/`. |
| [arXiv 2607.02623](https://arxiv.org/abs/2607.02623) | Evaluating Time Series Foundation Models for Electricity Price Forecasting: Contamination Risk, Distributional Shifts, and Covariate Dependence | Pan & Ezzat — ICML 2026 workshop | 2026-10-16 | unread | TSFMs depend on covariate support and don't reliably beat domain-specific methods; combination looks promising. Relates to Demo 1. |
| [arXiv 2605.05218](https://arxiv.org/abs/2605.05218) | Horizon-Constrained Rashomon Sets for Chaotic Forecasting | arXiv 2026 | 2026-10-16 | unread | Predictive multiplicity across horizons: tied short-horizon accuracy, diverging long-horizon paths. |
| [arXiv 2610.12232](https://arxiv.org/abs/2610.12232) | Training on the Future: A Delay-Aware Audit of Test-Time Adaptation for Time-Series Forecasting | arXiv Oct 2026 | 2026-10-16 | unread | Found via listing; abstract not checked (arxiv.org unreachable). Possible leakage audit of TTA methods. |

**Status values:** `unread` / `reading` / `used-in-<post-slug>` / `skipped`
(skipped = read, not a fit — leave a one-line reason in Notes rather than
deleting the row).
