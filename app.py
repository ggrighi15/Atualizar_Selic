import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Ajuste o caminho conforme sua hospedagem
LOGO_PATH = "Logotipo Vipal_positivo.png"

# CSS para fonte, botões, cores
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;400&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Montserrat', Arial, sans-serif;
    }
    .stButton>button, .stDownloadButton>button {
        background-color: #01438F !important;
        color: #FFF !important;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.6em 2em;
        font-size: 1.1em;
        box-shadow: 0px 2px 4px rgba(1,67,143,0.1);
        transition: background 0.2s;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #003366 !important;
        color: #FFF !important;
    }
    .title-main {
        font-size: 2.7rem;
        font-weight: bold;
        color: #01438F;
        margin-bottom: 0.3em;
        line-height: 1.0em;
    }
    .rainbow-bar {
        height: 5px;
        background: linear-gradient(90deg, #E4003A, #00B88A, #7256f1);
        border-radius: 8px;
        margin: 1.2em 0 1.2em 0;
    }
    </style>
""", unsafe_allow_html=True)

# ========== LAYOUT ==========
st.image(LOGO_PATH, width=150)
st.markdown('<div class="title-main">Atualização de valores pela Selic</div>', unsafe_allow_html=True)
st.write("(Bacen)")
st.markdown('<div class="rainbow-bar"></div>', unsafe_allow_html=True)

st.header("Atualização individual")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    data_inicial = st.text_input("Data inicial (dd/mm/aaaa)", placeholder="dd/mm/aaaa")
with col2:
    data_final = st.text_input("Data final (dd/mm/aaaa)", placeholder="dd/mm/aaaa")
with col3:
    valor_base = st.text_input("Valor base (R$)", placeholder="1.000,00")

btn_calc = st.button("Calcular valor atualizado")

def calcular_selic(d1, d2, v):
    # Substitua pela rotina oficial Selic se quiser cálculo real
    try:
        dt1 = datetime.strptime(d1, "%d/%m/%Y")
        dt2 = datetime.strptime(d2, "%d/%m/%Y")
        if dt1 >= dt2 or v <= 0:
            return None
        # Exemplo didático: 0,9% ao mês simples só para demonstração
        meses = (dt2.year - dt1.year) * 12 + (dt2.month - dt1.month)
        taxa = 0.009 * meses
        return round(v * (1 + taxa), 2)
    except Exception:
        return None

if btn_calc:
    try:
        valor_float = float(str(valor_base).replace(".", "").replace(",", "."))
        val = calcular_selic(data_inicial, data_final, valor_float)
        if val:
            st.success(f"Valor atualizado: R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        else:
            st.error("Verifique os dados. Formato correto: dd/mm/aaaa e valor em reais.")
    except Exception:
        st.error("Verifique os dados. Formato correto: dd/mm/aaaa e valor em reais.")

# ========== ATUALIZAÇÃO EM MASSA ==========
st.header("Atualização em massa (arquivo Excel)")
st.caption("Colunas obrigatórias: data_inicial (dd/mm/aaaa), data_final (dd/mm/aaaa), valor (1.000,00)")

# Exemplo Excel para download
def gerar_excel_exemplo():
    df = pd.DataFrame({
        "Data inicial (dd/mm/aaaa)": ["15/03/2023"],
        "Data final (dd/mm/aaaa)": ["15/03/2025"],
        "Valor base (R$)": ["1000,00"]
    })
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)
    return buffer

st.download_button(
    label="Baixar arquivo de exemplo",
    data=gerar_excel_exemplo(),
    file_name="exemplo_atualizacao_selic.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

arquivo = st.file_uploader("Selecione seu arquivo Excel", type=["xlsx"])
if arquivo:
    df = pd.read_excel(arquivo)
    colunas_ok = {"Data inicial (dd/mm/aaaa)", "Data final (dd/mm/aaaa)", "Valor base (R$)"}
    if set(df.columns) >= colunas_ok:
        resultados = []
        for _, row in df.iterrows():
            try:
                v = float(str(row["Valor base (R$)"]).replace(".", "").replace(",", "."))
                novo_valor = calcular_selic(str(row["Data inicial (dd/mm/aaaa)"]), str(row["Data final (dd/mm/aaaa)"]), v)
                resultados.append(novo_valor)
            except Exception:
                resultados.append(None)
        df["Valor atualizado"] = resultados
        st.dataframe(df)
        towrite = io.BytesIO()
        with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        towrite.seek(0)
        st.download_button(
            label="Exportar resultados atualizados",
            data=towrite,
            file_name="resultados_atualizados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("O arquivo precisa ter as colunas: Data inicial (dd/mm/aaaa), Data final (dd/mm/aaaa), Valor base (R$)")

st.markdown('<br><sub style="color:#01438F;">Fusione Automação Jurídica por Gustavo Righi</sub>', unsafe_allow_html=True)
