import streamlit as st
import pandas as pd
from bot_alertas import verificar_alertas

st.set_page_config(page_title="Bot de Alertas - WhatsApp", layout="wide")
st.title("📢 Bot de Alertas via WhatsApp")

st.markdown("### 1. Upload dos Arquivos")

uploaded_toa = st.file_uploader("🔄 Carregar Extração TOA", type=["xlsx"])
uploaded_tecnicos = st.file_uploader("📂 Atualizar Base de Técnicos", type=["xlsx"])

df_toa, df_tecnicos = None, None
if uploaded_toa:
    df_toa = pd.read_excel(uploaded_toa)
if uploaded_tecnicos:
    df_tecnicos = pd.read_excel(uploaded_tecnicos)

if df_toa is not None and df_tecnicos is not None:
    st.success("✅ Arquivos carregados com sucesso!")

    col1, col2, col3 = st.columns(3)
    if col1.button("🚨 Alerta de IQI"):
        resultado = verificar_alertas(df_toa.copy(), df_tecnicos.copy(), "IQI")
        st.success(f"Mensagens de IQI enviadas: {resultado}")
    if col2.button("🪜 Alerta de NR35"):
        resultado = verificar_alertas(df_toa.copy(), df_tecnicos.copy(), "NR35")
        st.success(f"Mensagens de NR35 enviadas: {resultado}")
    if col3.button("🔁 Alerta de LOG"):
        resultado = verificar_alertas(df_toa.copy(), df_tecnicos.copy(), "LOG")
        st.success(f"Mensagens de LOG enviadas: {resultado}")
else:
    st.warning("⚠️ Aguarde o carregamento das planilhas para ativar os alertas.")