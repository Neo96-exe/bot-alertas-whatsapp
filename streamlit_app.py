import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Bot de Alertas - Teste Parcial", layout="wide")

st.title("🚦 Validação Parcial do Bot de Alertas")

st.markdown("Carregando o layout, upload da planilha e teste do segredo do Google...")

# Upload da planilha TOA
uploaded_toa = st.file_uploader("📎 Carregar extração TOA (.xlsx)", type="xlsx")

if uploaded_toa:
    try:
        df_toa = pd.read_excel(uploaded_toa, engine="openpyxl")
        st.success("✅ Planilha carregada com sucesso!")
        st.dataframe(df_toa.head(), use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao ler a planilha: {e}")

# Testar leitura do secrets
st.markdown("---")
st.subheader("🔐 Teste de acesso ao Google Service Account")

try:
    cred_inicio = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])  # apenas testa leitura
    st.success("✅ Secrets carregado corretamente.")
    st.code(cred_inicio["client_email"])
except Exception as e:
    st.error(f"❌ Falha ao acessar secrets: {e}")
