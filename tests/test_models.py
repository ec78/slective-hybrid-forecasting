import numpy as np
import pytest

from src.models import build_lag_fourier_dataset, build_lag_fourier_features_at


def test_build_lag_fourier_dataset_alignment_no_fourier():
    values = np.arange(20, dtype=float)
    X, Y = build_lag_fourier_dataset(values, lags=[1, 2], max_horizon=3)

    # max_lag=2, max_horizon=3 -> rows_t = 2..16 inclusive (15 rows)
    assert X.shape == (15, 2)
    assert Y.shape == (15, 3)

    # first row: t=2 -> features [values[1], values[0]], targets [values[3:6]]
    np.testing.assert_allclose(X[0], [1.0, 0.0])
    np.testing.assert_allclose(Y[0], [3.0, 4.0, 5.0])

    # last row: t=16 -> features [values[15], values[14]], targets [values[17:20]]
    np.testing.assert_allclose(X[-1], [15.0, 14.0])
    np.testing.assert_allclose(Y[-1], [17.0, 18.0, 19.0])


def test_build_lag_fourier_dataset_never_uses_future_values():
    # For every row, every feature index and every target index must be a
    # value that exists strictly within `values` and targets must be later
    # in time than every feature used for that row.
    values = np.arange(50, dtype=float)
    lags = [1, 3, 5]
    max_horizon = 4
    X, Y = build_lag_fourier_dataset(values, lags, max_horizon)

    max_lag = max(lags)
    rows_t = np.arange(max_lag, len(values) - max_horizon)
    for i, t in enumerate(rows_t):
        expected_features = [values[t - lag] for lag in lags]
        expected_targets = [values[t + h] for h in range(1, max_horizon + 1)]
        np.testing.assert_allclose(X[i], expected_features)
        np.testing.assert_allclose(Y[i], expected_targets)
        assert max(t - lag for lag in lags) < t < min(t + h for h in range(1, max_horizon + 1))


def test_build_lag_fourier_dataset_appends_fourier_terms():
    values = np.arange(20, dtype=float)
    X, _ = build_lag_fourier_dataset(values, lags=[1, 2], max_horizon=3, fourier_periods=[4], fourier_order=1)

    assert X.shape == (15, 2 + 2)  # 2 lags + (sin, cos) for one harmonic of one period
    t0 = 2  # first row's t
    expected_sin = np.sin(2 * np.pi * 1 * t0 / 4)
    expected_cos = np.cos(2 * np.pi * 1 * t0 / 4)
    np.testing.assert_allclose(X[0, 2:], [expected_sin, expected_cos], atol=1e-10)


def test_build_lag_fourier_dataset_rejects_insufficient_history():
    values = np.arange(5, dtype=float)
    with pytest.raises(ValueError):
        build_lag_fourier_dataset(values, lags=[1, 2], max_horizon=10)


def test_build_lag_fourier_features_at_matches_dataset_schema():
    values = np.arange(20, dtype=float)
    origin = 10
    row = build_lag_fourier_features_at(values, origin, lags=[1, 2], fourier_periods=[4], fourier_order=1)

    assert row.shape == (1, 4)
    np.testing.assert_allclose(row[0, :2], [values[9], values[8]])
    expected_sin = np.sin(2 * np.pi * 1 * origin / 4)
    expected_cos = np.cos(2 * np.pi * 1 * origin / 4)
    np.testing.assert_allclose(row[0, 2:], [expected_sin, expected_cos], atol=1e-10)
