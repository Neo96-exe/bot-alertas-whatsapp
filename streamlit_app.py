
import streamlit as st
import pandas as pd
from bot_alertas import processar_alertas

st.set_page_config(page_title="Bot de Alertas - WhatsApp", layout="wide")
st.title("📢 Painel de Alertas - Integração WhatsApp via Z-API")
st.markdown("Envio automatizado de alertas para IQI, NR35 e LOG.")

uploaded_toa = st.file_uploader("📥 Carregar Extração TOA (.xlsx)", type=["xlsx"])
uploaded_tecnicos = st.file_uploader("👥 Atualizar Base de Técnicos (.xlsx)", type=["xlsx"])

if uploaded_toa:
    try:
        df_toa = pd.read_excel(uploaded_toa, engine="openpyxl")
        st.success("Extração TOA carregada com sucesso!")
    except Exception as e:
        st.error(f"Erro ao carregar TOA: {e}")
        df_toa = None
else:
    df_toa = None

if uploaded_tecnicos:
    try:
        df_tecnicos = pd.read_excel(uploaded_tecnicos, engine="openpyxl")
        st.success("Base de técnicos carregada com sucesso!")
    except Exception as e:
        st.error(f"Erro ao carregar base de técnicos: {e}")
        df_tecnicos = None
else:
    df_tecnicos = None

if df_toa is not None and df_tecnicos is not None:
    st.divider()
    st.subheader("🚨 Funções de Alerta")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚧 Alerta IQI"):
            enviados, falhas, total = processar_alertas(df_toa.copy(), df_tecnicos, "IQI")
            st.success(f"IQI ✅ Enviadas: {enviados} | ❌ Falhas: {falhas} | 📊 Total: {total}")
    
    with col2:
        if st.button("🪜 Alerta NR35"):
            enviados, falhas, total = processar_alertas(df_toa.copy(), df_tecnicos, "NR35")
            st.success(f"NR35 ✅ Enviadas: {enviados} | ❌ Falhas: {falhas} | 📊 Total: {total}")

    with col3:
        if st.button("🔁 Alerta LOG"):
            enviados, falhas, total = processar_alertas(df_toa.copy(), df_tecnicos, "LOG")
            st.success(f"LOG ✅ Enviadas: {enviados} | ❌ Falhas: {falhas} | 📊 Total: {total}")
else:
    st.info("Por favor, carregue os dois arquivos necessários para iniciar (TOA e Base Técnicos).")
