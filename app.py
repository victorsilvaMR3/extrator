
import fitz  # PyMuPDF
import re
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Analisador de Evoluções Médicas", layout="wide")
st.title("📄 Analisador de Evoluções Médicas a partir de PDF")


def extrair_texto_pdf(arquivo):
    doc = fitz.open(stream=arquivo.read(), filetype="pdf")
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()
    return texto


def parsear_evolucao(texto):
    dados = {}
    dados['nome'] = re.search(r'NOME DO PACIENTE: (.+)', texto).group(1).strip()
    dados['idade'] = re.search(r'IDADE: (\d+ anos)', texto).group(1)
    dados['data_internacao'] = re.search(r'DATA DA INTERNAÇÃO: (\d{2}/\d{2}/\d{4})', texto).group(1)

    diagnostico_match = re.search(r'DIAGNÓSTICOS: (.+?)\n', texto)
    dados['diagnosticos'] = diagnostico_match.group(1).strip() if diagnostico_match else ""

    hpp_match = re.search(r'# HPP:\n(.+?)\n\n', texto, re.DOTALL)
    dados['historia_pregressa'] = hpp_match.group(1).replace('-', '').strip() if hpp_match else ""

    exame_match = re.search(r'# EXAME FISICO:(.*?)# IMPRESSÃO:', texto, re.DOTALL)
    dados['exame_fisico'] = exame_match.group(1).strip() if exame_match else ""

    sinais_match = re.findall(r'Sinais vitais: (.+)', texto)
    dados['sinais_vitais'] = sinais_match[-1].strip() if sinais_match else ""

    impressao_match = re.search(r'# IMPRESSÃO:(.*?)CD:', texto, re.DOTALL)
    conduta_match = re.search(r'CD:(.*?)Sinais vitais:', texto, re.DOTALL)
    dados['impressao'] = impressao_match.group(1).strip() if impressao_match else ""
    dados['conduta'] = conduta_match.group(1).strip() if conduta_match else ""

    return dados


def gerar_evolucao(dados):
    texto = f"""
    ## Evolução Médica – {datetime.now().strftime('%d/%m/%Y')}

    **Paciente**: {dados['nome']}  
    **Idade**: {dados['idade']}  
    **Data da internação**: {dados['data_internacao']}  
    **Diagnóstico(s)**: {dados['diagnosticos']}  

    **Histórico Patológico Pregresso**:\n{dados['historia_pregressa']}  

    **Exame Físico**:\n{dados['exame_fisico']}  

    **Sinais Vitais**:\n{dados['sinais_vitais']}  

    **Impressão Clínica**:\n{dados['impressao']}  

    **Conduta**:\n{dados['conduta']}  
    """
    return texto.strip()


arquivo_pdf = st.file_uploader("📎 Faça o upload do PDF da evolução médica", type=["pdf"])

if arquivo_pdf:
    texto_extraido = extrair_texto_pdf(arquivo_pdf)
    dados = parsear_evolucao(texto_extraido)
    evolucao_formatada = gerar_evolucao(dados)
    st.markdown(evolucao_formatada)
