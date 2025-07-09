import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from io import BytesIO

# --- CONFIGURAÇÃO STREAMLIT ---
st.set_page_config(
    page_title="Atualização de Valores pela SELIC (Bacen)",
    layout="wide",
    page_icon="💸"
)

# --- CSS VIPAL ---
vipal_blue = "#01438F"
vipal_red = "#E4003A"
st.markdown(f"""
    <style>
    body {{
        background-color: #f8f9fa;
    }}
    .block-container {{
        padding-top: 1rem !important;
    }}
    .stApp {{
        background-color: #f8f9fa;
    }}
    .titulo-vipal {{
        color: {vipal_blue};
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 2.8rem;
        font-weight: 900;
        margin-bottom: 0px;
    }}
    .subtitulo-vipal {{
        color: #444;
        font-size: 1.2rem;
        margin-top: 0;
    }}
    .divider-vipal {{
        border: none;
        height: 3px;
        background: linear-gradient(90deg, {vipal_red} 0%, {vipal_blue} 100%);
        margin: 1rem 0;
    }}
    </style>
""", unsafe_allow_html=True)

# --- TOPO COM LOGOTIPO VIPAL ---
st.markdown(
    f"""
    <div style='display: flex; align-items: center; gap: 24px; margin-bottom:0px'>
        <img src="https://github.com/ggrighi15/Atualizar_Selic/raw/main/Logotipo%20Vipal_positivo.png" width="120"/>
        <div>
            <span class='titulo-vipal'>Atualização de Valores pela SELIC</span><br>
            <span class='subtitulo-vipal'>(Bacen)</span>
        </div>
    </div>
    <hr class="divider-vipal">
    """, unsafe_allow_html=True
)

# --- FUNÇÕES ---
def formatar_data_input(label):
    """Campo de data com formatação dd/mm/aaaa com barra automática"""
    data_txt = st.text_input(label, placeholder="dd/mm/aaaa")
    data_fmt = ""
    if data_txt:
        # Adiciona barra automaticamente enquanto digita
        d = ''.join(filter(str.isdigit, data_txt))
        if len(d) > 2:
            d = d[:2] + '/' + d[2:]
        if len(d) > 5:
            d = d[:5] + '/' + d[5:9]
        data_fmt = d
        # Atualiza valor exibido
        st.session_state[label] = data_fmt
    else:
        data_fmt = ""
    return data_fmt

def validar_data(data_str):
    try:
        datetime.strptime(data_str, "%d/%m/%Y")
        return True
    except Exception:
        return False

def get_selic_diaria(data_inicial, data_final):
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=csv&dataInicial={data_inicial}&dataFinal={data_final}"
    df = pd.read_csv(url, sep=';', decimal=',')
    df['valor'] = pd.to_numeric(df['valor'].str.replace(',', '.'), errors='coerce')
    return df

def calcular_atualizado(valor_inicial, df_selic):
    fator = (df_selic['valor'] / 100 + 1).prod()
    return valor_inicial * fator

def exemplo_excel():
    """Gera arquivo de exemplo"""
    df = pd.DataFrame({
        "data_inicial": ["01/01/2022", "01/06/2023"],
        "data_final":   ["01/07/2022", "01/07/2024"],
        "valor":        [1000.00, 2500.00]
    })
    output = BytesIO()
    df.to_excel(output, index=False)
    return output.getvalue()

