# =============================================================================
# KPIS.PY — Cálculo de KPIs Estratégicos
# Projeto de Análise de Dados | Educação Continuada
# =============================================================================
# Organização por dimensão analítica:
#   1. Financeiro
#   2. Acadêmico
#   3. Comercial / Marketing
#   4. Tabelas analíticas derivadas
# =============================================================================

import pandas as pd
import numpy as np

from config import ANOS_HISTORICO


# ─────────────────────────────────────────────────────────────────────────────
# 1. KPIs FINANCEIROS
# ─────────────────────────────────────────────────────────────────────────────

def kpis_financeiros(tabelas: dict) -> dict:
    """Retorna indicadores financeiros consolidados."""
    mat = tabelas["matriculas"]
    pag = tabelas["pagamentos"]
    inad = tabelas["inadimplencia"]

    pag_efetivos = pag[
        (pag["valor_pago"] > 0) & (pag["data_pagamento"].notna())
    ].copy()

    receita_total    = pag_efetivos["valor_pago"].sum()
    ticket_medio     = mat["valor_liquido"].mean()
    receita_bruta    = mat["valor_bruto"].sum()
    valor_inad_total = inad["valor_em_atraso"].sum()

    # Receita mensal consolidada (apenas pagamentos confirmados)
    rec_mensal = (
        pag_efetivos
        .groupby("ano_mes_pgto")["valor_pago"]
        .sum()
        .reset_index()
        .rename(columns={"ano_mes_pgto": "periodo", "valor_pago": "receita"})
    )
    rec_mensal["periodo_str"] = rec_mensal["periodo"].astype(str)
    rec_mensal = rec_mensal.sort_values("periodo")

    rec_historica = rec_mensal[
        rec_mensal["periodo_str"].str[:4].isin(ANOS_HISTORICO)
    ].copy()

    return {
        "receita_total":    receita_total,
        "ticket_medio":     ticket_medio,
        "receita_bruta":    receita_bruta,
        "valor_inad_total": valor_inad_total,
        "rec_mensal":       rec_mensal,
        "rec_historica":    rec_historica,
        "pag_efetivos":     pag_efetivos,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. KPIs ACADÊMICOS
# ─────────────────────────────────────────────────────────────────────────────

def kpis_academicos(tabelas: dict) -> dict:
    """Retorna indicadores de desempenho acadêmico e operacional."""
    mat   = tabelas["matriculas"]
    av    = tabelas["avaliacoes"]
    cert  = tabelas["certificados"]

    total_matriculas   = len(mat)
    total_alunos       = mat["aluno_id"].nunique()
    taxa_evasao        = mat["status"].isin(["Cancelada", "Evadida"]).mean()
    taxa_retencao      = 1 - taxa_evasao
    taxa_conclusao     = (mat["status"] == "Concluída").mean()
    taxa_inadimplencia = mat["inadimplente"].mean()
    taxa_recompra      = mat["recompra"].mean()

    nps_medio   = av["NPS"].mean()
    nota_satis  = av["nota_satisfacao"].mean()
    nota_prof   = av["nota_professor"].mean()
    nota_plat   = av["nota_plataforma"].mean()

    cert_emitidos = (cert["status_certificado"] == "Emitido").sum()

    # Evolução mensal de matrículas
    mat_mensal = (
        mat.groupby("ano_mes")
        .agg(
            matriculas=("matricula_id", "count"),
            receita=("valor_liquido", "sum"),
            alunos_novos=("aluno_id", "nunique"),
        )
        .reset_index()
    )
    mat_mensal["ano_mes_str"] = mat_mensal["ano_mes"].astype(str)
    mat_mensal = mat_mensal.sort_values("ano_mes")

    # Cohort por trimestre
    cohort_q = (
        mat.groupby("trimestre")
        .agg(
            matriculas=("matricula_id", "count"),
            receita=("valor_liquido", "sum"),
            evasao=("inadimplente", "mean"),
            ticket=("valor_liquido", "mean"),
        )
        .reset_index()
        .sort_values("trimestre")
    )
    cohort_hist = cohort_q[
        cohort_q["trimestre"].str[:4].isin(ANOS_HISTORICO)
    ]

    return {
        "total_matriculas":   total_matriculas,
        "total_alunos":       total_alunos,
        "taxa_evasao":        taxa_evasao,
        "taxa_retencao":      taxa_retencao,
        "taxa_conclusao":     taxa_conclusao,
        "taxa_inadimplencia": taxa_inadimplencia,
        "taxa_recompra":      taxa_recompra,
        "nps_medio":          nps_medio,
        "nota_satis":         nota_satis,
        "nota_prof":          nota_prof,
        "nota_plat":          nota_plat,
        "cert_emitidos":      cert_emitidos,
        "mat_mensal":         mat_mensal,
        "cohort_hist":        cohort_hist,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. KPIs COMERCIAIS / MARKETING
# ─────────────────────────────────────────────────────────────────────────────

def kpis_comerciais(tabelas: dict) -> dict:
    """Retorna indicadores de desempenho comercial e de marketing."""
    leads     = tabelas["leads"]
    campanhas = tabelas["campanhas"]
    mat       = tabelas["matriculas"]
    inad      = tabelas["inadimplencia"]

    total_leads    = len(leads)
    taxa_conversao = leads["conversao"].mean()
    cac_medio      = leads.loc[leads["conversao"], "CAC"].mean()
    cpl_medio      = leads["CPL"].mean()
    roi_medio_camp = campanhas["ROI"].mean()

    # Receita por categoria de curso
    rec_categoria = (
        mat.groupby("categoria")["valor_liquido"]
        .sum()
        .sort_values(ascending=False)
    )

    # Top 10 cursos por receita
    top_cursos_rec = (
        mat.groupby("curso_id")
        .agg(
            matriculas_qtd=("matricula_id", "count"),
            receita=("valor_liquido", "sum"),
        )
        .sort_values("receita", ascending=False)
        .head(10)
        .reset_index()
    )
    top_cursos_rec = top_cursos_rec.merge(
        tabelas["cursos"][["curso_id", "curso", "categoria", "area",
                            "taxa_evasao", "NPS"]],
        on="curso_id", how="left",
    )

    # Performance por canal de aquisição
    canais_aquis = (
        mat.groupby("canal_aquisicao")
        .agg(qtd=("matricula_id", "count"), receita=("valor_liquido", "sum"))
        .sort_values("receita", ascending=False)
        .reset_index()
    )
    canais_aquis["ticket_medio"] = canais_aquis["receita"] / canais_aquis["qtd"]

    # Performance de campanhas por canal de marketing
    camp_canal = (
        campanhas.groupby("canal")
        .agg(
            investimento=("orcamento", "sum"),
            leads_gerados=("leads_gerados", "sum"),
            conversoes=("conversoes", "sum"),
            roi_medio=("ROI", "mean"),
        )
        .reset_index()
    )
    camp_canal["cpl"]       = camp_canal["investimento"] / camp_canal["leads_gerados"]
    camp_canal["taxa_conv"] = camp_canal["conversoes"] / camp_canal["leads_gerados"]

    # Aging de inadimplência
    inad_copy = inad.copy()
    inad_copy["faixa"] = pd.cut(
        inad_copy["dias_em_atraso"],
        bins=[0, 30, 60, 90, 180, 9999],
        labels=["Até 30d", "31-60d", "61-90d", "91-180d", ">180d"],
    )
    aging_inad = (
        inad_copy.groupby("faixa", observed=True)
        .agg(valor=("valor_em_atraso", "sum"), qtd=("inadimplencia_id", "count"))
        .reset_index()
    )

    # Inadimplência mensal
    inad_mensal = (
        inad.groupby(inad["data_referencia"].dt.to_period("M"))["valor_em_atraso"]
        .sum()
        .reset_index()
    )
    inad_mensal.columns = ["periodo", "valor_inad"]
    inad_mensal["periodo_str"] = inad_mensal["periodo"].astype(str)

    # Motivos de cancelamento
    motivos_cancel = tabelas["cancelamentos"]["motivo"].value_counts().reset_index()
    motivos_cancel.columns = ["motivo", "quantidade"]

    return {
        "total_leads":     total_leads,
        "taxa_conversao":  taxa_conversao,
        "cac_medio":       cac_medio,
        "cpl_medio":       cpl_medio,
        "roi_medio_camp":  roi_medio_camp,
        "rec_categoria":   rec_categoria,
        "top_cursos_rec":  top_cursos_rec,
        "canais_aquis":    canais_aquis,
        "camp_canal":      camp_canal,
        "aging_inad":      aging_inad,
        "inad_mensal":     inad_mensal,
        "motivos_cancel":  motivos_cancel,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 4. ANÁLISE DE CORRELAÇÕES
# ─────────────────────────────────────────────────────────────────────────────

def calcular_correlacoes(tabelas: dict) -> pd.DataFrame:
    """Matriz de correlação entre indicadores acadêmicos e financeiros."""
    cols = [
        "valor_liquido", "nota_final", "presenca",
        "churn_risk", "lifetime_value", "bolsa_percentual", "desconto",
    ]
    mat = tabelas["matriculas"]
    colunas_ok = [c for c in cols if c in mat.columns]
    return mat[colunas_ok].corr()


# ─────────────────────────────────────────────────────────────────────────────
# 5. CONSOLIDAÇÃO GERAL
# ─────────────────────────────────────────────────────────────────────────────

def calcular_todos_kpis(tabelas: dict) -> dict:
    """
    Ponto de entrada único: calcula e retorna todos os KPIs em um só dict.
    Chamado por main.py.
    """
    fin  = kpis_financeiros(tabelas)
    acad = kpis_academicos(tabelas)
    com  = kpis_comerciais(tabelas)
    corr = calcular_correlacoes(tabelas)

    kpis = {**fin, **acad, **com, "corr_mat": corr}

    print(f"  ✓ Receita total:    R$ {kpis['receita_total']:,.0f}")
    print(f"  ✓ Ticket médio:     R$ {kpis['ticket_medio']:,.2f}")
    print(f"  ✓ Evasão: {kpis['taxa_evasao']:.1%} | "
          f"Retenção: {kpis['taxa_retencao']:.1%}")
    print(f"  ✓ Inadimplência: {kpis['taxa_inadimplencia']:.1%}")
    print(f"  ✓ NPS médio: {kpis['nps_medio']:.1f}")
    print(f"  ✓ Conversão leads: {kpis['taxa_conversao']:.1%}")

    return kpis
