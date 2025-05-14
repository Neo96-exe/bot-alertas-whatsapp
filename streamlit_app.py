import streamlit as st
import pandas as pd
from bot_alertas import processar_alertas

st.set_page_config(page_title="Bot de Alertas - WhatsApp", layout="wide")
st.title("📢 Bot de Alertas - WhatsApp (IQI • NR35 • LOG)")

st.markdown("### 1. Upload de arquivos")
uploaded_toa = st.file_uploader("📂 Enviar extração do TOA (.xlsx)", type="xlsx")
uploaded_base = st.file_uploader("📂 Enviar base de técnicos (.xlsx)", type="xlsx")

df_toa, df_tecnicos = None, None

if uploaded_toa:
    df_toa = pd.read_excel(uploaded_toa)
    st.success("Extração TOA carregada!")

if uploaded_base:
    df_tecnicos = pd.read_excel(uploaded_base)
    df_tecnicos.columns = [col.strip().upper().replace(" ", "_") for col in df_tecnicos.columns]
    st.success("Base de técnicos carregada!")

if df_toa is not None and df_tecnicos is not None:
    st.markdown("### 2. Disparar alertas")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🚨 Alerta IQI"):
            enviados, falhas, total = processar_alertas(df_toa.copy(), df_tecnicos, "IQI")
            st.success(f"IQI: {enviados} enviados com sucesso | {falhas} falharam | Total: {total}")

    with col2:
        if st.button("🪜 Alerta NR35"):
            enviados, falhas, total = processar_alertas(df_toa.copy(), df_tecnicos, "NR35")
            st.success(f"NR35: {enviados} enviados com sucesso | {falhas} falharam | Total: {total}")

    with col3:
        if st.button("🔁 Alerta LOG"):
            enviados, falhas, total = processar_alertas(df_toa.copy(), df_tecnicos, "LOG")
            st.success(f"LOG: {enviados} enviados com sucesso | {falhas} falharam | Total: {total}")
