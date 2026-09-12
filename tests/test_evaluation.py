import numpy as np
import pandas as pd
import pytest

from src.evaluation import (
    combine_results,
    directional_accuracy,
    generate_forecast_origins,
    mae,
    mase,
    rmse,
    rolling_origin_evaluate,
    summarize,
)


def test_mae_rmse_basic():
    actual = [1, 2, 3]
    forecast = [1, 2, 5]
    assert mae(actual, forecast) == pytest.approx(2 / 3)
    assert rmse(actual, forecast) == pytest.approx(np.sqrt(4 / 3))


def test_mase_matches_naive_scale():
    training_series = np.arange(10, dtype=float)  # naive step error is 1 everywhere
    actual = [10.0, 11.0]
    forecast = [11.0, 11.0]  # errors of 1 and 0
    result = mase(actual, forecast, training_series, seasonality=1)
    assert result == pytest.approx(0.5)


def test_mase_rejects_constant_training_series():
    with pytest.raises(ValueError):
        mase([1.0], [1.0], np.ones(10), seasonality=1)


def test_directional_accuracy():
    actual = [11, 9, 10]
    forecast = [12, 8, 10]
    origin_actual = [10, 10, 10]
    # ups: correct, correct; flat actual (10->10) has sign 0, forecast sign 0 -> correct
    assert directional_accuracy(actual, forecast, origin_actual) == pytest.approx(1.0)


def test_generate_forecast_origins_bounds():
    origins = generate_forecast_origins(n_obs=20, initial_train_size=15, max_horizon=3, step=1)
    assert origins == [15, 16, 17]  # last origin + max_horizon must be <= n_obs


def test_generate_forecast_origins_validates_inputs():
    with pytest.raises(ValueError):
        generate_forecast_origins(n_obs=10, initial_train_size=10, max_horizon=1)


def _naive_model(train, horizon):
    return np.full(horizon, train.iloc[-1])


def test_rolling_origin_evaluate_and_summarize_shapes():
    index = pd.date_range("2020-01-01", periods=30, freq="D")
    series = pd.Series(np.arange(30, dtype=float), index=index)

    results = rolling_origin_evaluate(
        series,
        model_fn=_naive_model,
        model_name="naive",
        horizons=[1, 2],
        initial_train_size=25,
        step=1,
    )
    # 4 origins (25,26,27,28) x 2 horizons
    assert len(results) == 8
    assert set(results["horizon"]) == {1, 2}

    summary = summarize(results)
    assert set(summary.columns) >= {"model", "horizon", "mae", "rmse", "mase", "directional_accuracy"}
    assert len(summary) == 2  # one row per horizon
    # naive forecast of a perfectly linear +1 series has a constant absolute error
    assert summary.loc[summary["horizon"] == 1, "mae"].iloc[0] == pytest.approx(1.0)
    assert summary.loc[summary["horizon"] == 2, "mae"].iloc[0] == pytest.approx(2.0)


def test_rolling_origin_evaluate_rejects_non_datetime_index():
    series = pd.Series(np.arange(10, dtype=float))
    with pytest.raises(TypeError):
        rolling_origin_evaluate(series, _naive_model, "naive", [1], initial_train_size=5)


def _constant_model(value):
    def model(train, horizon):
        return np.full(horizon, value)
    return model


def test_combine_results_matches_manual_weighted_average():
    index = pd.date_range("2020-01-01", periods=15, freq="D")
    series = pd.Series(np.arange(15, dtype=float), index=index)

    results_a = rolling_origin_evaluate(series, _constant_model(0.0), "zero", [1], initial_train_size=10)
    results_b = rolling_origin_evaluate(series, _constant_model(10.0), "ten", [1], initial_train_size=10)

    combined = combine_results(results_a, results_b, weight=0.25, model_name="hybrid")

    expected_forecast = 0.25 * 0.0 + 0.75 * 10.0
    assert (combined["forecast"] == expected_forecast).all()
    assert (combined["model"] == "hybrid").all()
    np.testing.assert_allclose(
        combined["scaled_absolute_error"],
        (combined["actual"] - expected_forecast).abs() / combined["mase_scale"],
    )


def test_combine_results_supports_per_horizon_weight_dict():
    index = pd.date_range("2020-01-01", periods=20, freq="D")
    series = pd.Series(np.arange(20, dtype=float), index=index)

    results_a = rolling_origin_evaluate(series, _constant_model(0.0), "zero", [1, 2], initial_train_size=15)
    results_b = rolling_origin_evaluate(series, _constant_model(10.0), "ten", [1, 2], initial_train_size=15)

    combined = combine_results(results_a, results_b, weight={1: 1.0, 2: 0.0}, model_name="hybrid")

    assert (combined.loc[combined["horizon"] == 1, "forecast"] == 0.0).all()
    assert (combined.loc[combined["horizon"] == 2, "forecast"] == 10.0).all()


def test_combine_results_rejects_incomplete_weight_dict():
    index = pd.date_range("2020-01-01", periods=20, freq="D")
    series = pd.Series(np.arange(20, dtype=float), index=index)

    results_a = rolling_origin_evaluate(series, _constant_model(0.0), "zero", [1, 2], initial_train_size=15)
    results_b = rolling_origin_evaluate(series, _constant_model(10.0), "ten", [1, 2], initial_train_size=15)

    with pytest.raises(ValueError):
        combine_results(results_a, results_b, weight={1: 1.0}, model_name="hybrid")
