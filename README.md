# Qubit Decoherence Lindblad Agent

A reproducible single-qubit decoherence calculator, accompanied by an older rule-based threshold-audit workflow. The two are independent: **a threshold-audit alert is not a result from solving a Lindblad master equation**.

## Browser simulator

Open `web/index.html` in a browser to use the simulator without installing Python or running a server. Enter relaxation time **T1**, coherence time **T2**, duration, initial Bloch-state angles, and optional angular frequency. The app calculates trajectories, plots excited-state probability, coherence magnitude, and purity, and exports CSV files.

- No network request is made during physics simulation; no input is uploaded.
- The optional threshold-audit panel is **server-only**. On a static host, it clearly reports that the API is unavailable rather than inventing results.
- The current public GitHub Pages deployment has not been verified. For now, open the HTML file directly or serve the app locally.

## Physical model and limitations

The model solves the **analytic** GKSL master equation for a single qubit, with Hamiltonian `H = (omega/2) sigma_z`, amplitude damping jump `sqrt(1/T1) sigma_-`, and pure dephasing jump `sqrt(gamma_phi/2) sigma_z`, where:

```text
gamma_phi = 1/T2 - 1/(2*T1) >= 0
P(|1>, t) = sin(theta/2)^2 * exp(-t/T1)
|rho_01(t)| = |sin(theta)|/2 * exp(-t/T2)
purity(t) = (1 + x(t)^2 + y(t)^2 + z(t)^2)/2
```

For complete positivity under these assumptions, `T1 > 0`, `T2 > 0`, and `T2 <= 2*T1`. The bath is at zero temperature, the dynamics are time-homogeneous and Markovian, and the initial state is `cos(theta/2)|0> + exp(i*phi)sin(theta/2)|1>`. Angles are in radians; times and inverse rates must share compatible units. This is **not** a general numerical multi-qubit Lindblad solver, hardware-calibrated simulator, process tomography implementation, or adaptive Runge–Kutta solver.

## Installation

Python 3.9+ is supported for the physics engine. For local API and tests:

```bash
git clone https://github.com/abusuraihsakhri/qubit-decoherence-lindblad-agent.git
cd qubit-decoherence-lindblad-agent
python -m pip install -e ".[server,test]"
python -m pytest -q
```

The analytic physics module has no third-party runtime dependencies.

## Physics CLI

```bash
python -m lindblad_decoherence.cli simulate --t1 30 --t2 20 --duration 100 --steps 201
python -m lindblad_decoherence.cli simulate --t1 30 --t2 20 --duration 100 --output trajectory.csv
```

The CLI prints a JSON object with a time series unless `--output` specifies CSV. The model also accepts `--theta`, `--phi`, and `--omega`. Input outside the physically valid parameter region is rejected.

## Local HTTP API and threshold audits

```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000/web/](http://127.0.0.1:8000/web/) for the browser UI, or [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the API schema.

- `POST /api/simulate`: validated physics input (`t1`, `t2`, `duration`, optional `steps`, `theta`, `phi`, `omega`), returning trajectories.
- `POST /api/audit`: original three-worker **heuristic threshold** evaluation with HMAC-linked metadata.
- `GET /health`, `GET /metrics`, `POST /api/chat`: existing service operations (chat uses a deterministic local placeholder, not a deployed language model).
- `GET /api/audit/logs`: requires an `AUDIT_API_KEY` server environment variable and matching `X-Audit-Api-Key` request header; otherwise returns 403.
- Existing command workflows are retained: `python cli.py audit ...`, `python cli.py batch -i sample.csv -o results.csv`, `python cli.py verify-audit`, and `python lindblad_decoherence_app.py audit ...`.

Audit thresholds (25 and 12 in the main workers, 25 and 10 in the alternative Lindblad-named audit module) are application-defined heuristics, **not** quantum physical constants or validated clinical thresholds. The older `enrichment.py` module remains for compatibility: its five classes evaluate simple thresholds and do **not** implement adaptive integration or process tomography.

## Privacy and security

The browser physics calculation is local. The API accepts JSON and retains threshold audit results and HMAC metadata **in memory**, not persistent storage. An optional `AUDIT_SECRET_KEY` environment variable sets a stable HMAC key; otherwise a random per-process key is generated. The chain now verifies the HMAC of each record, not just its predecessor pointer. The legacy identifier guard is **regex-based and incomplete**: it does not provide guaranteed de-identification, HIPAA compliance, or clinical safety. Do not send identifiable or sensitive health data. Do not expose the development service to untrusted networks without authentication, access controls, and deployment hardening.

## Development, CI, and compatibility

```bash
python -m pytest -q
node --check web/app.js
node tests/test_web.js
```

GitHub Actions tests Python 3.10–3.12 plus JavaScript with Node 22. Browser functionality uses modern JavaScript, inline SVG, and Blob downloads without external libraries or fonts. The Dockerfile and Compose file run the Python API; GitHub Pages can host **only** the browser calculation and not the server endpoints. A Python-in-WebAssembly runtime is unnecessary because the same analytic solution is implemented directly in browser JavaScript.

## License

[MIT](LICENSE).
