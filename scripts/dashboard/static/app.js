/* Trello Task Dashboard — フロントエンド描画 */

// Trello標準ラベル色 → CSS hex
const TRELLO_COLORS = {
  green: "#61bd4f",
  green_dark: "#519839",
  green_light: "#b7ddb0",
  yellow: "#f2d600",
  yellow_dark: "#d9b51c",
  yellow_light: "#f5ea92",
  orange: "#ff9f1a",
  orange_dark: "#cf513d",
  orange_light: "#ffd29c",
  red: "#eb5a46",
  red_dark: "#b04632",
  red_light: "#ef9a9a",
  purple: "#c377e0",
  purple_dark: "#89609e",
  purple_light: "#dfc0eb",
  blue: "#0079bf",
  blue_dark: "#055a8c",
  blue_light: "#8bbdd9",
  sky: "#00c2e0",
  sky_dark: "#0098b7",
  sky_light: "#8fdfeb",
  lime: "#51e898",
  lime_dark: "#4bbf6b",
  lime_light: "#b3f1d0",
  pink: "#ff78cb",
  pink_dark: "#ad5a7d",
  pink_light: "#f9c2e4",
  black: "#344563",
  black_dark: "#091e42",
  black_light: "#8993a4",
  unlabeled: "#94a3b8",
};

const FALLBACK_PALETTE = [
  "#38bdf8", "#f472b6", "#fbbf24", "#a78bfa", "#34d399",
  "#f87171", "#60a5fa", "#fb923c", "#c084fc", "#4ade80",
];

function colorForLabel(name, fallbackIndex) {
  if (!name) return FALLBACK_PALETTE[fallbackIndex % FALLBACK_PALETTE.length];
  const key = String(name).toLowerCase();
  if (TRELLO_COLORS[key]) return TRELLO_COLORS[key];
  // ラベル名に色名が含まれていれば採用
  for (const [k, v] of Object.entries(TRELLO_COLORS)) {
    if (key.includes(k)) return v;
  }
  return FALLBACK_PALETTE[fallbackIndex % FALLBACK_PALETTE.length];
}

let labelChart, monthlyChart, scatterChart, revenueTrendChart;

const JPY = new Intl.NumberFormat("ja-JP", { style: "currency", currency: "JPY", maximumFractionDigits: 0 });
const fmtYen = (n) => JPY.format(n || 0);

