import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

st.set_page_config(page_title="Atualização de Valores SELIC", layout="centered")

# ---- LOGOTIPO NO TOPO ----
st.image("Logotipo Vipal_cores.png", width=200)
st.markdown("<h1 style='text-align: center; color: #0047AB;'>Atualização de Valores pela SELIC<br><span style='font-size:0.6em;'>(Bacen)</span></h1>", unsafe_allow_html=True)

# ---- EXEMPLO ARQUIVO ----
exemplo = pd.DataFrame({
    'data_inicial': ['01/01/2020'],
    'data_final': ['01/01/2021'],
    'valor': [1000]
})
excel_exemplo = io.BytesIO()
exemplo.to_excel(excel_exemplo, index=False)
excel_exemplo.seek(0)

with st.expander("Baixe o arquivo de exemplo para atualização em massa", expanded=False):
    st.download_button(
        label="Baixar arquivo exemplo",
        data=excel_exemplo,
        file_name="exemplo_atualizacao_selic.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ---- FUNÇÕES ----
def get_selic_diaria(data_inicial, data_final):
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=csv&dataInicial={data_inicial}&dataFinal={data_final}"
    df = pd.read_csv(url, sep=';')
    df['valor'] = pd.to_numeric(df['valor'].str.replace(',', '.'), errors='coerce')
    return df

def calcular_atualizado(valor_inicial, df_selic):
    fator = (df_selic['valor'] / 100 + 1).prod()
    return valor_inicial * fator

# ---- INDIVIDUAL ----
st.subheader("Atualização Individual")
col1, col2, col3 = st.columns(3)
with col1:
    data_ini = st.date_input("Data Inicial")
with col2:
    data_fim = st.date_input("Data Final")
with col3:
    valor_base = st.text_input("Valor Base (R$)", value="")

if st.button("Calcular Valor Atualizado", type="primary"):
    try:
        valor_float = float(str(valor_base).replace('.', '').replace(',', '.'))
        ini = data_ini.strftime('%d/%m/%Y')
        fim = data_fim.strftime('%d/%m/%Y')
        df_selic = get_selic_diaria(ini, fim)
        if not df_selic.empty:
            valor_final = calcular_atualizado(valor_float, df_selic)
            st.success(f"Valor atualizado: R$ {valor_final:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        else:
            st.warning("Não foram encontrados dados SELIC para o período informado.")
    except Exception as e:
        st.error(f"Dados inválidos. Use datas no formato dd/mm/aaaa e valor em reais. Erro: {e}")

# ---- EM MASSA ----
st.subheader("Atualização em Massa (Arquivo Excel)")
st.markdown("Colunas obrigatórias: <b>data_inicial (dd/mm/aaaa)</b>, <b>data_final (dd/mm/aaaa)</b>, <b>valor (1.000,00)</b>", unsafe_allow_html=True)
arquivo = st.file_uploader("Selecione seu arquivo Excel", type=["xlsx"])
if arquivo:
    df_entrada = pd.read_excel(arquivo)
    resultados = []
    for _, row in df_entrada.iterrows():
        try:
            ini = pd.to_datetime(row['data_inicial'], dayfirst=True).strftime('%d/%m/%Y')
            fim = pd.to_datetime(row['data_final'], dayfirst=True).strftime('%d/%m/%Y')
            valor = float(str(row['valor']).replace('.', '').replace(',', '.'))
            df_selic = get_selic_diaria(ini, fim)
            valor_corrigido = calcular_atualizado(valor, df_selic)
            resultados.append(valor_corrigido)
        except Exception:
            resultados.append(None)
    df_entrada['valor_atualizado'] = [f"R$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if v is not None else '' for v in resultados]
    st.dataframe(df_entrada)
    excel_result = io.BytesIO()
    df_entrada.to_excel(excel_result, index=False)
    excel_result.seek(0)
    st.download_button(
        label="Exportar resultado atualizado",
        data=excel_result,
        file_name="resultado_atualizado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ---- RODAPÉ ----
st.caption("Fusione Automação Jurídica by Gustavo Righi")

