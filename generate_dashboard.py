#!/usr/bin/env python3
"""
generate_dashboard.py
---------------------
실행:  python generate_dashboard.py
출력:  dashboard.html

필요 패키지:
    pip install finance-datareader pandas
"""

import json
import datetime
import calendar
import sys
from pathlib import Path

try:
    import FinanceDataReader as fdr
    import pandas as pd
except ImportError as e:
    sys.exit(f"[오류] 패키지 누락: {e}\n설치: pip install finance-datareader pandas")


# ─────────────────────────────────────────────────────────────────────────────
# 날짜 헬퍼
# ─────────────────────────────────────────────────────────────────────────────

def get_reference_dates():
    """
    표시할 기준 날짜 목록을 반환한다.
    - 고정 : 2024년말, 2025년말, 2026년 1~3월말
    - 자동 : 2026년 4월 이후 이미 지난 월말 자동 추가
    - 마지막 : 항상 어제
    """
    today     = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    fixed = [
        datetime.date(2024, 12, 31),
        datetime.date(2025, 12, 31),
        datetime.date(2026,  1, 31),
        datetime.date(2026,  2, 28),
        datetime.date(2026,  3, 31),
    ]

    extra, y, m = [], 2026, 4
    while True:
        last = calendar.monthrange(y, m)[1]
        me   = datetime.date(y, m, last)
        if me >= today:
            break
        extra.append(me)
        if m == 12:
            m, y = 1, y + 1
        else:
            m += 1

    seen, result = set(), []
    for d in (fixed + extra + [yesterday]):
        if d not in seen:
            seen.add(d)
            result.append(d)
    return result


def col_label(d):
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    if d == yesterday:
        return f"어제\n({d.month}/{d.day})"
    if d.month == 12:
        return f"{d.year}년말"
    return f"{d.month}월말"


def to_date(idx_val):
    """다양한 인덱스 타입을 datetime.date로 변환."""
    if isinstance(idx_val, datetime.date) and not isinstance(idx_val, datetime.datetime):
        return idx_val
    return pd.Timestamp(idx_val).date()


# ─────────────────────────────────────────────────────────────────────────────
# 시계열 데이터 수집 (2024-01-01 ~ 어제)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_bond_series():
    """국고채 30년물 일별 수익률 (한국은행 ECOS)."""
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        from FinanceDataReader.ecos.data import _ecos_stat
        stat_ds = {
            'dsId': '817Y002',
            'dsItmId1': 'ACC_ITEM', 'dsItmId2': None, 'dsItmId3': None,
            'dsItmVal1': '010230000', 'dsItmVal2': None, 'dsItmVal3': None,
        }
        df = _ecos_stat([stat_ds], '2024-01-01', yesterday, freq='D')
        if df is None or df.empty:
            return [], []
        col    = df.columns[0]
        dates  = [str(to_date(i)) for i in df.index]
        values = [round(float(v), 3) for v in df[col].values]
        return dates, values
    except Exception as e:
        print(f"  [WARN] 국고채 30Y 시계열: {e}")
        return [], []


def fetch_kospi_series():
    """KOSPI 일별 종가 (KS11)."""
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        df = fdr.DataReader('KS11', '2024-01-01', yesterday)
        if df is None or df.empty:
            return [], []
        dates  = [str(to_date(i)) for i in df.index]
        values = [round(float(v), 2) for v in df['Close'].values]
        return dates, values
    except Exception as e:
        print(f"  [WARN] KOSPI 시계열: {e}")
        return [], []


def fetch_hanwha_series():
    """한화생명(088350) 일별 종가."""
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        df = fdr.DataReader('088350', '2024-01-01', yesterday)
        if df is None or df.empty:
            return [], []
        dates  = [str(to_date(i)) for i in df.index]
        values = [round(float(v)) for v in df['Close'].values]
        return dates, values
    except Exception as e:
        print(f"  [WARN] 한화생명 시계열: {e}")
        return [], []


# ─────────────────────────────────────────────────────────────────────────────
# 포인트 데이터 (기준일별 단일 값)
# ─────────────────────────────────────────────────────────────────────────────

def _closest(date_list, value_list, target):
    """
    시계열에서 target 날짜 이하의 최근 값을 반환한다.
    데이터가 없으면 None.
    """
    if not date_list:
        return None
    # date_list는 'YYYY-MM-DD' 문자열
    target_str = str(target)
    # target 이하인 날짜만 필터
    candidates = [(d, v) for d, v in zip(date_list, value_list) if d <= target_str]
    if not candidates:
        return None
    return candidates[-1][1]


