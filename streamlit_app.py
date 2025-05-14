import streamlit as st
import pandas as pd
from bot_alertas import verificar_iqi, verificar_escada, verificar_log

st.set_page_config(page_title="Bot de Alertas - WhatsApp", layout="wide")
st.title("🤖 Bot de Alertas - Integração com WhatsApp")

st.markdown("---")
st.subheader("📁 Upload das Bases")

uploaded_toa = st.file_uploader("Carregar extração TOA (.xlsx)", type=["xlsx"], key="toa")
uploaded_tecnicos = st.file_uploader("Atualizar base de técnicos (.xlsx)", type=["xlsx"], key="tecnicos")

df_toa, df_tecnicos = None, None

# Leitura segura da base TOA
if uploaded_toa:
    try:
        df_toa = pd.read_excel(uploaded_toa, engine="openpyxl")
        st.success("📄 Extração TOA carregada com sucesso.")
    except Exception as e:
        st.error(f"Erro ao carregar extração TOA: {e}")

# Leitura segura da base de técnicos
if uploaded_tecnicos:
    try:
        df_tecnicos = pd.read_excel(uploaded_tecnicos, engine="openpyxl")
        st.success("📄 Base de técnicos carregada com sucesso.")
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar base de técnicos: {e}")
else:
    st.warning("⚠️ Base de técnicos não carregada. Algumas funções exigem essa base.")

st.markdown("---")
st.subheader("🚀 Executar Alertas")

# Botão IQI
if st.button("📌 Alerta de IQI"):
    if df_toa is not None and df_tecnicos is not None:
        resultado = verificar_iqi(df_toa.copy(), df_tecnicos)
        st.success(resultado)
    else:
        st.error("❌ Carregue a extração TOA e a base de técnicos.")

# Botão NR35 (escada)
if st.button("🪜 Alerta de NR35"):
    if df_toa is not None and df_tecnicos is not None:
        resultado = verificar_escada(df_toa.copy(), df_tecnicos)
        st.success(resultado)
    else:
        st.error("❌ Carregue a extração TOA e a base de técnicos.")

# Botão LOG
if st.button("🔁 Alerta de LOG"):
    if df_toa is not None and df_tecnicos is not None:
        resultado = verificar_log(df_toa.copy(), df_tecnicos)
        st.success(resultado)
    else:
        st.error("❌ Carregue a extração TOA e a base de técnicos.")

st.markdown("---")
st.caption("📍 Desenvolvido por Wesley + ChatGPT | Versão de Produção")
