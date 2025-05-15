import streamlit as st
import pandas as pd
from datetime import datetime
from bot_alertas import processar_alertas

st.set_page_config(page_title="Bot de Alertas - WhatsApp", layout="wide")

st.markdown("""
    <style>
        .main {background-color: #f7f9fa;}
        .title {font-size:40px; font-weight:700; color:#1a73e8;}
        .alert-box {background-color:#ffffff;border-radius:10px;padding:20px;box-shadow:0 2px 5px rgba(0,0,0,0.1);}
        .metric {font-size:30px;font-weight:600;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>📢 Bot de Alertas - WhatsApp</div>", unsafe_allow_html=True)
st.markdown("**Gerencie e dispare alertas automatizados para a operação via WhatsApp.**")

# Upload de arquivos
uploaded_toa = st.file_uploader("📎 Carregar extração TOA (.xlsx obrigatório)", type="xlsx")
uploaded_tecnicos = st.file_uploader("📎 Atualizar base de técnicos (opcional)", type=["xlsx", "csv"])

# Leitura de arquivos
df_toa, df_tecnicos = None, None
if uploaded_toa:
    df_toa = pd.read_excel(uploaded_toa, engine="openpyxl")

if uploaded_tecnicos:
    if uploaded_tecnicos.name.endswith(".csv"):
        df_tecnicos = pd.read_csv(uploaded_tecnicos, delimiter=";", encoding="utf-8", on_bad_lines="skip")
    else:
        df_tecnicos = pd.read_excel(uploaded_tecnicos, engine="openpyxl")

if df_toa is not None:
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🚨 Alerta de IQI"):
            enviados, falhas, total, df_resumo = processar_alertas(df_toa.copy(), df_tecnicos, "IQI")
            st.success(f"✅ Mensagens IQI: {enviados} enviadas / {falhas} falhas (Total: {total})")

    with col2:
        if st.button("🪜 Alerta de NR35"):
            enviados, falhas, total, df_resumo = processar_alertas(df_toa.copy(), df_tecnicos, "NR35")
            st.success(f"✅ Mensagens NR35: {enviados} enviadas / {falhas} falhas (Total: {total})")

    with col3:
        if st.button("🔁 Alerta de LOG"):
            enviados, falhas, total, df_resumo = processar_alertas(df_toa.copy(), df_tecnicos, "LOG")
            st.success(f"✅ Mensagens LOG: {enviados} enviadas / {falhas} falhas (Total: {total})")

    with col4:
        if st.button("📄 Alerta Certidão de Atendimento"):
            enviados, falhas, total, df_resumo = processar_alertas(df_toa.copy(), df_tecnicos, "CERTIDAO")
            st.success(f"✅ Mensagens Certidão: {enviados} enviadas / {falhas} falhas (Total: {total})")

    st.markdown("---")
    if 'df_resumo' in locals():
        st.markdown("### 📊 Quantidade de alertas enviados por Área / Suporte / Gestão")
        st.dataframe(df_resumo, use_container_width=True)

    if st.button("🚀 Enviar TODOS os alertas"):
        total_alertas = 0
        for tipo in ["IQI", "NR35", "LOG", "CERTIDAO"]:
            enviados, falhas, total, _ = processar_alertas(df_toa.copy(), df_tecnicos, tipo)
            total_alertas += enviados
        st.success(f"Todos os alertas foram processados. Total enviados: {total_alertas}")

else:
    st.warning("⚠️ Por favor, carregue uma extração TOA para iniciar.")
