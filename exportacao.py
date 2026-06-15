# =============================================================================
# EXPORTACAO.PY — Resultados Analíticos
# Projeto de Análise de Dados | Educação Continuada
# =============================================================================
# Gera os CSVs analíticos em outputs/ com separador ; (Excel brasileiro).
#
#   01_receita_mensal.csv        — série temporal de receita
#   02_kpis_gerais.csv           — KPIs estratégicos consolidados
#   03_evasao.csv                — evasão por categoria, modalidade e canal
#   04_marketing.csv             — performance por canal de marketing
#   05_cursos.csv                — tabela analítica de cursos
#   06_matriculas_tratadas.csv   — base principal tratada
#   07_inadimplencia_aging.csv   — aging de inadimplência por faixa de atraso
#   08_leads_funil.csv           — funil de leads com métricas de conversão
#   09_cohort_trimestral.csv     — análise de cohort trimestral
#   10_avaliacoes_nps.csv        — NPS e notas de satisfação
# =============================================================================

import pandas as pd
from pathlib import Path

from config import PASTA_OUT, CSV_SEP


def exportar_resultados(tabelas: dict, kpis: dict) -> None:
    """Gera os 10 CSVs analíticos em outputs/."""
    out = PASTA_OUT

    # ── 01. receita_mensal.csv ────────────────────────────────────────────────
    rec = kpis["rec_mensal"].copy()
    rec["periodo"] = rec["periodo"].astype(str)
    rec.to_csv(out / "01_receita_mensal.csv", index=False, sep=CSV_SEP, encoding="utf-8-sig")

    # ── 02. kpis_gerais.csv ───────────────────────────────────────────────────
    kpis_df = pd.DataFrame([{
        "receita_total":      kpis["receita_total"],
        "receita_bruta":      kpis["receita_bruta"],
        "ticket_medio":       kpis["ticket_medio"],
        "valor_inad_total":   kpis["valor_inad_total"],
        "total_matriculas":   kpis["total_matriculas"],
        "total_alunos":       kpis["total_alunos"],
        "taxa_evasao":        kpis["taxa_evasao"],
        "taxa_retencao":      kpis["taxa_retencao"],
        "taxa_conclusao":     kpis["taxa_conclusao"],
        "taxa_inadimplencia": kpis["taxa_inadimplencia"],
        "taxa_recompra":      kpis["taxa_recompra"],
        "nps_medio":          kpis["nps_medio"],
        "nota_satis":         kpis["nota_satis"],
        "nota_prof":          kpis["nota_prof"],
        "nota_plat":          kpis["nota_plat"],
        "cert_emitidos":      kpis["cert_emitidos"],
        "total_leads":        kpis["total_leads"],
        "taxa_conversao":     kpis["taxa_conversao"],
        "cac_medio":          kpis["cac_medio"],
        "cpl_medio":          kpis["cpl_medio"],
        "roi_medio_camp":     kpis["roi_medio_camp"],
    }])
    kpis_df.to_csv(out / "02_kpis_gerais.csv", index=False, sep=CSV_SEP, encoding="utf-8-sig")

    # ── 03. evasao.csv ────────────────────────────────────────────────────────
    mat = tabelas["matriculas"]
    evasao = (
        mat.groupby(["categoria", "modalidade", "canal_aquisicao"])
        .agg(
            total=(           "matricula_id", "count"),
            concluidas=(      "matricula_id", lambda x:
                (mat.loc[x.index, "status"] == "Concluída").sum()),
            evasoes=(         "matricula_id", lambda x:
                mat.loc[x.index, "status"].isin(["Cancelada", "Evadida"]).sum()),
            churn_risk_medio=("churn_risk",   "mean"),
            receita=(         "valor_liquido", "sum"),
        )
        .reset_index()
    )
    evasao["taxa_evasao"]    = evasao["evasoes"]    / evasao["total"]
    evasao["taxa_conclusao"] = evasao["concluidas"] / evasao["total"]
    evasao.to_csv(out / "03_evasao.csv", index=False, sep=CSV_SEP, encoding="utf-8-sig")

    # ── 04. marketing.csv ─────────────────────────────────────────────────────
    kpis["camp_canal"].to_csv(out / "04_marketing.csv", index=False, sep=CSV_SEP, encoding="utf-8-sig")

    # ── 05. cursos.csv ────────────────────────────────────────────────────────
    tabelas["cursos"].copy().to_csv(out / "05_cursos.csv", index=False, sep=CSV_SEP, encoding="utf-8-sig")

    # ── 06. matriculas_tratadas.csv ───────────────────────────────────────────
    cols = [
        "matricula_id", "aluno_id", "curso_id", "data_matricula",
        "status", "canal_aquisicao", "categoria", "modalidade",
        "valor_bruto", "valor_liquido", "bolsa_percentual", "desconto",
        "nota_final", "presenca", "recompra", "inadimplente",
        "churn_risk", "lifetime_value", "ano", "mes", "ano_mes", "trimestre",
    ]
    cols_ok = [c for c in cols if c in mat.columns]
    mat_out = mat[cols_ok].copy()
    mat_out["ano_mes"] = mat_out["ano_mes"].astype(str)
    mat_out.to_csv(out / "06_matriculas_tratadas.csv", index=False, sep=CSV_SEP, encoding="utf-8-sig")

    # ── 07. inadimplencia_aging.csv ───────────────────────────────────────────
    kpis["aging_inad"].to_csv(out / "07_inadimplencia_aging.csv", index=False, sep=CSV_SEP, encoding="utf-8-sig")

    # ── 08. leads_funil.csv ───────────────────────────────────────────────────
    tabelas["leads"].to_csv(out / "08_leads_funil.csv", index=False, sep=CSV_SEP, encoding="utf-8-sig")

    # ── 09. cohort_trimestral.csv ─────────────────────────────────────────────
    kpis["cohort_hist"].copy().to_csv(out / "09_cohort_trimestral.csv", index=False, sep=CSV_SEP, encoding="utf-8-sig")

    # ── 10. avaliacoes_nps.csv ────────────────────────────────────────────────
    tabelas["avaliacoes"].to_csv(out / "10_avaliacoes_nps.csv", index=False, sep=CSV_SEP, encoding="utf-8-sig")

    n = len(list(out.glob("*.csv")))
    print(f"  ✓ {n} CSVs exportados para outputs/")
    _listar_outputs(out)


def _listar_outputs(out: Path) -> None:
    print("\n  RESULTADOS GERADOS:")
    print("  " + "─" * 40)
    for arq in sorted(out.glob("*.csv")):
        print(f"  📄 {arq.name}")
    print("  " + "─" * 40)
