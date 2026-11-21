"use strict";

const $ = id => document.getElementById(id);
const put = (id, text) => { $(id).textContent = text; };
const study = JSON.parse($("study-data").textContent);
const cycles = study.cycles;
const post = row => row.post_discharge;
for (const row of cycles) {
  for (const stage of ["post_discharge", "end_of_charge"]) {
    if (row[stage]) row[stage].packet = JSON.parse(row[stage].packetText);
  }
}

const colors = {
  grid: "#e0e5f0", text: "#505b72", border: "#c6cee1", accepted: "#09756d",
  raw: "#3548ca", forecast: "#754cc1", upper: "#ad681a", selection: "#edf0ff",
};
const accepted = row => post(row).event.action === "update";
const number = (value, digits = 3) => Number.isFinite(value) ? value.toFixed(digits) : null;
const amount = (value, digits = 3) => number(value, digits) ?? "Unavailable";
const stageName = stage => stage === "post_discharge" ? "Post-discharge" : "End of charge";
const actionName = { update: "Accepted", update_with_warning: "Qualified", reject: "Rejected" };
const checkName = {
  metadata_completeness: "Metadata",
  protocol_comparability: "Comparability",
  fit_convergence: "Fit convergence",
  fitted_snr: "Fitted SNR",
  peak_position: "Peak position",
  baseline_residual_lag1: "Residual structure",
  reference_fit: "Reference fit",
};
const last = items => items.at(-1);

const stops = [
  {
    row: cycles.find(row => post(row).packet.detection_class === "censored"),
    title: "When the signal is unresolved",
    text: "A non-detection gives an upper limit. The twin waits for a reliable quantitative observation.",
  },
  {
    row: cycles.find(accepted),
    title: "Establish a baseline",
    text: "A detected peak and a usable reference give the twin its first quantitative post-discharge signal ratio.",
  },
  {
    row: cycles.find(row => post(row).packet.qc_status === "FAIL"),
    title: "Put the quality gate to work",
    text: "This spectrum is in the audit trail. The acquisition failed a quality check, so the prior accepted state holds.",
  },
  {
    row: cycles.findLast(row => post(row).event.comparison === "deteriorating"),
    title: "Update the twin and ask what comes next",
    text: "Here the increase exceeds the uncertainty and model-sensitivity guard. Use the next-cycle forecast to plan a confirmatory measurement.",
  },
].filter(stop => stop.row);

let selected = last(cycles);
let mode = "explore";
let guideIndex = 0;
let stage = "post_discharge";
let region = "metal";
let panel = "spectrum";
let trajectoryScale = null;

function list(id, entries) {
  const root = $(id);
  root.replaceChildren(...entries.map(([label, result]) => {
    const line = document.createElement("div");
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = label;
    dd.textContent = result;
    line.append(dt, dd);
    return line;
  }));
}

function updateNavigation() {
  put("chart-selection", "Cycle " + selected.cycle);
  $("cycle-select").value = selected.cycle;
  for (const button of $("cycle-buttons").children) {
    button.setAttribute("aria-pressed", String(Number(button.dataset.cycle) === selected.cycle));
  }
  $("guide-panel").hidden = mode !== "guide";
  $("guide").setAttribute("aria-pressed", String(mode === "guide"));
  $("explore").setAttribute("aria-pressed", String(mode === "explore"));
  if (mode === "guide") {
    put("guide-progress", "Step " + (guideIndex + 1) + " of " + stops.length);
    put("guide-title", stops[guideIndex].title);
    put("guide-text", stops[guideIndex].text);
    $("guide-back").disabled = guideIndex === 0;
    put("guide-next", guideIndex === stops.length - 1 ? "Explore cycles" : "Next step");
  }
}

function showCycle(row, fromGuide = false) {
  if (!row) return;
  selected = row;
  if (!fromGuide) mode = "explore";
  render();
}

