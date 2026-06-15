# =============================================================================
# LIMPEZA.PY — Tratamento e Padronização dos Dados
# Projeto de Análise de Dados | Educação Continuada
# =============================================================================

import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# 1. CONVERSÃO DE DATAS
# ─────────────────────────────────────────────────────────────────────────────

_COLUNAS_DATA = {
    "matriculas":    ["data_matricula"],
    "pagamentos":    ["data_vencimento", "data_pagamento"],
    "leads":         ["data_lead"],
    "cancelamentos": ["data_cancelamento"],
    "campanhas":     ["data_inicio", "data_fim"],
    "inadimplencia": ["data_referencia"],
    "certificados":  ["data_emissao"],
    "suporte":       ["data_abertura", "data_resolucao"],
    "acessos":       ["data_acesso"],
    "alunos":        ["data_cadastro"],
}


def converter_datas(tabelas: dict[str, pd.DataFrame]) -> None:
    """Converte colunas de data para datetime in-place."""
    for nome, colunas in _COLUNAS_DATA.items():
        df = tabelas.get(nome)
        if df is None or df.empty:
            continue
        for col in colunas:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")


# ─────────────────────────────────────────────────────────────────────────────
# 2. CAMPOS TEMPORAIS DERIVADOS
# ─────────────────────────────────────────────────────────────────────────────

def extrair_campos_temporais(tabelas: dict[str, pd.DataFrame]) -> None:
    """Cria colunas derivadas de ano, mês e período em matrículas e pagamentos."""
    mat = tabelas["matriculas"]
    pag = tabelas["pagamentos"]

    if "data_matricula" in mat.columns:
        mat["ano"]     = mat["data_matricula"].dt.year
        mat["mes"]     = mat["data_matricula"].dt.month
        mat["ano_mes"] = mat["data_matricula"].dt.to_period("M")
        mat["trimestre"] = mat["data_matricula"].dt.to_period("Q").astype(str)

    if "data_pagamento" in pag.columns:
        pag["ano_mes_pgto"] = pag["data_pagamento"].dt.to_period("M")


# ─────────────────────────────────────────────────────────────────────────────
# 3. TRATAMENTO DE NULOS E TIPOS NUMÉRICOS
# ─────────────────────────────────────────────────────────────────────────────

def tratar_numericos(tabelas: dict[str, pd.DataFrame]) -> None:
    """Converte colunas numéricas críticas e preenche nulos com zero."""
    alvos = [
        ("matriculas",   "valor_liquido"),
        ("pagamentos",   "valor_pago"),
        ("leads",        "score_lead"),
        ("avaliacoes",   "nota_satisfacao"),
    ]
    for nome, col in alvos:
        df = tabelas.get(nome)
        if df is not None and col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)


# ─────────────────────────────────────────────────────────────────────────────
# 4. PIPELINE COMPLETO DE LIMPEZA
# ─────────────────────────────────────────────────────────────────────────────

def limpar(tabelas: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Aplica todo o pipeline de limpeza e padronização.
    Retorna o mesmo dict com os DataFrames tratados in-place.
    """
    converter_datas(tabelas)
    extrair_campos_temporais(tabelas)
    tratar_numericos(tabelas)

    print("  ✓ Datas convertidas e campos temporais extraídos")
    print("  ✓ Nulos tratados em colunas numéricas críticas")

    return tabelas
