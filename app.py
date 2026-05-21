import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import calendar
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configuração de página corporativa de alta fidelidade - Estilo Discord/Codespaces
st.set_page_config(
    page_title="Mercado Pago CX - Leal Assessoria",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estabelece a conexão nativa com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def inject_premium_dark_theme():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Ginto:wght@400;500;700&family=Inter:wght@300;400;500;600;700&display=swap');
            
            html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
                font-family: 'Inter', sans-serif;
                background-color: #1e1f22 !important;
                color: #dbdee1 !important;
            }
            [data-testid="stSidebar"] {
                background-color: #111214 !important;
                border-right: 1px solid #2b2d31 !important;
                padding-top: 10px;
            }
            h1, h2, h3, h4 { 
                color: #f2f3f5 !important; 
                font-weight: 700 !important;
                letter-spacing: -0.3px;
            }
            div[data-testid="stRadio"] [data-testid="stWidgetLabel"] { display: none !important; }
            div[data-testid="stRadio"] > div { flex-direction: column !important; gap: 4px; }
            div[data-testid="stRadio"] label {
                background-color: transparent !important;
                border-radius: 5px !important;
                padding: 10px 14px !important;
                color: #949ba4 !important;
                transition: all 0.15s ease-in-out;
                width: 100%;
                cursor: pointer;
                border: none !important;
            }
            div[data-testid="stRadio"] label:hover { background-color: #35373c !important; color: #dbdee1 !important; }
            div[data-testid="stRadio"] label[data-checked="true"] {
                background-color: #404249 !important;
                color: #ffffff !important;
                font-weight: 600 !important;
            }
            div[data-testid="stRadio"] label [data-testid="stMarker"] { display: none !important; }

            .discord-profile {
                background-color: #111214; border-radius: 12px; overflow: hidden;
                border: 1px solid #2b2d31; margin-bottom: 25px;
            }
            .discord-banner {
                background: linear-gradient(90deg, #009ee3 0%, #002f6c 100%); height: 100px; width: 100%;
            }
            .discord-avatar-area {
                padding: 0 20px; margin-top: -45px; display: flex; align-items: flex-end;
                justify-content: space-between; margin-bottom: 15px;
            }
            .discord-avatar {
                width: 85px; height: 85px; border-radius: 50%; background-color: #5865f2;
                border: 6px solid #111214; display: flex; align-items: center; justify-content: center;
                font-size: 28px; color: white; font-weight: bold; position: relative;
            }
            .discord-status-online {
                position: absolute; width: 20px; height: 20px; background-color: #23a55a;
                border-radius: 50%; bottom: -2px; right: -2px; border: 4px solid #111214;
            }
            .discord-badge-container { display: flex; gap: 6px; margin-bottom: 5px; }
            .discord-badge {
                background-color: #23a55a; color: white; font-size: 10px; font-weight: bold;
                padding: 3px 8px; border-radius: 4px; text-transform: uppercase;
            }
            .discord-badge-blue { background-color: #009ee3; }
            .discord-badge-purple { background-color: #5865f2; }
            .discord-badge-gold { background-color: #f0b232; color: #111214; }
            .discord-body { padding: 0 20px 20px 20px; }
            
            .cx-metric-card {
                background-color: #2b2d31; border: 1px solid #3f4248; border-radius: 8px; padding: 16px; margin-bottom: 15px;
            }
            .cx-label { font-size: 11px; color: #949ba4; font-weight: 600; text-transform: uppercase; }
            .cx-value { font-size: 24px; color: #f2f3f5; font-weight: 700; margin-top: 4px; }
            
            .stTextArea textarea, .stTextInput input, .stSelectbox div, .stNumberInput input, .stDateInput input { 
                background-color: #111214 !important; border: 1px solid #383a40 !important; color: #dbdee1 !important;
            }
            .stButton>button { 
                background-color: #5865f2 !important; color: white !important; border-radius: 4px !important; font-weight: 600 !important; width: 100%;
            }
            .stButton>button:hover { background-color: #4752c4 !important; }
            .stTabs [data-baseweb="tab-list"] { background-color: #111214; padding: 4px; border-radius: 6px; }
            .stTabs [data-baseweb="tab"] { color: #949ba4 !important; }
            .stTabs [aria-selected="true"] { color: #ffffff !important; font-weight: 700; }

            /* Estilos para a tela bonita de Feedback 1v1 */
            .feedback-board {
                background-color: #111214; border: 1px solid #2b2d31; border-radius: 12px; padding: 25px; margin-top: 15px;
            }
            .feedback-card-glow {
                background: #2b2d31; border-left: 5px solid #5865f2; border-radius: 6px; padding: 15px; margin-bottom: 15px;
            }
            .feedback-title { font-size: 14px; font-weight: 700; color: #f2f3f5; text-transform: uppercase; margin-bottom: 5px;}
            .feedback-text { font-size: 15px; color: #dbdee1; line-height: 1.5; }
        </style>
    """, unsafe_allow_html=True)

def calcular_tempo_atividade(data_admissao_val):
    try:
        if isinstance(data_admissao_val, (datetime, pd.Timestamp)):
            adm = data_admissao_val.date()
        else:
            adm = datetime.strptime(str(data_admissao_val).strip(), "%d/%m/%Y").date()
        hoje = datetime.now().date()
        if adm > hoje: return "Futuro"
        anos = hoje.year - adm.year
        meses = hoje.month - adm.month
        dias = hoje.day - adm.day
        if dias < 0:
            meses -= 1
            prev_month = hoje.month - 1 if hoje.month > 1 else 12
            prev_year = hoje.year if hoje.month > 1 else hoje.year - 1
            dias += calendar.monthrange(prev_year, prev_month)[1]
        if meses < 0:
            anos -= 1
            meses += 12
        partes = []
        if anos > 0: partes.append(f"{anos}a")
        if meses > 0: partes.append(f"{meses}m")
        if dias > 0: partes.append(f"{dias}d")
        return ", ".join(partes) if partes else "0d"
    except:
        return "N/A"

def get_data(worksheet_name, expected_cols):
    try:
        df = conn.read(worksheet=worksheet_name, ttl=0)
        df = df.dropna(how="all")
        if df.empty:
            return pd.DataFrame(columns=expected_cols)
        for col in expected_cols:
            if col not in df.columns:
                df[col] = np.nan
        return df[expected_cols]
    except:
        return pd.DataFrame(columns=expected_cols)

def save_data(worksheet_name, df):
    df = df.reset_index(drop=True)
    conn.update(worksheet=worksheet_name, data=df)
    st.cache_data.clear()

def listar_operadores():
    df_ops = get_data("Operadores", ["Nome", "Squad", "Nivel", "Admissao"])
    ops = []
    for _, row in df_ops.iterrows():
        if pd.notna(row["Nome"]) and str(row["Nome"]).strip() != "":
            ops.append({
                "nome": str(row["Nome"]).strip(),
                "squad": str(row["Squad"]),
                "nivel": str(row["Nivel"]),
                "admissao": str(row["Admissao"])
            })
    return sorted(ops, key=lambda x: x["nome"])

def salvar_perfil_operador(nome, squad, nivel, admissao):
    df_ops = get_data("Operadores", ["Nome", "Squad", "Nivel", "Admissao"])
    nome_clean = nome.strip()
    if nome_clean in df_ops["Nome"].astype(str).str.strip().values:
        return False
    new_row = pd.DataFrame([{"Nome": nome_clean, "Squad": squad, "Nivel": nivel, "Admissao": admissao.strftime("%d/%m/%Y")}])
    df_ops = pd.concat([df_ops, new_row], ignore_index=True)
    save_data("Operadores", df_ops)
    return True

def atualizar_perfil_operador(nome_antigo, nome_novo, nova_admissao):
    df_ops = get_data("Operadores", ["Nome", "Squad", "Nivel", "Admissao"])
    df_ciclos = get_data("Historico_Ciclos", ["Ciclo", "Operador", "Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR", "NPS"])
    df_feedbacks = get_data("Feedbacks", ["Data_Hora", "Operador", "Ciclo", "Metricas", "Gaps", "PDI"])
    
    nome_a_clean = nome_antigo.strip()
    nome_n_clean = nome_novo.strip()
    
    idx = df_ops[df_ops["Nome"].astype(str).str.strip() == nome_a_clean].index
    if len(idx) > 0:
        df_ops.loc[idx, "Nome"] = nome_n_clean
        df_ops.loc[idx, "Admissao"] = nova_admissao.strftime("%d/%m/%Y")
        save_data("Operadores", df_ops)
        
        df_ciclos.loc[df_ciclos["Operador"].astype(str).str.strip() == nome_a_clean, "Operador"] = nome_n_clean
        save_data("Historico_Ciclos", df_ciclos)
        
        df_feedbacks.loc[df_feedbacks["Operador"].astype(str).str.strip() == nome_a_clean, "Operador"] = nome_n_clean
        save_data("Feedbacks", df_feedbacks)
        return True
    return False

def deletar_operador(nome):
    nome_clean = nome.strip()
    save_data("Operadores", get_data("Operadores", ["Nome", "Squad", "Nivel", "Admissao"])[lambda x: x["Nome"].astype(str).str.strip() != nome_clean])
    save_data("Historico_Ciclos", get_data("Historico_Ciclos", ["Ciclo", "Operador", "Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR", "NPS"])[lambda x: x["Operador"].astype(str).str.strip() != nome_clean])
    save_data("Feedbacks", get_data("Feedbacks", ["Data_Hora", "Operador", "Ciclo", "Metricas", "Gaps", "PDI"])[lambda x: x["Operador"].astype(str).str.strip() != nome_clean])

def main():
    inject_premium_dark_theme()
    lista_ops = listar_operadores()
    
    with st.sidebar:
        st.markdown("<div style='padding: 10px 0;'><h2 style='margin:0; font-size:22px; color:#ffffff !important;'>Mercado Pago - CX</h2><p style='color:#949ba4 !important; font-size:14px; margin-top:2px;'>Leal Assessoria</p></div>", unsafe_allow_html=True)
        st.divider()
        st.markdown("<span style='font-size:10px; font-weight:700; color:#949ba4; letter-spacing: 0.8px;'>MÓDULOS DE NAVEGAÇÃO</span>", unsafe_allow_html=True)
        view_mode = st.radio("Navegação:", ["📊 Overview", "👤 Profile Analytics", "📢 1v1 Feedback", "📥 Log Notes", "🤖 AI Studio", "➕ Add Operator", "⚙️ Control Management"], label_visibility="collapsed")
        st.divider()
        st.markdown(f"<div style='color:#23a55a; font-size:12px; font-weight:600;'>● {len(lista_ops)} Operadores Conectados (Sheets)</div>", unsafe_allow_html=True)

    # 1. OVERVIEW
    if view_mode == "📊 Overview":
        st.title("Visão Geral da Célula")
        st.markdown("Métricas consolidadas sincronizadas em tempo real via Cloud Database Google Sheets.")
        
        df_ciclos = get_data("Historico_Ciclos", ["Ciclo", "Operador", "Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR", "NPS"])
        dados_ranking = []
        
        for op in lista_ops:
            df_ind = df_ciclos[df_ciclos["Operador"].astype(str).str.strip() == op["nome"]]
            mb, mi, mc, mnps = np.nan, np.nan, 0.0, np.nan
            if not df_ind.empty:
                mb = pd.to_numeric(df_ind["Nota_Banco"], errors='coerce').mean()
                mi = pd.to_numeric(df_ind["Nota_Interna"], errors='coerce').mean()
                mnps = pd.to_numeric(df_ind["NPS"], errors='coerce').mean()
                mc = np.nanmean([mb, mi]) if not (np.isnan(mb) and np.isnan(mi)) else 0.0
                
            dados_ranking.append({
                "Operador": op["nome"], 
                "Tempo de Casa": calcular_tempo_atividade(op.get("admissao", "19/05/2026")),
                "Média Mercado Pago": f"{mb:.1f}" if not np.isnan(mb) else "S/D",
                "Média Interna QA": f"{mi:.1f}" if not np.isnan(mi) else "S/D",
                "Média NPS": f"{mnps:.1f}" if not np.isnan(mnps) else "S/D",
                "Consolidado Geral": mc
            })
            
        if not dados_ranking:
            st.info("Nenhum operador registrado no sistema ou planilha vazia.")
        else:
            df_master = pd.DataFrame(dados_ranking).sort_values(by="Consolidado Geral", ascending=False).reset_index(drop=True)
            df_master.insert(0, 'Rank', df_master.index + 1)
            
            st.markdown("### Painel de Liderança de Performance")
            cols = st.columns(3)
            for idx, row in df_master.head(6).iterrows():
                with cols[idx % 3]:
                    st.markdown(f"<div class='cx-metric-card' style='border-top: 3px solid #5865f2;'><div style='display:flex; justify-content:space-between;'><span class='cx-label'>#{row['Rank']} NO RANKING</span><span style='color:#23a55a; font-size:11px; font-weight:700;'>{row['Tempo de Casa']}</span></div><div class='cx-value' style='font-size:18px;'>{row['Operador']}</div><div style='margin-top:10px; font-size:12px; display:flex; justify-content:space-between; color:#b5bac1;'><span>Score MP: <b>{row['Média Mercado Pago']}</b></span><span>QA Leal: <b>{row['Média Interna QA']}</b></span><span>NPS: <b>{row['Média NPS']}</b></span></div></div>", unsafe_allow_html=True)
            
            st.divider()
            
            # Formatação segura para remover dízimas (.000000) e centralizar tudo perfeitamente
            df_master["Consolidado Geral"] = df_master["Consolidado Geral"].map(lambda x: f"{x:.1f}" if x > 0 else "0.0")
            df_centralizado = df_master.style.set_properties(**{'text-align': 'center'}).set_table_styles([
                {'selector': 'th', 'props': [('text-align', 'center')]}
            ])
            st.dataframe(df_centralizado, use_container_width=True, hide_index=True)

    # 2. PROFILE ANALYTICS
    elif view_mode == "👤 Profile Analytics":
        st.title("Profile Quality Audit")
        if not lista_ops: st.warning("Nenhum operador cadastrado.")
        else:
            op_escolhido = st.selectbox("Inspecionar Perfil do Analista:", [o["nome"] for o in lista_ops])
            meta_op = next(o for o in lista_ops if o["nome"] == op_escolhido)
            
            df_ind = get_data("Historico_Ciclos", ["Ciclo", "Operador", "Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR", "NPS"])[lambda x: x["Operador"].astype(str).str.strip() == op_escolhido].copy()
            df_feed_ind = get_data("Feedbacks", ["Data_Hora", "Operador", "Ciclo", "Metricas", "Gaps", "PDI"])[lambda x: x["Operador"].astype(str).str.strip() == op_escolhido].copy()
            
            if not df_ind.empty:
                for c in ["Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR", "NPS"]: df_ind[c] = pd.to_numeric(df_ind[c], errors="coerce")
            
            med_banco = df_ind["Nota_Banco"].mean() if not df_ind.empty else 0
            med_interna = df_ind["Nota_Interna"].mean() if not df_ind.empty else 0
            med_nps = df_ind["NPS"].mean() if not df_ind.empty else 0
            tempo_casa = calcular_tempo_atividade(meta_op.get("admissao", "19/05/2026"))
            
            badges = f"<span class='discord-badge discord-badge-blue'>Leal Staff</span>"
            if med_interna >= 90: badges += "<span class='discord-badge discord-badge-gold'>🏆 Master QA</span>"
            if med_banco >= 85: badges += "<span class='discord-badge discord-badge-purple'>⚡ MP Hero</span>"
            
            iniciais = "".join([p[0] for p in op_escolhido.split()[:2]]).upper()
            st.markdown(f"<div class='discord-profile'><div class='discord-banner'></div><div class='discord-avatar-area'><div class='discord-avatar'>{iniciais}<div class='discord-status-online'></div></div><div class='discord-badge-container'>{badges}</div></div><div class='discord-body'><h2 style='margin:0; font-size:24px; color:#ffffff;'>{meta_op['nome']}</h2><p style='margin:2px 0 10px 0; color:#b5bac1; font-size:14px;'>@operador_cx_leal</p><hr style='border-color:#2b2d31 !important;'><div style='display:grid; grid-template-columns: 1fr 1fr 1fr; gap:15px; margin-top:15px;'><div><span class='cx-label'>SQUAD ALOCADA</span><div style='color:#dbdee1; font-size:14px; font-weight:600;'>{meta_op['squad']}</div></div><div><span class='cx-label'>PARCEIRO</span><div style='color:#009ee3; font-size:14px; font-weight:600;'>Leal ➔ Mercado Pago</div></div><div><span class='cx-label'>TEMPO DE ATIVIDADE</span><div style='color:#23a55a; font-size:14px; font-weight:600;'>{tempo_casa}</div></div></div></div></div>", unsafe_allow_html=True)
            
            txt_banco = f"{med_banco:.1f}" if med_banco > 0 else "S/D"
            txt_interna = f"{med_interna:.1f}" if med_interna > 0 else "S/D"
            txt_nps = f"{med_nps:.1f}" if not np.isnan(med_nps) and len(df_ind) > 0 else "S/D"
            
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(f"<div class='cx-metric-card'><span class='cx-label'>Média Mercado Pago</span><div class='cx-value'>{txt_banco}</div></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='cx-metric-card'><span class='cx-label'>Média Auditoria Leal</span><div class='cx-value'>{txt_interna}</div></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='cx-metric-card'><span class='cx-label'>Média NPS</span><div class='cx-value'>{txt_nps}</div></div>", unsafe_allow_html=True)
            with c4: st.markdown(f"<div class='cx-metric-card'><span class='cx-label'>Monitorias Coletadas</span><div class='cx-value'>{len(df_ind)} Ciclos</div></div>", unsafe_allow_html=True)
            
            st.markdown("#### Histórico de Evolução de Notas")
            st.line_chart(df_ind.set_index("Ciclo")[["Nota_Banco", "Nota_Interna", "NPS"]].dropna(how='all'), color=["#009ee3", "#5865f2", "#23a55a"])

    # 3. 1V1 FEEDBACK SESSION (NOVA ABA COMPLETA E CUSTOMIZÁVEL)
    elif view_mode == "📢 1v1 Feedback":
        st.title("📢 Painel de Apresentação Feedback 1v1")
        st.markdown("Use esta aba para apresentar as avaliações diretamente ao operador. Escolha exatamente o que quer mostrar na tela.")
        
        if not lista_ops: 
            st.warning("Nenhum operador cadastrado.")
        else:
            cc1, cc2 = st.columns([1, 3])
            with cc1:
                st.markdown("### ⚙️ Filtros de Exibição")
                op_feedback = st.selectbox("Selecione o Operador:", [o["nome"] for o in lista_ops])
                ciclo_feedback = st.selectbox("Selecione o Ciclo:", ["Ciclo 1", "Ciclo 2", "Ciclo 3", "Ciclo 4"])
                
                st.divider()
                st.write("**Marque o que deseja exibir:**")
                show_mp = st.checkbox("Nota Mercado Pago", value=True)
                show_leal = st.checkbox("Nota Interna Leal", value=True)
                show_nps = st.checkbox("Métrica de NPS", value=True)
                show_pilares = st.checkbox("Pilares (Compliance, Soft Skills, FCR)", value=False)
                show_gaps = st.checkbox("Diagnóstico de Gaps", value=True)
                show_pdi = st.checkbox("Plano de Ação Corretivo (PDI)", value=True)
                
            with cc2:
                st.markdown(f"### 📄 Quadro de Performance de {op_feedback} — `{ciclo_feedback}`")
                
                # Resgate dos dados das duas tabelas
                df_c = get_data("Historico_Ciclos", ["Ciclo", "Operador", "Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR", "NPS"])
                df_f = get_data("Feedbacks", ["Data_Hora", "Operador", "Ciclo", "Metricas", "Gaps", "PDI"])
                
                row_c = df_c[(df_c["Operador"].astype(str).str.strip() == op_feedback.strip()) & (df_c["Ciclo"].astype(str).str.strip() == ciclo_feedback.strip())]
                row_f = df_f[(df_f["Operador"].astype(str).str.strip() == op_feedback.strip()) & (df_f["Ciclo"].astype(str).str.strip() == ciclo_feedback.strip())]
                
                if row_c.empty:
                    st.info("Nenhum dado de monitoria foi localizado para este ciclo específico.")
                else:
                    st.markdown("<div class='feedback-board'>", unsafe_allow_html=True)
                    
                    # Seção de Métricas Principais
                    num_cols = sum([show_mp, show_leal, show_nps])
                    if num_cols > 0:
                        m_cols = st.columns(num_cols)
                        idx_col = 0
                        if show_mp:
                            val = row_c.iloc[0]["Nota_Banco"]
                            m_cols[idx_col].markdown(f"<div class='cx-metric-card' style='border-top:3px solid #009ee3'><span class='cx-label'>Nota Mercado Pago</span><div class='cx-value'>{val}</div></div>", unsafe_allow_html=True)
                            idx_col += 1
                        if show_leal:
                            val = row_c.iloc[0]["Nota_Interna"]
                            m_cols[idx_col].markdown(f"<div class='cx-metric-card' style='border-top:3px solid #5865f2'><span class='cx-label'>Nota Auditoria Leal</span><div class='cx-value'>{val}</div></div>", unsafe_allow_html=True)
                            idx_col += 1
                        if show_nps:
                            val = row_c.iloc[0]["NPS"]
                            m_cols[idx_col].markdown(f"<div class='cx-metric-card' style='border-top:3px solid #23a55a'><span class='cx-label'>Score NPS</span><div class='cx-value'>{val if pd.notna(val) else 'S/D'}</div></div>", unsafe_allow_html=True)
                    
                    # Seção de Pilares Técnicos
                    if show_pilares:
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("#### 🎯 Alinhamento de Pilares Operacionais")
                        pc1, pc2, pc3 = st.columns(3)
                        pc1.metric("Compliance e Regras", f"{row_c.iloc[0]['Compliance'] or 0}%")
                        pc2.metric("Soft Skills e Empatia", f"{row_c.iloc[0]['Soft_Skills'] or 0}%")
                        pc3.metric("Resolutividade (FCR)", f"{row_c.iloc[0]['FCR'] or 0}%")
                        
                    # Seção de Textos de Diagnóstico/PDI
                    if show_gaps:
                        gap_text = row_f.iloc[0]["Gaps"] if not row_f.empty else "Não documentado."
                        st.markdown(f"<div class='feedback-card-glow'><div class='feedback-title'>🔍 Diagnóstico e Gaps Identificados</div><div class='feedback-text'>{gap_text}</div></div>", unsafe_allow_html=True)
                        
                    if show_pdi:
                        pdi_text = row_f.iloc[0]["PDI"] if not row_f.empty else "Não documentado."
                        st.markdown(f"<div class='feedback-card-glow' style='border-left-color: #23a55a;'><div class='feedback-title' style='color:#23a55a;'>🌱 Plano de Desenvolvimento Individual (PDI)</div><div class='feedback-text'>{pdi_text}</div></div>", unsafe_allow_html=True)
                        
                    st.markdown("</div>", unsafe_allow_html=True)

    # 4. LOG NOTES (ALTERAÇÃO: NUM_INPUT PARA EDIÇÃO COMPLETA A QUALQUER MOMENTO)
    elif view_mode == "📥 Log Notes":
        st.title("Central de Auditoria de Monitoria (QA)")
        st.markdown("Insira ou edite as notas do operador para o ciclo selecionado. Se o ciclo já possuir notas, elas serão substituídas automaticamente.")
        if not lista_ops: st.warning("Cadastre profissionais antes de realizar auditorias.")
        else:
            with st.container(border=True):
                col1, col2 = st.columns(2)
                with col1:
                    op_alvo = st.selectbox("Escolha o Operador:", [o["nome"] for o in lista_ops])
                    ciclo_alvo = st.selectbox("Ciclo Avaliado:", ["Ciclo 1", "Ciclo 2", "Ciclo 3", "Ciclo 4"])
                    
                    # Puxar dados pré-existentes se houver para facilitar re-edição fluida
                    df_c_atual = get_data("Historico_Ciclos", ["Ciclo", "Operador", "Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR", "NPS"])
                    match_existente = df_c_atual[(df_c_atual["Operador"].astype(str).str.strip() == op_alvo.strip()) & (df_c_atual["Ciclo"].astype(str).str.strip() == ciclo_alvo.strip())]
                    
                    val_init_mp = float(match_existente.iloc[0]["Nota_Banco"]) if not match_existente.empty and pd.notna(match_existente.iloc[0]["Nota_Banco"]) else 85.0
                    val_init_leal = float(match_existente.iloc[0]["Nota_Interna"]) if not match_existente.empty and pd.notna(match_existente.iloc[0]["Nota_Interna"]) else 85.0
                    val_init_nps = float(match_existente.iloc[0]["NPS"]) if not match_existente.empty and pd.notna(match_existente.iloc[0]["NPS"]) else 0.0
                    
                    nota_mp = st.number_input("Nota Oficial Mercado Pago (0 a 100):", 0.0, 100.0, val_init_mp, step=1.0)
                    nota_leal = st.number_input("Nota Interna Leal (0 a 100):", 0.0, 100.0, val_init_leal, step=1.0)
                    nota_nps = st.number_input("Nota NPS Geral do Operador (-100 a 100):", -100.0, 100.0, val_init_nps, step=1.0)
                with col2:
                    st.markdown("<span class='cx-label'>Pilares Técnicos (Digite o valor de 0 a 100)</span>", unsafe_allow_html=True)
                    val_init_comp = int(match_existente.iloc[0]["Compliance"]) if not match_existente.empty and pd.notna(match_existente.iloc[0]["Compliance"]) else 85
                    val_init_soft = int(match_existente.iloc[0]["Soft_Skills"]) if not match_existente.empty and pd.notna(match_existente.iloc[0]["Soft_Skills"]) else 85
                    val_init_fcr = int(match_existente.iloc[0]["FCR"]) if not match_existente.empty and pd.notna(match_existente.iloc[0]["FCR"]) else 85
                    
                    v_comp = st.number_input("Compliance e Regras:", 0, 100, val_init_comp, step=1)
                    v_soft = st.number_input("Soft Skills e Cordialidade:", 0, 100, val_init_soft, step=1)
                    v_fcr = st.number_input("Resolutividade (FCR):", 0, 100, val_init_fcr, step=1)
                
                df_f_atual = get_data("Feedbacks", ["Data_Hora", "Operador", "Ciclo", "Metricas", "Gaps", "PDI"])
                match_f_existente = df_f_atual[(df_f_atual["Operador"].astype(str).str.strip() == op_alvo.strip()) & (df_f_atual["Ciclo"].astype(str).str.strip() == ciclo_alvo.strip())]
                val_init_gaps = str(match_f_existente.iloc[0]["Gaps"]) if not match_f_existente.empty else ""
                val_init_pdi = str(match_f_existente.iloc[0]["PDI"]) if not match_f_existente.empty else ""
                
                diag = st.text_area("Diagnóstico Técnico de Gaps:", value=val_init_gaps)
                pdi = st.text_area("Plano de Ação Corretivo (PDI):", value=val_init_pdi)
                
                if st.button("🚀 Gravar / Atualizar Auditoria no Google Sheets"):
                    df_c = get_data("Historico_Ciclos", ["Ciclo", "Operador", "Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR", "NPS"])
                    match = (df_c["Operador"].astype(str).str.strip() == op_alvo.strip()) & (df_c["Ciclo"].astype(str).str.strip() == ciclo_alvo.strip())
                    if match.any():
                        df_c.loc[df_c[match].index, ["Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR", "NPS"]] = [nota_mp, nota_leal, v_comp, v_soft, v_fcr, nota_nps]
                    else:
                        df_c = pd.concat([df_c, pd.DataFrame([{"Ciclo": ciclo_alvo, "Operador": op_alvo.strip(), "Nota_Banco": nota_mp, "Nota_Interna": nota_leal, "Compliance": v_comp, "Soft_Skills": v_soft, "FCR": v_fcr, "NPS": nota_nps}])], ignore_index=True)
                    save_data("Historico_Ciclos", df_c)
                    
                    df_f = get_data("Feedbacks", ["Data_Hora", "Operador", "Ciclo", "Metricas", "Gaps", "PDI"])
                    match_f = (df_f["Operador"].astype(str).str.strip() == op_alvo.strip()) & (df_f["Ciclo"].astype(str).str.strip() == ciclo_alvo.strip())
                    if match_f.any():
                        df_f.loc[df_f[match_f].index, ["Data_Hora", "Metricas", "Gaps", "PDI"]] = [datetime.now().strftime('%d/%m/%Y %H:%M'), f"MP: {nota_mp} | Leal: {nota_leal} | NPS: {nota_nps}", diag if diag else 'Nenhum', pdi if pdi else 'Preventivo']
                    else:
                        df_f = pd.concat([df_f, pd.DataFrame([{"Data_Hora": datetime.now().strftime('%d/%m/%Y %H:%M'), "Operador": op_alvo.strip(), "Ciclo": ciclo_alvo, "Metricas": f"MP: {nota_mp} | Leal: {nota_leal} | NPS: {nota_nps}", "Gaps": diag if diag else 'Nenhum', "PDI": pdi if pdi else 'Preventivo'}])], ignore_index=True)
                    save_data("Feedbacks", df_f)
                    st.success("Dados salvos e sincronizados perfeitamente!")
                    st.rerun()

    # 5. AI STUDIO
    elif view_mode == "🤖 AI Studio":
        st.title("AI Studio Engine")
        if not lista_ops: st.warning("Cadastre operadores primeiro.")
        else:
            op_ai = st.selectbox("Escolha o Analista Alvo:", [o["nome"] for o in lista_ops])
            templates = {
                "Report de Performance QA": "# REPORT DE PERFORMANCE CX\nOperador: {{OPERADOR}}\nMédia MP: {{NOTA_BANCO}}\nMédia Interna: {{NOTA_INTERNA}}\n\n## Notas do QA:\n{{NOTAS_LIDER}}",
                "PDI Estratégico": "# PLANO DE DESENVOLVIMENTO INDIVIDUAL\nAnalista: {{OPERADOR}}\nScores: MP ({{NOTA_BANCO}}) | Leal ({{NOTA_INTERNA}})\n\n## Plano Estratégico:\n{{NOTAS_LIDER}}"
            }
            mod_sel = st.selectbox("Template Estrutural:", list(templates.keys()))
            obs_lider = st.text_area("Observações Avançadas:")
            
            df_ind = get_data("Historico_Ciclos", ["Ciclo", "Operador", "Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR", "NPS"])[lambda x: x["Operador"].astype(str).str.strip() == op_ai.strip()]
            mb = pd.to_numeric(df_ind["Nota_Banco"], errors="coerce").mean() if not df_ind.empty else 0.0
            mi = pd.to_numeric(df_ind["Nota_Interna"], errors="coerce").mean() if not df_ind.empty else 0.0
            
            payload = templates[mod_sel].replace("{{OPERADOR}}", op_ai).replace("{{NOTA_BANCO}}", f"{mb:.1f}").replace("{{NOTA_INTERNA}}", f"{mi:.1f}").replace("{{NOTAS_LIDER}}", obs_lider if obs_lider else "Sem notas.")
            st.text_area("Payload Pronto:", value=payload, height=200)

    # 6. ADD OPERATOR
    elif view_mode == "➕ Add Operator":
        st.title("Provisioning System")
        with st.container(border=True):
            novo_nome = st.text_input("Nome Completo:")
            data_adm = st.date_input("Data de Integração:")
            if st.button("💾 Provisionar Analista no Sheets"):
                if novo_nome.strip():
                    if salvar_perfil_operador(novo_nome.strip(), "Negociação em atraso", "Operador de CX", data_adm):
                        st.success("Criado!"); st.rerun()
                    else: st.error("Operador já cadastrado!")

    # 7. CONTROL MANAGEMENT
    elif view_mode == "⚙️ Control Management":
        st.title("Control Management")
        if not lista_ops: 
            st.warning("Sem analistas cadastrados.")
        else:
            op_gerenciar = st.selectbox("Escolha a Conta:", [o["nome"] for o in lista_ops])
            meta_g = next(o for o in lista_ops if o["nome"] == op_gerenciar)
            
            t_edit, t_danger = st.tabs(["📝 Editar", "🚨 Excluir"])
            
            with t_edit:
                nn = st.text_input("Corrigir Nome:", value=meta_g["nome"])
                
                try: 
                    da_inicial = datetime.strptime(meta_g["admissao"], "%d/%m/%Y").date()
                except: 
                    da_inicial = datetime.now().date()
                
                nova_data_adm = st.date_input("Corrigir Data de Admissão:", value=da_inicial)
                
                if st.button("Commit Alterações"):
                    if nn.strip():
                        with st.spinner("Sincronizando com o Google Sheets..."):
                            sucesso = atualizar_perfil_operador(op_gerenciar, nn.strip(), nova_data_adm)
                            if sucesso:
                                st.success("Cadastro atualizado com sucesso!")
                                st.rerun()
                            else:
                                st.error("Erro interno ao atualizar os registros.")
                    else:
                        st.warning("O campo de Nome não pode ser deixado em branco.")
                        
            with t_danger:
                if st.checkbox("Confirmar exclusão irreversível profissional") and st.button("Deletar do Sheets"):
                    deletar_operador(op_gerenciar)
                    st.success("Expurgado com sucesso!")
                    st.rerun()

if __name__ == "__main__":
    main()
