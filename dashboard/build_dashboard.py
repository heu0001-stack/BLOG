"""
Reads metrics.json and generates dashboard.html (a self-contained page with
embedded data + hand-rolled SVG charts, no external libraries).
Re-run this after editing metrics.json, then publish dashboard.html.
"""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).parent
DATA = json.loads((ROOT / "metrics.json").read_text(encoding="utf-8"))
PDF_PATH = ROOT.parent / "content" / "products" / "자취시작_플래너.pdf"
PDF_B64 = base64.b64encode(PDF_PATH.read_bytes()).decode("ascii")

HTML_TEMPLATE = r"""<title>가전픽 수익화 대시보드</title>
<style>
.viz-root {
  color-scheme: light;
  --surface-1: #fcfcfb;
  --page: #f9f9f7;
  --text-primary: #0b0b0b;
  --text-secondary: #52514e;
  --text-muted: #898781;
  --grid: #e1e0d9;
  --axis: #c3c2b7;
  --border: rgba(11,11,11,0.10);
  --series-1: #2a78d6; /* blog */
  --series-2: #eb6834; /* naver */
  --series-3: #1baf7a; /* shorts */
  --series-4: #eda100; /* shorts subs */
  --good: #006300;
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) .viz-root {
    color-scheme: dark;
    --surface-1: #1a1a19;
    --page: #0d0d0d;
    --text-primary: #ffffff;
    --text-secondary: #c3c2b7;
    --text-muted: #898781;
    --grid: #2c2c2a;
    --axis: #383835;
    --border: rgba(255,255,255,0.10);
    --series-1: #3987e5;
    --series-2: #d95926;
    --series-3: #199e70;
    --series-4: #c98500;
    --good: #0ca30c;
  }
}
:root[data-theme="dark"] .viz-root {
  color-scheme: dark;
  --surface-1: #1a1a19;
  --page: #0d0d0d;
  --text-primary: #ffffff;
  --text-secondary: #c3c2b7;
  --text-muted: #898781;
  --grid: #2c2c2a;
  --axis: #383835;
  --border: rgba(255,255,255,0.10);
  --series-1: #3987e5;
  --series-2: #d95926;
  --series-3: #199e70;
  --series-4: #c98500;
  --good: #0ca30c;
}
* { box-sizing: border-box; }
body { margin: 0; }
.viz-root {
  background: var(--page);
  color: var(--text-primary);
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  padding: 24px 16px 64px;
}
.wrap { max-width: 980px; margin: 0 auto; }
h1 { font-size: 22px; margin: 0 0 4px; }
.sub { color: var(--text-secondary); font-size: 14px; margin: 0 0 24px; }
.card {
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  overflow-x: auto;
}
.card h2 { font-size: 15px; margin: 0 0 2px; }
.card .desc { color: var(--text-secondary); font-size: 13px; margin: 0 0 12px; }
.hero-row { display: flex; gap: 24px; flex-wrap: wrap; align-items: baseline; margin-bottom: 8px; }
.hero-figure { font-size: 40px; font-weight: 600; }
.hero-label { color: var(--text-secondary); font-size: 13px; }
.hero-delta { font-size: 13px; color: var(--text-secondary); }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
@media (max-width: 720px) { .grid3 { grid-template-columns: 1fr; } }
.legend { display: flex; gap: 16px; flex-wrap: wrap; font-size: 12px; color: var(--text-secondary); margin-top: 8px; }
.legend-item { display: flex; align-items: center; gap: 6px; }
.legend-swatch { width: 14px; height: 2px; border-radius: 1px; }
.legend-swatch.dash { background: repeating-linear-gradient(90deg, currentColor 0 4px, transparent 4px 7px); height: 2px; }
.tooltip {
  position: absolute; pointer-events: none; z-index: 5;
  background: var(--surface-1); border: 1px solid var(--border); border-radius: 8px;
  padding: 8px 10px; font-size: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  opacity: 0; transition: opacity 0.08s;
  white-space: nowrap;
}
.tooltip .t-week { color: var(--text-secondary); margin-bottom: 4px; }
.tooltip .t-row { display: flex; justify-content: space-between; gap: 12px; }
.tooltip .t-val { font-weight: 600; }
.chart-holder { position: relative; }
table.data-table { border-collapse: collapse; width: 100%; font-size: 12px; font-variant-numeric: tabular-nums; }
table.data-table th, table.data-table td { border-bottom: 1px solid var(--grid); padding: 6px 8px; text-align: right; white-space: nowrap; }
table.data-table th:first-child, table.data-table td:first-child { text-align: left; }
table.data-table th { color: var(--text-secondary); font-weight: 500; }
details summary { cursor: pointer; font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
.note { font-size: 12px; color: var(--text-muted); line-height: 1.6; margin-top: 12px; }
.gate-badge { display: inline-block; font-size: 11px; background: var(--grid); color: var(--text-secondary); border-radius: 999px; padding: 2px 8px; margin-left: 6px; }
.status-badge { display: inline-block; font-size: 11px; font-weight: 600; border-radius: 999px; padding: 3px 10px; }
.status-active { background: color-mix(in srgb, var(--good) 18%, transparent); color: var(--good); }
.status-waiting { background: color-mix(in srgb, var(--series-4) 22%, transparent); color: var(--text-primary); }
.status-paused { background: var(--grid); color: var(--text-secondary); }
.tabs { display: flex; gap: 4px; margin-bottom: 20px; border-bottom: 1px solid var(--border); }
.tab-btn { appearance: none; border: none; background: transparent; font: inherit; font-size: 14px; font-weight: 600;
  color: var(--text-secondary); padding: 10px 16px; cursor: pointer; border-bottom: 2px solid transparent; }
.tab-btn.active { color: var(--series-1); border-bottom-color: var(--series-1); }
.tab-panel { display: none; }
.tab-panel.active { display: block; }
.status-row { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--grid); }
.status-row:last-child { border-bottom: none; }
.status-name { font-weight: 600; font-size: 14px; }
.status-detail { color: var(--text-secondary); font-size: 12.5px; margin-top: 3px; line-height: 1.5; }
.roadmap-item { display: flex; gap: 14px; padding: 10px 0; border-bottom: 1px solid var(--grid); }
.roadmap-item:last-child { border-bottom: none; }
.roadmap-when { flex: 0 0 130px; font-weight: 600; font-size: 12.5px; color: var(--series-1); }
.roadmap-task { font-size: 13px; color: var(--text-primary); line-height: 1.5; }
.status-details summary { list-style: none; cursor: pointer; }
.status-details summary::-webkit-details-marker { display: none; }
.status-details summary .status-row { border-bottom: none; }
.status-details { border-bottom: 1px solid var(--grid); }
.status-details:last-child { border-bottom: none; }
.status-details summary::after {
  content: "펼치기 ▸"; display: block; font-size: 11px; color: var(--series-1); margin-top: -6px; padding-bottom: 10px;
}
.status-details[open] summary::after { content: "접기 ▾"; }
.content-list-wrap { padding: 0 0 14px; }
.sched-list { list-style: none; margin: 0; padding: 0; }
.sched-item { display: flex; align-items: baseline; gap: 10px; padding: 6px 0; font-size: 12.5px; border-bottom: 1px dashed var(--grid); }
.sched-item:last-child { border-bottom: none; }
.sched-check { flex: 0 0 16px; color: var(--text-muted); }
.sched-item.sched-done .sched-check { color: var(--good); }
.sched-date { flex: 0 0 78px; font-variant-numeric: tabular-nums; color: var(--text-secondary); }
.sched-item.sched-done .sched-date { color: var(--good); font-weight: 600; }
.sched-title { color: var(--text-primary); }
.sched-item.sched-done .sched-title { color: var(--text-secondary); text-decoration: line-through; text-decoration-color: var(--grid); }
.filter-chip {
  appearance: none; border: 1px solid var(--border); background: var(--surface-1); border-radius: 999px;
  padding: 4px 10px 4px 4px; display: flex; align-items: center; gap: 6px; font: inherit; font-size: 12px;
  color: var(--text-secondary); cursor: pointer;
}
.filter-chip:hover { border-color: var(--axis); }
.filter-chip.active { border-color: var(--series-1); background: color-mix(in srgb, var(--series-1) 10%, var(--surface-1)); color: var(--text-primary); }
.preview-table { margin: 4px 0 14px; }
.preview-table td, .preview-table th { text-align: left; }
</style>

<div class="viz-root">
  <div class="wrap">
    <h1>가전픽 리뷰 - 수익화 성장 대시보드</h1>
    <p class="sub">Blogger·네이버블로그·디지털상품(쇼츠는 보류), 계획 대비 실제 누적수익 추적. 매주 1회 갱신.</p>

    <div class="tabs">
      <button class="tab-btn active" data-tab="status">작업현황 &amp; 일정</button>
      <button class="tab-btn" data-tab="growth">성장 대시보드</button>
    </div>

    <div class="tab-panel" id="tab-growth">
    <div class="card" id="hero-card">
      <h2>누적 총수익 (목표 ₩__GOAL__)</h2>
      <p class="desc">음영: 비관~낙관 추정 범위 · 점선: 현실 시나리오 계획 · 실선: 실제 누적수익</p>
      <div class="hero-row">
        <div>
          <div class="hero-figure" id="hero-figure">₩0</div>
          <div class="hero-label">현재까지 실제 누적수익</div>
        </div>
        <div class="hero-delta" id="hero-delta"></div>
      </div>
      <div class="chart-holder"><svg id="hero-chart" width="100%" height="260"></svg></div>
      <div class="legend">
        <div class="legend-item"><span class="legend-swatch" style="background:var(--series-1);opacity:.18;width:14px;height:10px;"></span>비관~낙관 범위</div>
        <div class="legend-item"><span class="legend-swatch dash" style="color:var(--series-1)"></span>현실 계획</div>
        <div class="legend-item"><span class="legend-swatch" style="background:var(--series-1)"></span>실제</div>
      </div>
    </div>

    <div class="grid3" id="channel-charts"></div>

    <div class="card">
      <h2>주차별 데이터 입력 / 표로 보기</h2>
      <p class="desc">매주 각 채널의 실제 방문자·조회수·매출을 알려주시면 이 표와 위 차트가 갱신됩니다.</p>
      <details open>
        <summary>전체 데이터 표 펼치기/접기</summary>
        <div id="table-holder"></div>
      </details>
      <p class="note">__NOTE_ADPOST__<br>__NOTE_DISCLAIMER__</p>
    </div>
    </div>

    <div class="tab-panel active" id="tab-status">
      <div class="card">
        <h2>진행 중인 작업</h2>
        <p class="desc">최근 갱신: __LAST_UPDATED__</p>
        <div class="legend" id="status-filter-bar" style="margin-bottom:10px;">
          <button class="filter-chip" data-status="운영중"><span class="status-badge status-active">운영중</span><span>실제로 돌아가는 중</span></button>
          <button class="filter-chip" data-status="대기중"><span class="status-badge status-waiting">대기중</span><span>사람의 다음 행동 필요</span></button>
          <button class="filter-chip" data-status="보류"><span class="status-badge status-paused">보류</span><span>지시로 중단, 코드는 보존</span></button>
        </div>
        <div id="status-list"></div>
      </div>
      <div class="card">
        <h2>작업 예정 일정</h2>
        <div id="roadmap-list"></div>
      </div>

      <div class="card">
        <details class="status-details" open>
          <summary>
            <div class="status-row">
              <div>
                <div class="status-name">디지털 상품 — 자취시작 플래너.pdf</div>
                <div class="status-detail">커버 + 4개 섹션, 쿠팡 링크 클릭 가능. 아래 버튼으로 바로 다운로드하세요.</div>
              </div>
            </div>
          </summary>
        <div class="content-list-wrap">
          <button id="pdf-download-btn" class="filter-chip" style="padding:8px 16px;">
            <span>⬇ PDF 다운로드</span>
          </button>
          <span id="pdf-download-status" style="font-size:12px;color:var(--text-secondary);margin-left:8px;"></span>

          <div class="content-group-name" style="margin-top:14px;">표지</div>
          <p style="font-size:12.5px;color:var(--text-secondary);margin:0 0 4px;">"자취 시작 플래너" — 이사 체크리스트부터 예산 관리, 가전 구매 우선순위까지 한 권으로.</p>

          <div class="content-group-name">01. 이사 체크리스트</div>
          <p style="font-size:12.5px;margin:0 0 4px;">입주 전 / 입주 후 / 가전·생활 3단계, 체크박스형. 전입신고·확정일자 안내 포함.</p>

          <div class="content-group-name">02. 월 예산 관리표</div>
          <p style="font-size:12.5px;margin:0 0 4px;">수입 / 지출(예산 vs 실제) 표. 카드 결제일 분리 관리 팁 포함.</p>

          <div class="content-group-name">03. 고정비 · 저축 관리</div>
          <p style="font-size:12.5px;margin:0 0 4px;">결제일순 고정비 표 + 저축 목표 트래커.</p>

          <div class="content-group-name">04. 가전 구매 우선순위</div>
          <p style="font-size:12.5px;margin:0;">순위별 카드 레이아웃, 각 항목에 실제 쿠팡 제품 링크 연결.</p>
        </div>
        </details>
      </div>
    </div>
  </div>
  <div class="tooltip" id="tooltip"></div>
</div>

<script>
const DATA = __DATA_JSON__;
const PDF_B64 = "__PDF_B64__";
let statusFilter = '운영중';

function base64ToBytes(b64) {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

const pdfBtn = document.getElementById('pdf-download-btn');
if (pdfBtn) {
  pdfBtn.addEventListener('click', async () => {
    const statusEl = document.getElementById('pdf-download-status');
    statusEl.textContent = '';
    const downloads = await claude.use('downloads');
    if (!downloads) { statusEl.textContent = '이 화면에서는 다운로드를 지원하지 않습니다.'; return; }
    try {
      const bytes = base64ToBytes(PDF_B64);
      await downloads.save({ filename: '자취시작_플래너.pdf', data: bytes });
      statusEl.textContent = '다운로드 완료 ✓';
    } catch (e) {
      statusEl.textContent = '다운로드 실패: ' + (e && e.code ? e.code : String(e));
    }
  });
}
const tooltip = document.getElementById('tooltip');
const fmtWon = n => n === null || n === undefined ? '-' : '₩' + n.toLocaleString('ko-KR');
const fmtNum = n => n === null || n === undefined ? '-' : n.toLocaleString('ko-KR');

function svgns(tag) { return document.createElementNS('http://www.w3.org/2000/svg', tag); }

function lastActualIndex(arr) {
  let idx = -1;
  arr.forEach((v, i) => { if (v !== null && v !== undefined) idx = i; });
  return idx;
}

function pathFromSeries(values, xScale, yScale, uptoIdx) {
  const pts = [];
  for (let i = 0; i <= uptoIdx; i++) {
    if (values[i] === null || values[i] === undefined) continue;
    pts.push([xScale(i), yScale(values[i])]);
  }
  if (!pts.length) return '';
  return 'M' + pts.map(p => p[0].toFixed(1) + ',' + p[1].toFixed(1)).join('L');
}

function drawChart(svgEl, opts) {
  // opts: {weekLabels, band:{lo,hi,color}?, lines:[{data,color,dash,upto}], yFmt, height}
  const width = svgEl.clientWidth || 600;
  const height = opts.height || 240;
  const padL = 46, padR = 12, padT = 12, padB = 24;
  const innerW = width - padL - padR, innerH = height - padT - padB;
  svgEl.setAttribute('viewBox', `0 0 ${width} ${height}`);
  svgEl.innerHTML = '';

  const n = opts.weekLabels.length;
  const xScale = i => padL + (innerW * i / (n - 1));
  let maxV = 1;
  const allVals = [];
  if (opts.band) { allVals.push(...opts.band.hi.filter(v => v !== null)); }
  opts.lines.forEach(l => allVals.push(...l.data.filter(v => v !== null && v !== undefined)));
  maxV = Math.max(1, ...allVals) * 1.12;
  const yScale = v => padT + innerH - (innerH * v / maxV);

  // gridlines (4 steps)
  const gGrid = svgns('g');
  for (let s = 0; s <= 4; s++) {
    const v = maxV * s / 4;
    const y = yScale(v);
    const line = svgns('line');
    line.setAttribute('x1', padL); line.setAttribute('x2', width - padR);
    line.setAttribute('y1', y); line.setAttribute('y2', y);
    line.setAttribute('stroke', 'var(--grid)'); line.setAttribute('stroke-width', '1');
    gGrid.appendChild(line);
    const label = svgns('text');
    label.setAttribute('x', padL - 8); label.setAttribute('y', y + 4);
    label.setAttribute('text-anchor', 'end'); label.setAttribute('font-size', '10');
    label.setAttribute('fill', 'var(--text-muted)');
    label.textContent = opts.yFmt ? opts.yFmt(Math.round(v)) : Math.round(v);
    gGrid.appendChild(label);
  }
  svgEl.appendChild(gGrid);

  // x axis labels (every 2nd week)
  for (let i = 0; i < n; i += 2) {
    const t = svgns('text');
    t.setAttribute('x', xScale(i)); t.setAttribute('y', height - 6);
    t.setAttribute('text-anchor', 'middle'); t.setAttribute('font-size', '10');
    t.setAttribute('fill', 'var(--text-muted)');
    t.textContent = 'W' + (i + 1);
    svgEl.appendChild(t);
  }

  // band
  if (opts.band) {
    const pts = [];
    for (let i = 0; i < n; i++) pts.push([xScale(i), yScale(opts.band.hi[i])]);
    for (let i = n - 1; i >= 0; i--) pts.push([xScale(i), yScale(opts.band.lo[i])]);
    const poly = svgns('polygon');
    poly.setAttribute('points', pts.map(p => p.join(',')).join(' '));
    poly.setAttribute('fill', opts.band.color);
    poly.setAttribute('opacity', '0.14');
    svgEl.appendChild(poly);
  }

  // lines
  opts.lines.forEach(l => {
    const upto = l.upto !== undefined ? l.upto : n - 1;
    const d = pathFromSeries(l.data, xScale, yScale, upto);
    if (!d) return;
    const path = svgns('path');
    path.setAttribute('d', d);
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', l.color);
    path.setAttribute('stroke-width', '2');
    path.setAttribute('stroke-linecap', 'round');
    path.setAttribute('stroke-linejoin', 'round');
    if (l.dash) path.setAttribute('stroke-dasharray', '5,4');
    svgEl.appendChild(path);
    // end dot
    let lastI = -1;
    for (let i = 0; i <= upto; i++) if (l.data[i] !== null && l.data[i] !== undefined) lastI = i;
    if (lastI >= 0) {
      const dot = svgns('circle');
      dot.setAttribute('cx', xScale(lastI)); dot.setAttribute('cy', yScale(l.data[lastI]));
      dot.setAttribute('r', 4); dot.setAttribute('fill', l.color);
      dot.setAttribute('stroke', 'var(--surface-1)'); dot.setAttribute('stroke-width', '2');
      svgEl.appendChild(dot);
    }
  });

  // crosshair + tooltip layer
  const hitRect = svgns('rect');
  hitRect.setAttribute('x', padL); hitRect.setAttribute('y', padT);
  hitRect.setAttribute('width', innerW); hitRect.setAttribute('height', innerH);
  hitRect.setAttribute('fill', 'transparent');
  const crosshair = svgns('line');
  crosshair.setAttribute('y1', padT); crosshair.setAttribute('y2', padT + innerH);
  crosshair.setAttribute('stroke', 'var(--axis)'); crosshair.setAttribute('stroke-width', '1');
  crosshair.style.display = 'none';
  svgEl.appendChild(crosshair);
  svgEl.appendChild(hitRect);

  hitRect.addEventListener('pointermove', ev => {
    const rect = svgEl.getBoundingClientRect();
    const scaleX = width / rect.width;
    const mx = (ev.clientX - rect.left) * scaleX;
    let idx = Math.round((mx - padL) / innerW * (n - 1));
    idx = Math.max(0, Math.min(n - 1, idx));
    crosshair.style.display = '';
    crosshair.setAttribute('x1', xScale(idx)); crosshair.setAttribute('x2', xScale(idx));

    let rows = '';
    opts.lines.forEach(l => {
      const v = l.data[idx];
      rows += `<div class="t-row"><span>${l.name}</span><span class="t-val" style="color:${l.color}">${opts.yFmt ? opts.yFmt(v) : fmtNum(v)}</span></div>`;
    });
    tooltip.innerHTML = `<div class="t-week">${opts.weekLabels[idx]}</div>${rows}`;
    tooltip.style.opacity = '1';
    tooltip.style.left = (ev.clientX + 14) + 'px';
    tooltip.style.top = (ev.clientY + 14) + 'px';
  });
  hitRect.addEventListener('pointerleave', () => {
    crosshair.style.display = 'none';
    tooltip.style.opacity = '0';
  });
}

function render() {
  const weeks = DATA.weeks;
  const weekLabels = weeks.map(w => `W${w.week} · ${w.week_start}`);
  const totals = DATA.total_revenue_krw;
  const lastActual = lastActualIndex(totals.actual_cum);

  document.getElementById('hero-figure').textContent = fmtWon(lastActual >= 0 ? totals.actual_cum[lastActual] : 0);
  if (lastActual >= 0) {
    const plan = totals.plan_realistic_cum[lastActual];
    const actual = totals.actual_cum[lastActual];
    const diff = actual - plan;
    const pct = plan ? Math.round(diff / plan * 100) : 0;
    document.getElementById('hero-delta').innerHTML =
      `${weekLabels[lastActual]} 기준 · 계획 대비 <span style="color:${diff >= 0 ? 'var(--good)' : 'var(--series-2)'}">${diff >= 0 ? '+' : ''}${fmtWon(diff)} (${diff>=0?'+':''}${pct}%)</span>`;
  } else {
    document.getElementById('hero-delta').textContent = '아직 실제 데이터 입력 전 — 계획선만 표시됩니다.';
  }

  drawChart(document.getElementById('hero-chart'), {
    weekLabels, height: 260, yFmt: fmtWon,
    band: { lo: totals.plan_pessimistic_cum, hi: totals.plan_optimistic_cum, color: 'var(--series-1)' },
    lines: [
      { name: '현실 계획', data: totals.plan_realistic_cum, color: 'var(--series-1)', dash: true },
      { name: '실제', data: totals.actual_cum, color: 'var(--series-1)', dash: false },
    ],
  });

  const container = document.getElementById('channel-charts');
  container.innerHTML = '';
  const chOrder = ['blog_blogger', 'blog_naver', 'digital_product'];
  const trafficMetricByKey = { digital_product: 'units_sold' };
  const trafficLabelByKey = { digital_product: '주간 판매수' };
  chOrder.forEach(key => {
    const ch = DATA.channels[key];
    const color = `var(--series-${ch.color_slot})`;
    const card = document.createElement('div');
    card.className = 'card';
    const trafficMetric = trafficMetricByKey[key] || 'visits';
    const trafficLabel = trafficLabelByKey[key] || '주간 방문자';
    const pausedBadge = ch.paused ? ' <span class="status-badge status-paused">보류</span>' : '';
    card.innerHTML = `
      <h2>${ch.label} — 주간 매출(원)${pausedBadge}</h2>
      <div class="chart-holder"><svg width="100%" height="150" class="rev-chart"></svg></div>
      <h2 style="margin-top:16px;">${ch.label} — ${trafficLabel}</h2>
      <div class="chart-holder"><svg width="100%" height="150" class="traffic-chart"></svg></div>
      <div class="legend">
        <div class="legend-item"><span class="legend-swatch dash" style="color:${color}"></span>계획</div>
        <div class="legend-item"><span class="legend-swatch" style="background:${color}"></span>실제</div>
      </div>
    `;
    container.appendChild(card);
    drawChart(card.querySelector('.rev-chart'), {
      weekLabels, height: 150, yFmt: fmtWon,
      lines: [
        { name: '계획', data: ch.plan.revenue_krw, color, dash: true },
        { name: '실제', data: ch.actual.revenue_krw, color, dash: false },
      ],
    });
    drawChart(card.querySelector('.traffic-chart'), {
      weekLabels, height: 150, yFmt: fmtNum,
      lines: [
        { name: '계획', data: ch.plan[trafficMetric], color, dash: true },
        { name: '실제', data: ch.actual[trafficMetric], color, dash: false },
      ],
    });
  });

  // table
  let rows = '';
  weeks.forEach((w, i) => {
    const gate = i + 1 === DATA.notes.naver_adpost_gate_week ? ' <span class="gate-badge">애드포스트 개시</span>' : '';
    rows += `<tr>
      <td>W${w.week} (${w.week_start})${gate}</td>
      <td>${fmtNum(DATA.channels.blog_blogger.plan.visits[i])}</td>
      <td>${fmtNum(DATA.channels.blog_blogger.actual.visits[i])}</td>
      <td>${fmtWon(DATA.channels.blog_blogger.plan.revenue_krw[i])}</td>
      <td>${fmtWon(DATA.channels.blog_blogger.actual.revenue_krw[i])}</td>
      <td>${fmtNum(DATA.channels.blog_naver.plan.visits[i])}</td>
      <td>${fmtNum(DATA.channels.blog_naver.actual.visits[i])}</td>
      <td>${fmtWon(DATA.channels.blog_naver.plan.revenue_krw[i])}</td>
      <td>${fmtWon(DATA.channels.blog_naver.actual.revenue_krw[i])}</td>
      <td>${fmtNum(DATA.channels.digital_product.plan.units_sold[i])}</td>
      <td>${fmtNum(DATA.channels.digital_product.actual.units_sold[i])}</td>
      <td>${fmtWon(DATA.channels.digital_product.plan.revenue_krw[i])}</td>
      <td>${fmtWon(DATA.channels.digital_product.actual.revenue_krw[i])}</td>
      <td>${fmtWon(totals.plan_realistic_cum[i])}</td>
      <td>${fmtWon(totals.actual_cum[i])}</td>
    </tr>`;
  });
  document.getElementById('table-holder').innerHTML = `
    <table class="data-table">
      <thead><tr>
        <th>주차</th>
        <th colspan="2">Blogger 방문</th><th colspan="2">Blogger 매출</th>
        <th colspan="2">네이버 방문</th><th colspan="2">네이버 매출</th>
        <th colspan="2">디지털상품 판매</th><th colspan="2">디지털상품 매출</th>
        <th>누적계획</th><th>누적실제</th>
      </tr><tr>
        <th></th><th>계획</th><th>실제</th><th>계획</th><th>실제</th>
        <th>계획</th><th>실제</th><th>계획</th><th>실제</th>
        <th>계획</th><th>실제</th><th>계획</th><th>실제</th>
        <th></th><th></th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;

  const statusClassMap = { '운영중': 'status-active', '대기중': 'status-waiting', '보류': 'status-paused' };
  document.querySelectorAll('.filter-chip').forEach(chip => {
    chip.classList.toggle('active', chip.dataset.status === statusFilter);
  });
  const visibleStatus = DATA.project_status.filter(s => !statusFilter || s.status === statusFilter);
  document.getElementById('status-list').innerHTML = visibleStatus.map(s => {
    const header = `
    <div class="status-row">
      <div>
        <div class="status-name">${s.name}</div>
        <div class="status-detail">${s.detail}</div>
      </div>
      <span class="status-badge ${statusClassMap[s.status] || 'status-waiting'}">${s.status}</span>
    </div>`;
    if (!s.content_schedule) return header;
    const rows2 = s.content_schedule.map(item => `
      <li class="sched-item ${item.done ? 'sched-done' : ''}">
        <span class="sched-check">${item.done ? '✔' : '○'}</span>
        <span class="sched-date">${item.date}</span>
        <span class="sched-title">${item.title}</span>
      </li>
    `).join('');
    return `<details class="status-details">
      <summary>${header}</summary>
      <div class="content-list-wrap"><ol class="sched-list">${rows2}</ol></div>
    </details>`;
  }).join('');

  document.getElementById('roadmap-list').innerHTML = DATA.roadmap.map(r => `
    <div class="roadmap-item">
      <div class="roadmap-when">${r.when}</div>
      <div class="roadmap-task">${r.task}</div>
    </div>
  `).join('');
}

document.getElementById('status-filter-bar').addEventListener('click', ev => {
  const chip = ev.target.closest('.filter-chip');
  if (!chip) return;
  statusFilter = statusFilter === chip.dataset.status ? null : chip.dataset.status;
  render();
});

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
    render();
  });
});

render();
window.addEventListener('resize', render);
</script>
"""


def main() -> None:
    html = HTML_TEMPLATE
    html = html.replace("__DATA_JSON__", json.dumps(DATA, ensure_ascii=False))
    html = html.replace("__GOAL__", f"{DATA['goal_krw']:,}")
    html = html.replace("__NOTE_ADPOST__", DATA["notes"]["naver_adpost_gate_reason"])
    html = html.replace("__NOTE_DISCLAIMER__", DATA["notes"]["estimate_disclaimer"])
    html = html.replace("__LAST_UPDATED__", DATA["notes"]["last_updated"])
    html = html.replace("__PDF_B64__", PDF_B64)
    out_path = ROOT / "dashboard.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
