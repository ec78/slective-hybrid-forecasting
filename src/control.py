"""A small synthetic controllable system, and the control-fidelity tools built
around it (Post 02).

Testing whether a forecaster has learned a system's genuine input-output
relationship -- as opposed to merely fitting whatever trajectory its
historical policy happened to produce -- requires a ground-truth
counterfactual: what would actually have happened under a different control?
No real historical series (CISO demand, SPY) can give us that, so this one
post works from a small simulated system instead. See
literature/excitation-2026.pdf (Amria et al., 2026) for the paper this is
inspired by, and that paper's response-gain metric (Eq. 3), which
``response_gain`` below implements.
"""

import numpy as np


# ---------------------------------------------------------------------------
# The system: T[t+1] = a*T[t] + b*U[t] + c*D[t] + noise
# ---------------------------------------------------------------------------

def simulate_disturbance(n, period=200, amplitude=1.0, noise_std=0.05, rng=None):
    """A smooth, weather-like exogenous disturbance, independent of control."""
    rng = rng or np.random.default_rng()
    t = np.arange(n)
    return amplitude * np.sin(2 * np.pi * t / period) + rng.normal(scale=noise_std, size=n)


def simulate_open_loop(control, disturbance, a=0.85, b=0.4, c=0.1, noise_std=0.05, t0=0.0, rng=None):
    """Roll the system forward under a *given* control trajectory.

    Used both to generate "excited" context data (control independent of
    state) and to obtain ground-truth outcomes for counterfactual probes.
    """
    rng = rng or np.random.default_rng()
    control = np.asarray(control, dtype=float)
    disturbance = np.asarray(disturbance, dtype=float)
    n = len(control)
    target = np.empty(n)
    target[0] = t0
    for t in range(n - 1):
        target[t + 1] = (
            a * target[t] + b * control[t] + c * disturbance[t] + rng.normal(scale=noise_std)
        )
    return target


def rollout_from(initial_target, control, disturbance, a=0.85, b=0.4, c=0.1, noise_std=0.0, rng=None):
    """Simulate ``len(control)`` steps forward from a known current state.

    Unlike ``simulate_open_loop`` (which treats its first element as a given
    starting sample, useful for generating a full context trajectory), this
    returns exactly the forecasted values at t+1, ..., t+len(control) -- not
    including ``initial_target`` itself. Used to obtain the ground-truth
    outcome of a counterfactual probe continuing from the end of a context.
    """
    rng = rng or np.random.default_rng()
    control = np.asarray(control, dtype=float)
    disturbance = np.asarray(disturbance, dtype=float)
    horizon = len(control)

    forecast = np.empty(horizon)
    previous = initial_target
    for h in range(horizon):
        previous = a * previous + b * control[h] + c * disturbance[h] + rng.normal(scale=noise_std)
        forecast[h] = previous
    return forecast


def simulate_closed_loop(
    disturbance, setpoint=0.0, kp=0.8, u_min=-10.0, u_max=10.0,
    a=0.85, b=0.4, c=0.1, noise_std=0.05, t0=0.0, rng=None,
):
    """Simulate the system under a proportional policy that reacts to the
    current state -- "unexcited" data: control is a near-deterministic
    function of the state (and, if ``setpoint`` varies, of time), so
    observing it carries little *independent* information about the
    system's response.

    ``setpoint`` may be a scalar (constant target) or an array of length
    ``len(disturbance)`` (e.g. a slowly time-varying comfort setpoint) --
    either way the control is fully determined by the setpoint and the
    current state, never by anything orthogonal to them.
    """
    rng = rng or np.random.default_rng()
    disturbance = np.asarray(disturbance, dtype=float)
    n = len(disturbance)
    setpoint = np.full(n, setpoint, dtype=float) if np.isscalar(setpoint) else np.asarray(setpoint, dtype=float)

    target = np.empty(n)
    control = np.empty(n)
    target[0] = t0
    for t in range(n):
        control[t] = np.clip(kp * (setpoint[t] - target[t]), u_min, u_max)
        if t + 1 < n:
            target[t + 1] = (
                a * target[t] + b * control[t] + c * disturbance[t] + rng.normal(scale=noise_std)
            )
    return target, control


# ---------------------------------------------------------------------------
# Excitation signal
# ---------------------------------------------------------------------------

def generate_aprbs(n, amplitude, min_dwell, max_dwell, rng=None):
    """Amplitude-modulated pseudo-random binary sequence: piecewise-constant,
    switching between -amplitude and +amplitude at randomized dwell times.
    Independent of system state -- the opposite of a closed-loop policy.
    """
    rng = rng or np.random.default_rng()
    values = []
    while len(values) < n:
        dwell = int(rng.integers(min_dwell, max_dwell + 1))
        level = rng.choice([-amplitude, amplitude])
        values.extend([level] * dwell)
    return np.asarray(values[:n], dtype=float)


# ---------------------------------------------------------------------------
# Counterfactual probes + response gain
# ---------------------------------------------------------------------------

