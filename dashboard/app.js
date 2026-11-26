/* CJP Discourse Analysis Dashboard — Story-Driven Visual Analytics */

const ICONS = {
  overview: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
  1: '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>',
  2: '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
  3: '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>',
  4: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
  5: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  6: '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
  7: '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
  8: '<line x1="3" y1="12" x2="21" y2="12"/><polyline points="8 7 3 12 8 17"/><polyline points="16 7 21 12 16 17"/>',
  9: '<polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/><polyline points="21 16 21 21 16 21"/><line x1="15" y1="15" x2="21" y2="21"/><line x1="4" y1="4" x2="9" y2="9"/>',
  10: '<circle cx="6" cy="19" r="2"/><circle cx="18" cy="5" r="2"/><path d="M12 19h4a4 4 0 0 0 0-8H8a4 4 0 0 1 0-8h4"/>',
  11: '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
  conclusion: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
};

const STEPS = [
  { id: "overview", label: "Overview" },
  { id: "1", label: "Cleaning" },
  { id: "2", label: "Activity" },
  { id: "3", label: "Network" },
  { id: "4", label: "Community" },
  { id: "5", label: "Sentiment" },
  { id: "6", label: "Trends" },
  { id: "7", label: "Check" },
  { id: "8", label: "EI" },
  { id: "9", label: "Mixing" },
  { id: "10", label: "Controversy" },
  { id: "11", label: "Themes" },
  { id: "conclusion", label: "Conclusion" },
];

const TITLES_STEPS = {
  overview: ["Overview", "All 11 steps, starting from the result"],
  1: ["1 · Cleaning", "Preparing a clean dataset from X & Reddit"],
  2: ["2 · Activity", "Tracking when and where protest activity surged"],
  3: ["3 · Network", "Mapping who replies to or mentions whom"],
  4: ["4 · Community", "Finding natural user clusters on each platform"],
  5: ["5 · Sentiment", "Testing whether the 6 groups feel differently"],
  6: ["6 · Trends", "Separating emotional tone from Pro/Anti-CJP stance"],
  7: ["7 · Check", "Verifying automatic stance labels by hand"],
  8: ["8 · EI Index", "Checking if groups talk inside or across boundaries"],
  9: ["9 · Mixing", "Testing if opposing sides actually talk to each other"],
  10: ["10 · Controversy", "Measuring how sealed or open the network is"],
  11: ["11 · Themes", "Checking whether groups talk about different topics"],
  conclusion: ["Conclusion", "What all 11 steps prove together"],
};

const DEFINITIONS = {
  cleaning: {
    def: "Removed bot accounts, deleted posts, 1,037 duplicate scrapes, and off-topic posts.",
    val: "Keeping 5,487 verified posts (74.3%) ensures counts and networks reflect real users.",
  },
  phases: {
    def: "X tweets grouped around the July 20 march: Before (Jun 7–Jul 19), Peak (Jul 20–24), After (Jul 25–30).",
    val: "Peak holds 1,691 tweets (187.9/day), nearly 10× higher than Before (18.7/day).",
  },
  engagement: {
    def: "Median likes and retweets per tweet across each protest phase.",
    val: "Median likes dropped from 21 (Before) to 5 (Peak) as casual users joined the surge.",
  },
  reciprocity: {
    def: "Share of user pairs that reply to each other both ways.",
    val: "Reddit (14.5%) has 25× more two-way replies than X (0.58%), where users mostly broadcast.",
  },
  modularity: {
    def: "Modularity (Q) measures how cleanly a network splits into separate groups (0 to 1).",
    val: "Above 0.40 is strong clustering. Reddit (0.89) separates tighter than X (0.75).",
  },
  vader: {
    def: "VADER scores emotional tone from −1 (very negative) to +1 (very positive).",
    val: "X (−0.31) is much more negative than Reddit (−0.03); p < 0.001.",
  },
  stance: {
    def: "Stance classifier labels each post as Pro-CJP, Anti-CJP, or Neutral toward the movement.",
    val: "~75% of X and ~71% of Reddit posts are Pro-CJP, even though their tone sounds negative.",
  },
  f1: {
    def: "Weighted F1 balances precision and recall across 180 hand-labeled posts (0 to 1).",
    val: "0.86 F1 (86.1% accuracy) confirms labels are reliable. Neutral recall (0.68) is lowest.",
  },
  ei: {
    def: "E-I Index compares outside links vs. inside links: (E − I) / (E + I), from −1 to +1.",
    val: "Negative means inward groups. X (−0.75) tightens over time; Reddit (−0.94) is even more inward.",
  },
  mixing: {
    def: "Tracks how often Pro-CJP and Anti-CJP users reply to or mention the opposite side.",
    val: "Anti-CJP users direct 64.4% (X) and 70.3% (Reddit) of ties to Pro-CJP, disproving sealed silos.",
  },
  rwc: {
    def: "Random Walk Controversy measures how likely a random walker stays trapped on one side (0 to 1).",
    val: "Near 0 (0.05 X, 0.03 Reddit, 0.14 Peak) means both sides connect easily rather than staying sealed.",
  },
  js: {
    def: "Jensen-Shannon distance measures how different two groups' topics are (0 = identical, 1 = completely different).",
    val: "X (0.40) differs more than Reddit (0.29) mainly because C5 focuses on hashtag campaigning.",
  },
};

const state = {
  platform: "all",
  phase: "all",
  netTab: "x",
  openDef: null,
};

function stepIcon(id) {
  return `<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">${ICONS[id]}</svg>`;
}

function card(span, inner) {
  return `<article class="card ${span}">${inner}</article>`;
}

function storyHeader(question, answer) {
  return `<div class="story-bar s12">
    <div>
      <p class="sb-q">${question}</p>
      <p class="sb-sub">${answer}</p>
    </div>
  </div>`;
}

function termPill(key, label) {
  const isOpen = state.openDef === key;
  const info = DEFINITIONS[key];
  return `<button type="button" class="term-btn ${isOpen ? "open" : ""}" data-def="${key}" title="Click for definition & meaning">${label} <i>ⓘ</i></button>
    ${isOpen && info ? `<div class="def-box"><strong>Definition:</strong> ${info.def}<br><strong>What this value means:</strong> ${info.val}</div>` : ""}`;
}

function filterBar(options, activeVal, attrName, label) {
  return `<div class="filter-bar s12">
    <span class="kicker" style="margin:0">${label}</span>
    <div class="seg-group">
      ${options.map((o) => `<button type="button" class="seg-btn ${activeVal === o.id ? "active" : ""}" data-${attrName}="${o.id}">${o.label}</button>`).join("")}
    </div>
  </div>`;
}

// ============================================================================
// NATIVE INTERACTIVE SVG CHARTS (Uncompressed, Generous Height)
// ============================================================================

function svgLineChart(xLabels, series, opts = {}) {
  const w = 520;
  const h = 215;
  const pad = { top: 18, right: 22, bottom: 32, left: 44 };
  const innerW = w - pad.left - pad.right;
  const innerH = h - pad.top - pad.bottom;

  const allVals = series.flatMap((s) => s.values);
  const minV = opts.min !== undefined ? opts.min : Math.min(0, ...allVals);
  const maxV = opts.max !== undefined ? opts.max : Math.max(...allVals);
  const span = maxV - minV || 1;

  const xPos = (i) => pad.left + (xLabels.length === 1 ? innerW / 2 : (i / (xLabels.length - 1)) * innerW);
  const yPos = (v) => pad.top + ((maxV - v) / span) * innerH;

  const ticks = [0, 0.25, 0.5, 0.75, 1].map((t) => minV + t * span);
  const gridSvg = ticks.map((val) => {
    const y = yPos(val);
    const isZero = Math.abs(val) < 1e-6 && minV < 0 && maxV > 0;
    return `<line x1="${pad.left}" y1="${y.toFixed(1)}" x2="${w - pad.right}" y2="${y.toFixed(1)}" stroke="${isZero ? "#94a3b8" : "#eceff3"}" stroke-dasharray="${isZero ? "4 3" : "0"}" stroke-width="1"/>
      <text x="${pad.left - 8}" y="${(y + 4).toFixed(1)}" text-anchor="end" font-size="11" font-weight="600" fill="#8b919a">${opts.fmt ? opts.fmt(val) : val.toFixed(2)}</text>`;
  }).join("");

  const xSvg = xLabels.map((lbl, i) => `<text x="${xPos(i).toFixed(1)}" y="${h - 8}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#4d545e">${lbl}</text>`).join("");

  const linesSvg = series.map((s) => {
    const pts = s.values.map((v, i) => `${xPos(i).toFixed(1)},${yPos(v).toFixed(1)}`).join(" ");
    const dots = s.values.map((v, i) => {
      const cx = xPos(i).toFixed(1);
      const cy = yPos(v).toFixed(1);
      const valStr = opts.fmt ? opts.fmt(v) : v.toFixed(3);
      return `<circle cx="${cx}" cy="${cy}" r="5" fill="#ffffff" stroke="${s.color}" stroke-width="2.5" style="cursor:pointer" data-tip="${s.name} · ${xLabels[i]}: ${valStr}"/>`;
    }).join("");
    return `<polyline fill="none" stroke="${s.color}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" points="${pts}"/>${dots}`;
  }).join("");

  const legend = `<div class="legend" style="margin-bottom:8px">${series.map((s) => `<span><i class="dot" style="background:${s.color}"></i>${s.name}</span>`).join("")}</div>`;
  return `${legend}<svg viewBox="0 0 ${w} ${h}" style="width:100%;height:auto;display:block">${gridSvg}${xSvg}${linesSvg}</svg>`;
}