function selectStage(nextStage) {
  stage = nextStage;
  if (!selected[stage].reference) region = "metal";
  updateEvidence();
}

function updateDecision() {
  const { packet, event } = post(selected);
  const prior = last(cycles.filter(row => row.cycle < selected.cycle && accepted(row)));
  const current = accepted(selected) ? selected : prior;
  const forecast = event.forecast_issued;
  const badge = $("decision-badge");
  badge.textContent = actionName[event.action];
  badge.className = "badge " + ({ update: "pass", update_with_warning: "warn", reject: "fail" })[event.action];

  put("accepted-value", current ? amount(post(current).packet.value) : "—");
  put("accepted-detail", current
    ? "± " + amount(post(current).packet.uncertainty.value) + " fit SD · Cycle " + current.cycle
    : "Awaiting a reliable post-discharge observation");
  put("prior-value", prior ? amount(post(prior).packet.value) + " · Cycle " + prior.cycle : "No prior accepted value");
  const { detection_class: detection, value, upper_limit: limit, uncertainty } = packet;
  const observed = Number.isFinite(value) ? amount(value) + " ± " + amount(uncertainty.value)
    : Number.isFinite(limit) ? "Upper limit " + amount(limit, 4) : "No quantitative RMDI";
  put("observation-value", observed);
  let headline = event.reason;
  let action = actionName[event.action] + " · " + packet.qc_status + " QC";
  if (event.comparison === "deteriorating") {
    headline = "Accumulation warning. The increase exceeds the change threshold.";
    action = "+" + amount(event.change.delta) + " vs " + amount(event.change.significance_threshold) + " threshold";
  } else if (event.comparison === "stable") {
    headline = "Stable within the configured measurement resolution.";
  } else if (event.action === "reject") {
    headline = "QC failed. The accepted estimate is unchanged.";
  } else if (detection === "censored") {
    headline = "Signal unresolved. The record retains the upper limit.";
  } else if (detection === "uncertain") {
    headline = "Peak evidence is ambiguous. The accepted estimate is unchanged.";
  }
  put("decision-summary", headline);
  put("action-value", action);
  put("forecast-value", forecast?.estimate != null
    ? amount(forecast.estimate) + " [" + amount(forecast.lower, 2) + ", " + amount(forecast.upper, 2) + "]"
    : forecast?.reason ? "Insufficient reliable observations" : "No new forecast");
  put("next-evidence", event.next_evidence);
  const priorForecast = event.forecast_comparison;
  put("chart-description",
    "Selected cycle " + selected.cycle + ". " + observed + ". " + headline
    + (priorForecast ? " The reading " + (priorForecast.within_interval ? "falls within" : "falls outside") + " its previously issued prediction interval." : ""));
}

