import numpy as np
import pandas as pd
import pytest

from src.coarse_to_fine import (
    coarse_plus_residual_memory_forecast,
    seasonal_naive_residuals,
)


def test_seasonal_naive_residuals_matches_hand_computed_values():
    values = np.array([10.0, 20.0, 30.0, 13.0, 23.0, 33.0])
    residuals = seasonal_naive_residuals(values, season_length=3)

    assert np.isnan(residuals[:3]).all()
    np.testing.assert_allclose(residuals[3:], [13.0 - 10.0, 23.0 - 20.0, 33.0 - 30.0])


def test_seasonal_naive_residuals_preserves_pandas_index():
    index = pd.date_range("2020-01-01", periods=6, freq="h")
    series = pd.Series([10.0, 20.0, 30.0, 13.0, 23.0, 33.0], index=index)
    residuals = seasonal_naive_residuals(series, season_length=3)

    assert isinstance(residuals, pd.Series)
    pd.testing.assert_index_equal(residuals.index, index)
    assert residuals.iloc[3] == pytest.approx(3.0)


def test_coarse_plus_residual_memory_rejects_lookback_shorter_than_season():
    index = pd.date_range("2020-01-01", periods=50, freq="h")
    series = pd.Series(np.sin(np.arange(50) / 5.0), index=index)
    with pytest.raises(ValueError):
        coarse_plus_residual_memory_forecast(series, horizon=3, season_length=10, lookback=5)


def test_coarse_plus_residual_memory_zero_weight_equals_coarse_alone():
    rng = np.random.default_rng(0)
    index = pd.date_range("2020-01-01", periods=120, freq="h")
    cycle = np.sin(2 * np.pi * np.arange(120) / 12)
    series = pd.Series(cycle + rng.normal(scale=0.01, size=120), index=index)

    from src.models import seasonal_naive_forecast

    season_length, horizon, lookback = 12, 6, 24
    coarse = seasonal_naive_forecast(series, horizon, season_length)

    result = coarse_plus_residual_memory_forecast(
        series, horizon, season_length=season_length, lookback=lookback, k=3, weight=0.0,
    )
    np.testing.assert_allclose(result["forecast"], coarse)


def test_coarse_plus_residual_memory_weight_scales_linearly():
    rng = np.random.default_rng(1)
    index = pd.date_range("2020-01-01", periods=150, freq="h")
    cycle = np.sin(2 * np.pi * np.arange(150) / 12) * 5
    series = pd.Series(cycle + rng.normal(scale=0.2, size=150), index=index)

    season_length, horizon, lookback = 12, 6, 24
    full = coarse_plus_residual_memory_forecast(
        series, horizon, season_length=season_length, lookback=lookback, k=3, weight=1.0,
    )
    half = coarse_plus_residual_memory_forecast(
        series, horizon, season_length=season_length, lookback=lookback, k=3, weight=0.5,
    )
    zero = coarse_plus_residual_memory_forecast(
        series, horizon, season_length=season_length, lookback=lookback, k=3, weight=0.0,
    )

    implied_correction_full = full["forecast"] - zero["forecast"]
    implied_correction_half = half["forecast"] - zero["forecast"]
    np.testing.assert_allclose(implied_correction_half, 0.5 * implied_correction_full, atol=1e-10)
