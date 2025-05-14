import pandas as pd
import requests
from datetime import datetime

# Configurações da API Z-API
ZAPI_ID = "3E11C001D24090423EED3EF0F02679BC"
ZAPI_TOKEN = "ACB36F2DA2CAE524DC7ECA59"
ZAPI_CLIENT_TOKEN = "F60283feb8a754753aad942f9fcc2c8f0S"
ZAPI_URL = f"https://api.z-api.io/instances/{ZAPI_ID}/token/{ZAPI_TOKEN}/send-text"
GRUPO_ID = "120363401162031107@g.us"
NUM_TESTE = "5521959309325"

# Controle de alertas únicos
alertas_enviados = set()

def enviar_mensagem(numero, mensagem):
    headers = {"Client-Token": ZAPI_CLIENT_TOKEN}
    payload = {"phone": numero, "message": mensagem}
    response = requests.post(ZAPI_URL, json=payload, headers=headers)
    return response.status_code == 200

def enviar_mensagem_grupo(mensagem):
    headers = {"Client-Token": ZAPI_CLIENT_TOKEN}
    payload = {"chatId": GRUPO_ID, "message": mensagem}
    response = requests.post(ZAPI_URL, json=payload, headers=headers)
    return response.status_code == 200

def formatar_mensagem(tipo, tecnico, contrato, area, endereco, inicio, janela, log_count=0):
    marcacoes = f"@{tecnico['TELEFONE_TECNICO']} @{tecnico['TELEFONE_SUPORTE']} @{tecnico['TELEFONE_FISCAL']}"
    if tipo == "IQI":
        return f"""🛠️ *Alerta de Autoinspeção (IQI)*

Atenção ao processo de autoinspeção e ao padrão de instalação. Seguir dentro das normas da Claro, o contrato será auditado dentro de 5 dias.

📌 Técnico: {tecnico['NOME']}
Contrato: {contrato}
Área: {area}
Endereço: {endereco}
Início: {inicio}
Janela: {janela}
{marcacoes}

⚠️ Contratos pontuados pelo IQI geram medida disciplinar caso não estejam dentro da regra de execução. Qualquer pendência, sinalizar ao fiscal e suporte imediatamente.
"""
    elif tipo == "NR35":
        return f"""🪜 *Contrato Aderente ao Processo NR35* 

Detectado uso de escada neste contrato. Certifique-se de seguir corretamente os protocolos de segurança NR35 definidos pela Claro.

📌 Técnico: {tecnico['NOME']}
Contrato: {contrato}
Área: {area}
Endereço: {endereco}
Início: {inicio}
Janela: {janela}
{marcacoes}

⚠️ Atenção ao acionamento do botão escada no app Nota 10 e o mais importante: atenção à sua segurança.
"""
    elif tipo == "LOG":
        extra = f"@{tecnico['TELEFONE_GESTOR']}" if log_count >= 2 else ""
        return f"""🔁 *Contrato com LOG para Validação*

Contrato com histórico de retorno identificado. Revisar a execução e garantir que esteja dentro dos padrões.

📌 Técnico: {tecnico['NOME']}
Contrato: {contrato}
Área: {area}
Endereço: {endereco}
Início: {inicio}
Janela: {janela}
Contador de LOG: {log_count}
{marcacoes} {extra}

⚠️ Contratos com retorno devem ser validados criteriosamente para evitar reincidência.
"""
    elif tipo == "CERTIDAO":
        return f"""📄 *Certidão de Atendimento Obrigatória*

Este contrato está com status iniciado e deve obrigatoriamente conter evidência via Certidão de Atendimento, conforme norma da Claro.

📌 Técnico: {tecnico['NOME']}
Contrato: {contrato}
Área: {area}
Endereço: {endereco}
Início: {inicio}
Janela: {janela}
@{tecnico['TELEFONE_FISCAL']}

⚠️ A certidão deve ser gerada ainda durante o atendimento. Em caso de dúvida, sinalizar ao fiscal.
"""

def obter_tecnico(login, df_tecnicos):
    return df_tecnicos[df_tecnicos["LOGIN"] == login.upper()].iloc[0]

def processar_alertas(df_toa, df_tecnicos, tipo_alerta):
    enviados = 0
    falhas = 0
    total = 0
    hoje = datetime.now().strftime("%Y-%m-%d")

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
        filtro = (df_toa["Status da Atividade"].str.lower() == "iniciado")

    else:
        return enviados, falhas, total  # tipo inválido

    df_filtrado = df_toa[filtro]

    agrupado = df_filtrado.groupby(df_filtrado["SUPORTE"] if "SUPORTE" in df_filtrado.columns else "Login do Técnico")

    for suporte, grupo in agrupado:
        for _, row in grupo.iterrows():
            contrato = row["Contrato"]
            login = row["Login do Técnico"]
            chave_alerta = f"{tipo_alerta}_{contrato}_{login}_{hoje}"
            if chave_alerta in alertas_enviados:
                continue
            try:
                tecnico = obter_tecnico(login, df_tecnicos)
                mensagem = formatar_mensagem(
                    tipo_alerta, tecnico, contrato,
                    row["Área de Trabalho"], row["Endereço"],
                    row["Início"], row["Janela de Serviço"],
                    int(row.get("Contador de log", 0))
                )
                # Envia para privado do técnico, suporte, fiscal
                for numero in [
                    tecnico["TELEFONE_TECNICO"],
                    tecnico["TELEFONE_SUPORTE"],
                    tecnico["TELEFONE_FISCAL"],
                ]:
                    enviar_mensagem(numero, mensagem)
                # Envia no grupo
                enviar_mensagem_grupo(mensagem)
                alertas_enviados.add(chave_alerta)
                enviados += 1
            except Exception as e:
                falhas += 1
            total += 1

    return enviados, falhas, total

def enviar_todos_os_alertas(df_toa, df_tecnicos):
    totais = {"IQI": 0, "NR35": 0, "LOG": 0, "CERTIDAO": 0}
    for tipo in totais.keys():
        enviados, _, _ = processar_alertas(df_toa, df_tecnicos, tipo)
        totais[tipo] = enviados
    return totais
