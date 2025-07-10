import streamlit as st
import pandas as pd
from io import BytesIO
import re

# ----------- CONFIGURAÇÃO -----------
VIPAL_AZUL = "#01438F"
VIPAL_VERMELHO = "#E4003A"

INDICES = {
    "Selic": {"fonte": "Bacen"},
    "IPCA": {"fonte": "IBGE"},
    "CDI": {"fonte": "B3"},
    "IGPM": {"fonte": "FGV"},
}

LOGO_PATH = "Logotipo Vipal_positivo.png"
FUSIONE_LOGO = "fusione_logo_v2_main.png"

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

st.set_page_config(page_title="Atualização de valores", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com/css?family=Montserrat:400,700&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"]  {
            font-family: 'Montserrat', sans-serif !important;
        }
        .stTextInput>div>div>input { font-family: Montserrat,sans-serif; }
        .stDownloadButton button, .stButton button {
            font-family: Montserrat,sans-serif;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)

# ----------- LAYOUT -----------

col_logo, col_titulo = st.columns([1.8, 7.2])

with col_logo:
    st.image(LOGO_PATH, width=330)

with col_titulo:
    st.markdown(
        f"""<div style="margin-top:30px; text-align:center;">
            <span style="font-size:2.8rem;font-weight:700;color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;">
                Atualização de valores pelo(a) <span id="indice_nome_span">Selic</span>
            </span>
        </div>""",
        unsafe_allow_html=True,
    )

# Índice dinâmico
st.markdown("""
    <style>
        .fonte-indice {text-align:right; margin-top:10px; margin-bottom:8px;}
    </style>
""", unsafe_allow_html=True)

col_select, col_fonte = st.columns([8, 2])

with col_select:
    st.markdown(f"<span style='font-size:1.16rem;font-weight:700;color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;'>Escolha o índice</span>", unsafe_allow_html=True)
    indice_nome = st.selectbox(
        "", list(INDICES.keys()),
        key="indice_select", index=0, label_visibility='collapsed'
    )

with col_fonte:
    st.markdown(
        f"<div class='fonte-indice'><span style='font-size:1.1rem;color:#333;font-family:Montserrat,sans-serif;'>Fonte do índice: {INDICES[indice_nome]['fonte']}</span></div>",
        unsafe_allow_html=True
    )

# Altera o título ao trocar índice (JS hack porque Streamlit não faz nativo)
st.markdown(f"""
    <script>
    const span = window.parent.document.getElementById("indice_nome_span");
    if(span) span.innerText = "{indice_nome}";
    </script>
""", unsafe_allow_html=True)

# Barra colorida
st.markdown(
    f"<div style='height:7px;width:100%;background:linear-gradient(90deg,{VIPAL_VERMELHO},#019FFF,#8e44ad);border-radius:8px;margin-bottom:2rem;'></div>",
    unsafe_allow_html=True
)

# ----------- ATUALIZAÇÃO INDIVIDUAL -----------

data_inicial, data_final, valor_base = '', '', ''

