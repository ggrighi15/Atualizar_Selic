import streamlit as st
import pandas as pd
from io import BytesIO
import re

# ---------- CONFIGURAÇÃO ----------

LOGO_PATH = "Logotipo Vipal_positivo.png"

# Paleta VIPAL
VIPAL_AZUL = "#01438F"
VIPAL_VERMELHO = "#E4003A"

# Lista de índices disponíveis (exemplo)
INDICES = {
    "Selic": {"fonte": "Bacen"},
    "IPCA": {"fonte": "IBGE"},
    "CDI": {"fonte": "B3"},
    "IGPM": {"fonte": "FGV"},
}

# ---------- FUNÇÕES UTILITÁRIAS ----------

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

def calcular_indice(valor_base, data_inicial, data_final, indice_nome):
    # Troque pelas funções/calculadoras reais de cada índice!
    dt_ini = pd.to_datetime(data_inicial, dayfirst=True)
    dt_fim = pd.to_datetime(data_final, dayfirst=True)
    meses = max((dt_fim.year - dt_ini.year) * 12 + dt_fim.month - dt_ini.month, 0)
    taxas = {
        "Selic": 0.01,
        "IPCA": 0.006,
        "CDI": 0.008,
        "IGPM": 0.007,
    }
    tx = taxas.get(indice_nome, 0.01)
    return valor_base * ((1 + tx) ** meses)

def gerar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def exemplo_excel():
    return pd.DataFrame({
        "Dados iniciais (dd/mm/aaaa)": ["15/03/2023"],
        "Dados finais (dd/mm/aaaa)": ["09/07/2025"],
        "Valor base (R$)": ["1.000,00"],
        "Índice": ["1,21"],
        "Valor atualizado": ["1.210,00"]
    })

# ---------- LAYOUT ----------

st.set_page_config(page_title="Atualização de valores", layout="wide")

# Logo e título
col_logo, col_title = st.columns([1, 8])
with col_logo:
    st.image(LOGO_PATH, width=120)
with col_title:
    # Seleção de índice
    indice_nome = st.selectbox(
        "Escolha o índice",
        options=list(INDICES.keys()),
        index=0,
        key="indice_select",
        help="Selecione o índice para cálculo"
    )
    # Título customizado
    st.markdown(
        f"""
        <div style='display: flex; flex-direction: column; align-items: flex-start;'>
            <span style='font-size:2.2rem;font-weight:700;color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;'>
                Atualização de valores pela {indice_nome}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
    # Fonte alinhada à direita
    st.markdown(
        f"""
        <div style='width:100%;text-align:right;margin-top:-1.2rem;'>
            <span style='font-size:1rem;color:#444;font-family:Montserrat,sans-serif;'>{INDICES[indice_nome]["fonte"]}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# Barra colorida
st.markdown(
    f"<div style='height:7px;width:100%;background:linear-gradient(90deg,{VIPAL_VERMELHO},#019FFF,#8e44ad);border-radius:8px;margin-bottom:2rem;'></div>",
    unsafe_allow_html=True
)

# ---------- ATUALIZAÇÃO INDIVIDUAL ----------

st.markdown(
    f"<h2 style='color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;font-size:2rem;'>Atualização individual</h2>",
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([1,1,1])

with col1:
    data_inicial = st.text_input(
        "Data inicial (dd/mm/aaaa)",
        max_chars=10,
        help="Digite a data no formato ddmmaaaa ou dd/mm/aaaa"
    )
    data_inicial_formatada = data_inicial
    if data_inicial and ("/" not in data_inicial or len(data_inicial.replace("/", "")) == 8):
        data_inicial_formatada = auto_formatar_data(data_inicial)

with col2:
    data_final = st.text_input(
        "Data final (dd/mm/aaaa)",
        max_chars=10,
        help="Digite a data no formato ddmmaaaa ou dd/mm/aaaa"
    )
    data_final_formatada = data_final
    if data_final and ("/" not in data_final or len(data_final.replace("/", "")) == 8):
        data_final_formatada = auto_formatar_data(data_final)

with col3:
    valor_base = st.text_input(
        "Valor base (R$)",
        max_chars=20,
        help="Digite o valor. Ex: 1000 ou 2.000,00"
    )

# Botão azul com fonte branca
calcular = st.button(
    "Calcular valor atualizado",
    use_container_width=True,
    type="primary"
)

mensagem = ""
cor_mensagem = "#FFDFDF"
resultado = None

if calcular:
    dt_ini = validar_data(data_inicial_formatada)
    dt_fim = validar_data(data_final_formatada)
    try:
        valor = parse_valor(valor_base)
    except Exception:
        valor = None

    if not (dt_ini and dt_fim and valor_base.strip() and valor is not None and valor > 0):
        mensagem = "Verifique os dados. Formato correto: dd/mm/aaaa e valor em reais."
        cor_mensagem = "#FFDFDF"
    elif dt_ini > dt_fim:
        mensagem = "A data final deve ser posterior à data inicial."
        cor_mensagem = "#FFDFDF"
    else:
        atualizado = calcular_indice(valor, data_inicial_formatada, data_final_formatada, indice_nome)
        mensagem = f"Valor atualizado: R$ {atualizado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        cor_mensagem = "#D2FAD2"
        resultado = atualizado

if mensagem:
    st.markdown(
        f"<div style='margin-top:1rem;padding:1rem 1.2rem;background:{cor_mensagem};border-radius:10px;font-size:1.2rem;color:#333;font-weight:500;'>{mensagem}</div>",
        unsafe_allow_html=True,
    )

# ---------- ATUALIZAÇÃO EM MASSA ----------

st.markdown(
    f"<h2 style='color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;margin-top:3rem;'>Atualização em massa (arquivo Excel)</h2>",
    unsafe_allow_html=True
)
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
    arquivo = st.file_uploader(
        "Selecione seu arquivo Excel",
        type=["xlsx"],
        help="Arraste e solte um arquivo .xlsx com as colunas corretas"
    )

if arquivo:
    try:
        df = pd.read_excel(arquivo)
        obrigatorias = ["data_inicial (dd/mm/aaaa)", "data_final (dd/mm/aaaa)", "valor base (r$)"]
        df.columns = [c.lower().strip() for c in df.columns]
        if all(col in df.columns for col in obrigatorias):
            indices = []
            valores_atualizados = []
            for _, row in df.iterrows():
                vi = row['data_inicial (dd/mm/aaaa)']
                vf = row['data_final (dd/mm/aaaa)']
                vb = parse_valor(row['valor base (r$)'])
                ind = 1.21  # Exemplo fixo
                va = calcular_indice(vb, vi, vf, indice_nome)
                indices.append(ind)
                valores_atualizados.append(va)
            df["índice"] = indices
            df["valor atualizado"] = valores_atualizados
            st.dataframe(df)
            st.download_button(
                "Exportar atualização em massa",
                gerar_excel(df),
                file_name="atualizacao_resultado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.error("Arquivo Excel não contém todas as colunas obrigatórias.")
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

st.markdown(
    "<div style='margin-top:3rem;font-size:1.1rem;color:#555;'>Fusione Automação Jurídica por Gustavo Righi</div>",
    unsafe_allow_html=True
)
