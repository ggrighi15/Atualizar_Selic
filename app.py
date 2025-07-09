import streamlit as st
import pandas as pd
from datetime import datetime
import re
from io import BytesIO

# PALETA VIPAL
VIPAL_AZUL = "#01438F"
VIPAL_VERMELHO = "#E4003A"

# LOGO
LOGO_URL = "https://raw.githubusercontent.com/ggrighi15/Atualizar_Selic/main/Logotipo%20Vipal_positivo.png"

def auto_formatar_data(valor):
    v = re.sub(r"\D", "", valor)[:8]
    if len(v) >= 5:
        return f"{v[:2]}/{v[2:4]}/{v[4:]}"
    elif len(v) >= 3:
        return f"{v[:2]}/{v[2:]}"
    else:
        return v

def parse_valor(valor):
    v = str(valor).replace('.', '').replace(',', '.')
    return float(re.sub(r"[^\d.]", "", v)) if v else 0.0

def validar_data(data):
    try:
        return pd.to_datetime(data, dayfirst=True, errors="raise")
    except Exception:
        return None

def calcular_selic(valor_base, data_inicial, data_final):
    """Exemplo: juros simples diário 0,0375% (corrija com a tabela oficial depois)"""
    dt_ini = pd.to_datetime(data_inicial, dayfirst=True)
    dt_fim = pd.to_datetime(data_final, dayfirst=True)
    dias = (dt_fim - dt_ini).days
    if dias < 0:
        return None
    taxa_diaria = 0.000375  # 0,0375% ao dia (~13,75% a.a.)
    return valor_base * ((1 + taxa_diaria) ** dias)

def gerar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def exemplo_excel():
    return pd.DataFrame({
        "Data inicial (dd/mm/aaaa)": ["15/03/2023"],
        "Data final (dd/mm/aaaa)": ["09/07/2025"],
        "Valor base (R$)": ["1.000,00"],
        "Índice": ["1,21"],
        "Valor atualizado": ["1.210,00"]
    })

st.set_page_config(page_title="Atualização de valores pela Selic", layout="wide")

# --------- TOPO E LOGO ----------
st.markdown(f"""
<div style='display:flex;align-items:center;gap:24px;margin-bottom:1rem'>
    <img src="{LOGO_URL}" style='height:70px'/>
    <span style='font-size:2.8rem;font-weight:700;color:{VIPAL_AZUL};font-family:sans-serif;'>Atualização de valores pela Selic</span>
</div>
<div style='color:#444;font-size:1.1rem;margin-bottom:0.5rem'>(Bacen)</div>
<div style='height:8px;width:100%;background:linear-gradient(90deg,{VIPAL_VERMELHO},#019FFF,#8e44ad);border-radius:8px;margin-bottom:2rem;'></div>
""", unsafe_allow_html=True)

