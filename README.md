# Qubit Decoherence Lindblad Agent

> **Domain:** Clinical Decision Support & Biomedical Computing / Quantum Physics  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks` / `Open Quantum Systems Theory`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Qubit Decoherence Lindblad Agent is a multi-agent analytical platform that evaluates system tasks through specialized worker agents, producing consensus dossiers with cryptographic audit trails. The system includes:

- **Clinical & Biomedical AI Module**: Multi-tier risk classification with automated action recommendations
- **Quantum Physics Module**: Lindblad Master Equation T1/T2 qubit decoherence simulation
- **Enrichment Suite**: Adaptive time-stepping solver, quantum process tomography, and calibration engines

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED_RISK, CRITICAL_STAT_PANIC)
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection
- **Multi-Agent Consensus**: InvariantQC, SafetyEscalation, ProtocolConformance, and specialized Lindblad agents
- **Enrichment Engines**: 5 specialized engines for adaptive solving, implementation, testing, and quantum process tomography

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/qubit-decoherence-lindblad-agent.git
cd qubit-decoherence-lindblad-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# Optional: Set audit secret key for persistent audit integrity
export AUDIT_SECRET_KEY="your-secure-random-key-here"
```

---

## 🚀 CLI Quickstart & Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Interactive Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
| Parameter | Description | Default |
|:----------|:------------|:--------|
| `--task-id` | Unique task/case identifier | TASK-2026-001 |
| `--target` | Entity or target identifier | KEY-TARGET-01 |
| `--primary` | Primary measurement (float) | 28.5 |
| `--secondary` | Secondary metric (float) | 14.2 |
| `--critical` | Emergency escalation flag | False |
| `--status` | Status descriptor | DISCORDANT |

### Input Data Schema (CSV Batch)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Parameter / observation metric | Required |
| `target_identifier` | Parameter / observation metric | Required |
| `primary_metric` | Numeric primary measurement | Required |
| `secondary_metric` | Numeric secondary measurement | Required |
| `is_critical_flag` | Boolean critical flag | Optional |
| `status_descriptor` | Status code or phenotype | Optional |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation
* **Secure Key Management:** Audit keys generated via `secrets.token_hex()` if `AUDIT_SECRET_KEY` env var not set
* **Input Validation:** Batch processing validates file paths and numeric inputs with descriptive errors
* **Air-Gapped LLM Reasoning Adapter:** Local Ollama, Claude, OpenAI integration with deterministic test mocks

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

Run Lindblad decoherence module CLI:

```bash
python lindblad_decoherence_app.py audit --task-id Q-001 --primary 29.4 --secondary 15.1
```

---

## 🐳 Container Deployment

```bash
# Build and run with Docker Compose (recommended)
AUDIT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))") docker-compose up --build

# Or manual Docker build
docker build -t qubit-decoherence-lindblad-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY="your-key" qubit-decoherence-lindblad-agent
```

---

## 📁 Project Structure

```
qubit-decoherence-lindblad-agent/
├── agents/                     # Core multi-agent system
│   ├── api.py                  # FastAPI REST endpoints
│   ├── base.py                 # Security, PHI guard, HMAC audit
│   ├── models.py               # Pydantic data schemas
│   ├── supervisor.py           # Orchestrator coordinator
│   ├── workers.py              # Specialized evaluation workers
│   ├── llm_factory.py          # LLM client abstraction
│   ├── learning.py             # Bayesian calibration engine
│   ├── metrics.py              # Prometheus metrics collector
│   └── streamer.py             # WebSocket telemetry broadcaster
├── lindblad_decoherence/       # Quantum physics module
│   ├── engine.py               # Core algorithmic engine
│   ├── agents.py               # Specialized sub-agents
│   ├── models.py               # Data models
│   ├── cli.py                  # CLI interface
│   └── server.py               # FastAPI server factory
├── tests/                      # Test suite
├── web/index.html              # Operations console UI
├── cli.py                      # Main CLI entry point
├── lindblad_decoherence_app.py # Lindblad CLI entry point
├── simulator.py                # High-throughput stress simulator
├── enrichment.py               # Enrichment feature engines
├── pyproject.toml              # Package configuration
├── Dockerfile                  # Container definition
└── docker-compose.yml          # Multi-service orchestration
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
