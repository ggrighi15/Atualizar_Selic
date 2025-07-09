import streamlit as st
import pandas as pd
import requests
import io
import re
from datetime import datetime

# ---- VISUAL ----
st.set_page_config(page_title="Atualizador SELIC", page_icon="💸", layout="centered")

# Paleta Vipal (azul e cinza)
VIPAL_AZUL = "#0047AB"
VIPAL_CINZA = "#333333"

# Header com logotipos
col_logo1, col_logo2 = st.columns([1, 8])
with col_logo1:
    st.image("Logotipo Vipal_cores.png", width=80)
with col_logo2:
    st.image("fusione_logo_v2_main.png", width=120)

st.markdown(f"<h1 style='color:{VIPAL_AZUL}; font-size:2.2em; margin-bottom:0;'>Atualização de Valores pela SELIC</h1>", unsafe_allow_html=True)
st.markdown(f"<span style='color:{VIPAL_CINZA}; font-size:1.2em;'>(Bacen)</span>", unsafe_allow_html=True)

st.markdown("---")

# ---- FUNÇÕES ----
def mascara_data(valor):
    # Aplica máscara dd/mm/aaaa automaticamente
    v = re.sub(r'\D', '', valor)
    if len(v) > 2:
        v = v[:2] + '/' + v[2:]
    if len(v) > 5:
        v = v[:5] + '/' + v[5:]
    return v[:10]

def validar_data(d):
    try:
        datetime.strptime(d, "%d/%m/%Y")
        return True
    except:
        return False

def validar_valor(v):
    try:
        float(str(v).replace('.', '').replace(',', '.'))
        return True
    except:
        return False

def get_selic_diaria(data_inicial, data_final):
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=csv&dataInicial={data_inicial}&dataFinal={data_final}"
    df = pd.read_csv(url, sep=';')
    df['valor'] = pd.to_numeric(df['valor'].str.replace(',', '.'), errors='coerce')
    return df

def calcular_atualizado(valor_inicial, df_selic):
    fator = (df_selic['valor'] / 100 + 1).prod()
    return valor_inicial * fator

def formatar_reais(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# ---- INTERFACE INDIVIDUAL ----
st.subheader("Atualização Individual", divider='rainbow')
with st.form("form_individual"):
    data_ini = st.text_input("Data Inicial (dd/mm/aaaa)", value="", max_chars=10, help="Ex: 01/01/2010")
    data_fim = st.text_input("Data Final (dd/mm/aaaa)", value="", max_chars=10, help="Ex: 09/07/2025")
    valor_base = st.text_input("Valor Base (R$)", value="", max_chars=20, help="Ex: 1.000,00")

    # Máscara automática (Live no campo não é possível, mas corrige ao submit)
    data_ini = mascara_data(data_ini)
    data_fim = mascara_data(data_fim)

    submitted = st.form_submit_button("Calcular Valor Atualizado", use_container_width=True)
    if submitted:
        erro = None
        if not (validar_data(data_ini) and validar_data(data_fim)):
            erro = "Informe datas válidas no formato dd/mm/aaaa."
        elif not validar_valor(valor_base):
            erro = "Informe um valor base em reais (ex: 1.000,00)."
        else:
            valor_float = float(str(valor_base).replace('.', '').replace(',', '.'))
            try:
                df_selic = get_selic_diaria(data_ini, data_fim)
                if not df_selic.empty:
                    valor_final = calcular_atualizado(valor_float, df_selic)
                    st.success(f"Valor atualizado: **{formatar_reais(valor_final)}**")
                else:
                    erro = "Não há dados SELIC para o período."
            except Exception as e:
                erro = f"Erro ao buscar dados Bacen: {e}"
        if erro:
            st.error(erro)

# ---- ATUALIZAÇÃO EM MASSA ----
st.subheader("Atualização em Massa (Arquivo Excel)", divider='rainbow')
st.caption("Colunas obrigatórias: data_inicial (dd/mm/aaaa), data_final (dd/mm/aaaa), valor (1.000,00)")

col_upload, col_download = st.columns([2,1])
with col_upload:
    arquivo = st.file_uploader("Selecione seu arquivo Excel", type=["xlsx"])

# Exemplo para download
exemplo = pd.DataFrame({
    'data_inicial': ['01/01/2015', '15/05/2020'],
    'data_final':   ['01/06/2015', '09/07/2025'],
    'valor':        ['1.000,00',   '2.500,00']
})
with col_download:
    exemplo_bytes = io.BytesIO()
    exemplo.to_excel(exemplo_bytes, index=False)
    st.download_button("Baixar modelo Excel", exemplo_bytes.getvalue(), file_name="modelo_atualizacao.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

if arquivo:
    df_entrada = pd.read_excel(arquivo)
    resultados = []
    for _, row in df_entrada.iterrows():
        erro = None
        d_ini = mascara_data(str(row['data_inicial']))
        d_fim = mascara_data(str(row['data_final']))
        v = row['valor']
        if not (validar_data(d_ini) and validar_data(d_fim)):
            resultados.append(None)
            continue
        if not validar_valor(v):
            resultados.append(None)
            continue
        valor_float = float(str(v).replace('.', '').replace(',', '.'))
        try:
            df_selic = get_selic_diaria(d_ini, d_fim)
            if not df_selic.empty:
                valor_corrigido = calcular_atualizado(valor_float, df_selic)
                resultados.append(valor_corrigido)
            else:
                resultados.append(None)
        except:
            resultados.append(None)
    df_entrada['valor_atualizado'] = [formatar_reais(v) if v is not None else "" for v in resultados]
    st.dataframe(df_entrada)
    result_bytes = io.BytesIO()
    df_entrada.to_excel(result_bytes, index=False)
    st.download_button("Baixar resultado atualizado", result_bytes.getvalue(), file_name="resultado_atualizado.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

# ---- FOOTER ----
st.markdown("---")
colF, colT = st.columns([1, 10])
with colF:
    st.image("fusione_logo_v2_main.png", width=40)
with colT:
    st.caption("Fusione Automação Jurídica by Gustavo Righi | Powered by Bacen API | Vipal Automação Interna")

# --- FIM ---
