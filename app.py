"""
╔══════════════════════════════════════════════════════╗
║           LEAL — CX  |  Sistema de Qualidade         ║
║           Operação Mercado Pago                      ║
╚══════════════════════════════════════════════════════╝
Rodar localmente:
    pip install streamlit pandas openpyxl plotly
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, date
from pathlib import Path

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False

# ─── Configuração da página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Leal — CX",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS: Design Galáxia Imersivo ─────────────────────────────────────────────
GALAXY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main, .block-container {
    background-color: #05050a !important;
    color: #f0f0f8 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── CANVAS ESTRELAS ── */
#star-canvas {
    position: fixed; top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none; z-index: 0;
}

/* ── ORBS DE LUZ AMBIENTE ── */
.ambient-orb-1 {
    position: fixed; top: -80px; left: 15%;
    width: 380px; height: 380px; border-radius: 50%;
    background: radial-gradient(circle, rgba(212,168,83,0.04) 0%, transparent 70%);
    pointer-events: none; z-index: 0;
}
.ambient-orb-2 {
    position: fixed; bottom: 10%; right: 10%;
    width: 260px; height: 260px; border-radius: 50%;
    background: radial-gradient(circle, rgba(99,102,241,0.04) 0%, transparent 70%);
    pointer-events: none; z-index: 0;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: rgba(8,8,20,0.97) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    backdrop-filter: blur(20px) !important;
}
[data-testid="stSidebar"] * { color: #f0f0f8 !important; }
[data-testid="stSidebarContent"] { padding: 0 !important; }

/* ── MÉTRICAS ── */
[data-testid="stMetric"] {
    background: #0c0c14 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    padding: 18px 18px !important;
    position: relative !important;
    overflow: hidden !important;
    transition: border-color 0.25s, transform 0.2s, box-shadow 0.25s !important;
    cursor: default !important;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute; top: 0; left: 0;
    width: 2px; height: 100%;
    background: linear-gradient(180deg, #d4a853 0%, rgba(212,168,83,0.1) 100%);
}
[data-testid="stMetric"]::after {
    content: '';
    position: absolute; top: -30px; right: -30px;
    width: 80px; height: 80px; border-radius: 50%;
    background: radial-gradient(circle, rgba(212,168,83,0.07), transparent 70%);
    pointer-events: none;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(212,168,83,0.28) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(0,0,0,0.4), 0 0 0 1px rgba(212,168,83,0.08) !important;
}
[data-testid="stMetricLabel"] {
    color: #52525b !important;
    font-size: 10px !important;
    font-weight: 500 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    color: #f0f0f8 !important;
    font-size: 24px !important;
    font-weight: 600 !important;
    letter-spacing: -0.025em !important;
}
[data-testid="stMetricDelta"] { color: #d4a853 !important; font-size: 11px !important; }

/* ── INPUTS ── */
input, textarea,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: #0c0c14 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #f0f0f8 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
input:focus, textarea:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #d4a853 !important;
    box-shadow: 0 0 0 3px rgba(212,168,83,0.1) !important;
    outline: none !important;
}
input::placeholder, textarea::placeholder { color: #3a3a50 !important; }

/* ── LABELS ── */
label, [data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p {
    color: #6b6b88 !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
}

/* ── BOTÕES ── */
.stButton > button {
    background: #0c0c14 !important;
    color: #c8c8e8 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 8px 18px !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.02em !important;
}
.stButton > button:hover {
    background: #111120 !important;
    border-color: rgba(212,168,83,0.4) !important;
    color: #d4a853 !important;
    box-shadow: 0 0 20px rgba(212,168,83,0.1), 0 4px 12px rgba(0,0,0,0.4) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── SELECTBOX ── */
[data-baseweb="select"] > div {
    background: #0c0c14 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #f0f0f8 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
}
[data-baseweb="select"] > div:focus-within {
    border-color: #d4a853 !important;
    box-shadow: 0 0 0 3px rgba(212,168,83,0.1) !important;
}
[data-baseweb="popover"], [data-baseweb="menu"] {
    background: #0e0e1a !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    box-shadow: 0 16px 48px rgba(0,0,0,0.8) !important;
}
[data-baseweb="option"] {
    background: transparent !important;
    color: #9898b8 !important;
    font-size: 13px !important;
    padding: 10px 14px !important;
}
[data-baseweb="option"]:hover {
    background: rgba(255,255,255,0.04) !important;
    color: #f0f0f8 !important;
}
[data-baseweb="option"][aria-selected="true"] {
    background: rgba(212,168,83,0.08) !important;
    color: #d4a853 !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"],
[data-testid="stDataFrame"] table {
    background: transparent !important;
    border: none !important;
}
[data-testid="stDataFrame"] thead tr th {
    background: #0c0c14 !important;
    color: #52525b !important;
    font-size: 10px !important;
    font-weight: 500 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
    padding: 11px 14px !important;
}
[data-testid="stDataFrame"] tbody tr td {
    background: #080812 !important;
    color: #9898b8 !important;
    font-size: 12px !important;
    border-bottom: 1px solid rgba(255,255,255,0.03) !important;
    padding: 10px 14px !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background: rgba(212,168,83,0.04) !important;
    color: #f0f0f8 !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
    background: #0c0c14 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    transition: border-color 0.2s !important;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(212,168,83,0.2) !important;
}
[data-testid="stExpander"] summary {
    background: #0c0c14 !important;
    padding: 13px 18px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #9898b8 !important;
}
[data-testid="stExpander"] summary:hover {
    background: rgba(255,255,255,0.02) !important;
    color: #f0f0f8 !important;
}
[data-testid="stExpander"][open] summary {
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
    color: #d4a853 !important;
}

/* ── TABS ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
    gap: 4px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: #52525b !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    border-bottom: 2px solid transparent !important;
    padding: 10px 16px !important;
    transition: color 0.2s !important;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover { color: #9898b8 !important; }
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
    color: #d4a853 !important;
    border-bottom: 2px solid #d4a853 !important;
}

/* ── PROGRESS BAR ── */
[data-testid="stProgressBar"] > div {
    background: #1a1a2e !important;
    border-radius: 6px !important;
    height: 5px !important;
}
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #92400e, #d4a853, #f0c96a) !important;
    border-radius: 6px !important;
    box-shadow: 0 0 8px rgba(212,168,83,0.35) !important;
}

/* ── SLIDER ── */
[data-testid="stSlider"] > div > div > div {
    background: #1a1a2e !important;
}
[data-testid="stSlider"] [role="slider"] {
    background: #d4a853 !important;
    border: 2px solid #05050a !important;
    box-shadow: 0 0 8px rgba(212,168,83,0.5) !important;
}

/* ── DIVISOR ── */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
    margin: 1.5rem 0 !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    background: #0c0c14 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px !important;
    border-left: 3px solid #d4a853 !important;
    border-radius: 0 8px 8px 0 !important;
}

/* ── FORM SUBMIT ── */
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, rgba(92,60,0,0.4), rgba(60,40,0,0.6)) !important;
    color: #d4a853 !important;
    border: 1px solid rgba(212,168,83,0.4) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    transition: all 0.2s !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
    background: #d4a853 !important;
    color: #05050a !important;
    box-shadow: 0 0 24px rgba(212,168,83,0.3) !important;
    transform: translateY(-1px) !important;
}

/* ── HEADINGS ── */
h1 {
    color: #f0f0f8 !important;
    font-size: 22px !important;
    font-weight: 600 !important;
    letter-spacing: -0.025em !important;
    margin-bottom: 2px !important;
}
h2 { color: #d8d8f0 !important; font-weight: 500 !important; font-size: 18px !important; }
h3 { color: #9898b8 !important; font-size: 14px !important; font-weight: 500 !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #05050a; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(212,168,83,0.4); }

/* ── BLOCK CONTAINER ── */
.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 2rem !important;
    max-width: 1440px !important;
}

/* ── COMPONENTES CUSTOM ── */
.page-header {
    padding-bottom: 1rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.sidebar-logo {
    padding: 1.4rem 1.2rem 1.1rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 0.4rem;
}
.badge-faixa {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 5px;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.03em;
}
.gold-text { color: #d4a853 !important; }
.muted-text { color: #52525b !important; }

/* ── DATE INPUT ── */
[data-testid="stDateInput"] input {
    background: #0c0c14 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #f0f0f8 !important;
    border-radius: 8px !important;
}

/* ── NUMBER INPUT BOTÕES ── */
[data-testid="stNumberInput"] button {
    background: #111120 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #6b6b88 !important;
    border-radius: 6px !important;
}
[data-testid="stNumberInput"] button:hover {
    background: rgba(212,168,83,0.08) !important;
    color: #d4a853 !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: #0c0c14 !important;
    border: 1px dashed rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(212,168,83,0.35) !important;
}

/* ── DOWNLOAD BUTTON ── */
[data-testid="stDownloadButton"] > button {
    background: #0c0c14 !important;
    color: #d4a853 !important;
    border: 1px solid rgba(212,168,83,0.25) !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
[data-testid="stDownloadButton"] > button:hover {
    border-color: rgba(212,168,83,0.5) !important;
    box-shadow: 0 0 16px rgba(212,168,83,0.15) !important;
    transform: translateY(-1px) !important;
}
</style>
"""

