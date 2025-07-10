import streamlit as st
import pandas as pd
from io import BytesIO
import re

# ----------- CONFIGURAÇÃO -----------

# Troque para True para ativar modo venda Fusione (personalização total)
MODO_FUSIONE = False

# Cores padrão VIPAL
VIPAL_AZUL = "#01438F"
VIPAL_VERMELHO = "#E4003A"

# Upload e seleção de paleta no modo Fusione
if MODO_FUSIONE:
    st.sidebar.markdown("## Personalização Fusione")
    fusione_logo = st.sidebar.file_uploader("Logotipo (PNG)", type=['png'])
    cor_primaria = st.sidebar.color_picker("Cor primária", value=VIPAL_AZUL)
    cor_secundaria = st.sidebar.color_picker("Cor secundária", value=VIPAL_VERMELHO)
    if fusione_logo:
        LOGO_PATH = fusione_logo
    else:
        LOGO_PATH = "Logotipo Vipal_positivo.png"
    VIPAL_AZUL, VIPAL_VERMELHO = cor_primaria, cor_secundaria
else:
    LOGO_PATH = "Logotipo Vipal_positivo.png"

# Índices disponíveis
INDICES = {
    "Selic": {"fonte": "Bacen"},
    "IPCA": {"fonte": "IBGE"},
    "CDI": {"fonte": "B3"},
    "IGPM": {"fonte": "FGV"},
}

# ----------- FUNÇÕES -----------

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

# ----------- LAYOUT -----------

st.set_page_config(page_title="Atualização de valores", layout="wide")

# CSS para forçar Montserrat
st.markdown("""
    <link href="https://fonts.googleapis.com/css?family=Montserrat:400,700&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"]  {
            font-family: 'Montserrat', sans-serif !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ----------- NOVO BLOCO DE TÍTULO, ÍNDICE E FONTE -----------

# 1. Seleção do índice, alinhada à esquerda, tamanho mínimo
st.markdown(
    f"""<div style="display:flex; align-items:center; margin-top:14px;">
        <span style="font-size:1.14rem;font-family:Montserrat,sans-serif;font-weight:600; color:{VIPAL_AZUL};margin-right:16px;">
            Escolha o índice
        </span>
        <div style="min-width:140px;max-width:170px;">
        """,
    unsafe_allow_html=True
)
indice_nome = st.selectbox(
    "", list(INDICES.keys()), key="indice_select", index=0, label_visibility='collapsed'
)
st.markdown("</div></div>", unsafe_allow_html=True)

# 2. Bloco do logo, título e fonte (ajustado conforme seu pedido)
col_logo, col_gap, col_titulo = st.columns([1.7, 0.2, 7])

with col_logo:
    st.image(LOGO_PATH, width=330)  # +50% maior

with col_titulo:
    st.markdown(
        f"""<div style="margin-top:18px; margin-bottom:-2px; text-align:left;">
            <span style="font-size:2.6rem;font-weight:700;color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;">
                Atualização de valores pelo(a) {indice_nome}
            </span>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""<div style="text-align:right; margin-right:20px; margin-top:-8px;">
            <span style="font-size:1.18rem; color:#555; font-family:Montserrat,sans-serif;">
                Fonte do índice: {INDICES[indice_nome]["fonte"]}
            </span>
        </div>""",
        unsafe_allow_html=True
    )

# Barra colorida
st.markdown(
    f"<div style='height:7px;width:100%;background:linear-gradient(90deg,{VIPAL_VERMELHO},#019FFF,#8e44ad);border-radius:8px;margin-bottom:2rem;'></div>",
    unsafe_allow_html=True
)

# Seções menores (Atualização individual e em massa)
# ----------- ATUALIZAÇÃO INDIVIDUAL -----------
arquivo = None  # Se quiser condicionar com upload, ajustar aqui

if not arquivo:
    st.markdown(
        f"<h3 style='color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;font-size:1.27rem;margin-bottom:-6px;'>Atualização individual</h3>",
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
    # Botão centralizado, tamanho igual ao campo do meio
    st.markdown(
        """
        <div style="display:flex;justify-content:center;">
            <div style="width:100%;">
        """, unsafe_allow_html=True)
    calcular = st.button(
        "Calcular valor atualizado",
        use_container_width=True,
        type="primary"
    )
    st.markdown("</div></div>", unsafe_allow_html=True)

    # Mensagem e resultado/erro
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
            f"<div style='margin-top:1rem;padding:1rem 1.2rem;background:{cor_mensagem};border-radius:10px;font-size:1.1rem;color:#333;font-weight:500;'>{mensagem}</div>",
            unsafe_allow_html=True,
        )

# ----------- MASSA (EM EXCEL) -----------
st.markdown(
    f"<h3 style='color:{VIPAL_AZUL};font-family:Montserrat,sans-serif;margin-top:2.3rem;font-size:1.27rem;'>Atualização em massa (arquivo Excel)</h3>",
    unsafe_allow_html=True
)
st.write("<b>Colunas obrigatórias:</b> data_inicial (dd/mm/aaaa), data_final (dd/mm/aaaa), valor (1.000,00)", unsafe_allow_html=True)

# Campo de upload personalizado PT-BR, alinhado à esquerda
st.markdown(
    """<div style='margin-bottom:6px; margin-top:10px; font-family:Montserrat,sans-serif;font-size:1.1rem;color:#333;'>Selecione seu arquivo Excel</div>""",
    unsafe_allow_html=True
)
arquivo = st.file_uploader(
    "Arraste e solte o arquivo aqui",
    type=["xlsx"],
    help="Arraste e solte um arquivo .xlsx com as colunas corretas"
)
# Mensagem drag and drop ptbr
st.markdown(
    """<div style='font-size:0.97rem;color:#555;font-family:Montserrat,sans-serif;margin-top:-16px;margin-bottom:14px;'>
        Limite 200MB por arquivo • XLSX
    </div>""", unsafe_allow_html=True
)
# Botão de baixar/exemplo, agora "Exportar dados ou arquivo de exemplo", alinhado à esquerda logo abaixo do upload
exemplo_df = exemplo_excel()
exemplo_bytes = gerar_excel(exemplo_df)
st.download_button(
    "Exportar dados ou arquivo de exemplo",
    exemplo_bytes,
    file_name="exemplo_atualizacao.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
    help="Download do modelo Excel correto"
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

# ----------- RODAPÉ -----------

st.markdown(
    f"""
    <div style='margin-top:2.8rem;display:flex;align-items:center;justify-content:center;gap:18px;'>
        <img src="https://raw.githubusercontent.com/ggrighi15/Atualizar_Selic/main/fusione_logo_v2_main.png" style="height:28px;" />
        <span style="font-size:1.05rem;color:#555;font-family:Montserrat,sans-serif;">Fusione Automação | por Gustavo Giovani Righi</span>
    </div>
    """,
    unsafe_allow_html=True
)
