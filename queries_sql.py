# =============================================================================
# QUERIES_SQL.PY — Geração e Gravação de Queries SQL Analíticas
# Projeto de Análise de Dados | Educação Continuada
# =============================================================================
# As queries são escritas para PostgreSQL e documentam a lógica analítica
# aplicada ao banco de dados. Cada query é salva como arquivo .sql em SQL/.
# =============================================================================

from config import PASTA_SQL


# ─────────────────────────────────────────────────────────────────────────────
# DICIONÁRIO CENTRAL DE QUERIES
# ─────────────────────────────────────────────────────────────────────────────

QUERIES: dict[str, str] = {}

# ── 01 | Receita Total e Indicadores Financeiros Globais ──────────────────────
QUERIES["01_receita_total"] = """
-- ============================================================
-- QUERY 01 | RECEITA TOTAL E INDICADORES FINANCEIROS GLOBAIS
-- Objetivo: visão consolidada da performance financeira
-- ============================================================

SELECT
    COUNT(DISTINCT m.matricula_id)          AS total_matriculas,
    COUNT(DISTINCT m.aluno_id)              AS total_alunos,
    SUM(m.valor_bruto)                      AS receita_bruta,
    SUM(m.valor_liquido)                    AS receita_liquida,
    AVG(m.valor_liquido)                    AS ticket_medio,
    SUM(m.valor_bruto) - SUM(m.valor_liquido)
                                            AS total_descontos_bolsas,
    ROUND(
      (SUM(m.valor_bruto) - SUM(m.valor_liquido))
      / NULLIF(SUM(m.valor_bruto), 0) * 100, 2
    )                                       AS pct_desconto_medio

FROM matriculas m
WHERE m.status NOT IN ('Trancada');
"""

# ── 02 | Receita Mensal com Crescimento M/M ───────────────────────────────────
QUERIES["02_receita_mensal"] = """
-- ============================================================
-- QUERY 02 | RECEITA MENSAL COM CRESCIMENTO M/M
-- Objetivo: monitorar tendência de receita e sazonalidade
-- ============================================================

WITH receita_base AS (
    SELECT
        DATE_TRUNC('month', p.data_pagamento)   AS mes,
        SUM(p.valor_pago)                       AS receita_mes,
        COUNT(DISTINCT p.matricula_id)          AS matriculas_pagas
    FROM pagamentos p
    WHERE p.valor_pago > 0
      AND p.data_pagamento IS NOT NULL
    GROUP BY 1
),

crescimento AS (
    SELECT
        mes,
        receita_mes,
        matriculas_pagas,
        LAG(receita_mes) OVER (ORDER BY mes)    AS receita_mes_anterior,
        ROUND(
          (receita_mes - LAG(receita_mes) OVER (ORDER BY mes))
          / NULLIF(LAG(receita_mes) OVER (ORDER BY mes), 0) * 100, 2
        )                                       AS crescimento_pct
    FROM receita_base
)

SELECT
    TO_CHAR(mes, 'YYYY-MM')                     AS periodo,
    receita_mes,
    matriculas_pagas,
    receita_mes_anterior,
    crescimento_pct,
    SUM(receita_mes) OVER (
        ORDER BY mes ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                                           AS receita_acumulada
FROM crescimento
ORDER BY mes;
"""

# ── 03 | Ticket Médio por Categoria e Modalidade ─────────────────────────────
QUERIES["03_ticket_medio_categoria"] = """
-- ============================================================
-- QUERY 03 | TICKET MÉDIO POR CATEGORIA E MODALIDADE
-- Objetivo: análise de precificação e segmentação de produto
-- ============================================================

SELECT
    m.categoria,
    m.modalidade,
    COUNT(m.matricula_id)                   AS total_matriculas,
    ROUND(AVG(m.valor_bruto), 2)            AS preco_bruto_medio,
    ROUND(AVG(m.valor_liquido), 2)          AS ticket_medio_liquido,
    ROUND(AVG(m.bolsa_percentual), 1)       AS bolsa_media_pct,
    ROUND(AVG(m.desconto), 1)               AS desconto_medio,
    SUM(m.valor_liquido)                    AS receita_total_segmento,
    ROUND(
      SUM(m.valor_liquido) * 100.0 /
      SUM(SUM(m.valor_liquido)) OVER (), 2
    )                                       AS participacao_receita_pct
FROM matriculas m
GROUP BY m.categoria, m.modalidade
ORDER BY receita_total_segmento DESC;
"""

