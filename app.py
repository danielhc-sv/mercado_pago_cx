"""
╔══════════════════════════════════════════════════════╗
║           LEAL — CX  |  Sistema de Qualidade         ║
║           Operação Mercado Pago                      ║
╚══════════════════════════════════════════════════════╝
Rodar localmente:
    pip install streamlit pandas openpyxl
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, date
from pathlib import Path

# ─── Google Sheets / Auth (graceful fallback) ─────────────────────────────────
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

# ─── CSS: Design Premium — Preto dominante ────────────────────────────────────
GALAXY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main, .block-container {
    background-color: #080808 !important;
    color: #E8E8E8 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── CANVAS ESTRELAS ── */
#star-canvas {
    position: fixed; top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none; z-index: 0;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #0D0D0D !important;
    border-right: 1px solid #1E1E1E !important;
    box-shadow: 4px 0 24px rgba(0,0,0,0.6) !important;
}
[data-testid="stSidebar"] * { color: #E8E8E8 !important; }
[data-testid="stSidebarContent"] { padding: 0 !important; }

/* ── MÉTRICAS ── */
[data-testid="stMetric"] {
    background: #111111 !important;
    border: 1px solid #1E1E1E !important;
    border-radius: 12px !important;
    padding: 20px 18px !important;
    position: relative !important;
    overflow: hidden !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute; top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, #C9A84C, #8B6914);
}
[data-testid="stMetric"]:hover {
    border-color: #2A2A2A !important;
    box-shadow: 0 4px 20px rgba(201,168,76,0.08) !important;
}
[data-testid="stMetricLabel"] {
    color: #888888 !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 26px !important;
    font-weight: 600 !important;
}
[data-testid="stMetricDelta"] { color: #C9A84C !important; font-size: 12px !important; }

/* ── INPUTS ── */
input, textarea,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: #111111 !important;
    border: 1px solid #222222 !important;
    color: #E8E8E8 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
input:focus, textarea:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #C9A84C !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.12) !important;
    outline: none !important;
}
input::placeholder, textarea::placeholder { color: #444444 !important; }

/* ── LABELS ── */
label, [data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p {
    color: #999999 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    margin-bottom: 4px !important;
}

/* ── BOTÕES ── */
.stButton > button {
    background: #111111 !important;
    color: #E8E8E8 !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 18px !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.02em !important;
}
.stButton > button:hover {
    background: #1A1A1A !important;
    border-color: #C9A84C !important;
    color: #C9A84C !important;
    box-shadow: 0 0 16px rgba(201,168,76,0.15) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── SELECTBOX ── */
[data-baseweb="select"] > div {
    background: #111111 !important;
    border: 1px solid #222222 !important;
    color: #E8E8E8 !important;
    border-radius: 8px !important;
    font-size: 14px !important;
}
[data-baseweb="select"] > div:focus-within {
    border-color: #C9A84C !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.12) !important;
}
[data-baseweb="popover"],
[data-baseweb="menu"] {
    background: #111111 !important;
    border: 1px solid #1E1E1E !important;
    border-radius: 10px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.8) !important;
}
[data-baseweb="option"] {
    background: transparent !important;
    color: #C8C8C8 !important;
    font-size: 13px !important;
    padding: 10px 14px !important;
}
[data-baseweb="option"]:hover {
    background: #1A1A1A !important;
    color: #FFFFFF !important;
}
[data-baseweb="option"][aria-selected="true"] {
    background: #161616 !important;
    color: #C9A84C !important;
}

/* ── TABELAS / DATAFRAME ── */
[data-testid="stDataFrame"],
[data-testid="stDataFrame"] table {
    background: transparent !important;
    border: none !important;
}
[data-testid="stDataFrame"] thead tr th {
    background: #111111 !important;
    color: #888888 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid #1E1E1E !important;
    padding: 12px 14px !important;
}
[data-testid="stDataFrame"] tbody tr td {
    background: #0D0D0D !important;
    color: #D0D0D0 !important;
    font-size: 13px !important;
    border-bottom: 1px solid #161616 !important;
    padding: 11px 14px !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background: #131313 !important;
    color: #FFFFFF !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
    background: #0D0D0D !important;
    border: 1px solid #1E1E1E !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    background: #0D0D0D !important;
    padding: 14px 18px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #D0D0D0 !important;
}
[data-testid="stExpander"] summary:hover {
    background: #111111 !important;
    color: #FFFFFF !important;
}
[data-testid="stExpander"][open] summary {
    border-bottom: 1px solid #1E1E1E !important;
    color: #C9A84C !important;
}

/* ── TABS ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1E1E1E !important;
    gap: 4px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: #666666 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    border-bottom: 2px solid transparent !important;
    padding: 10px 16px !important;
    transition: color 0.2s !important;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover { color: #AAAAAA !important; }
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
    color: #C9A84C !important;
    border-bottom: 2px solid #C9A84C !important;
}

/* ── PROGRESS BAR ── */
[data-testid="stProgressBar"] > div {
    background: #1A1A1A !important;
    border-radius: 6px !important;
    height: 6px !important;
}
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #8B6914, #C9A84C, #E8CC7A) !important;
    border-radius: 6px !important;
    box-shadow: 0 0 8px rgba(201,168,76,0.4) !important;
}

/* ── SLIDER ── */
[data-testid="stSlider"] > div > div > div {
    background: #1A1A1A !important;
}
[data-testid="stSlider"] [role="slider"] {
    background: #C9A84C !important;
    border: 2px solid #080808 !important;
    box-shadow: 0 0 8px rgba(201,168,76,0.5) !important;
}

/* ── DIVIDER ── */
hr {
    border: none !important;
    border-top: 1px solid #1A1A1A !important;
    margin: 1.5rem 0 !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    background: #0D0D0D !important;
    border: 1px solid #1E1E1E !important;
    border-radius: 8px !important;
}
[data-testid="stAlert"][data-baseweb="notification"] {
    border-left: 3px solid #C9A84C !important;
}

/* ── FORM SUBMIT BUTTON ── */
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #1A1500, #2A2000) !important;
    color: #C9A84C !important;
    border: 1px solid #C9A84C !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    transition: all 0.2s !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
    background: #C9A84C !important;
    color: #080808 !important;
    box-shadow: 0 0 20px rgba(201,168,76,0.3) !important;
}

/* ── HEADINGS ── */
h1 {
    color: #FFFFFF !important;
    font-size: 26px !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
    margin-bottom: 2px !important;
}
h2 { color: #DDDDDD !important; font-weight: 500 !important; font-size: 20px !important; }
h3 {
    color: #BBBBBB !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #080808; }
::-webkit-scrollbar-thumb { background: #222222; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #C9A84C; }

/* ── BLOCK CONTAINER ── */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px !important;
}

/* ── COMPONENTS CUSTOMIZADOS ── */
.badge-meta {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.sidebar-logo {
    padding: 1.5rem 1.2rem 1.2rem;
    border-bottom: 1px solid #1A1A1A;
    margin-bottom: 0.5rem;
}
.page-header {
    padding-bottom: 1rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid #1A1A1A;
}
.stat-card {
    background: #0D0D0D;
    border: 1px solid #1A1A1A;
    border-radius: 12px;
    padding: 18px 20px;
}
.gold { color: #C9A84C !important; }
.muted { color: #666666 !important; }
.tag-dot {
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
}

/* ── DATE INPUT ── */
[data-testid="stDateInput"] input {
    background: #111111 !important;
    border: 1px solid #222222 !important;
    color: #E8E8E8 !important;
    border-radius: 8px !important;
}

/* ── NUMBER INPUT BOTÕES +/- ── */
[data-testid="stNumberInput"] button {
    background: #1A1A1A !important;
    border: 1px solid #222222 !important;
    color: #888888 !important;
    border-radius: 6px !important;
}
[data-testid="stNumberInput"] button:hover {
    background: #222222 !important;
    color: #C9A84C !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: #0D0D0D !important;
    border: 1px dashed #2A2A2A !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #C9A84C !important;
}

/* ── CHECKBOX ── */
[data-testid="stCheckbox"] span {
    background: #111111 !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 4px !important;
}

/* ── DOWNLOAD BUTTON ── */
[data-testid="stDownloadButton"] > button {
    background: #0D0D0D !important;
    color: #C9A84C !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}
[data-testid="stDownloadButton"] > button:hover {
    border-color: #C9A84C !important;
    box-shadow: 0 0 12px rgba(201,168,76,0.2) !important;
}

/* ── NOTIFICATION / INFO / SUCCESS ── */
.stInfo, .stSuccess, .stWarning, .stError {
    border-radius: 8px !important;
    font-size: 13px !important;
}
</style>
"""

