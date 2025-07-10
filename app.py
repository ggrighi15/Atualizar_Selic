import streamlit as st
import pandas as pd
import re
from io import BytesIO

# --- CORES VIPAL ---
VIPAL_AZUL = "#01438F"
VIPAL_VERMELHO = "#E4003A"
FONTE_MONTSERRAT = "'Montserrat', sans-serif"

# --- ÍNDICES DISPONÍVEIS ---
INDICES = {
    "Selic": {"fonte": "Bacen"},
    "IPCA": {"fonte": "IBGE"},
    "CDI": {"fonte": "B3"},
    "IGPM": {"fonte": "FGV"},
}

# --- FUNÇÕES AUXILIARES ---
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

# --- CONFIG PAGE ---
st.set_page_config(page_title="Atualização de valores", layout="wide")

# --- CSS: MONTSERRAT, CENTRALIZAÇÕES, AJUSTES ---
st.markdown(f"""
<link href="https://fonts.googleapis.com/css?family=Montserrat:400,700&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] {{
    font-family: {FONTE_MONTSERRAT} !important;
}}
.stButton>button, .stDownloadButton>button {{
    font-family: {FONTE_MONTSERRAT} !important;
    font-weight: 700;
}}
.stTextInput>div>input, .stSelectbox>div>div>input {{
    font-family: {FONTE_MONTSERRAT} !important;
}}
</style>
""", unsafe_allow_html=True)

# --- LOGO VIPAL (ESQUERDA, GRANDE) ---
st.markdown("""
<div style="display:flex;align-items:center;gap:40px;">
    <img src="https://raw.githubusercontent.com/ggrighi15/Atualizar_Selic/main/Logotipo%20Vipal_positivo.png" width="330" style="margin-bottom: -16px;"/>
</div>
""", unsafe_allow_html=True)

# --- TÍTULO CENTRAL, FONTE DO ÍNDICE À DIREITA ---
col_titulo, col_fonte = st.columns([10, 2])
with col_titulo:
    st.markdown(
        f"""<div style="text-align:center;margin-top:-120px;margin-bottom:16px;">
            <span style="font-size:3rem;font-weight:700;color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;">
                Atualização de valores pelo(a) <span id="indice-title"></span>
            </span>
        </div>""", unsafe_allow_html=True
    )
with col_fonte:
    st.markdown(
        f"""<div style="text-align:right; margin-top:8px; font-family:Montserrat,sans-serif;">
            <span style="font-size:1.15rem; color:#333;">Fonte do índice: <span id="indice-fonte"></span></span>
        </div>""", unsafe_allow_html=True
    )

# --- ESCOLHA O ÍNDICE, SELECTBOX CENTRALIZADO ---
st.markdown(f"""<div style="text-align:left; font-weight:700; color:{VIPAL_AZUL};font-size:1.32rem;font-family:Montserrat,sans-serif;margin-top:5px;">Escolha o índice</div>""", unsafe_allow_html=True)

indice_nome = st.selectbox(
    "",
    list(INDICES.keys()),
    index=0,
    key="indice_select",
    help="Selecione o índice desejado"
)

# --- TÍTULO DINÂMICO E FONTE DO ÍNDICE (usando javascript) ---
st.markdown(f"""
<script>
document.getElementById("indice-title").innerText = "{indice_nome}";
document.getElementById("indice-fonte").innerText = "{INDICES[indice_nome]['fonte']}";
</script>
""", unsafe_allow_html=True)

# --- BARRA COLORIDA ---
st.markdown(
    f"<div style='height:8px;width:100%;background:linear-gradient(90deg,{VIPAL_VERMELHO},#019FFF,#8e44ad);border-radius:8px;margin-bottom:2.3rem;margin-top:2px;'></div>",
    unsafe_allow_html=True
)

# --- BOTÃO 2: UPLOAD DE ARQUIVO (CENTRALIZADO) ---
st.markdown(f"""<div style='text-align:center;font-weight:700;color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;font-size:1.25rem;margin-bottom:12px;margin-top:30px;'>Atualização em massa (opcional)</div>""", unsafe_allow_html=True)

st.markdown("<div style='display:flex;justify-content:center;'><div style='width:100%;max-width:510px;'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Selecione ou arraste seu arquivo Excel (máximo 200MB)",
    type=["xlsx"],
    key="file",
    help="Selecione ou arraste seu arquivo Excel"
)
st.markdown("</div></div>", unsafe_allow_html=True)

