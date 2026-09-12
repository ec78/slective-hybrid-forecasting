# selective-hybrid-forecasting

Small, conceptual demonstrations of *when* combining a pretrained time-series
foundation model with classical/local methods actually helps — inspired by a
handful of recent papers, not a reproduction of their full architectures.

This is a companion to two earlier posts:

- [Chasing Chronos](https://medium.com/@eclow/chasing-chronos-663cc8883558)
- [Transformers vs. ARIMA: Do More Complex Models Produce Better Forecasts?](https://medium.com/@eclow/transformers-vs-arima-do-more-complex-models-produce-better-forecasts-28ca372052d4)

Those posts asked whether more complex models beat simple ones. This repo
asks a follow-up question: **when a pretrained model *is* worth using, is it
better used on its own, or as one ingredient in something more selective?**

## Shared evaluation design

Every notebook uses the same rolling-origin evaluation:

- Identical forecast origins and horizons across all models being compared.
- Metrics: MAE, RMSE, MASE (scaled by the in-sample naive/seasonal-naive
  error), and directional accuracy where it's meaningful.
- Runtime and any training/adaptation cost is recorded alongside accuracy —
  a model that wins by a fraction of a point of MASE but costs 50x the
  compute is a different story than one that wins for free.
- A seasonal-naive or naive baseline is always in the comparison.
- Any weight, scale, or hyperparameter that isn't fixed in advance is
  selected on a validation slice only, never on the test period.

Two series are used throughout (see [data/README.md](data/README.md)):

- **CISO hourly electricity demand** (2019-2026) — seasonal, high-signal.
- **SPY daily adjusted close** (1993-2026) — close to a random walk, used to
  show what happens when there isn't much signal to extract.

## Demos

| Notebook | Question |
|---|---|
| [01_zero_shot_and_local_baselines.ipynb](notebooks/01_zero_shot_and_local_baselines.ipynb) | When does a pretrained zero-shot forecast add value beyond local baselines, and does a validation-weighted hybrid do better than either alone? |
| [02_residual_memory_correction.ipynb](notebooks/02_residual_memory_correction.ipynb) | Can retrieving residuals from similar past situations correct a frozen base forecast? |
| [03_frequency_informed_features.ipynb](notebooks/03_frequency_informed_features.ipynb) | Does giving a flexible model explicit Fourier terms for known periodicity help it generalize? |

### 1. Zero-shot is the starting line

Compares seasonal-naive, a local ARIMA baseline, Chronos-2 zero-shot, and a
validation-weighted ARIMA/Chronos combination, at short/medium/long horizons.
The hybrid weight is chosen only on validation data. The point isn't that the
hybrid always wins — it's that "pretrained" and "locally demonstrated value"
are different claims, and this makes the gap between them visible.

### 2. Residual memory as a correction layer

Fits ARIMA and, at each forecast origin, looks up the most similar prior
lookback windows (nearest-neighbor on a normalized window), retrieves the
residual paths that followed those windows, and adds a distance-weighted,
validation-scaled correction to the frozen base forecast. Causal retrieval is
enforced everywhere: no matched window or its residual path is allowed to
extend past the forecast origin (see `tests/test_residual_memory.py`).

### 3. Classical structure as model input

On hourly electricity demand, compares a lag-only regression/small neural
net against the same model given Fourier terms for daily and weekly
periodicity, alongside a SARIMAX benchmark using those same Fourier terms as
exogenous regressors. Not a reproduction of CoSPOT — a small illustration of
its underlying idea: a flexible learner can benefit when classical analysis
hands it a credible representation of recurring structure.

## Repository structure

```
selective-hybrid-forecasting/
├── data/
│   ├── README.md
│   └── raw/                  electricity_ciso.csv, spy.csv (+ metadata)
├── notebooks/                one notebook per demo
├── src/
│   ├── data.py                loaders + train/val/test split
│   ├── evaluation.py           metrics + rolling-origin harness
│   ├── models.py                naive / ARIMA / Chronos / hybrid / Fourier+SARIMAX
│   ├── residual_memory.py     causal nearest-neighbor residual retrieval
│   └── dataimport.py           optional: refresh the raw CSVs
├── tests/                    unit tests for the metrics and causal retrieval logic
└── results/
    ├── figures/
    └── metrics/
```

## Setup

```bash
python -m venv .venv
.venv/Scripts/activate   # source .venv/bin/activate on macOS/Linux

pip install -e ".[notebooks,dev]"   # base install + Jupyter + pytest
pip install -e ".[chronos]"          # adds torch + chronos-forecasting (large download)
```

Run the test suite with `pytest`. Chronos-2 (`amazon/chronos-2`) downloads
from Hugging Face on first use and runs on CPU unless a CUDA GPU is
available; expect zero-shot inference to be the slowest part of Demo 1 and
the Chronos branch of Demo 2.

## References

- Pendyala, V., Fu, Y., Yan, W., & Virani, N. (2026). *Assessing
  Covariate-Informed Grid Load Forecasting with a Time-Series Foundation
  Model.*
- He, Y., Cang, Y., Ning, Z., Wang, N., & Shi, L. (2026). *RATL: Learning
  from Retrieved Residuals for Robust Multivariate Time-Series Forecasting.*
- Choi, S., Kim, H., Lee, J.-G., & Park, C. (2026). *Compositional Spectral
  Prompts for LLM-based Online Time Series Forecasting.*
- Chen, L., & Wang, W. (2026). *From Vector Autoregressions to AI-based Time
  Series Forecasting: A Review.*
- Garcia, C., & Remy, G. (2026). *Statistical Benchmarking of Transformer
  Models in Low Signal-to-Noise Time-Series Forecasting.*
