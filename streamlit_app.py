import streamlit as st
import pandas as pd
from datetime import datetime
from bot_alertas import processar_alertas, enviar_todos_os_alertas

st.set_page_config(page_title="Bot de Alertas - WhatsApp", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #f5f7fb;
        color: #333;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #3366cc;
        color: white;
        padding: 10px 16px;
        border: none;
        border-radius: 6px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #274b8e;
    }
    .counter-box {
        background-color: #fff;
        border-radius: 8px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📢 Painel de Alertas - WhatsApp")

# Upload dos arquivos
uploaded_toa = st.file_uploader("📄 Carregar Extração TOA", type=["xlsx", "xls"])
uploaded_tecnicos = st.file_uploader("👤 Atualizar Base de Técnicos", type=["xlsx", "xls"])

if uploaded_toa is not None and uploaded_tecnicos is not None:
    df_toa = pd.read_excel(uploaded_toa, engine='openpyxl')
    df_tecnicos = pd.read_excel(uploaded_tecnicos, engine='openpyxl')

    # Limpa linhas inválidas
    df_toa = df_toa[df_toa["Contrato"].notna()]
    df_toa = df_toa[df_toa["Status da Atividade"].str.lower() != "suspenso"]

    st.success("✅ Arquivos carregados com sucesso!")

    # Contadores do dia
    if "contadores" not in st.session_state:
        st.session_state.contadores = {
            "IQI": 0,
            "NR35": 0,
            "LOG": 0,
            "CERTIDAO": 0,
            "total": 0
        }

    # Ações
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🚨 Enviar Alerta IQI"):
            enviados, falhas, total = processar_alertas(df_toa.copy(), df_tecnicos.copy(), "IQI")
            st.session_state.contadores["IQI"] += enviados
            st.success(f"IQI: {enviados} enviados com sucesso. {falhas} falharam.")

    with col2:
        if st.button("🪜 Enviar Alerta NR35"):
            enviados, falhas, total = processar_alertas(df_toa.copy(), df_tecnicos.copy(), "NR35")
            st.session_state.contadores["NR35"] += enviados
            st.success(f"NR35: {enviados} enviados com sucesso. {falhas} falharam.")

    with col3:
        if st.button("🔁 Enviar Alerta LOG"):
            enviados, falhas, total = processar_alertas(df_toa.copy(), df_tecnicos.copy(), "LOG")
            st.session_state.contadores["LOG"] += enviados
            st.success(f"LOG: {enviados} enviados com sucesso. {falhas} falharam.")

    with col4:
        if st.button("📄 Enviar Alerta CERTIDÃO"):
            enviados, falhas, total = processar_alertas(df_toa.copy(), df_tecnicos.copy(), "CERTIDAO")
            st.session_state.contadores["CERTIDAO"] += enviados
            st.success(f"CERTIDÃO: {enviados} enviados com sucesso. {falhas} falharam.")

    st.markdown("---")

    if st.button("🚀 Enviar Todos os Alertas"):
        resultado = enviar_todos_os_alertas(df_toa.copy(), df_tecnicos.copy())
        for tipo, qtde in resultado.items():
            st.session_state.contadores[tipo] += qtde
        st.success("Todos os alertas foram processados com sucesso!")

    st.markdown("### 📊 Alertas enviados hoje:")
    col_iqi, col_nr, col_log, col_cert = st.columns(4)
    with col_iqi:
        st.markdown(f"<div class='counter-box'><h3>{st.session_state.contadores['IQI']}</h3><p>IQI Sinalizados</p></div>", unsafe_allow_html=True)
    with col_nr:
        st.markdown(f"<div class='counter-box'><h3>{st.session_state.contadores['NR35']}</h3><p>NR35 Sinalizados</p></div>", unsafe_allow_html=True)
    with col_log:
        st.markdown(f"<div class='counter-box'><h3>{st.session_state.contadores['LOG']}</h3><p>LOG Sinalizados</p></div>", unsafe_allow_html=True)
    with col_cert:
        st.markdown(f"<div class='counter-box'><h3>{st.session_state.contadores['CERTIDAO']}</h3><p>Certidões Sinalizadas</p></div>", unsafe_allow_html=True)

else:
    st.warning("⚠️ Para iniciar, envie a extração TOA e a base de técnicos.")
