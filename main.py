# =============================================================================
# MAIN.PY — Orquestrador Principal do Projeto
# Projeto de Análise de Dados | Educação Continuada
# =============================================================================
#
# FLUXO:
#   Excel (dados/) → PostgreSQL → Python (limpeza + KPIs) → outputs/ (CSVs)
#
# EXECUÇÃO:
#   python main.py --carga-inicial   (carrega Excel no PostgreSQL e executa)
#   python main.py                   (lê do PostgreSQL, fallback para Excel)
#
# SAÍDAS:
#   outputs/  → CSVs brutos + CSVs analíticos (separador ;)
#   SQL/      → 10 queries analíticas .sql
# =============================================================================

import sys
import warnings
warnings.filterwarnings("ignore")

from config import PROJETO, PASTA_OUT, PASTA_SQL

from carregamento import (carregar_excel, exportar_csvs_brutos,
                           carregar_para_postgres, ler_postgres, extrair_tabelas)
from limpeza      import limpar
from kpis         import calcular_todos_kpis
from queries_sql  import gerar_arquivos_sql
from exportacao   import exportar_resultados


def _cabecalho():
    print("=" * 70)
    print(f"  {PROJETO['nome'].upper()}")
    print(f"  {PROJETO['autor']}")
    print("=" * 70)


def _resumo_final(kpis: dict) -> None:
    print("\n[5/5] Pipeline concluído.")
    print("=" * 70)
    print("  RESUMO EXECUTIVO — EDUCAÇÃO CONTINUADA")
    print("=" * 70)
    print(f"  Receita Total:          R$ {kpis['receita_total']:>15,.0f}")
    print(f"  Receita Bruta:          R$ {kpis['receita_bruta']:>15,.0f}")
    print(f"  Ticket Médio:           R$ {kpis['ticket_medio']:>15,.2f}")
    print(f"  Valor Inadimplente:     R$ {kpis['valor_inad_total']:>15,.0f}")
    print(f"  Total Matrículas:           {kpis['total_matriculas']:>15,}")
    print(f"  Alunos Únicos:              {kpis['total_alunos']:>15,}")
    print(f"  Taxa de Conclusão:          {kpis['taxa_conclusao']:>14.1%}")
    print(f"  Taxa de Evasão:             {kpis['taxa_evasao']:>14.1%}")
    print(f"  Taxa de Retenção:           {kpis['taxa_retencao']:>14.1%}")
    print(f"  Taxa de Inadimplência:      {kpis['taxa_inadimplencia']:>14.1%}")
    print(f"  Taxa de Recompra:           {kpis['taxa_recompra']:>14.1%}")
    print(f"  NPS Médio:                  {kpis['nps_medio']:>14.1f}")
    print(f"  Satisfação Média:           {kpis['nota_satis']:>14.1f} / 100")
    print(f"  Total Leads:                {kpis['total_leads']:>15,}")
    print(f"  Conversão de Leads:         {kpis['taxa_conversao']:>14.1%}")
    print(f"  CAC Médio:              R$ {kpis['cac_medio']:>15,.2f}")
    print(f"  ROI Médio Campanhas:        {kpis['roi_medio_camp']:>14.2f}x")
    print(f"  Certificados Emitidos:      {kpis['cert_emitidos']:>15,}")
    print("=" * 70)
    print("\n  ARQUIVOS GERADOS:")
    print(f"  📁 outputs/  → {len(list(PASTA_OUT.glob('*.csv')))} CSVs")
    print(f"  📁 SQL/      → {len(list(PASTA_SQL.glob('*.sql')))} queries .sql")
    print("\n  Análise concluída com sucesso.")
    print("=" * 70)


# =============================================================================
# PIPELINE PRINCIPAL
# =============================================================================

def executar(carga_inicial: bool = False) -> None:
    _cabecalho()

    # ── [1/5] Carregamento ────────────────────────────────────────────────────
    print("\n[1/5] Carregando dados...")
    if carga_inicial:
        print("  Modo carga inicial: Excel → PostgreSQL")
        todas = carregar_excel()
        exportar_csvs_brutos(todas)
        carregar_para_postgres(todas)
        tabelas = extrair_tabelas(todas)
    else:
        print("  Lendo do PostgreSQL (fallback automático para Excel)")
        todas = ler_postgres()
        exportar_csvs_brutos(todas)
        tabelas = extrair_tabelas(todas)

    # ── [2/5] Limpeza ─────────────────────────────────────────────────────────
    print("\n[2/5] Limpeza e padronização...")
    limpar(tabelas)

    # ── [3/5] KPIs ────────────────────────────────────────────────────────────
    print("\n[3/5] Calculando KPIs estratégicos...")
    kpis = calcular_todos_kpis(tabelas)

    # ── [4/5] SQL ─────────────────────────────────────────────────────────────
    print("\n[4/5] Gerando queries SQL...")
    gerar_arquivos_sql()

    # ── [5/5] Exportação ──────────────────────────────────────────────────────
    print("\n[5/5] Exportando resultados...")
    exportar_resultados(tabelas, kpis)

    _resumo_final(kpis)


# =============================================================================
# ENTRADA
# =============================================================================

if __name__ == "__main__":
    carga_inicial = "--carga-inicial" in sys.argv
    executar(carga_inicial=carga_inicial)
