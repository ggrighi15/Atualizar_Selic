import streamlit as st
import pandas as pd
from io import BytesIO
import re

# LOGO DA VIPAL - use o nome do arquivo exatamente como está no repositório
LOGO_PATH = "Logotipo Vipal_positivo.png"

# Paleta VIPAL
VIPAL_AZUL = "#01438F"
VIPAL_VERMELHO = "#E4003A"

# ---------- Funções utilitárias ----------

def auto_formatar_data(valor):
    """Formata a string enquanto digita para dd/mm/aaaa"""
    v = re.sub(r"\D", "", valor)[:8]
    if len(v) >= 5:
        return f"{v[:2]}/{v[2:4]}/{v[4:]}"
    elif len(v) >= 3:
        return f"{v[:2]}/{v[2:]}"
    else:
        return v

def parse_valor(valor):
    """Aceita 2000, 2.000,00, 2000,00, etc e retorna float"""
    v = str(valor).replace('.', '').replace(',', '.')
    return float(re.sub(r"[^\d.]", "", v)) if v else 0.0

def validar_data(data):
    """Verifica se está no formato dd/mm/aaaa e se é data válida"""
    try:
        return pd.to_datetime(data, dayfirst=True, errors="raise")
    except Exception:
        return None

def calcular_selic(valor_base, data_inicial, data_final):
    """Simulação de cálculo real (corrija depois pela tabela oficial SELIC/Bacen)"""
    # EXEMPLO: juros simples 1% a.m. para teste (substitua pela tabela SELIC real depois)
    dt_ini = pd.to_datetime(data_inicial, dayfirst=True)
    dt_fim = pd.to_datetime(data_final, dayfirst=True)
    meses = max((dt_fim.year - dt_ini.year) * 12 + dt_fim.month - dt_ini.month, 0)
    return valor_base * ((1 + 0.01) ** meses)

def gerar_excel(df):
    output = BytesIO()
    wit
