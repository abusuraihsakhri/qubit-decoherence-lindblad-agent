"use strict";

// Exact analytic solution to a zero-temperature single-qubit GKSL semigroup.
const byId = (id) => document.getElementById(id);
const ns = "http://www.w3.org/2000/svg";
let latestSamples = null;

function readNumber(id) {
  const element = byId(id);
  const value = element.valueAsNumber;
  if (!Number.isFinite(value)) throw new Error("Enter a finite value for " + id + ".");
  return value;
}

function simulate(params) {
  const { t1, t2, duration, steps, theta, phi, omega } = params;
  if (t1 <= 0 || t2 <= 0 || duration <= 0) {
    throw new Error("T₁, T₂, and duration must be positive.");
  }
  if (t2 > 2 * t1 * (1 + 1e-12)) {
    throw new Error("T₂ cannot exceed 2T₁ in this Markovian model.");
  }
  if (!Number.isInteger(steps) || steps < 2 || steps > 2001) {
    throw new Error("Time points must be an integer between 2 and 2001.");
  }
  if (theta < 0 || theta > Math.PI) {
    throw new Error("θ must lie between 0 and π radians.");
  }

  const sinTheta = Math.sin(theta);
  const cosTheta = Math.cos(theta);
  const samples = [];
  for (let i = 0; i < steps; i += 1) {
    const time = duration * i / (steps - 1);
    const decay1 = Math.exp(-time / t1);
    const decay2 = Math.exp(-time / t2);
    const phase = phi + omega * time;
    const x = sinTheta * decay2 * Math.cos(phase);
    const y = sinTheta * decay2 * Math.sin(phase);
    const z = 1 - (1 - cosTheta) * decay1;
    samples.push({
      time,
      p_excited: (1 - z) / 2,
      coherence_abs: Math.hypot(x, y) / 2,
      purity: (1 + x * x + y * y + z * z) / 2,
      x, y, z
    });
  }
  return samples;
}

function svgElement(name, attrs, text) {
  const element = document.createElementNS(ns, name);
  Object.entries(attrs).forEach(([k, v]) => element.setAttribute(k, String(v)));
  if (text !== undefined) element.textContent = text;
  return element;
}

function draw(samples, duration) {
  const grid = byId("plot-grid");
  grid.replaceChildren();
  const x0 = 57, y0 = 18, w = 682, h = 268;
  const px = (time) => x0 + (time / duration) * w;
  const py = (value) => y0 + (1 - value) * h;
  for (let i = 0; i <= 4; i += 1) {
    const y = py(i / 4);
    grid.appendChild(svgElement("line", { x1:x0, y1:y, x2:x0+w, y2:y, class:"gridline" }));
    grid.appendChild(svgElement("text", { x:47, y:y+4, "text-anchor":"end" }, (i / 4).toFixed(2)));
    const x = x0 + (i / 4) * w;
    grid.appendChild(svgElement("line", { x1:x, y1:y0, x2:x, y2:y0+h, class:"gridline" }));
    grid.appendChild(svgElement("text", { x, y:305, "text-anchor":"middle" }, (duration * i / 4).toPrecision(3)));
  }
  grid.appendChild(svgElement("line", { x1:x0, y1:y0+h, x2:x0+w, y2:y0+h, class:"axis" }));
  grid.appendChild(svgElement("text", { x:x0+w/2, y:333, "text-anchor":"middle" }, "Time"));
  for (const [id, key] of [
    ["series-pop", "p_excited"],
    ["series-coh", "coherence_abs"],
    ["series-purity", "purity"]
  ]) {
    const d = samples.map((sample, i) => {
      return (i === 0 ? "M" : "L") + px(sample.time).toFixed(3) + "," + py(sample[key]).toFixed(3);
    }).join(" ");
    byId(id).setAttribute("d", d);
  }
}

function setMessage(id, text, error = false) {
  const element = byId(id);
  element.textContent = text;
  element.classList.toggle("error", error);
}

function calculate() {
  try {
    const params = {
      t1:readNumber("t1"), t2:readNumber("t2"),
      duration:readNumber("duration"), steps:readNumber("steps"),
      theta:readNumber("theta"), phi:readNumber("phi"), omega:readNumber("omega")
    };
    latestSamples = simulate(params);
    draw(latestSamples, params.duration);
    const end = latestSamples[latestSamples.length - 1];
    byId("final-pop").textContent = end.p_excited.toFixed(5);
    byId("final-coh").textContent = end.coherence_abs.toFixed(5);
    byId("final-purity").textContent = end.purity.toFixed(5);
    byId("export-csv").disabled = false;
    const gamma = Math.max(0, 1 / params.t2 - 1 / (2 * params.t1));
    setMessage("sim-message", "Computed " + latestSamples.length + " samples locally. Pure-dephasing rate γφ = " + gamma.toPrecision(5) + ".");
  } catch (err) {
    latestSamples = null;
    byId("export-csv").disabled = true;
    setMessage("sim-message", err.message, true);
  }
}

function downloadCSV() {
  if (!latestSamples) return;
  const fields = ["time","p_excited","coherence_abs","purity","x","y","z"];
  const csv = [fields.join(",")].concat(latestSamples.map(sample =>
    fields.map(name => sample[name].toPrecision(16)).join(",")
  )).join("\r\n") + "\r\n";
  const url = URL.createObjectURL(new Blob([csv], { type:"text/csv;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = "qubit-decoherence.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function runAudit() {
  const submit = byId("audit-form").querySelector('button[type="submit"]');
  submit.disabled = true;
  setMessage("audit-message", "Submitting to same-origin FastAPI server…");
  try {
    const payload = {
      task_id:byId("task_id").value,
      target_identifier:byId("target_id").value,
      primary_metric:readNumber("primary_metric"),
      secondary_metric:readNumber("secondary_metric"),
      status_descriptor:byId("status_descriptor").value,
      is_critical_flag:byId("is_critical").checked
    };
    if (location.hostname.endsWith(".github.io")) {
      throw new Error("Static GitHub Pages does not run the audit API. Use the local FastAPI server.");
    }
    const response = await fetch("/api/audit", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(payload)
    });
    if (!response.ok) {
      let detail = "HTTP " + response.status;
      try {
        const body = await response.json();
        if (typeof body.detail === "string") detail += ": " + body.detail;
      } catch (_) { /* Server may return non-JSON on failure. */ }
      throw new Error(detail);
    }
    const result = await response.json();
    byId("audit-result").textContent = JSON.stringify(result, null, 2);
    setMessage("audit-message", "Audit completed by the connected server.");
  } catch (err) {
    byId("audit-result").textContent = "No verified audit result. " + err.message;
    setMessage("audit-message", err.message, true);
  } finally {
    submit.disabled = false;
  }
}

if (typeof document !== "undefined") {
  byId("sim-form").addEventListener("submit", event => {
    event.preventDefault();
    calculate();
  });
  byId("audit-form").addEventListener("submit", event => {
    event.preventDefault();
    void runAudit();
  });
  byId("export-csv").addEventListener("click", downloadCSV);
  calculate();
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { simulate };
}
