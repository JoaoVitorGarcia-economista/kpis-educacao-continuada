# 📊 Dashboard — Educação Continuada

Dashboard analítico desenvolvido em Python para monitoramento de KPIs acadêmicos, financeiros e comerciais de uma instituição de educação continuada.

## 🔗 Acesso
[Abrir dashboard](https://seuapp.streamlit.app)

---

## 📈 Principais KPIs monitorados

| Indicador | Valor |
|---|---|
| Receita Total | R$ 341,3M |
| Receita Bruta | R$ 431,7M |
| Ticket Médio | R$ 14.265 |
| Matrículas | 28.000 |
| Alunos Únicos | 12.000 |
| Taxa de Conclusão | 66,3% |
| Taxa de Evasão | 26,5% |
| Taxa de Recompra | 30,1% |
| NPS Médio | 79,0 |
| Certificados Emitidos | 18.569 |
| ROI Médio Campanhas | 2,37x |
| CAC Médio | R$ 785 |

---

## 📋 Glossário rápido

- **NPS** — nota de 0 a 100 que mede se o aluno recomendaria a instituição. Acima de 70 é excelente.
- **ROI** — retorno sobre o investimento. ROI de 2,93x = cada R$1 investido retornou R$2,93.
- **CAC** — custo médio para conquistar um novo aluno.
- **CPL** — custo para gerar um lead (contato interessado) antes de virar aluno.
- **Ticket Médio** — valor médio pago por matrícula.
- **Evasão** — % de alunos que abandonaram o curso antes de concluir.
- **Recompra** — % de alunos que fizeram mais de um curso na instituição.
- **Aging** — classificação das dívidas por tempo de atraso (30, 60, 90 dias). Quanto mais velho, menor a chance de receber.
- **Cohort** — análise de grupos de alunos por período de matrícula para acompanhar comportamento ao longo do tempo.

---

## 🖥️ Páginas do Dashboard

- **Visão Geral** — KPIs consolidados, gauges de qualidade e alertas automáticos
- **Financeiro** — Receita mensal com média móvel 3m, cohort trimestral, ticket médio, receita por categoria e modalidade
- **Acadêmico** — Evasão e conclusão por modalidade/categoria, NPS, satisfação, nota professor vs plataforma
- **Marketing** — ROI por canal, funil de leads, tabela completa com CAC e CPL
- **Inadimplência** — Aging por faixa de atraso, distribuição de risco e alertas de ação
- **Ranking de Cursos** — Top cursos por NPS, ROI e evasão

---

## 🗂️ Estrutura do Projeto

```
educacao_continuada/
├── dashboard.py          # Interface principal (Streamlit)
├── requirements.txt      # Dependências
├── .streamlit/
│   └── config.toml
└── outputs/              # CSVs processados pelo pipeline
    ├── 01_receita_mensal.csv
    ├── 02_kpis_gerais.csv
    ├── 03_evasao.csv
    ├── 04_marketing.csv
    ├── 05_cursos.csv
    ├── 06_matriculas_tratadas.csv
    ├── 07_inadimplencia_aging.csv
    ├── 08_leads_funil.csv
    ├── 09_cohort_trimestral.csv
    └── 10_avaliacoes_nps.csv
```

> Para atualizar os dados, rode o pipeline principal (`python main.py`) e substitua os arquivos da pasta `outputs/`.

---

## 🛠️ Stack

- **Python 3.11+**
- **Streamlit** — interface web
- **Plotly** — visualizações interativas
- **Pandas** — processamento de dados
- **PostgreSQL** — banco de dados (com fallback para leitura direta do Excel)