function updateEvidence() {
  const evidence = selected[stage];
  const { packet } = evidence;
  $("stage-select").value = stage;
  $("region-select").value = region;
  $("region-select").options[1].disabled = !evidence.reference;
  put("evidence-context", "Cycle " + selected.cycle + " · " + stageName(stage) + " · " + packet.origin);
  const fit = evidence[region];
  list("fit-metrics", [
    ["Fit center", fit.center == null ? "Unavailable" : amount(fit.center, 1) + " ± " + amount(fit.center_sd, 1) + " ppm"],
    ["Gaussian σ", fit.parameters ? amount(fit.parameters[2], 1) + " ppm" : "Unavailable"],
    ["Full-line area", fit.area == null ? "Unavailable" : amount(fit.area, 2) + " ± " + amount(fit.area_sd, 2) + " a.u.·ppm"],
    ["Fitted SNR", amount(fit.snr, 1)],
    ["Line-shape area shift", fit.shape_shift == null ? "Unavailable" : amount(fit.shape_shift, 2) + " a.u.·ppm"],
    ["Window area shift", fit.window_shift == null ? "Unavailable" : amount(fit.window_shift, 2) + " a.u.·ppm"],
  ]);
  put("fit-note", stage === "end_of_charge"
    ? "End-of-charge spectra provide context. The twin uses post-discharge evidence for RMDI."
    : "Fit diagnostics describe the selected spectral region. The cycle-level decision also uses comparability and acquisition QC.");

  $("qc-rows").replaceChildren(...packet.qc_checks.map(check => {
    const tr = document.createElement("tr");
    const title = tr.insertCell();
    title.textContent = checkName[check.name] ?? check.name.replaceAll("_", " ");
    title.title = check.threshold + " · " + check.owner;
    const observed = tr.insertCell();
    const val = check.value;
    observed.textContent = typeof val === "number" ? amount(val, 2) + (check.unit === "1" ? "" : " " + check.unit)
      : typeof val === "boolean" ? (val ? "Yes" : "No") : val ?? "Unavailable";
    const label = document.createElement("span");
    label.className = "badge " + check.status.toLowerCase();
    label.textContent = check.status;
    tr.insertCell().append(label);
    return tr;
  }));
  const acq = packet.acquisition_context;
  const conditions = packet.cell_conditions;
  const entries = [
    ["Origin", packet.origin],
    ["Acquisition", acq.sequence ? acq.sequence.replaceAll("_", " ") + " · " + acq.averages + " averages" : "Sequence metadata missing"],
    ["Conditions", conditions.temperature_C + " °C · " + conditions.charge_current_mA + " mA charge"],
    ["Reference", acq.spectral_reference ?? "Unavailable"],
    ["Fit SD", typeof packet.uncertainty.value === "number" ? amount(packet.uncertainty.value) + " " + packet.unit : "Unavailable"],
    ["Model sensitivity", packet.model_sensitivity == null ? "Unavailable" : amount(packet.model_sensitivity) + " " + packet.unit],
    ["Config / pipeline", packet.processing.config_version + " / " + packet.processing.version],
  ];
  if (packet.upper_limit_method) entries.push(["Upper-limit method", packet.upper_limit_method]);
  if (evidence.event.forecast_comparison) entries.push(["Earlier forecast check",
    evidence.event.forecast_comparison.within_interval ? "Observation within interval" : "Observation outside interval"]);
  list("trust-metrics", entries);
  const pathName = path => path.split("/").at(-1);
  $("trace-list").replaceChildren(...[
    ["Source spectrum", pathName(packet.source_object), packet.source_sha256],
    ...packet.provenance.activities.map(item => [item.step, pathName(item.artifact.path), item.artifact.sha256]),
    ["Evidence packet and twin event", packet.packet_id, evidence.event.packet_sha256],
  ].map(([label, file, digest]) => {
    const line = document.createElement("li");
    line.textContent = label + " · " + file;
    const code = document.createElement("code");
    code.textContent = digest;
    line.append(code);
    return line;
  }));
  drawSpectrum();
}

function drawTarget(canvasId) {
  const canvas = $(canvasId);
  const { width, height } = canvas.getBoundingClientRect();
  if (width < 1 || height < 1) return null;
  const ratio = Math.min(window.devicePixelRatio || 1, 3);
  canvas.width = Math.round(width * ratio);
  canvas.height = Math.round(height * ratio);
  const ctx = canvas.getContext("2d");
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  ctx.font = "12px system-ui, sans-serif";
  ctx.lineJoin = "round";
  ctx.lineCap = "round";
  return { ctx, width, height };
}

function path(ctx, points, color, width = 1, dash = []) {
  if (points.length < 2) return;
  ctx.beginPath();
  ctx.moveTo(...points[0]);
  for (const point of points.slice(1)) ctx.lineTo(...point);
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.setLineDash(dash);
  ctx.stroke();
  ctx.setLineDash([]);
}

function dot(ctx, x, y, radius, fill, stroke = null) {
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, 2 * Math.PI);
  ctx.fillStyle = fill;
  ctx.fill();
  if (stroke) {
    ctx.strokeStyle = stroke;
    ctx.lineWidth = 1.4;
    ctx.stroke();
  }
}

