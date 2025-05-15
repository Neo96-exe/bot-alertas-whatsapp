import pandas as pd
from datetime import datetime
import requests

# Configuração Z-API
ZAPI_URL = "https://api.z-api.io/instances/3E11C001D24090423EED3EF0F02679BC/token/ACB36F2DA2CAE524DC7ECA59/send-text"
CLIENT_TOKEN = "F60283feb8a754753aad942f9fcc2c8f0S"
HEADERS = {"Client-Token": CLIENT_TOKEN}
NUM_TESTE = "5521959309325"

# Controle de alertas enviados por dia
alertas_enviados = set()

def enviar_mensagem(numero, mensagem):
    payload = {"phone": numero, "message": mensagem}
    response = requests.post(ZAPI_URL, json=payload, headers=HEADERS)
    return response.status_code == 200

def obter_tecnico(login, df_tecnicos):
    return df_tecnicos[df_tecnicos["LOGIN"] == login.upper()].iloc[0]

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

⚠️ Contratos pontuados pelo IQI geram medida disciplinar caso não estejam dentro da regra de execução. Qualquer pendência, sinalizar ao fiscal e suporte imediatamente."""

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

⚠️ Atenção ao acionamento do botão escada no app Nota 10 e o mais importante: atenção à sua segurança."""

    elif tipo == "LOG":
        extra = f" @{tecnico['TELEFONE_GESTOR']}" if log_count >= 2 else ""
        return f"""🔁 *Contrato com LOG para Validação*

Contrato com histórico de retorno identificado. Revisar a execução e garantir que esteja dentro dos padrões.

📌 Técnico: {tecnico['NOME']}
Contrato: {contrato}
Área: {area}
Endereço: {endereco}
Início: {inicio}
Janela: {janela}
Contador de LOG: {log_count}
{marcacoes}{extra}

⚠️ Contratos com retorno devem ser validados criteriosamente para evitar reincidência."""

    elif tipo == "CERTIDAO":
        return f"""📝 *Certidão de Atendimento Obrigatória*

Contrato iniciado. Realizar a certidão conforme padrão Claro para evitar retorno técnico.

📌 Técnico: {tecnico['NOME']}
Contrato: {contrato}
Área: {area}
Endereço: {endereco}
Início: {inicio}
Janela: {janela}
@{tecnico['TELEFONE_TECNICO']} @{tecnico['TELEFONE_FISCAL']}

⚠️ Atenção: certidões devem ser preenchidas para todos os contratos iniciados, conforme orientações de qualidade."""

def processar_alertas(df_toa, df_tecnicos, tipo_alerta):
    enviados, falhas, total = 0, 0, 0
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
        filtro = df_toa["Status da Atividade"].str.lower() == "iniciado"
    else:
        return 0, 0, 0, pd.DataFrame()

    df_filtrado = df_toa[filtro]

    for _, row in df_filtrado.iterrows():
        contrato = row["Contrato"]
        login = row["Login do Técnico"]
        chave = f"{tipo_alerta}_{contrato}_{login}_{hoje}"
        if chave in alertas_enviados:
            continue
        try:
            tecnico = obter_tecnico(login, df_tecnicos)
            mensagem = formatar_mensagem(
                tipo_alerta,
                tecnico,
                contrato,
                row["Área de Trabalho"],
                row["Endereço"],
                row["Início"],
                row["Janela de Serviço"],
                int(row.get("Contador de log", 0))
            )
            if enviar_mensagem(NUM_TESTE, mensagem):
                alertas_enviados.add(chave)
                enviados += 1
            else:
                falhas += 1
            total += 1
        except:
            falhas += 1

    # SEGURA df_resumo em qualquer caso:
    try:
        if df_filtrado.empty:
            df_resumo = pd.DataFrame(columns=["Área", "Suporte", "Gestor", "Qtd"])
        else:
            df_agrupado = df_filtrado.merge(df_tecnicos, left_on="Login do Técnico", right_on="LOGIN", how="left")
            df_resumo = (
                df_agrupado.groupby(["Área de Trabalho", "SUPORTE", "GESTOR"])
                .size()
                .reset_index(name="Qtd")
                .rename(columns={"Área de Trabalho": "Área", "SUPORTE": "Suporte", "GESTOR": "Gestor"})
            )
    except Exception:
        df_resumo = pd.DataFrame(columns=["Área", "Suporte", "Gestor", "Qtd"])

    return enviados, falhas, total, df_resumo