"""Forecasting models shared across the demo notebooks.

Kept intentionally small: each function takes a training series and a
horizon and returns either a length-``horizon`` array, or a dict with a
``"forecast"`` key plus any diagnostics worth keeping (fitted order,
residuals, etc.) — matching the contract expected by
``src.evaluation.rolling_origin_evaluate``.
"""

from functools import lru_cache

import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX


# ---------------------------------------------------------------------------
# Naive baselines
# ---------------------------------------------------------------------------

def naive_forecast(train, horizon):
    """Repeat the last observed value."""
    return np.full(horizon, train.iloc[-1], dtype=float)


def seasonal_naive_forecast(train, horizon, season_length):
    """Repeat the most recent full seasonal cycle."""
    if len(train) < season_length:
        raise ValueError("train is shorter than one seasonal cycle.")
    last_season = train.iloc[-season_length:].to_numpy(dtype=float)
    reps = int(np.ceil(horizon / season_length))
    return np.tile(last_season, reps)[:horizon]


# ---------------------------------------------------------------------------
# ARIMA
# ---------------------------------------------------------------------------

def select_order_by_aicc(train, candidate_pq=((0, 0), (1, 0), (0, 1), (1, 1), (2, 1), (2, 2)), d=1):
    """Small AICc grid search over (p, q) at a fixed differencing order.

    Meant to be run once (e.g. on the initial training window) to pick a
    plausible ARIMA(p, d, q) spec, then held fixed across forecast origins
    for speed — the conceptual point of Demo 1 is what a *local* ARIMA
    baseline can do, not a full AutoARIMA search at every origin.
    """
    train_values = train.to_numpy(dtype=float)
    n = len(train_values)

    best_order, best_aicc = None, np.inf
    for p, q in candidate_pq:
        try:
            fit = ARIMA(train_values, order=(p, d, q)).fit()
        except Exception:
            continue

        k = p + q + 1
        if n - k - 1 <= 0:
            aicc = fit.aic
        else:
            aicc = fit.aic + (2 * k * (k + 1)) / (n - k - 1)

        if aicc < best_aicc:
            best_aicc, best_order = aicc, (p, d, q)

    if best_order is None:
        raise RuntimeError("No candidate ARIMA order converged.")
    return best_order


def arima_forecast(train, horizon, order=(1, 1, 1)):
    """Fixed-specification ARIMA forecast."""
    fit = ARIMA(train.to_numpy(dtype=float), order=order).fit()
    forecast = np.asarray(fit.forecast(steps=horizon), dtype=float)
    residuals = np.asarray(fit.resid, dtype=float)
    return {"forecast": forecast, "order": str(order), "residuals": residuals}


# ---------------------------------------------------------------------------
# Chronos zero-shot
# ---------------------------------------------------------------------------

CHRONOS_MODEL_ID = "amazon/chronos-2"


@lru_cache(maxsize=1)
def _load_chronos_pipeline(model_id=CHRONOS_MODEL_ID, device=None):
    import torch
    from chronos import Chronos2Pipeline

    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    pipeline = Chronos2Pipeline.from_pretrained(model_id, device_map=device)
    return pipeline


def chronos_zero_shot_forecast(train, horizon, max_context_length=512, model_id=CHRONOS_MODEL_ID):
    """Zero-shot median forecast from a frozen, pretrained Chronos-2 model.

    No parameters are fit to ``train`` — it is only used as context. This is
    the "pretrained capability" side of Demo 1.
    """
    pipeline = _load_chronos_pipeline(model_id=model_id)
    context = train.to_numpy(dtype=float)[-max_context_length:].copy()

    _, point_forecasts = pipeline.predict_quantiles(
        inputs=[context],
        prediction_length=horizon,
        quantile_levels=[0.5],
        batch_size=1,
        context_length=min(len(context), max_context_length),
    )

    forecast = np.asarray(point_forecasts[0], dtype=float).reshape(-1)[:horizon]
    return {"forecast": forecast, "context_length": len(context)}


# ---------------------------------------------------------------------------
# Validation-weighted hybrid combination
# ---------------------------------------------------------------------------

def fit_hybrid_weight(actual, forecast_a, forecast_b, grid=np.linspace(0, 1, 21)):
    """Pick the convex-combination weight on ``forecast_a`` that minimizes MAE.

    Must only ever be called on a validation slice — never on test data.
    Returns the weight ``w`` such that ``w * forecast_a + (1 - w) * forecast_b``
    is the combined forecast.
    """
    actual = np.asarray(actual, dtype=float)
    forecast_a = np.asarray(forecast_a, dtype=float)
    forecast_b = np.asarray(forecast_b, dtype=float)

    errors = [
        np.mean(np.abs(actual - (w * forecast_a + (1 - w) * forecast_b)))
        for w in grid
    ]
    return float(grid[int(np.argmin(errors))])


def combine_forecasts(forecast_a, forecast_b, weight):
    return weight * np.asarray(forecast_a, dtype=float) + (1 - weight) * np.asarray(forecast_b, dtype=float)


# ---------------------------------------------------------------------------
# Frequency-informed features (Demo 3)
# ---------------------------------------------------------------------------