# ── 04 | Análise de Inadimplência (Aging) ────────────────────────────────────
QUERIES["04_inadimplencia"] = """
-- ============================================================
-- QUERY 04 | ANÁLISE DE INADIMPLÊNCIA (AGING)
-- Objetivo: dimensionar exposição financeira e perfil de risco
-- ============================================================

WITH base_inad AS (
    SELECT
        i.inadimplencia_id,
        i.aluno_id,
        i.curso_id,
        i.valor_em_atraso,
        i.dias_em_atraso,
        i.status_cobranca,
        m.categoria,
        m.modalidade,
        m.canal_aquisicao,
        CASE
            WHEN i.dias_em_atraso <= 30  THEN '01 - Até 30 dias'
            WHEN i.dias_em_atraso <= 60  THEN '02 - 31 a 60 dias'
            WHEN i.dias_em_atraso <= 90  THEN '03 - 61 a 90 dias'
            WHEN i.dias_em_atraso <= 180 THEN '04 - 91 a 180 dias'
            ELSE                              '05 - Acima de 180 dias'
        END AS faixa_aging
    FROM inadimplencia i
    JOIN matriculas m ON m.matricula_id = i.matricula_id
)

SELECT
    faixa_aging,
    COUNT(*)                            AS qtd_casos,
    SUM(valor_em_atraso)                AS valor_total,
    ROUND(AVG(valor_em_atraso), 2)      AS valor_medio,
    ROUND(AVG(dias_em_atraso), 1)       AS dias_medio,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2)
                                        AS participacao_casos_pct,
    ROUND(SUM(valor_em_atraso) * 100.0 /
          SUM(SUM(valor_em_atraso)) OVER (), 2)
                                        AS participacao_valor_pct
FROM base_inad
GROUP BY faixa_aging
ORDER BY faixa_aging;
"""

# ── 05 | Evasão e Retenção por Categoria/Canal ───────────────────────────────
QUERIES["05_evasao_retencao"] = """
-- ============================================================
-- QUERY 05 | EVASÃO E RETENÇÃO POR CATEGORIA / CANAL
-- Objetivo: identificar segmentos de maior risco de churn
-- ============================================================

WITH status_base AS (
    SELECT
        m.categoria,
        m.modalidade,
        m.canal_aquisicao,
        COUNT(*)                            AS total,
        SUM(CASE WHEN m.status = 'Concluída'            THEN 1 ELSE 0 END) AS concluidas,
        SUM(CASE WHEN m.status IN ('Cancelada','Evadida') THEN 1 ELSE 0 END) AS evasoes,
        SUM(CASE WHEN m.status = 'Ativa'                THEN 1 ELSE 0 END) AS ativas,
        ROUND(AVG(m.churn_risk), 1)         AS churn_risk_medio
    FROM matriculas m
    GROUP BY m.categoria, m.modalidade, m.canal_aquisicao
)

SELECT
    categoria, modalidade, canal_aquisicao,
    total, concluidas, evasoes, ativas,
    ROUND(concluidas * 100.0 / NULLIF(total, 0), 2) AS taxa_conclusao_pct,
    ROUND(evasoes   * 100.0 / NULLIF(total, 0), 2) AS taxa_evasao_pct,
    churn_risk_medio
FROM status_base
ORDER BY taxa_evasao_pct DESC;
"""