# Exibe campos individuais se NÃO houver upload de arquivo
if "uploaded_file" not in st.session_state:
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        data_inicial = st.text_input(
            "Data inicial (dd/mm/aaaa)", max_chars=10,
            help="Digite a data no formato ddmmaaaa ou dd/mm/aaaa"
        )
    with col2:
        data_final = st.text_input(
            "Data final (dd/mm/aaaa)", max_chars=10,
            help="Digite a data no formato ddmmaaaa ou dd/mm/aaaa"
        )
    with col3:
        valor_base = st.text_input(
            "Valor base (R$)", max_chars=20,
            help="Digite o valor. Ex: 1000 ou 2.000,00"
        )
    st.markdown(
        "<div style='display:flex;justify-content:center;'><div style='width:70%;'>",
        unsafe_allow_html=True)
    calcular = st.button(
        "Calcular valor atualizado",
        use_container_width=True,
        type="primary"
    )
    st.markdown("</div></div>", unsafe_allow_html=True)
    mensagem = ""
    resultado = None

    if calcular:
        di_fmt = auto_formatar_data(data_inicial)
        df_fmt = auto_formatar_data(data_final)
        valor_fmt = re.sub(r"[^\d,]", "", valor_base)
        valor_fmt = valor_fmt.replace(",", ".") if "," in valor_fmt else valor_fmt

        dt_ini = validar_data(di_fmt)
        dt_fim = validar_data(df_fmt)
        try:
            valor = parse_valor(valor_base)
        except Exception:
            valor = None

        if not (dt_ini and dt_fim and valor_base.strip() and valor is not None and valor > 0):
            mensagem = "Verifique os dados. Formato correto: dd/mm/aaaa e valor em reais."
            cor_mensagem = "#fff"
            st.markdown(
                f"<div style='margin-top:1rem;padding:1.1rem 1.2rem;background:#fff;border:1.8px solid {VIPAL_VERMELHO};border-radius:10px;font-size:1.17rem;color:{VIPAL_VERMELHO};font-weight:500;text-align:center;'>{mensagem}</div>",
                unsafe_allow_html=True,
            )
        elif dt_ini > dt_fim:
            mensagem = "A data final deve ser posterior à data inicial."
            cor_mensagem = "#fff"
            st.markdown(
                f"<div style='margin-top:1rem;padding:1.1rem 1.2rem;background:#fff;border:1.8px solid {VIPAL_VERMELHO};border-radius:10px;font-size:1.17rem;color:{VIPAL_VERMELHO};font-weight:500;text-align:center;'>{mensagem}</div>",
                unsafe_allow_html=True,
            )
        else:
            atualizado = calcular_indice(valor, di_fmt, df_fmt, indice_nome)
            mensagem = f"Valor atualizado: R$ {atualizado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.markdown(
                f"<div style='margin: 36px auto 0 auto; padding:1.4rem 1.2rem;background:{VIPAL_AZUL};border-radius:14px;font-size:1.33rem;color:#fff;font-family:Montserrat,sans-serif;font-weight:700;text-align:center;max-width:650px;'>{mensagem}</div>",
                unsafe_allow_html=True,
            )

# ----------- ATUALIZAÇÃO EM MASSA (UPLOAD) -----------

st.markdown(
    f"<div style='margin: 2.4rem 0 0 0;text-align:center;font-size:1.13rem;color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;font-weight:700;'>Atualização em massa (opcional)</div>",
    unsafe_allow_html=True
)
uploaded_file = st.file_uploader(
    "Selecione ou arraste seu arquivo Excel", type=["xlsx"], label_visibility="collapsed"
)
if uploaded_file:
    st.session_state.uploaded_file = uploaded_file
else:
    st.session_state.uploaded_file = None

st.markdown(
    "<div style='margin-bottom:2px;text-align:center;font-family:Montserrat,sans-serif;font-size:1.06rem;'>Colunas obrigatórias: data_inicial (dd/mm/aaaa), data_final (dd/mm/aaaa), valor (1.000,00)</div>",
    unsafe_allow_html=True
)

# Download de exemplo/excel
exemplo_df = exemplo_excel()
exemplo_bytes = gerar_excel(exemplo_df)
st.download_button(
    "Exportar dados ou arquivo de exemplo",
    exemplo_bytes,
    file_name="exemplo_atualizacao.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

# ----------- RODAPÉ -----------

st.markdown(
    f"""
    <div style='margin-top:2.7rem;display:flex;align-items:center;justify-content:center;gap:18px;'>
        <img src="https://raw.githubusercontent.com/ggrighi15/Atualizar_Selic/main/fusione_logo_v2_main.png" style="height:28px;" />
        <span style="font-size:1.07rem;color:#555;font-family:Montserrat,sans-serif;margin-left:4px;'>Fusione Automação | por Gustavo Giovani Righi</span>
    </div>
    """,
    unsafe_allow_html=True
)