def fourier_features(index, periods, order=3):
    """Sin/cos Fourier terms for one or more periodicities.

    Parameters
    ----------
    index : array-like of int
        Integer time step (e.g. hours since series start).
    periods : list of float
        Cycle lengths in the same units as ``index`` (e.g. 24 and 168 for
        daily and weekly seasonality in hourly data).
    order : int
        Number of harmonics per period.
    """
    index = np.asarray(index, dtype=float)
    features = {}
    for period in periods:
        for k in range(1, order + 1):
            angle = 2 * np.pi * k * index / period
            features[f"sin_{int(period)}_{k}"] = np.sin(angle)
            features[f"cos_{int(period)}_{k}"] = np.cos(angle)
    return features


def lag_features(series, lags):
    """Lagged values of ``series`` as a dict of {f"lag_{L}": shifted array}."""
    return {f"lag_{lag}": series.shift(lag) for lag in lags}


def build_lag_fourier_dataset(values, lags, max_horizon, fourier_periods=None, fourier_order=3):
    """Direct multi-horizon supervised dataset built from one 1-D history.

    Row ``t`` (for every ``t`` with a full set of lags behind it and
    ``max_horizon`` targets ahead of it) has:

    - features: ``values[t - lag]`` for each ``lag`` in ``lags``, optionally
      concatenated with Fourier terms describing *t itself* (not the target
      time — see the SARIMAX benchmark for the alternative convention of
      attaching Fourier terms to the forecasted time instead).
    - targets: ``values[t + 1], ..., values[t + max_horizon]``.

    Returns
    -------
    X : ndarray, shape (n_rows, n_features)
    Y : ndarray, shape (n_rows, max_horizon)
    """
    values = np.asarray(values, dtype=float)
    max_lag = max(lags)
    rows_t = np.arange(max_lag, len(values) - max_horizon)
    if len(rows_t) == 0:
        raise ValueError("Not enough history for the requested lags and horizon.")

    feature_cols = [values[rows_t - lag] for lag in lags]
    if fourier_periods:
        fourier = fourier_features(rows_t, fourier_periods, fourier_order)
        feature_cols.extend(fourier.values())

    X = np.column_stack(feature_cols)
    Y = np.column_stack([values[rows_t + h] for h in range(1, max_horizon + 1)])
    return X, Y


def build_lag_fourier_features_at(values, origin, lags, fourier_periods=None, fourier_order=3):
    """One feature row for forecasting from ``origin`` — same schema as
    ``build_lag_fourier_dataset``."""
    values = np.asarray(values, dtype=float)
    feature_cols = [values[origin - lag] for lag in lags]
    if fourier_periods:
        fourier = fourier_features(np.array([origin]), fourier_periods, fourier_order)
        feature_cols.extend(float(v[0]) for v in fourier.values())
    return np.array(feature_cols, dtype=float).reshape(1, -1)


def lag_regression_forecast(
    train,
    horizon,
    lags,
    fourier_periods=None,
    fourier_order=3,
    hidden_layer_sizes=(16,),
    random_state=0,
):
    """Direct multi-horizon MLP forecast from lagged values (+ optional Fourier terms).

    A fresh small MLP is fit at every forecast origin on a dataset built
    entirely from the training history, then used once to predict all
    ``horizon`` lead times at once.
    """
    from sklearn.neural_network import MLPRegressor
    from sklearn.preprocessing import StandardScaler

    values = train.to_numpy(dtype=float)
    X, Y = build_lag_fourier_dataset(values, lags, horizon, fourier_periods, fourier_order)

    x_scaler = StandardScaler().fit(X)
    y_scaler = StandardScaler().fit(Y)

    model = MLPRegressor(hidden_layer_sizes=hidden_layer_sizes, max_iter=2000, random_state=random_state)
    model.fit(x_scaler.transform(X), y_scaler.transform(Y))

    x_new = build_lag_fourier_features_at(values, len(values), lags, fourier_periods, fourier_order)
    forecast = y_scaler.inverse_transform(model.predict(x_scaler.transform(x_new)))[0]
    return {"forecast": np.asarray(forecast, dtype=float)}


def sarimax_forecast(train, horizon, exog_train, exog_future, order=(1, 1, 1)):
    """SARIMAX with exogenous regressors already built — a low-level primitive."""
    fit = SARIMAX(
        train.to_numpy(dtype=float),
        exog=exog_train,
        order=order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    ).fit(disp=False)
    forecast = np.asarray(fit.forecast(steps=horizon, exog=exog_future), dtype=float)
    return {"forecast": forecast, "order": str(order)}


def sarimax_fourier_forecast(train, horizon, fourier_periods, fourier_order=2, order=(1, 1, 1)):
    """SARIMAX with Fourier terms as exogenous regressors — the classical Demo 3 benchmark.

    Unlike ``lag_regression_forecast``, the Fourier terms here describe the
    *forecasted* time steps (exog must be supplied at both fit and forecast
    time), which is the idiomatic way SARIMAX consumes seasonal information.
    """
    n = len(train)
    exog_train = np.column_stack(list(
        fourier_features(np.arange(n), fourier_periods, fourier_order).values()
    ))
    exog_future = np.column_stack(list(
        fourier_features(np.arange(n, n + horizon), fourier_periods, fourier_order).values()
    ))
    return sarimax_forecast(train, horizon, exog_train, exog_future, order=order)