# ─────────────────────────────────────────────────────────────────────────────
# HTML 템플릿
# ─────────────────────────────────────────────────────────────────────────────

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>Morning Dashboard — %%GEN_DATE%%</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', 'Malgun Gothic', Arial, sans-serif;
    background: #eef0f5; color: #1e1e1e; font-size: 13px;
    -webkit-text-size-adjust: 100%;
  }

  /* ── Header ── */
  .header {
    background: linear-gradient(135deg, #1a2744 0%, #2b3f72 100%);
    color: #fff; padding: 14px 20px;
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 3px solid #f4841e;
  }
  .header h1 { font-size: 15px; font-weight: 600; letter-spacing: 0.3px; }
  .header .sub { font-size: 10px; color: #a8bad8; margin-top: 2px; }
  .header .meta { font-size: 11px; color: #c8d4ea; text-align: right; line-height: 1.6; }
  .header .meta strong { color: #fff; }

  /* ── Layout ── */
  .container { max-width: 1440px; margin: 0 auto; padding: 14px 14px; }

  .card {
    background: #fff; border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,.07);
    margin-bottom: 14px; overflow: hidden;
  }
  .card-title {
    padding: 11px 16px; font-size: 10.5px; font-weight: 700;
    color: #666; text-transform: uppercase; letter-spacing: 0.9px;
    border-bottom: 1px solid #f2f2f2; background: #fafbfd;
  }

  /* ── Table ── */
  .table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  table { width: 100%; border-collapse: collapse; min-width: 400px; }
  th, td { padding: 7px 10px; border-bottom: 1px solid #f4f4f4; }
  th {
    background: #f4f6fb; color: #555; font-weight: 600; font-size: 9.5px;
    text-align: center; white-space: pre-line; line-height: 1.35;
  }
  th:first-child { text-align: left; width: 90px; }
  td { text-align: right; color: #333; font-size: 10px; }
  td:first-child {
    text-align: left; font-weight: 600; color: #2c2c2c;
    background: #fafbfd; font-size: 10px;
  }
  tr:last-child td { border-bottom: none; }
  td.today { font-weight: 700; color: #1a2744; }
  td.null-val { color: #bbb; }

  /* ── KPI 카드 (모바일 전용) ── */
  .kpi-row {
    display: none;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px; margin-bottom: 14px;
  }
  .kpi {
    background: #fff; border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,.07);
    padding: 14px 12px; text-align: center;
  }
  .kpi .label { font-size: 10px; color: #888; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.7px; margin-bottom: 6px; }
  .kpi .value { font-size: 18px; font-weight: 700; color: #1a2744; }
  .kpi .sub-val { font-size: 10px; color: #aaa; margin-top: 3px; }

  /* ── Charts ── */
  .charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .chart-pad { padding: 14px 16px 12px; }
  .chart-pad canvas { max-height: 250px; }

  /* ── Footer ── */
  .footer { text-align: right; color: #bbb; font-size: 10px; padding: 4px 0 16px; }

  /* ── 모바일 반응형 ── */
  @media (max-width: 640px) {
    .header h1 { font-size: 13px; }
    .header .sub { display: none; }
    .header .meta { font-size: 10px; }
    .container { padding: 12px 10px; }
    .kpi-row { display: grid; }
    .charts-row { grid-template-columns: 1fr; }
    .chart-pad canvas { max-height: 200px; }
    .card-title { font-size: 10px; padding: 10px 14px; }
  }
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>&#9790;&nbsp; Morning Dashboard</h1>
    <div class="sub">Hanwha Life &nbsp;·&nbsp; 임원 의사결정 참고용</div>
  </div>
  <div class="meta">
    <strong>%%GEN_DATE%%</strong><br>
    기준: 전일 종가
  </div>
</div>

<div class="container">

  <!-- 모바일 KPI 카드 (핸드폰에서만 표시) -->
  <div class="kpi-row" id="kpiRow"></div>

  <!-- 요약 테이블 -->
  <div class="card">
    <div class="card-title">주요 지표 요약</div>
    <div class="table-wrap">
      <table>
        <thead><tr id="hdr"></tr></thead>
        <tbody id="tbd"></tbody>
      </table>
    </div>
  </div>

  <!-- 차트 -->
  <div class="charts-row">
    <div class="card">
      <div class="card-title">국고채 30년물 금리 추이 (%)</div>
      <div class="chart-pad"><canvas id="cBond"></canvas></div>
    </div>
    <div class="card">
      <div class="card-title">KOSPI / 한화생명 주가 추이</div>
      <div class="chart-pad"><canvas id="cEquity"></canvas></div>
    </div>
  </div>

  <div class="footer">%%GEN_DATETIME%% &nbsp;·&nbsp; FinanceDataReader</div>
</div>

<script>
const D = %%DATA_JSON%%;

// ── 모바일 KPI 카드 (어제 값만 표시) ─────────────────────────────────────────
(function() {
  const n = D.columns.length;
  const kpiRow = document.getElementById('kpiRow');
  const defs = [
    { key:'bond',   label:'국고채 30Y', fmt: v => v != null ? v.toFixed(2)+'%' : '—' },
    { key:'kospi',  label:'KOSPI',      fmt: v => v != null ? v.toLocaleString('ko-KR',{maximumFractionDigits:0}) : '—' },
    { key:'hanwha', label:'한화생명',   fmt: v => v != null ? v.toLocaleString('ko-KR')+'원' : '—' },
  ];
  defs.forEach(d => {
    const today = D.rows[d.key][n-1];
    const prev  = D.rows[d.key][n-2];
    let chg = '';
    if (today != null && prev != null) {
      const diff = today - prev;
      const sign = diff >= 0 ? '▲' : '▼';
      const color = diff >= 0 ? '#e03e3e' : '#2563eb';
      if (d.key === 'bond') {
        chg = `<span style="color:${color}">${sign} ${Math.abs(diff).toFixed(2)}%p</span>`;
      } else {
        chg = `<span style="color:${color}">${sign} ${Math.abs(diff).toLocaleString('ko-KR',{maximumFractionDigits:0})}</span>`;
      }
    }
    kpiRow.innerHTML += `
      <div class="kpi">
        <div class="label">${d.label}</div>
        <div class="value">${d.fmt(today)}</div>
        <div class="sub-val">${chg || '&nbsp;'}</div>
      </div>`;
  });
})();

// ── 테이블 ────────────────────────────────────────────────────────────────────
(function() {
  const hdr = document.getElementById('hdr');
  const tbd = document.getElementById('tbd');
  const n   = D.columns.length;

  // 헤더
  const th0 = document.createElement('th');
  th0.textContent = '지표';
  hdr.appendChild(th0);
  D.columns.forEach(col => {
    const th = document.createElement('th');
    th.textContent = col.label;
    hdr.appendChild(th);
  });

  // 데이터 행
  const rows = [
    { key:'bond',   name:'국고채 30Y (%)', fmt: v => v != null ? v.toFixed(2)+'%' : null },
    { key:'kospi',  name:'KOSPI',           fmt: v => v != null ? v.toLocaleString('ko-KR', {maximumFractionDigits:0}) : null },
    { key:'hanwha', name:'한화생명 (원)',   fmt: v => v != null ? v.toLocaleString('ko-KR') : null },
  ];

  rows.forEach(row => {
    const tr = document.createElement('tr');
    const td0 = document.createElement('td');
    td0.textContent = row.name;
    tr.appendChild(td0);

    D.rows[row.key].forEach((v, i) => {
      const td  = document.createElement('td');
      const txt = row.fmt(v);
      if (txt == null) {
        td.textContent = '—';
        td.className = 'null-val';
      } else {
        td.textContent = txt;
        if (i === n - 1) td.className = 'today';
      }
      tr.appendChild(td);
    });
    tbd.appendChild(tr);
  });
})();


// ── 차트 공통 옵션 ─────────────────────────────────────────────────────────────
const TICK = { color: '#999', font: { size: 11 } };
const GRID = { color: '#f2f2f2' };


// ── 국고채 30Y 차트 ────────────────────────────────────────────────────────────
(function() {
  const ctx  = document.getElementById('cBond').getContext('2d');
  const grad = ctx.createLinearGradient(0, 0, 0, 265);
  grad.addColorStop(0, 'rgba(26,39,68,0.18)');
  grad.addColorStop(1, 'rgba(26,39,68,0.01)');

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: D.bond_s.dates,
      datasets: [{
        label: '국고채 30Y (%)',
        data:  D.bond_s.values,
        borderColor: '#1a2744',
        backgroundColor: grad,
        borderWidth: 1.8,
        pointRadius: 0,
        tension: 0.2,
        fill: true,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { ...TICK, maxTicksLimit: 8, maxRotation: 0 }, grid: GRID },
        y: { ticks: { ...TICK, callback: v => v.toFixed(2)+'%' }, grid: GRID },
      }
    }
  });
})();


// ── KOSPI / 한화생명 이중축 차트 ───────────────────────────────────────────────
(function() {
  new Chart(document.getElementById('cEquity').getContext('2d'), {
    type: 'line',
    data: {
      labels: D.kospi_s.dates,
      datasets: [
        {
          label: 'KOSPI',
          data:  D.kospi_s.values,
          borderColor: '#2563eb',
          backgroundColor: 'transparent',
          borderWidth: 1.8,
          pointRadius: 0,
          tension: 0.2,
          yAxisID: 'y1',
        },
        {
          label: '한화생명 (원)',
          data:  D.hanwha_aligned,
          borderColor: '#f4841e',
          backgroundColor: 'transparent',
          borderWidth: 1.8,
          pointRadius: 0,
          tension: 0.2,
          yAxisID: 'y2',
        },
      ]
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { labels: { font: { size: 11 }, boxWidth: 12, padding: 16 } }
      },
      scales: {
        x:  { ticks: { ...TICK, maxTicksLimit: 8, maxRotation: 0 }, grid: GRID },
        y1: {
          position: 'left',
          ticks: { ...TICK, callback: v => v.toLocaleString('ko-KR', {maximumFractionDigits:0}) },
          grid: GRID
        },
        y2: {
          position: 'right',
          ticks: { ...TICK, callback: v => v.toLocaleString('ko-KR') },
          grid: { display: false }
        },
      }
    }
  });
})();
</script>
</body>
</html>
"""


def build_html(data, gen_date, gen_datetime):
    data_json = json.dumps(data, ensure_ascii=False)
    html = HTML_TEMPLATE
    html = html.replace('%%GEN_DATE%%',     gen_date)
    html = html.replace('%%GEN_DATETIME%%', gen_datetime)
    html = html.replace('%%DATA_JSON%%',    data_json)
    return html


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    today = datetime.date.today()
    ref_dates = get_reference_dates()

    print(f"=== Morning Dashboard Generator ({today}) ===")
    print(f"기준 날짜 ({len(ref_dates)}개): {[str(d) for d in ref_dates]}\n")

    # ── 시계열 수집 ───────────────────────────────────────────────────────────
    print("[ 1/2 ] 시계열 데이터 수집 중 (2024-01-01 ~ 어제)...")

    print("  국고채 30Y (investing.com)...")
    bd, bv = fetch_bond_series()
    print(f"    -> {len(bd)}건 {'OK' if bd else 'EMPTY'}")

    print("  KOSPI...")
    kd, kv = fetch_kospi_series()
    print(f"    -> {len(kd)}건 {'OK' if kd else 'EMPTY'}")

    print("  한화생명 (088350)...")
    hd, hv = fetch_hanwha_series()
    print(f"    -> {len(hd)}건 {'OK' if hd else 'EMPTY'}")

    # ── 포인트 데이터 (시계열에서 추출) ──────────────────────────────────────
    print("\n[ 2/2 ] 기준일별 포인트 값 추출 중...")
    bond_pts, kospi_pts, hanwha_pts = [], [], []
    for d in ref_dates:
        b = _closest(bd, bv, d)
        k = _closest(kd, kv, d)
        h = _closest(hd, hv, d)
        bond_pts.append(b)
        kospi_pts.append(k)
        hanwha_pts.append(h)
        print(f"  {d}  국고채={b}  KOSPI={k}  한화생명={h}")

    # KOSPI 날짜 축에 한화생명 정렬
    hmap = dict(zip(hd, hv))
    hanwha_aligned = [hmap.get(d) for d in kd]

    # ── HTML 생성 ─────────────────────────────────────────────────────────────
    data = {
        'columns': [{'label': col_label(d), 'date': str(d)} for d in ref_dates],
        'rows': {
            'bond':   bond_pts,
            'kospi':  kospi_pts,
            'hanwha': hanwha_pts,
        },
        'bond_s':         {'dates': bd, 'values': bv},
        'kospi_s':        {'dates': kd, 'values': kv},
        'hanwha_aligned': hanwha_aligned,
    }

    gen_date     = today.strftime('%Y-%m-%d')
    gen_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    html = build_html(data, gen_date, gen_datetime)

    out = Path(__file__).parent / 'dashboard.html'
    out.write_text(html, encoding='utf-8')
    print(f"\n[완료] {out.resolve()}")


if __name__ == '__main__':
    main()