async function fetchJSON(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path} ${r.status}`);
  return r.json();
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function renderSummaryCards(summary) {
  setText("stat-total", summary.total_cards);
  setText("stat-rate", `${Math.round((summary.stats.completion_rate || 0) * 100)}%`);
  setText("stat-median", `${summary.stats.median_elapsed_days || 0}日`);
  setText("stat-sum", `${summary.stats.sum_elapsed_days || 0}日`);
  const p = summary.period || {};
  setText(
    "stat-period",
    p.start && p.end ? `${p.start} 〜 ${p.end}` : "--"
  );
}

function renderLabelChart(summary) {
  const ctx = document.getElementById("labelChart");
  if (labelChart) labelChart.destroy();
  const names = summary.labels.names || [];
  labelChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: names,
      datasets: [
        {
          label: "経過日数 合計",
          data: summary.labels.days,
          backgroundColor: names.map((n, i) => colorForLabel(n, i)),
        },
        {
          label: "件数",
          data: summary.labels.counts,
          backgroundColor: "#475569",
          yAxisID: "y2",
        },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: "#e2e8f0" } } },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } },
        y: { ticks: { color: "#e2e8f0" }, grid: { color: "#334155" } },
        y2: { display: false },
      },
    },
  });
}

function renderMonthlyChart(summary) {
  const ctx = document.getElementById("monthlyChart");
  if (monthlyChart) monthlyChart.destroy();
  const months = summary.monthly.months || [];
  const datasets = (summary.monthly.series || []).map((s, i) => {
    const c = colorForLabel(s.label, i);
    return {
      label: s.label,
      data: s.values,
      backgroundColor: c,
      borderColor: c,
      tension: 0.2,
      fill: true,
    };
  });
  monthlyChart = new Chart(ctx, {
    type: "bar",
    data: { labels: months, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: "#e2e8f0" } } },
      scales: {
        x: {
          stacked: true,
          ticks: { color: "#94a3b8" },
          grid: { color: "#334155" },
        },
        y: {
          stacked: true,
          ticks: { color: "#94a3b8" },
          grid: { color: "#334155" },
          title: { display: true, text: "経過日数合計", color: "#94a3b8" },
        },
      },
    },
  });
}

function renderScatter(points) {
  const ctx = document.getElementById("scatterChart");
  if (scatterChart) scatterChart.destroy();
  const byLabel = new Map();
  for (const p of points) {
    const k = p.label || "unlabeled";
    if (!byLabel.has(k)) byLabel.set(k, []);
    byLabel.get(k).push({ x: p.x, y: p.y, name: p.name, card_id: p.card_id, url: p.url });
  }
  let i = 0;
  const datasets = [];
  for (const [label, arr] of byLabel) {
    datasets.push({
      label,
      data: arr,
      backgroundColor: colorForLabel(label, i++),
      pointRadius: 4,
      pointHoverRadius: 6,
    });
  }
  scatterChart = new Chart(ctx, {
    type: "scatter",
    data: { datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#e2e8f0" } },
        tooltip: {
          callbacks: {
            label: (c) => {
              const p = c.raw;
              return `${p.name} (${p.x}日, 反応${p.y})`;
            },
          },
        },
      },
      scales: {
        x: {
          title: { display: true, text: "経過日数", color: "#94a3b8" },
          ticks: { color: "#94a3b8" },
          grid: { color: "#334155" },
        },
        y: {
          title: { display: true, text: "コメント + チェック数", color: "#94a3b8" },
          ticks: { color: "#94a3b8" },
          grid: { color: "#334155" },
        },
      },
    },
  });
}

function renderInsights(items) {
  const root = document.getElementById("insightsList");
  if (!items.length) {
    root.innerHTML = '<p class="loading">示唆は検出されませんでした 🎉</p>';
    return;
  }
  root.innerHTML = items
    .map((it) => {
      const link = it.url
        ? ` <a href="${it.url}" target="_blank" rel="noreferrer">Trelloで開く</a>`
        : "";
      return `<div class="insight ${it.level}">
        <div class="insight-title">${it.icon || ""} ${it.title}</div>
        <div class="insight-message">${it.message}${link}</div>
      </div>`;
    })
    .join("");
}

function renderGoal(goal) {
  const meta = document.getElementById("goalMeta");
  const month = goal.current_month || "--";
  const confirmedTxt = goal.current_confirmed ? "確定" : "暫定";
  meta.textContent = `直近: ${month} ${fmtYen(goal.current_revenue)} (${confirmedTxt})`;

  const etaLabel = (m) =>
    m === null || m === undefined ? "到達予測なし" : m === 0 ? "達成済" : `残 ${m}ヶ月`;

  const order = ["short_term", "year_1", "year_3", "ultimate"];
  const bars = order
    .filter((k) => goal.targets[k])
    .map((k) => {
      const t = goal.targets[k];
      const pct = Math.min(100, Math.round((t.pct || 0) * 100));
      const met = pct >= 100;
      return `
        <div class="goal-bar">
          <div class="goal-bar-head">
            <span class="goal-bar-label">${t.label}</span>
            <span class="goal-bar-pct">${pct}%</span>
          </div>
          <div class="goal-bar-track">
            <div class="goal-bar-fill ${met ? "met" : ""}" style="width:${pct}%"></div>
          </div>
          <div class="goal-bar-sub">
            <span>${fmtYen(goal.current_revenue)} / ${fmtYen(t.target_yen)}</span>
            <span>${etaLabel(t.eta_months)}</span>
          </div>
        </div>`;
    })
    .join("");
  document.getElementById("goalBars").innerHTML = bars;

  // トレンド折れ線
  const ctx = document.getElementById("revenueTrendChart");
  if (revenueTrendChart) revenueTrendChart.destroy();
  const labels = goal.trend.months || [];
  const amounts = goal.trend.amounts || [];
  const forecast = goal.trend.forecast_next;
  const forecastData = amounts.map(() => null);
  if (forecast !== null && forecast !== undefined) {
    forecastData.push(forecast);
    labels.push("next");
    amounts.push(null);
  }
  const targetLines = Object.entries(goal.targets || {}).map(([k, t]) => ({
    label: t.label,
    data: labels.map(() => t.target_yen),
    borderColor: k === "short_term" ? "#fbbf24" : k === "year_1" ? "#34d399" : "#a78bfa",
    borderDash: [5, 4],
    borderWidth: 1.5,
    pointRadius: 0,
    fill: false,
  }));
  revenueTrendChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "月売上",
          data: amounts,
          borderColor: "#38bdf8",
          backgroundColor: "rgba(56,189,248,0.2)",
          tension: 0.2,
          fill: true,
          pointRadius: 3,
        },
        {
          label: "翌月予測",
          data: forecastData,
          borderColor: "#f472b6",
          borderDash: [2, 3],
          pointRadius: 5,
          pointStyle: "rectRot",
          fill: false,
        },
        ...targetLines,
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#e2e8f0", font: { size: 11 } } },
        tooltip: {
          callbacks: {
            label: (c) => `${c.dataset.label}: ${fmtYen(c.parsed.y)}`,
          },
        },
      },
      scales: {
        x: { ticks: { color: "#94a3b8", maxRotation: 0, autoSkip: true }, grid: { color: "#1e293b" } },
        y: {
          ticks: {
            color: "#94a3b8",
            callback: (v) => fmtYen(v),
          },
          grid: { color: "#1e293b" },
        },
      },
    },
  });

  // イニシアチブ
  const init = goal.initiatives || [];
  const dep = goal.dependency || {};
  const depBadge =
    dep.sheet_top_customer && dep.sheet_top_customer_pct > 0
      ? `<div class="initiative-meta">⚠️ 依存度: ${dep.sheet_top_customer} が ${Math.round(dep.sheet_top_customer_pct * 100)}% (スプシ分)</div>`
      : "";
  const initHtml = init
    .map((i) => {
      const status = i.status || "pending";
      const due = i.due ? ` / 期限 ${i.due}` : i.completed ? ` / 完了 ${i.completed}` : "";
      const rationale = i.rationale ? `<div class="initiative-meta">${i.rationale}</div>` : "";
      return `<div class="initiative-item">
        <span class="init-status ${status}">${status}</span>
        <div>
          <div>${i.name}<span class="initiative-meta"> ${i.category || ""}${due}</span></div>
          ${rationale}
        </div>
      </div>`;
    })
    .join("");
  document.getElementById("goalInitiatives").innerHTML =
    `<h3>🚀 イニシアチブ (${init.length})</h3>${depBadge}${initHtml}`;
}

async function loadAll() {
  try {
    const [summary, scatter, insights, goal] = await Promise.all([
      fetchJSON("/api/summary"),
      fetchJSON("/api/scatter"),
      fetchJSON("/api/insights"),
      fetchJSON("/api/goal-progress"),
    ]);
    renderSummaryCards(summary);
    renderLabelChart(summary);
    renderMonthlyChart(summary);
    renderScatter(scatter);
    renderInsights(insights);
    renderGoal(goal);
  } catch (e) {
    console.error(e);
    document.getElementById("insightsList").innerHTML =
      `<p class="loading">読み込みエラー: ${e.message}</p>`;
  }
}

document.getElementById("refreshBtn").addEventListener("click", async () => {
  const status = document.getElementById("refreshStatus");
  status.textContent = "同期中...";
  try {
    const r = await fetch("/api/refresh", { method: "POST" });
    const data = await r.json();
    status.textContent = data.ok ? "✅ 同期完了" : `⚠️ 失敗 (rc=${data.returncode})`;
    await loadAll();
  } catch (e) {
    status.textContent = `⚠️ エラー: ${e.message}`;
  }
});

loadAll();
