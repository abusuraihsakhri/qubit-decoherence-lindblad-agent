"""
Tests for security, validation, and reliability improvements.
"""
import sys
import os
import warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import tempfile
import csv

from agents.base import AuditTrail, PHIGuard, SecurityException
from cli import _validate_input_path, _safe_float
from enrichment import (
    LindbladMasterEquationSolverWithAdaptiveTimeSteppingEngine,
    ImplementationEngine,
    FilesToCreatemodifyEngine,
    TestingEngine,
    QuantumProcessTomographyViaLindbladSuperoperatorEngine,
    QubitdecoherencelindbladagentEnrichmentSuite,
)


class TestAuditTrailSecurity:
    """Test secure audit trail key generation."""

    def test_audit_trail_generates_key_when_env_not_set(self):
        """When AUDIT_SECRET_KEY is not set, a random key should be generated."""
        original_key = os.environ.pop("AUDIT_SECRET_KEY", None)
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                trail = AuditTrail()
                assert len(w) == 1
                assert "AUDIT_SECRET_KEY not set" in str(w[0].message)
            assert trail.secret_key is not None
            assert len(trail.secret_key) > 0
        finally:
            if original_key is not None:
                os.environ["AUDIT_SECRET_KEY"] = original_key

    def test_audit_trail_uses_env_key_when_set(self):
        """When AUDIT_SECRET_KEY is set, it should be used."""
        test_key = "test-secret-key-12345"
        original_key = os.environ.get("AUDIT_SECRET_KEY")
        os.environ["AUDIT_SECRET_KEY"] = test_key
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                trail = AuditTrail()
                assert len(w) == 0
            assert trail.secret_key == test_key.encode("utf-8")
        finally:
            if original_key is not None:
                os.environ["AUDIT_SECRET_KEY"] = original_key
            else:
                del os.environ["AUDIT_SECRET_KEY"]

    def test_audit_trail_accepts_explicit_key(self):
        """Explicit key parameter should take precedence."""
        explicit_key = "explicit-key-12345"
        trail = AuditTrail(secret_key=explicit_key)
        assert trail.secret_key == explicit_key.encode("utf-8")


class TestInputValidation:
    """Test input validation functions."""

    def test_validate_existing_file(self):
        """Valid file path should return resolved path."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            f.write(b"test")
            temp_path = f.name
        try:
            result = _validate_input_path(temp_path)
            assert Path(result).exists()
        finally:
            os.unlink(temp_path)

    def test_validate_nonexistent_file_raises(self):
        """Non-existent file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            _validate_input_path("/nonexistent/path/file.csv")

    def test_validate_directory_raises(self):
        """Directory path should raise ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="not a file"):
                _validate_input_path(tmpdir)

    def test_safe_float_valid(self):
        """Valid float string should parse correctly."""
        assert _safe_float("3.14", "test", 0.0) == 3.14
        assert _safe_float("42", "test", 0.0) == 42.0

    def test_safe_float_invalid_raises(self):
        """Invalid float string should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid numeric value"):
            _safe_float("not-a-number", "test_field", 0.0)


class TestEnrichmentSuite:
    """Test enrichment suite after deduplication."""

    def test_all_engines_unique(self):
        """All 5 engines should be present and unique."""
        suite = QubitdecoherencelindbladagentEnrichmentSuite()
        assert suite.lindbladmasterequati is not None
        assert suite.implementationengine is not None
        assert suite.filestocreatemodifye is not None
        assert suite.testingengine is not None
        assert suite.quantumprocesstomogr is not None

    def test_execute_all_returns_five_results(self):
        """execute_all should return exactly 5 unique results."""
        suite = QubitdecoherencelindbladagentEnrichmentSuite()
        results = suite.execute_all(primary_val=0.5, secondary_val=0.2)
        assert len(results) == 5
        expected_keys = {
            "LindbladMasterEquationSolverWithAdaptiveTimeSteppingEngine",
            "ImplementationEngine",
            "FilesToCreatemodifyEngine",
            "TestingEngine",
            "QuantumProcessTomographyViaLindbladSuperoperatorEngine",
        }
        assert set(results.keys()) == expected_keys

    def test_enrichment_threshold_escalation(self):
        """Values above threshold should trigger WARNING or CRITICAL."""
        suite = QubitdecoherencelindbladagentEnrichmentSuite()
        results = suite.execute_all(primary_val=10.0, secondary_val=5.0)
        for k, v in results.items():
            assert v.status in ["WARNING", "CRITICAL_ALERT"]
            assert len(v.alerts) > 0


class TestBatchCLI:
    """Test batch CLI with validation."""

    def test_batch_with_valid_csv(self, tmp_path):
        """Batch processing should work with valid CSV."""
        from cli import main
        csv_file = tmp_path / "test_input.csv"
        csv_file.write_text(
            "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n"
            "T1,TARGET-01,28.4,14.2,True,DISCORDANT\n"
            "T2,TARGET-02,12.0,4.1,False,NOMINAL\n"
        )
        output_file = tmp_path / "test_output.csv"
        ret = main(["batch", "-i", str(csv_file), "-o", str(output_file)])
        assert ret == 0
        assert output_file.exists()

    def test_batch_with_missing_file(self):
        """Batch processing with missing file should raise error."""
        from cli import main
        with pytest.raises(FileNotFoundError):
            main(["batch", "-i", "/nonexistent/file.csv"])
