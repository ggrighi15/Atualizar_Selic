import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Logo Vipal
LOGO_PATH = "Logotipo Vipal_positivo.png"
st.image(LOGO_PATH, width=170)

# Títulos ajustados
st.title("Atualização de valores pela Selic")
st.write("(Bacen)")

# Entrada de dados com validação
st.subheader("Atualização individual")

data_inicial = st.text_input("Data inicial (dd/mm/aaaa)")
data_final = st.text_input("Data final (dd/mm/aaaa)")
valor_base = st.number_input("Valor base (R$)", min_value=0.01, format='%f')

def calcular_valor_selic(data_inicial, data_final, valor_base):
    try:
        inicio = datetime.strptime(data_inicial, "%d/%m/%Y")
        fim = datetime.strptime(data_final, "%d/%m/%Y")
        dias = (fim - inicio).days
        taxa_selic_diaria = 0.000375  # Exemplo: 0.0375% ao dia
        valor_atualizado = valor_base * ((1 + taxa_selic_diaria) ** dias)
        return valor_atualizado
    except:
        return None

if st.button("Calcular valor atualizado"):
    valor_atualizado = calcular_valor_selic(data_inicial, data_final, valor_base)
    if valor_atualizado:
        st.success(f"Valor atualizado: R$ {valor_atualizado:,.2f}")
    else:
        st.error("Verifique os dados. Formato correto: dd/mm/aaaa e valor em reais.")

# Exemplo para atualização em massa
st.subheader("Atualização em massa (arquivo Excel)")
st.write("Colunas obrigatórias: data_inicial, data_final, valor")

arquivo = st.file_uploader("Selecione seu arquivo Excel", type=["xlsx"])

if arquivo:
    df = pd.read_excel(arquivo)
    df['Valor atualizado'] = df.apply(
        lambda x: calcular_valor_selic(x['data_inicial'], x['data_final'], x['valor']), axis=1
    )
    output = io.BytesIO()
    df.to_excel(output, index=False)
    st.download_button(label="Baixar arquivo atualizado", data=output, file_name="atualizacao_selic.xlsx")

