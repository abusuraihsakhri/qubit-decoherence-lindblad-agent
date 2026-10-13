"""HTTP API for threshold audits and analytic one-qubit decoherence."""
import hmac
import math
import os
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .base import AuditLogger, SecurityException
from .models import SystemTaskPayload
from .supervisor import SystemSupervisor
from lindblad_decoherence.physics import simulate_decoherence

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Qubit Decoherence Lindblad Agent API",
    description="Threshold-based audit workflow and analytic GKSL single-qubit simulation.",
    version="3.1.0",
)


class ChatRequest(BaseModel):
    query: str


class SimulationRequest(BaseModel):
    t1: float = Field(..., gt=0, allow_inf_nan=False)
    t2: float = Field(..., gt=0, allow_inf_nan=False)
    duration: float = Field(..., gt=0, allow_inf_nan=False)
    steps: int = Field(default=201, ge=2, le=2001)
    theta: float = Field(default=math.pi / 2, ge=0, le=math.pi, allow_inf_nan=False)
    phi: float = Field(default=0, allow_inf_nan=False)
    omega: float = Field(default=0, allow_inf_nan=False)


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "qubit-decoherence-lindblad-agent",
            "domain": "Quantum physics and threshold audits", "version": "3.1.0"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "audit_chain_valid": AuditLogger.verify_integrity(),
    }


@app.post("/api/simulate")
def api_simulate(req: SimulationRequest):
    try:
        return simulate_decoherence(**req.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        return supervisor.process_task(payload).to_dict()
    except SecurityException as exc:
        raise HTTPException(status_code=422, detail="A prohibited identifier was detected") from exc


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        return {"response": supervisor.query_supervisory_chat(req.query)}
    except SecurityException as exc:
        raise HTTPException(status_code=422, detail="A prohibited identifier was detected") from exc


@app.get("/api/audit/logs")
def api_audit_logs(x_audit_api_key: str | None = Header(default=None)):
    """Detailed audit metadata is never public without explicit configuration."""
    expected = os.getenv("AUDIT_API_KEY")
    if not expected or not x_audit_api_key or not hmac.compare_digest(expected, x_audit_api_key):
        raise HTTPException(status_code=403, detail="Audit log access is disabled or unauthorized")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}


WEB_DIR = Path(__file__).resolve().parent.parent / "web"
if WEB_DIR.is_dir():
    app.mount("/web", StaticFiles(directory=str(WEB_DIR), html=True), name="web")

    @app.get("/", include_in_schema=False)
    def index():
        return RedirectResponse("/web/")
