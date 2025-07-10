import streamlit as st
import pandas as pd
import re
from io import BytesIO

# --- CORES FUSIONE ---
FUSIONE_AZUL_ESCURO = "#1e3a8a"
FUSIONE_AZUL_MEDIO = "#3b82f6"
FUSIONE_AZUL_CLARO = "#60a5fa"
FUSIONE_BRANCO = "#ffffff"
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
st.set_page_config(page_title="Sistema Fusione - Atualização de valores", layout="wide")

# Inicializar session_state se não existir
if 'data_inicial_formatada' not in st.session_state:
    st.session_state.data_inicial_formatada = ""
if 'data_final_formatada' not in st.session_state:
    st.session_state.data_final_formatada = ""

# --- CSS: TEMA FUSIONE MELHORADO ---
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] {{
    font-family: {FONTE_MONTSERRAT} !important;
    background: linear-gradient(135deg, {FUSIONE_AZUL_ESCURO} 0%, {FUSIONE_AZUL_MEDIO} 100%);
}}
.stButton>button, .stDownloadButton>button {{
    font-family: {FONTE_MONTSERRAT} !important;
    font-weight: 700;
    background: {FUSIONE_AZUL_MEDIO} !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
}}
.stTextInput>div>input, .stSelectbox>div>div>input {{
    font-family: {FONTE_MONTSERRAT} !important;
    border-radius: 8px !important;
}}
.main .block-container {{
    padding-top: 2rem;
    background: {FUSIONE_BRANCO};
    border-radius: 15px;
    margin: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}}
.fusione-logo {{
    font-family: 'Montserrat', sans-serif;
    font-weight: 900;
    font-size: 2.2rem;
    color: {FUSIONE_BRANCO};
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}}
</style>
""", unsafe_allow_html=True)

# --- HEADER FUSIONE MELHORADO ---
st.markdown(f"""
<div style="background: linear-gradient(135deg, {FUSIONE_AZUL_ESCURO} 0%, {FUSIONE_AZUL_MEDIO} 100%); 
     padding: 25px; margin: -20px -20px 30px -20px; border-radius: 15px 15px 0 0;">
    <div style="display: flex; align-items: center; justify-content: center; gap: 20px;">
        <div style="background: {FUSIONE_BRANCO}; padding: 12px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <img src="https://raw.githubusercontent.com/ggrighi15/Atualizar_Selic/main/fusione_logo_v2_main.png" style="height:45px;" />
        </div>
        <div style="text-align: center;">
            <div class="fusione-logo">SISTEMA FUSIONE</div>
            <p style="color: {FUSIONE_AZUL_CLARO}; margin: 5px 0 0 0; font-size: 1.1rem; font-weight: 600;">
                Atualização Monetária Profissional
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- ESCOLHA O ÍNDICE PRIMEIRO (INVERTIDO COM TÍTULO) ---
st.markdown(f"""<div style="font-weight:700; color:{FUSIONE_AZUL_ESCURO};font-size:1.3rem;font-family:Montserrat,sans-serif;margin-bottom:15px;text-align:center;">Escolha o índice</div>""", unsafe_allow_html=True)

col_select, col_space = st.columns([6, 4])
with col_select:
    indice_nome = st.selectbox(
        "",
        list(INDICES.keys()),
        index=0,
        key="indice_select",
        help="Selecione o índice desejado"
    )

# --- TÍTULO DINÂMICO E FONTE (APÓS SELEÇÃO) ---
col_titulo, col_fonte = st.columns([8, 2])
with col_titulo:
    st.markdown(
        f"""<div style="text-align:center;margin:25px 0;">
            <span style="font-size:2.8rem;font-weight:700;color:{FUSIONE_AZUL_ESCURO};font-family:Montserrat,sans-serif;">
                Atualização de valores pelo(a) {indice_nome}
            </span>
        </div>""", unsafe_allow_html=True
    )
with col_fonte:
    st.markdown(
        f"""<div style="text-align:right; margin-top:50px; font-family:Montserrat,sans-serif;">
            <span style="font-size:1.2rem; color:{FUSIONE_AZUL_MEDIO}; font-weight: 600;">Fonte: {INDICES[indice_nome]['fonte']}</span>
        </div>""", unsafe_allow_html=True
    )

# --- BARRA DECORATIVA ---
st.markdown(
    f"<div style='height:6px;width:100%;background:linear-gradient(90deg,{FUSIONE_AZUL_ESCURO},{FUSIONE_AZUL_MEDIO},{FUSIONE_AZUL_CLARO});border-radius:6px;margin-bottom:1.5rem;'></div>",
    unsafe_allow_html=True
)