# --------- ATUALIZAÇÃO INDIVIDUAL ----------
st.markdown(f"<h2 style='color:{VIPAL_AZUL};font-family:sans-serif;'>Atualização individual</h2>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1,1,1])
with col1:
    data_inicial = st.text_input("Data inicial (dd/mm/aaaa)", max_chars=10, key="data_ini", help="Digite a data no formato ddmmaaaa ou dd/mm/aaaa")
    if data_inicial and ("/" not in data_inicial or len(data_inicial.replace("/", "")) == 8):
        st.session_state["data_ini"] = auto_formatar_data(data_inicial)
with col2:
    data_final = st.text_input("Data final (dd/mm/aaaa)", max_chars=10, key="data_fim", help="Digite a data no formato ddmmaaaa ou dd/mm/aaaa")
    if data_final and ("/" not in data_final or len(data_final.replace("/", "")) == 8):
        st.session_state["data_fim"] = auto_formatar_data(data_final)
with col3:
    valor_base = st.text_input("Valor base (R$)", max_chars=20, key="valor_base", help="Ex: 2000 ou 2.000,00")

st.markdown("""
    <style>
    .stButton > button {
        background-color: #01438F !important;
        color: #fff !important;
        font-weight: 600 !important;
        border-radius: 7px !important;
        font-size: 1.1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

if st.button("Calcular valor atualizado", use_container_width=True):
    dt_ini = validar_data(data_inicial)
    dt_fim = validar_data(data_final)
    try:
        valor = parse_valor(valor_base)
    except Exception:
        valor = None

    if not (dt_ini and dt_fim and valor_base.strip() and valor is not None and valor > 0):
        st.markdown("<div style='margin-top:1rem;padding:1rem 1.2rem;background:#FFDFDF;border-radius:10px;font-size:1.1rem;color:#333;font-weight:500;'>Verifique os dados. Formato correto: dd/mm/aaaa e valor em reais.</div>", unsafe_allow_html=True)
    elif dt_ini > dt_fim:
        st.markdown("<div style='margin-top:1rem;padding:1rem 1.2rem;background:#FFDFDF;border-radius:10px;font-size:1.1rem;color:#333;font-weight:500;'>A data final deve ser posterior à data inicial.</div>", unsafe_allow_html=True)
    else:
        atualizado = calcular_selic(valor, data_inicial, data_final)
        if atualizado:
            st.markdown(f"<div style='margin-top:1rem;padding:1rem 1.2rem;background:#D2FAD2;border-radius:10px;font-size:1.2rem;color:#333;font-weight:600;'>Valor atualizado: R$ {atualizado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + "</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='margin-top:1rem;padding:1rem 1.2rem;background:#FFDFDF;border-radius:10px;font-size:1.1rem;color:#333;font-weight:500;'>Erro no cálculo. Revise as datas.</div>", unsafe_allow_html=True)

# --------- ATUALIZAÇÃO EM MASSA ----------
st.markdown(f"<h2 style='color:{VIPAL_AZUL};font-family:sans-serif;margin-top:3rem;'>Atualização em massa (arquivo Excel)</h2>", unsafe_allow_html=True)
st.write("Colunas obrigatórias: **data_inicial (dd/mm/aaaa), data_final (dd/mm/aaaa), valor (1.000,00)**")
exemplo_df = exemplo_excel()
exemplo_bytes = gerar_excel(exemplo_df)

col_e1, col_e2 = st.columns([1,2])
with col_e1:
    st.download_button(
        "Baixar arquivo de exemplo",
        exemplo_bytes,
        file_name="exemplo_atualizacao_selic.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        help="Download do modelo Excel correto"
    )
with col_e2:
    arquivo = st.file_uploader("Selecione seu arquivo Excel", type=["xlsx"], help="Arraste um arquivo .xlsx com as colunas corretas")

if arquivo:
    try:
        df = pd.read_excel(arquivo)
        obrigatorias = ["data inicial (dd/mm/aaaa)", "data final (dd/mm/aaaa)", "valor base (r$)"]
        df.columns = [c.lower().strip() for c in df.columns]
        if all(col in df.columns for col in obrigatorias):
            indices = []
            valores_atualizados = []
            for _, row in df.iterrows():
                vi = row['data inicial (dd/mm/aaaa)']
                vf = row['data final (dd/mm/aaaa)']
                vb = parse_valor(row['valor base (r$)'])
                ind = 1.21  # Exemplo fixo
                va = calcular_selic(vb, vi, vf)
                indices.append(ind)
                valores_atualizados.append(va)
            df["índice"] = indices
            df["valor atualizado"] = valores_atualizados
            st.dataframe(df)
            st.download_button(
                "Exportar atualização em massa",
                gerar_excel(df),
                file_name="atualizacao_selic_resultado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.error("Arquivo Excel não contém todas as colunas obrigatórias.")
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

st.markdown("<div style='margin-top:3rem;font-size:1.1rem;color:#555;'>Fusione Automação Jurídica por Gustavo Righi</div>", unsafe_allow_html=True)
