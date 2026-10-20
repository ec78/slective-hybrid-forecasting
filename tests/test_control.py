import numpy as np
import pytest

from src.control import (
    build_offset_probes,
    fit_linear_arx,
    generate_aprbs,
    linear_arx_forecast,
    response_gain,
    rollout_from,
    simulate_closed_loop,
    simulate_open_loop,
)


def test_simulate_open_loop_matches_hand_computed_recursion():
    control = np.array([1.0, 2.0, 3.0])
    disturbance = np.array([0.0, 0.0, 0.0])
    rng = np.random.default_rng(0)
    # noise_std=0 -> fully deterministic
    target = simulate_open_loop(control, disturbance, a=0.5, b=2.0, c=0.0, noise_std=0.0, t0=1.0, rng=rng)

    assert target[0] == 1.0
    assert target[1] == pytest.approx(0.5 * 1.0 + 2.0 * 1.0)  # a*T0 + b*U0
    assert target[2] == pytest.approx(0.5 * target[1] + 2.0 * 2.0)  # a*T1 + b*U1


def test_simulate_closed_loop_control_reacts_to_state():
    disturbance = np.zeros(10)
    rng = np.random.default_rng(0)
    target, control = simulate_closed_loop(
        disturbance, setpoint=5.0, kp=1.0, u_min=-100, u_max=100,
        a=0.9, b=1.0, c=0.0, noise_std=0.0, t0=0.0, rng=rng,
    )
    # control[t] must equal kp*(setpoint - target[t]) exactly (no clipping hit here)
    np.testing.assert_allclose(control, 1.0 * (5.0 - target))
    # and the state recursion must hold
    np.testing.assert_allclose(target[1:], 0.9 * target[:-1] + 1.0 * control[:-1])


def test_simulate_closed_loop_respects_actuator_clip():
    disturbance = np.zeros(5)
    target, control = simulate_closed_loop(
        disturbance, setpoint=1000.0, kp=10.0, u_min=-2.0, u_max=2.0,
        a=0.9, b=0.1, c=0.0, noise_std=0.0, rng=np.random.default_rng(0),
    )
    assert np.all(control <= 2.0) and np.all(control >= -2.0)


def test_rollout_from_matches_hand_computed_recursion_and_excludes_initial():
    control = np.array([1.0, 0.0, 2.0])
    disturbance = np.array([0.0, 0.0, 0.0])
    forecast = rollout_from(initial_target=1.0, control=control, disturbance=disturbance,
                             a=0.5, b=2.0, c=0.0, noise_std=0.0, rng=np.random.default_rng(0))

    assert len(forecast) == 3  # excludes the initial point, unlike simulate_open_loop
    expected_0 = 0.5 * 1.0 + 2.0 * 1.0
    expected_1 = 0.5 * expected_0 + 2.0 * 0.0
    expected_2 = 0.5 * expected_1 + 2.0 * 2.0
    np.testing.assert_allclose(forecast, [expected_0, expected_1, expected_2])


def test_generate_aprbs_within_amplitude_and_piecewise_constant():
    rng = np.random.default_rng(1)
    signal = generate_aprbs(200, amplitude=3.0, min_dwell=2, max_dwell=5, rng=rng)
    assert len(signal) == 200
    assert np.all(np.isin(signal, [-3.0, 3.0]))
    # not constant throughout (should actually switch at least once)
    assert len(np.unique(signal)) == 2


def test_build_offset_probes_shapes_and_clip():
    nominal = np.array([0.0, 1.0, 2.0])
    probes = build_offset_probes(nominal, offsets=[-10, 0, 10], u_min=-5, u_max=5)
    assert set(probes.keys()) == {-10, 0, 10}
    np.testing.assert_allclose(probes[0], nominal)
    assert np.all(probes[-10] == -5.0)
    assert np.all(probes[10] == 5.0)


def test_response_gain_perfect_alignment_is_one():
    # predicted == realized exactly -> gain must be 1
    realized = np.array([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0]])  # 3 probes, horizon 2
    gain = response_gain(realized, realized.copy())
    assert gain == pytest.approx(1.0)


def test_response_gain_zero_when_predictions_identical_across_probes():
    # predicted doesn't vary with the probe at all -> no aligned response -> gain 0
    realized = np.array([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0]])
    predicted = np.full_like(realized, fill_value=7.0)
    gain = response_gain(realized, predicted)
    assert gain == pytest.approx(0.0)


def test_response_gain_scales_correctly():
    realized = np.array([[-1.0], [0.0], [1.0]])
    predicted_half = realized * 0.5
    assert response_gain(realized, predicted_half) == pytest.approx(0.5)
    predicted_double = realized * 2.0
    assert response_gain(realized, predicted_double) == pytest.approx(2.0)


def test_response_gain_ignores_shared_constant_bias():
    realized = np.array([[-1.0], [0.0], [1.0]])
    predicted = realized + 1000.0  # huge shared offset, no probe-dependent error
    assert response_gain(realized, predicted) == pytest.approx(1.0)


def test_response_gain_supports_multiple_windows():
    realized = np.stack([
        np.array([[-1.0], [0.0], [1.0]]),
        np.array([[-2.0], [0.0], [2.0]]),
    ])
    predicted = realized.copy()
    assert response_gain(realized, predicted) == pytest.approx(1.0)


def test_response_gain_rejects_degenerate_realized():
    realized = np.ones((3, 2))  # no variation across probes
    with pytest.raises(ValueError):
        response_gain(realized, realized.copy())


def test_fit_linear_arx_recovers_true_coefficients_noiseless():
    rng = np.random.default_rng(2)
    n = 50
    control = rng.normal(size=n)
    disturbance = rng.normal(size=n)
    target = simulate_open_loop(control, disturbance, a=0.7, b=1.5, c=-0.3, noise_std=0.0, t0=0.0, rng=rng)

    a, b, c, bias = fit_linear_arx(target, control, disturbance)
    assert a == pytest.approx(0.7, abs=1e-6)
    assert b == pytest.approx(1.5, abs=1e-6)
    assert c == pytest.approx(-0.3, abs=1e-6)
    assert bias == pytest.approx(0.0, abs=1e-6)


def test_linear_arx_forecast_matches_hand_computed_rollout():
    coeffs = (0.5, 2.0, 0.0, 1.0)  # a, b, c, bias
    future_control = np.array([1.0, 0.0])
    future_disturbance = np.array([0.0, 0.0])
    forecast = linear_arx_forecast(coeffs, last_target=0.0, future_control=future_control, future_disturbance=future_disturbance)

    expected_0 = 0.5 * 0.0 + 2.0 * 1.0 + 0.0 + 1.0
    expected_1 = 0.5 * expected_0 + 2.0 * 0.0 + 0.0 + 1.0
    np.testing.assert_allclose(forecast, [expected_0, expected_1])
