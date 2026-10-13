"""Physical regression tests independent of legacy threshold-audit tests."""
import math
import pytest
from agents.base import AuditTrail
from agents.models import SystemTaskPayload
from lindblad_decoherence.physics import simulate_decoherence


def test_plus_state_relaxation_and_dephasing():
    t1, t2, t = 30.0, 20.0, 20.0
    result = simulate_decoherence(t1, t2, t, steps=2)
    initial, final = result["samples"]
    assert initial["p_excited"] == pytest.approx(0.5)
    assert initial["coherence_abs"] == pytest.approx(0.5)
    assert initial["purity"] == pytest.approx(1)
    assert final["p_excited"] == pytest.approx(0.5 * math.exp(-t / t1))
    assert final["coherence_abs"] == pytest.approx(0.5 * math.exp(-t / t2))
    assert result["gamma_phi"] == pytest.approx(1 / t2 - 1 / (2 * t1))
    assert 0.5 <= final["purity"] <= 1


def test_bloch_phase_and_equilibrium():
    result = simulate_decoherence(
        t1=10, t2=20, duration=250, steps=3,
        theta=math.pi / 2, omega=1,
    )
    last = result["samples"][-1]
    assert last["p_excited"] < 1e-10
    assert last["coherence_abs"] < 1e-5
    assert last["purity"] == pytest.approx(1, abs=1e-8)
    initial = simulate_decoherence(
        10, 10, 1, steps=2, theta=math.pi / 2,
        phi=math.pi / 2,
    )["samples"][0]
    assert initial["x"] == pytest.approx(0, abs=1e-12)
    assert initial["y"] == pytest.approx(1)


@pytest.mark.parametrize("args", [
    (0, 1, 10), (1, -1, 10), (1, 1, 0),
    (1, 2.01, 10), (math.inf, 1, 10),
    (1, math.nan, 10),
])
def test_invalid_physics_rejected(args):
    with pytest.raises(ValueError):
        simulate_decoherence(*args)


def test_bad_sample_count_and_theta_rejected():
    with pytest.raises(ValueError):
        simulate_decoherence(1, 1, 10, steps=1)
    with pytest.raises(ValueError):
        simulate_decoherence(1, 1, 10, steps=2002)
    with pytest.raises(ValueError):
        simulate_decoherence(1, 1, 10, theta=math.pi + 0.1)


def test_audit_hmac_catches_content_modification():
    trail = AuditTrail(secret_key="unit-test-only")
    trail.log("runner", "test", "FIRST", {"total_alerts": 0})
    trail.log("runner", "test", "SECOND", {"total_alerts": 1})
    assert trail.verify_integrity()
    snapshot = trail.get_trail()
    snapshot[0]["actor"] = "tampered-external-copy"
    assert trail.verify_integrity()  # snapshots cannot modify the internal ledger
    trail.logs[0]["actor"] = "tampered"
    assert not trail.verify_integrity()


def test_nonfinite_payload_rejected():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="X", target_identifier="Q1", primary_metric=math.nan)
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="X", target_identifier="Q1", primary_metric=1, secondary_metric=math.inf)


def test_audit_hmac_prevents_field_repartition():
    trail = AuditTrail(secret_key="unit-test-only")
    trail.log("a|b", "c", "EVENT", {"count": 1})
    assert trail.verify_integrity()
    trail.logs[0]["actor"] = "a"
    trail.logs[0]["actor_tier"] = "b|c"
    assert not trail.verify_integrity()


def test_physics_cli_csv_export(tmp_path):
    import csv
    from lindblad_decoherence.cli import main
    destination = tmp_path / "trajectory.csv"
    assert main([
        "simulate", "--t1", "30", "--t2", "20",
        "--duration", "10", "--steps", "3",
        "--output", str(destination),
    ]) == 0
    with destination.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 3
    assert float(rows[0]["p_excited"]) == pytest.approx(0.5)
    assert float(rows[-1]["p_excited"]) == pytest.approx(0.5 * math.exp(-10 / 30))
