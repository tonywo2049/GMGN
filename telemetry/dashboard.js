"use strict";

const elements = {
  serviceState: document.querySelector("#service-state"),
  serviceStateText: document.querySelector("#service-state-text"),
  refreshButton: document.querySelector("#refresh-button"),
  sessionCount: document.querySelector("#session-count"),
  sessionForm: document.querySelector("#session-form"),
  sessionInput: document.querySelector("#session-input"),
  sessionSearch: document.querySelector("#session-search"),
  showSubagents: document.querySelector("#show-subagents"),
  sessionList: document.querySelector("#session-list"),
  emptyState: document.querySelector("#empty-state"),
  loadingState: document.querySelector("#loading-state"),
  errorState: document.querySelector("#error-state"),
  errorMessage: document.querySelector("#error-message"),
  dashboard: document.querySelector("#dashboard"),
  reportSource: document.querySelector("#report-source"),
  reportTitle: document.querySelector("#report-title"),
  reportSessionId: document.querySelector("#report-session-id"),
  includeDescendants: document.querySelector("#include-descendants"),
  generatedAt: document.querySelector("#generated-at"),
  metricGrid: document.querySelector("#metric-grid"),
  tokenChart: document.querySelector("#token-chart"),
  sourceList: document.querySelector("#source-list"),
  gmgnMetrics: document.querySelector("#gmgn-metrics"),
  docstarMetrics: document.querySelector("#docstar-metrics"),
  docstarNote: document.querySelector("#docstar-note"),
  toolBars: document.querySelector("#tool-bars"),
  toolSummaryBody: document.querySelector("#tool-summary-body"),
  skillBody: document.querySelector("#skill-body"),
  recentToolBody: document.querySelector("#recent-tool-body"),
  qualityStrip: document.querySelector("#quality-strip"),
};

const state = {
  sessions: [],
  selectedSessionId: null,
  reportController: null,
};

function createElement(tagName, className, text) {
  const element = document.createElement(tagName);
  if (className) {
    element.className = className;
  }
  if (text !== undefined && text !== null) {
    element.textContent = String(text);
  }
  return element;
}

function formatNumber(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "未知";
  }
  return new Intl.NumberFormat("zh-CN", { notation: "compact", maximumFractionDigits: 1 }).format(Number(value));
}

function formatExactNumber(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "未知";
  }
  return new Intl.NumberFormat("zh-CN").format(Number(value));
}

function formatDuration(milliseconds) {
  if (milliseconds === null || milliseconds === undefined || Number.isNaN(Number(milliseconds))) {
    return "未知";
  }
  const value = Number(milliseconds);
  if (value < 1000) {
    return `${Math.round(value)} ms`;
  }
  if (value < 60000) {
    return `${(value / 1000).toFixed(value < 10000 ? 1 : 0)} 秒`;
  }
  if (value < 3600000) {
    return `${(value / 60000).toFixed(1)} 分钟`;
  }
  return `${(value / 3600000).toFixed(1)} 小时`;
}

