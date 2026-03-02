const API_BASE = "http://127.0.0.1:8000";

const DATASET_ORDER = [
  "price_history", "pe", "dividend_yield", "dividend_history", "market_cap", "volume", "volume_avg", "volume_avg_10",
  "income_statement", "quaterly_income_statement", "balance_sheet", "earnings_dates", "calendar", "recommendations",
  "price_targets", "earnings_estimate", "revenue_estimate", "eps_trend", "growth_estimates", "insider_purchases",
  "insider_transactions", "news"
];

const els = {
  input: document.getElementById("tickerInput"),
  examples: document.getElementById("tickerExamples"),
  button: document.getElementById("searchBtn"),
  status: document.getElementById("statusText"),
  lastUpdated: document.getElementById("lastUpdated"),
  error: document.getElementById("errorText"),
  results: document.getElementById("resultsSection"),
  tabs: document.getElementById("tabs"),
  panelTitle: document.getElementById("panelTitle"),
  panelContent: document.getElementById("panelContent")
};

let lastResponse = null;
let activeDataset = null;

els.examples.addEventListener("change", () => { if (els.examples.value) els.input.value = els.examples.value; });
els.button.addEventListener("click", searchTicker);
els.input.addEventListener("keydown", (e) => { if (e.key === "Enter") searchTicker(); });

function normalizeTicker(value) {
  return (value || "").trim().toUpperCase();
}

async function searchTicker() {
  const ticker = normalizeTicker(els.input.value);
  if (!ticker) {
    setError("Please enter a ticker symbol.");
    return;
  }

  setLoading(true, `Loading ${ticker}...`);
  clearError();

  try {
    const res = await fetch(`${API_BASE}/api/ticker/${ticker}/all`);
    const body = await res.json().catch(() => ({}));
    if (!res.ok) {
      const msg = body?.error?.message || `Request failed (${res.status})`;
      const details = body?.error?.details ? `: ${body.error.details}` : "";
      throw new Error(`${msg}${details}`);
    }

    lastResponse = body;
    activeDataset = DATASET_ORDER[0];
    els.lastUpdated.textContent = `Last updated: ${formatDate(body.timestamp)}`;
    els.status.textContent = `Loaded ${body.symbol || ticker}.`;
    buildTabs();
    renderActiveDataset();
    els.results.classList.remove("hidden");
  } catch (err) {
    setError(err.message || "Unexpected error.");
    els.status.textContent = "Could not load data.";
  } finally {
    setLoading(false);
  }
}

function setLoading(isLoading, message = "") {
  els.button.disabled = isLoading;
  els.status.textContent = isLoading ? message : els.status.textContent;
}

function setError(message) {
  els.error.textContent = message;
  els.error.classList.remove("hidden");
}

function clearError() {
  els.error.textContent = "";
  els.error.classList.add("hidden");
}

function buildTabs() {
  els.tabs.innerHTML = "";
  DATASET_ORDER.forEach((key) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `tab-btn${key === activeDataset ? " active" : ""}`;
    btn.textContent = key;
    btn.setAttribute("role", "tab");
    btn.addEventListener("click", () => {
      activeDataset = key;
      buildTabs();
      renderActiveDataset();
    });
    els.tabs.appendChild(btn);
  });
}

function renderActiveDataset() {
  const value = lastResponse?.data?.[activeDataset];
  els.panelTitle.textContent = `${activeDataset} · Last updated ${formatDate(lastResponse?.timestamp)}`;
  els.panelContent.innerHTML = "";

  if (activeDataset === "news") {els.panelContent.appendChild(renderNews(value));
    return;
  }
  if (isEmpty(value)) return renderMessage("No data available");
  if (isDataFrameLike(value)) return renderTable(["Index", ...value.columns], value.data.map((row, i) => [value.index?.[i], ...row]));
  if (isSeriesLike(value)) return renderTable(["Index", "Value"], value.index.map((idx, i) => [idx, value.data[i]]));
  if (Array.isArray(value)) return renderArray(value);
  if (isObject(value)) return renderObject(value);
  return renderTable(["Metric", "Value"], [[activeDataset, value]]);
}

function renderArray(arr) {
  if (!arr.length) return renderMessage("No data available");
  const allObjects = arr.every(isObject);
  if (!allObjects) return renderTable(["Value"], arr.map((v) => [displayValue(v)]));

  const preferredNews = ["title", "publisher", "providerPublishTime", "link"];
  const keySet = new Set(arr.flatMap((item) => Object.keys(item || {})));
  const keys = activeDataset === "news"
    ? [...preferredNews.filter((k) => keySet.has(k)), ...[...keySet].filter((k) => !preferredNews.includes(k))]
    : [...keySet];

  const rows = arr.map((item) => keys.map((k) => displayValue(item?.[k], k)));
  renderTable(keys, rows);
}

