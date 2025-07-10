import streamlit as st
import pandas as pd
from io import BytesIO
import re

# ----------- CONFIG VIPAL/FUSIONE -----------
LOGO_PATH = "Logotipo Vipal_positivo.png"
FUSIONE_LOGO = "fusione_logo_v2_main.png"
VIPAL_AZUL = "#01438F"
VIPAL_VERMELHO = "#E4003A"

INDICES = {
    "Selic": {"fonte": "Bacen"},
    "IPCA": {"fonte": "IBGE"},
    "CDI": {"fonte": "B3"},
    "IGPM": {"fonte": "FGV"},
}

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
    taxas = {"Selic": 0.01, "IPCA": 0.006, "CDI": 0.008, "IGPM": 0.007}
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

# ---------- LAYOUT E CSS ----------
st.set_page_config(page_title="Atualização de valores", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com/css?family=Montserrat:400,700&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"]  { font-family: 'Montserrat', sans-serif !important; }
        .block-container { padding-top: 0rem; }
    </style>
    """, unsafe_allow_html=True)

# --- TOPO VIPAL + TÍTULO + FONTE + ÍNDICE ---
col_logo, col_titulo, col_fonte = st.columns([2.2, 5.5, 2.3])

with col_logo:
    st.image(LOGO_PATH, width=330)
with col_titulo:
    st.markdown(
        f"""<div style="margin-top:24px; margin-bottom:-2px; text-align:center;">
            <span style="font-size:2.7rem;font-weight:700;color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;">
                Atualização de valores pelo(a) <span id="indice-titulo"></span>
            </span>
        </div>""",
        unsafe_allow_html=True,
    )
with col_fonte:
    indice_nome = st.session_state.get("indice_nome", "Selic")
    st.markdown(
        f"""<div style="margin-top:38px;text-align:right;">
            <span style="font-size:1.18rem; color:#555; font-family:Montserrat,sans-serif;">
                Fonte do índice: <span id="fonte-indice"></span>
            </span>
        </div>""",
        unsafe_allow_html=True
    )

# --- ESCOLHA DE ÍNDICE (direita, alinhado ao título) ---
col_vazio, col_idx = st.columns([7.6, 2.4])
with col_idx:
    indice_nome = st.selectbox(
        "Escolha o índice", list(INDICES.keys()),
        key="indice_nome",
        index=list(INDICES.keys()).index(indice_nome),
        label_visibility="visible"
    )

# Script para atualizar o título e fonte dinamicamente
st.markdown(
    f"""
    <script>
        document.getElementById("indice-titulo").innerText = "{indice_nome}";
        document.getElementById("fonte-indice").innerText = "{INDICES[indice_nome]['fonte']}";
    </script>
    """, unsafe_allow_html=True
)

# --- BARRA COLORIDA ---
st.markdown(
    f"<div style='height:7px;width:100%;background:linear-gradient(90deg,{VIPAL_VERMELHO},#019FFF,#8e44ad);border-radius:8px;margin-bottom:2.2rem;'></div>",
    unsafe_allow_html=True
)

# --- ATUALIZAÇÃO INDIVIDUAL (VISÍVEL SÓ SE NÃO HOUVER EXCEL) ---
if "uploaded_file" not in st.session_state or st.session_state["uploaded_file"] is None:
    st.markdown(
        f"<h3 style='color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;font-size:1.27rem;margin-bottom:-6px;text-align:center;'>Atualização individual</h3>",
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

    st.markdown(
        "<div style='display:flex;justify-content:center;'><div style='width:100%;max-width:490px;margin:auto;'>",
        unsafe_allow_html=True
    )
    calcular = st.button(
        "Calcular valor atualizado",
        use_container_width=True,
        type="primary"
    )
    st.markdown("</div></div>", unsafe_allow_html=True)

    # Mensagem resultado/erro centralizada
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
            f"<div style='margin-top:1rem;padding:1rem 1.2rem;background:{cor_mensagem};border-radius:10px;font-size:1.1rem;color:#333;font-weight:500;text-align:center;'>{mensagem}</div>",
            unsafe_allow_html=True,
        )

# --- UPLOAD (CENTRALIZADO, ABAIXO DO BOTÃO) ---
st.markdown("""
    <div style='display:flex;justify-content:center;'><div style='width:100%;max-width:490px;margin:auto;'>
    """, unsafe_allow_html=True
)
uploaded_file = st.file_uploader(
    "Selecione ou arraste seu arquivo Excel",
    type=["xlsx"],
    help="Limite 200MB por arquivo • XLSX",
    label_visibility="visible"
)
st.markdown(
    """<div style="font-size:0.97rem;color:#555;font-family:Montserrat,sans-serif;margin-top:-4px;">
        Limite 200MB por arquivo • XLSX<br>
        atualização em massa (opcional)
    </div>""",
    unsafe_allow_html=True
)
st.markdown("</div></div>", unsafe_allow_html=True)

# --- INFORMAÇÃO DAS COLUNAS OBRIGATÓRIAS ---
st.markdown(
    "<div style='margin-top:18px;text-align:center;font-family:Montserrat,sans-serif;'><b>Colunas obrigatórias:</b> data_inicial (dd/mm/aaaa), data_final (dd/mm/aaaa), valor (1.000,00)</div><br>",
    unsafe_allow_html=True
)

# --- EXPORTAR CÁLCULO OU ARQUIVO DE EXEMPLO ---
exemplo_df = exemplo_excel()
exemplo_bytes = gerar_excel(exemplo_df)
st.markdown("<div style='display:flex;justify-content:center;'><div style='width:100%;max-width:490px;margin:auto;'>", unsafe_allow_html=True)
st.download_button(
    "Exportar cálculo ou arquivo de exemplo",
    exemplo_bytes,
    file_name="exemplo_atualizacao.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
    help="Download do modelo Excel correto"
)
st.markdown("</div></div>", unsafe_allow_html=True)

# --- PROCESSAMENTO DO EXCEL (CENTRALIZADO) ---
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
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

# --- RODAPÉ ---
st.markdown(
    f"""
    <div style='margin-top:2.8rem;display:flex;align-items:center;justify-content:center;gap:18px;'>
        <img src="https://raw.githubusercontent.com/ggrighi15/Atualizar_Selic/main/fusione_logo_v2_main.png" style="height:28px;" />
        <span style="font-size:1.05rem;color:#555;font-family:Montserrat,sans-serif;">Fusione Automação | por Gustavo Giovani Righi</span>
    </div>
    """,
    unsafe_allow_html=True
)