function formatTimestamp(value, includeDate = true) {
  if (!value) {
    return "时间未知";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return String(value);
  }
  const options = includeDate
    ? { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit" }
    : { hour: "2-digit", minute: "2-digit", second: "2-digit" };
  return new Intl.DateTimeFormat("zh-CN", options).format(parsed);
}

function shortSessionId(sessionId) {
  if (!sessionId) {
    return "未知任务";
  }
  if (sessionId.length <= 18) {
    return sessionId;
  }
  return `${sessionId.slice(0, 8)}…${sessionId.slice(-6)}`;
}

function setServiceState(mode, text) {
  elements.serviceState.classList.remove("online", "offline");
  if (mode) {
    elements.serviceState.classList.add(mode);
  }
  elements.serviceStateText.textContent = text;
}

function setView(view, message) {
  elements.emptyState.hidden = view !== "empty";
  elements.loadingState.hidden = view !== "loading";
  elements.errorState.hidden = view !== "error";
  elements.dashboard.hidden = view !== "dashboard";
  if (view === "error") {
    elements.errorMessage.textContent = message || "请稍后重试。";
  }
}

async function fetchJson(path, options = {}) {
  const response = await fetch(path, {
    cache: "no-store",
    headers: { Accept: "application/json" },
    ...options,
  });
  if (!response.ok) {
    const error = new Error(`HTTP ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return response.json();
}

function filteredSessions() {
  const query = elements.sessionSearch.value.trim().toLocaleLowerCase();
  return state.sessions.filter((session) => {
    if (!elements.showSubagents.checked && session.is_subagent === true) {
      return false;
    }
    if (!query) {
      return true;
    }
    return [session.session_id, session.model, session.source]
      .filter(Boolean)
      .some((value) => String(value).toLocaleLowerCase().includes(query));
  });
}

function renderSessionList() {
  const sessions = filteredSessions();
  elements.sessionList.replaceChildren();
  elements.sessionCount.textContent = formatExactNumber(sessions.length);
  if (!sessions.length) {
    elements.sessionList.append(createElement("p", "session-empty", "没有匹配的任务。可以直接输入 Session ID。"));
    return;
  }
  const fragment = document.createDocumentFragment();
  sessions.forEach((session) => {
    const button = createElement("button", "session-item");
    button.type = "button";
    button.title = session.session_id;
    if (session.session_id === state.selectedSessionId) {
      button.classList.add("selected");
    }
    const top = createElement("span", "session-item-top");
    top.append(createElement("strong", "", shortSessionId(session.session_id)));
    top.append(createElement("span", "session-kind", session.is_subagent === true ? "Subagent" : "Main"));
    const metadata = createElement("span", "session-meta");
    metadata.append(createElement("span", "", session.model || "model unknown"));
    metadata.append(createElement("span", "", formatTimestamp(session.last_seen)));
    button.append(top, metadata);
    button.addEventListener("click", () => selectSession(session.session_id));
    fragment.append(button);
  });
  elements.sessionList.append(fragment);
}

async function loadSessions({ keepSelection = true } = {}) {
  try {
    const document = await fetchJson("/api/sessions");
    state.sessions = Array.isArray(document.sessions) ? document.sessions : [];
    setServiceState("online", "Collector 正常");
    renderSessionList();
    if (!keepSelection || !state.selectedSessionId) {
      const requested = new URL(window.location.href).searchParams.get("session");
      const initial = requested || state.sessions.find((session) => session.is_subagent !== true)?.session_id || state.sessions[0]?.session_id;
      if (initial) {
        await selectSession(initial);
      }
    }
  } catch (error) {
    setServiceState("offline", "Collector 不可用");
    if (!state.selectedSessionId) {
      setView("error", "无法读取本机会话索引，请确认 Collector 正在运行。");
    }
  }
}

async function selectSession(sessionId) {
  const normalized = String(sessionId || "").trim();
  if (!normalized) {
    return;
  }
  state.selectedSessionId = normalized;
  elements.sessionInput.value = normalized;
  renderSessionList();
  const url = new URL(window.location.href);
  url.searchParams.set("session", normalized);
  window.history.replaceState({}, "", url);
  await loadReport();
}

async function loadReport() {
  if (!state.selectedSessionId) {
    setView("empty");
    return;
  }
  if (state.reportController) {
    state.reportController.abort();
  }
  const controller = new AbortController();
  state.reportController = controller;
  setView("loading");
  const parameters = new URLSearchParams({
    session_id: state.selectedSessionId,
    descendants: elements.includeDescendants.checked ? "true" : "false",
  });
  try {
    const document = await fetchJson(`/api/report?${parameters}`, { signal: controller.signal });
    if (controller.signal.aborted) {
      return;
    }
    renderReport(document);
    setView("dashboard");
  } catch (error) {
    if (error.name === "AbortError") {
      return;
    }
    const message = error.status === 503
      ? "另一个报告正在生成，请稍后刷新。"
      : error.status === 400
        ? "Session ID 无效或报告参数不正确。"
        : "无法生成报告，请确认 Session 数据仍在保留期内。";
    setView("error", message);
  } finally {
    if (state.reportController === controller) {
      state.reportController = null;
    }
  }
}

function metricCard(label, value, note) {
  const card = createElement("div", "metric-card");
  card.append(
    createElement("span", "metric-card-label", label),
    createElement("strong", "metric-card-value", value),
    createElement("span", "metric-card-note", note),
  );
  return card;
}

function renderMetrics(run) {
  const timing = run.timing || {};
  const tokens = run.actual_tokens || {};
  const sessions = run.session_counts || {};
  const api = run.api_calls || {};
  elements.metricGrid.replaceChildren(
    metricCard("墙钟时长", formatDuration(timing.main_wall_elapsed_ms), `完成 turn ${formatDuration(timing.completed_turn_duration_ms)}`),
    metricCard("实际 Token", formatNumber(tokens.total), `输入 ${formatNumber(tokens.input)} · 输出 ${formatNumber(tokens.output)}`),
    metricCard("工具调用", formatExactNumber(run.tool_call_count), `Native ${formatExactNumber((run.native_tool_results || {}).count)}`),
    metricCard("Skill 调用", formatExactNumber(run.skill_call_count), `上下文 Token 为估算值`),
    metricCard("会话数量", formatExactNumber(sessions.total), `主 ${formatExactNumber(sessions.main)} · 子 ${formatExactNumber(sessions.descendants)} · API ${formatExactNumber(api.count)}`),
  );
}

function renderTokenChart(tokens) {
  const definitions = [
    ["Input", tokens.input, "#185c45"],
    ["Cached", tokens.cached, "#2a8a65"],
    ["Output", tokens.output, "#b96b2c"],
    ["Reasoning", tokens.reasoning, "#17324a"],
  ];
  const maximum = Math.max(1, ...definitions.map((definition) => Number(definition[1]) || 0));
  const fragment = document.createDocumentFragment();
  definitions.forEach(([label, value, color]) => {
    const row = createElement("div", "bar-row");
    const track = createElement("div", "bar-track");
    const fill = createElement("div", "bar-fill");
    const width = value === null || value === undefined ? 0 : Math.max(1, (Number(value) / maximum) * 100);
    fill.style.setProperty("--bar-width", `${width}%`);
    fill.style.setProperty("--bar-color", color);
    track.append(fill);
    row.append(
      createElement("span", "bar-label", label),
      track,
      createElement("span", "bar-value", formatExactNumber(value)),
    );
    fragment.append(row);
  });
  elements.tokenChart.replaceChildren(fragment);
}

function coverageLabel(details) {
  const coverage = details?.coverage || "unknown";
  const source = details?.source || "unknown";
  return { coverage, source };
}

function renderSources(run) {
  const definitions = [
    ["实际 Token", run.coverage?.actual_tokens],
    ["工具调用", run.coverage?.tool_calls],
    ["GMGN", run.coverage?.gmgn],
    ["DocStar", run.coverage?.docstar],
    ["Skills", run.coverage?.skills],
  ];
  const fragment = document.createDocumentFragment();
  definitions.forEach(([label, details]) => {
    const normalized = coverageLabel(details);
    const item = createElement("div", "source-item");
    const name = createElement("div", "source-name");
    name.append(createElement("strong", "", label), createElement("span", "", normalized.source));
    const chip = createElement("span", `coverage-chip ${normalized.coverage}`, normalized.coverage);
    item.append(name, chip);
    fragment.append(item);
  });
  elements.sourceList.replaceChildren(fragment);
}

function miniMetric(label, value) {
  const metric = createElement("div", "mini-metric");
  metric.append(createElement("span", "", label), createElement("strong", "", value));
  return metric;
}

function renderGmgn(gmgn) {
  elements.gmgnMetrics.replaceChildren(
    miniMetric("Spawn", formatExactNumber(gmgn.spawn_calls)),
    miniMetric("Wait", formatExactNumber(gmgn.wait_calls)),
    miniMetric("Wait time", formatDuration(gmgn.wait_duration_ms)),
    miniMetric("Send", formatExactNumber(gmgn.send_calls)),
  );
}

function renderDocstar(docstar, followWindow) {
  const hasObservedCalls = docstar.calls !== null && docstar.calls !== undefined;
  const followUp = hasObservedCalls && Array.isArray(docstar.follow_up)
    ? docstar.follow_up.reduce((total, item) => total + (Number(item.grep_read_calls) || 0), 0)
    : null;
  elements.docstarMetrics.replaceChildren(
    miniMetric("Calls", formatExactNumber(docstar.calls)),
    miniMetric("Grep / Read", formatExactNumber(docstar.grep_read_calls)),
    miniMetric("Follow-up", formatExactNumber(followUp)),
    miniMetric("Window", formatExactNumber(followWindow)),
  );
  elements.docstarNote.textContent = docstar.causal_status === "causal_not_measured"
    ? "关联已观测；未把相关性解释为因果节省。"
    : String(docstar.causal_status || "因果状态未知");
}

function renderToolSummary(summary) {
  const tools = Array.isArray(summary) ? summary : [];
  const maximum = Math.max(1, ...tools.map((item) => Number(item.calls) || 0));
  const bars = document.createDocumentFragment();
  tools.slice(0, 10).forEach((item) => {
    const row = createElement("div", "tool-bar-row");
    const track = createElement("div", "bar-track");
    const fill = createElement("div", "bar-fill");
    fill.style.setProperty("--bar-width", `${Math.max(1, (Number(item.calls) / maximum) * 100)}%`);
    track.append(fill);
    row.append(
      createElement("span", "tool-bar-name", item.tool),
      track,
      createElement("span", "tool-bar-count", formatExactNumber(item.calls)),
    );
    bars.append(row);
  });
  elements.toolBars.replaceChildren(bars);

  elements.toolSummaryBody.replaceChildren();
  if (!tools.length) {
    appendEmptyRow(elements.toolSummaryBody, 6, "没有可用的工具调用数据");
    return;
  }
  const rows = document.createDocumentFragment();
  tools.forEach((item) => {
    const row = document.createElement("tr");
    const tokenTotal = item.estimated_input_tokens === null || item.estimated_output_tokens === null
      ? null
      : Number(item.estimated_input_tokens) + Number(item.estimated_output_tokens);
    row.append(
      tableCell(item.tool),
      chipCell(item.category, "category-chip"),
      tableCell(formatExactNumber(item.calls)),
      tableCell(formatDuration(item.duration_ms)),
      tableCell(formatDuration(item.average_duration_ms)),
      tableCell(formatExactNumber(tokenTotal)),
    );
    rows.append(row);
  });
  elements.toolSummaryBody.append(rows);
}

function tableCell(value) {
  return createElement("td", "", value);
}

function chipCell(value, className) {
  const cell = document.createElement("td");
  cell.append(createElement("span", className, value || "unknown"));
  return cell;
}

function appendEmptyRow(target, columns, message) {
  const row = document.createElement("tr");
  const cell = createElement("td", "empty-table", message);
  cell.colSpan = columns;
  row.append(cell);
  target.append(row);
}

function renderSkills(skills) {
  const entries = Array.isArray(skills) ? skills : [];
  elements.skillBody.replaceChildren();
  if (!entries.length) {
    appendEmptyRow(elements.skillBody, 5, "没有观测到 Skill 调用");
    return;
  }
  const fragment = document.createDocumentFragment();
  entries.forEach((skill) => {
    const row = document.createElement("tr");
    row.append(
      tableCell(skill.skill || "unknown"),
      tableCell(formatDuration(skill.load_duration_ms)),
      tableCell(formatDuration(skill.observed_span_ms)),
      tableCell(formatExactNumber(skill.estimated_context_tokens)),
      chipCell(skill.linkage || "unknown", "category-chip"),
    );
    fragment.append(row);
  });
  elements.skillBody.append(fragment);
}

function renderRecentTools(calls) {
  const entries = Array.isArray(calls) ? calls : [];
  elements.recentToolBody.replaceChildren();
  if (!entries.length) {
    appendEmptyRow(elements.recentToolBody, 6, "没有最近工具调用");
    return;
  }
  const fragment = document.createDocumentFragment();
  entries.forEach((call) => {
    const row = document.createElement("tr");
    const status = call.success === true ? "成功" : call.success === false ? "失败" : "未知";
    const statusClass = call.success === true ? "success" : call.success === false ? "failure" : "";
    const tokenTotal = call.estimated_input_tokens === null || call.estimated_output_tokens === null
      ? null
      : Number(call.estimated_input_tokens) + Number(call.estimated_output_tokens);
    row.append(
      tableCell(formatTimestamp(call.start, false)),
      tableCell(call.tool || "unknown"),
      chipCell(call.category || "other", "category-chip"),
      tableCell(formatDuration(call.duration_ms)),
      chipCell(status, `status-chip ${statusClass}`),
      tableCell(formatExactNumber(tokenTotal)),
    );
    fragment.append(row);
  });
  elements.recentToolBody.append(fragment);
}

function renderQuality(run) {
  const quality = run.data_quality || {};
  const fallback = run.sources?.session_jsonl_unstable_fallback;
  const items = [
    `数据源 ${run.source || "unknown"}`,
    `Malformed ${formatExactNumber(quality.malformed_lines)}`,
    `Telemetry malformed ${formatExactNumber(quality.malformed_telemetry_lines)}`,
    `Unpaired ${formatExactNumber(quality.unpaired_calls)}`,
    `Missing ${formatExactNumber(Array.isArray(quality.missing_sessions) ? quality.missing_sessions.length : null)}`,
    `Fallback ${fallback?.used ? "used" : "not used"}`,
  ];
  elements.qualityStrip.replaceChildren(...items.map((item) => createElement("span", "", item)));
}

function renderReport(document) {
  const run = document.run || {};
  elements.reportSource.textContent = run.source || "Telemetry report";
  elements.reportTitle.textContent = run.session_id ? "任务报告" : "未找到任务";
  elements.reportSessionId.textContent = run.session_id || run.requested_id || state.selectedSessionId;
  elements.generatedAt.textContent = `生成于 ${formatTimestamp(document.generated_at)}`;
  renderMetrics(run);
  renderTokenChart(run.actual_tokens || {});
  renderSources(run);
  renderGmgn(run.gmgn || {});
  renderDocstar(run.docstar || {}, document.configuration?.follow_window);
  renderToolSummary(run.tool_summary || []);
  renderSkills(run.skills || []);
  renderRecentTools(run.recent_tool_calls || []);
  renderQuality(run);
}

elements.sessionForm.addEventListener("submit", (event) => {
  event.preventDefault();
  selectSession(elements.sessionInput.value);
});

elements.sessionSearch.addEventListener("input", renderSessionList);
elements.showSubagents.addEventListener("change", renderSessionList);
elements.includeDescendants.addEventListener("change", loadReport);
elements.refreshButton.addEventListener("click", async () => {
  elements.refreshButton.disabled = true;
  try {
    await loadSessions({ keepSelection: true });
    if (state.selectedSessionId) {
      await loadReport();
    }
  } finally {
    elements.refreshButton.disabled = false;
  }
});

loadSessions({ keepSelection: false });
