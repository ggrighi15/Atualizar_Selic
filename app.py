import streamlit as st
import pandas as pd
from io import BytesIO
import re

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
        "data_inicial (dd/mm/aaaa)": ["15/03/2023"],
        "data_final (dd/mm/aaaa)": ["09/07/2025"],
        "valor base (R$)": ["1.000,00"]
    })

st.set_page_config(page_title="Atualização de valores", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com/css?family=Montserrat:400,700&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"]  { font-family: 'Montserrat', sans-serif !important; }
        .stButton button { font-family: 'Montserrat', sans-serif; font-weight: 600; font-size: 1.15rem; }
    </style>
    """, unsafe_allow_html=True)

# ----------- HEADER -----------

st.markdown(
    f"""
    <div style="display: flex; flex-direction: column; align-items: flex-start; margin-bottom: -25px;">
        <img src="https://raw.githubusercontent.com/ggrighi15/Atualizar_Selic/main/Logotipo%20Vipal_positivo.png" style="height:92px;margin-bottom: -8px;margin-left:2px;" />
    </div>
    """, unsafe_allow_html=True
)

st.markdown(
    f"""<div style="width:100%; text-align:center;">
        <span style="font-size:2.7rem;font-weight:700;color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;">
            Atualização de valores pelo(a) <span id='indice-titulo'></span>
        </span>
    </div>""",
    unsafe_allow_html=True
)

# Fonte do índice, direita e abaixo do título
indice_nome = st.selectbox(
    "Escolha o índice", list(INDICES.keys()),
    key="indice_select", index=0,
    label_visibility='collapsed'
)

st.markdown(
    f"""<div style="display:flex; justify-content:center; align-items:flex-end; margin-bottom:8px;">
        <div style="flex:1;"></div>
        <div style="font-size:1.18rem; color:#555; font-family:Montserrat,sans-serif;text-align:right;width:430px;">
            Fonte do índice: {INDICES[indice_nome]['fonte']}
        </div>
    </div>""", unsafe_allow_html=True
)

# Atualiza título dinamicamente JS (gambiarra de compatibilidade para Streamlit Cloud)
st.markdown(
    f"""
    <script>
    var titulo = window.parent.document.querySelector('#indice-titulo');
    if (titulo) titulo.textContent = '{indice_nome}';
    </script>
    """, unsafe_allow_html=True
)

# Escolha de índice centralizada, logo abaixo do fonte do índice
st.markdown(
    f"""<div style="width:100%;text-align:center;margin-bottom:-8px;">
        <div style="display:inline-block;min-width:160px;max-width:210px;">
        <span style="font-size:1.13rem;font-family:Montserrat,sans-serif;font-weight:600; color:{VIPAL_AZUL};margin-right:12px;">
            Escolha o índice
        </span>
        </div>
    </div>""",
    unsafe_allow_html=True
)

# Barra colorida
st.markdown(
    f"<div style='height:7px;width:100%;background:linear-gradient(90deg,{VIPAL_VERMELHO},#019FFF,#8e44ad);border-radius:8px;margin-bottom:2rem;'></div>",
    unsafe_allow_html=True
)

# ----------- INDIVIDUAL -----------
arquivo = None
uploaded_file = None
if 'uploaded_file' in st.session_state:
    uploaded_file = st.session_state['uploaded_file']

if not uploaded_file:
    st.markdown(
        f"<h3 style='color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;font-size:1.25rem;margin-bottom:-3px;text-align:left;margin-left:9px;'>Atualização individual</h3>",
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        data_inicial = st.text_input(
            "Data inicial (dd/mm/aaaa)",
            max_chars=10,
            help="Digite a data no formato ddmmaaaa ou dd/mm/aaaa"
        )
        if data_inicial and ("/" not in data_inicial or len(data_inicial.replace("/", "")) == 8):
            data_inicial = auto_formatar_data(data_inicial)
    with col2:
        data_final = st.text_input(
            "Data final (dd/mm/aaaa)",
            max_chars=10,
            help="Digite a data no formato ddmmaaaa ou dd/mm/aaaa"
        )
        if data_final and ("/" not in data_final or len(data_final.replace("/", "")) == 8):
            data_final = auto_formatar_data(data_final)
    with col3:
        valor_base = st.text_input(
            "Valor base (R$)",
            max_chars=20,
            help="Digite o valor. Ex: 1000 ou 2.000,00"
        )
    # BOTÃO CENTRALIZADO, IGUAL AO CAMPO DO MEIO
    st.markdown("<div style='display:flex;justify-content:center;'><div style='width:100%;max-width:440px;'>", unsafe_allow_html=True)
    calcular = st.button(
        "Calcular valor atualizado",
        use_container_width=True,
        key="btn_calcular"
    )
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    mensagem = ""
    cor_mensagem = VIPAL_AZUL
    if calcular:
        dt_ini = validar_data(data_inicial)
        dt_fim = validar_data(data_final)
        try:
            valor = parse_valor(valor_base)
        except Exception:
            valor = None

        if not (dt_ini and dt_fim and valor_base.strip() and valor is not None and valor > 0):
            mensagem = "Verifique os dados. Formato correto: dd/mm/aaaa e valor em reais."
            cor_mensagem = "#E4003A"
        elif dt_ini > dt_fim:
            mensagem = "A data final deve ser posterior à data inicial."
            cor_mensagem = "#E4003A"
        else:
            atualizado = calcular_indice(valor, data_inicial, data_final, indice_nome)
            mensagem = f"Valor atualizado: R$ {atualizado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            cor_mensagem = VIPAL_AZUL
    if mensagem:
        st.markdown(
            f"<div style='margin:18px auto 0 auto; width:100%;max-width:440px;padding:1.13rem 1.2rem;background:{cor_mensagem};border-radius:10px;font-size:1.2rem;color:#fff;font-weight:500;text-align:center;'>{mensagem}</div>",
            unsafe_allow_html=True,
        )

# ----------- UPLOAD EXCEL -----------
st.markdown(
    "<div style='margin:24px auto 2px auto;width:100%;max-width:440px;text-align:center;font-family:Montserrat,sans-serif;font-size:1.07rem;font-weight:500;color:#333;'>Atualização em massa (opcional)</div>",
    unsafe_allow_html=True
)
arquivo = st.file_uploader(
    "Selecione ou arraste seu arquivo Excel",
    type=["xlsx"],
    key="uploaded_file",
    label_visibility="collapsed"
)
st.markdown(
    "<div style='margin:0 auto -1px auto;width:100%;max-width:440px;text-align:center;color:#555;font-size:0.98rem;'>Limite 200MB por arquivo • XLSX</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div style='margin:19px auto 10px auto;width:100%;max-width:660px;text-align:center;color:#333;font-size:1.06rem;font-family:Montserrat,sans-serif;font-weight:600;'>Colunas obrigatórias: data_inicial (dd/mm/aaaa), data_final (dd/mm/aaaa), valor (1.000,00)</div>",
    unsafe_allow_html=True
)

exemplo_df = exemplo_excel()
exemplo_bytes = gerar_excel(exemplo_df)
st.markdown("<div style='margin:0 auto 0 auto;width:100%;max-width:440px;text-align:center;'>", unsafe_allow_html=True)
st.download_button(
    "Exportar dados ou arquivo de exemplo",
    exemplo_bytes,
    file_name="exemplo_atualizacao.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
    help="Download do modelo Excel correto"
)
st.markdown("</div>", unsafe_allow_html=True)

# ----------- RODAPÉ -----------
st.markdown(
    f"""
    <div style='margin-top:2.4rem;display:flex;align-items:center;justify-content:center;gap:18px;'>
        <img src="https://raw.githubusercontent.com/ggrighi15/Atualizar_Selic/main/fusione_logo_v2_main.png" style="height:32px;" />
        <span style="font-size:1.11rem;color:#555;font-family:Montserrat,sans-serif;">Fusione Automação | por Gustavo Giovani Righi</span>
    </div>
    """,
    unsafe_allow_html=True
)