# ─── JS: Campo Estelar Imersivo ───────────────────────────────────────────────
STARS_JS = """
<div class="ambient-orb-1"></div>
<div class="ambient-orb-2"></div>
<canvas id="star-canvas"></canvas>
<script>
(function(){
  var cv = document.getElementById('star-canvas');
  if (!cv) return;
  var ctx = cv.getContext('2d');
  var W = window.innerWidth, H = window.innerHeight;
  cv.width = W; cv.height = H;

  var STAR_COUNT = 300;
  var stars = [];

  function rand(a, b) { return Math.random() * (b - a) + a; }

  function makeStar() {
    var isGold = Math.random() > 0.80;
    var isBig  = Math.random() > 0.93;
    return {
      x: rand(0, W), y: rand(0, H),
      r: rand(0.2, isBig ? 2.2 : (isGold ? 1.6 : 1.0)),
      baseAlpha: rand(0.08, isGold ? 0.65 : 0.38),
      pa: rand(0, Math.PI * 2),
      ps: rand(0.003, 0.016),
      vx: rand(-0.05, 0.05),
      vy: rand(-0.04, 0.04),
      gold: isGold,
      big: isBig
    };
  }
  for (var i = 0; i < STAR_COUNT; i++) stars.push(makeStar());

  var shoots = [], stimer = 0;
  function makeShoot() {
    return {
      x: rand(0, W * 0.65), y: rand(0, H * 0.45),
      len: rand(90, 180), spd: rand(8, 18),
      ang: rand(0.22, 0.52),
      life: 0, max: rand(28, 55), a: 1.0
    };
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);

    for (var i = 0; i < stars.length; i++) {
      var s = stars[i];
      s.pa += s.ps;
      var a = s.baseAlpha * (0.4 + 0.6 * Math.sin(s.pa));

      if (s.big) {
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r * 3.5, 0, Math.PI * 2);
        ctx.fillStyle = s.gold
          ? 'rgba(212,168,83,' + (a * 0.10) + ')'
          : 'rgba(200,200,240,' + (a * 0.08) + ')';
        ctx.fill();
      }

      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fillStyle = s.gold
        ? 'rgba(212,168,83,' + a + ')'
        : (s.big ? 'rgba(240,240,255,' + a + ')' : 'rgba(190,190,230,' + a + ')');
      ctx.fill();

      if (s.r > 1.0) {
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r * 2.2, 0, Math.PI * 2);
        ctx.fillStyle = s.gold
          ? 'rgba(212,168,83,' + (a * 0.14) + ')'
          : 'rgba(200,210,255,' + (a * 0.10) + ')';
        ctx.fill();
      }

      s.x += s.vx; s.y += s.vy;
      if (s.x < -4) s.x = W + 4; if (s.x > W + 4) s.x = -4;
      if (s.y < -4) s.y = H + 4; if (s.y > H + 4) s.y = -4;
    }

    stimer++;
    if (stimer > 260 && Math.random() > 0.96) {
      shoots.push(makeShoot()); stimer = 0;
    }
    for (var j = shoots.length - 1; j >= 0; j--) {
      var sh = shoots[j]; sh.life++;
      sh.a = 1 - sh.life / sh.max;
      var ex = sh.x + Math.cos(sh.ang) * sh.len;
      var ey = sh.y + Math.sin(sh.ang) * sh.len;
      var g = ctx.createLinearGradient(sh.x, sh.y, ex, ey);
      g.addColorStop(0, 'rgba(212,168,83,0)');
      g.addColorStop(0.5, 'rgba(212,168,83,' + (sh.a * 0.7) + ')');
      g.addColorStop(1, 'rgba(240,200,120,' + sh.a + ')');
      ctx.beginPath(); ctx.moveTo(sh.x, sh.y); ctx.lineTo(ex, ey);
      ctx.strokeStyle = g; ctx.lineWidth = 1.3; ctx.stroke();
      sh.x += Math.cos(sh.ang) * sh.spd;
      sh.y += Math.sin(sh.ang) * sh.spd;
      if (sh.life >= sh.max || sh.x > W || sh.y > H) shoots.splice(j, 1);
    }

    requestAnimationFrame(draw);
  }
  draw();

  window.addEventListener('resize', function() {
    W = window.innerWidth; H = window.innerHeight;
    cv.width = W; cv.height = H;
  });
})();
</script>
"""

st.markdown(GALAXY_CSS, unsafe_allow_html=True)

# ─── Constantes ───────────────────────────────────────────────────────────────
DATA_DIR    = Path("data")
DATA_DIR.mkdir(exist_ok=True)
OPS_FILE    = DATA_DIR / "operadores.json"
EVALS_FILE  = DATA_DIR / "avaliacoes.json"
FAIXAS_FILE = DATA_DIR / "faixas.json"
USERS_FILE  = DATA_DIR / "usuarios.json"

NIVEIS = {
    "comandante": "Comandante 🌌",
    "copiloto":   "Copiloto 🚀",
    "observador": "Observador Estelar 🔭",
    "tripulacao": "Tripulação ⭐",
}

MESES_LABEL = [f"Mês {i:02d}" for i in range(1, 13)]
CICLOS      = ["Ciclo 1", "Ciclo 2", "Ciclo 3", "Ciclo 4", "Ciclo 5"]
CARGOS_GESTAO = ["Gerente de Qualidade", "Coordenador(a)", "Supervisor(a)", "Analista de Qualidade"]
CARGOS_OP     = ["Operador(a)"]

DEFAULT_FAIXAS = [
    {"id":"f1","desc":"Abaixo da meta","min":0,  "max":79.9,"bonus":0},
    {"id":"f2","desc":"Faixa Bronze",  "min":80, "max":84.9,"bonus":75},
    {"id":"f3","desc":"Faixa Prata",   "min":85, "max":89.9,"bonus":150},
    {"id":"f4","desc":"Faixa Ouro",    "min":90, "max":94.9,"bonus":250},
    {"id":"f5","desc":"Faixa Diamante","min":95, "max":100, "bonus":400},
]
DEFAULT_USUARIOS = [
    {"login":"comandante","senha":"leal2024","nivel":"comandante","nome":"Gerente de Qualidade","op_id":""},
    {"login":"copiloto",  "senha":"leal2024","nivel":"copiloto",  "nome":"Coordenadora","op_id":""},
    {"login":"observador","senha":"leal2024","nivel":"observador","nome":"Gerente","op_id":""},
]

# ─── Plotly: Tema base escuro ─────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, sans-serif", color="#9898b8", size=11),
    margin=dict(l=8, r=8, t=8, b=8),
    showlegend=False,
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.06)",
        tickfont=dict(color="#52525b", size=10),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.06)",
        tickfont=dict(color="#52525b", size=10),
    ),
)

PLOTLY_CFG = {"displayModeBar": False}

GOLD      = "#d4a853"
GOLD_FILL = "rgba(212,168,83,0.10)"
INDIGO    = "#818cf8"
INDIGO_F  = "rgba(129,140,248,0.06)"
GREEN     = "#4ade80"
RED       = "#ef4444"
AMBER     = "#f59e0b"
PURPLE    = "#a78bfa"
SLATE     = "#64748b"


def plotly_line(labels, datasets):
    """Gráfico de linha multi-série elegante."""
    if not PLOTLY_AVAILABLE:
        return None
    fig = go.Figure()
    colors = [GOLD, INDIGO, GREEN, AMBER]
    fills  = [GOLD_FILL, INDIGO_F, "rgba(74,222,128,0.06)", "rgba(245,158,11,0.06)"]
    dashes = ["solid", "dot", "dash", "dashdot"]
    for i, ds in enumerate(datasets):
        c = colors[i % len(colors)]
        fig.add_trace(go.Scatter(
            x=labels, y=ds["data"], name=ds["label"],
            mode="lines+markers",
            line=dict(color=c, width=2, dash=dashes[i]),
            marker=dict(color=c, size=5, line=dict(color="#05050a", width=1.5)),
            fill="tozeroy",
            fillcolor=fills[i % len(fills)],
            hovertemplate=f"<b>%{{x}}</b><br>{ds['label']}: %{{y:.1f}}%<extra></extra>",
        ))
    layout = dict(PLOTLY_LAYOUT)
    layout["yaxis"] = dict(PLOTLY_LAYOUT["yaxis"], ticksuffix="%", range=[75, 100])
    fig.update_layout(**layout)
    return fig


def plotly_donut(labels, values, colors_list):
    """Gráfico de rosca com espaçamento entre fatias."""
    if not PLOTLY_AVAILABLE:
        return None
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.62,
        marker=dict(colors=colors_list, line=dict(color="#05050a", width=3)),
        textfont=dict(size=10, color="#9898b8"),
        hovertemplate="<b>%{label}</b><br>%{value} operadores<extra></extra>",
        direction="clockwise",
        sort=False,
    ))
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def plotly_bar_h(labels, values, color=GOLD):
    """Barras horizontais para comparativos."""
    if not PLOTLY_AVAILABLE:
        return None

    bar_colors = []
    for v in values:
        if v is None:
            bar_colors.append(SLATE)
        elif v >= 90:
            bar_colors.append(GOLD)
        elif v >= 80:
            bar_colors.append(AMBER)
        else:
            bar_colors.append(RED)

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(
            color=bar_colors,
            cornerradius=4,
            line=dict(width=0),
        ),
        text=[f"{v:.1f}%" if v else "—" for v in values],
        textposition="outside",
        textfont=dict(color="#9898b8", size=10),
        hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra></extra>",
    ))
    height = max(200, len(labels) * 38 + 60)
    layout = dict(PLOTLY_LAYOUT)
    layout["xaxis"] = dict(PLOTLY_LAYOUT["xaxis"], range=[0, 105], ticksuffix="%")
    layout["yaxis"] = dict(PLOTLY_LAYOUT["yaxis"], autorange="reversed")
    layout["margin"] = dict(l=8, r=50, t=8, b=8)
    layout["height"] = height
    fig.update_layout(**layout)
    return fig