# ── 06 | Cursos Mais Vendidos e Rentáveis ────────────────────────────────────
QUERIES["06_cursos_mais_vendidos"] = """
-- ============================================================
-- QUERY 06 | CURSOS MAIS VENDIDOS E RENTÁVEIS
-- Objetivo: ranking de produtos por volume, receita e margem
-- ============================================================

SELECT
    c.curso_id, c.curso, c.categoria, c.area, c.modalidade,
    COUNT(m.matricula_id)               AS total_matriculas,
    SUM(m.valor_liquido)                AS receita_total,
    ROUND(AVG(m.valor_liquido), 2)      AS ticket_medio,
    ROUND(AVG(av.nota_satisfacao), 1)   AS satisfacao_media,
    ROUND(AVG(av.NPS), 1)               AS nps_medio,
    c.taxa_evasao, c.taxa_conclusao, c.margem_lucro, c.roi
FROM cursos c
LEFT JOIN matriculas m  ON m.curso_id = c.curso_id
LEFT JOIN avaliacoes av ON av.curso_id = c.curso_id
GROUP BY c.curso_id, c.curso, c.categoria, c.area, c.modalidade,
         c.taxa_evasao, c.taxa_conclusao, c.margem_lucro, c.roi
HAVING COUNT(m.matricula_id) > 0
ORDER BY receita_total DESC
LIMIT 20;
"""

# ── 07 | Funil de Conversão de Leads ─────────────────────────────────────────
QUERIES["07_conversao_leads"] = """
-- ============================================================
-- QUERY 07 | FUNIL DE CONVERSÃO DE LEADS
-- Objetivo: eficiência comercial por canal e temperatura de lead
-- ============================================================

WITH funil AS (
    SELECT
        l.canal, l.origem, l.temperatura_lead,
        COUNT(l.lead_id)                    AS total_leads,
        SUM(CASE WHEN l.conversao THEN 1 ELSE 0 END) AS leads_convertidos,
        ROUND(AVG(l.score_lead), 1)         AS score_medio,
        ROUND(AVG(l.tempo_resposta_min), 1) AS tempo_resposta_medio_min,
        ROUND(AVG(l.CPL), 2)                AS cpl_medio,
        ROUND(AVG(CASE WHEN l.conversao THEN l.CAC END), 2) AS cac_medio
    FROM leads l
    GROUP BY l.canal, l.origem, l.temperatura_lead
)

SELECT
    canal, origem, temperatura_lead,
    total_leads, leads_convertidos,
    ROUND(leads_convertidos * 100.0 / NULLIF(total_leads, 0), 2) AS taxa_conversao_pct,
    score_medio, tempo_resposta_medio_min, cpl_medio, cac_medio
FROM funil
ORDER BY leads_convertidos DESC;
"""

# ── 08 | Crescimento Mensal de Matrículas (YoY / MoM) ────────────────────────
QUERIES["08_crescimento_mensal"] = """
-- ============================================================
-- QUERY 08 | CRESCIMENTO MENSAL DE MATRÍCULAS (YoY / MoM)
-- Objetivo: análise de tendência e sazonalidade
-- ============================================================

WITH base AS (
    SELECT
        EXTRACT(YEAR  FROM data_matricula) AS ano,
        EXTRACT(MONTH FROM data_matricula) AS mes,
        COUNT(*)                           AS matriculas,
        SUM(valor_liquido)                 AS receita
    FROM matriculas
    WHERE data_matricula IS NOT NULL
    GROUP BY 1, 2
),
com_anterior AS (
    SELECT
        ano, mes, matriculas, receita,
        LAG(matriculas)     OVER (ORDER BY ano, mes) AS mat_mes_ant,
        LAG(matriculas, 12) OVER (ORDER BY ano, mes) AS mat_ano_ant
    FROM base
)

SELECT
    ano, mes, matriculas, receita,
    ROUND((matriculas - mat_mes_ant) * 100.0 / NULLIF(mat_mes_ant, 0), 2) AS crescimento_mom_pct,
    ROUND((matriculas - mat_ano_ant) * 100.0 / NULLIF(mat_ano_ant, 0), 2) AS crescimento_yoy_pct
FROM com_anterior
ORDER BY ano, mes;
"""

