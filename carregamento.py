# =============================================================================
# CARREGAMENTO.PY — Carregamento de Dados
# Projeto de Análise de Dados | Educação Continuada
# =============================================================================
# Fluxo: Excel (dados/) → PostgreSQL → Python
# =============================================================================

import pandas as pd
from pathlib import Path

try:
    from sqlalchemy import create_engine, text
    SQLALCHEMY_OK = True
except ImportError:
    SQLALCHEMY_OK = False

from config import ARQUIVO_BASE, PASTA_OUT, PG_URL, CSV_SEP


# ─────────────────────────────────────────────────────────────────────────────
# 1. LEITURA DO EXCEL (carga inicial / fallback)
# ─────────────────────────────────────────────────────────────────────────────

def carregar_excel(caminho: Path = ARQUIVO_BASE) -> dict[str, pd.DataFrame]:
    """Lê todas as abas do Excel em dados/ e retorna dict {nome_aba: DataFrame}."""
    if not caminho.exists():
        raise FileNotFoundError(
            f"\n  Arquivo não encontrado: {caminho}\n"
            f"  Coloque o Excel dentro da pasta dados/ e tente novamente."
        )
    print(f"  Lendo Excel: {caminho.name}")
    todas = pd.read_excel(caminho, sheet_name=None)
    print(f"  ✓ {len(todas)} abas carregadas")
    return todas


def exportar_csvs_brutos(todas: dict[str, pd.DataFrame]) -> None:
    """Exporta cada aba como CSV em outputs/."""
    for nome, df in todas.items():
        df.to_csv(PASTA_OUT / f"{nome}.csv", index=False, sep=CSV_SEP, encoding="utf-8-sig")
    print(f"  ✓ {len(todas)} CSVs exportados para outputs/")


# ─────────────────────────────────────────────────────────────────────────────
# 2. CARGA NO POSTGRESQL (ETL inicial)
# ─────────────────────────────────────────────────────────────────────────────

def carregar_para_postgres(todas: dict[str, pd.DataFrame]) -> None:
    """
    Envia cada DataFrame como tabela no PostgreSQL.
    Modo: replace — recria a tabela a cada carga.
    """
    if not SQLALCHEMY_OK:
        print("  ⚠ SQLAlchemy não instalado. Pulando carga no PostgreSQL.")
        return

    engine = create_engine(PG_URL)
    for nome, df in todas.items():
        df.to_sql(nome, engine, if_exists="replace", index=False)
        print(f"    → tabela '{nome}' carregada ({len(df):,} linhas)")
    print(f"  ✓ {len(todas)} tabelas enviadas ao PostgreSQL")


# ─────────────────────────────────────────────────────────────────────────────
# 3. LEITURA DO POSTGRESQL (fluxo principal)
# ─────────────────────────────────────────────────────────────────────────────

TABELAS = [
    "alunos", "matriculas", "pagamentos", "cursos", "leads",
    "campanhas_marketing", "cancelamentos", "inadimplencia",
    "avaliacoes", "certificados", "acessos_plataforma",
    "crm_comercial", "professores", "suporte",
    "trilhas_aprendizado", "empresas_clientes",
]


def ler_postgres(tabelas: list[str] = TABELAS) -> dict[str, pd.DataFrame]:
    """
    Lê as tabelas do PostgreSQL.
    Se o banco estiver vazio, faz a carga inicial automaticamente.
    Fallback automático para Excel se o banco não estiver acessível.
    """
    if not SQLALCHEMY_OK:
        print("  ⚠ SQLAlchemy não instalado. Usando fallback Excel.")
        return carregar_excel()

    engine = create_engine(PG_URL)
    dados = {}
    try:
        with engine.connect() as conn:
            for tabela in tabelas:
                df = pd.read_sql(text(f"SELECT * FROM {tabela}"), conn)
                dados[tabela] = df
        print(f"  ✓ {len(dados)} tabelas lidas do PostgreSQL")
    except Exception:
        print("  Banco vazio ou tabelas não encontradas.")
        print("  → Fazendo carga inicial automaticamente...")
        dados = carregar_excel()
        exportar_csvs_brutos(dados)
        carregar_para_postgres(dados)
        print("  ✓ Carga inicial concluída.")

    return dados


# ─────────────────────────────────────────────────────────────────────────────
# 4. EXTRAÇÃO DOS DataFrames INDIVIDUAIS
# ─────────────────────────────────────────────────────────────────────────────

def extrair_tabelas(dados: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Retorna as tabelas com nomes padronizados para o restante do pipeline."""
    return {
        "alunos":        dados.get("alunos",               pd.DataFrame()),
        "matriculas":    dados.get("matriculas",            pd.DataFrame()),
        "pagamentos":    dados.get("pagamentos",            pd.DataFrame()),
        "cursos":        dados.get("cursos",                pd.DataFrame()),
        "leads":         dados.get("leads",                 pd.DataFrame()),
        "campanhas":     dados.get("campanhas_marketing",   pd.DataFrame()),
        "cancelamentos": dados.get("cancelamentos",         pd.DataFrame()),
        "inadimplencia": dados.get("inadimplencia",         pd.DataFrame()),
        "avaliacoes":    dados.get("avaliacoes",            pd.DataFrame()),
        "certificados":  dados.get("certificados",          pd.DataFrame()),
        "acessos":       dados.get("acessos_plataforma",    pd.DataFrame()),
        "crm":           dados.get("crm_comercial",         pd.DataFrame()),
        "professores":   dados.get("professores",           pd.DataFrame()),
        "suporte":       dados.get("suporte",               pd.DataFrame()),
        "trilhas":       dados.get("trilhas_aprendizado",   pd.DataFrame()),
        "empresas":      dados.get("empresas_clientes",     pd.DataFrame()),
    }