def plotly_ciclo_line(ciclos_labels, series):
    """Linha por ciclo dentro do mês."""
    if not PLOTLY_AVAILABLE:
        return None
    fig = go.Figure()
    colors = [GOLD, INDIGO, GREEN, AMBER, PURPLE, RED]
    for i, (name, data) in enumerate(series.items()):
        c = colors[i % len(colors)]
        fig.add_trace(go.Scatter(
            x=ciclos_labels, y=data, name=name,
            mode="lines+markers",
            line=dict(color=c, width=1.8),
            marker=dict(color=c, size=4, line=dict(color="#05050a", width=1.5)),
            hovertemplate=f"<b>%{{x}}</b><br>{name}: %{{y:.1f}}%<extra></extra>",
        ))
    layout = dict(PLOTLY_LAYOUT)
    layout["showlegend"] = True
    layout["legend"] = dict(
        bgcolor="rgba(0,0,0,0)", bordercolor="rgba(255,255,255,0.06)",
        borderwidth=1, font=dict(color="#9898b8", size=10),
        orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
    )
    layout["yaxis"] = dict(PLOTLY_LAYOUT["yaxis"], ticksuffix="%", range=[70, 102])
    fig.update_layout(**layout)
    return fig


# ─── Google Sheets / Persistência ────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

ABA_HEADERS = {
    "operadores": ["id","nome","cargo","adm","status","notas","op_id"],
    "avaliacoes":  ["id","op_id","mes","ciclo","mp","nota_int","feed","pos","acao","criado"],
    "faixas":      ["id","desc","min","max","bonus"],
    "usuarios":    ["login","senha","nivel","nome","op_id"],
}

def _use_gsheets():
    if not GSHEETS_AVAILABLE:
        return False
    try:
        return "gcp_service_account" in st.secrets and "gsheets" in st.secrets
    except Exception:
        return False

def _gc():
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=SCOPES
    )
    return gspread.authorize(creds)

def _spreadsheet():
    sid = st.secrets["gsheets"]["spreadsheet_id"]
    return _gc().open_by_key(sid)

def _get_or_create_ws(nome):
    sh = _spreadsheet()
    titles = [ws.title for ws in sh.worksheets()]
    if nome not in titles:
        ws = sh.add_worksheet(title=nome, rows=1000, cols=30)
        ws.append_row(ABA_HEADERS[nome])
        return ws
    ws = sh.worksheet(nome)
    vals = ws.get_all_values()
    if not vals:
        ws.append_row(ABA_HEADERS[nome])
    return ws

def _gs_read(nome):
    try:
        ws = _get_or_create_ws(nome)
        rows = ws.get_all_values()
        if len(rows) < 2:
            return []
        headers = rows[0]
        result = []
        for row in rows[1:]:
            padded = row + [""] * (len(headers) - len(row))
            result.append(dict(zip(headers, padded)))
        return result
    except Exception as e:
        st.session_state.setdefault("gs_last_error", str(e))
        return None

def _gs_write(nome, data):
    try:
        ws = _get_or_create_ws(nome)
        ws.clear()
        headers = ABA_HEADERS.get(nome, list(data[0].keys()) if data else [])
        rows = [headers] + [[str(r.get(h, "")) for h in headers] for r in data]
        ws.update(rows, "A1")
    except Exception as e:
        st.error(f"❌ Falha ao sincronizar '{nome}' com Google Sheets: {e}")

def _json_read(path, default):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def _json_write(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _none_to_str(data):
    if isinstance(data, list):
        return [{k: ("" if v is None else v) for k, v in r.items()} for r in data]
    return data

def _str_to_none(data, none_fields):
    result = []
    for r in data:
        row = dict(r)
        for f in none_fields:
            if row.get(f) == "":
                row[f] = None
        result.append(row)
    return result

def _fix_numbers(data, float_fields):
    result = []
    for r in data:
        row = dict(r)
        for f in float_fields:
            v = row.get(f)
            if v not in (None, ""):
                try: row[f] = float(v)
                except: pass
        result.append(row)
    return result

def load_operadores():
    if _use_gsheets():
        data = _gs_read("operadores")
        if data is None:
            return _json_read(OPS_FILE, [])
        return _str_to_none(data, ["op_id"])
    return _json_read(OPS_FILE, [])

def save_operadores(d):
    d = _none_to_str(d)
    _json_write(OPS_FILE, d)
    if _use_gsheets():
        _gs_write("operadores", d)

def load_avaliacoes():
    if _use_gsheets():
        data = _gs_read("avaliacoes")
        if data is None:
            return _json_read(EVALS_FILE, [])
        return _fix_numbers(data, ["mp","nota_int"])
    return _json_read(EVALS_FILE, [])

def save_avaliacoes(d):
    d = _none_to_str(d)
    _json_write(EVALS_FILE, d)
    if _use_gsheets():
        _gs_write("avaliacoes", d)

def load_faixas():
    if _use_gsheets():
        data = _gs_read("faixas")
        if data is None or len(data) == 0:
            return DEFAULT_FAIXAS
        return _fix_numbers(data, ["min","max","bonus"])
    return _json_read(FAIXAS_FILE, DEFAULT_FAIXAS)

def save_faixas(d):
    _json_write(FAIXAS_FILE, d)
    if _use_gsheets():
        _gs_write("faixas", d)

def load_usuarios():
    if _use_gsheets():
        data = _gs_read("usuarios")
        if data is None or len(data) == 0:
            return DEFAULT_USUARIOS
        return _str_to_none(data, ["op_id"])
    return _json_read(USERS_FILE, DEFAULT_USUARIOS)

def save_usuarios(d):
    d = _none_to_str(d)
    _json_write(USERS_FILE, d)
    if _use_gsheets():
        _gs_write("usuarios", d)

def storage_status():
    if _use_gsheets():
        return "✅ Google Sheets ativo"
    return "💾 Armazenamento local (JSON)"

def _gs_test_write():
    import traceback
    steps = []
    try:
        steps.append("1/4 Autenticando credenciais...")
        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]), scopes=SCOPES
        )
        gc = gspread.authorize(creds)
        steps.append("✓ Credenciais OK")
        steps.append("2/4 Abrindo planilha...")
        sid = st.secrets["gsheets"]["spreadsheet_id"]
        sh = gc.open_by_key(sid)
        steps.append(f"✓ Planilha: {sh.title}")
        steps.append("3/4 Listando abas...")
        titles = [ws.title for ws in sh.worksheets()]
        steps.append(f"✓ Abas: {titles}")
        steps.append("4/4 Testando leitura...")
        ws_test = sh.worksheet(titles[0]) if titles else sh.add_worksheet("test", 5, 5)
        ws_test.cell(1, 1)
        steps.append("✓ Conexão OK")
        return True, " | ".join(steps)
    except Exception as e:
        tb = traceback.format_exc()
        steps.append(f"ERRO: {e}")
        return False, "\n".join(steps) + f"\n\nDetalhes:\n{tb}"


# ─── Helpers de negócio ───────────────────────────────────────────────────────
def eval_int(e):
    v = e.get("nota_int")
    if v in (None, ""): return None
    try: return float(v)
    except: return None

def eval_final(e, pesos):
    mp = e.get("mp")
    iv = eval_int(e)
    mp_f = None
    if mp not in (None, ""):
        try: mp_f = float(mp)
        except: pass
    if mp_f is None and iv is None:
        return None
    pm = pesos.get("mp", 50) / 100
    pi = pesos.get("int", 50) / 100
    if mp_f is not None and iv is not None:
        return round(mp_f * pm + iv * pi, 2)
    if mp_f is not None:
        return round(mp_f, 2)
    return round(iv, 2)

def get_faixa(nota, faixas):
    if nota is None: return None
    for f in sorted(faixas, key=lambda x: x["min"]):
        if f["min"] <= nota <= f["max"]: return f
    return None

def tenure(adm_str):
    if not adm_str: return "—"
    try:
        adm = datetime.strptime(adm_str, "%Y-%m-%d").date()
        months = max(0, int((date.today() - adm).days / 30.44))
        return f"{months}m" if months < 12 else f"{months//12}a {months%12}m"
    except: return "—"

def nota_cor(v):
    if v is None: return "#52525b"
    return "#d4a853" if v >= 90 else "#f59e0b" if v >= 80 else "#ef4444"

def badge_faixa_html(fx):
    if not fx: return "<span style='color:#3a3a50'>—</span>"
    b = fx["bonus"]
    if b == 0:
        cor, bg, border = "#52525b", "rgba(255,255,255,0.04)", "rgba(255,255,255,0.08)"
    elif b < 150:
        cor, bg, border = "#d97706", "rgba(245,158,11,0.08)", "rgba(245,158,11,0.25)"
    elif b < 300:
        cor, bg, border = "#d4a853", "rgba(212,168,83,0.10)", "rgba(212,168,83,0.28)"
    elif b < 400:
        cor, bg, border = "#d4a853", "rgba(212,168,83,0.12)", "rgba(212,168,83,0.35)"
    else:
        cor, bg, border = "#a78bfa", "rgba(139,92,246,0.10)", "rgba(139,92,246,0.28)"
    return (f"<span class='badge-faixa' style='color:{cor};background:{bg};"
            f"border:1px solid {border};'>{fx['desc']} · R$ {fx['bonus']:.2f}</span>")


