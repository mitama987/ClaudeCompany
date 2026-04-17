/* Trello Task Dashboard — フロントエンド描画 */
const PALETTE = [
  "#38bdf8", "#f472b6", "#fbbf24", "#a78bfa", "#34d399",
  "#f87171", "#60a5fa", "#fb923c", "#c084fc", "#4ade80",
  "#facc15", "#22d3ee", "#fca5a5", "#818cf8", "#f59e0b",
];
const colorFor = (i) => PALETTE[i % PALETTE.length];

let labelChart, monthlyChart, scatterChart;

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
          backgroundColor: names.map((_, i) => colorFor(i)),
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
  const datasets = (summary.monthly.series || []).map((s, i) => ({
    label: s.label,
    data: s.values,
    backgroundColor: colorFor(i),
    borderColor: colorFor(i),
    tension: 0.2,
    fill: true,
  }));
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
      backgroundColor: colorFor(i++),
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

async function loadAll() {
  try {
    const [summary, scatter, insights] = await Promise.all([
      fetchJSON("/api/summary"),
      fetchJSON("/api/scatter"),
      fetchJSON("/api/insights"),
    ]);
    renderSummaryCards(summary);
    renderLabelChart(summary);
    renderMonthlyChart(summary);
    renderScatter(scatter);
    renderInsights(insights);
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
