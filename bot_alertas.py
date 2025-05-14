import pandas as pd
import requests
from datetime import datetime

ZAPI_ID = "3E11C001D24090423EED3EF0F02679BC"
ZAPI_TOKEN = "ACB36F2DA2CAE524DC7ECA59"
CLIENT_TOKEN = "F60283feb8a754753aad942f9fcc2c8f0S"
ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_ID}/token/{ZAPI_TOKEN}/send-text"

ENVIADO_HOJE = set()

def normalizar_coluna(nome):
    return nome.strip().lower().replace(" ", "_")

def localizar_coluna(df, nome_coluna_alvo):
    for col in df.columns:
        if nome_coluna_alvo.lower() in col.lower():
            return col
    return None

def carregar_colunas_essenciais(df):
    return {
        "login": localizar_coluna(df, "Login do Técnico"),
        "status": localizar_coluna(df, "Status da Atividade"),
        "tipo_os": localizar_coluna(df, "Tipo O.S 1"),
        "codigo_baixa": [col for col in df.columns if "Cód de Baixa" in col],
        "contrato": localizar_coluna(df, "Contrato"),
        "inicio": localizar_coluna(df, "Início"),
        "janela": localizar_coluna(df, "Janela de Serviço"),
        "area": localizar_coluna(df, "Área de Trabalho"),
        "endereco": localizar_coluna(df, "Endereço"),
        "escada": localizar_coluna(df, "Habilidade de Trabalho"),
        "log": localizar_coluna(df, "Contador de log")
    }

def enviar_mensagem(numero, mensagem):
    payload = {"phone": numero, "message": mensagem}
    headers = {"Client-Token": CLIENT_TOKEN}
    response = requests.post(ZAPI_URL, json=payload, headers=headers)
    return response.status_code == 200

def montar_mensagem(tipo, tecnico, contrato, area, endereco, inicio, janela, telefones, log_count=None):
    marcacoes = " ".join([f"@{t}" for t in telefones if t])
    if tipo == "IQI":
        return f'''
[ALERTA DE IQI]

Atenção ao processo de autoinspeção e ao padrão de instalação. Seguir dentro das normas da Claro, o contrato será auditado dentro de 5 dias.

Técnico: {tecnico}
Contrato: {contrato}
Área: {area}
Endereço: {endereco}
Início: {inicio}
Janela: {janela}
{marcacoes}

Atenção, contratos pontuados pelo IQI geram medida disciplinar caso não estejam dentro da regra de execução, qualquer pendência sinalizar ao fiscal e suporte imediato.
'''.strip()
    elif tipo == "NR35":
        return f'''
[ALERTA DE NR35 - USO DE ESCADA]

Contrato aderente ao processo de NR35. Atente-se às normas de segurança e sinalize qualquer anomalia!

Técnico: {tecnico}
Contrato: {contrato}
Área: {area}
Endereço: {endereco}
Início: {inicio}
Janela: {janela}
{marcacoes}
'''.strip()
    elif tipo == "LOG":
        return f'''
[ALERTA DE LOG DE RETORNO]

Contrato de retorno com apontamento de LOG. Necessário revisão imediata da execução.

Técnico: {tecnico}
Contrato: {contrato}
Área: {area}
Endereço: {endereco}
Início: {inicio}
Janela: {janela}
Contador de LOG: {log_count}
{marcacoes}
'''.strip()
    return ""

def verificar_alertas(df, df_tecnicos, tipo_alerta):
    col = carregar_colunas_essenciais(df)
    enviados = 0
    for _, row in df.iterrows():
        try:
            login = row[col["login"]]
            contrato = row[col["contrato"]]
            status = row[col["status"]]
            tipo_os = row[col["tipo_os"]]
            codigos = [str(row[c]) for c in col["codigo_baixa"] if pd.notna(row[c])]
            habilidade = row[col["escada"]]
            log_count = int(row[col["log"]]) if col["log"] else 0

            id_unico = f"{login}_{contrato}_{tipo_alerta}"
            if id_unico in ENVIADO_HOJE:
                continue

            info = df_tecnicos[df_tecnicos["LOGIN"] == login].iloc[0]
            tecnicos = [
                str(info["TELEFONE_TECNICO"]),
                str(info["TELEFONE_SUPORTE"]),
                str(info["TELEFONE_FISCAL"])
            ]
            if tipo_alerta == "LOG" and log_count >= 2:
                tecnicos.append(str(info["TELEFONE_GESTOR"]))

            msg = None
            if tipo_alerta == "IQI":
                if status.lower() == "iniciado" and tipo_os.lower() == "adesao" and not codigos:
                    msg = montar_mensagem("IQI", info["NOME"], contrato, row[col["area"]], row[col["endereco"]], row[col["inicio"]], row[col["janela"]], tecnicos)
            elif tipo_alerta == "NR35":
                if status.lower() == "iniciado" and "escada" in str(habilidade).lower():
                    msg = montar_mensagem("NR35", info["NOME"], contrato, row[col["area"]], row[col["endereco"]], row[col["inicio"]], row[col["janela"]], tecnicos)
            elif tipo_alerta == "LOG":
                if tipo_os == "69 - RETORNO DE CREDENCIADA" and log_count > 0:
                    msg = montar_mensagem("LOG", info["NOME"], contrato, row[col["area"]], row[col["endereco"]], row[col["inicio"]], row[col["janela"]], tecnicos, log_count)

            if msg:
                for numero in tecnicos:
                    if numero and numero.isdigit():
                        sucesso = enviar_mensagem(numero, msg)
                        if sucesso:
                            ENVIADO_HOJE.add(id_unico)
                            enviados += 1
        except Exception:
            continue
    return enviados