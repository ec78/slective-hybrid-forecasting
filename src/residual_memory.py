"""Residual-memory correction for a frozen base forecast (RATL-inspired).

The idea: at a forecast origin, find prior points in history whose recent
window looked similar to the current one, and see what actually happened to
the base model's errors after those earlier points. Average those residual
paths (optionally distance-weighted) and add the result as a correction.

Causality is the whole point of this module: a query window, its matched
neighbor windows, and the residual paths retrieved for those neighbors must
all end at or before the forecast origin. Nothing here is allowed to look
into the future.
"""

import numpy as np


def _normalize(window):
    mean, std = window.mean(), window.std()
    std = std if std > 0 else 1.0
    return (window - mean) / std


def retrieve_residual_correction(
    values,
    residuals,
    origin,
    lookback,
    horizon,
    k=5,
    weighting="inverse_distance",
    eps=1e-8,
):
    """Retrieve a distance-weighted residual-path correction at ``origin``.

    Parameters
    ----------
    values : 1-D array
        Raw series values, used only to measure window similarity.
    residuals : 1-D array
        Base-model residuals aligned index-for-index with ``values``.
    origin : int
        Forecast-origin position. The query window is ``values[origin -
        lookback:origin]``. Every candidate neighbor window and its
        residual path must end at or before ``origin`` — see the causality
        check below.
    lookback : int
        Window length used for similarity matching.
    horizon : int
        Length of the residual path to retrieve.
    k : int
        Number of nearest neighbors to average.
    weighting : {"inverse_distance", "uniform"}

    Returns
    -------
    correction : numpy.ndarray, shape (horizon,)
    diagnostics : dict
        Neighbor anchors, distances, and weights actually used.
    """
    values = np.asarray(values, dtype=float)
    residuals = np.asarray(residuals, dtype=float)

    if origin < lookback:
        raise ValueError("origin must be >= lookback.")

    query = _normalize(values[origin - lookback:origin])

    # Causal candidates: window ends at s (s >= lookback so the window fits),
    # and its residual path [s:s+horizon] must not extend past the origin.
    candidate_ends = np.arange(lookback, origin - horizon + 1)
    if len(candidate_ends) == 0:
        raise ValueError("Not enough history before origin for any causal neighbor.")

    windows = np.stack([values[s - lookback:s] for s in candidate_ends])
    windows_norm = (windows - windows.mean(axis=1, keepdims=True)) / np.where(
        windows.std(axis=1, keepdims=True) > 0, windows.std(axis=1, keepdims=True), 1.0
    )
    distances = np.linalg.norm(windows_norm - query, axis=1)

    k = min(k, len(candidate_ends))
    nearest = np.argsort(distances)[:k]
    nearest_ends = candidate_ends[nearest]
    nearest_distances = distances[nearest]

    if weighting == "uniform":
        weights = np.full(k, 1.0 / k)
    elif weighting == "inverse_distance":
        inverse = 1.0 / (nearest_distances + eps)
        weights = inverse / inverse.sum()
    else:
        raise ValueError("weighting must be 'inverse_distance' or 'uniform'.")

    residual_paths = np.stack([residuals[s:s + horizon] for s in nearest_ends])
    correction = weights @ residual_paths

    diagnostics = {
        "neighbor_anchors": nearest_ends.tolist(),
        "neighbor_distances": nearest_distances.tolist(),
        "weights": weights.tolist(),
    }
    return correction, diagnostics


def apply_correction(results, correction, scale, model_name):
    """Build a corrected-model results frame from a base model's results frame.

    Parameters
    ----------
    results : pandas.DataFrame
        Output of ``src.evaluation.rolling_origin_evaluate`` for the base
        (uncorrected) model — must have ``origin``, ``horizon``, ``actual``,
        ``forecast``, ``origin_actual``, and ``mase_scale`` columns.
    correction : pandas.DataFrame
        Columns ``origin``, ``horizon``, ``correction`` — one row per
        (origin, horizon) pair present in ``results``.
    scale : float or dict
        A single scale applied everywhere, or a ``{horizon: scale}`` dict —
        fit on validation data only (see ``fit_correction_scale``).
    """
    merged = results.merge(correction, on=["origin", "horizon"], how="left")
    if merged["correction"].isna().any():
        raise ValueError("correction is missing rows present in results.")

    if isinstance(scale, dict):
        s = merged["horizon"].map(scale)
        if s.isna().any():
            missing = sorted(merged.loc[s.isna(), "horizon"].unique())
            raise ValueError(f"scale has no entry for horizon(s) {missing}.")
    else:
        s = scale

    merged["forecast"] = merged["forecast"] + s * merged["correction"]
    merged["model"] = model_name
    merged["scaled_absolute_error"] = (merged["actual"] - merged["forecast"]).abs() / merged["mase_scale"]
    merged["direction_correct"] = (
        np.sign(merged["actual"] - merged["origin_actual"]) == np.sign(merged["forecast"] - merged["origin_actual"])
    )
    return merged.drop(columns=["correction"])


def fit_correction_scale(actual, base_forecast, correction, grid=None):
    """Pick a scale alpha (on validation data only) minimizing MAE of
    ``base_forecast + alpha * correction`` against ``actual``.

    Inputs may be flattened across many validation origins/horizons.
    """
    grid = np.linspace(0.0, 2.0, 21) if grid is None else np.asarray(grid)
    actual = np.asarray(actual, dtype=float)
    base_forecast = np.asarray(base_forecast, dtype=float)
    correction = np.asarray(correction, dtype=float)

    errors = [
        np.mean(np.abs(actual - (base_forecast + alpha * correction)))
        for alpha in grid
    ]
    return float(grid[int(np.argmin(errors))])
