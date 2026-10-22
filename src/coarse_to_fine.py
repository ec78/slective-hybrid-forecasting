"""Coarse-to-fine forecasting: a cheap global-shape model first, then a
refiner that only has to predict what the coarse model got wrong (Post 03).

Loosely inspired by SCALER (Le et al., KDD 2026, arXiv:2608.08675) -- not a
reproduction of its trained coarse-forecaster + LLM-refinement architecture,
just its underlying idea: an expensive model's job gets easier, and cheaper,
once a cheap model has already removed the easy-to-predict structure. Both
refiners here are existing building blocks from earlier posts, pointed at a
residual series instead of the raw target.
"""

import numpy as np
import pandas as pd


def seasonal_naive_residuals(series, season_length):
    """Causal one-step residuals of the seasonal-naive model.

    ``residual[t] = series[t] - series[t - season_length]``, defined for
    ``t >= season_length``. The first ``season_length`` entries have no
    causal residual and come back as NaN.
    """
    values = series.to_numpy(dtype=float) if hasattr(series, "to_numpy") else np.asarray(series, dtype=float)
    residuals = np.full(len(values), np.nan)
    residuals[season_length:] = values[season_length:] - values[:-season_length]

    if hasattr(series, "index"):
        return pd.Series(residuals, index=series.index)
    return residuals


def coarse_plus_chronos_refiner_forecast(train, horizon, season_length, max_context_length=512, weight=1.0):
    """Seasonal-naive coarse shape + Chronos-2 zero-shot forecasting its residual.

    The expensive model never sees the raw series -- only the coarse
    model's historical residual, which has the big seasonal swing already
    removed.
    """
    from src.models import chronos_zero_shot_forecast, seasonal_naive_forecast

    coarse = seasonal_naive_forecast(train, horizon, season_length)

    residuals = seasonal_naive_residuals(train, season_length).dropna()
    refinement = chronos_zero_shot_forecast(residuals, horizon, max_context_length=max_context_length)["forecast"]

    forecast = coarse + weight * refinement
    return {"forecast": forecast}


def coarse_plus_residual_memory_forecast(train, horizon, season_length, lookback, k=5, weight=1.0):
    """Seasonal-naive coarse shape + nearest-neighbor residual-memory refinement.

    Reuses ``src.residual_memory.retrieve_residual_correction`` exactly as
    in Post 01 Demo 2, just pointed at the seasonal-naive model's residuals
    instead of ARIMA's. ``lookback`` must be at least ``season_length`` so
    that no causal window or retrieved residual path touches the undefined
    (NaN) residuals before the first full season.
    """
    from src.models import seasonal_naive_forecast
    from src.residual_memory import retrieve_residual_correction

    if lookback < season_length:
        raise ValueError("lookback must be >= season_length to avoid NaN residuals.")

    coarse = seasonal_naive_forecast(train, horizon, season_length)

    values = train.to_numpy(dtype=float)
    residuals = seasonal_naive_residuals(train, season_length).to_numpy()
    origin = len(train)

    correction, diagnostics = retrieve_residual_correction(
        values, residuals, origin=origin, lookback=lookback, horizon=horizon, k=k,
    )

    forecast = coarse + weight * correction
    return {"forecast": forecast, "neighbor_anchors": str(diagnostics["neighbor_anchors"])}
