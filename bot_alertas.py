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

GRUPO_ID = "120363401162031107-group"

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

def enviar_mensagem_grupo(mensagem):
    try:
        payload = {"phone": GRUPO_ID, "message": mensagem}
        response = requests.post(f"{BASE_URL}/send-text", json=payload, headers=HEADERS)
        return response.status_code == 200
    except:
        return False
