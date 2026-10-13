"""
Command-Line Interface for Lindblad Master Equation T1 / T2 Qubit Decoherence Simulator.
"""
import argparse
import csv
import json
import sys
from pathlib import Path
from .models import FrontierPayload
from .agents import LindbladCoordinator
from .physics import simulate_decoherence

coordinator = LindbladCoordinator()


def _validate_input_path(filepath: str) -> str:
    """Validate input file path exists and is within allowed directory."""
    path = Path(filepath).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {filepath}")
    if not path.is_file():
        raise ValueError(f"Input path is not a file: {filepath}")
    return str(path)


def _safe_float(value: str, field_name: str, default: float) -> float:
    """Safely parse a float value with descriptive error handling."""
    try:
        return float(value)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid numeric value for '{field_name}': {value!r}") from e


def main(argv=None):
    parser = argparse.ArgumentParser(prog="qubit-decoherence-lindblad-agent", description="Lindblad Master Equation T1 / T2 Qubit Decoherence Simulator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Physical single-qubit simulation
    p_sim = subparsers.add_parser("simulate", help="Simulate GKSL T1/T2 decoherence")
    p_sim.add_argument("--t1", type=float, required=True, help="Energy relaxation time")
    p_sim.add_argument("--t2", type=float, required=True, help="Coherence decay time (must be <= 2*T1)")
    p_sim.add_argument("--duration", type=float, required=True)
    p_sim.add_argument("--steps", type=int, default=201)
    p_sim.add_argument("--theta", type=float, default=1.5707963267948966, help="Initial polar angle (radians)")
    p_sim.add_argument("--phi", type=float, default=0.0, help="Initial azimuth (radians)")
    p_sim.add_argument("--omega", type=float, default=0.0, help="Qubit angular frequency (radians per time)")
    p_sim.add_argument("--output", help="Optional CSV destination (otherwise JSON to stdout)")

    # Audit
    p_audit = subparsers.add_parser("audit", help="Run single task evaluation")
    p_audit.add_argument("--task-id", default="TASK-2026-001")
    p_audit.add_argument("--target", default="TARGET-GEN-01")
    p_audit.add_argument("--primary", type=float, default=29.4)
    p_audit.add_argument("--secondary", type=float, default=15.1)
    p_audit.add_argument("--critical", action="store_true")
    p_audit.add_argument("--status", default="DISCORDANT")

    # Chat
    p_chat = subparsers.add_parser("chat", help="System configuration query")
    p_chat.add_argument("query", nargs="+")

    # Batch
    p_batch = subparsers.add_parser("batch", help="Batch process CSV records")
    p_batch.add_argument("-i", "--input", required=True)
    p_batch.add_argument("-o", "--output", default="results.csv")

    # Serve
    p_serve = subparsers.add_parser("serve", help="Launch FastAPI REST server")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)

    if args.command == "simulate":
        try:
            result = simulate_decoherence(
                args.t1, args.t2, args.duration, args.steps,
                args.theta, args.phi, args.omega,
            )
        except ValueError as exc:
            parser.error(str(exc))
        if args.output:
            with open(args.output, "w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(result["samples"][0]))
                writer.writeheader()
                writer.writerows(result["samples"])
            print(f"Wrote {len(result['samples'])} time points to {args.output}")
        else:
            print(json.dumps(result, indent=2))
        return 0

    if args.command == "audit":
        payload = FrontierPayload(
            task_id=args.task_id,
            target_identifier=args.target,
            primary_metric=args.primary,
            secondary_metric=args.secondary,
            status_descriptor=args.status,
            is_critical_flag=args.critical,
        )
        dossier = coordinator.process(payload)
        print("=" * 80)
        print(f"  LINDBLAD MASTER EQUATION T1 / T2 QUBIT DECOHERENCE SIMULATOR")
        print(f"  Domain: Quantum Physics | Standard: Open Quantum Systems Theory")
        print(f"  Task: {dossier['task_id']} | Status: [{dossier['overall_status']}] | Total Alerts: {dossier['total_alerts']}")
        print("=" * 80)
        for a in dossier["alerts"]:
            print(f"\n  [{a['status']}] from {a['origin_agent']}:")
            print(f"  Summary: {a['summary']}")
            print(f"  Details: {a['technical_details']}")
            print(f"  Action:  {a['actionable_remediation']}")
        print("\n" + "=" * 80)
        return 0

    if args.command == "chat":
        ans = coordinator.query_supervisory_chat(" ".join(args.query))
        print(f"\n[LindbladCoordinator]:\n{ans}\n")
        return 0

    if args.command == "batch":
        input_path = _validate_input_path(args.input)
        with open(input_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames or [])
            rows = list(reader)

        out_fields = fieldnames + ["overall_status", "total_alerts", "critical_count", "consensus_summary"]
        out_rows = []
        errors = []
        for idx, r in enumerate(rows):
            try:
                payload = FrontierPayload(
                    task_id=r.get("task_id", "TASK-01"),
                    target_identifier=r.get("target_identifier", "TARGET-01"),
                    primary_metric=_safe_float(r.get("primary_metric", "15.0"), "primary_metric", 15.0),
                    secondary_metric=_safe_float(r.get("secondary_metric", "5.0"), "secondary_metric", 5.0),
                    status_descriptor=r.get("status_descriptor", "NOMINAL"),
                    is_critical_flag=str(r.get("is_critical_flag", "")).lower() in ("true", "1", "yes"),
                )
                dossier = coordinator.process(payload)
                row_dict = dict(r)
                row_dict["overall_status"] = dossier["overall_status"]
                row_dict["total_alerts"] = dossier["total_alerts"]
                row_dict["critical_count"] = dossier["critical_count"]
                row_dict["consensus_summary"] = dossier["consensus_summary"]
                out_rows.append(row_dict)
            except (ValueError, Exception) as e:
                errors.append(f"Row {idx + 1}: {e}")

        if errors:
            print(f"WARNING: {len(errors)} row(s) had errors:")
            for err in errors:
                print(f"  - {err}")

        with open(args.output, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(out_rows)
        print(f"Processed {len(out_rows)}/{len(rows)} records -> {args.output}")
        return 0

    if args.command == "serve":
        try:
            import uvicorn
            from .server import create_app
            app = create_app()
            if app:
                print(f"Starting Lindblad Master Equation T1 / T2 Qubit Decoherence Simulator on http://{args.host}:{args.port}")
                uvicorn.run(app, host=args.host, port=args.port)
        except ImportError:
            print("FastAPI / uvicorn not installed. Run 'pip install fastapi uvicorn'")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