function grid(target, xDomain, yDomain, xTicks, yTicks, xText, yText, top = 12) {
  const { ctx, width, height } = target;
  const box = { left: 44, right: width - 24, top, bottom: height - 30 };
  const x = value => box.left + (value - xDomain[0]) / (xDomain[1] - xDomain[0]) * (box.right - box.left);
  const y = value => box.bottom - (value - yDomain[0]) / (yDomain[1] - yDomain[0]) * (box.bottom - box.top);
  ctx.fillStyle = colors.text;
  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  for (const tick of yTicks) {
    const at = y(tick);
    path(ctx, [[box.left, at], [box.right, at]], colors.grid);
    ctx.fillText(yText(tick), box.left - 8, at);
  }
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  for (const tick of xTicks) ctx.fillText(xText(tick), x(tick), box.bottom + 9);
  path(ctx, [[box.left, box.top], [box.left, box.bottom], [box.right, box.bottom]], colors.border);
  return { x, y, box, cycleAt: pixel => xDomain[0] + (pixel - box.left) / (box.right - box.left) * (xDomain[1] - xDomain[0]) };
}

function errorBar(ctx, x, bottom, top, color) {
  path(ctx, [[x, bottom], [x, top]], color, 1.5);
  path(ctx, [[x - 4, top], [x + 4, top]], color, 1.5);
  path(ctx, [[x - 4, bottom], [x + 4, bottom]], color, 1.5);
}

function drawTrajectory() {
  const target = drawTarget("trajectory-plot");
  if (!target) return;
  const { ctx, width } = target;
  const shown = mode === "guide" ? cycles.filter(row => row.cycle <= selected.cycle) : cycles;
  const future = post(selected).event.forecast_issued;
  const forecast = future?.estimate != null ? future : null;
  const maxCycle = mode === "guide" ? Math.max(4, selected.cycle + 1) : last(cycles).cycle + 1;
  const highest = Math.max(.12, forecast?.upper ?? 0, ...shown.map(row => {
    const packet = post(row).packet;
    return accepted(row) ? packet.value + packet.uncertainty.value : packet.upper_limit ?? 0;
  }));
  const range = forecast?.lower < 0 ? highest - forecast.lower : highest;
  const scale = 10 ** Math.floor(Math.log10(range / 4));
  const step = [1, 2, 2.5, 5, 10].map(n => n * scale).find(n => n >= range / 4);
  const low = step * Math.floor(Math.min(0, forecast?.lower ?? 0) / step);
  const high = step * Math.ceil(highest * 1.06 / step);
  const yTicks = Array.from({ length: Math.round((high - low) / step) + 1 }, (_, index) => low + index * step);
  const labelStep = width < 500 && maxCycle > 8 ? 2 : 1;
  const xTicks = Array.from({ length: Math.ceil(maxCycle / labelStep) }, (_, index) => 1 + index * labelStep);
  const xDomain = [.65, maxCycle + .35];
  const { x, y, box, cycleAt } = grid(target, xDomain, [low, high], xTicks, yTicks, String,
    value => value.toFixed(step < .1 ? 2 : 1));
  trajectoryScale = { cycleAt, box };
  const band = Math.min(26, (x(2) - x(1)) * .55);
  ctx.fillStyle = colors.selection;
  ctx.fillRect(x(selected.cycle) - band / 2, box.top, band, box.bottom - box.top);
  path(ctx, [[x(selected.cycle), box.top], [x(selected.cycle), box.bottom]], "#b7c0fc", 1, [3, 5]);

  const observed = shown.filter(accepted);
  for (let i = 1; i < observed.length; i++) {
    const first = observed[i - 1];
    const second = observed[i];
    const dim = second.cycle > selected.cycle;
    path(ctx, [[x(first.cycle), y(post(first).packet.value)], [x(second.cycle), y(post(second).packet.value)]],
      dim ? "#c5d6dc" : colors.accepted, 2.1, second.cycle - first.cycle > 1 ? [4, 4] : []);
  }
  for (const row of observed) {
    const { value, uncertainty } = post(row).packet;
    const px = x(row.cycle);
    const py = y(value);
    const color = row.cycle > selected.cycle ? "#a1bdc5" : colors.accepted;
    errorBar(ctx, px, y(value - uncertainty.value), y(value + uncertainty.value), color);
    if (selected.cycle === row.cycle) dot(ctx, px, py, 8.5, "#fff", color);
    dot(ctx, px, py, 4.4, color);
  }
  for (const row of shown.filter(row => post(row).packet.upper_limit != null)) {
    const px = x(row.cycle);
    const py = y(post(row).packet.upper_limit);
    ctx.beginPath();
    ctx.moveTo(px - 5, py - 5);
    ctx.lineTo(px + 5, py - 5);
    ctx.lineTo(px, py + 3);
    ctx.closePath();
    ctx.fillStyle = colors.upper;
    ctx.fill();
  }
  if (forecast) {
    const px = x(forecast.target_cycle) + (forecast.target_cycle <= last(cycles).cycle ? 6 : 0);
    const py = y(forecast.estimate);
    path(ctx, [[x(selected.cycle), y(post(selected).packet.value)], [px, py]], colors.forecast, 1.6, [4, 4]);
    errorBar(ctx, px, y(forecast.lower), y(forecast.upper), colors.forecast);
    ctx.beginPath();
    ctx.moveTo(px, py - 6);
    ctx.lineTo(px + 6, py);
    ctx.lineTo(px, py + 6);
    ctx.lineTo(px - 6, py);
    ctx.closePath();
    ctx.fillStyle = "#fff";
    ctx.fill();
    ctx.strokeStyle = colors.forecast;
    ctx.lineWidth = 2;
    ctx.stroke();
  }
}