function svgStackedBars(categories, segments) {
  const w = 520;
  const h = 215;
  const pad = { top: 14, right: 14, bottom: 28, left: 38 };
  const innerW = w - pad.left - pad.right;
  const innerH = h - pad.top - pad.bottom;
  const barSlot = innerW / categories.length;
  const barW = Math.min(38, barSlot * 0.56);

  const grid = [0, 50, 100].map((v) => {
    const y = pad.top + ((100 - v) / 100) * innerH;
    return `<line x1="${pad.left}" y1="${y.toFixed(1)}" x2="${w - pad.right}" y2="${y.toFixed(1)}" stroke="#eceff3" stroke-width="1"/>
      <text x="${pad.left - 7}" y="${(y + 4).toFixed(1)}" text-anchor="end" font-size="11" font-weight="600" fill="#8b919a">${v}%</text>`;
  }).join("");

  const bars = categories.map((cat, idx) => {
    const x = pad.left + idx * barSlot + (barSlot - barW) / 2;
    let yBottom = pad.top + innerH;
    const rects = segments.map((seg) => {
      const val = seg.values[idx] || 0;
      const segH = (val / 100) * innerH;
      const yTop = yBottom - segH;
      yBottom = yTop;
      return `<rect x="${x.toFixed(1)}" y="${yTop.toFixed(1)}" width="${barW.toFixed(1)}" height="${Math.max(0, segH).toFixed(1)}" rx="3" fill="${seg.color}" data-tip="${cat} · ${seg.name}: ${val.toFixed(1)}%"/>`;
    }).join("");
    const lbl = `<text x="${(x + barW / 2).toFixed(1)}" y="${h - 7}" text-anchor="middle" font-size="11.5" font-weight="700" fill="#4d545e">${cat}</text>`;
    return rects + lbl;
  }).join("");

  const legend = `<div class="legend" style="margin-bottom:8px">${segments.map((s) => `<span><i class="dot" style="background:${s.color}"></i>${s.name}</span>`).join("")}</div>`;
  return `${legend}<svg viewBox="0 0 ${w} ${h}" style="width:100%;height:auto;display:block">${grid}${bars}</svg>`;
}

function svgVerticalBars(items, opts = {}) {
  const w = 480;
  const h = 250;
  const pad = { top: 24, right: 16, bottom: 32, left: 44 };
  const innerW = w - pad.left - pad.right;
  const innerH = h - pad.top - pad.bottom;
  const maxV = opts.max || Math.max(...items.map((d) => d.value));
  const slot = innerW / items.length;
  const barW = Math.min(54, slot * 0.54);

  const grid = [0, 0.5, 1].map((t) => {
    const v = t * maxV;
    const y = pad.top + (1 - t) * innerH;
    return `<line x1="${pad.left}" y1="${y.toFixed(1)}" x2="${w - pad.right}" y2="${y.toFixed(1)}" stroke="#eceff3" stroke-width="1"/>
      <text x="${pad.left - 8}" y="${(y + 4).toFixed(1)}" text-anchor="end" font-size="11.5" font-weight="600" fill="#8b919a">${Math.round(v)}</text>`;
  }).join("");

  const bars = items.map((d, i) => {
    const bh = Math.max(4, (d.value / maxV) * innerH);
    const x = pad.left + i * slot + (slot - barW) / 2;
    const y = pad.top + innerH - bh;
    const fill = d.alt ? "#f0a04a" : (d.muted ? "#d5d8df" : "#7dce45");
    return `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${barW.toFixed(1)}" height="${bh.toFixed(1)}" rx="7" fill="${fill}" data-tip="${d.tip || `${d.label}: ${d.value}`}"/>
      <text x="${(x + barW / 2).toFixed(1)}" y="${(y - 7).toFixed(1)}" text-anchor="middle" font-size="12" font-weight="700" fill="#4d545e">${d.text || d.value}</text>
      <text x="${(x + barW / 2).toFixed(1)}" y="${h - 8}" text-anchor="middle" font-size="12" font-weight="700" fill="#8b919a">${d.label}</text>`;
  }).join("");

  return `<svg viewBox="0 0 ${w} ${h}" style="width:100%;height:230px;display:block">${grid}${bars}</svg>`;
}

function heatmapMatrix(rowLabels, colLabels, matrix) {
  return `<div class="cm-grid" style="grid-template-columns:92px repeat(${colLabels.length},1fr)">
    <div></div>${colLabels.map((c) => `<div class="cm-head">${c}</div>`).join("")}
    ${rowLabels.map((r, ri) => `
      <div class="cm-row-lbl">${r}</div>
      ${matrix[ri].map((cell, ci) => `
        <div class="cm-cell" style="background:${cell.bg || "#f4f6f8"};color:${cell.fg || "var(--ink)"}" data-tip="${cell.tip || `${r}, ${colLabels[ci]}: ${cell.val}`}">
          ${cell.val}${cell.sub ? `<small>${cell.sub}</small>` : ""}
        </div>
      `).join("")}
    `).join("")}
  </div>`;
}

// ============================================================================
// EXISTING OVERVIEW HELPER COMPONENTS (Preserved Intact)
// ============================================================================

function volumeBars(maxWeight) {
  const phases = [
    { label: "Before", tweets: 806, weight: 521, internal: 423, external: 98, ei: -0.6238 },
    { label: "Peak", tweets: 1691, weight: 977, internal: 847, external: 130, ei: -0.7339 },
    { label: "After", tweets: 950, weight: 1062, internal: 946, external: 116, ei: -0.7815 },
  ];
  return `<div class="vbars">${phases.map((phase) => {
    const height = Math.round((phase.weight / maxWeight) * 168);
    const inn = Math.round((phase.internal / phase.weight) * height);
    const ext = height - inn;
    const hot = phase.label === "After" ? " hot" : "";
    return `<div class="vbar" data-tip="${phase.label}: ${phase.internal} inside, ${phase.external} across (E-I ${phase.ei.toFixed(4)})">
      <div class="stack" style="height:${height}px"><i class="ext" style="height:${ext}px"></i><i class="inn${hot}" style="height:${inn}px"></i></div>
      <span>${phase.label}</span>
    </div>`;
  }).join("")}</div>`;
}

function hbars(rows, wide = false) {
  const max = Math.max(...rows.map((row) => row.value));
  return `<div class="hbar ${wide ? "wide" : ""}">${rows.map((row) => `
    <div class="row" data-tip="${row.tip || `${row.label}: ${row.text}`}"><span>${row.label}</span><div class="track"><b class="${row.alt ? "alt" : ""}" style="width:${Math.max(4, (row.value / max) * 100)}%"></b></div><em>${row.text}</em></div>
  `).join("")}</div>`;
}

function gauge(percent, gradientId) {
  const radius = 54;
  const length = Math.PI * radius;
  const drawn = (percent / 100) * length;
  return `<svg viewBox="0 0 140 86" width="144" height="88" aria-hidden="true">
    <defs>
      <linearGradient id="${gradientId}" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="#c6e86a"/><stop offset="1" stop-color="#5eae2e"/>
      </linearGradient>
    </defs>
    <path d="M16 72 A 54 54 0 0 1 124 72" fill="none" stroke="#e6e8ee" stroke-width="12" stroke-linecap="round"/>
    <path d="M16 72 A 54 54 0 0 1 124 72" fill="none" stroke="url(#${gradientId})" stroke-width="12" stroke-linecap="round"
      stroke-dasharray="${drawn.toFixed(1)} ${length.toFixed(1)}"/>
    <text x="70" y="68" text-anchor="middle" font-size="18" font-weight="800" fill="#1c1e21">${Number.isInteger(percent) ? percent.toFixed(0) : percent.toFixed(1)}%</text>
  </svg>`;
}

function splitBar(neg, neu, pos) {
  return `<div class="split" data-tip="Negative ${neg}%, Neutral ${neu}%, Positive ${pos}%">
    <span class="neg" style="width:${neg}%"></span>
    <span class="neu" style="width:${neu}%"></span>
    <span class="pos" style="width:${pos}%"></span>
  </div>
  <div class="split-key"><span><i class="dot o"></i>Negative ${neg}%</span><span><i class="dot n"></i>Neutral ${neu}%</span><span><i class="dot g"></i>Positive ${pos}%</span></div>`;
}

function divergingBars(rows) {
  return `<div class="hbar">${rows.map((r) => {
    const pct = Math.min(50, Math.abs(r.value) * 50);
    const isNeg = r.value < 0;
    const left = isNeg ? (50 - pct) : 50;
    return `<div class="div-row" data-tip="${r.tip || `${r.label}: ${r.value.toFixed(4)}`}">
      <span style="font-weight:700">${r.label}</span>
      <div class="div-track">
        <div class="div-zero"></div>
        <div class="div-fill ${isNeg ? "inward" : "outward"}" style="left:${left}%;width:${pct}%"></div>
      </div>
      <em style="font-style:normal;text-align:right;font-weight:700;color:${isNeg ? "var(--green-deep)" : "#b85c0b"}">${r.value > 0 ? "+" : ""}${r.value.toFixed(3)}</em>
    </div>`;
  }).join("")}</div>`;
}

