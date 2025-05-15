import streamlit as st
import pandas as pd
from datetime import datetime
from bot_alertas import processar_alertas, enviar_mensagem, enviar_mensagem_grupo

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

# === Upload de Arquivos ===
uploaded_toa = st.file_uploader("📎 Carregar extração TOA (.xlsx obrigatório)", type="xlsx")
uploaded_tecnicos = st.file_uploader("📎 Atualizar base de técnicos (opcional)", type=["xlsx", "csv"])

df_toa, df_tecnicos = None, None
if uploaded_toa:
    df_toa = pd.read_excel(uploaded_toa, engine="openpyxl")

if uploaded_tecnicos:
    if uploaded_tecnicos.name.endswith(".csv"):
        df_tecnicos = pd.read_csv(uploaded_tecnicos, delimiter=";", encoding="utf-8", on_bad_lines="skip")
    else:
        df_tecnicos = pd.read_excel(uploaded_tecnicos, engine="openpyxl")

# === Execução dos Botões ===
if df_toa is not None:
    st.markdown("---")
    st.subheader("🚨 Disparar alertas por função")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📌 Alerta IQI"):
            enviados, falhas, total, df_resumo = processar_alertas(df_toa.copy(), df_tecnicos, "IQI")
            st.success(f"✅ IQI: {enviados} enviados / ❌ {falhas} falhas (Total: {total})")

    with col2:
        if st.button("🪜 Alerta NR35"):
            enviados, falhas, total, df_resumo = processar_alertas(df_toa.copy(), df_tecnicos, "NR35")
            st.success(f"✅ NR35: {enviados} enviados / ❌ {falhas} falhas (Total: {total})")

    with col3:
        if st.button("🔁 Alerta LOG"):
            enviados, falhas, total, df_resumo = processar_alertas(df_toa.copy(), df_tecnicos, "LOG")
            st.success(f"✅ LOG: {enviados} enviados / ❌ {falhas} falhas (Total: {total})")

    with col4:
        if st.button("📄 Alerta Certidão"):
            enviados, falhas, total, df_resumo = processar_alertas(df_toa.copy(), df_tecnicos, "CERTIDAO")
            st.success(f"✅ Certidão: {enviados} enviados / ❌ {falhas} falhas (Total: {total})")

    st.markdown("---")

    # === Painel de Resumo ===
    if 'df_resumo' in locals() and not df_resumo.empty:
        st.markdown("### 📊 Resumo de alertas enviados por Área / Suporte / Gestão")
        st.dataframe(df_resumo, use_container_width=True)

    # === Envio geral ===
    if st.button("🚀 Enviar TODOS os alertas"):
        total_enviados = 0
        for tipo in ["IQI", "NR35", "LOG", "CERTIDAO"]:
            enviados, _, _, _ = processar_alertas(df_toa.copy(), df_tecnicos, tipo)
            total_enviados += enviados
        st.success(f"✅ Todos os alertas processados. Total enviados: {total_enviados}")

    st.markdown("---")
    st.subheader("💬 Envio manual de mensagens")

    # Botão 1: Teste individual
    if st.button("🧪 Enviar mensagem de teste"):
        if enviar_mensagem("5521959309325", "🚀 Teste de envio via Bot de Alertas - WhatsApp"):
            st.success("✅ Mensagem de teste enviada com sucesso.")
        else:
            st.error("❌ Falha ao enviar a mensagem.")

    # Botão 1.1: Teste no grupo
    if st.button("🧪 Enviar mensagem de teste no grupo"):
        if enviar_mensagem_grupo("[TESTE] Mensagem enviada no grupo com sucesso via Z-API"):
            st.success("✅ Mensagem enviada no grupo com sucesso.")
        else:
            st.error("❌ Falha ao enviar mensagem no grupo.")

    # Botão 2: Envio em massa
    st.markdown("### 📢 Enviar mensagem para grupo de contatos")
    grupo = st.selectbox("Grupo destino", ["Técnicos", "Fiscais", "Suportes"])
    mensagem_massa = st.text_area("📨 Digite a mensagem para envio em massa")

    if st.button("📤 Enviar para grupo selecionado"):
        if df_tecnicos is None:
            st.warning("⚠️ É necessário carregar a base de técnicos.")
        else:
            col_map = {
                "Técnicos": "TELEFONE_TECNICO",
                "Fiscais": "TELEFONE_FISCAL",
                "Suportes": "TELEFONE_SUPORTE"
            }
            col = col_map[grupo]
            numeros = df_tecnicos[col].dropna().unique().astype(str)
            enviados, falhas = 0, 0
            for numero in numeros:
                if enviar_mensagem(numero, mensagem_massa):
                    enviados += 1
                else:
                    falhas += 1
            st.success(f"✅ Enviados: {enviados} | ❌ Falhas: {falhas}")

    # Botão 3: Mensagem personalizada
    st.markdown("### ✍️ Enviar mensagem personalizada")
    numero_manual = st.text_input("Número com DDD (ex: 5521999999999)")
    mensagem_manual = st.text_area("✏️ Mensagem personalizada")

    if st.button("📬 Enviar mensagem personalizada"):
        if enviar_mensagem(numero_manual, mensagem_manual):
            st.success("✅ Mensagem personalizada enviada com sucesso.")
        else:
            st.error("❌ Falha no envio da mensagem.")

else:
    st.warning("⚠️ Por favor, carregue uma extração TOA para iniciar.")
