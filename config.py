# =============================================================================
# CONFIG.PY — Configurações Centralizadas do Projeto
# Projeto de Análise de Dados | Educação Continuada
# =============================================================================

from pathlib import Path

# ─── Pastas do projeto ────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent
PASTA_DADOS = BASE_DIR / "dados"      # ← coloque o Excel aqui
PASTA_OUT   = BASE_DIR / "outputs"    # ← todos os resultados gerados
PASTA_SQL   = BASE_DIR / "SQL"        # ← queries .sql geradas

for pasta in [PASTA_DADOS, PASTA_OUT, PASTA_SQL]:
    pasta.mkdir(parents=True, exist_ok=True)

# ─── Arquivo-base ─────────────────────────────────────────────────────────────
# Coloque o Excel dentro da pasta dados/ e ajuste o nome abaixo se necessário.
ARQUIVO_BASE = PASTA_DADOS / "base_educacao_continuada_COMPLETA.xlsx"

# ─── PostgreSQL ───────────────────────────────────────────────────────────────
PG_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "database": "educacao_continuada",
    "user":     "postgres",
    "password": "torterra",   # !! ajuste !!
}

PG_URL = (
    f"postgresql+psycopg2://{PG_CONFIG['user']}:{PG_CONFIG['password']}"
    f"@{PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['database']}"
)

# ─── Separador CSV ────────────────────────────────────────────────────────────
CSV_SEP = ";"

# ─── Período analítico ────────────────────────────────────────────────────────
ANOS_HISTORICO = ["2022", "2023", "2024", "2025"]

# ─── Metadados do projeto ─────────────────────────────────────────────────────
PROJETO = {
    "nome":    "Educação Continuada — Analytics Pipeline",
    "periodo": "2022–2025",
    "autor":   "Setor de Analytics | Educação Continuada",
}