def build_offset_probes(nominal_control, offsets, u_min=-10.0, u_max=10.0):
    """Constant-offset candidate control trajectories sharing one nominal
    trajectory, clipped to the actuator range (Amria et al., Appendix B).
    """
    nominal_control = np.asarray(nominal_control, dtype=float)
    return {
        offset: np.clip(nominal_control + offset, u_min, u_max)
        for offset in offsets
    }


def response_gain(realized, predicted):
    """Pooled least-squares response gain (Amria et al., Eq. 3).

    Parameters
    ----------
    realized, predicted : array-like, shape (n_probes, horizon) or
        (n_windows, n_probes, horizon)
        Ground-truth and predicted trajectories for a set of matched probes
        that share context, initial state, and disturbances, and differ only
        in their future control.

    Returns
    -------
    float
        1.0 = a correctly scaled response to the control intervention;
        0.0 = no response aligned with the true one (the model may still be
        inaccurate in some *other* direction and still score 0 here --
        gain measures only the component aligned with the true response).
    """
    realized = np.asarray(realized, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    if realized.shape != predicted.shape:
        raise ValueError("realized and predicted must have the same shape.")
    if realized.ndim == 2:
        realized = realized[None]
        predicted = predicted[None]
    if realized.shape[1] < 2:
        raise ValueError("response_gain needs at least two probes per window.")

    # Subtract the per-(window, horizon-step) probe mean -- this removes
    # anything shared across probes (a constant model bias included) and
    # isolates the variation associated with the control intervention.
    realized_dev = realized - realized.mean(axis=1, keepdims=True)
    predicted_dev = predicted - predicted.mean(axis=1, keepdims=True)

    denominator = np.sum(realized_dev**2)
    if denominator == 0:
        raise ValueError("realized deviations are degenerate (zero variance across probes).")

    return float(np.sum(predicted_dev * realized_dev) / denominator)


# ---------------------------------------------------------------------------
# Models: Chronos-2 with covariates, and a linear ARX baseline
# ---------------------------------------------------------------------------

def chronos_control_forecast(
    context_target, context_control, context_disturbance,
    future_control, future_disturbance,
    max_context_length=512,
):
    """Chronos-2 zero-shot forecast conditioned on past + candidate future
    control and known future disturbance, supplied as covariates.
    """
    from src.models import CHRONOS_MODEL_ID, _load_chronos_pipeline

    pipeline = _load_chronos_pipeline(model_id=CHRONOS_MODEL_ID)

    context_target = np.asarray(context_target, dtype=np.float32)[-max_context_length:]
    context_control = np.asarray(context_control, dtype=np.float32)[-max_context_length:]
    context_disturbance = np.asarray(context_disturbance, dtype=np.float32)[-max_context_length:]
    future_control = np.asarray(future_control, dtype=np.float32)
    future_disturbance = np.asarray(future_disturbance, dtype=np.float32)
    horizon = len(future_control)

    item = {
        "target": context_target,
        "past_covariates": {"control": context_control, "disturbance": context_disturbance},
        "future_covariates": {"control": future_control, "disturbance": future_disturbance},
    }
    _, point_forecasts = pipeline.predict_quantiles(
        inputs=[item],
        prediction_length=horizon,
        quantile_levels=[0.5],
        context_length=min(len(context_target), max_context_length),
    )
    return np.asarray(point_forecasts[0], dtype=float).reshape(-1)[:horizon]


def fit_linear_arx(context_target, context_control, context_disturbance):
    """Least-squares fit of T[t+1] = a*T[t] + b*U[t] + c*D[t] + bias on one
    context window.

    A baseline that is handed the *correct functional form* (because we
    know the toy system is linear) and only has to estimate its
    coefficients from the context -- analogous to, but much simpler than,
    the per-window linear system-identification baseline in Amria et al.
    """
    target = np.asarray(context_target, dtype=float)
    control = np.asarray(context_control, dtype=float)
    disturbance = np.asarray(context_disturbance, dtype=float)
    if len(target) < 2:
        raise ValueError("Need at least two context points to fit an ARX model.")

    design = np.column_stack([target[:-1], control[:-1], disturbance[:-1], np.ones(len(target) - 1)])
    targets = target[1:]
    coeffs, *_ = np.linalg.lstsq(design, targets, rcond=None)
    return coeffs  # (a, b, c, bias)


def linear_arx_forecast(coeffs, last_target, future_control, future_disturbance):
    """Recursive multi-step rollout of a fitted ARX model."""
    a, b, c, bias = coeffs
    future_control = np.asarray(future_control, dtype=float)
    future_disturbance = np.asarray(future_disturbance, dtype=float)
    horizon = len(future_control)

    forecast = np.empty(horizon)
    previous = last_target
    for h in range(horizon):
        previous = a * previous + b * future_control[h] + c * future_disturbance[h] + bias
        forecast[h] = previous
    return forecast