// ============================================================================
// OVERVIEW (Preserved intact)
// ============================================================================

function overview() {
  return `<div class="grid">
    ${card("s6", `<p class="kicker">Network E-I · Inward Clustering</p><h2>−0.75 <span style="font-size:16px;font-weight:600;color:var(--muted)">X · −0.94 Reddit</span></h2><p class="lead">X tightens from −0.62 (Before) to −0.73 (Peak) to −0.78 (After).</p>
      <div class="legend" style="margin-top:12px"><span><i class="dot g"></i>Inside</span><span><i class="dot o"></i>Across</span></div>
      ${volumeBars(1062)}`)}
    ${card("s3", `<div class="stat-list">
      <article><p class="kicker">X posts in the analysis</p><h2>3,447</h2><p class="delta up">Peak holds 1,691 · 86.1% stance F1 check</p></article>
      <article><p class="kicker">Reddit posts and comments</p><h2>2,040</h2><p class="delta flat">14.5% two-way reply reciprocity</p></article>
      <article><p class="kicker">Most separated moment</p><h2>0.14</h2><p class="delta up">Peak RWC on X (0.05 full, 0.03 Reddit)</p></article>
    </div>`)}
    ${card("s3 green-card", `<p class="kicker">The result</p><h3 style="font-size:21px;letter-spacing:-0.03em;margin-top:8px">Communities tighten, and the sides still meet.</h3>
      <p class="lead">Pro-CJP stays near 75% on X and 71% on Reddit. Anti-CJP directs 64%–70% of its ties straight to Pro-CJP, and both platforms share the same street protest theme.</p>`)}
    ${card("s4", `
      <div class="fig-head">
        <p class="kicker" style="margin:0">Stance Split (Pro-CJP vs. Anti-CJP)</p>
        <span class="fig-tag">0.86 F1</span>
      </div>
      <div class="hbar" style="margin-top:14px">
        <div class="row" data-tip="X: 75.5% Pro-CJP, 23.0% Anti-CJP, 1.5% Neutral"><span>X Pro</span><div class="track"><b style="width:75.5%"></b></div><em>75.5%</em></div>
        <div class="row" data-tip="Reddit: 71.2% Pro-CJP, 27.8% Anti-CJP, 1.0% Neutral"><span>Red Pro</span><div class="track"><b style="width:71.2%"></b></div><em>71.2%</em></div>
        <div class="row" data-tip="X Anti-CJP: 23.0% | Reddit Anti-CJP: 27.8%"><span>Anti avg</span><div class="track"><b class="alt" style="width:25.4%"></b></div><em>23–28%</em></div>
      </div>
      <p class="takeaway">Roughly 3 in 4 posts back CJP on both platforms.</p>
    `)}
    ${card("s4", `
      <div class="fig-head">
        <p class="kicker" style="margin:0">Emotional Tone (VADER)</p>
        <span class="fig-tag">−0.31 X · −0.03 Red</span>
      </div>
      <div style="margin-top:12px">
        <div style="display:flex;justify-content:space-between;font-size:12px;font-weight:700;margin-bottom:4px"><span>X (Twitter)</span><span style="color:var(--muted)">73.5% Neg</span></div>
        <div class="split" style="margin-top:0" data-tip="X: 73.5% Neg, 7.9% Neu, 18.6% Pos"><span class="neg" style="width:73.5%"></span><span class="neu" style="width:7.9%"></span><span class="pos" style="width:18.6%"></span></div>
      </div>
      <div style="margin-top:10px">
        <div style="display:flex;justify-content:space-between;font-size:12px;font-weight:700;margin-bottom:4px"><span>Reddit</span><span style="color:var(--muted)">37.7% Neg · 35.4% Pos</span></div>
        <div class="split" style="margin-top:0" data-tip="Reddit: 37.7% Neg, 27.0% Neu, 35.4% Pos"><span class="neg" style="width:37.7%"></span><span class="neu" style="width:27.0%"></span><span class="pos" style="width:35.4%"></span></div>
      </div>
      <div class="split-key" style="margin-top:10px"><span><i class="dot o"></i>Negative</span><span><i class="dot n"></i>Neutral</span><span><i class="dot g"></i>Positive</span></div>
    `)}
    ${card("s4", `
      <div class="fig-head">
        <p class="kicker" style="margin:0">Cross-Stance Mixing</p>
        <span class="fig-tag">Anti to Pro</span>
      </div>
      <div class="hbar" style="margin-top:14px">
        <div class="row" data-tip="On X, 64.4% of Anti-CJP interactions target Pro-CJP"><span>X Ties</span><div class="track"><b class="alt" style="width:64.4%"></b></div><em>64.4%</em></div>
        <div class="row" data-tip="On Reddit, 70.3% of Anti-CJP replies target Pro-CJP"><span>Reddit</span><div class="track"><b class="alt" style="width:70.3%"></b></div><em>70.3%</em></div>
      </div>
      <div class="pair" style="margin-top:auto;padding-top:10px"><div class="duo">
        <div class="mini"><span>Clean Kept</span><b>5,487</b></div>
        <div class="mini"><span>Raw Scraped</span><b>7,388</b></div>
      </div></div>
    `)}
  </div>`;
}

// ============================================================================
// 1. CLEANING
// ============================================================================

function step1() {
  return `<div class="grid">
    ${storyHeader("Which posts did we keep, and why did we remove the rest?", "We removed bots, duplicate scrapes, and off-topic posts so only genuine protest discussion enters the analysis.")}

    ${card("s6", `
      ${termPill("cleaning", "Clean Corpus")}
      <h2>5,487 <span style="font-size:15px;font-weight:600;color:var(--muted)">of 7,388 raw (74.3%)</span></h2>
      <div class="funnel-list">
        <div class="funnel-step" data-tip="All collected posts from X (4,909) and Reddit (2,479)">
          <span class="funnel-label">Raw Harvest</span>
          <div class="funnel-bar-wrap"><div class="funnel-bar" style="width:100%"></div></div>
          <span class="funnel-val">7,388</span>
        </div>
        <div class="funnel-step" data-tip="1,037 duplicate scrapes + 864 bots/off-topic">
          <span class="funnel-label">Removed</span>
          <div class="funnel-bar-wrap"><div class="funnel-bar drop" style="width:25.7%"></div></div>
          <span class="funnel-val">−1,901</span>
        </div>
        <div class="funnel-step" data-tip="3,447 of 4,909 X tweets (70.2%)">
          <span class="funnel-label">X Clean</span>
          <div class="funnel-bar-wrap"><div class="funnel-bar" style="width:70.2%"></div></div>
          <span class="funnel-val">3,447</span>
        </div>
        <div class="funnel-step" data-tip="149 posts + 1,891 comments (82.3%)">
          <span class="funnel-label">Reddit Clean</span>
          <div class="funnel-bar-wrap"><div class="funnel-bar" style="width:82.3%"></div></div>
          <span class="funnel-val">2,040</span>
        </div>
      </div>
      <p class="takeaway"><strong>Where it happened:</strong> X (3,447 tweets across 3 windows) and Reddit (2,040 items across 2 subreddits).</p>
    `)}

    ${card("s6", `
      ${termPill("phases", "X Posts by Protest Phase")}
      ${svgVerticalBars([
        { label: "Before (43d)", value: 806, text: "806", tip: "Jun 7 – Jul 19 (43 days)" },
        { label: "Peak (9d)", value: 1691, text: "1,691", tip: "Jul 20 – Jul 24 (9 days)" },
        { label: "After (7d)", value: 950, text: "950", alt: true, tip: "Jul 25 – Jul 30 (7 days)" },
      ])}
      <p class="takeaway"><strong>Key takeaway:</strong> Almost half of all X tweets (1,691) arrived during the 9-day Peak window around July 20.</p>
    `)}
  </div>`;
}

// ============================================================================
// 2. ACTIVITY
// ============================================================================

