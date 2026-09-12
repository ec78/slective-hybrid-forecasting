import numpy as np
import pandas as pd
import pytest

from src.residual_memory import apply_correction, fit_correction_scale, retrieve_residual_correction


def _periodic_series(period=10, n_periods=6):
    cycle = np.array([0, 1, 2, 3, 2, 1, 0, -1, -2, -1], dtype=float)
    values = np.tile(cycle, n_periods)
    residuals = 0.1 * values  # also exactly periodic, phase-locked to values
    return values, residuals


def test_retrieval_finds_same_phase_neighbors_and_matches_expected_correction():
    values, residuals = _periodic_series()
    lookback, horizon, origin, k = 10, 3, 30, 2

    correction, diagnostics = retrieve_residual_correction(
        values, residuals, origin=origin, lookback=lookback, horizon=horizon, k=k
    )

    # s=10 and s=20 are the two same-phase, zero-distance neighbors below the origin.
    assert sorted(diagnostics["neighbor_anchors"]) == [10, 20]
    np.testing.assert_allclose(diagnostics["neighbor_distances"], [0.0, 0.0], atol=1e-8)

    expected = residuals[10:13]  # identical to residuals[20:23] by periodicity
    np.testing.assert_allclose(correction, expected, atol=1e-8)


def test_retrieval_is_causal_no_neighbor_or_path_crosses_origin():
    rng = np.random.default_rng(0)
    values = rng.normal(size=200)
    residuals = rng.normal(size=200)
    lookback, horizon, origin, k = 15, 5, 120, 4

    _, diagnostics = retrieve_residual_correction(
        values, residuals, origin=origin, lookback=lookback, horizon=horizon, k=k
    )

    for anchor in diagnostics["neighbor_anchors"]:
        assert anchor - lookback >= 0  # window fits in history
        assert anchor + horizon <= origin  # residual path does not cross the origin


def test_retrieval_rejects_origin_shorter_than_lookback():
    values, residuals = _periodic_series()
    with pytest.raises(ValueError):
        retrieve_residual_correction(values, residuals, origin=5, lookback=10, horizon=3)


def test_retrieval_rejects_insufficient_causal_history():
    values, residuals = _periodic_series(period=10, n_periods=2)  # only 20 points
    # origin so close to the start that no candidate window + path fits before it
    with pytest.raises(ValueError):
        retrieve_residual_correction(values, residuals, origin=12, lookback=10, horizon=5)


def test_fit_correction_scale_recovers_true_alpha():
    rng = np.random.default_rng(1)
    correction = rng.normal(size=500)
    base_forecast = rng.normal(size=500)
    true_alpha = 0.5
    actual = base_forecast + true_alpha * correction

    grid = np.linspace(0, 1.5, 31)
    fitted = fit_correction_scale(actual, base_forecast, correction, grid=grid)
    assert fitted == pytest.approx(true_alpha, abs=grid[1] - grid[0])


def _base_results():
    return pd.DataFrame({
        "origin": [1, 1, 2, 2],
        "horizon": [1, 2, 1, 2],
        "origin_actual": [100.0, 100.0, 110.0, 110.0],
        "actual": [102.0, 104.0, 111.0, 113.0],
        "forecast": [100.0, 100.0, 110.0, 110.0],
        "mase_scale": [2.0, 2.0, 2.0, 2.0],
    })


def test_apply_correction_with_scalar_scale():
    results = _base_results()
    correction = pd.DataFrame({
        "origin": [1, 1, 2, 2],
        "horizon": [1, 2, 1, 2],
        "correction": [2.0, 4.0, 1.0, 3.0],
    })

    corrected = apply_correction(results, correction, scale=1.0, model_name="ARIMA+memory")
    np.testing.assert_allclose(corrected["forecast"], [102.0, 104.0, 111.0, 113.0])
    assert (corrected["model"] == "ARIMA+memory").all()
    np.testing.assert_allclose(corrected["scaled_absolute_error"], [0.0, 0.0, 0.0, 0.0])


def test_apply_correction_with_per_horizon_scale():
    results = _base_results()
    correction = pd.DataFrame({
        "origin": [1, 1, 2, 2],
        "horizon": [1, 2, 1, 2],
        "correction": [2.0, 4.0, 1.0, 3.0],
    })

    corrected = apply_correction(results, correction, scale={1: 0.0, 2: 1.0}, model_name="ARIMA+memory")
    horizon_1 = corrected[corrected["horizon"] == 1]
    horizon_2 = corrected[corrected["horizon"] == 2]
    np.testing.assert_allclose(horizon_1["forecast"], horizon_1["origin_actual"])  # scale 0 -> uncorrected
    np.testing.assert_allclose(horizon_2["forecast"], horizon_2["actual"])  # scale 1 -> exact correction


def test_apply_correction_rejects_missing_rows():
    results = _base_results()
    correction = pd.DataFrame({"origin": [1], "horizon": [1], "correction": [2.0]})
    with pytest.raises(ValueError):
        apply_correction(results, correction, scale=1.0, model_name="ARIMA+memory")