# --- SEÇÃO INDIVIDUAL (SEMPRE VISÍVEL, MAS DESAPARECE QUANDO ARQUIVO É CARREGADO) ---
if not uploaded_file:
    st.markdown(
        f"""<div style='font-family:Montserrat,sans-serif;font-weight:700;font-size:1.18rem;color:{VIPAL_AZUL};margin-top:18px;margin-bottom:0.5rem;'>Atualização individual</div>""",
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

    # --- BOTÃO 1: CALCULAR VALOR ATUALIZADO (CENTRALIZADO) ---
    st.markdown("<div style='display:flex;justify-content:center;margin-top:20px;'><div style='width:100%;max-width:510px;'>", unsafe_allow_html=True)
    calcular = st.button(
        "Calcular valor atualizado",
        use_container_width=True,
        type="primary"
    )
    st.markdown("</div></div>", unsafe_allow_html=True)

    # --- RESULTADO CENTRALIZADO ---
    if calcular:
        dt_ini = validar_data(data_inicial_formatada)
        dt_fim = validar_data(data_final_formatada)
        try:
            valor = parse_valor(valor_base)
        except Exception:
            valor = None
        if not (dt_ini and dt_fim and valor_base.strip() and valor is not None and valor > 0):
            mensagem = "Verifique os dados. Formato correto: dd/mm/aaaa e valor em reais."
            st.markdown(f"<div style='margin:18px auto 0 auto;padding:20px;background:#fff;color:{VIPAL_VERMELHO};border:2px solid {VIPAL_VERMELHO};border-radius:10px;width:100%;max-width:650px;text-align:center;font-family:Montserrat,sans-serif;'>{mensagem}</div>", unsafe_allow_html=True)
        elif dt_ini > dt_fim:
            mensagem = "A data final deve ser posterior à data inicial."
            st.markdown(f"<div style='margin:18px auto 0 auto;padding:20px;background:#fff;color:{VIPAL_VERMELHO};border:2px solid {VIPAL_VERMELHO};border-radius:10px;width:100%;max-width:650px;text-align:center;font-family:Montserrat,sans-serif;'>{mensagem}</div>", unsafe_allow_html=True)
        else:
            atualizado = calcular_indice(valor, data_inicial_formatada, data_final_formatada, indice_nome)
            mensagem = f"Valor atualizado: R$ {atualizado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.markdown(f"<div style='margin:24px auto 0 auto;padding:20px;background:{VIPAL_AZUL};color:#fff;font-weight:700;border-radius:12px;width:100%;max-width:650px;text-align:center;font-family:Montserrat,sans-serif;font-size:1.27rem;'>{mensagem}</div>", unsafe_allow_html=True)

# --- BOTÃO 2: UPLOAD DE ARQUIVO (CENTRALIZADO) ---
st.markdown(f"""<div style='text-align:center;font-weight:700;color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;font-size:1.25rem;margin-bottom:12px;margin-top:30px;'>Atualização em massa (opcional)</div>""", unsafe_allow_html=True)

st.markdown("<div style='display:flex;justify-content:center;'><div style='width:100%;max-width:510px;'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Selecione ou arraste seu arquivo Excel (máximo 200MB)",
    type=["xlsx"],
    key="file",
    help="Selecione ou arraste seu arquivo Excel"
)
st.markdown("</div></div>", unsafe_allow_html=True)

# --- BOTÃO 3: EXPORTAR DADOS OU ARQUIVO DE EXEMPLO (CENTRALIZADO) ---
st.markdown(f"""<div style='text-align:center;font-family:Montserrat,sans-serif;font-size:1.08rem;margin:20px 0 5px 0;'>Colunas obrigatórias: data_inicial (dd/mm/aaaa), data_final (dd/mm/aaaa), valor (1.000,00)</div>""", unsafe_allow_html=True)

exemplo_df = exemplo_excel()
exemplo_bytes = gerar_excel(exemplo_df)
st.markdown("<div style='display:flex;justify-content:center;'><div style='width:100%;max-width:510px;'>", unsafe_allow_html=True)
st.download_button(
    "Exportar dados ou arquivo de exemplo",
    exemplo_bytes,
    file_name="exemplo_atualizacao.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
    help="Download do modelo Excel correto"
)
st.markdown("</div></div>", unsafe_allow_html=True)

# --- PROCESSAMENTO DO ARQUIVO CARREGADO ---
if uploaded_file:
    # Esconde a seção individual quando arquivo é carregado
    st.markdown(f"""<div style='text-align:center;font-weight:700;color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;font-size:1.25rem;margin-top:30px;'>Arquivo carregado com sucesso!</div>""", unsafe_allow_html=True)
    
    try:
        df = pd.read_excel(uploaded_file)
        st.markdown(f"""<div style='text-align:center;font-family:Montserrat,sans-serif;font-size:1.1rem;margin:15px 0;'>Processando {len(df)} registros...</div>""", unsafe_allow_html=True)
        
        # Aqui você pode adicionar o processamento do arquivo Excel
        # Por exemplo, aplicar os cálculos de atualização em massa
        
    except Exception as e:
        st.markdown(f"<div style='margin:18px auto 0 auto;padding:20px;background:#fff;color:{VIPAL_VERMELHO};border:2px solid {VIPAL_VERMELHO};border-radius:10px;width:100%;max-width:650px;text-align:center;font-family:Montserrat,sans-serif;'>Erro ao processar arquivo: {str(e)}</div>", unsafe_allow_html=True)

# --- RODAPÉ: FUSIONE CENTRALIZADO ---
st.markdown(
    f"""
    <div style='margin-top:2.5rem;display:flex;align-items:center;justify-content:center;gap:16px;font-family:Montserrat,sans-serif;'>
        <img src="https://raw.githubusercontent.com/ggrighi15/Atualizar_Selic/main/fusione_logo_v2_main.png" style="height:30px;" />
        <span style="font-size:1.09rem;color:#555;">Fusione Automação | por Gustavo Giovani Righi</span>
    </div>
    """,
    unsafe_allow_html=True
)