function step2() {
  const showX = state.platform === "all" || state.platform === "x";
  const showR = state.platform === "all" || state.platform === "reddit";

  return `<div class="grid">
    ${storyHeader("When did people post the most, and who did they mention?", "Volume spiked 10× during the Peak march, while engagement per post dropped as casual users joined.")}

    ${filterBar([
      { id: "all", label: "Both Platforms" },
      { id: "x", label: "X (Twitter)" },
      { id: "reddit", label: "Reddit" },
    ], state.platform, "platform", "Platform")}

    ${showX ? card("s6", `
      ${termPill("phases", "X Daily Rate (Tweets / Day)")}
      ${svgVerticalBars([
        { label: "Before", value: 18.7, text: "18.7/d", tip: "806 tweets over 43 days" },
        { label: "Peak", value: 187.9, text: "187.9/d", tip: "1,691 tweets over 9 days (max 459 on Jul 24)" },
        { label: "After", value: 135.7, text: "135.7/d", alt: true, tip: "950 tweets over 7 days" },
      ])}
      <p class="takeaway"><strong>Peak day:</strong> Posting hit 459 tweets on July 24 — nearly 10× the Before baseline.</p>
    `) : ""}

    ${showX ? card("s6", `
      ${termPill("engagement", "Median Likes & Retweets")}
      ${svgLineChart(["Before", "Peak", "After"], [
        { name: "Median Likes", color: "#7dce45", values: [21, 5, 6] },
        { name: "Median Retweets", color: "#f0a04a", values: [5, 1, 1] },
      ], { fmt: (v) => Math.round(v), min: 0, max: 25 })}
      <p class="takeaway"><strong>Engagement paradox:</strong> More posts meant lower median likes (21 down to 5), though viral clips still hit 41,566 likes.</p>
    `) : ""}

    ${showX ? card("s6", `
      <p class="kicker">Top Protest Hashtags on X</p>
      ${hbars([
        { label: "#cjp", value: 1219, text: "1,219" },
        { label: "#neet", value: 1044, text: "1,044" },
        { label: "#protest", value: 514, text: "514" },
        { label: "#jantarmantar", value: 471, text: "471" },
        { label: "#cjpprotest", value: 405, text: "405" },
        { label: "#dharmendrapradhan", value: 378, text: "378", alt: true },
        { label: "#sonamwangchuk", value: 330, text: "330" },
        { label: "#delhi", value: 263, text: "263" },
      ], true)}
      <p class="takeaway"><strong>Focus:</strong> Tags link the CJP movement directly to NEET, Jantar Mantar, and Education Minister Pradhan.</p>
    `) : ""}

    ${showX ? card("s6", `
      <p class="kicker">Top Mentioned Accounts on X</p>
      ${hbars([
        { label: "@abhijeet_dipke", value: 158, text: "158" },
        { label: "@cockroachisback", value: 123, text: "123" },
        { label: "@cjp_for_india", value: 88, text: "88" },
        { label: "@wangchuk66", value: 85, text: "85" },
        { label: "@sauravdassss", value: 60, text: "60" },
        { label: "@narendramodi", value: 53, text: "53", alt: true },
        { label: "@delhipolice", value: 48, text: "48", alt: true },
        { label: "@bjp4india", value: 43, text: "43", alt: true },
      ], true)}
      <p class="takeaway"><strong>Actors:</strong> Green bars are protest organizers; orange bars are government and police targets.</p>
    `) : ""}

    ${showR ? card("s6", `
      <p class="kicker">Reddit Activity Over Time</p>
      ${svgVerticalBars([
        { label: "May", value: 1, text: "1", muted: true, tip: "May 2026: 1 post" },
        { label: "Jun", value: 465, text: "465", tip: "June 2026: 465 posts & comments" },
        { label: "Jul", value: 1457, text: "1,457", tip: "July 2026: 1,457 posts & comments (71.4%)" },
        { label: "Aug", value: 117, text: "117", alt: true, tip: "August 2026: 117 posts & comments" },
      ])}
      <p class="takeaway"><strong>July spike:</strong> 71.4% of all Reddit activity happened in July around the protest peak.</p>
    `) : ""}

    ${showR ? card("s6", `
      <p class="kicker">Reddit Reply Depth (2,040 Items)</p>
      ${svgVerticalBars([
        { label: "Posts", value: 149, text: "149", muted: true, tip: "149 main posts" },
        { label: "Direct", value: 712, text: "712", tip: "712 top-level comments" },
        { label: "Nested", value: 1179, text: "1,179", tip: "1,179 nested replies" },
      ])}
      <p class="takeaway"><strong>Discussion depth:</strong> 57.8% of Reddit items are nested replies inside back-and-forth threads.</p>
    `) : ""}

    ${showR ? card("s12", `
      <p class="kicker">Reddit Participation Summary</p>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:8px">
        <div class="mini"><span>Subreddits</span><b>2</b></div>
        <div class="mini"><span>Active Accounts</span><b>1,109</b></div>
        <div class="mini"><span>Top User Share</span><b>5.2%</b></div>
        <div class="mini"><span>Two-Way Pairs</span><b>226</b></div>
      </div>
      <p class="takeaway"><strong>Where it happened:</strong> Continuous May–Aug discussion across r/cockroachjantaparty and r/IndianFocus.</p>
    `) : ""}
  </div>`;
}

// ============================================================================
// 3. NETWORK
// ============================================================================

function step3() {
  return `<div class="grid">
    ${storyHeader("Who is talking to whom on X and Reddit?", "Next, we map replies and mentions into a network. Reddit forms two-way debates; X is mostly one-way tagging.")}

    ${card("s4", `
      <p class="kicker">X Interaction Graph</p>
      <h2>1,517 <span style="font-size:14px;font-weight:600;color:var(--muted)">accounts</span></h2>
      <div class="pair" style="margin-top:auto;padding-top:10px"><div class="duo">
        <div class="mini"><span>Edges</span><b>1,722</b></div>
        <div class="mini"><span>Components</span><b>114</b></div>
      </div></div>
      <p class="takeaway"><strong>Pattern:</strong> Mentions and quotes connect users to public figures.</p>
    `)}

    ${card("s4", `
      <p class="kicker">Reddit Reply Graph</p>
      <h2>1,109 <span style="font-size:14px;font-weight:600;color:var(--muted)">accounts</span></h2>
      <div class="pair" style="margin-top:auto;padding-top:10px"><div class="duo">
        <div class="mini"><span>Edges</span><b>1,560</b></div>
        <div class="mini"><span>Components</span><b>129</b></div>
      </div></div>
      <p class="takeaway"><strong>Pattern:</strong> Comment-to-parent replies form dense thread hubs.</p>
    `)}

    ${card("s4", `
      ${termPill("reciprocity", "Two-Way Reciprocity")}
      ${hbars([
        { label: "Reddit", value: 14.49, text: "14.5% (226)" },
        { label: "X", value: 0.58, text: "0.58% (10)", alt: true },
      ])}
      <p class="takeaway"><strong>Key difference:</strong> Reddit has 25× more two-way replies than X.</p>
    `)}

    ${card("s12", `
      <div class="fig-head" style="margin-bottom:8px">
        <div><p class="kicker" style="margin:0">Reddit Reply Network</p></div>
        <span class="fig-tag">1,109 Accounts · 1,560 Links</span>
      </div>
      <div class="zoom-viewport" data-zoom-box="net-svg">
        <div class="zoom-stage" id="zoom-net-svg">
          <img src="../output/03_network_analysis/reddit/reddit_data.svg" alt="Reddit Interaction Network" style="display:block;width:100%;max-height:420px;object-fit:contain;pointer-events:none">
        </div>
        <div class="zoom-controls">
          <button type="button" class="zoom-btn" data-zoom-target="net-svg" data-zoom-dir="in" title="Zoom in">+</button>
          <button type="button" class="zoom-btn" data-zoom-target="net-svg" data-zoom-dir="out" title="Zoom out">−</button>
          <button type="button" class="zoom-btn" data-zoom-target="net-svg" data-zoom-dir="reset" title="Reset view">Reset</button>
        </div>
      </div>
      <p class="takeaway"><strong>Use + / − or drag to pan:</strong> Dots sitting close together reply in the same threads. Next step: splitting these into 6 communities.</p>
    `)}
  </div>`;
}

// ============================================================================
// 4. COMMUNITY
// ============================================================================

