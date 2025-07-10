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
    """Formata automaticamente a data inserindo barras"""
    if not valor:
        return ""
    
    # Remove tudo que não é número
    numeros = re.sub(r"\D", "", valor)
    
    # Limita a 8 dígitos
    numeros = numeros[:8]
    
    # Aplica formatação progressiva
    if len(numeros) <= 2:
        return numeros
    elif len(numeros) <= 4:
        return f"{numeros[:2]}/{numeros[2:]}"
    else:
        return f"{numeros[:2]}/{numeros[2:4]}/{numeros[4:]}"

def formatar_valor_monetario(valor):
    """Formata valor no padrão brasileiro 1.000,00"""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def parse_valor(valor):
    """Converte string de valor para float"""
    if not valor:
        return 0.0
    v = str(valor).replace('.', '').replace(',', '.')
    return float(re.sub(r"[^\d.]", "", v)) if v else 0.0

def validar_data(data):
    """Valida se a data está no formato correto"""
    try:
        return pd.to_datetime(data, dayfirst=True, errors="raise")
    except Exception:
        return None

def calcular_indice(valor_base, data_inicial, data_final, indice_nome):
    """Calcula o valor atualizado pelo índice selecionado"""
    dt_ini = pd.to_datetime(data_inicial, dayfirst=True)
    dt_fim = pd.to_datetime(data_final, dayfirst=True)
    meses = max((dt_fim.year - dt_ini.year) * 12 + dt_fim.month - dt_ini.month, 0)
    taxas = {"Selic": 0.01, "IPCA": 0.006, "CDI": 0.008, "IGPM": 0.007}
    tx = taxas.get(indice_nome, 0.01)
    return valor_base * ((1 + tx) ** meses)