# --- ATUALIZAÇÃO INDIVIDUAL ---
st.markdown(f"<h2 class='titulo-vipal' style='font-size:1.8rem;margin-bottom:0.2em'>Atualização Individual</h2>", unsafe_allow_html=True)
st.markdown(f"<hr class='divider-vipal'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1,1,1])

with col1:
    data_ini = st.text_input("Data Inicial (dd/mm/aaaa)", key="data_ini", placeholder="dd/mm/aaaa")
    if data_ini and len(data_ini.replace('/', '')) in (4, 6, 8):
        # Completa barras
        d = ''.join(filter(str.isdigit, data_ini))
        if len(d) >= 2: d = d[:2] + '/' + d[2:]
        if len(d) >= 4: d = d[:5] + '/' + d[4:8]
        data_ini = d
        st.session_state["data_ini"] = data_ini
with col2:
    data_fim = st.text_input("Data Final (dd/mm/aaaa)", key="data_fim", placeholder="dd/mm/aaaa")
    if data_fim and len(data_fim.replace('/', '')) in (4, 6, 8):
        d = ''.join(filter(str.isdigit, data_fim))
        if len(d) >= 2: d = d[:2] + '/' + d[2:]
        if len(d) >= 4: d = d[:5] + '/' + d[4:8]
        data_fim = d
        st.session_state["data_fim"] = data_fim
with col3:
    valor_base = st.text_input("Valor Base (R$)", key="valor_base", placeholder="1.000,00")

if st.button("Calcular Valor Atualizado", use_container_width=True):
    # --- Validação ---
    try:
        v = float(str(valor_base).replace('.', '').replace(',', '.'))
        v_ok = v > 0
    except Exception:
        v_ok = False
    data_ini_ok = validar_data(data_ini)
    data_fim_ok = validar_data(data_fim)
    if not (data_ini_ok and data_fim_ok and v_ok):
        st.error("Dados inválidos. Use datas no formato dd/mm/aaaa e valor em reais.")
    else:
        # Formatar para API
        dinicio = datetime.strptime(data_ini, "%d/%m/%Y").strftime("%d/%m/%Y")
        dfim = datetime.strptime(data_fim, "%d/%m/%Y").strftime("%d/%m/%Y")
        df_selic = get_selic_diaria(dinicio, dfim)
        if not df_selic.empty:
            valor_final = calcular_atualizado(float(str(valor_base).replace('.', '').replace(',', '.')), df_selic)
            st.success(f"Valor atualizado: R$ {valor_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        else:
            st.warning("Não foram encontrados dados SELIC para o período informado.")

# --- ATUALIZAÇÃO EM MASSA ---
st.markdown(f"<h2 class='titulo-vipal' style='font-size:1.5rem;margin-top:1.8em'>Atualização em Massa (Arquivo Excel)</h2>", unsafe_allow_html=True)
st.caption("Colunas obrigatórias: data_inicial (dd/mm/aaaa), data_final (dd/mm/aaaa), valor (1.000,00)")
col_up, col_ex = st.columns([3,1])
with col_up:
    arquivo = st.file_uploader("Selecione seu arquivo Excel", type=["xlsx"])
with col_ex:
    st.download_button("Baixar Exemplo de Arquivo Excel", exemplo_excel(), file_name="exemplo_atualizacao_selic.xlsx", use_container_width=True)

if arquivo:
    df_entrada = pd.read_excel(arquivo)
    resultados = []
    for _, row in df_entrada.iterrows():
        try:
            data_ini_x = pd.to_datetime(str(row['data_inicial']), dayfirst=True).strftime('%d/%m/%Y')
            data_fim_x = pd.to_datetime(str(row['data_final']), dayfirst=True).strftime('%d/%m/%Y')
            valor_x = float(str(row['valor']).replace('.', '').replace(',', '.'))
            df_selic = get_selic_diaria(data_ini_x, data_fim_x)
            valor_corrigido = calcular_atualizado(valor_x, df_selic) if not df_selic.empty else None
            resultados.append(valor_corrigido)
        except Exception:
            resultados.append(None)
    df_entrada['valor_atualizado'] = [
        f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if v else None
        for v in resultados
    ]
    st.dataframe(df_entrada)
    # Exportação resultado
    output_xlsx = BytesIO()
    df_entrada.to_excel(output_xlsx, index=False)
    st.download_button(
        "Baixar Resultado Atualizado",
        output_xlsx.getvalue(),
        file_name="resultado_atualizado_selic.xlsx",
        use_container_width=True
    )

# --- FOOTER ---
st.markdown(
    """
    <div style='margin-top:30px;display:flex;align-items:center;gap:10px;'>
        <img src='https://raw.githubusercontent.com/ggrighi15/Atualizar_Selic/main/fusione_logo_v2_main.png' width='48'>
        <span style='color:#666;font-size:1rem;'>Fusione Automação Jurídica por Gustavo Righi</span>
    </div>
    """, unsafe_allow_html=True
)