# ─── Sessão ───────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
if "pesos" not in st.session_state:
    st.session_state.pesos = {"mp": 50, "int": 50}


# ═══════════════════════════════════════════════════════════════════════════════
# TELA DE LOGIN
# ═══════════════════════════════════════════════════════════════════════════════
def tela_login():
    st.markdown(STARS_JS, unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center;padding-top:3.5rem;position:relative;z-index:2;'>
        <div style='display:inline-block;width:68px;height:68px;border-radius:18px;
                    background:radial-gradient(circle at 40% 40%,rgba(212,168,83,0.15),rgba(0,0,0,0));
                    border:1px solid rgba(212,168,83,0.35);margin-bottom:20px;
                    box-shadow:0 0 40px rgba(212,168,83,0.12);
                    line-height:68px;font-size:30px;'>🌌</div>
        <h1 style='color:#f0f0f8;font-size:30px;font-weight:600;letter-spacing:-0.025em;margin-bottom:4px;'>
            Leal <span style='color:#d4a853'>CX</span>
        </h1>
        <p style='color:#3a3a50;font-size:11px;letter-spacing:0.14em;font-weight:500;margin-bottom:2px;'>
            SISTEMA DE GESTÃO DE QUALIDADE
        </p>
        <p style='color:#3a3a50;font-size:11px;'>Operação Mercado Pago</p>
    </div>
    """, unsafe_allow_html=True)

    _, c2, _ = st.columns([1, 1.0, 1])
    with c2:
        st.markdown("""
        <div style='background:rgba(12,12,20,0.95);border:1px solid rgba(255,255,255,0.08);
                    border-radius:16px;padding:2rem 2rem 1.5rem;margin-top:1.5rem;
                    box-shadow:0 32px 80px rgba(0,0,0,0.7);
                    backdrop-filter:blur(20px);position:relative;z-index:2;'>
            <p style='color:#3a3a50;font-size:10px;letter-spacing:0.1em;
                      font-weight:600;margin-bottom:1.2rem;'>AUTENTICAÇÃO</p>
        """, unsafe_allow_html=True)
        login_i = st.text_input("Login", placeholder="Identificador de acesso", key="lf", label_visibility="collapsed")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        senha_i = st.text_input("Senha", type="password", placeholder="Senha", key="sf", label_visibility="collapsed")
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        entrar = st.button("Entrar", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if entrar:
            u = next((u for u in load_usuarios() if u["login"] == login_i and u["senha"] == senha_i), None)
            if u:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Credenciais inválidas.")

    st.markdown("""
    <div style='text-align:center;margin-top:3rem;color:#1e1e2e;font-size:10px;
                letter-spacing:0.08em;position:relative;z-index:2;'>
        LEAL — CX · QUALIDADE · MERCADO PAGO
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
def render_sidebar(user):
    with st.sidebar:
        nivel = user["nivel"]
        st.markdown(f"""
        <div class='sidebar-logo'>
            <div style='display:flex;align-items:center;gap:10px;'>
                <div style='width:36px;height:36px;border-radius:9px;
                            background:radial-gradient(circle at 40% 40%,rgba(212,168,83,0.15),transparent);
                            border:1px solid rgba(212,168,83,0.3);
                            display:flex;align-items:center;justify-content:center;
                            font-size:17px;flex-shrink:0;
                            box-shadow:0 0 16px rgba(212,168,83,0.1);'>🌌</div>
                <div>
                    <div style='font-size:15px;font-weight:600;color:#f0f0f8;letter-spacing:-0.02em;line-height:1.1;'>
                        Leal <span style='color:#d4a853'>CX</span>
                    </div>
                    <div style='font-size:9px;color:#2a2a3e;letter-spacing:0.12em;font-weight:600;'>QUALIDADE · MP</div>
                </div>
            </div>
        </div>
        <div style='margin:8px 10px 6px;background:rgba(212,168,83,0.05);
                    border:1px solid rgba(212,168,83,0.18);border-radius:10px;padding:11px 13px;'>
            <div style='font-size:9px;color:#3a3a50;letter-spacing:0.08em;font-weight:600;margin-bottom:5px;'>
                SESSÃO ATIVA
            </div>
            <div style='font-size:13px;font-weight:600;color:#f0f0f8;margin-bottom:3px;'>{user['nome']}</div>
            <div style='display:flex;align-items:center;gap:5px;'>
                <div style='width:5px;height:5px;border-radius:50%;background:#d4a853;
                            box-shadow:0 0 5px #d4a853;animation:none;'></div>
                <span style='font-size:10px;color:#d4a853;font-weight:500;'>{NIVEIS.get(nivel, nivel)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if nivel in ("comandante", "copiloto", "observador"):
            if "page" not in st.session_state:
                st.session_state.page = "Dashboard"

            st.markdown("<div style='padding:4px 8px;'>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:9px;color:#2a2a3e;letter-spacing:0.1em;font-weight:600;"
                        "padding:6px 4px 4px;margin-bottom:4px;'>NAVEGAÇÃO</p>", unsafe_allow_html=True)

            pages = [("🏠", "Dashboard"), ("👥", "Operadores"), ("📋", "Avaliações"),
                     ("🏆", "Metas"), ("📈", "Evolução")]
            if nivel == "comandante":
                pages.append(("⚙️", "Configurações"))

            for icon, pg in pages:
                is_active = st.session_state.page == pg
                prefix = "▸ " if is_active else ""
                if st.button(f"{icon}  {prefix}{pg}", key=f"nav_{pg}", use_container_width=True):
                    st.session_state.page = pg
                    st.rerun()

        st.markdown("---")
        st.markdown(
            f"<p style='font-size:10px;color:#2a2a3e;padding:0 4px;line-height:1.5;'>"
            f"{storage_status()}</p>",
            unsafe_allow_html=True
        )
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.button("↩ Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_dashboard(user, readonly=False):
    st.markdown("""
    <div class='page-header'>
        <div style='display:flex;align-items:center;gap:12px;'>
            <div style='width:40px;height:40px;border-radius:10px;
                        background:rgba(212,168,83,0.06);border:1px solid rgba(212,168,83,0.2);
                        display:flex;align-items:center;justify-content:center;font-size:18px;
                        box-shadow:0 0 16px rgba(212,168,83,0.08);'>🏠</div>
            <div>
                <h1 style='margin:0;'>Dashboard</h1>
                <p style='margin:0;font-size:11px;color:#3a3a50;'>Visão geral da operação</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"<p style='color:#3a3a50;font-size:11px;margin-top:-1rem;margin-bottom:1.5rem;'>"
        f"Atualizado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>",
        unsafe_allow_html=True
    )

    ops    = load_operadores()
    evs    = load_avaliacoes()
    faixas = load_faixas()
    pesos  = st.session_state.pesos
    ativos = [o for o in ops if o.get("status") == "Ativo"]

    all_mps  = [float(e["mp"]) for e in evs if e.get("mp") not in (None, "")]
    all_ivs  = [eval_int(e) for e in evs if eval_int(e) is not None]
    all_fins = [eval_final(e, pesos) for e in evs if eval_final(e, pesos) is not None]

    avg_mp  = round(sum(all_mps) / len(all_mps), 1) if all_mps else None
    avg_iv  = round(sum(all_ivs) / len(all_ivs), 1) if all_ivs else None
    avg_fin = round(sum(all_fins) / len(all_fins), 1) if all_fins else None

    total_bonus = 0
    for op in ativos:
        op_evs = sorted(
            [e for e in evs if e["op_id"] == op["id"]],
            key=lambda x: (x.get("mes", ""), x.get("ciclo", "")), reverse=True
        )
        if op_evs:
            fx = get_faixa(eval_final(op_evs[0], pesos), faixas)
            total_bonus += fx["bonus"] if fx else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("👥 Ativos",           len(ativos),                   f"de {len(ops)}")
    c2.metric("📋 Avaliações",        len(evs))
    c3.metric("🎯 Média MP",          f"{avg_mp:.1f}"  if avg_mp  is not None else "—")
    c4.metric("📝 Média interna",     f"{avg_iv:.1f}"  if avg_iv  is not None else "—")
    c5.metric("🏆 Nota final média",  f"{avg_fin:.1f}%" if avg_fin is not None else "—")
    c6.metric("💰 Total bonificação", f"R$ {total_bonus:.2f}")

    st.markdown("---")
    meses_disp = sorted(set(e.get("mes", "") for e in evs if e.get("mes")), reverse=True)
    col_s, _ = st.columns([2, 4])
    mes_sel = col_s.selectbox("📅 Filtrar mês", ["Todos"] + meses_disp, key="dash_mes")

    # ── Tabela resumo ──
    st.markdown("### 🧑‍🚀 Resumo da equipe")
    rows = []
    for op in ativos:
        op_evs = [e for e in evs if e["op_id"] == op["id"]]
        if mes_sel != "Todos":
            op_evs = [e for e in op_evs if e.get("mes") == mes_sel]
        op_evs = sorted(op_evs, key=lambda x: x.get("ciclo", ""), reverse=True)
        last = op_evs[0] if op_evs else None
        mp_v = float(last["mp"]) if last and last.get("mp") not in (None, "") else None
        iv_v = eval_int(last) if last else None
        fn_v = eval_final(last, pesos) if last else None
        fx   = get_faixa(fn_v, faixas)
        rows.append({
            "Operador":      op["nome"],
            "Tempo de casa": tenure(op.get("adm")),
            "Nota MP":       f"{mp_v:.1f}" if mp_v is not None else "—",
            "Nota interna":  f"{iv_v:.1f}" if iv_v is not None else "—",
            "Nota final":    f"{fn_v:.1f}%" if fn_v is not None else "—",
            "Faixa":         fx["desc"] if fx else "—",
            "Bônus":         f"R$ {fx['bonus']:.2f}" if fx else "R$ 0,00",
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Cadastre operadores e avaliações para ver o resumo.")

    # ── Gráficos por ciclo ──
    if mes_sel != "Todos" and PLOTLY_AVAILABLE:
        st.markdown(f"### 📊 Desempenho por ciclo — {mes_sel}")
        col_l, col_r = st.columns(2)

        # Linha: médias da equipe por ciclo
        with col_l:
            series_data = {}
            ciclos_com_dados = []
            for ciclo in CICLOS:
                cevs = [e for e in evs if e.get("mes") == mes_sel and e.get("ciclo") == ciclo]
                if not cevs:
                    continue
                fps = [eval_final(e, pesos) for e in cevs if eval_final(e, pesos) is not None]
                mps = [float(e["mp"]) for e in cevs if e.get("mp") not in (None, "")]
                if fps:
                    ciclos_com_dados.append(ciclo)
                    series_data["Nota final"] = series_data.get("Nota final", []) + [round(sum(fps)/len(fps), 1)]
                    if mps:
                        series_data["Nota MP"] = series_data.get("Nota MP", []) + [round(sum(mps)/len(mps), 1)]

            if series_data and ciclos_com_dados:
                fig = plotly_ciclo_line(ciclos_com_dados, series_data)
                st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CFG)

        # Donut: distribuição por faixa
        with col_r:
            fx_counts = {}
            for op in ativos:
                op_evs = [e for e in evs if e["op_id"] == op["id"] and e.get("mes") == mes_sel]
                fn_vals = [eval_final(e, pesos) for e in op_evs if eval_final(e, pesos) is not None]
                fn_med  = round(sum(fn_vals)/len(fn_vals), 1) if fn_vals else None
                fx = get_faixa(fn_med, faixas)
                key = fx["desc"] if fx else "Sem avaliação"
                fx_counts[key] = fx_counts.get(key, 0) + 1

            if fx_counts:
                fx_colors = {
                    "Faixa Diamante": PURPLE, "Faixa Ouro": GOLD, "Faixa Prata": SLATE,
                    "Faixa Bronze": AMBER, "Abaixo da meta": RED, "Sem avaliação": "#2a2a3e"
                }
                labels_d = list(fx_counts.keys())
                values_d = list(fx_counts.values())
                colors_d = [fx_colors.get(l, SLATE) for l in labels_d]
                fig2 = plotly_donut(labels_d, values_d, colors_d)
                st.plotly_chart(fig2, use_container_width=True, config=PLOTLY_CFG)

    # ── Metas mês atual ──
    st.markdown("---")
    st.markdown("### 🏆 Situação de metas — mês mais recente")
    mes_rec = meses_disp[0] if meses_disp else None
    if mes_rec:
        for op in ativos:
            op_evs = [e for e in evs if e["op_id"] == op["id"] and e.get("mes") == mes_rec]
            if not op_evs: continue
            fn_vals = [eval_final(e, pesos) for e in op_evs if eval_final(e, pesos) is not None]
            fn_med  = round(sum(fn_vals)/len(fn_vals), 1) if fn_vals else None
            fx = get_faixa(fn_med, faixas)
            cor = nota_cor(fn_med)
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:12px;padding:9px 0;"
                f"border-bottom:1px solid rgba(255,255,255,0.04);'>"
                f"<span style='flex:1;color:#d0d0e8;font-size:13px;'>{op['nome']}</span>"
                f"{'<span style=\"font-weight:700;color:' + cor + ';font-size:14px;\">' + str(fn_med) + '%</span>' if fn_med else '<span style=\"color:#3a3a50\">sem avaliação</span>'}"
                f"<span style='min-width:180px;text-align:right;'>{badge_faixa_html(fx)}</span>"
                f"</div>",
                unsafe_allow_html=True
            )


# ═══════════════════════════════════════════════════════════════════════════════
# OPERADORES
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_operadores(user, readonly=False):
    st.markdown("""
    <div class='page-header'>
        <div style='display:flex;align-items:center;gap:12px;'>
            <div style='width:40px;height:40px;border-radius:10px;
                        background:rgba(212,168,83,0.06);border:1px solid rgba(212,168,83,0.2);
                        display:flex;align-items:center;justify-content:center;font-size:18px;'>👥</div>
            <div>
                <h1 style='margin:0;'>Operadores</h1>
                <p style='margin:0;font-size:11px;color:#3a3a50;'>Cadastro, tempo de casa e acompanhamento</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    ops    = load_operadores()
    evs    = load_avaliacoes()
    faixas = load_faixas()
    pesos  = st.session_state.pesos

    if not readonly:
        with st.expander("➕ Cadastrar novo operador", expanded=False):
            with st.form("form_op"):
                c1, c2 = st.columns(2)
                nome   = c1.text_input("Nome completo")
                cargo  = c2.selectbox("Cargo", CARGOS_OP + CARGOS_GESTAO)
                c3, c4 = st.columns(2)
                adm    = c3.date_input("Data de admissão", value=date.today())
                status = c4.selectbox("Status", ["Ativo", "Afastado", "Desligado"])
                notas  = st.text_area("Observações gerais", height=70)
                st.markdown("**Login de acesso (Tripulação)**")
                c5, c6 = st.columns(2)
                login_op = c5.text_input("Login", placeholder="Ex.: ana.silva")
                senha_op = c6.text_input("Senha", type="password", placeholder="Ex.: cx2024")
                if st.form_submit_button("🚀 Salvar operador"):
                    if not nome.strip():
                        st.error("Informe o nome.")
                    else:
                        op_id = f"op_{int(datetime.now().timestamp()*1000)}"
                        ops.append({
                            "id": op_id, "nome": nome.strip(), "cargo": cargo,
                            "adm": adm.strftime("%Y-%m-%d"), "status": status, "notas": notas
                        })
                        save_operadores(ops)
                        if login_op.strip() and senha_op.strip():
                            usu = load_usuarios()
                            if any(u["login"] == login_op.strip() for u in usu):
                                st.warning(f"Login '{login_op}' já existe. Operador salvo sem login.")
                            else:
                                usu.append({
                                    "login": login_op.strip(), "senha": senha_op.strip(),
                                    "nivel": "tripulacao", "nome": nome.strip(), "op_id": op_id
                                })
                                save_usuarios(usu)
                        st.success(f"✅ {nome} cadastrado!")
                        st.rerun()

    st.markdown("---")
    c1, c2 = st.columns([3, 1])
    busca  = c1.text_input("🔍 Buscar", placeholder="Nome...")
    filtro = c2.selectbox("Status", ["Todos", "Ativo", "Afastado", "Desligado"], key="op_f")
    lista  = [o for o in ops
              if (not busca or busca.lower() in o["nome"].lower())
              and (filtro == "Todos" or o.get("status") == filtro)]

    if not lista:
        st.info("Nenhum operador encontrado.")
        return

    for op in lista:
        op_evs = sorted(
            [e for e in evs if e["op_id"] == op["id"]],
            key=lambda x: (x.get("mes", ""), x.get("ciclo", "")), reverse=True
        )
        last = op_evs[0] if op_evs else None
        fn   = eval_final(last, pesos) if last else None
        fx   = get_faixa(fn, faixas)

        with st.expander(f"🧑‍🚀 {op['nome']} — {op.get('cargo','—')} · {tenure(op.get('adm'))}"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Status", op.get("status", "—"))
            c2.metric("Tempo de casa", tenure(op.get("adm")))
            if last:
                mp_v = float(last["mp"]) if last.get("mp") not in (None, "") else None
                iv_v = eval_int(last)
                c3.metric("Nota MP (última)", f"{mp_v:.1f}" if mp_v is not None else "—")
                c4.metric("Nota interna (última)", f"{iv_v:.1f}" if iv_v is not None else "—")
            if op.get("notas"):
                st.markdown(f"*{op['notas']}*")
            if fn is not None:
                pct = min(100, max(0, fn))
                st.markdown(f"**Nota final: {fn:.1f}%**")
                st.progress(pct / 100)
                st.markdown(badge_faixa_html(fx), unsafe_allow_html=True)
                proxima = next(
                    (f for f in sorted(faixas, key=lambda x: x["min"]) if f["min"] > fn), None
                )
                if proxima:
                    st.markdown(
                        f"<p style='color:#818cf8;font-size:13px;'>⭐ Faltam <b>{round(proxima['min']-fn,2)} pontos</b> "
                        f"para {proxima['desc']} (R$ {proxima['bonus']:.2f})</p>",
                        unsafe_allow_html=True
                    )
            if not readonly:
                if st.button("🗑️ Excluir operador", key=f"del_{op['id']}"):
                    ops = [o for o in ops if o["id"] != op["id"]]
                    save_operadores(ops)
                    st.success("Removido.")
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# AVALIAÇÕES
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_avaliacoes(user, readonly=False):
    st.markdown("""
    <div class='page-header'>
        <div style='display:flex;align-items:center;gap:12px;'>
            <div style='width:40px;height:40px;border-radius:10px;
                        background:rgba(212,168,83,0.06);border:1px solid rgba(212,168,83,0.2);
                        display:flex;align-items:center;justify-content:center;font-size:18px;'>📋</div>
            <div>
                <h1 style='margin:0;'>Avaliações</h1>
                <p style='margin:0;font-size:11px;color:#3a3a50;'>Notas MP, nota interna, feedbacks e plano de ação</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    ops   = load_operadores()
    evs   = load_avaliacoes()
    pesos = st.session_state.pesos
    ativ  = [o for o in ops if o.get("status") == "Ativo"]

    if not readonly and ativ:
        with st.expander("➕ Registrar nova avaliação", expanded=False):
            with st.form("form_eval"):
                op_map   = {o["nome"]: o["id"] for o in ativ}
                c1, c2, c3 = st.columns(3)
                op_nome  = c1.selectbox("Operador", list(op_map.keys()))
                mes_sel  = c2.selectbox("Mês de referência", MESES_LABEL)
                ciclo_s  = c3.selectbox("Ciclo / Semana", CICLOS)
                st.markdown("---")
                c4, c5 = st.columns(2)
                with c4:
                    st.markdown("**🎯 Nota Mercado Pago (0–100)**")
                    mp_val = st.number_input("Nota MP", 0.0, 100.0, step=0.1, format="%.1f", key="nmp")
                with c5:
                    st.markdown("**📝 Nota Avaliação Interna (0–100)**")
                    int_val = st.number_input("Nota interna", 0.0, 100.0, step=0.1, format="%.1f", key="nint")
                st.markdown("---")
                c6, c7   = st.columns(2)
                feed_val = c6.text_area("Pontos de melhoria", height=90)
                pos_val  = c7.text_area("Pontos positivos", height=90)
                acao_val = st.text_input("Plano de ação / Desenvolvimento")
                if st.form_submit_button("💾 Salvar avaliação"):
                    ev = {
                        "id":       f"ev_{int(datetime.now().timestamp()*1000)}",
                        "op_id":    op_map[op_nome],
                        "mes":      mes_sel, "ciclo": ciclo_s,
                        "mp":       mp_val, "nota_int": int_val,
                        "feed":     feed_val, "pos": pos_val,
                        "acao":     acao_val,
                        "criado":   datetime.now().isoformat(),
                    }
                    evs.append(ev)
                    save_avaliacoes(evs)
                    st.success(f"✅ Avaliação de {op_nome} — {mes_sel} / {ciclo_s} salva!")
                    st.rerun()

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    op_f  = c1.selectbox("Operador", ["Todos"] + [o["nome"] for o in ops], key="evop")
    mes_f = c2.selectbox("Mês", ["Todos"] + sorted(set(e.get("mes", "") for e in evs if e.get("mes")), reverse=True), key="evmes")
    cic_f = c3.selectbox("Ciclo", ["Todos"] + CICLOS, key="evci")

    lista = evs
    if op_f  != "Todos": lista = [e for e in lista if e["op_id"] == next((o["id"] for o in ops if o["nome"] == op_f), None)]
    if mes_f != "Todos": lista = [e for e in lista if e.get("mes") == mes_f]
    if cic_f != "Todos": lista = [e for e in lista if e.get("ciclo") == cic_f]
    lista = sorted(lista, key=lambda x: (x.get("mes", ""), x.get("ciclo", "")), reverse=True)

    if not lista:
        st.info("Nenhuma avaliação encontrada.")
        return

    rows = []
    for e in lista:
        op   = next((o for o in ops if o["id"] == e["op_id"]), {})
        iv   = eval_int(e)
        fn   = eval_final(e, pesos)
        mp_v = e.get("mp")
        rows.append({
            "Operador":      op.get("nome", "—"),
            "Mês":           e.get("mes", "—"),
            "Ciclo":         e.get("ciclo", "—"),
            "Nota MP":       f"{float(mp_v):.1f}" if mp_v not in (None, "") else "—",
            "Nota interna":  f"{iv:.1f}"           if iv is not None else "—",
            "Nota final":    f"{fn:.1f}%"          if fn is not None else "—",
            "Plano de ação": e.get("acao", "—"),
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Exportar CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"leal_cx_avaliacoes_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# METAS
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_metas(user, readonly=False):
    st.markdown("""
    <div class='page-header'>
        <div style='display:flex;align-items:center;gap:12px;'>
            <div style='width:40px;height:40px;border-radius:10px;
                        background:rgba(212,168,83,0.06);border:1px solid rgba(212,168,83,0.2);
                        display:flex;align-items:center;justify-content:center;font-size:18px;'>🏆</div>
            <div>
                <h1 style='margin:0;'>Metas e Bonificações</h1>
                <p style='margin:0;font-size:11px;color:#3a3a50;'>Faixas configuráveis e resultado por operador</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    faixas = load_faixas()
    ops    = load_operadores()
    evs    = load_avaliacoes()
    pesos  = st.session_state.pesos

    c_p, c_f = st.columns([1, 2])
    with c_p:
        st.markdown("### ⚖️ Pesos da nota final")
        if not readonly:
            pm = st.slider("Peso Nota MP (%)",      0, 100, pesos.get("mp", 50),  step=5)
            pi = st.slider("Peso Nota interna (%)", 0, 100, pesos.get("int", 50), step=5)
            if pm + pi != 100:
                st.warning(f"Soma: {pm+pi}% (deve ser 100%)")
            else:
                st.session_state.pesos = {"mp": pm, "int": pi}
                st.success("✓ Pesos salvos")
        else:
            st.markdown(f"- Nota MP: **{pesos['mp']}%**  \n- Nota interna: **{pesos['int']}%**")

    with c_f:
        st.markdown("### 🎯 Faixas de bonificação")
        for f in sorted(faixas, key=lambda x: x["min"]):
            cc1, cc2, cc3, cc4 = st.columns([3, 2, 2, 1])
            cc1.markdown(f"**{f['desc']}**")
            cc2.markdown(f"{f['min']}% – {f['max']}%")
            cc3.markdown(f"R$ {f['bonus']:.2f}")
            if not readonly and cc4.button("🗑️", key=f"delf_{f['id']}"):
                faixas = [x for x in faixas if x["id"] != f["id"]]
                save_faixas(faixas)
                st.rerun()
        if not readonly:
            st.markdown("---")
            with st.form("ff"):
                c1, c2, c3, c4 = st.columns(4)
                fd = c1.text_input("Descrição")
                fn = c2.number_input("Mín (%)", 0.0, 100.0, step=0.1)
                fm = c3.number_input("Máx (%)", 0.0, 100.0, step=0.1)
                fb = c4.number_input("Bônus R$", 0.0, step=0.01)
                if st.form_submit_button("➕ Adicionar faixa"):
                    if not fd.strip():
                        st.error("Informe a descrição.")
                    elif fn > fm:
                        st.error("Mínimo maior que máximo.")
                    else:
                        faixas.append({
                            "id": f"f_{int(datetime.now().timestamp()*1000)}",
                            "desc": fd, "min": fn, "max": fm, "bonus": fb
                        })
                        save_faixas(faixas)
                        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Resultado por mês")
    meses = sorted(set(e.get("mes", "") for e in evs if e.get("mes")), reverse=True)
    if not meses:
        st.info("Nenhuma avaliação registrada ainda.")
        return

    col_m, _ = st.columns([2, 4])
    mes_sel   = col_m.selectbox("Mês", meses, key="metas_mes")

    ativos = [o for o in ops if o.get("status") == "Ativo"]
    rows = []; total_b = 0
    for op in ativos:
        op_evs  = [e for e in evs if e["op_id"] == op["id"] and e.get("mes") == mes_sel]
        fn_vals = [eval_final(e, pesos) for e in op_evs if eval_final(e, pesos) is not None]
        mp_vals = [float(e["mp"]) for e in op_evs if e.get("mp") not in (None, "")]
        iv_vals = [eval_int(e) for e in op_evs if eval_int(e) is not None]
        fn_med  = round(sum(fn_vals)/len(fn_vals), 1) if fn_vals else None
        mp_med  = round(sum(mp_vals)/len(mp_vals), 1) if mp_vals else None
        iv_med  = round(sum(iv_vals)/len(iv_vals), 1) if iv_vals else None
        fx  = get_faixa(fn_med, faixas)
        bv  = fx["bonus"] if fx else 0
        total_b += bv
        sit = "✅ Meta atingida" if fn_med and fn_med >= 80 else ("⚠️ Abaixo" if fn_med is not None else "📭 Sem avaliação")
        rows.append({
            "Operador":   op["nome"],
            "Nota MP":    f"{mp_med:.1f}" if mp_med else "—",
            "Nota int.":  f"{iv_med:.1f}" if iv_med else "—",
            "Nota final": f"{fn_med:.1f}%" if fn_med else "—",
            "Faixa":      fx["desc"] if fx else "—",
            "Bônus":      f"R$ {bv:.2f}",
            "Situação":   sit,
        })

    if rows:
        # Gráfico de barras horizontais
        if PLOTLY_AVAILABLE:
            nomes = [r["Operador"] for r in rows]
            notas = [float(r["Nota final"].replace("%","")) if r["Nota final"] != "—" else None for r in rows]
            fig_bar = plotly_bar_h(nomes, notas)
            st.plotly_chart(fig_bar, use_container_width=True, config=PLOTLY_CFG)

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.markdown(
            f"<p style='color:#818cf8;font-weight:600;font-size:14px;'>"
            f"💰 Total bonificação da equipe ({mes_sel}): R$ {total_b:.2f}</p>",
            unsafe_allow_html=True
        )
        csv = pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Exportar CSV metas", data=csv,
            file_name=f"leal_cx_metas_{mes_sel}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhuma avaliação para este mês.")


# ═══════════════════════════════════════════════════════════════════════════════
# EVOLUÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_evolucao(user, readonly=False):
    st.markdown("""
    <div class='page-header'>
        <div style='display:flex;align-items:center;gap:12px;'>
            <div style='width:40px;height:40px;border-radius:10px;
                        background:rgba(212,168,83,0.06);border:1px solid rgba(212,168,83,0.2);
                        display:flex;align-items:center;justify-content:center;font-size:18px;'>📈</div>
            <div>
                <h1 style='margin:0;'>Evolução</h1>
                <p style='margin:0;font-size:11px;color:#3a3a50;'>Progressão da equipe e individual ao longo dos meses</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    ops   = load_operadores()
    evs   = load_avaliacoes()
    pesos = st.session_state.pesos

    if not evs:
        st.info("Registre avaliações para ver a evolução.")
        return

    meses = sorted(set(e.get("mes", "") for e in evs if e.get("mes")))

    c1, c2 = st.columns(2)
    opcao   = c1.selectbox("Visualizar", ["Média da equipe"] + [o["nome"] for o in ops])
    metrica = c2.selectbox("Métrica", ["Nota final (%)", "Nota MP", "Nota interna"])

    def get_val(e, met):
        if met == "Nota final (%)": return eval_final(e, pesos)
        if met == "Nota MP":        return float(e["mp"]) if e.get("mp") not in (None, "") else None
        if met == "Nota interna":   return eval_int(e)

    # Série por mês
    data_m = {}
    for mes in meses:
        m_evs = [e for e in evs if e.get("mes") == mes]
        if opcao != "Média da equipe":
            op = next((o for o in ops if o["nome"] == opcao), None)
            m_evs = [e for e in m_evs if op and e["op_id"] == op["id"]]
        vals = [get_val(e, metrica) for e in m_evs if get_val(e, metrica) is not None]
        data_m[mes] = round(sum(vals)/len(vals), 1) if vals else None

    df_m = pd.DataFrame({"Mês": list(data_m.keys()), metrica: list(data_m.values())}).dropna()

    if not df_m.empty and PLOTLY_AVAILABLE:
        st.markdown(f"### 🌌 {opcao} — {metrica} por mês")
        datasets_m = [{"label": metrica, "data": df_m[metrica].tolist()}]
        fig_ev = plotly_line(df_m["Mês"].tolist(), datasets_m)
        st.plotly_chart(fig_ev, use_container_width=True, config=PLOTLY_CFG)
    elif not df_m.empty:
        st.line_chart(df_m.set_index("Mês"))

    # Comparativo operadores no mês mais recente
    st.markdown("---")
    mes_rec = meses[-1] if meses else None
    if mes_rec and PLOTLY_AVAILABLE:
        st.markdown(f"### 🧑‍🚀 Comparativo — {mes_rec}")
        comp = []
        for op in ops:
            op_evs = [e for e in evs if e["op_id"] == op["id"] and e.get("mes") == mes_rec]
            vals = [get_val(e, metrica) for e in op_evs if get_val(e, metrica) is not None]
            if vals:
                comp.append({"Operador": op["nome"], metrica: round(sum(vals)/len(vals), 1)})
        if comp:
            df_c   = pd.DataFrame(comp).sort_values(metrica, ascending=True)
            fig_c  = plotly_bar_h(df_c["Operador"].tolist(), df_c[metrica].tolist())
            st.plotly_chart(fig_c, use_container_width=True, config=PLOTLY_CFG)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_configuracoes(user):
    st.markdown("""
    <div class='page-header'>
        <div style='display:flex;align-items:center;gap:12px;'>
            <div style='width:40px;height:40px;border-radius:10px;
                        background:rgba(212,168,83,0.06);border:1px solid rgba(212,168,83,0.2);
                        display:flex;align-items:center;justify-content:center;font-size:18px;'>⚙️</div>
            <div>
                <h1 style='margin:0;'>Configurações</h1>
                <p style='margin:0;font-size:11px;color:#3a3a50;'>Usuários, credenciais e backup de dados</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if _use_gsheets():
        st.markdown("### 🔌 Diagnóstico da conexão")
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(
                f"<p style='font-size:12px;color:#6b6b88;'>ID da planilha: "
                f"<code>{st.secrets['gsheets']['spreadsheet_id']}</code></p>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<p style='font-size:12px;color:#6b6b88;'>Conta de serviço: "
                f"<code>{st.secrets['gcp_service_account'].get('client_email','?')}</code></p>",
                unsafe_allow_html=True
            )
        with c2:
            if st.button("🧪 Testar conexão", use_container_width=True):
                with st.spinner("Testando..."):
                    ok, msg = _gs_test_write()
                if ok:
                    st.success("✅ Conexão funcionando!")
                    with st.expander("Ver detalhes"):
                        for linha in msg.split(" | "):
                            st.markdown(f"- {linha}")
                else:
                    st.error("❌ Falhou")
                    st.code(msg, language="text")
        st.markdown("---")

    st.markdown("### 👤 Usuários do sistema")
    usuarios = load_usuarios()

    st.markdown("**Editar usuários de gestão**")
    for i, u in enumerate(usuarios):
        if u.get("nivel") == "tripulacao": continue
        with st.expander(f"✏️ {u['nome']} — `{u['login']}` — {NIVEIS.get(u['nivel'], u['nivel'])}"):
            with st.form(f"edit_user_{u['login']}"):
                novo_nome  = st.text_input("Nome de exibição", value=u.get("nome", ""), key=f"nn_{i}")
                novo_login = st.text_input("Login", value=u.get("login", ""), key=f"nl_{i}")
                nova_senha = st.text_input("Nova senha (deixe vazio para manter)", type="password", key=f"ns_{i}")
                if st.form_submit_button("💾 Salvar alterações"):
                    outros_logins = [x["login"] for x in usuarios if x["login"] != u["login"]]
                    if novo_login.strip() in outros_logins:
                        st.error("Este login já está em uso.")
                    else:
                        for uu in usuarios:
                            if uu["login"] == u["login"]:
                                uu["nome"]  = novo_nome.strip() or uu["nome"]
                                uu["login"] = novo_login.strip() or uu["login"]
                                if nova_senha.strip():
                                    if len(nova_senha.strip()) < 4:
                                        st.error("Senha muito curta.")
                                        break
                                    uu["senha"] = nova_senha.strip()
                        save_usuarios(usuarios)
                        if u["login"] == user["login"] or novo_login.strip() == user["login"]:
                            updated = next(
                                (x for x in load_usuarios() if x["login"] == novo_login.strip()), None
                            )
                            if updated:
                                st.session_state.user = updated
                        st.success("✅ Usuário atualizado!")
                        st.rerun()

    st.markdown("---")
    st.markdown("**Todos os usuários**")
    for u in usuarios:
        c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
        c1.markdown(f"**{u['nome']}**")
        c2.markdown(f"`{u['login']}`")
        c3.markdown(NIVEIS.get(u["nivel"], u["nivel"]))
        if u["nivel"] != "comandante" and c4.button("🗑️", key=f"delu_{u['login']}"):
            usuarios = [x for x in usuarios if x["login"] != u["login"]]
            save_usuarios(usuarios)
            st.rerun()

    st.markdown("---")
    st.markdown("### 💾 Backup")
    backup = {
        "exportado_em": datetime.now().isoformat(),
        "operadores":   load_operadores(),
        "avaliacoes":   load_avaliacoes(),
        "faixas":       load_faixas(),
        "pesos":        st.session_state.pesos,
    }
    st.download_button(
        "⬇️ Baixar backup JSON",
        data=json.dumps(backup, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name=f"leal_cx_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json"
    )

    st.markdown("### 📥 Importar backup")
    arq = st.file_uploader("Arquivo .json", type=["json"])
    if arq:
        try:
            d = json.load(arq)
            if st.button("⚠️ Confirmar importação"):
                if "operadores" in d: save_operadores(d["operadores"])
                if "avaliacoes" in d: save_avaliacoes(d["avaliacoes"])
                if "faixas"     in d: save_faixas(d["faixas"])
                if "pesos"      in d: st.session_state.pesos = d["pesos"]
                st.success("Dados importados!")
                st.rerun()
        except Exception as ex:
            st.error(f"Erro: {ex}")


# ═══════════════════════════════════════════════════════════════════════════════
# PORTAL DA TRIPULAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
def portal_tripulacao(user):
    ops    = load_operadores()
    evs    = load_avaliacoes()
    faixas = load_faixas()
    pesos  = st.session_state.pesos

    op = next((o for o in ops if o["id"] == user.get("op_id")), None)
    if not op:
        st.error("Operador não encontrado. Contate o administrador.")
        return

    st.markdown(f"""
    <div style='padding:1.5rem 0 1rem;'>
        <div style='display:flex;align-items:center;gap:16px;margin-bottom:4px;'>
            <div style='width:54px;height:54px;border-radius:14px;
                        background:radial-gradient(circle at 40% 40%,rgba(212,168,83,0.15),transparent);
                        border:1px solid rgba(212,168,83,0.3);
                        display:flex;align-items:center;justify-content:center;
                        font-size:22px;font-weight:700;color:#d4a853;
                        box-shadow:0 0 24px rgba(212,168,83,0.12);'>
                {op['nome'][0].upper()}
            </div>
            <div>
                <h1 style='margin:0;font-size:24px;'>Olá, {op['nome'].split()[0]}!</h1>
                <p style='margin:0;font-size:12px;color:#52525b;'>{op.get('cargo','Operador(a)')} · {tenure(op.get('adm'))} de empresa</p>
            </div>
        </div>
    </div>
    <hr/>
    """, unsafe_allow_html=True)

    op_evs = sorted(
        [e for e in evs if e["op_id"] == op["id"]],
        key=lambda x: (x.get("mes", ""), x.get("ciclo", "")), reverse=True
    )

    if not op_evs:
        st.info("Você ainda não possui avaliações registradas.")
        return

    last = op_evs[0]
    fn   = eval_final(last, pesos)
    fx   = get_faixa(fn, faixas)
    iv   = eval_int(last)
    mp_v = float(last["mp"]) if last.get("mp") not in (None, "") else None

    st.markdown(
        f"<p style='color:#52525b;font-size:11px;font-weight:500;letter-spacing:0.06em;margin-bottom:0.8rem;'>"
        f"ÚLTIMA AVALIAÇÃO — {last.get('mes','—')} / {last.get('ciclo','—')}</p>",
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Nota MP",      f"{mp_v:.1f}" if mp_v is not None else "—")
    c2.metric("Nota interna", f"{iv:.1f}"   if iv  is not None else "—")
    c3.metric("Nota final",   f"{fn:.1f}%"  if fn  is not None else "—")

    if fn is not None:
        pct = min(100, max(0, fn))
        cor = nota_cor(fn)
        st.markdown(f"""
        <div style='background:#0c0c14;border:1px solid rgba(255,255,255,0.07);border-radius:12px;
                    padding:20px;margin:1rem 0;'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;'>
                <span style='font-size:10px;color:#3a3a50;font-weight:600;letter-spacing:0.07em;'>
                    PROGRESSO DA META
                </span>
                <span style='font-size:22px;font-weight:600;color:{cor};'>{fn:.1f}%</span>
            </div>
            <div style='height:7px;background:#111120;border-radius:4px;overflow:hidden;'>
                <div style='height:100%;width:{pct}%;
                            background:linear-gradient(90deg,#92400e,{cor});
                            border-radius:4px;box-shadow:0 0 12px rgba(212,168,83,0.3);
                            transition:width 0.5s ease;'></div>
            </div>
            <div style='display:flex;justify-content:space-between;margin-top:7px;
                        font-size:10px;color:#2a2a3e;'>
                <span>0%</span><span>50%</span><span>100%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(badge_faixa_html(fx), unsafe_allow_html=True)
        proxima = next((f for f in sorted(faixas, key=lambda x: x["min"]) if f["min"] > fn), None)
        if proxima:
            falta = round(proxima["min"] - fn, 2)
            st.markdown(
                f"<p style='color:#d4a853;font-size:13px;margin-top:8px;'>"
                f"✦ Faltam <b>{falta} pontos</b> para <b>{proxima['desc']}</b> → R$ {proxima['bonus']:.2f}</p>",
                unsafe_allow_html=True
            )
        else:
            st.markdown("<p style='color:#f0c96a;font-weight:600;'>🏆 Você atingiu a faixa máxima!</p>", unsafe_allow_html=True)

    if last.get("pos") or last.get("feed") or last.get("acao"):
        st.markdown("---")
        st.markdown(
            "<p style='color:#3a3a50;font-size:10px;font-weight:600;letter-spacing:0.07em;margin-bottom:0.8rem;'>"
            "FEEDBACK DA AVALIAÇÃO</p>",
            unsafe_allow_html=True
        )
        if last.get("pos"):
            st.markdown(
                f"<div style='background:#0c0c14;border:1px solid rgba(255,255,255,0.06);"
                f"border-left:2px solid #22c55e;border-radius:0 8px 8px 0;padding:16px;margin-bottom:10px;'>"
                f"<p style='color:#22c55e;font-size:10px;font-weight:600;letter-spacing:0.06em;margin-bottom:8px;'>✓ PONTOS POSITIVOS</p>"
                f"<p style='color:#9898b8;font-size:13px;line-height:1.6;margin:0;'>{last['pos']}</p></div>",
                unsafe_allow_html=True
            )
        if last.get("feed"):
            st.markdown(
                f"<div style='background:#0c0c14;border:1px solid rgba(255,255,255,0.06);"
                f"border-left:2px solid #f59e0b;border-radius:0 8px 8px 0;padding:16px;margin-bottom:10px;'>"
                f"<p style='color:#f59e0b;font-size:10px;font-weight:600;letter-spacing:0.06em;margin-bottom:8px;'>⚠ PONTOS DE MELHORIA</p>"
                f"<p style='color:#9898b8;font-size:13px;line-height:1.6;margin:0;'>{last['feed']}</p></div>",
                unsafe_allow_html=True
            )
        if last.get("acao"):
            st.markdown(
                f"<div style='background:#0c0c14;border:1px solid rgba(255,255,255,0.06);"
                f"border-left:2px solid #d4a853;border-radius:0 8px 8px 0;padding:16px;'>"
                f"<p style='color:#d4a853;font-size:10px;font-weight:600;letter-spacing:0.06em;margin-bottom:8px;'>→ PLANO DE AÇÃO</p>"
                f"<p style='color:#9898b8;font-size:13px;line-height:1.6;margin:0;'>{last['acao']}</p></div>",
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.markdown(
        "<p style='color:#3a3a50;font-size:10px;font-weight:600;letter-spacing:0.07em;margin-bottom:0.8rem;'>"
        "EVOLUÇÃO — NOTA FINAL POR MÊS E CICLO</p>",
        unsafe_allow_html=True
    )

    chart_rows = []
    for e in sorted(op_evs, key=lambda x: (x.get("mes", ""), x.get("ciclo", ""))):
        fn_e = eval_final(e, pesos)
        if fn_e is not None:
            chart_rows.append({
                "Período":       f"{e.get('mes','?')} / {e.get('ciclo','?')}",
                "Nota final (%)": fn_e,
                "Nota MP":       float(e["mp"]) if e.get("mp") not in (None, "") else None,
                "Nota interna":  eval_int(e),
            })

    if chart_rows and PLOTLY_AVAILABLE:
        df_chart = pd.DataFrame(chart_rows)
        labels_c = df_chart["Período"].tolist()
        datasets_c = []
        for col in ["Nota final (%)", "Nota MP", "Nota interna"]:
            vals = df_chart[col].tolist()
            if any(v is not None for v in vals):
                datasets_c.append({"label": col, "data": [v if v else 0 for v in vals]})
        if datasets_c:
            fig_trip = plotly_line(labels_c, datasets_c)
            st.plotly_chart(fig_trip, use_container_width=True, config=PLOTLY_CFG)

        st.markdown(
            "<p style='color:#3a3a50;font-size:10px;font-weight:600;letter-spacing:0.07em;"
            "margin-top:1.5rem;margin-bottom:0.8rem;'>HISTÓRICO COMPLETO</p>",
            unsafe_allow_html=True
        )
        hist = []
        for e in op_evs:
            fn_h = eval_final(e, pesos)
            fx_h = get_faixa(fn_h, faixas)
            hist.append({
                "Mês":          e.get("mes", "—"),
                "Ciclo":        e.get("ciclo", "—"),
                "Nota MP":      f"{float(e['mp']):.1f}" if e.get("mp") not in (None, "") else "—",
                "Nota interna": f"{eval_int(e):.1f}"    if eval_int(e) is not None else "—",
                "Nota final":   f"{fn_h:.1f}%"          if fn_h else "—",
                "Faixa":        fx_h["desc"]             if fx_h else "—",
                "Bônus":        f"R$ {fx_h['bonus']:.2f}" if fx_h else "R$ 0,00",
            })
        st.dataframe(pd.DataFrame(hist), use_container_width=True, hide_index=True)
    else:
        st.info("Dados insuficientes para o gráfico.")


# ═══════════════════════════════════════════════════════════════════════════════
# ROTEADOR PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    tela_login()
else:
    user  = st.session_state.user
    nivel = user["nivel"]

    st.markdown(STARS_JS, unsafe_allow_html=True)

    if nivel == "tripulacao":
        render_sidebar(user)
        portal_tripulacao(user)
    else:
        render_sidebar(user)
        readonly = (nivel == "observador")
        page = st.session_state.get("page", "Dashboard")

        if   page == "Dashboard":    pagina_dashboard(user, readonly)
        elif page == "Operadores":   pagina_operadores(user, readonly)
        elif page == "Avaliações":   pagina_avaliacoes(user, readonly)
        elif page == "Metas":        pagina_metas(user, readonly)
        elif page == "Evolução":     pagina_evolucao(user, readonly)
        elif page == "Configurações" and nivel == "comandante":
            pagina_configuracoes(user)