# --- SEÇÃO INDIVIDUAL (ESPAÇAMENTO REDUZIDO) ---
st.markdown(f"""
<div style="background: linear-gradient(135deg, {FUSIONE_AZUL_CLARO}15 0%, {FUSIONE_AZUL_MEDIO}15 100%); 
     padding: 15px; border-radius: 10px; margin-bottom: 15px;">
    <h3 style="color: {FUSIONE_AZUL_ESCURO}; margin: 0 0 10px 0; font-family: Montserrat, sans-serif; font-weight: 700;">
        Atualização individual
    </h3>
</div>
""", unsafe_allow_html=True)

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

# --- BOTÃO CALCULAR ---
st.markdown("<div style='display:flex;justify-content:center;margin-top:20px;'><div style='width:100%;max-width:510px;'>", unsafe_allow_html=True)
calcular = st.button(
    "Calcular valor atualizado",
    use_container_width=True,
    type="primary"
)
st.markdown("</div></div>", unsafe_allow_html=True)

# --- RESULTADO ---
if calcular:
    dt_ini = validar_data(st.session_state.data_inicial_formatada)
    dt_fim = validar_data(st.session_state.data_final_formatada)
    try:
        valor = parse_valor(valor_base)
    except Exception:
        valor = None
    
    if not (dt_ini and dt_fim and valor_base.strip() and valor is not None and valor > 0):
        mensagem = "Verifique os dados. Formato correto: dd/mm/aaaa e valor em reais."
        st.markdown(f"<div style='margin:18px auto 0 auto;padding:20px;background:#fff;color:#dc2626;border:2px solid #dc2626;border-radius:10px;width:100%;max-width:650px;text-align:center;font-family:Montserrat,sans-serif;'>{mensagem}</div>", unsafe_allow_html=True)
    elif dt_ini > dt_fim:
        mensagem = "A data final deve ser posterior à data inicial."
        st.markdown(f"<div style='margin:18px auto 0 auto;padding:20px;background:#fff;color:#dc2626;border:2px solid #dc2626;border-radius:10px;width:100%;max-width:650px;text-align:center;font-family:Montserrat,sans-serif;'>{mensagem}</div>", unsafe_allow_html=True)
    else:
        atualizado = calcular_indice(valor, st.session_state.data_inicial_formatada, st.session_state.data_final_formatada, indice_nome)
        mensagem = f"Valor atualizado: R$ {formatar_valor_monetario(atualizado)}"
        st.markdown(f"<div style='margin:24px auto 0 auto;padding:20px;background:linear-gradient(135deg,{FUSIONE_AZUL_ESCURO},{FUSIONE_AZUL_MEDIO});color:#fff;font-weight:700;border-radius:12px;width:100%;max-width:650px;text-align:center;font-family:Montserrat,sans-serif;font-size:1.27rem;box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>{mensagem}</div>", unsafe_allow_html=True)

# --- INFORMAÇÕES E EXPORTAR ---
st.markdown(f"""<div style='text-align:center;font-family:Montserrat,sans-serif;font-size:1.08rem;margin:20px 0 5px 0;color:{FUSIONE_AZUL_MEDIO};font-weight:600;'>Colunas obrigatórias: data_inicial (dd/mm/aaaa), data_final (dd/mm/aaaa), valor (1.000,00)</div>""", unsafe_allow_html=True)

exemplo_df = exemplo_excel()
exemplo_bytes = gerar_excel(exemplo_df)
st.markdown("<div style='display:flex;justify-content:center;'><div style='width:100%;max-width:510px;'>", unsafe_allow_html=True)
st.download_button(
    "Exportar dados ou arquivo de exemplo",
    exemplo_bytes,
    file_name="exemplo_atualizacao_fusione.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
    help="Download do modelo Excel correto"
)
st.markdown("</div></div>", unsafe_allow_html=True)

# --- RODAPÉ FUSIONE MELHORADO ---
st.markdown(f"""
<div style='margin-top:3rem;padding:25px;background:linear-gradient(135deg,{FUSIONE_AZUL_ESCURO},{FUSIONE_AZUL_MEDIO});
     border-radius:12px;text-align:center;box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
    <div style='display:flex;align-items:center;justify-content:center;gap:20px;'>
        <img src="https://raw.githubusercontent.com/ggrighi15/Atualizar_Selic/main/fusione_logo_v2_main.png" style="height:30px;" />
        <span style="font-size:1.1rem;color:{FUSIONE_BRANCO};font-family:Montserrat,sans-serif;font-weight:700;">
            FUSIONE AUTOMAÇÃO
        </span>
    </div>
    <p style="color:{FUSIONE_AZUL_CLARO};margin:10px 0 0 0;font-size:0.95rem;font-weight:600;">
        Desenvolvido por Gustavo Giovani Righi | Sistema integrado de gestão empresarial
    </p>
</div>
""", unsafe_allow_html=True)

