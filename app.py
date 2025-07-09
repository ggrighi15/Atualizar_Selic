import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

# =================== CONFIGURAR ===================
LOGO_PATH = "Logotipo Vipal_positivo.png"  # Certifique-se do nome no GitHub!

VIPAL_AZUL = "#01438F"
VIPAL_VERMELHO = "#E4003A"

# =================== CSS - Paleta Vipal ===================
st.markdown(f"""
    <style>
        .main {{
            background-color: #f8fafc;
        }}
        .css-18e3th9 {{
            background-color: #f8fafc !important;
        }}
        h1, h2, h3, h4, h5 {{
            color: {VIPAL_AZUL};
        }}
        .st-bb {{
            color: {VIPAL_VERMELHO} !important;
        }}
        .titulo-vipal {{
            color: {VIPAL_AZUL};
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 0;
            margin-top: 0.5rem;
            font-family: Arial, sans-serif;
        }}
        .bar-colorida {{
            height: 6px;
            background: linear-gradient(90deg, {VIPAL_VERMELHO}, #33B4E3, #92D14F, #9561C6);
            border-radius: 2px;
            margin-bottom: 1.5rem;
            margin-top: 0.2rem;
        }}
    </style>
""", unsafe_allow_html=True)

# =================== TOPO DO SISTEMA ===================
st.image(LOGO_PATH, width=170)
st.markdown('<div class="titulo-vipal">Atualização de Valores pela SELIC</div>', unsafe_allow_html=True)
st.write("**(Bacen)**")
st.markdown('<div class="bar-colorida"></div>', unsafe_allow_html=True)

# =================== FUNÇÕES ===================
def get_selic_diaria(data_inicial, data_final):
    """Consulta a SELIC diária da API do Bacen."""
    url = (
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?"
        f"formato=csv&dataInicial={data_inicial}&dataFinal={data_final}"
    )
    df = pd.read_csv(url, sep=";")
    df['valor'] = pd.to_numeric(df['valor'].str.replace(',', '.'), errors='coerce')
    return df

def calcular_atualizado(valor_inicial, df_selic):
    """Calcula o valor atualizado pela SELIC acumulada."""
    fator = (df_selic['valor'] / 100 + 1).prod()
    return valor_inicial * fator

def gerar_excel(df):
    """Gera arquivo Excel para download."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# =================== ATUALIZAÇÃO INDIVIDUAL ===================
st.subheader("Atualização Individual")
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    data_ini = st.date_input("Data Inicial (dd/mm/aaaa)", format="DD/MM/YYYY")
with col2:
    data_fim = st.date_input("Data Final (dd/mm/aaaa)", format="DD/MM/YYYY")
with col3:
    valor_base = st.number_input("Valor Base (R$)", min_value=0.01, format="%.2f")

if st.button("Calcular Valor Atualizado", use_container_width=True):
    if data_fim < data_ini:
        st.error("A data final deve ser igual ou posterior à data inicial.")
    else:
        # Formata datas para API
        ini = data_ini.strftime('%d/%m/%Y')
        fim = data_fim.strftime('%d/%m/%Y')
        try:
            df_selic = get_selic_diaria(ini, fim)
            if df_selic.empty:
                st.warning("Não foram encontrados dados SELIC para o período informado.")
            else:
                valor_final = calcular_atualizado(valor_base, df_selic)
                st.success(f"Valor atualizado: R$ {valor_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        except Exception as e:
            st.error(f"Erro ao calcular: {e}")

# =================== ATUALIZAÇÃO EM MASSA ===================
st.subheader("Atualização em Massa (Arquivo Excel)")
st.caption("Colunas obrigatórias: data_inicial (dd/mm/aaaa), data_final (dd/mm/aaaa), valor (1.000,00)")

# Botão baixar exemplo
exemplo = pd.DataFrame({
    "data_inicial": ["01/01/2023", "01/07/2024"],
    "data_final": ["31/12/2023", "09/07/2025"],
    "valor": [1000, 2500]
})
st.download_button(
    "Baixar arquivo exemplo", 
    data=gerar_excel(exemplo),
    file_name="exemplo_atualizacao_selic.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Upload
arquivo = st.file_uploader("Selecione seu arquivo Excel", type=["xlsx"])
if arquivo:
    df_entrada = pd.read_excel(arquivo)
    resultados = []
    for _, row in df_entrada.iterrows():
        try:
            ini = pd.to_datetime(str(row['data_inicial']), dayfirst=True).strftime('%d/%m/%Y')
            fim = pd.to_datetime(str(row['data_final']), dayfirst=True).strftime('%d/%m/%Y')
            df_selic = get_selic_diaria(ini, fim)
            valor_corrigido = calcular_atualizado(row['valor'], df_selic)
            resultados.append(valor_corrigido)
        except Exception:
            resultados.append(None)
    df_entrada['valor_atualizado'] = resultados
    st.dataframe(df_entrada)
    st.download_button(
        "Baixar resultado atualizado",
        data=gerar_excel(df_entrada),
        file_name="resultado_atualizado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.caption("Fusione Automação Jurídica by Gustavo Righi")