# ── 09 | Satisfação, NPS e Qualidade por Curso ───────────────────────────────
QUERIES["09_satisfacao_nps"] = """
-- ============================================================
-- QUERY 09 | SATISFAÇÃO, NPS E QUALIDADE POR CURSO
-- Objetivo: monitorar experiência do aluno e reputação acadêmica
-- ============================================================

WITH notas AS (
    SELECT
        av.curso_id, c.curso, c.categoria,
        COUNT(av.avaliacao_id)              AS total_avaliacoes,
        ROUND(AVG(av.nota_satisfacao), 1)   AS satisfacao_media,
        ROUND(AVG(av.nota_professor), 1)    AS nota_professor,
        ROUND(AVG(av.nota_plataforma), 1)   AS nota_plataforma,
        ROUND(AVG(av.NPS), 1)               AS nps_medio,
        SUM(CASE WHEN av.NPS >= 70           THEN 1 ELSE 0 END) AS promotores,
        SUM(CASE WHEN av.NPS BETWEEN 50 AND 69 THEN 1 ELSE 0 END) AS neutros,
        SUM(CASE WHEN av.NPS < 50            THEN 1 ELSE 0 END) AS detratores,
        SUM(CASE WHEN av.recomendaria THEN 1 ELSE 0 END) AS recomendaria_qtd,
        ROUND(AVG(av.tempo_resposta_suporte_h), 1) AS tempo_suporte_h_medio
    FROM avaliacoes av
    JOIN cursos c ON c.curso_id = av.curso_id
    GROUP BY av.curso_id, c.curso, c.categoria
)

SELECT
    curso_id, curso, categoria, total_avaliacoes,
    satisfacao_media, nota_professor, nota_plataforma, nps_medio,
    ROUND(promotores  * 100.0 / NULLIF(total_avaliacoes, 0), 1) AS pct_promotores,
    ROUND(neutros     * 100.0 / NULLIF(total_avaliacoes, 0), 1) AS pct_neutros,
    ROUND(detratores  * 100.0 / NULLIF(total_avaliacoes, 0), 1) AS pct_detratores,
    ROUND(recomendaria_qtd * 100.0 / NULLIF(total_avaliacoes, 0), 1) AS pct_recomendaria,
    tempo_suporte_h_medio
FROM notas
ORDER BY nps_medio DESC;
"""

# ── 10 | Painel Completo de Matrículas ───────────────────────────────────────
QUERIES["10_total_matriculas"] = """
-- ============================================================
-- QUERY 10 | PAINEL COMPLETO DE MATRÍCULAS
-- Objetivo: visão 360° do portfólio de alunos matriculados
-- ============================================================

SELECT
    m.status, m.categoria, m.modalidade,
    COUNT(m.matricula_id)                   AS total_matriculas,
    COUNT(DISTINCT m.aluno_id)              AS alunos_unicos,
    ROUND(AVG(m.nota_final), 1)             AS nota_media,
    ROUND(AVG(m.presenca) * 100, 1)         AS presenca_media_pct,
    ROUND(AVG(m.churn_risk), 1)             AS risco_churn_medio,
    SUM(CASE WHEN m.recompra THEN 1 ELSE 0 END)   AS qtd_recompras,
    ROUND(
      SUM(CASE WHEN m.recompra THEN 1 ELSE 0 END) * 100.0
      / NULLIF(COUNT(*), 0), 2
    )                                       AS taxa_recompra_pct,
    SUM(CASE WHEN m.inadimplente THEN 1 ELSE 0 END) AS qtd_inadimplentes,
    SUM(m.valor_liquido)                    AS receita_total
FROM matriculas m
GROUP BY m.status, m.categoria, m.modalidade
ORDER BY total_matriculas DESC;
"""


# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÃO DE EXPORTAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

def gerar_arquivos_sql() -> None:
    """Grava cada query como arquivo .sql em SQL/."""
    for nome, sql in QUERIES.items():
        caminho = PASTA_SQL / f"{nome}.sql"
        caminho.write_text(sql.strip(), encoding="utf-8")
    print(f"  ✓ {len(QUERIES)} queries SQL geradas em SQL/")
