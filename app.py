import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import calendar
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configuração de página corporativa de alta fidelidade
st.set_page_config(
    page_title="Mercado Pago CX - Leal Assessoria",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Conexão Nativa com o Google Sheets
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
    df_ciclos = get_data("Historico_Ciclos", ["Ciclo", "Operador", "Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR"])
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
    save_data("Historico_Ciclos", get_data("Historico_Ciclos", ["Ciclo", "Operador", "Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR"])[lambda x: x["Operador"].astype(str).str.strip() != nome_clean])
    save_data("Feedbacks", get_data("Feedbacks", ["Data_Hora", "Operador", "Ciclo", "Metricas", "Gaps", "PDI"])[lambda x: x["Operador"].astype(str).str.strip() != nome_clean])

def main():
    inject_premium_dark_theme()
    lista_ops = listar_operadores()
    
    with st.sidebar:
        st.markdown("<div style='padding: 10px 0;'><h2 style='margin:0; font-size:22px; color:#ffffff !important;'>Mercado Pago - CX</h2><p style='color:#949ba4 !important; font-size:14px; margin-top:2px;'>Leal Assessoria</p></div>", unsafe_allow_html=True)
        st.divider()
        st.markdown("<span style='font-size:10px; font-weight:700; color:#949ba4; letter-spacing: 0.8px;'>MÓDULOS DE NAVEGAÇÃO</span>", unsafe_allow_html=True)
        view_mode = st.radio("Navegação:", ["📊 Overview", "👤 Profile Analytics", "📥 Log Notes", "🤖 AI Studio", "➕ Add Operator", "⚙️ Control Management"], label_visibility="collapsed")
        st.divider()
        st.markdown(f"<div style='color:#23a55a; font-size:12px; font-weight:600;'>● {len(lista_ops)} Operadores Conectados (Sheets)</div>", unsafe_allow_html=True)

    # 1. OVERVIEW
    if view_mode == "📊 Overview":
        st.title("Visão Geral da Célula")
        st.markdown("Métricas consolidadas sincronizadas em tempo real via Cloud Database Google Sheets.")
        
        df_ciclos = get_data("Historico_Ciclos", ["Ciclo", "Operador", "Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR"])
        dados_ranking = []
        
        for op in lista_ops:
            df_ind = df_ciclos[df_ciclos["Operador"].astype(str).str.strip() == op["nome"]]
            mb, mi, mc = np.nan, np.nan, 0.0
            if not df_ind.empty:
                mb = pd.to_numeric(df_ind["Nota_Banco"], errors='coerce').mean()
                mi = pd.to_numeric(df_ind["Nota_Interna"], errors='coerce').mean()
                mc = np.nanmean([mb, mi]) if not (np.isnan(mb) and np.isnan(mi)) else 0.0
                
            dados_ranking.append({
                "Operador": op["nome"], "Tempo de Casa": calcular_tempo_atividade(op.get("admissao", "19/05/2026")),
                "Média Mercado Pago": round(mb, 1) if not np.isnan(mb) else "S/D",
                "Média Interna QA": round(mi, 1) if not np.isnan(mi) else "S/D",
                "Consolidado Geral": round(mc, 1) if mc > 0 else 0.0
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
                    st.markdown(f"<div class='cx-metric-card' style='border-top: 3px solid #5865f2;'><div style='display:flex; justify-content:space-between;'><span class='cx-label'>#{row['Rank']} NO RANKING</span><span style='color:#23a55a; font-size:11px; font-weight:700;'>{row['Tempo de Casa']}</span></div><div class='cx-value' style='font-size:18px;'>{row['Operador']}</div><div style='margin-top:10px; font-size:12px; display:flex; justify-content:space-between; color:#b5bac1;'><span>Score MP: <b>{row['Média Mercado Pago']}</b></span><span>Score QA Leal: <b>{row['Média Interna QA']}</b></span></div></div>", unsafe_allow_html=True)
            
            st.divider()
            st.dataframe(df_master, use_container_width=True, hide_index=True)

    # 2. PROFILE ANALYTICS
    elif view_mode == "👤 Profile Analytics":
        st.title("Profile Quality Audit")
        if not lista_ops: st.warning("Nenhum operador cadastrado.")
        else:
            op_escolhido = st.selectbox("Inspecionar Perfil do Analista:", [o["nome"] for o in lista_ops])
            meta_op = next(o for o in lista_ops if o["nome"] == op_escolhido)
            
            df_ind = get_data("Historico_Ciclos", ["Ciclo", "Operador", "Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR"])[lambda x: x["Operador"].astype(str).str.strip() == op_escolhido].copy()
            df_feed_ind = get_data("Feedbacks", ["Data_Hora", "Operador", "Ciclo", "Metricas", "Gaps", "PDI"])[lambda x: x["Operador"].astype(str).str.strip() == op_escolhido].copy()
            
            if not df_ind.empty:
                for c in ["Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR"]: df_ind[c] = pd.to_numeric(df_ind[c], errors="coerce")
            
            med_banco = df_ind["Nota_Banco"].mean() if not df_ind.empty else 0
            med_interna = df_ind["Nota_Interna"].mean() if not df_ind.empty else 0
            tempo_casa = calcular_tempo_atividade(meta_op.get("admissao", "19/05/2026"))
            
            badges = f"<span class='discord-badge discord-badge-blue'>Leal Staff</span>"
            if med_interna >= 90: badges += "<span class='discord-badge discord-badge-gold'>🏆 Master QA</span>"
            if med_banco >= 85: badges += "<span class='discord-badge discord-badge-purple'>⚡ MP Hero</span>"
            
            iniciais = "".join([p[0] for p in op_escolhido.split()[:2]]).upper()
            st.markdown(f"<div class='discord-profile'><div class='discord-banner'></div><div class='discord-avatar-area'><div class='discord-avatar'>{iniciais}<div class='discord-status-online'></div></div><div class='discord-badge-container'>{badges}</div></div><div class='discord-body'><h2 style='margin:0; font-size:24px; color:#ffffff;'>{meta_op['nome']}</h2><p style='margin:2px 0 10px 0; color:#b5bac1; font-size:14px;'>@operador_cx_leal</p><hr style='border-color:#2b2d31 !important;'><div style='display:grid; grid-template-columns: 1fr 1fr 1fr; gap:15px; margin-top:15px;'><div><span class='cx-label'>SQUAD ALOCADA</span><div style='color:#dbdee1; font-size:14px; font-weight:600;'>{meta_op['squad']}</div></div><div><span class='cx-label'>PARCEIRO</span><div style='color:#009ee3; font-size:14px; font-weight:600;'>Leal ➔ Mercado Pago</div></div><div><span class='cx-label'>TEMPO DE ATIVIDADE</span><div style='color:#23a55a; font-size:14px; font-weight:600;'>{tempo_casa}</div></div></div></div></div>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f"<div class='cx-metric-card'><span class='cx-label'>Média Mercado Pago</span><div class='cx-value'>{med_banco:.1f if med_banco > 0 else 'S/D'}</div></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='cx-metric-card'><span class='cx-label'>Média Auditoria Leal</span><div class='cx-value'>{med_interna:.1f if med_interna > 0 else 'S/D'}</div></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='cx-metric-card'><span class='cx-label'>Monitorias Coletadas</span><div class='cx-value'>{len(df_ind)} Ciclos</div></div>", unsafe_allow_html=True)
            
            if not df_ind.empty and "Compliance" in df_ind.columns:
                st.markdown("#### Matriz de Competências de CX")
                cc1, cc2, cc3 = st.columns(3)
                with cc1: st.slider("Script & Compliance Legal", 0, 100, int(df_ind["Compliance"].fillna(80).mean()), disabled=True)
                with cc2: st.slider("Soft Skills & Empatia", 0, 100, int(df_ind["Soft_Skills"].fillna(80).mean()), disabled=True)
                with cc3: st.slider("Resolutividade (FCR)", 0, 100, int(df_ind["FCR"].fillna(80).mean()), disabled=True)
                st.line_chart(df_ind.set_index("Ciclo")[["Nota_Banco", "Nota_Interna"]], color=["#009ee3", "#5865f2"])
            
            st.markdown("#### 📝 Prontuário Clínico de Monitoria")
            if not df_feed_ind.empty:
                txt = "".join([f"[{r['Data_Hora']}] {r['Ciclo']}\nMétricas: {r['Metricas']}\nGaps: {r['Gaps']}\nPDI: {r['PDI']}\n{'-'*60}\n\n" for _, r in df_feed_ind.iterrows()])
                st.text_area("Histórico Completo:", value=txt, height=200, disabled=True)
            else: st.text_area("Histórico Completo:", "Nenhum feedback registrado.", height=70, disabled=True)

    # 3. LOG NOTES
    elif view_mode == "📥 Log Notes":
        st.title("Central de Auditoria de Monitoria (QA)")
        if not lista_ops: st.warning("Cadastre profissionais antes de realizar auditorias.")
        else:
            with st.container(border=True):
                col1, col2 = st.columns(2)
                with col1:
                    op_alvo = st.selectbox("Escolha o Operador:", [o["nome"] for o in lista_ops])
                    ciclo_alvo = st.selectbox("Ciclo Avaliado:", ["Ciclo 1", "Ciclo 2", "Ciclo 3", "Ciclo 4"])
                    nota_mp = st.number_input("Nota Oficial Mercado Pago (0 a 100):", 0.0, 100.0, 85.0)
                    nota_leal = st.number_input("Nota Interna Leal (0 a 100):", 0.0, 100.0, 85.0)
                with col2:
                    st.markdown("<span class='cx-label'>Pilares Técnicos</span>", unsafe_allow_html=True)
                    v_comp = st.slider("Compliance e Regras:", 0, 100, 85)
                    v_soft = st.slider("Soft Skills e Cordialidade:", 0, 100, 85)
                    v_fcr = st.slider("Resolutividade (FCR):", 0, 100, 85)
                diag = st.text_area("Diagnóstico Técnico de Gaps:")
                pdi = st.text_area("Plano de Ação Corretivo (PDI):")
                
                if st.button("🚀 Gravar Auditoria e Sincronizar com Google Sheets"):
                    df_c = get_data("Historico_Ciclos", ["Ciclo", "Operador", "Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR"])
                    match = (df_c["Operador"].astype(str).str.strip() == op_alvo.strip()) & (df_c["Ciclo"].astype(str).str.strip() == ciclo_alvo.strip())
                    if match.any():
                        df_c.loc[df_c[match].index, ["Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR"]] = [nota_mp, nota_leal, v_comp, v_soft, v_fcr]
                    else:
                        df_c = pd.concat([df_c, pd.DataFrame([{"Ciclo": ciclo_alvo, "Operador": op_alvo.strip(), "Nota_Banco": nota_mp, "Nota_Interna": nota_leal, "Compliance": v_comp, "Soft_Skills": v_soft, "FCR": v_fcr}])], ignore_index=True)
                    save_data("Historico_Ciclos", df_c)
                    
                    df_f = get_data("Feedbacks", ["Data_Hora", "Operador", "Ciclo", "Metricas", "Gaps", "PDI"])
                    df_f = pd.concat([df_f, pd.DataFrame([{"Data_Hora": datetime.now().strftime('%d/%m/%Y %H:%M'), "Operador": op_alvo.strip(), "Ciclo": ciclo_alvo, "Metricas": f"MP: {nota_mp} | Leal: {nota_leal}", "Gaps": diag if diag else 'Nenhum', "PDI": pdi if pdi else 'Preventivo'}])], ignore_index=True)
                    save_data("Feedbacks", df_f)
                    st.success("Dados enviados com sucesso!")
                    st.rerun()

    # 4. AI STUDIO
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
            
            df_ind = get_data("Historico_Ciclos", ["Ciclo", "Operador", "Nota_Banco", "Nota_Interna", "Compliance", "Soft_Skills", "FCR"])[lambda x: x["Operador"].astype(str).str.strip() == op_ai.strip()]
            mb = pd.to_numeric(df_ind["Nota_Banco"], errors="coerce").mean() if not df_ind.empty else 0.0
            mi = pd.to_numeric(df_ind["Nota_Interna"], errors="coerce").mean() if not df_ind.empty else 0.0
            
            payload = templates[mod_sel].replace("{{OPERADOR}}", op_ai).replace("{{NOTA_BANCO}}", f"{mb:.1f}").replace("{{NOTA_INTERNA}}", f"{mi:.1f}").replace("{{NOTAS_LIDER}}", obs_lider if obs_lider else "Sem notas.")
            st.text_area("Payload Pronto:", value=payload, height=200)

    # 5. ADD OPERATOR
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

    # 6. CONTROL MANAGEMENT
    elif view_mode == "⚙️ Control Management":
        st.title("Control Management")
        if not lista_ops: st.warning("Sem analistas.")
        else:
            op_gerenciar = st.selectbox("Escolha a Conta:", [o["nome"] for o in lista_ops])
            meta_g = next(o for o in lista_ops if o["nome"] == op_gerenciar)
            t_edit, t_danger = st.tabs(["📝 Editar", "🚨 Excluir"])
            with t_edit:
                nn = st.text_input("Corrigir Nome:", value=meta_g["nome"])
                try: da = datetime.strptime(meta_g["admissao"], "%d/%m/%Y").date()
                except: da = datetime.now().date()
                if st.button("Commit Alterações") and nn.strip():
                    atualizar_perfil_operador(op_gerenciar, nn.strip(), st.date_input("Corrigir Admissão:", value=da))
                    st.success("Atualizado!"); st.rerun()
            with t_danger:
                if st.checkbox("Confirmar exclusão irreversível") and st.button("Deletar do Sheets"):
                    deletar_operador(op_gerenciar); st.success("Expurgado!"); st.rerun()

if __name__ == "__main__":
    main()
