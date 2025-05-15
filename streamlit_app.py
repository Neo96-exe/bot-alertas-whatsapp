import streamlit as st
import pandas as pd
from datetime import datetime
from bot_alertas import processar_alertas

st.set_page_config(page_title="Bot de Alertas - WhatsApp", layout="wide")

st.title("📡 Bot de Alertas - WhatsApp")
st.markdown("Este painel envia alertas de IQI, NR35, LOG e Certidão de Atendimento para os técnicos via WhatsApp.")

# Upload dos arquivos
uploaded_toa = st.file_uploader("📎 Carregar Extração TOA (obrigatório)", type=["xlsx"])
uploaded_tecnicos = st.file_uploader("📎 Atualizar Base de Técnicos (opcional)", type=["xlsx"])

# Botões de ação
col1, col2, col3 = st.columns(3)
with col1:
    acionar_iqi = st.button("🚨 Alerta de IQI")
with col2:
    acionar_nr35 = st.button("🪜 Alerta de NR35")
with col3:
    acionar_log = st.button("🔁 Alerta de LOG")

col4, col5 = st.columns(2)
with col4:
    acionar_certidao = st.button("📄 Alerta de Certidão")
with col5:
    acionar_todos = st.button("📢 Enviar Todos os Alertas")

# Contadores globais
st.markdown("---")
st.subheader("📊 Relatório de Envios do Dia")

contador_geral = {}

if uploaded_toa:
    df_toa = pd.read_excel(uploaded_toa, engine="openpyxl")

    # Limpeza da planilha TOA
    df_toa = df_toa[df_toa["Contrato"].notna()]
    df_toa = df_toa[~df_toa["Status da Atividade"].str.lower().eq("suspenso")]

    df_tecnicos = None
    if uploaded_tecnicos:
        df_tecnicos = pd.read_excel(uploaded_tecnicos, engine="openpyxl")

    # Função auxiliar para exibir resultados
    def mostrar_resultados(tipo, enviados, falhas, total, detalhes_area):
        st.success(f"✅ {tipo}: {enviados} enviados com sucesso / {falhas} falharam / {total} no total")
        for _, linha in detalhes_area.iterrows():
            st.markdown(
                f"- **Área:** {linha['Área']} | **Suporte:** {linha['Suporte']} | "
                f"**Gestor:** {linha['Gestor']} | **Qtd:** {linha['Qtd']}"
            )
        contador_geral[tipo] = enviados

    if acionar_iqi:
        enviados, falhas, total, df_resumo = processar_alertas(df_toa.copy(), df_tecnicos, "IQI")
        mostrar_resultados("IQI", enviados, falhas, total, df_resumo)

    if acionar_nr35:
        enviados, falhas, total, df_resumo = processar_alertas(df_toa.copy(), df_tecnicos, "NR35")
        mostrar_resultados("NR35", enviados, falhas, total, df_resumo)

    if acionar_log:
        enviados, falhas, total, df_resumo = processar_alertas(df_toa.copy(), df_tecnicos, "LOG")
        mostrar_resultados("LOG", enviados, falhas, total, df_resumo)

    if acionar_certidao:
        enviados, falhas, total, df_resumo = processar_alertas(df_toa.copy(), df_tecnicos, "CERTIDAO")
        mostrar_resultados("Certidão", enviados, falhas, total, df_resumo)

    if acionar_todos:
        for tipo_alerta in ["IQI", "NR35", "LOG", "CERTIDAO"]:
            enviados, falhas, total, df_resumo = processar_alertas(df_toa.copy(), df_tecnicos, tipo_alerta)
            mostrar_resultados(tipo_alerta, enviados, falhas, total, df_resumo)

    # Tabela final com contagem por tipo
    if contador_geral:
        st.markdown("---")
        st.subheader("📌 Total de Alertas por Tipo")
        st.dataframe(pd.DataFrame.from_dict(contador_geral, orient='index', columns=['Enviados']))

else:
    st.warning("⚠️ Por favor, carregue a extração TOA para continuar.")