function renderObject(obj) {
  const rows = [];
  Object.entries(obj).forEach(([k, v]) => {
    if (isObject(v) && !Array.isArray(v)) {
      Object.entries(v).forEach(([k2, v2]) => rows.push([`${k}.${k2}`, displayValue(v2, k2)]));
    } else {
      rows.push([k, displayValue(v, k)]);
    }
  });
  renderTable(["Metric", "Value"], rows);
}

function renderTable(headers, rows) {
  if (!rows.length) return renderMessage("No data available");
  const wrap = document.createElement("div");
  wrap.className = "table-wrap";
  const table = document.createElement("table");
  const thead = document.createElement("thead");
  const htr = document.createElement("tr");
  headers.forEach((h) => { const th = document.createElement("th"); th.textContent = h; htr.appendChild(th); });
  thead.appendChild(htr);
  const tbody = document.createElement("tbody");
  rows.forEach((r) => {
    const tr = document.createElement("tr");
    r.forEach((cell, idx) => {
      const td = document.createElement("td");
      if (headers[idx] === "link" && typeof cell === "string" && /^https?:\/\//.test(cell)) {
        const a = document.createElement("a");
        a.href = cell; a.textContent = "Open"; a.target = "_blank"; a.rel = "noreferrer";
        td.appendChild(a);
      } else {
        td.textContent = displayValue(cell);
      }
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.append(thead, tbody);
  wrap.appendChild(table);
  els.panelContent.appendChild(wrap);
}

function renderMessage(text) {
  const p = document.createElement("p");
  p.textContent = text;
  els.panelContent.appendChild(p);
}

function isDataFrameLike(v) { return isObject(v) && Array.isArray(v.columns) && Array.isArray(v.index) && Array.isArray(v.data); }
function isSeriesLike(v) { return isObject(v) && !Array.isArray(v.columns) && Array.isArray(v.index) && Array.isArray(v.data); }
function isObject(v) { return v !== null && typeof v === "object"; }
function isEmpty(v) {
  return v == null || v === "" || (Array.isArray(v) && v.length === 0) || (isObject(v) && !Object.keys(v).length);
}

function displayValue(value, key = "") {
  if (value == null || Number.isNaN(value)) return "";
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "number" && key.toLowerCase().includes("time")) return formatDate(value);
  if (typeof value === "string" && /\d{4}-\d{2}-\d{2}t/i.test(value)) return formatDate(value);
  if (isObject(value)) return JSON.stringify(value);
  return String(value);
}

function formatDate(value) {
  if (value == null || value === "") return "—";
  const asNum = typeof value === "number" ? value * 1000 : value;
  const dt = new Date(asNum);
  return Number.isNaN(dt.getTime()) ? String(value) : dt.toLocaleString();
}

function formatUnixSeconds(sec) {
  if (!sec || typeof sec !== "number") return "";
  return new Date(sec * 1000).toLocaleString();
}

function safeText(v) {
  if (v === null || v === undefined) return "";
  if (typeof v === "string") return v;
  return String(v);
}

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === "className") node.className = v;
    else node.setAttribute(k, v);
  }
  for (const child of children) {
    if (child == null) continue;
    node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
  }
  return node;
}

function renderNews(dataset) {
  // dataset is usually an array like: [{id: "...", content: {...}}, ...]
  if (!Array.isArray(dataset) || dataset.length === 0) {
    return el("div", { className: "empty" }, "No news available");
  }

  // Normalize each item so we have flat fields to show
  const rows = dataset.map((item) => {
    const c = (item && item.content && typeof item.content === "object") ? item.content : item;

    const title = c.title || c.headline || "";
    const publisher =
      c.publisher ||
      c.provider?.displayName ||
      c.provider?.name ||
      c.source ||
      "";
    const published =
      c.providerPublishTime ? formatUnixSeconds(c.providerPublishTime)
      : (c.pubDate ? safeText(c.pubDate) : "");
    const link =
      c.canonicalUrl?.url ||
      c.clickThroughUrl?.url ||
      c.link ||
      c.url ||
      c.originalUrl ||
      "";

    // optional “summary-like” field
    const summary = c.summary || c.description || "";

    return { title, publisher, published, link, summary };
  });

  // Build table
  const table = el("table", { className: "tbl" });
  const thead = el("thead", {}, el("tr", {},
    el("th", {}, "Title"),
    el("th", {}, "Publisher"),
    el("th", {}, "Published"),
    el("th", {}, "Link"),
    el("th", {}, "Summary")
  ));
  table.appendChild(thead);

  const tbody = el("tbody");
  rows.forEach((r) => {
    const linkCell = r.link
      ? el("a", { href: r.link, target: "_blank", rel: "noopener noreferrer" }, "Open")
      : el("span", { className: "muted" }, "");

    tbody.appendChild(
      el("tr", {},
        el("td", {}, safeText(r.title)),
        el("td", {}, safeText(r.publisher)),
        el("td", {}, safeText(r.published)),
        el("td", {}, linkCell),
        el("td", {}, safeText(r.summary))
      )
    );
  });

  table.appendChild(tbody);

  // Wrap for horizontal scroll
  return el("div", { className: "tableWrap" }, table);
}