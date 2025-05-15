import streamlit as st
import pandas as pd
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Bot de Alertas - Teste Google Sheets", layout="wide")

st.title("📄 Validação do Google Sheets via Secrets")

# Upload da planilha TOA
uploaded_toa = st.file_uploader("📎 Carregar extração TOA (.xlsx)", type="xlsx")

if uploaded_toa:
    try:
        df_toa = pd.read_excel(uploaded_toa, engine="openpyxl")
        st.success("✅ Planilha carregada com sucesso!")
        st.dataframe(df_toa.head(), use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao ler a planilha: {e}")

st.markdown("---")
st.subheader("🔐 Teste de acesso ao Google Sheets")

# Autenticando e lendo planilha Google
try:
    SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    json_keyfile = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
    CREDS = ServiceAccountCredentials.from_json_keyfile_dict(json_keyfile, SCOPE)
    CLIENT = gspread.authorize(CREDS)

    SHEET = CLIENT.open_by_url("https://docs.google.com/spreadsheets/d/1PsTOZU12b8ruzJcQTe6MiIYGRpqPnUaF7qryBEb9TEI").worksheet("alertas_enviados")
    dados = SHEET.get_all_records()
    df_sheet = pd.DataFrame(dados)

    st.success("✅ Planilha 'alertas_enviados' carregada com sucesso!")
    st.dataframe(df_sheet.head(), use_container_width=True)

except Exception as e:
    st.error(f"❌ Erro ao acessar Google Sheets: {e}")