# ─── JS: Estrelas animadas — tema premium preto ──────────────────────────────
STARS_JS = """
<canvas id="star-canvas"></canvas>
<script>
(function(){
  var canvas = document.getElementById('star-canvas');
  if(!canvas) return;
  var ctx = canvas.getContext('2d');
  var W = window.innerWidth, H = window.innerHeight;
  canvas.width = W; canvas.height = H;

  var STAR_COUNT = 220;
  var stars = [];
  function rand(a,b){ return Math.random()*(b-a)+a; }

  function makeStar(){
    var gold = Math.random() > 0.88;
    return {
      x: rand(0,W), y: rand(0,H),
      r: rand(0.3, gold ? 1.8 : 1.2),
      alpha: rand(0.1, gold ? 0.7 : 0.4),
      dx: rand(-0.12,0.12), dy: rand(-0.08,0.08),
      pulse: rand(0,Math.PI*2),
      pulseSpeed: rand(0.004,0.018),
      gold: gold
    };
  }
  for(var i=0;i<STAR_COUNT;i++) stars.push(makeStar());

  var shooters=[], shooterTimer=0;
  function makeShooter(){
    return {
      x:rand(0,W*0.7), y:rand(0,H*0.35),
      len:rand(80,160), speed:rand(8,16),
      angle:rand(0.25,0.55),
      alpha:1.0, life:0, maxLife:rand(25,50)
    };
  }

  function draw(){
    ctx.clearRect(0,0,W,H);
    for(var i=0;i<stars.length;i++){
      var s=stars[i];
      s.pulse+=s.pulseSpeed;
      var a=s.alpha*(0.5+0.5*Math.sin(s.pulse));
      ctx.beginPath();
      ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
      ctx.fillStyle = s.gold
        ? 'rgba(201,168,76,'+a+')'
        : 'rgba(200,200,200,'+a+')';
      ctx.fill();
      s.x+=s.dx; s.y+=s.dy;
      if(s.x<-4) s.x=W+4; if(s.x>W+4) s.x=-4;
      if(s.y<-4) s.y=H+4; if(s.y>H+4) s.y=-4;
    }
    shooterTimer++;
    if(shooterTimer>280 && Math.random()>0.97){
      shooters.push(makeShooter()); shooterTimer=0;
    }
    for(var j=shooters.length-1;j>=0;j--){
      var sh=shooters[j]; sh.life++;
      sh.alpha=1-sh.life/sh.maxLife;
      var ex=sh.x+Math.cos(sh.angle)*sh.len;
      var ey=sh.y+Math.sin(sh.angle)*sh.len;
      var g=ctx.createLinearGradient(sh.x,sh.y,ex,ey);
      g.addColorStop(0,'rgba(201,168,76,0)');
      g.addColorStop(1,'rgba(201,168,76,'+sh.alpha+')');
      ctx.beginPath(); ctx.moveTo(sh.x,sh.y); ctx.lineTo(ex,ey);
      ctx.strokeStyle=g; ctx.lineWidth=1.2; ctx.stroke();
      sh.x+=Math.cos(sh.angle)*sh.speed;
      sh.y+=Math.sin(sh.angle)*sh.speed;
      if(sh.life>=sh.maxLife||sh.x>W||sh.y>H) shooters.splice(j,1);
    }
    requestAnimationFrame(draw);
  }
  draw();
  window.addEventListener('resize',function(){
    W=window.innerWidth; H=window.innerHeight;
    canvas.width=W; canvas.height=H;
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
    "comandante": "Comandante \U0001f30c",
    "copiloto":   "Copiloto \U0001f680",
    "observador": "Observador Estelar \U0001f52d",
    "tripulacao": "Tripulação ⭐",
}

MESES_LABEL = [f"Mês {i:02d}" for i in range(1, 13)]
CICLOS      = ["Ciclo 1", "Ciclo 2", "Ciclo 3", "Ciclo 4", "Ciclo 5"]

CARGOS_GESTAO  = ["Gerente de Qualidade", "Coordenador(a)", "Supervisor(a)", "Analista de Qualidade"]
CARGOS_OP      = ["Operador(a)"]

ABAS = ["operadores", "avaliacoes", "faixas", "usuarios"]

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

# ─── Camada de persistência: Google Sheets + fallback JSON ───────────────────

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Cabeçalhos padrão de cada aba — garante que a planilha seja inicializada correta
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
    """Abre cliente gspread autenticado — novo a cada chamada, sem cache de objeto."""
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=SCOPES
    )
    return gspread.authorize(creds)

def _spreadsheet():
    """Abre a planilha pelo ID configurado em secrets."""
    sid = st.secrets["gsheets"]["spreadsheet_id"]
    return _gc().open_by_key(sid)

def _get_or_create_ws(nome):
    """Abre ou cria a worksheet garantindo cabeçalho."""
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
    """Lê aba e retorna lista de dicts. Retorna None em caso de erro."""
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
    """Sobrescreve aba inteira. Exibe erro visível se falhar."""
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
        if data is None:  # erro de conexão — usa JSON local
            return _json_read(OPS_FILE, [])
        return _str_to_none(data, ["op_id"])
    return _json_read(OPS_FILE, [])

def save_operadores(d):
    d = _none_to_str(d)
    _json_write(OPS_FILE, d)  # sempre salva local também
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
        sid = st.secrets["gsheets"]["spreadsheet_id"]
        return f"✅ Google Sheets ativo"
    return "💾 Armazenamento local (JSON)"

def _gs_test_write():
    """Teste rápido de escrita — confirma que as credenciais têm permissão de editar."""
    try:
        sh = _spreadsheet()
        titles = [ws.title for ws in sh.worksheets()]
        return True, f"{len(titles)} abas acessíveis"
    except Exception as e:
        return False, str(e)


# ─── Helpers de negócio ───────────────────────────────────────────────────────
def avg_of(values):
    vals = [float(v) for v in values if v not in (None,"") and str(v).strip() != "" and float(v) != 0]
    return round(sum(vals)/len(vals), 2) if vals else None

def eval_int(e):
    """Nota interna: campo 'nota_int' direto (0-100)."""
    v = e.get("nota_int")
    if v in (None, ""): return None
    try: return float(v)
    except: return None

def eval_final(e, pesos):
    """
    Nota MP: 0-100 (direto)
    Nota interna: 0-100 (direto)
    Nota final = média ponderada das duas, resultado 0-100
    """
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

def badge_faixa(fx):
    if not fx: return "<span style='color:#444'>—</span>"
    b = fx["bonus"]
    if b == 0:
        cor, bg = "#666666", "rgba(255,255,255,0.04)"
    elif b < 150:
        cor, bg = "#C9841A", "rgba(201,132,26,0.12)"
    elif b < 300:
        cor, bg = "#C9A84C", "rgba(201,168,76,0.12)"
    else:
        cor, bg = "#E8CC7A", "rgba(232,204,122,0.15)"
    return (f"<span class='badge-meta' style='color:{cor};background:{bg};"
            f"border:1px solid {cor};'>{fx['desc']} · R$ {fx['bonus']:.2f}</span>")

def nota_cor(v):
    if v is None: return "#555555"
    return "#E8CC7A" if v >= 90 else "#C9A84C" if v >= 80 else "#8B5E3C"

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
    <div style='text-align:center;padding-top:3rem;'>
        <div style='display:inline-block;width:64px;height:64px;border-radius:16px;
                    background:linear-gradient(135deg,#1A1500,#2A2000);
                    border:1px solid #C9A84C;margin-bottom:20px;
                    box-shadow:0 0 32px rgba(201,168,76,0.2);
                    line-height:64px;font-size:28px;'>🌌</div>
        <h1 style='color:#FFFFFF;font-size:28px;font-weight:700;letter-spacing:-0.02em;margin-bottom:4px;'>
            Leal <span style='color:#C9A84C'>CX</span>
        </h1>
        <p style='color:#444444;font-size:12px;letter-spacing:0.14em;font-weight:500;margin-bottom:2px;'>
            SISTEMA DE GESTÃO DE QUALIDADE
        </p>
        <p style='color:#555555;font-size:12px;'>Operação Mercado Pago</p>
    </div>
    """, unsafe_allow_html=True)

    _, c2, _ = st.columns([1, 1.1, 1])
    with c2:
        st.markdown("""
        <div style='background:#0D0D0D;border:1px solid #1A1A1A;border-radius:14px;
                    padding:2rem 2rem 1.5rem;margin-top:1.5rem;
                    box-shadow:0 24px 64px rgba(0,0,0,0.8);'>
            <p style='color:#666666;font-size:11px;letter-spacing:0.1em;
                      font-weight:600;margin-bottom:1.2rem;'>AUTENTICAÇÃO</p>
        """, unsafe_allow_html=True)
        login_i = st.text_input("Login", placeholder="Identificador de acesso", key="lf", label_visibility="collapsed")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        senha_i = st.text_input("Senha", type="password", placeholder="Senha", key="sf", label_visibility="collapsed")
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        entrar  = st.button("Entrar", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if entrar:
            u = next((u for u in load_usuarios() if u["login"]==login_i and u["senha"]==senha_i), None)
            if u:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Credenciais inválidas.")

    st.markdown("""
    <div style='text-align:center;margin-top:3rem;color:#222222;font-size:11px;letter-spacing:0.06em;'>
        LEAL — CX · QUALIDADE · MERCADO PAGO
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
def render_sidebar(user):
    with st.sidebar:
        st.markdown(f"""
        <div class='sidebar-logo'>
            <div style='display:flex;align-items:center;gap:10px;'>
                <div style='width:36px;height:36px;border-radius:8px;
                            background:linear-gradient(135deg,#1A1500,#2A2000);
                            border:1px solid #C9A84C;
                            display:flex;align-items:center;justify-content:center;
                            font-size:18px;flex-shrink:0;'>🌌</div>
                <div>
                    <div style='font-size:16px;font-weight:700;color:#FFFFFF;letter-spacing:-0.01em;line-height:1.1;'>
                        Leal <span style='color:#C9A84C'>CX</span>
                    </div>
                    <div style='font-size:9px;color:#333333;letter-spacing:0.12em;font-weight:600;'>QUALIDADE · MP</div>
                </div>
            </div>
        </div>
        <div style='margin:0 0.8rem 1rem;background:#111111;border:1px solid #1A1A1A;
                    border-radius:10px;padding:12px 14px;'>
            <div style='font-size:10px;color:#444444;letter-spacing:0.08em;font-weight:600;margin-bottom:6px;'>
                SESSÃO ATIVA
            </div>
            <div style='font-size:14px;font-weight:600;color:#FFFFFF;margin-bottom:2px;'>{user['nome']}</div>
            <div style='display:flex;align-items:center;gap:6px;'>
                <div style='width:6px;height:6px;border-radius:50%;background:#C9A84C;'></div>
                <span style='font-size:11px;color:#C9A84C;font-weight:500;'>{NIVEIS.get(user['nivel'], user['nivel'])}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        nivel = user["nivel"]
        if nivel in ("comandante","copiloto","observador"):
            if "page" not in st.session_state:
                st.session_state.page = "Dashboard"

            st.markdown("<div style='padding:0 0.5rem;'>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:10px;color:#333333;letter-spacing:0.1em;font-weight:600;padding:0 0.3rem;margin-bottom:6px;'>NAVEGAÇÃO</p>", unsafe_allow_html=True)

            pages = [("🏠","Dashboard"),("👥","Operadores"),("📋","Avaliações"),("🏆","Metas"),("📈","Evolução")]
            if nivel == "comandante":
                pages.append(("⚙️","Configurações"))

            for icon, pg in pages:
                is_active = st.session_state.page == pg
                prefix = "▸ " if is_active else ""
                if st.button(f"{icon}  {prefix}{pg}", key=f"nav_{pg}", use_container_width=True):
                    st.session_state.page = pg
                    st.rerun()

        st.markdown("---")
        # Status do armazenamento
        st.markdown(f"<p style='font-size:10px;color:#333333;padding:0 0.3rem;line-height:1.5;'>{storage_status()}</p>", unsafe_allow_html=True)
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
            <div style='width:40px;height:40px;border-radius:10px;background:#111111;
                        border:1px solid #1A1A1A;display:flex;align-items:center;
                        justify-content:center;font-size:18px;'>🏠</div>
            <div>
                <h1 style='margin:0;font-size:22px;'>Dashboard</h1>
                <p style='margin:0;font-size:12px;color:#444;'></p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"<p style='color:#444444;font-size:12px;margin-top:-1rem;margin-bottom:1.5rem;'>Atualizado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>", unsafe_allow_html=True)

    ops    = load_operadores()
    evs    = load_avaliacoes()
    faixas = load_faixas()
    pesos  = st.session_state.pesos
    ativos = [o for o in ops if o.get("status") == "Ativo"]

    all_mps  = [float(e["mp"])  for e in evs if e.get("mp")  not in (None,"")]
    all_ivs  = [eval_int(e)     for e in evs]
    all_fins = [eval_final(e,pesos) for e in evs]
    all_fins = [v for v in all_fins if v is not None]
    all_ivs  = [v for v in all_ivs  if v is not None]

    avg_mp  = round(sum(all_mps) /len(all_mps), 1)  if all_mps  else None
    avg_iv  = round(sum(all_ivs) /len(all_ivs), 1)  if all_ivs  else None
    avg_fin = round(sum(all_fins)/len(all_fins), 1)  if all_fins else None

    total_bonus = 0
    for op in ativos:
        op_evs = sorted([e for e in evs if e["op_id"]==op["id"]], key=lambda x:(x.get("mes",""),x.get("ciclo","")), reverse=True)
        if op_evs:
            fx = get_faixa(eval_final(op_evs[0], pesos), faixas)
            total_bonus += fx["bonus"] if fx else 0

    abaixo_80 = sum(
        1 for op in ativos
        if (lambda ev: ev is not None and eval_final(ev,pesos) is not None and eval_final(ev,pesos)<80)(
            next((e for e in sorted([e for e in evs if e["op_id"]==op["id"]], key=lambda x:(x.get("mes",""),x.get("ciclo","")),reverse=True)),None)
        )
    )

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("👥 Ativos",          len(ativos), f"de {len(ops)}")
    c2.metric("📋 Avaliações",       len(evs))
    c3.metric("🎯 Média MP",         f"{avg_mp:.1f}"  if avg_mp  is not None else "—")
    c4.metric("📝 Média interna",    f"{avg_iv:.1f}"  if avg_iv  is not None else "—")
    c5.metric("🏆 Nota final média", f"{avg_fin:.1f}%" if avg_fin is not None else "—")
    c6.metric("💰 Total bonificação",f"R$ {total_bonus:.2f}")

    st.markdown("---")
    meses_disp = sorted(set(e.get("mes","") for e in evs if e.get("mes")), reverse=True)
    col_s, _ = st.columns([2,4])
    mes_sel = col_s.selectbox("📅 Filtrar mês", ["Todos"]+meses_disp, key="dash_mes")

    st.markdown("### 🧑‍🚀 Resumo da equipe")
    rows = []
    for op in ativos:
        op_evs = [e for e in evs if e["op_id"]==op["id"]]
        if mes_sel != "Todos":
            op_evs = [e for e in op_evs if e.get("mes")==mes_sel]
        op_evs = sorted(op_evs, key=lambda x: x.get("ciclo",""), reverse=True)
        last = op_evs[0] if op_evs else None
        mp_v = float(last["mp"]) if last and last.get("mp") not in (None,"") else None
        iv_v = eval_int(last)    if last else None
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

    if mes_sel != "Todos":
        st.markdown(f"### 📊 Médias por ciclo — {mes_sel}")
        ciclo_data = []
        for ciclo in CICLOS:
            cevs = [e for e in evs if e.get("mes")==mes_sel and e.get("ciclo")==ciclo]
            if not cevs: continue
            fps = [eval_final(e,pesos) for e in cevs if eval_final(e,pesos) is not None]
            mps = [float(e["mp"]) for e in cevs if e.get("mp") not in (None,"")]
            ciclo_data.append({
                "Ciclo": ciclo,
                "Média MP": round(sum(mps)/len(mps),1) if mps else None,
                "Nota final": round(sum(fps)/len(fps),1) if fps else None,
                "Qtd avaliados": len(cevs),
            })
        if ciclo_data:
            df_c = pd.DataFrame(ciclo_data)
            st.dataframe(df_c, use_container_width=True, hide_index=True)
            df_chart = df_c.dropna(subset=["Nota final"])
            if not df_chart.empty:
                st.line_chart(df_chart.set_index("Ciclo")[["Nota final"]], color="#4CC9F0")

    st.markdown("---")
    st.markdown("### 🏆 Situação de metas — mês atual")
    mes_rec = meses_disp[0] if meses_disp else None
    if mes_rec:
        for op in ativos:
            op_evs = [e for e in evs if e["op_id"]==op["id"] and e.get("mes")==mes_rec]
            if not op_evs: continue
            fn_vals = [eval_final(e,pesos) for e in op_evs if eval_final(e,pesos) is not None]
            fn_med  = round(sum(fn_vals)/len(fn_vals),1) if fn_vals else None
            fx = get_faixa(fn_med, faixas)
            cor = nota_cor(fn_med)
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid #1F3A52;'>"
                f"<span style='flex:1;color:#E2E8F0;font-size:14px;'>{op['nome']}</span>"
                f"{'<span style=\"font-weight:700;color:'+cor+';\">'+str(fn_med)+'%</span>' if fn_med else '<span style=\"color:#555\">sem avaliação</span>'}"
                f"{badge_faixa(fx)}</div>",
                unsafe_allow_html=True
            )

# ═══════════════════════════════════════════════════════════════════════════════
# OPERADORES
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_operadores(user, readonly=False):
    st.markdown("""
    <div class='page-header'>
        <div style='display:flex;align-items:center;gap:12px;'>
            <div style='width:40px;height:40px;border-radius:10px;background:#111111;
                        border:1px solid #1A1A1A;display:flex;align-items:center;
                        justify-content:center;font-size:18px;'>👥</div>
            <div>
                <h1 style='margin:0;font-size:22px;'>Operadores</h1>
                <p style='margin:0;font-size:12px;color:#444;'>Cadastro, tempo de casa e acompanhamento</p>
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
                status = c4.selectbox("Status", ["Ativo","Afastado","Desligado"])
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
                        ops.append({"id":op_id,"nome":nome.strip(),"cargo":cargo,"adm":adm.strftime("%Y-%m-%d"),"status":status,"notas":notas})
                        save_operadores(ops)
                        if login_op.strip() and senha_op.strip():
                            usu = load_usuarios()
                            if any(u["login"]==login_op.strip() for u in usu):
                                st.warning(f"Login '{login_op}' já existe. Operador salvo sem login.")
                            else:
                                usu.append({"login":login_op.strip(),"senha":senha_op.strip(),"nivel":"tripulacao","nome":nome.strip(),"op_id":op_id})
                                save_usuarios(usu)
                        st.success(f"✅ {nome} cadastrado!")
                        st.rerun()

    st.markdown("---")
    c1, c2 = st.columns([3,1])
    busca  = c1.text_input("🔍 Buscar", placeholder="Nome...")
    filtro = c2.selectbox("Status", ["Todos","Ativo","Afastado","Desligado"], key="op_f")
    lista  = [o for o in ops if (not busca or busca.lower() in o["nome"].lower()) and (filtro=="Todos" or o.get("status")==filtro)]

    if not lista:
        st.info("Nenhum operador encontrado.")
        return

    for op in lista:
        op_evs = sorted([e for e in evs if e["op_id"]==op["id"]], key=lambda x:(x.get("mes",""),x.get("ciclo","")), reverse=True)
        last   = op_evs[0] if op_evs else None
        fn     = eval_final(last, pesos) if last else None
        fx     = get_faixa(fn, faixas)

        with st.expander(f"🧑‍🚀 {op['nome']} — {op.get('cargo','—')} · {tenure(op.get('adm'))}"):
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Status", op.get("status","—"))
            c2.metric("Tempo de casa", tenure(op.get("adm")))
            if last:
                mp_v = float(last["mp"]) if last.get("mp") not in (None,"") else None
                iv_v = eval_int(last)
                c3.metric("Nota MP (última)", f"{mp_v:.1f}" if mp_v is not None else "—")
                c4.metric("Nota interna (última)", f"{iv_v:.1f}" if iv_v is not None else "—")
            if op.get("notas"):
                st.markdown(f"*{op['notas']}*")
            if fn is not None:
                pct = min(100, max(0, fn))
                st.markdown(f"**Nota final: {fn:.1f}%**")
                st.progress(pct/100)
                st.markdown(badge_faixa(fx), unsafe_allow_html=True)
                proxima = next((f for f in sorted(faixas,key=lambda x:x["min"]) if f["min"]>fn), None)
                if proxima:
                    st.markdown(f"<p style='color:#4CC9F0;font-size:13px;'>⭐ Faltam <b>{round(proxima['min']-fn,2)} pontos</b> para {proxima['desc']} (R$ {proxima['bonus']:.2f})</p>", unsafe_allow_html=True)
            if not readonly:
                if st.button("🗑️ Excluir operador", key=f"del_{op['id']}"):
                    ops = [o for o in ops if o["id"]!=op["id"]]
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
            <div style='width:40px;height:40px;border-radius:10px;background:#111111;
                        border:1px solid #1A1A1A;display:flex;align-items:center;
                        justify-content:center;font-size:18px;'>📋</div>
            <div>
                <h1 style='margin:0;font-size:22px;'>Avaliações</h1>
                <p style='margin:0;font-size:12px;color:#444;'>Notas MP, nota interna, feedbacks e plano de ação</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    ops   = load_operadores()
    evs   = load_avaliacoes()
    pesos = st.session_state.pesos
    ativ  = [o for o in ops if o.get("status")=="Ativo"]

    if not readonly and ativ:
        with st.expander("➕ Registrar nova avaliação", expanded=False):
            with st.form("form_eval"):
                op_map  = {o["nome"]: o["id"] for o in ativ}
                c1,c2,c3 = st.columns(3)
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
                c6, c7 = st.columns(2)
                feed_val = c6.text_area("Pontos de melhoria", height=90)
                pos_val  = c7.text_area("Pontos positivos",   height=90)
                acao_val = st.text_input("Plano de ação / Desenvolvimento")

                if st.form_submit_button("💾 Salvar avaliação"):
                    ev = {
                        "id":       f"ev_{int(datetime.now().timestamp()*1000)}",
                        "op_id":    op_map[op_nome],
                        "mes":      mes_sel,
                        "ciclo":    ciclo_s,
                        "mp":       mp_val,
                        "nota_int": int_val,
                        "feed":     feed_val,
                        "pos":      pos_val,
                        "acao":     acao_val,
                        "criado":   datetime.now().isoformat(),
                    }
                    evs.append(ev)
                    save_avaliacoes(evs)
                    st.success(f"✅ Avaliação de {op_nome} — {mes_sel} / {ciclo_s} salva!")
                    st.rerun()

    st.markdown("---")
    c1,c2,c3 = st.columns(3)
    op_f  = c1.selectbox("Operador",    ["Todos"]+[o["nome"] for o in ops], key="evop")
    mes_f = c2.selectbox("Mês",         ["Todos"]+sorted(set(e.get("mes","") for e in evs if e.get("mes")),reverse=True), key="evmes")
    cic_f = c3.selectbox("Ciclo",       ["Todos"]+CICLOS, key="evci")

    lista = evs
    if op_f  != "Todos": lista = [e for e in lista if e["op_id"]==next((o["id"] for o in ops if o["nome"]==op_f),None)]
    if mes_f != "Todos": lista = [e for e in lista if e.get("mes")==mes_f]
    if cic_f != "Todos": lista = [e for e in lista if e.get("ciclo")==cic_f]
    lista = sorted(lista, key=lambda x:(x.get("mes",""),x.get("ciclo","")), reverse=True)

    if not lista:
        st.info("Nenhuma avaliação encontrada.")
        return

    rows = []
    for e in lista:
        op  = next((o for o in ops if o["id"]==e["op_id"]), {})
        iv  = eval_int(e)
        fn  = eval_final(e, pesos)
        mp_v = e.get("mp")
        rows.append({
            "Operador":     op.get("nome","—"),
            "Mês":          e.get("mes","—"),
            "Ciclo":        e.get("ciclo","—"),
            "Nota MP":      f"{float(mp_v):.1f}" if mp_v not in (None,"") else "—",
            "Nota interna": f"{iv:.1f}"           if iv is not None else "—",
            "Nota final":   f"{fn:.1f}%"          if fn is not None else "—",
            "Plano de ação": e.get("acao","—"),
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Exportar CSV", data=df.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"leal_cx_avaliacoes_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")

# ═══════════════════════════════════════════════════════════════════════════════
# METAS
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_metas(user, readonly=False):
    st.markdown("""
    <div class='page-header'>
        <div style='display:flex;align-items:center;gap:12px;'>
            <div style='width:40px;height:40px;border-radius:10px;background:#111111;
                        border:1px solid #1A1A1A;display:flex;align-items:center;
                        justify-content:center;font-size:18px;'>🏆</div>
            <div>
                <h1 style='margin:0;font-size:22px;'>Metas e Bonificações</h1>
                <p style='margin:0;font-size:12px;color:#444;'>Faixas configuráveis e resultado por operador</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    faixas = load_faixas()
    ops    = load_operadores()
    evs    = load_avaliacoes()
    pesos  = st.session_state.pesos

    c_p, c_f = st.columns([1,2])
    with c_p:
        st.markdown("### ⚖️ Pesos da nota final")
        if not readonly:
            pm = st.slider("Peso Nota MP (%)",      0, 100, pesos.get("mp",50), step=5)
            pi = st.slider("Peso Nota interna (%)", 0, 100, pesos.get("int",50), step=5)
            if pm+pi != 100:
                st.warning(f"Soma atual: {pm+pi}% (deve ser 100%)")
            else:
                st.session_state.pesos = {"mp":pm,"int":pi}
                st.success("✓ Pesos salvos")
        else:
            st.markdown(f"- Nota MP: **{pesos['mp']}%**  \n- Nota interna: **{pesos['int']}%**")

    with c_f:
        st.markdown("### 🎯 Faixas de bonificação")
        for f in sorted(faixas, key=lambda x:x["min"]):
            cc1,cc2,cc3,cc4 = st.columns([3,2,2,1])
            cc1.markdown(f"**{f['desc']}**")
            cc2.markdown(f"{f['min']}% – {f['max']}%")
            cc3.markdown(f"R$ {f['bonus']:.2f}")
            if not readonly and cc4.button("🗑️", key=f"delf_{f['id']}"):
                faixas = [x for x in faixas if x["id"]!=f["id"]]
                save_faixas(faixas)
                st.rerun()
        if not readonly:
            st.markdown("---")
            with st.form("ff"):
                c1,c2,c3,c4 = st.columns(4)
                fd = c1.text_input("Descrição")
                fn = c2.number_input("Mín (%)", 0.0, 100.0, step=0.1)
                fm = c3.number_input("Máx (%)", 0.0, 100.0, step=0.1)
                fb = c4.number_input("Bônus R$", 0.0, step=0.01)
                if st.form_submit_button("➕ Adicionar faixa"):
                    if not fd.strip(): st.error("Informe a descrição.")
                    elif fn>fm:        st.error("Mínimo maior que máximo.")
                    else:
                        faixas.append({"id":f"f_{int(datetime.now().timestamp()*1000)}","desc":fd,"min":fn,"max":fm,"bonus":fb})
                        save_faixas(faixas)
                        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Resultado por mês")
    meses = sorted(set(e.get("mes","") for e in evs if e.get("mes")), reverse=True)
    if not meses:
        st.info("Nenhuma avaliação registrada ainda.")
        return
    col_m,_ = st.columns([2,4])
    mes_sel  = col_m.selectbox("Mês", meses, key="metas_mes")

    ativos = [o for o in ops if o.get("status")=="Ativo"]
    rows=[]; total_b=0
    for op in ativos:
        op_evs = [e for e in evs if e["op_id"]==op["id"] and e.get("mes")==mes_sel]
        fn_vals = [eval_final(e,pesos) for e in op_evs if eval_final(e,pesos) is not None]
        mp_vals = [float(e["mp"]) for e in op_evs if e.get("mp") not in (None,"")]
        iv_vals = [eval_int(e) for e in op_evs if eval_int(e) is not None]
        fn_med  = round(sum(fn_vals)/len(fn_vals),1) if fn_vals else None
        mp_med  = round(sum(mp_vals)/len(mp_vals),1) if mp_vals else None
        iv_med  = round(sum(iv_vals)/len(iv_vals),1) if iv_vals else None
        fx = get_faixa(fn_med, faixas)
        bv = fx["bonus"] if fx else 0
        total_b += bv
        sit = "✅ Meta atingida" if fn_med and fn_med>=80 else ("⚠️ Abaixo" if fn_med is not None else "📭 Sem avaliação")
        rows.append({
            "Operador":  op["nome"],
            "Nota MP":   f"{mp_med:.1f}" if mp_med else "—",
            "Nota int.": f"{iv_med:.1f}" if iv_med else "—",
            "Nota final":f"{fn_med:.1f}%" if fn_med else "—",
            "Faixa":     fx["desc"] if fx else "—",
            "Bônus":     f"R$ {bv:.2f}",
            "Situação":  sit,
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.markdown(f"<p style='color:#4CC9F0;font-weight:600;font-size:15px;'>💰 Total bonificação da equipe ({mes_sel}): R$ {total_b:.2f}</p>", unsafe_allow_html=True)
        csv = pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ Exportar CSV metas", data=csv,
                           file_name=f"leal_cx_metas_{mes_sel}_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
    else:
        st.info("Nenhuma avaliação para este mês.")

# ═══════════════════════════════════════════════════════════════════════════════
# EVOLUÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_evolucao(user, readonly=False):
    st.markdown("""
    <div class='page-header'>
        <div style='display:flex;align-items:center;gap:12px;'>
            <div style='width:40px;height:40px;border-radius:10px;background:#111111;
                        border:1px solid #1A1A1A;display:flex;align-items:center;
                        justify-content:center;font-size:18px;'>📈</div>
            <div>
                <h1 style='margin:0;font-size:22px;'>Evolução</h1>
                <p style='margin:0;font-size:12px;color:#444;'>Progressão da equipe e individual ao longo dos meses</p>
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

    meses = sorted(set(e.get("mes","") for e in evs if e.get("mes")))

    c1,c2 = st.columns(2)
    opcao   = c1.selectbox("Visualizar", ["Média da equipe"]+[o["nome"] for o in ops])
    metrica = c2.selectbox("Métrica", ["Nota final (%)","Nota MP","Nota interna"])

    def get_val(e, met):
        if met=="Nota final (%)": return eval_final(e,pesos)
        if met=="Nota MP":        return float(e["mp"]) if e.get("mp") not in (None,"") else None
        if met=="Nota interna":   return eval_int(e)

    st.markdown("---")
    # Gráfico por mês (fechamento)
    data_m = {}
    for mes in meses:
        m_evs = [e for e in evs if e.get("mes")==mes]
        if opcao!="Média da equipe":
            op = next((o for o in ops if o["nome"]==opcao),None)
            m_evs = [e for e in m_evs if op and e["op_id"]==op["id"]]
        vals = [get_val(e,metrica) for e in m_evs if get_val(e,metrica) is not None]
        data_m[mes] = round(sum(vals)/len(vals),1) if vals else None

    df_m = pd.DataFrame({"Mês":list(data_m.keys()), metrica:list(data_m.values())}).dropna()
    if not df_m.empty:
        st.markdown(f"### 🌌 {opcao} — {metrica} por mês")
        st.line_chart(df_m.set_index("Mês"), color="#4CC9F0")

    # Comparativo entre operadores
    st.markdown("---")
    mes_rec = meses[-1] if meses else None
    if mes_rec:
        st.markdown(f"### 🧑‍🚀 Comparativo — {mes_rec}")
        comp = []
        for op in ops:
            op_evs = [e for e in evs if e["op_id"]==op["id"] and e.get("mes")==mes_rec]
            vals = [get_val(e,metrica) for e in op_evs if get_val(e,metrica) is not None]
            if vals: comp.append({"Operador":op["nome"], metrica: round(sum(vals)/len(vals),1)})
        if comp:
            df_c = pd.DataFrame(comp).sort_values(metrica, ascending=False)
            st.bar_chart(df_c.set_index("Operador"), color="#4CC9F0")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES (Comandante)
# ═══════════════════════════════════════════════════════════════════════════════
def pagina_configuracoes(user):
    st.markdown("""
    <div class='page-header'>
        <div style='display:flex;align-items:center;gap:12px;'>
            <div style='width:40px;height:40px;border-radius:10px;background:#111111;
                        border:1px solid #1A1A1A;display:flex;align-items:center;
                        justify-content:center;font-size:18px;'>⚙️</div>
            <div>
                <h1 style='margin:0;font-size:22px;'>Configurações</h1>
                <p style='margin:0;font-size:12px;color:#444;'>Usuários, credenciais e backup de dados</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Diagnóstico Google Sheets ──────────────────────────────────────────
    if _use_gsheets():
        st.markdown("### 🔌 Diagnóstico da conexão")
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"<p style='font-size:13px;color:#888;'>ID da planilha: <code>{st.secrets['gsheets']['spreadsheet_id']}</code></p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:13px;color:#888;'>Conta de serviço: <code>{st.secrets['gcp_service_account'].get('client_email','?')}</code></p>", unsafe_allow_html=True)
        with c2:
            if st.button("🧪 Testar conexão agora", use_container_width=True):
                ok, msg = _gs_test_write()
                if ok:
                    st.success(f"✅ Conectado — {msg}")
                else:
                    st.error(f"❌ Falhou: {msg}")
        st.markdown("---")

    st.markdown("### 👤 Usuários do sistema")
    usuarios = load_usuarios()

    # Editar nome e senha de qualquer usuário de gestão
    st.markdown("**Editar usuários de gestão**")
    for i, u in enumerate(usuarios):
        if u.get("nivel") == "tripulacao": continue
        with st.expander(f"✏️ {u['nome']} — `{u['login']}` — {NIVEIS.get(u['nivel'],u['nivel'])}"):
            with st.form(f"edit_user_{u['login']}"):
                novo_nome  = st.text_input("Nome de exibição", value=u.get("nome",""), key=f"nn_{i}")
                novo_login = st.text_input("Login", value=u.get("login",""), key=f"nl_{i}")
                nova_senha = st.text_input("Nova senha (deixe vazio para manter)", type="password", key=f"ns_{i}")
                if st.form_submit_button("💾 Salvar alterações"):
                    # Verificar login duplicado
                    outros_logins = [x["login"] for x in usuarios if x["login"]!=u["login"]]
                    if novo_login.strip() in outros_logins:
                        st.error("Este login já está em uso.")
                    else:
                        for uu in usuarios:
                            if uu["login"]==u["login"]:
                                uu["nome"]  = novo_nome.strip() or uu["nome"]
                                uu["login"] = novo_login.strip() or uu["login"]
                                if nova_senha.strip():
                                    if len(nova_senha.strip())<4:
                                        st.error("Senha muito curta.")
                                        break
                                    uu["senha"] = nova_senha.strip()
                        save_usuarios(usuarios)
                        # Atualizar sessão se for o próprio usuário
                        if u["login"]==user["login"] or novo_login.strip()==user["login"]:
                            updated = next((x for x in load_usuarios() if x["login"]==novo_login.strip()),None)
                            if updated:
                                st.session_state.user = updated
                        st.success("✅ Usuário atualizado!")
                        st.rerun()

    st.markdown("---")
    st.markdown("**Todos os usuários**")
    for u in usuarios:
        c1,c2,c3,c4 = st.columns([2,2,2,1])
        c1.markdown(f"**{u['nome']}**")
        c2.markdown(f"`{u['login']}`")
        c3.markdown(NIVEIS.get(u["nivel"],u["nivel"]))
        if u["nivel"]!="comandante" and c4.button("🗑️", key=f"delu_{u['login']}"):
            usuarios = [x for x in usuarios if x["login"]!=u["login"]]
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
    st.download_button("⬇️ Baixar backup JSON",
                       data=json.dumps(backup, ensure_ascii=False, indent=2).encode("utf-8"),
                       file_name=f"leal_cx_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                       mime="application/json")

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

    op = next((o for o in ops if o["id"]==user.get("op_id")), None)
    if not op:
        st.error("Operador não encontrado. Contate o administrador.")
        return

    st.markdown(f"""
    <div style='padding:1.5rem 0 1rem;'>
        <div style='display:flex;align-items:center;gap:16px;margin-bottom:4px;'>
            <div style='width:52px;height:52px;border-radius:14px;
                        background:linear-gradient(135deg,#1A1500,#2A2000);
                        border:1px solid #C9A84C;
                        display:flex;align-items:center;justify-content:center;
                        font-size:22px;font-weight:700;color:#C9A84C;
                        box-shadow:0 0 20px rgba(201,168,76,0.15);'>
                {op['nome'][0].upper()}
            </div>
            <div>
                <h1 style='margin:0;font-size:24px;color:#FFFFFF;'>Olá, {op['nome'].split()[0]}!</h1>
                <p style='margin:0;font-size:13px;color:#555555;'>{op.get('cargo','Operador(a)')} · {tenure(op.get('adm'))} de empresa</p>
            </div>
        </div>
    </div>
    <hr/>
    """, unsafe_allow_html=True)

    op_evs = sorted([e for e in evs if e["op_id"]==op["id"]],
                    key=lambda x:(x.get("mes",""),x.get("ciclo","")), reverse=True)

    if not op_evs:
        st.info("Você ainda não possui avaliações registradas.")
        return

    last = op_evs[0]
    fn   = eval_final(last, pesos)
    fx   = get_faixa(fn, faixas)
    iv   = eval_int(last)
    mp_v = float(last["mp"]) if last.get("mp") not in (None,"") else None

    st.markdown(f"<p style='color:#666;font-size:12px;font-weight:500;letter-spacing:0.06em;margin-bottom:0.8rem;'>ÚLTIMA AVALIAÇÃO — {last.get('mes','—')} / {last.get('ciclo','—')}</p>", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    c1.metric("Nota MP",       f"{mp_v:.1f}" if mp_v is not None else "—")
    c2.metric("Nota interna",  f"{iv:.1f}"   if iv  is not None else "—")
    c3.metric("Nota final",    f"{fn:.1f}%"  if fn  is not None else "—")

    if fn is not None:
        pct = min(100, max(0, fn))
        cor = nota_cor(fn)
        st.markdown(f"""
        <div style='background:#0D0D0D;border:1px solid #1A1A1A;border-radius:12px;padding:20px;margin:1rem 0;'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;'>
                <span style='font-size:12px;color:#555;font-weight:600;letter-spacing:0.06em;'>PROGRESSO DA META</span>
                <span style='font-size:20px;font-weight:700;color:{cor};'>{fn:.1f}%</span>
            </div>
            <div style='height:8px;background:#1A1A1A;border-radius:4px;overflow:hidden;'>
                <div style='height:100%;width:{pct}%;background:linear-gradient(90deg,#8B6914,{cor});
                            border-radius:4px;box-shadow:0 0 10px rgba(201,168,76,0.4);'></div>
            </div>
            <div style='display:flex;justify-content:space-between;margin-top:8px;font-size:11px;color:#333;'>
                <span>0%</span><span>50%</span><span>100%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(badge_faixa(fx), unsafe_allow_html=True)
        proxima = next((f for f in sorted(faixas,key=lambda x:x["min"]) if f["min"]>fn), None)
        if proxima:
            falta = round(proxima["min"]-fn, 2)
            st.markdown(f"<p style='color:#C9A84C;font-size:13px;margin-top:8px;'>✦ Faltam <b>{falta} pontos</b> para <b>{proxima['desc']}</b> → R$ {proxima['bonus']:.2f}</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:#E8CC7A;font-weight:600;'>🏆 Você atingiu a faixa máxima!</p>", unsafe_allow_html=True)

    if last.get("pos") or last.get("feed") or last.get("acao"):
        st.markdown("---")
        st.markdown("<p style='color:#666;font-size:12px;font-weight:600;letter-spacing:0.06em;margin-bottom:0.8rem;'>FEEDBACK DA AVALIAÇÃO</p>", unsafe_allow_html=True)
        if last.get("pos"):
            st.markdown(f"<div style='background:#0D0D0D;border:1px solid #1A1A1A;border-left:3px solid #4A7A4A;border-radius:8px;padding:16px;margin-bottom:10px;'><p style='color:#5A9A5A;font-size:11px;font-weight:600;letter-spacing:0.06em;margin-bottom:8px;'>✓ PONTOS POSITIVOS</p><p style='color:#C0C0C0;font-size:14px;line-height:1.6;margin:0;'>{last['pos']}</p></div>", unsafe_allow_html=True)
        if last.get("feed"):
            st.markdown(f"<div style='background:#0D0D0D;border:1px solid #1A1A1A;border-left:3px solid #7A5A3A;border-radius:8px;padding:16px;margin-bottom:10px;'><p style='color:#C9841A;font-size:11px;font-weight:600;letter-spacing:0.06em;margin-bottom:8px;'>⚠ PONTOS DE MELHORIA</p><p style='color:#C0C0C0;font-size:14px;line-height:1.6;margin:0;'>{last['feed']}</p></div>", unsafe_allow_html=True)
        if last.get("acao"):
            st.markdown(f"<div style='background:#0D0D0D;border:1px solid #1A1A1A;border-left:3px solid #C9A84C;border-radius:8px;padding:16px;'><p style='color:#C9A84C;font-size:11px;font-weight:600;letter-spacing:0.06em;margin-bottom:8px;'>→ PLANO DE AÇÃO</p><p style='color:#C0C0C0;font-size:14px;line-height:1.6;margin:0;'>{last['acao']}</p></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='color:#666;font-size:12px;font-weight:600;letter-spacing:0.06em;margin-bottom:0.8rem;'>EVOLUÇÃO — NOTA FINAL POR MÊS E CICLO</p>", unsafe_allow_html=True)

    chart_rows = []
    for e in sorted(op_evs, key=lambda x:(x.get("mes",""),x.get("ciclo",""))):
        fn_e = eval_final(e, pesos)
        if fn_e is not None:
            chart_rows.append({
                "Período": f"{e.get('mes','?')} / {e.get('ciclo','?')}",
                "Nota final (%)": fn_e,
                "Nota MP": float(e["mp"]) if e.get("mp") not in (None,"") else None,
                "Nota interna": eval_int(e),
            })

    if chart_rows:
        df_chart = pd.DataFrame(chart_rows).set_index("Período")
        cols_disp = [c for c in ["Nota final (%)","Nota MP","Nota interna"] if df_chart[c].notna().any()]
        st.line_chart(df_chart[cols_disp])

        st.markdown("<p style='color:#666;font-size:12px;font-weight:600;letter-spacing:0.06em;margin-top:1.5rem;margin-bottom:0.8rem;'>HISTÓRICO COMPLETO</p>", unsafe_allow_html=True)
        hist = []
        for e in op_evs:
            fn_h = eval_final(e, pesos)
            fx_h = get_faixa(fn_h, faixas)
            hist.append({
                "Mês":          e.get("mes","—"),
                "Ciclo":        e.get("ciclo","—"),
                "Nota MP":      f"{float(e['mp']):.1f}" if e.get("mp") not in (None,"") else "—",
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

    # Injetar estrelas animadas para usuários logados
    st.markdown(STARS_JS, unsafe_allow_html=True)

    if nivel == "tripulacao":
        render_sidebar(user)
        portal_tripulacao(user)
    else:
        render_sidebar(user)
        readonly = (nivel == "observador")
        page = st.session_state.get("page","Dashboard")

        if page == "Dashboard":       pagina_dashboard(user, readonly)
        elif page == "Operadores":    pagina_operadores(user, readonly)
        elif page == "Avaliações":    pagina_avaliacoes(user, readonly)
        elif page == "Metas":         pagina_metas(user, readonly)
        elif page == "Evolução":      pagina_evolucao(user, readonly)
        elif page == "Configurações" and nivel=="comandante":
            pagina_configuracoes(user)