function drawSpectrum() {
  const target = drawTarget("spectrum-plot");
  const residualTarget = drawTarget("residual-plot");
  if (!target || !residualTarget) return;
  const spectrum = selected[stage][region];
  const { ppm, intensity, parameters, window: limits, residual, native_ppm: nativePpm } = spectrum;
  const model = parameters ? ppm.map(shift => {
    const [height, center, sigma, intercept, slope] = parameters;
    return height * Math.exp(-.5 * ((shift - center) / sigma) ** 2) + intercept + slope * (shift - (limits[0] + limits[1]) / 2);
  }) : [];
  const low = Math.min(...intensity, ...model);
  const high = Math.max(...intensity, ...model);
  const span = Math.max(high - low, .01);
  const ticks = [.0, .25, .5, .75, 1].map(fraction => limits[1] - (limits[1] - limits[0]) * fraction);
  const xDomain = [limits[1], limits[0]];
  const yDomain = [low - span * .1, high + span * .1];
  const lines = [.15, .45, .75].map(fraction => low + span * fraction);
  const main = grid(target, xDomain, yDomain, ticks, lines, tick => tick + " ppm", tick => tick.toFixed(2));
  path(target.ctx, ppm.map((shift, i) => [main.x(shift), main.y(intensity[i])]), colors.raw, 2);
  path(target.ctx, ppm.slice(0, model.length).map((shift, i) => [main.x(shift), main.y(model[i])]), colors.forecast, 1.8, [5, 3]);
  const maxResidual = Math.max(.03, ...residual.map(Math.abs)) * 1.12;
  const detail = grid(residualTarget, xDomain, [-maxResidual, maxResidual], [], [0], String, () => "0");
  residual.forEach((value, i) => dot(residualTarget.ctx, detail.x(nativePpm[i]), detail.y(value), 2.8, colors.accepted));
  residualTarget.ctx.fillStyle = colors.text;
  residualTarget.ctx.textAlign = "left";
  residualTarget.ctx.fillText("Residual · a.u.", detail.box.left, detail.box.bottom + 9);
}