function step4() {
  const xComms = [
    { label: "C1", value: 175, text: "175", tip: "Organizers & activists" },
    { label: "C2", value: 145, text: "145", tip: "Media & officials" },
    { label: "C3", value: 76, text: "76", tip: "Legal & civil rights" },
    { label: "C4", value: 74, text: "74", tip: "Political commentary" },
    { label: "C5", value: 69, text: "69", tip: "Regional chapter" },
    { label: "C6", value: 57, text: "57", alt: true, tip: "Skeptics" },
  ];
  const rComms = [
    { label: "C1", value: 133, text: "133", tip: "Protest coordination" },
    { label: "C2", value: 82, text: "82", tip: "News & current affairs" },
    { label: "C3", value: 76, text: "76", tip: "Exam policy" },
    { label: "C4", value: 59, text: "59", tip: "Student grievances" },
    { label: "C5", value: 59, text: "59", tip: "Political talk" },
    { label: "C6", value: 57, text: "57", tip: "Personal stories" },
  ];

  const netSrc = state.netTab === "x"
    ? "../output/04_community_detection/x/interactive_x_network.html"
    : "../output/04_community_detection/reddit/interactive_reddit_network.html";

  return `<div class="grid">
    ${storyHeader("Do users naturally split into smaller groups?", "Both platforms partition cleanly into 6 major communities (C1–C6). Next, we check if those groups feel differently.")}

    ${card("s6", `
      ${termPill("modularity", "X Modularity (Q)")}
      <h2>0.75</h2>
      ${hbars(xComms)}
      <div class="role-grid">
        <span class="role-chip"><b>C1</b> Organizers</span>
        <span class="role-chip"><b>C2</b> Media &amp; Officials</span>
        <span class="role-chip"><b>C3</b> Legal &amp; Rights</span>
        <span class="role-chip"><b>C4</b> Political Debate</span>
        <span class="role-chip"><b>C5</b> Regional Chapter</span>
        <span class="role-chip"><b>C6</b> Skeptics</span>
      </div>
    `)}

    ${card("s6", `
      ${termPill("modularity", "Reddit Modularity (Q)")}
      <h2>0.89</h2>
      ${hbars(rComms)}
      <div class="role-grid">
        <span class="role-chip"><b>C1</b> Coordination</span>
        <span class="role-chip"><b>C2</b> Current Affairs</span>
        <span class="role-chip"><b>C3</b> Exam Policy</span>
        <span class="role-chip"><b>C4</b> Student Grievances</span>
        <span class="role-chip"><b>C5</b> Political Talk</span>
        <span class="role-chip"><b>C6</b> Personal Stories</span>
      </div>
    `)}

    ${card("s12", `
      <div class="fig-head" style="margin-bottom:8px">
        <div>
          <p class="kicker" style="margin:0">Interactive Cluster Map (${state.netTab === "x" ? "X · Q = 0.75" : "Reddit · Q = 0.89"})</p>
        </div>
        <div class="seg-group">
          <button type="button" class="seg-btn ${state.netTab === "x" ? "active" : ""}" data-nettab="x">X Network</button>
          <button type="button" class="seg-btn ${state.netTab === "reddit" ? "active" : ""}" data-nettab="reddit">Reddit Network</button>
        </div>
      </div>
      <div class="net-iframe-wrap" data-zoom-box="comm-net">
        <div class="zoom-stage" id="zoom-comm-net">
          <iframe class="net-iframe" src="${netSrc}" title="Interactive ${state.netTab} community network"></iframe>
        </div>
        <div class="zoom-controls">
          <button type="button" class="zoom-btn" data-zoom-target="comm-net" data-zoom-dir="in" title="Zoom in">+</button>
          <button type="button" class="zoom-btn" data-zoom-target="comm-net" data-zoom-dir="out" title="Zoom out">−</button>
          <button type="button" class="zoom-btn" data-zoom-target="comm-net" data-zoom-dir="reset" title="Reset view">Reset</button>
        </div>
      </div>
      <p class="takeaway"><strong>How to explore:</strong> Use <strong>+ / −</strong> or scroll to zoom, drag any node to inspect its cluster, and match C1–C6 roles above.</p>
    `)}
  </div>`;
}

// ============================================================================
// 5. SENTIMENT
// ============================================================================

function step5() {
  const showX = state.platform === "all" || state.platform === "x";
  const showR = state.platform === "all" || state.platform === "reddit";

  return `<div class="grid">
    ${storyHeader("We found 6 groups — do they feel differently?", "X is overwhelmingly negative (−0.31), while Reddit is evenly balanced (−0.03). Both platforms show real differences across their 6 groups.")}

    ${filterBar([
      { id: "all", label: "Both Platforms" },
      { id: "x", label: "X (Twitter)" },
      { id: "reddit", label: "Reddit" },
    ], state.platform, "platform", "Platform")}

    ${showX ? card("s6", `
      ${termPill("vader", "X VADER Sentiment")}
      <h2>−0.31</h2>
      <p class="lead">73.5% of 3,447 tweets carry a negative tone.</p>
      ${splitBar(73.5, 7.9, 18.6)}
      <p class="takeaway"><strong>Why X is negative:</strong> Protest posts express outrage at exam leaks and police detentions.</p>
    `) : ""}

    ${showR ? card("s6", `
      ${termPill("vader", "Reddit VADER Sentiment")}
      <h2>−0.03</h2>
      <p class="lead">Balanced mood across 2,040 posts and comments.</p>
      ${splitBar(37.7, 27.0, 35.4)}
      <p class="takeaway"><strong>Why Reddit is calmer:</strong> Longer comment threads mix critique, neutral facts, and support (p &lt; 0.001 vs. X).</p>
    `) : ""}

    ${showX ? card("s6", `
      <p class="kicker">X Tone by Community (C1–C6)</p>
      ${svgStackedBars(["C1", "C2", "C3", "C4", "C5", "C6", "Other"], [
        { name: "Negative", color: "#f0a04a", values: [70.9, 80.0, 66.0, 82.3, 90.8, 69.2, 74.3] },
        { name: "Neutral", color: "#d5d8df", values: [3.9, 5.2, 7.8, 0.0, 0.0, 1.9, 6.8] },
        { name: "Positive", color: "#7dce45", values: [25.3, 14.8, 26.2, 17.7, 9.2, 28.9, 19.0] },
      ])}
      <p class="takeaway"><strong>Where groups differ:</strong> C5 is 90.8% negative; C4 (political debate) is significantly harsher than C2 (media, p = 0.024).</p>
    `) : ""}

    ${showR ? card("s6", `
      <p class="kicker">Reddit Tone by Community (C1–C6)</p>
      ${svgStackedBars(["C1", "C2", "C3", "C4", "C5", "C6", "Other"], [
        { name: "Negative", color: "#f0a04a", values: [28.7, 31.4, 45.1, 39.0, 39.0, 26.8, 37.9] },
        { name: "Neutral", color: "#d5d8df", values: [40.4, 33.9, 29.2, 32.0, 35.4, 28.1, 24.4] },
        { name: "Positive", color: "#7dce45", values: [30.9, 34.7, 25.7, 29.0, 25.6, 45.1, 37.6] },
      ])}
      <p class="takeaway"><strong>Where groups differ:</strong> C3 (policy critique) is most negative (45.1%), while C6 (student stories) is most positive (45.1%, p = 0.006).</p>
    `) : ""}
  </div>`;
}

// ============================================================================
// 6. TRENDS
// ============================================================================

function step6() {
  const phaseData = {
    all: { label: "All Phases (3,447)", pro: 75.54, anti: 22.98, neu: 1.48 },
    before: { label: "Before (806)", pro: 75.19, anti: 24.57, neu: 0.25 },
    peak: { label: "Peak (1,691)", pro: 75.10, anti: 23.65, neu: 1.24 },
    after: { label: "After (950)", pro: 76.63, anti: 20.42, neu: 2.95 },
  }[state.phase];

  const cMap = (v) => v >= 60 ? { bg: "#fdf2e6", fg: "#9a4706" } : v >= 20 ? { bg: "#eef9e4", fg: "#2e6412" } : { bg: "#f4f6f8", fg: "#4d545e" };

  return `<div class="grid">
    ${storyHeader("Does sounding angry mean opposing CJP, and did support change over time?", "No: 73.5% of Pro-CJP tweets sound negative because supporters are angry about exam leaks. Support stayed steady near 75% across all phases.")}

    ${filterBar([
      { id: "all", label: "All Phases" },
      { id: "before", label: "Before" },
      { id: "peak", label: "Peak" },
      { id: "after", label: "After" },
    ], state.phase, "phase", "X Time Phase")}

    ${card("s4", `
      ${termPill("stance", `X Stance · ${phaseData.label}`)}
      <div class="gauge-wrap">${gauge(phaseData.pro, "g-x-trend")}<div class="gauge-copy"><strong>${phaseData.pro.toFixed(1)}% Pro-CJP</strong><br>${phaseData.anti.toFixed(1)}% Anti-CJP · ${phaseData.neu.toFixed(1)}% Neutral</div></div>
      <p class="takeaway"><strong>Stability:</strong> About 3 in 4 X posts support CJP in every phase.</p>
    `)}

    ${card("s4", `
      ${termPill("stance", "Reddit Stance (2,040)")}
      <div class="gauge-wrap">${gauge(71.23, "g-r-trend")}<div class="gauge-copy"><strong>71.2% Pro-CJP</strong><br>27.8% Anti-CJP · 1.0% Neutral</div></div>
      <p class="takeaway"><strong>Cross-platform:</strong> Reddit also backs CJP (71.2%), with slightly more pushback (27.8%).</p>
    `)}

    ${card("s4", `
      <p class="kicker">Negative Tone Inside Each Side</p>
      ${hbars([
        { label: "Pro-CJP", value: 73.46, text: "73.5% Neg" },
        { label: "Anti-CJP", value: 75.00, text: "75.0% Neg", alt: true },
        { label: "Neutral", value: 52.94, text: "52.9% Neg" },
      ])}
      <p class="takeaway"><strong>Key insight:</strong> Anger does not equal opposition — both sides sound negative.</p>
    `)}

    ${card("s6", `
      <p class="kicker">X Support Across Phases</p>
      ${svgLineChart(["Before", "Peak", "After"], [
        { name: "Pro-CJP (%)", color: "#7dce45", values: [75.19, 75.10, 76.63] },
        { name: "Anti-CJP (%)", color: "#f0a04a", values: [24.57, 23.65, 20.42] },
        { name: "Neutral (%)", color: "#94a3b8", values: [0.25, 1.24, 2.95] },
      ], { min: 0, max: 100, fmt: (v) => `${Math.round(v)}%` })}
      <p class="takeaway"><strong>What happened:</strong> Even as Peak volume jumped 10×, the Pro/Anti split barely moved.</p>
    `)}

    ${card("s6", `
      <p class="kicker">Sentiment × Stance Matrix (%)</p>
      ${heatmapMatrix(
        ["Pro-CJP", "Anti-CJP", "Neutral"],
        ["Negative", "Neutral", "Positive"],
        [
          [{ val: "73.5%", ...cMap(73.5) }, { val: "9.0%", ...cMap(9.0) }, { val: "17.6%", ...cMap(17.6) }],
          [{ val: "75.0%", ...cMap(75.0) }, { val: "3.8%", ...cMap(3.8) }, { val: "21.2%", ...cMap(21.2) }],
          [{ val: "52.9%", ...cMap(52.9) }, { val: "17.7%", ...cMap(17.7) }, { val: "29.4%", ...cMap(29.4) }],
        ]
      )}
      <p class="takeaway"><strong>Proof:</strong> 73.5% of Pro-CJP and 75.0% of Anti-CJP posts are negative — tone and stance are separate.</p>
    `)}

    ${card("s6", `
      <p class="kicker">X Communities by Side (C1–C6)</p>
      ${svgStackedBars(["C1", "C2", "C3", "C4", "C5", "C6", "Other"], [
        { name: "Pro-CJP", color: "#7dce45", values: [71.9, 73.0, 79.6, 54.8, 93.9, 59.8, 75.0] },
        { name: "Neutral", color: "#d5d8df", values: [2.3, 0.9, 3.9, 1.6, 3.1, 0.6, 1.4] },
        { name: "Anti-CJP", color: "#f0a04a", values: [25.8, 26.1, 16.5, 43.6, 3.1, 39.6, 23.7] },
      ])}
      <p class="takeaway"><strong>Where sides sit:</strong> C5 is 93.9% Pro-CJP; C4 (43.6% Anti) and C6 (39.6% Anti) hold more skeptics, yet none are Anti-majority.</p>
    `)}

    ${card("s6", `
      <p class="kicker">Reddit Communities by Side (C1–C6)</p>
      ${svgStackedBars(["C1", "C2", "C3", "C4", "C5", "C6", "Other"], [
        { name: "Pro-CJP", color: "#7dce45", values: [76.2, 64.5, 80.5, 67.0, 76.8, 79.3, 70.0] },
        { name: "Neutral", color: "#d5d8df", values: [0.0, 1.7, 0.0, 0.0, 1.2, 1.2, 1.3] },
        { name: "Anti-CJP", color: "#f0a04a", values: [23.8, 33.9, 19.5, 33.0, 22.0, 19.5, 28.7] },
      ])}
      <p class="takeaway"><strong>Ideological mixing:</strong> Every Reddit group mixes both sides (Pro-CJP ranges from 64.5% to 80.5%).</p>
    `)}
  </div>`;
}

