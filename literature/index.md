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
| [excitation-2026.pdf](excitation-2026.pdf) | Time-series Foundation Models for Predictive Control: The Role of Excitation | Amria, Hoffmann, Bordne, Rothenhäusler, Frison, Walnum, Gros, Bödecker — U. Freiburg / NTNU | 2026-10-15 | unread | TSFMs for MPC; low forecast error doesn't guarantee the model captures system response to actions. New angle (control), not yet covered by any post. |
| [arxiv 2608.14106](https://arxiv.org/abs/2608.14106) | Forecast Collapse in Time-Series Foundation Models | Wan, Ma et al. — arXiv, Aug 2026 | 2026-10-19 | unread | TSFMs give near-flat, poorly-ranked stock return forecasts; relevant to SPY series. Abstract not verified directly. |
| [arxiv 2609.24559](https://arxiv.org/abs/2609.24559) | t0: A Time-Series Foundation Model for Forecasting with Context | The Forecasting Company — arXiv, Sep 2026 | 2026-10-19 | unread | Open-weights TSFM using past and known-future covariates; pairs with Demo 3 / CISO. |
| [arxiv 2608.08675](https://arxiv.org/abs/2608.08675) | Efficient Test-Time Scaling for LLM-based Time Series Forecasting (SCALER) | Le et al. — KDD 2026 | 2026-10-19 | unread | Coarse shape model guiding LLM residual refinement; cousin of CTRL and Demo 2. |

**Status values:** `unread` / `reading` / `used-in-<post-slug>` / `skipped`
(skipped = read, not a fit — leave a one-line reason in Notes rather than
deleting the row).
