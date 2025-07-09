import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Atualizador SELIC", page_icon="💸", layout="centered")

# --- LOGO E HEADER ---
col1, col2 = st.columns([1,5])
with col1:
    st.image("fusione_logo_v2_main.png", width=80)
with col2:
    st.markdown("<h2 style='margin-bottom:0'>Atualização de Valores pela SELIC <span style='font-size:18px'>(Bacen)</span></h2>", unsafe_allow_html=True)

st.markdown("---")

# --- Funções ---
def get_selic_diaria(data_inicial, data_final):
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=csv&dataInicial={data_inicial}&dataFinal={data_final}"
    df = pd.read_csv(url, sep=';')
    df['valor'] = pd.to_numeric(df['valor'].str.replace(',', '.'), errors='coerce')
    return df

def calcular_atualizado(valor_inicial, df_selic):
    fator = (df_selic['valor'] / 100 + 1).prod()
    return valor_inicial * fator

# --- Atualização Individual ---
st.subheader("Atualização Individual")

with st.form("individual_form"):
    data_ini = st.text_input("Data Inicial (dd/mm/aaaa)", value="")
    data_fim = st.text_input("Data Final (dd/mm/aaaa)", value="")
    valor_base = st.text_input("Valor Base (R$)", value="")

    submitted = st.form_submit_button("Calcular Valor Atualizado")
    if submitted:
        erro = None
        try:
            data_ini_dt = datetime.strptime(data_ini.strip(), "%d/%m/%Y")
            data_fim_dt = datetime.strptime(data_fim.strip(), "%d/%m/%Y")
            valor_base_f = float(str(valor_base).replace(",", "."))
            if valor_base_f <= 0:
                erro = "Informe um valor base maior que zero."
            elif data_fim_dt < data_ini_dt:
                erro = "Data final deve ser maior ou igual à data inicial."
        except:
            erro = "Dados inválidos. Use datas no formato dd/mm/aaaa e valor em reais."

        if not erro:
            df_selic = get_selic_diaria(data_ini_dt.strftime('%d/%m/%Y'), data_fim_dt.strftime('%d/%m/%Y'))
            if not df_selic.empty:
                valor_final = calcular_atualizado(valor_base_f, df_selic)
                valor_final_fmt = f"R$ {valor_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                st.success(f"Valor atualizado: {valor_final_fmt}")
            else:
                st.warning("Não foram encontrados dados SELIC para o período informado.")
        else:
            st.error(erro)

# --- Atualização em Massa ---
st.subheader("Atualização em Massa (Arquivo Excel)")
st.caption("Colunas obrigatórias: data_inicial (dd/mm/aaaa), data_final (dd/mm/aaaa), valor (1.000,00)")

arquivo = st.file_uploader("Selecione seu arquivo Excel", type=["xlsx"])
if arquivo:
    df_entrada = pd.read_excel(arquivo)
    resultados = []
    for _, row in df_entrada.iterrows():
        try:
            ini = datetime.strptime(str(row['data_inicial']).strip(), "%d/%m/%Y")
            fim = datetime.strptime(str(row['data_final']).strip(), "%d/%m/%Y")
            val = float(str(row['valor']).replace(",", "."))
            df_selic = get_selic_diaria(ini.strftime('%d/%m/%Y'), fim.strftime('%d/%m/%Y'))
            val_corrigido = calcular_atualizado(val, df_selic)
            val_corrigido_fmt = f"{val_corrigido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            resultados.append(val_corrigido_fmt)
        except Exception as e:
            resultados.append("Erro")
    df_entrada['valor_atualizado'] = resultados
    st.dataframe(df_entrada)
    st.download_button(
        "Baixar resultado atualizado",
        df_entrada.to_excel(index=False), file_name="resultado_atualizado.xlsx"
    )

st.caption("![logo](fusione_logo_v2_main.png) Fusione Automação Jurídica by Gustavo Righi")

# --- Logo Vipal (exemplo de uso interno, oculto por padrão) ---
# st.image("Logotipo Vipal_positivo.svg", width=120)  # Se for exibir só para uso interno