// ============================================================================
// 7. CHECK
// ============================================================================

function step7() {
  return `<div class="grid">
    ${storyHeader("Can we trust our automatic Pro/Anti-CJP labels?", "Before measuring echo chambers, we hand-labeled 180 random posts (90 X, 90 Reddit) and found 86.1% agreement (0.86 F1).")}

    ${card("s4", `
      ${termPill("f1", "Weighted F1 (N = 180)")}
      <h2>0.86</h2>
      <p class="lead">86.1% overall accuracy (155 / 180 matched).</p>
      ${hbars([
        { label: "Anti-CJP", value: 91.55, text: "0.92 F1" },
        { label: "Pro-CJP", value: 84.35, text: "0.84 F1" },
        { label: "Neutral", value: 78.87, text: "0.79 F1", alt: true },
      ])}
      <p class="takeaway"><strong>Result:</strong> High accuracy on Pro and Anti classes validates steps 8–10.</p>
    `)}

    ${card("s8", `
      <p class="kicker">Hand-Label vs. Model Match (N = 180)</p>
      ${heatmapMatrix(
        ["True Pro (67)", "True Anti (72)", "True Neu (41)"],
        ["Pred: Pro", "Pred: Anti", "Pred: Neu"],
        [
          [
            { val: "62", sub: "92.5%", bg: "#dff4d1", fg: "#1d420a" },
            { val: "3", sub: "4.5%", bg: "#f8fafc" },
            { val: "2", sub: "3.0%", bg: "#f8fafc" },
          ],
          [
            { val: "7", sub: "9.7%", bg: "#fdebd8" },
            { val: "65", sub: "90.3%", bg: "#dff4d1", fg: "#1d420a" },
            { val: "0", sub: "0.0%", bg: "#f8fafc" },
          ],
          [
            { val: "11", sub: "26.8%", bg: "#fdebd8" },
            { val: "2", sub: "4.9%", bg: "#f8fafc" },
            { val: "28", sub: "68.3%", bg: "#eef9e4", fg: "#2e6412" },
          ],
        ]
      )}
      <p class="takeaway"><strong>Weakest cell:</strong> Neutral recall (68.3%) because neutral news quotes protest slogans, leaning 11 items toward Pro-CJP.</p>
    `)}
  </div>`;
}

// ============================================================================
// 8. EI
// ============================================================================

function step8() {
  const eiComms = state.platform === "reddit" ? [
    { label: "C1", value: -0.8571 },
    { label: "C2", value: -0.8110 },
    { label: "C3", value: -0.7667 },
    { label: "C4", value: -0.8614 },
    { label: "C5", value: -0.6744 },
    { label: "C6", value: -0.8353 },
    { label: "Overall", value: -0.9381 },
  ] : [
    { label: "C1", value: -0.4308 },
    { label: "C2", value: -0.5077 },
    { label: "C3", value: -0.0097 },
    { label: "C4", value: -0.5781 },
    { label: "C5", value: -0.9231 },
    { label: "C6", value: -0.5868 },
    { label: "Overall", value: -0.7547 },
  ];

  return `<div class="grid">
    ${storyHeader("Do groups talk mostly inside themselves, or across to other groups?", "Both platforms point inward overall (X −0.75, Reddit −0.94), and X tightens over time — except C3, which bridges outward after the march.")}

    ${filterBar([
      { id: "x", label: "X Groups (−0.75)" },
      { id: "reddit", label: "Reddit Groups (−0.94)" },
    ], state.platform === "reddit" ? "reddit" : "x", "platform", "Platform")}

    ${card("s6", `
      ${termPill("ei", `Group E-I Index (${state.platform === "reddit" ? "Reddit" : "X"})`)}
      <div class="legend" style="margin:4px 0 8px"><span><i class="dot g"></i>Inside (−1)</span><span><i class="dot o"></i>Outside (+1)</span></div>
      ${divergingBars(eiComms)}
      <p class="takeaway"><strong>Where it's happening:</strong> ${state.platform === "reddit"
        ? "All Reddit groups stay tightly inside their own threads (−0.67 to −0.86)."
        : "On X, C5 (−0.92) is most isolated, while C3 (−0.01) talks equally inside and outside."}</p>
    `)}

    ${card("s6", `
      <p class="kicker">X E-I Score Over Time</p>
      ${svgLineChart(["Before", "Peak", "After"], [
        { name: "Overall X", color: "#1c1e21", values: [-0.6238, -0.7339, -0.7815] },
        { name: "C1 (Organizers)", color: "#7dce45", values: [-0.1675, -0.3633, -0.5561] },
        { name: "C3 (Legal/Rights)", color: "#f0a04a", values: [0.0303, -0.0933, 0.1636] },
        { name: "Anti-CJP Users", color: "#5eae2e", values: [0.5122, 0.2708, 0.5630] },
      ], { min: -1, max: 0.75 })}
      <p class="takeaway"><strong>Timeline shift:</strong> Network E-I tightens (−0.62 to −0.78), while C3 flips outward (+0.16) in the After phase.</p>
    `)}
  </div>`;
}

// ============================================================================
// 9. MIXING
// ============================================================================

function step9() {
  return `<div class="grid">
    ${storyHeader("Do Pro-CJP and Anti-CJP users actually talk to each other?", "Yes: while Pro-CJP talks mostly inside its majority, Anti-CJP directs 64% (X) and 70% (Reddit) of its ties straight to Pro-CJP.")}

    ${card("s6", `
      ${termPill("mixing", "X Cross-Side Matrix")}
      <h2>64.4% <span style="font-size:14px;font-weight:600;color:var(--muted)">Anti to Pro</span></h2>
      ${heatmapMatrix(
        ["From: Pro", "From: Anti", "From: Neu"],
        ["To: Pro", "To: Anti", "To: Neu"],
        [
          [{ val: "422", sub: "77.6%", bg: "#dff4d1", fg: "#1d420a" }, { val: "92", sub: "16.9%", bg: "#f8fafc" }, { val: "30", sub: "5.5%", bg: "#f8fafc" }],
          [{ val: "261", sub: "64.4%", bg: "#fdebd8", fg: "#9a4706" }, { val: "101", sub: "24.9%", bg: "#eef9e4" }, { val: "43", sub: "10.6%", bg: "#f8fafc" }],
          [{ val: "9", sub: "81.8%", bg: "#f8fafc" }, { val: "2", sub: "18.2%", bg: "#f8fafc" }, { val: "0", sub: "0%", bg: "#f8fafc" }],
        ]
      )}
      <p class="takeaway"><strong>On X:</strong> 261 of 405 Anti-CJP interactions target Pro-CJP accounts directly.</p>
    `)}

    ${card("s6", `
      ${termPill("mixing", "Reddit Cross-Side Matrix")}
      <h2>70.3% <span style="font-size:14px;font-weight:600;color:var(--muted)">Anti to Pro</span></h2>
      ${heatmapMatrix(
        ["From: Pro", "From: Anti", "From: Neu"],
        ["To: Pro", "To: Anti", "To: Neu"],
        [
          [{ val: "1,123", sub: "80.6%", bg: "#dff4d1", fg: "#1d420a" }, { val: "265", sub: "19.0%", bg: "#f8fafc" }, { val: "5", sub: "0.4%", bg: "#f8fafc" }],
          [{ val: "326", sub: "70.3%", bg: "#fdebd8", fg: "#9a4706" }, { val: "137", sub: "29.5%", bg: "#eef9e4" }, { val: "1", sub: "0.2%", bg: "#f8fafc" }],
          [{ val: "13", sub: "81.3%", bg: "#f8fafc" }, { val: "3", sub: "18.8%", bg: "#f8fafc" }, { val: "0", sub: "0%", bg: "#f8fafc" }],
        ]
      )}
      <p class="takeaway"><strong>On Reddit:</strong> 326 of 464 Anti-CJP replies engage Pro-CJP commenters directly.</p>
    `)}

    ${card("s12", `
      <p class="kicker">Stance E-I Comparison</p>
      ${divergingBars([
        { label: "X · Pro", value: -0.6420 },
        { label: "Reddit · Pro", value: -0.6182 },
        { label: "X · Anti", value: 0.4420 },
        { label: "Reddit · Anti", value: 0.4082 },
      ])}
      <p class="takeaway"><strong>Conclusion:</strong> Because Anti-CJP scores positive (+0.44 X, +0.41 Reddit), the two sides are not sealed in separate bubbles.</p>
    `)}
  </div>`;
}

