"""Analytic GKSL evolution for one qubit with zero-temperature T1 decay and pure dephasing.

Hamiltonian H = (omega/2) sigma_z, jump L1 = sqrt(1/T1) sigma_-,
and dephasing jump Lphi = sqrt(gamma_phi/2) sigma_z, with
gamma_phi = 1/T2 - 1/(2*T1) >= 0. Units of time must be consistent.
"""
import math


def simulate_decoherence(
    t1: float,
    t2: float,
    duration: float,
    steps: int = 201,
    theta: float = math.pi / 2,
    phi: float = 0.0,
    omega: float = 0.0,
) -> dict:
    """Return sampled Bloch coordinates and density-matrix observables.

    Initial state: cos(theta/2)|0> + exp(i*phi)sin(theta/2)|1>.
    The bath is at zero temperature; the equilibrium state is |0>.
    """
    values = (t1, t2, duration, theta, phi, omega)
    if any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError("All physical parameters must be finite numbers")
    if t1 <= 0 or t2 <= 0 or duration <= 0:
        raise ValueError("T1, T2, and duration must be positive")
    if t2 > 2 * t1 * (1 + 1e-12):
        raise ValueError("T2 must not exceed 2*T1 for this Markovian model")
    if not isinstance(steps, int) or isinstance(steps, bool) or not 2 <= steps <= 2001:
        raise ValueError("steps must be an integer between 2 and 2001")
    if not 0 <= theta <= math.pi:
        raise ValueError("theta must be between 0 and pi radians")

    gamma_phi = max(0.0, 1 / t2 - 1 / (2 * t1))
    sin_theta = math.sin(theta)
    cos_theta = math.cos(theta)
    samples = []
    for i in range(steps):
        t = duration * i / (steps - 1)
        decay1 = math.exp(-t / t1)
        decay2 = math.exp(-t / t2)
        phase = phi + omega * t
        x = sin_theta * decay2 * math.cos(phase)
        y = sin_theta * decay2 * math.sin(phase)
        z = 1 - (1 - cos_theta) * decay1
        samples.append({
            "time": t,
            "p_excited": (1 - z) / 2,
            "coherence_abs": math.hypot(x, y) / 2,
            "purity": (1 + x * x + y * y + z * z) / 2,
            "x": x, "y": y, "z": z,
        })
    return {
        "model": "zero-temperature GKSL amplitude damping and pure dephasing",
        "t1": t1,
        "t2": t2,
        "gamma_phi": gamma_phi,
        "duration": duration,
        "steps": steps,
        "theta": theta,
        "phi": phi,
        "omega": omega,
        "samples": samples,
    }