function render() {
  updateNavigation();
  updateDecision();
  updateEvidence();
  drawTrajectory();
}

const tabIds = ["evidence-tab", "trust-tab"];
function selectTab(nextPanel) {
  panel = nextPanel;
  tabIds.forEach((id, index) => {
    const active = (index === 0) === (panel === "spectrum");
    $(id).setAttribute("aria-selected", String(active));
    $(id).tabIndex = active ? 0 : -1;
  });
  $("spectrum-panel").hidden = panel !== "spectrum";
  $("trust-panel").hidden = panel !== "trust";
  if (panel === "spectrum") drawSpectrum();
}

put("cell-id", study.cellId);
put("study-size", cycles.length + " cycles · ²³Na NMR");
put("config-version", "Config " + study.configVersion);
const intervalLevel = cycles.find(row => post(row).event.forecast_issued?.interval_level != null);
if (intervalLevel) {
  put("forecast-legend", "Forecast · " + Math.round(post(intervalLevel).event.forecast_issued.interval_level * 100) + "% interval");
}
for (const row of cycles) {
  const option = document.createElement("option");
  option.value = row.cycle;
  option.textContent = "Cycle " + row.cycle;
  $("cycle-select").append(option);
  const button = document.createElement("button");
  button.type = "button";
  button.dataset.cycle = row.cycle;
  button.textContent = row.cycle;
  button.setAttribute("aria-label", "Cycle " + row.cycle + " · " + actionName[post(row).event.action]);
  button.className = { update: "", update_with_warning: "qualified", reject: "rejected" }[post(row).event.action];
  button.addEventListener("click", () => showCycle(row));
  $("cycle-buttons").append(button);
}
$("guide").disabled = !stops.length;
$("guide").addEventListener("click", () => {
  mode = "guide";
  guideIndex = 0;
  selectStage("post_discharge");
  selectTab("spectrum");
  showCycle(stops[0].row, true);
});
$("explore").addEventListener("click", () => { mode = "explore"; render(); });
$("guide-back").addEventListener("click", () => showCycle(stops[--guideIndex].row, true));
$("guide-next").addEventListener("click", () => {
  if (guideIndex === stops.length - 1) {
    $("explore").click();
    $("explore").focus();
  } else {
    showCycle(stops[++guideIndex].row, true);
  }
});
$("cycle-select").addEventListener("change", event => showCycle(cycles.find(row => row.cycle === Number(event.target.value))));
$("stage-select").addEventListener("change", event => selectStage(event.target.value));
$("region-select").addEventListener("change", event => { region = event.target.value; updateEvidence(); });
$("trajectory-plot").addEventListener("click", event => {
  if (!trajectoryScale) return;
  const { box, cycleAt } = trajectoryScale;
  if (event.offsetX < box.left || event.offsetX > box.right) return;
  const cycle = Math.round(cycleAt(event.offsetX));
  showCycle(cycles.find(row => row.cycle === cycle));
});
tabIds.forEach((id, index) => {
  $(id).addEventListener("click", () => selectTab(index === 0 ? "spectrum" : "trust"));
  $(id).addEventListener("keydown", event => {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const next = event.key === "Home" ? 0 : event.key === "End" ? 1 : 1 - index;
    $(tabIds[next]).click();
    $(tabIds[next]).focus();
  });
});
$("download").addEventListener("click", () => {
  const evidence = selected[stage];
  const link = document.createElement("a");
  const url = URL.createObjectURL(new Blob([evidence.packetText], { type: "application/json" }));
  link.href = url;
  link.download = evidence.packet.packet_id + ".json";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
render();
const observer = new ResizeObserver(() => { drawTrajectory(); if (panel === "spectrum") drawSpectrum(); });
observer.observe($("trajectory-plot"));
observer.observe($("spectrum-plot"));
