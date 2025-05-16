import pandas as pd
from datetime import datetime
import requests
import gspread
import json
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

# ==================== CONFIGURAÇÕES ====================
ZAPI_ID = "3E11C001D24090423EED3EF0F02679BC"
ZAPI_TOKEN = "ACB36F2DA2CAE524DC7ECA59"
CLIENT_TOKEN = "F60283feb8a754753aad942f9fcc2c8f0S"

BASE_URL = f"https://api.z-api.io/instances/{ZAPI_ID}/token/{ZAPI_TOKEN}"
HEADERS = {
    "Content-Type": "application/json",
    "Client-Token": CLIENT_TOKEN
}

GRUPO_ID = "120363401162031107@g.us"

# ==================== GOOGLE SHEETS ====================
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_keyfile = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
CREDS = ServiceAccountCredentials.from_json_keyfile_dict(json_keyfile, SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET = CLIENT.open_by_url("https://docs.google.com/spreadsheets/d/1PsTOZU12b8ruzJcQTe6MiIYGRpqPnUaF7qryBEb9TEI").worksheet("alertas_enviados")

# ==================== FUNÇÕES GOOGLE SHEETS ====================
def carregar_alertas_enviados(sheet):
    registros = sheet.get_all_records()
    return set((r['data'], r['login'], r['contrato'], r['tipo_alerta']) for r in registros)

def registrar_alerta_enviado(sheet, data, login, contrato, tipo_alerta):
    nova_linha = [data, login, contrato, tipo_alerta]
    sheet.append_row(nova_linha)

alertas_enviados = carregar_alertas_enviados(SHEET)

# ==================== Z-API ====================
def enviar_mensagem(numero, mensagem):
    try:
        payload = {"phone": numero, "message": mensagem}
        response = requests.post(f"{BASE_URL}/send-text", json=payload, headers=HEADERS)
        return response.status_code == 200
    except:
        return False

def enviar_mensagem_grupo(mensagem, telefones_mention=[]):
    try:
        payload = {
            "chatId": GRUPO_ID,
            "message": mensagem,
            "mentioned": [f"{t}@c.us" for t in telefones_mention]
        }
        response = requests.post(f"{BASE_URL}/send-text", json=payload, headers=HEADERS)
        return response.status_code == 200
    except:
        return False

# ==================== LÓGICA DE ALERTAS ====================
def obter_tecnico(login, df_tecnicos):
    return df_tecnicos[df_tecnicos["LOGIN"] == login.upper()].iloc[0]

def gerar_alertas_log(log_count):
    return "⚠️" * int(log_count)

def formatar_mensagem(tipo, tecnico, contrato, area, endereco, inicio, janela, log_count=0):
    hierarquia = f"""Gestor: {tecnico['GESTOR']}
Suporte: {tecnico['SUPORTE']}
Fiscal: {tecnico['FISCAL']}
Técnico: {tecnico['NOME']}"""

    mencao_telefones = [
        tecnico["TELEFONE_GESTOR"],
        tecnico["TELEFONE_SUPORTE"],
        tecnico["TELEFONE_FISCAL"],
        tecnico["TELEFONE_TECNICO"]
    ]
    marcacoes = " ".join([f"@{t}" for t in mencao_telefones])

    if tipo == "IQI":
        mensagem = f"""[Alerta contrato aderente ao IQI]

Atenção ao processo de autoinspeção e ao padrão de instalação. Seguir dentro das normas da Claro, o contrato será auditado dentro de 5 dias.

{hierarquia}

Contrato: {contrato}
Área: {area}
Endereço: {endereco}
Início: {inicio}
Janela: {janela}

{marcacoes}

Atenção, contratos pontuados pelo IQI geram medida disciplinar caso não estejam dentro da regra de execução. Qualquer pendência sinalizar ao fiscal e suporte imediato."""
    elif tipo == "LOG":
        alertas = gerar_alertas_log(log_count)
        mensagem = f"""{alertas} Alerta de Retorno com LOG

{hierarquia}

Contrato: {contrato}
Área: {area}
Endereço: {endereco}
Início: {inicio}
Janela: {janela}

{marcacoes}

Esse contrato já apresenta histórico de retorno. Reforce com o técnico a correta execução. Casos reincidentes impactam diretamente na operação."""
    elif tipo == "NR35":
        mensagem = f"""🪜 Contrato aderente ao processo NR35

{hierarquia}

Contrato: {contrato}
Área: {area}
Endereço: {endereco}
Início: {inicio}
Janela: {janela}

{marcacoes}

Contrato iniciado com uso de escada. Atenção redobrada aos procedimentos de segurança!"""
    elif tipo == "CERTIDAO":
        mensagem = f"""📄 Contrato requer Certidão de Atendimento

{hierarquia}

Contrato: {contrato}
Área: {area}
Endereço: {endereco}
Início: {inicio}
Janela: {janela}

{marcacoes}

Todos os contratos produtivos devem conter evidências da Certidão de Atendimento. Suba as fotos no grupo de evidências até o fim do dia."""
    return mensagem, mencao_telefones

def processar_alertas(df_toa, df_tecnicos, tipo_alerta):
    enviados, falhas, total = 0, 0, 0
    hoje = datetime.now().strftime("%Y-%m-%d")
    df_resumo = pd.DataFrame()

    if tipo_alerta == "IQI":
        filtro = (df_toa["Status da Atividade"].str.lower() == "iniciado") & \
                 (df_toa["Tipo O.S 1"].str.lower().str.contains("adesao")) & \
                 (df_toa[[col for col in df_toa.columns if "Cód de Baixa" in col]].isnull().all(axis=1))
    elif tipo_alerta == "NR35":
        filtro = (df_toa["Status da Atividade"].str.lower() == "iniciado") & \
                 (df_toa["Habilidade de Trabalho"].str.contains("Escada", case=False, na=False))
    elif tipo_alerta == "LOG":
        filtro = (df_toa["Status da Atividade"].str.lower() == "iniciado") & \
                 (df_toa["Tipo O.S 1"].str.contains("69", na=False)) & \
                 (df_toa["Contador de log"].fillna(0).astype(int) > 0)
    elif tipo_alerta == "CERTIDAO":
        filtro = df_toa["Status da Atividade"].str.lower() == "iniciado"
    else:
        return enviados, falhas, total, df_resumo

    df_filtrado = df_toa[filtro]

    for _, row in df_filtrado.iterrows():
        contrato = row["Contrato"]
        login = row["Login do Técnico"]
        chave = (hoje, login, contrato, tipo_alerta)

        if chave in alertas_enviados:
            continue

        try:
            tecnico = obter_tecnico(login, df_tecnicos)
            mensagem, telefones_mencao = formatar_mensagem(
                tipo_alerta, tecnico, contrato, row["Área de Trabalho"],
                row["Endereço"], row["Início"], row["Janela de Serviço"],
                int(row.get("Contador de log", 0))
            )

            if tipo_alerta in ["NR35", "CERTIDAO"]:
                enviado = enviar_mensagem(tecnico["TELEFONE_TECNICO"], mensagem)
            elif tipo_alerta in ["IQI", "LOG"]:
                enviado = all([
                    enviar_mensagem(tecnico["TELEFONE_TECNICO"], mensagem),
                    enviar_mensagem(tecnico["TELEFONE_SUPORTE"], mensagem),
                    enviar_mensagem(tecnico["TELEFONE_FISCAL"], mensagem)
                ])
                if tipo_alerta == "LOG" and int(row.get("Contador de log", 0)) >= 2:
                    enviado = enviado and enviar_mensagem(tecnico["TELEFONE_GESTOR"], mensagem)
            else:
                enviado = False

            if enviado:
                registrar_alerta_enviado(SHEET, hoje, login, contrato, tipo_alerta)
                alertas_enviados.add(chave)
                enviados += 1
            else:
                falhas += 1
            total += 1

        except Exception:
            falhas += 1

    try:
        if not df_filtrado.empty:
            df_agrupado = df_filtrado.merge(df_tecnicos, left_on="Login do Técnico", right_on="LOGIN", how="left")
            df_resumo = df_agrupado.groupby(["Área de Trabalho", "SUPORTE", "GESTOR"]) \
                .size().reset_index(name="Qtd") \
                .rename(columns={"Área de Trabalho": "Área", "SUPORTE": "Suporte", "GESTOR": "Gestor"})
        else:
            df_resumo = pd.DataFrame(columns=["Área", "Suporte", "Gestor", "Qtd"])
    except:
        df_resumo = pd.DataFrame(columns=["Área", "Suporte", "Gestor", "Qtd"])

    return enviados, falhas, total, df_resumo