// ============================================================================
// 10. CONTROVERSY
// ============================================================================

function step10() {
  const rwcRows = [
    { label: "Before", value: -0.0704 },
    { label: "Peak", value: 0.1390 },
    { label: "After", value: -0.0692 },
    { label: "X Full", value: 0.0460 },
    { label: "Reddit", value: 0.0313 },
  ];

  return `<div class="grid">
    ${storyHeader("If you start on one side, can you still reach the other side?", "Yes. Random Walk Controversy stays near 0 across all graphs (0.05 X, 0.03 Reddit, 0.14 Peak), proving the sides remain connected.")}

    ${card("s7", `
      ${termPill("rwc", "Random Walk Controversy (RWC)")}
      <h2>0.14 <span style="font-size:14px;font-weight:600;color:var(--muted)">max (X Peak)</span></h2>
      ${divergingBars(rwcRows)}
      <p class="takeaway"><strong>What 0.14 means:</strong> Even at the Peak march, random walks cross easily between Pro and Anti hubs (sealed chambers score near 1.0).</p>
    `)}

    ${card("s5", `
      <p class="kicker">Walker Landing Probabilities</p>
      <table>
        <thead><tr><th>Graph</th><th class="num">Pro to Pro</th><th class="num">Anti to Pro</th><th class="num">RWC</th></tr></thead>
        <tbody>
          <tr><td>X Before</td><td class="num">72.6%</td><td class="num">79.7%</td><td class="num"><span class="rwc-badge">−0.070</span></td></tr>
          <tr><td>X Peak</td><td class="num">66.3%</td><td class="num">52.5%</td><td class="num"><span class="rwc-badge peak">+0.139</span></td></tr>
          <tr><td>X After</td><td class="num">43.2%</td><td class="num">50.1%</td><td class="num"><span class="rwc-badge">−0.069</span></td></tr>
          <tr><td>X Full</td><td class="num">57.4%</td><td class="num">52.8%</td><td class="num"><span class="rwc-badge">+0.046</span></td></tr>
          <tr><td>Reddit Full</td><td class="num">73.2%</td><td class="num">70.0%</td><td class="num"><span class="rwc-badge">+0.031</span></td></tr>
        </tbody>
      </table>
      <p class="takeaway"><strong>Why Before &amp; After are −0.07:</strong> Anti-CJP walks cross into Pro-CJP hubs over 50% of the time.</p>
    `)}
  </div>`;
}

// ============================================================================
// 11. THEMES
// ============================================================================

function step11() {
  const topics = [
    { name: "Street protest", count: "2,572", words: "jantar mantar, wangchuk, police, delhi" },
    { name: "Hashtag campaign", count: "382", words: "sonamwangchuk, dharmendrapradhan, neetpaperleak" },
    { name: "Education minister", count: "335", words: "dharmendra pradhan, minister, education" },
    { name: "Video & media", count: "330", words: "video, media, viral" },
    { name: "BJP & Congress", count: "303", words: "bjp, opposition, congress, modi" },
    { name: "Organizer accounts", count: "224", words: "abhijeetdipke, jantarmantar, rahulgandhi" },
  ];

  const showX = state.platform === "all" || state.platform === "x";
  const showR = state.platform === "all" || state.platform === "reddit";

  return `<div class="grid">
    ${storyHeader("Are the groups talking about completely different topics?", "No — both platforms share the same core grievance (the Jantar Mantar street protest), with only X's C5 focusing on hashtag campaigning.")}

    ${filterBar([
      { id: "all", label: "Both Platforms" },
      { id: "x", label: "X (Twitter)" },
      { id: "reddit", label: "Reddit" },
    ], state.platform, "platform", "Platform")}

    ${card("s6", `
      ${termPill("js", "X Topic Distance (JS)")}
      <h2>0.40 <span style="font-size:14px;font-weight:600;color:var(--muted)">vs. 0.19 random</span></h2>
      <p class="takeaway"><strong>Widest pair:</strong> C5 vs. C6 (0.66) because C5 is a hashtag campaign while C6 discusses the street protest.</p>
    `)}

    ${card("s6", `
      ${termPill("js", "Reddit Topic Distance (JS)")}
      <h2>0.29 <span style="font-size:14px;font-weight:600;color:var(--muted)">vs. 0.22 random</span></h2>
      <p class="takeaway"><strong>Closer together:</strong> Every Reddit community spends 49%–74% of posts on the same street protest.</p>
    `)}

    ${showX ? card("s6", `
      <p class="kicker">X Topics by Group (C1–C6)</p>
      ${svgStackedBars(["C1", "C2", "C3", "C4", "C5", "C6"], [
        { name: "Street protest", color: "#7dce45", values: [50.4, 36.9, 39.0, 50.0, 23.0, 51.9] },
        { name: "Hashtag campaign", color: "#f0a04a", values: [13.9, 7.2, 11.0, 9.7, 55.7, 1.3] },
        { name: "Other 9 themes", color: "#d5d8df", values: [35.7, 55.9, 50.0, 40.3, 21.3, 46.8] },
      ])}
      <p class="takeaway"><strong>Key outlier:</strong> C5 is 55.7% hashtag campaigning; C1, C4, and C6 center on Jantar Mantar.</p>
    `) : ""}

    ${showR ? card("s6", `
      <p class="kicker">Reddit Topics by Group (C1–C6)</p>
      ${svgStackedBars(["C1", "C2", "C3", "C4", "C5", "C6"], [
        { name: "Street protest", color: "#7dce45", values: [68.2, 68.9, 48.8, 60.7, 69.1, 73.9] },
        { name: "Video & media", color: "#c6e86a", values: [14.6, 15.6, 12.8, 10.1, 13.2, 5.8] },
        { name: "Other 9 themes", color: "#d5d8df", values: [17.2, 15.5, 38.4, 29.2, 17.7, 20.3] },
      ])}
      <p class="takeaway"><strong>Shared topic:</strong> Street protest leads in all 6 Reddit groups, followed by video &amp; media.</p>
    `) : ""}

    ${showX ? card("s6", `
      <p class="kicker">X Topics Over Time</p>
      ${svgLineChart(["Before", "Peak", "After"], [
        { name: "Street protest (%)", color: "#7dce45", values: [50.0, 45.4, 40.6] },
        { name: "Hashtag campaign (%)", color: "#f0a04a", values: [6.9, 10.1, 14.5] },
        { name: "Education minister (%)", color: "#5eae2e", values: [8.1, 9.5, 9.0] },
        { name: "BJP & Congress (%)", color: "#8b919a", values: [6.7, 9.1, 7.3] },
      ], { min: 0, max: 60, fmt: (v) => `${Math.round(v)}%` })}
      <p class="takeaway"><strong>Stability:</strong> Topics stay steady across phases; hashtag campaigning rises slightly from 6.9% to 14.5%.</p>
    `) : ""}

    ${card("s6", `
      <p class="kicker">Top Themes (Post Counts)</p>
      ${hbars(topics.map((t, i) => ({ label: t.name, value: Number(t.count.replace(",", "")), text: t.count, alt: i === 1, tip: `${t.name}: ${t.words}` })), true)}
      <p class="takeaway"><strong>Overall:</strong> 2,572 posts center on the Jantar Mantar street protest — one shared grievance.</p>
    `)}
  </div>`;
}

// ============================================================================
// CONCLUSION
// ============================================================================