def gerar_excel(df):
    """Gera arquivo Excel para download"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def exemplo_excel():
    """Cria DataFrame de exemplo para download"""
    return pd.DataFrame({
        "data_inicial": ["15/03/2023"],
        "data_final": ["09/07/2025"],
        "valor": ["1.000,00"]
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

# --- LOGO VIPAL (ESQUERDA) ---
col_logo, col_resto = st.columns([2, 8])

with col_logo:
    st.markdown("""
    <div style="display:flex;align-items:center;">
        <img src="https://raw.githubusercontent.com/ggrighi15/Atualizar_Selic/main/Logotipo%20Vipal_positivo.png" width="200"/>
    </div>
    """, unsafe_allow_html=True)

with col_resto:
    # --- ESCOLHA O ÍNDICE PRIMEIRO (PARA DEFINIR O TÍTULO) ---
    st.markdown(f"""<div style="font-weight:700; color:{VIPAL_AZUL};font-size:1.2rem;font-family:Montserrat,sans-serif;margin-bottom:10px;">Escolha o índice</div>""", unsafe_allow_html=True)
    
    indice_nome = st.selectbox(
        "",
        list(INDICES.keys()),
        index=0,
        key="indice_select",
        help="Selecione o índice desejado"
    )
    
    # --- TÍTULO DINÂMICO CENTRALIZADO E FONTE DO ÍNDICE À DIREITA ---
    col_titulo, col_fonte = st.columns([8, 2])
    with col_titulo:
        st.markdown(
            f"""<div style="text-align:center;margin:20px 0;">
                <span style="font-size:2.5rem;font-weight:700;color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;">
                    Atualização de valores pelo(a) {indice_nome}
                </span>
            </div>""", unsafe_allow_html=True
        )
    with col_fonte:
        st.markdown(
            f"""<div style="text-align:right; margin-top:40px; font-family:Montserrat,sans-serif;">
                <span style="font-size:1.15rem; color:#333;">Fonte do índice: {INDICES[indice_nome]['fonte']}</span>
            </div>""", unsafe_allow_html=True
        )

# --- BARRA COLORIDA ---
st.markdown(
    f"<div style='height:8px;width:100%;background:linear-gradient(90deg,{VIPAL_VERMELHO},#019FFF,#8e44ad);border-radius:8px;margin-bottom:2.3rem;margin-top:2px;'></div>",
    unsafe_allow_html=True
)

# --- SEÇÃO INDIVIDUAL (SEMPRE VISÍVEL) ---
st.markdown(
    f"""<div style='font-family:Montserrat,sans-serif;font-weight:700;font-size:1.18rem;color:{VIPAL_AZUL};margin-top:18px;margin-bottom:0.5rem;'>Atualização individual</div>""",
    unsafe_allow_html=True
)

# Inicializar session_state se não existir
if 'data_inicial_formatada' not in st.session_state:
    st.session_state.data_inicial_formatada = ""
if 'data_final_formatada' not in st.session_state:
    st.session_state.data_final_formatada = ""

col1, col2, col3 = st.columns([1,1,1])

with col1:
    data_inicial = st.text_input(
        "Data inicial (dd/mm/aaaa)",
        value=st.session_state.data_inicial_formatada,
        max_chars=10,
        help="Digite a data no formato ddmmaaaa ou dd/mm/aaaa",
        key="data_inicial_input"
    )
    
    # Aplicar formatação automática
    if data_inicial != st.session_state.data_inicial_formatada:
        data_formatada = auto_formatar_data(data_inicial)
        st.session_state.data_inicial_formatada = data_formatada
        if data_formatada != data_inicial:
            st.rerun()

with col2:
    data_final = st.text_input(
        "Data final (dd/mm/aaaa)",
        value=st.session_state.data_final_formatada,
        max_chars=10,
        help="Digite a data no formato ddmmaaaa ou dd/mm/aaaa",
        key="data_final_input"
    )
    
    # Aplicar formatação automática
    if data_final != st.session_state.data_final_formatada:
        data_formatada = auto_formatar_data(data_final)
        st.session_state.data_final_formatada = data_formatada
        if data_formatada != data_final:
            st.rerun()

with col3:
    valor_base = st.text_input(
        "Valor base (R$)",
        placeholder="1.000,00",
        max_chars=20,
        help="Digite o valor. Ex: 1000 ou 2.000,00"
    )

# --- BOTÃO CALCULAR VALOR ATUALIZADO (CENTRALIZADO) ---
st.markdown("<div style='display:flex;justify-content:center;margin-top:20px;'><div style='width:100%;max-width:510px;'>", unsafe_allow_html=True)
calcular = st.button(
    "Calcular valor atualizado",
    use_container_width=True,
    type="primary"
)
st.markdown("</div></div>", unsafe_allow_html=True)

# --- RESULTADO CENTRALIZADO ---
if calcular:
    dt_ini = validar_data(st.session_state.data_inicial_formatada)
    dt_fim = validar_data(st.session_state.data_final_formatada)
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
        atualizado = calcular_indice(valor, st.session_state.data_inicial_formatada, st.session_state.data_final_formatada, indice_nome)
        mensagem = f"Valor atualizado: R$ {formatar_valor_monetario(atualizado)}"
        st.markdown(f"<div style='margin:24px auto 0 auto;padding:20px;background:{VIPAL_AZUL};color:#fff;font-weight:700;border-radius:12px;width:100%;max-width:650px;text-align:center;font-family:Montserrat,sans-serif;font-size:1.27rem;'>{mensagem}</div>", unsafe_allow_html=True)

# --- TEXTO COLUNAS OBRIGATÓRIAS ---
st.markdown(f"""<div style='text-align:center;font-family:Montserrat,sans-serif;font-size:1.08rem;margin:20px 0 5px 0;'>Colunas obrigatórias: data_inicial (dd/mm/aaaa), data_final (dd/mm/aaaa), valor (1.000,00)</div>""", unsafe_allow_html=True)

# --- BOTÃO EXPORTAR DADOS OU ARQUIVO DE EXEMPLO (CENTRALIZADO) ---
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