function conclusion() {
  return `<div class="grid">
    ${card("s8", `
      <p class="kicker">Key Findings Across 11 Steps</p>
      <div class="stat-list" style="margin-top:8px">
        <article style="display:flex;justify-content:space-between;align-items:center;gap:16px">
          <div>
            <h3 style="margin:0">Groups point inward, yet sides still meet</h3>
            <p class="lead" style="margin:4px 0 0">Anti-CJP users direct 64.4% (X) and 70.3% (Reddit) of ties straight to Pro-CJP.</p>
          </div>
          <div style="text-align:right;flex:none"><b style="font-size:20px;color:var(--green-deep)">−0.75 / −0.94</b><br><span style="font-size:11.5px;color:var(--muted)">E-I Index</span></div>
        </article>
        <article style="display:flex;justify-content:space-between;align-items:center;gap:16px">
          <div>
            <h3 style="margin:0">Angry tone does not mean opposition</h3>
            <p class="lead" style="margin:4px 0 0">73.5% of Pro-CJP tweets sound negative due to exam-leak outrage; support stays near 75%.</p>
          </div>
          <div style="text-align:right;flex:none"><b style="font-size:20px">75.5%</b><br><span style="font-size:11.5px;color:var(--muted)">Pro-CJP (0.86 F1)</span></div>
        </article>
        <article style="display:flex;justify-content:space-between;align-items:center;gap:16px">
          <div>
            <h3 style="margin:0">Both platforms share one street protest</h3>
            <p class="lead" style="margin:4px 0 0">Random walks cross freely between sides, and every cluster centers on Jantar Mantar.</p>
          </div>
          <div style="text-align:right;flex:none"><b style="font-size:20px;color:#b85c0b">0.05 / 0.03</b><br><span style="font-size:11.5px;color:var(--muted)">RWC (0.14 Peak)</span></div>
        </article>
      </div>
    `)}

    ${card("s4 green-card", `
      <p class="kicker">The Bottom Line</p>
      <h2 style="font-size:24px;line-height:1.2;margin-top:8px">No pure echo chambers.</h2>
      <p class="lead" style="margin-top:12px">Communities cluster tightly, but opposing voices keep debating each other around one shared grievance.</p>
    `)}

    ${card("s12", `
      <p class="kicker">Future Scope</p>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:8px">
        <div class="mini">
          <span>1 · Newer CJP Protests</span>
          <b style="font-size:14.5px;margin-top:4px">Track Repeat Waves</b>
          <p class="note" style="margin-top:4px">Test if cross-side debate holds up in newer CJP protests after June–July.</p>
        </div>
        <div class="mini">
          <span>2 · Broader Dataset</span>
          <b style="font-size:14.5px;margin-top:4px">More Platforms</b>
          <p class="note" style="margin-top:4px">Expand beyond 5,487 posts with Instagram, YouTube, and regional languages.</p>
        </div>
        <div class="mini">
          <span>3 · Deeper Study</span>
          <b style="font-size:14.5px;margin-top:4px">User &amp; Bridge Shifts</b>
          <p class="note" style="margin-top:4px">Track individual stance shifts and how bridge groups like C3 connect sides.</p>
        </div>
      </div>
    `)}
  </div>`;
}

// ============================================================================
// ROUTING, LIGHTBOX, TOOLTIPS, DEFINITIONS, COLLAPSE & FILTERS
// ============================================================================

const VIEWS = {
  overview, 1: step1, 2: step2, 3: step3, 4: step4, 5: step5, 6: step6, 7: step7, 8: step8, 9: step9, 10: step10, 11: step11, conclusion,
};

const nav = document.getElementById("nav");
const stage = document.getElementById("stage");
const title = document.getElementById("title");
const crumb = document.getElementById("crumb");
let currentId = "overview";

const tipEl = document.createElement("div");
tipEl.className = "chart-tooltip";
document.body.appendChild(tipEl);

function bindStageInteractions() {
  stage.querySelectorAll("[data-def]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const k = btn.dataset.def;
      state.openDef = state.openDef === k ? null : k;
      renderCurrent();
    });
  });

  stage.querySelectorAll("[data-lb-src]").forEach((el) => {
    el.addEventListener("click", () => {
      document.getElementById("lb-img").src = el.dataset.lbSrc;
      document.getElementById("lb-img").alt = el.dataset.lbTitle;
      document.getElementById("lb-title").textContent = el.dataset.lbTitle;
      document.getElementById("lb-tag").textContent = el.dataset.lbTag;
      document.getElementById("lb-cap").textContent = el.dataset.lbCap;
      document.getElementById("lightbox").hidden = false;
    });
  });

  stage.querySelectorAll("[data-platform]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.platform = btn.dataset.platform;
      renderCurrent();
    });
  });

  stage.querySelectorAll("[data-phase]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.phase = btn.dataset.phase;
      renderCurrent();
    });
  });

  stage.querySelectorAll("[data-nettab]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.netTab = btn.dataset.nettab;
      renderCurrent();
    });
  });

  // Inline + / - / Reset zoom & drag-pan for network viewports
  const zoomState = {};
  const applyZoom = (id) => {
    const z = zoomState[id] || { scale: 1, x: 0, y: 0 };
    const el = document.getElementById(`zoom-${id}`);
    if (el) el.style.transform = `translate(${z.x}px, ${z.y}px) scale(${z.scale})`;
  };

  stage.querySelectorAll("[data-zoom-target]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const id = btn.dataset.zoomTarget;
      const dir = btn.dataset.zoomDir;
      const z = zoomState[id] || (zoomState[id] = { scale: 1, x: 0, y: 0 });
      if (dir === "in") z.scale = Math.min(3.5, +(z.scale + 0.35).toFixed(2));
      else if (dir === "out") z.scale = Math.max(0.7, +(z.scale - 0.35).toFixed(2));
      else { z.scale = 1; z.x = 0; z.y = 0; }
      applyZoom(id);
    });
  });

  stage.querySelectorAll("[data-zoom-box]").forEach((box) => {
    const id = box.dataset.zoomBox;
    let dragging = false, sx = 0, sy = 0;
    box.addEventListener("mousedown", (e) => {
      if (e.target.closest(".zoom-controls")) return;
      dragging = true;
      const z = zoomState[id] || (zoomState[id] = { scale: 1, x: 0, y: 0 });
      sx = e.clientX - z.x;
      sy = e.clientY - z.y;
    });
    window.addEventListener("mousemove", (e) => {
      if (!dragging) return;
      const z = zoomState[id] || (zoomState[id] = { scale: 1, x: 0, y: 0 });
      z.x = e.clientX - sx;
      z.y = e.clientY - sy;
      applyZoom(id);
    });
    window.addEventListener("mouseup", () => { dragging = false; });
  });

  stage.querySelectorAll("[data-tip]").forEach((el) => {
    el.addEventListener("mouseenter", (e) => {
      tipEl.textContent = el.dataset.tip;
      tipEl.style.display = "block";
      positionTip(e);
    });
    el.addEventListener("mousemove", positionTip);
    el.addEventListener("mouseleave", () => {
      tipEl.style.display = "none";
    });
  });
}

function positionTip(e) {
  const pad = 12;
  let x = e.clientX + pad;
  let y = e.clientY + pad;
  if (x + 250 > window.innerWidth) x = e.clientX - 250;
  if (y + 80 > window.innerHeight) y = e.clientY - 70;
  tipEl.style.left = `${x}px`;
  tipEl.style.top = `${y}px`;
}

function renderCurrent() {
  const view = VIEWS[currentId] || overview;
  const [heading, eyebrow] = TITLES_STEPS[currentId] || TITLES_STEPS.overview;
  title.textContent = heading;
  crumb.textContent = eyebrow;
  stage.innerHTML = view();
  tipEl.style.display = "none";
  bindStageInteractions();
}

function show(id) {
  currentId = VIEWS[id] ? String(id) : "overview";
  state.openDef = null;
  if (currentId === "8" && state.platform === "all") state.platform = "x";
  renderCurrent();
  [...nav.children].forEach((button) => {
    button.classList.toggle("active", button.dataset.id === currentId);
  });
  history.replaceState(null, "", `#${currentId}`);
  document.querySelector("main").scrollTop = 0;
}

STEPS.forEach((step) => {
  const button = document.createElement("button");
  button.dataset.id = step.id;
  button.title = step.label;
  button.innerHTML = `<span class="n">${stepIcon(step.id)}</span><span class="lbl">${step.label}</span>`;
  button.addEventListener("click", () => show(step.id));
  nav.appendChild(button);
});

const shellEl = document.querySelector(".shell");
const collapseBtn = document.getElementById("collapse-btn");
if (collapseBtn && shellEl) {
  collapseBtn.addEventListener("click", () => {
    const isCollapsed = shellEl.classList.toggle("collapsed");
    collapseBtn.setAttribute("aria-expanded", String(!isCollapsed));
    collapseBtn.title = isCollapsed ? "Expand sidebar" : "Collapse sidebar";
    collapseBtn.querySelector(".c-ico").textContent = isCollapsed ? "»" : "«";
  });
}

document.getElementById("find").addEventListener("input", (event) => {
  const query = event.target.value.trim().toLowerCase();
  [...nav.children].forEach((button) => {
    button.hidden = query.length > 0 && !button.textContent.toLowerCase().includes(query);
  });
});

function closeLightbox() {
  document.getElementById("lightbox").hidden = true;
}
document.getElementById("lb-close").addEventListener("click", closeLightbox);
document.getElementById("lb-close-bg").addEventListener("click", closeLightbox);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeLightbox();
});

const start = location.hash.replace("#", "");
if (VIEWS[start]) show(start);
else show("overview");
