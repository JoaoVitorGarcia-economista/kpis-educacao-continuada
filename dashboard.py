import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import numpy as np

# ─── CONFIG ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Educação Continuada | Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* ── fundo ── */
  .stApp { background-color: #080c14; }

  /* ── sidebar ── */
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1520 0%, #080c14 100%);
    border-right: 1px solid #162032;
  }
  section[data-testid="stSidebar"] * { color: #94a3b8 !important; }

  .sidebar-logo {
    font-size: 1.25rem; font-weight: 800; color: #38bdf8 !important;
    letter-spacing: 0.04em; margin-bottom: 0.15rem;
  }
  .sidebar-sub {
    font-size: 0.7rem; color: #334155 !important;
    margin-bottom: 1.2rem; text-transform: uppercase; letter-spacing: 0.08em;
  }
  .sidebar-section {
    font-size: 0.65rem; font-weight: 700; color: #334155 !important;
    text-transform: uppercase; letter-spacing: 0.12em;
    margin: 1.2rem 0 0.5rem 0;
  }

  /* ── KPI cards ── */
  .kpi-card {
    background: linear-gradient(135deg, #0d1a2d 0%, #0a1422 100%);
    border: 1px solid #162032;
    border-radius: 16px;
    padding: 1.25rem 1.4rem 1rem 1.4rem;
    position: relative;
    overflow: hidden;
    transition: all 0.2s ease;
    margin-bottom: 0.5rem;
  }
  .kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 16px 16px 0 0;
  }
  .kpi-card.blue::before  { background: linear-gradient(90deg, #38bdf8, #0ea5e9); }
  .kpi-card.green::before { background: linear-gradient(90deg, #34d399, #10b981); }
  .kpi-card.red::before   { background: linear-gradient(90deg, #f87171, #ef4444); }
  .kpi-card.yellow::before{ background: linear-gradient(90deg, #fbbf24, #f59e0b); }
  .kpi-card.purple::before{ background: linear-gradient(90deg, #a78bfa, #8b5cf6); }
  .kpi-card.pink::before  { background: linear-gradient(90deg, #f472b6, #ec4899); }

  .kpi-card:hover {
    border-color: #1e3a5f;
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(14,165,233,0.12);
  }
  .kpi-icon  { font-size: 1.5rem; float: right; opacity: 0.5; margin-top: -0.1rem; }
  .kpi-label { font-size: 0.68rem; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; }
  .kpi-value { font-size: 1.75rem; font-weight: 800; color: #f1f5f9; line-height: 1; }
  .kpi-sub   { font-size: 0.72rem; color: #475569; margin-top: 0.45rem; font-weight: 500; }
  .kpi-sub.up   { color: #34d399; }
  .kpi-sub.down { color: #f87171; }
  .kpi-sub.warn { color: #fbbf24; }

  /* ── page header ── */
  .page-header {
    background: linear-gradient(135deg, #0d1a2d 0%, #080c14 60%, #0a0f1a 100%);
    border: 1px solid #162032;
    border-radius: 18px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  .page-header-icon { font-size: 2.2rem; }
  .page-header h1   { font-size: 1.5rem; font-weight: 800; color: #f1f5f9; margin: 0 0 0.25rem 0; }
  .page-header p    { font-size: 0.8rem; color: #475569; margin: 0; }

  /* ── section label ── */
  .section-label {
    font-size: 0.68rem; font-weight: 700; color: #38bdf8;
    text-transform: uppercase; letter-spacing: 0.12em;
    border-left: 3px solid #38bdf8; padding-left: 0.7rem;
    margin: 1.6rem 0 0.9rem 0;
  }

  /* ── insight box ── */
  .insight {
    border-radius: 12px; padding: 0.85rem 1.1rem;
    margin-bottom: 0.75rem; font-size: 0.8rem; line-height: 1.6;
    border-left-width: 4px; border-left-style: solid;
  }
  .insight.green  { background: #052e16; border-color: #34d399; color: #6ee7b7; }
  .insight.red    { background: #1a0808; border-color: #f87171; color: #fca5a5; }
  .insight.yellow { background: #1a1200; border-color: #fbbf24; color: #fde68a; }
  .insight.blue   { background: #0a1929; border-color: #38bdf8; color: #7dd3fc; }

  /* ── gauge label ── */
  .gauge-wrap { text-align: center; }
  .gauge-label { font-size: 0.7rem; color: #475569; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.3rem; }

  /* ── ranking table ── */
  .rank-row {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.55rem 0.75rem; border-radius: 10px;
    margin-bottom: 0.35rem; background: #0d1a2d;
    border: 1px solid #162032;
  }
  .rank-num  { font-size: 0.7rem; color: #334155; font-weight: 700; width: 1.2rem; text-align: center; }
  .rank-name { font-size: 0.8rem; color: #cbd5e1; flex: 1; font-weight: 500; }
  .rank-val  { font-size: 0.8rem; color: #38bdf8; font-weight: 700; }
  .rank-bar-wrap { width: 80px; height: 5px; background: #162032; border-radius: 3px; }
  .rank-bar      { height: 5px; border-radius: 3px; background: linear-gradient(90deg, #38bdf8, #0ea5e9); }

  /* ── misc ── */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.4rem; padding-bottom: 1rem; }
  .stDataFrame { background: #0d1a2d !important; border-radius: 12px; }
  div[data-testid="stMetric"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTES ──────────────────────────────────────────────────────────────
OUTPUTS = Path(__file__).resolve().parent.parent / "outputs"

C = {
    "blue":   "#38bdf8",
    "green":  "#34d399",
    "yellow": "#fbbf24",
    "red":    "#f87171",
    "purple": "#a78bfa",
    "pink":   "#f472b6",
    "teal":   "#2dd4bf",
    "orange": "#fb923c",
    "bg":     "#080c14",
    "card":   "#0d1a2d",
    "border": "#162032",
    "text":   "#f1f5f9",
    "muted":  "#475569",
}
SEQ = [C["blue"], C["green"], C["yellow"], C["red"], C["purple"], C["pink"], C["teal"], C["orange"]]

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=C["text"], family="Inter", size=12),
    margin=dict(l=8, r=8, t=36, b=8),
    xaxis=dict(gridcolor="#0d1a2d", linecolor=C["border"],
               tickfont_size=11, title_font_size=11),
    yaxis=dict(gridcolor="#0d1a2d", linecolor=C["border"],
               tickfont_size=11, title_font_size=11),
)

LEGEND = dict(bgcolor="rgba(13,26,45,0.9)", bordercolor=C["border"],
              borderwidth=1, font_size=11)

# ─── FUNÇÕES AUXILIARES ──────────────────────────────────────────────────────
@st.cache_data
def load(fn):
    p = OUTPUTS / fn
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, sep=";", encoding="utf-8-sig")

def fmt_brl(v):
    if v >= 1_000_000: return f"R$ {v/1_000_000:.1f}M"
    if v >= 1_000:     return f"R$ {v/1_000:.0f}K"
    return f"R$ {v:,.0f}"

def fmt_pct(v):  return f"{v*100:.1f}%"
def fmt_n(v):    return f"{int(v):,}"

def kpi(label, value, sub=None, sub_type="", color="blue", icon=""):
    sub_html = f'<div class="kpi-sub {sub_type}">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="kpi-card {color}">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {sub_html}
    </div>""", unsafe_allow_html=True)

def section(t): st.markdown(f'<div class="section-label">{t}</div>', unsafe_allow_html=True)

def header(icon, title, sub):
    st.markdown(f"""
    <div class="page-header">
      <div class="page-header-icon">{icon}</div>
      <div>
        <h1>{title}</h1>
        <p>{sub}</p>
      </div>
    </div>""", unsafe_allow_html=True)

def insight(text, kind="blue"):
    icons = {"green": "✔", "red": "⚠", "yellow": "💡", "blue": "→"}
    st.markdown(f'<div class="insight {kind}">{icons[kind]}  {text}</div>',
                unsafe_allow_html=True)

def gauge(value, title, min_=0, max_=100, thresholds=None, fmt="{:.1f}"):
    if thresholds is None: thresholds = [33, 66]
    color = C["red"] if value < thresholds[0] else (C["yellow"] if value < thresholds[1] else C["green"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(suffix="", font=dict(size=28, color=C["text"], family="Inter")),
        gauge=dict(
            axis=dict(range=[min_, max_], tickcolor=C["muted"], tickfont_size=10),
            bar=dict(color=color, thickness=0.7),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            steps=[
                dict(range=[min_, thresholds[0]], color="#1a0808"),
                dict(range=[thresholds[0], thresholds[1]], color="#1a1200"),
                dict(range=[thresholds[1], max_], color="#052e16"),
            ],
        ),
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color=C["text"],
                      font_family="Inter", height=180,
                      margin=dict(l=20, r=20, t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f'<div class="gauge-wrap"><div class="gauge-label">{title}</div></div>',
                unsafe_allow_html=True)

def ranking_html(rows, max_val):
    html = ""
    for i, (name, val, val_fmt) in enumerate(rows, 1):
        pct = int((val / max_val) * 100) if max_val else 0
        html += f"""
        <div class="rank-row">
          <div class="rank-num">{i}</div>
          <div class="rank-name">{name}</div>
          <div class="rank-bar-wrap"><div class="rank-bar" style="width:{pct}%"></div></div>
          <div class="rank-val">{val_fmt}</div>
        </div>"""
    st.markdown(html, unsafe_allow_html=True)

# ─── CARREGAMENTO ────────────────────────────────────────────────────────────
kpis      = load("02_kpis_gerais.csv")
receita   = load("01_receita_mensal.csv")
evasao    = load("03_evasao.csv")
marketing = load("04_marketing.csv")
cursos    = load("05_cursos.csv")
mats      = load("06_matriculas_tratadas.csv")
aging     = load("07_inadimplencia_aging.csv")
leads     = load("08_leads_funil.csv")
cohort    = load("09_cohort_trimestral.csv")
aval      = load("10_avaliacoes_nps.csv")

if kpis.empty:
    st.error("⚠ Pasta outputs/ não encontrada ou vazia. Rode o pipeline primeiro: **python main.py**")
    st.stop()

K = kpis.iloc[0]

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">📊 EDUCAÇÃO CONT.</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Analytics Dashboard · 2022–2025</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">Navegação</div>', unsafe_allow_html=True)
    page = st.radio("", [
        "🏠  Visão Geral",
        "💰  Financeiro",
        "🎓  Acadêmico",
        "📣  Marketing",
        "⚠️  Inadimplência",
        "🏆  Ranking Cursos",
        "🔍  Explorar",
    ], label_visibility="collapsed")

    st.divider()
    st.markdown('<div class="sidebar-section">Filtros</div>', unsafe_allow_html=True)

    anos_d = sorted(mats["ano"].dropna().unique().tolist()) if not mats.empty and "ano" in mats.columns else []
    anos_s = st.multiselect("Ano", anos_d, default=anos_d, label_visibility="collapsed",
                             placeholder="Todos os anos")

    cats_d = sorted(mats["categoria"].dropna().unique().tolist()) if not mats.empty and "categoria" in mats.columns else []
    cats_s = st.multiselect("Categoria", cats_d, default=cats_d, label_visibility="collapsed",
                             placeholder="Todas as categorias")

    mods_d = sorted(mats["modalidade"].dropna().unique().tolist()) if not mats.empty and "modalidade" in mats.columns else []
    mods_s = st.multiselect("Modalidade", mods_d, default=mods_d, label_visibility="collapsed",
                             placeholder="Todas as modalidades")

    canais_d = sorted(mats["canal_aquisicao"].dropna().unique().tolist()) if not mats.empty and "canal_aquisicao" in mats.columns else []
    canais_s = st.multiselect("Canal", canais_d, default=canais_d, label_visibility="collapsed",
                               placeholder="Todos os canais")

    st.divider()
    total_f = len(mats)
    if not mats.empty:
        mf = mats.copy()
        if anos_s   and "ano"            in mf.columns: mf = mf[mf["ano"].isin(anos_s)]
        if cats_s   and "categoria"      in mf.columns: mf = mf[mf["categoria"].isin(cats_s)]
        if mods_s   and "modalidade"     in mf.columns: mf = mf[mf["modalidade"].isin(mods_s)]
        if canais_s and "canal_aquisicao"in mf.columns: mf = mf[mf["canal_aquisicao"].isin(canais_s)]
    else:
        mf = pd.DataFrame()

    pct_f = len(mf) / total_f * 100 if total_f else 0
    st.caption(f"**{len(mf):,}** matrículas selecionadas ({pct_f:.0f}% do total)")
    st.caption("Dados de `outputs/` · Rode `python main.py` para atualizar")


# ═══════════════════════════════════════════════════════════════════════════
# VISÃO GERAL
# ═══════════════════════════════════════════════════════════════════════════
if page == "🏠  Visão Geral":
    header("📊", "Visão Geral", "Painel consolidado de todos os KPIs estratégicos · 2022–2025")

    # ── linha 1: financeiro ──────────────────────────────────────────────
    section("Financeiro")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi("Receita Total",   fmt_brl(K.receita_total),    icon="💵", color="blue")
    with c2: kpi("Receita Bruta",   fmt_brl(K.receita_bruta),    icon="📋", color="blue")
    with c3: kpi("Ticket Médio",    f"R$ {K.ticket_medio:,.0f}", icon="🎟️", color="blue")
    with c4:
        gap = K.receita_bruta - K.receita_total
        kpi("Gap (desc.+inad.)", fmt_brl(gap),
            sub=f"{gap/K.receita_bruta*100:.1f}% da bruta", sub_type="down",
            icon="📉", color="red")
    with c5: kpi("Certificados",    fmt_n(K.cert_emitidos),      icon="🎓", color="green")

    # ── linha 2: acadêmico ───────────────────────────────────────────────
    section("Acadêmico")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: kpi("Matrículas",    fmt_n(K.total_matriculas),  icon="📚", color="blue")
    with c2: kpi("Alunos Únicos", fmt_n(K.total_alunos),      icon="👤", color="blue")
    with c3: kpi("Conclusão",     fmt_pct(K.taxa_conclusao),  sub="✔ Saudável",         sub_type="up",   icon="✅", color="green")
    with c4: kpi("Evasão",        fmt_pct(K.taxa_evasao),     sub="⚠ Acima do ideal",   sub_type="down", icon="🚪", color="red")
    with c5: kpi("Recompra",      fmt_pct(K.taxa_recompra),   sub="✔ Boa fidelização",  sub_type="up",   icon="🔄", color="green")
    with c6: kpi("Inadimplência", fmt_pct(K.taxa_inadimplencia), sub="6,1% da base",    sub_type="warn", icon="⚠️", color="yellow")

    # ── linha 3: qualidade ───────────────────────────────────────────────
    section("Qualidade e Comercial")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: kpi("NPS Médio",     f"{K.nps_medio:.1f}",     sub="✔ Excelente (>70)",  sub_type="up",   icon="⭐", color="green")
    with c2: kpi("Satisfação",    f"{K.nota_satis:.1f}",    sub="/ 100",              sub_type="",     icon="😊", color="blue")
    with c3: kpi("Professor",     f"{K.nota_prof:.1f}",     sub="✔ Diferencial",      sub_type="up",   icon="👨‍🏫", color="green")
    with c4: kpi("Plataforma",    f"{K.nota_plat:.1f}",     sub="⚠ Gap de 18 pontos", sub_type="down", icon="💻", color="red")
    with c5: kpi("ROI Campanhas", f"{K.roi_medio_camp:.2f}x", icon="📈", color="purple")
    with c6: kpi("CAC Médio",     f"R$ {K.cac_medio:,.0f}", icon="💸", color="purple")

    st.divider()

    # ── gráficos principais ──────────────────────────────────────────────
    col1, col2 = st.columns([3, 2])

    with col1:
        section("Receita Mensal")
        if not receita.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=receita["periodo_str"], y=receita["receita"],
                mode="lines", line=dict(color=C["blue"], width=2.5),
                fill="tozeroy", fillcolor="rgba(56,189,248,0.06)",
                hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>",
            ))
            media = receita["receita"].mean()
            fig.add_hline(y=media, line_dash="dot", line_color=C["yellow"],
                          annotation_text=f"Média R$ {media/1e6:.2f}M",
                          annotation_font_color=C["yellow"],
                          annotation_font_size=11)
            fig.update_layout(**LAYOUT, height=280,
                xaxis_tickangle=-45, xaxis_nticks=20,
                yaxis_tickprefix="R$ ", yaxis_tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Status das Matrículas")
        if not mf.empty and "status" in mf.columns:
            ct = mf["status"].value_counts().reset_index()
            ct.columns = ["status", "qtd"]
            CMAP = {"Concluída": C["green"], "Cancelada": C["red"],
                    "Ativa": C["blue"], "Evadida": C["yellow"], "Trancada": C["muted"]}
            fig = go.Figure(go.Pie(
                labels=ct["status"], values=ct["qtd"],
                marker_colors=[CMAP.get(s, "#888") for s in ct["status"]],
                hole=0.6, textinfo="percent",
                hovertemplate="<b>%{label}</b><br>%{value:,} (%{percent})<extra></extra>",
            ))
            fig.update_layout(**LAYOUT, height=280, showlegend=True,
                legend={**LEGEND, "orientation": "v", "x": 1, "y": 0.5},
                annotations=[dict(text=f"{len(mf):,}", x=0.5, y=0.55,
                                  font_size=20, font_color=C["text"],
                                  font_family="Inter", showarrow=False),
                             dict(text="matrículas", x=0.5, y=0.42,
                                  font_size=11, font_color=C["muted"],
                                  font_family="Inter", showarrow=False)])
            st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        section("Evasão por Modalidade")
        if not evasao.empty:
            ev = evasao.groupby("modalidade")["taxa_evasao"].mean().reset_index()
            ev = ev.sort_values("taxa_evasao")
            fig = px.bar(ev, x="taxa_evasao", y="modalidade", orientation="h",
                color="taxa_evasao",
                color_continuous_scale=[[0, C["green"]], [0.4, C["yellow"]], [1, C["red"]]])
            fig.update_layout(**LAYOUT, height=260,
                showlegend=False, coloraxis_showscale=False,
                xaxis_tickformat=".0%")
            fig.update_traces(hovertemplate="<b>%{y}</b><br>%{x:.1%}<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("ROI por Canal")
        if not marketing.empty:
            mk = marketing.sort_values("roi_medio")
            fig = px.bar(mk, x="roi_medio", y="canal", orientation="h",
                color="roi_medio",
                color_continuous_scale=[[0, "#162032"], [0.5, C["blue"]], [1, C["green"]]])
            fig.update_layout(**LAYOUT, height=260,
                showlegend=False, coloraxis_showscale=False)
            fig.update_traces(texttemplate="%{x:.2f}x", textposition="outside",
                hovertemplate="<b>%{y}</b><br>ROI: %{x:.2f}x<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)

    with col3:
        section("Cohort — Matrículas/Trimestre")
        if not cohort.empty:
            fig = px.area(cohort, x="trimestre", y="matriculas",
                color_discrete_sequence=[C["purple"]])
            fig.update_traces(line_width=2, fillcolor="rgba(167,139,250,0.15)",
                hovertemplate="<b>%{x}</b><br>%{y:,} matrículas<extra></extra>")
            fig.update_layout(**LAYOUT, height=260,
                showlegend=False, xaxis_tickangle=-45, xaxis_nticks=8)
            st.plotly_chart(fig, use_container_width=True)

    # ── insights automáticos ─────────────────────────────────────────────
    section("Alertas e Insights Automáticos")
    col1, col2 = st.columns(2)
    with col1:
        insight(f"NPS de <b>{K.nps_medio:.1f}</b> — nível de excelência mundial (acima de 70). Principal ativo de crescimento orgânico.", "green")
        insight(f"Professor com nota <b>{K.nota_prof:.1f}</b> vs plataforma com <b>{K.nota_plat:.1f}</b> — gap de <b>{K.nota_prof - K.nota_plat:.1f} pontos</b>. Com 45%+ das matrículas em modalidades digitais, isso afeta a evasão.", "red")
        insight(f"Taxa de recompra de <b>{fmt_pct(K.taxa_recompra)}</b> — cada aluno faz em média <b>{K.total_matriculas/K.total_alunos:.1f} cursos</b>.", "green")
    with col2:
        insight(f"Evasão de <b>{fmt_pct(K.taxa_evasao)}</b> — acima do benchmark de mercado (10–20%). Concentrada no EAD e Preparatório.", "red")
        insight(f"Gap de <b>{fmt_brl(K.receita_bruta - K.receita_total)}</b> entre receita bruta e efetiva — <b>{(K.receita_bruta - K.receita_total)/K.receita_bruta*100:.0f}%</b> do potencial não virou caixa.", "yellow")
        insight(f"<b>{fmt_brl(K.valor_inad_total)}</b> em inadimplência total. Mais de 58% nas faixas de baixa recuperabilidade (>60 dias).", "yellow")


# ═══════════════════════════════════════════════════════════════════════════
# FINANCEIRO
# ═══════════════════════════════════════════════════════════════════════════
elif page == "💰  Financeiro":
    header("💰", "Análise Financeira", "Receita, ticket médio, cohort e evolução temporal")

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Receita Total",  fmt_brl(K.receita_total),    color="blue", icon="💵")
    with c2: kpi("Receita Bruta",  fmt_brl(K.receita_bruta),    color="blue", icon="📋")
    with c3: kpi("Ticket Médio",   f"R$ {K.ticket_medio:,.0f}", color="green", icon="🎟️")
    with c4:
        gap = K.receita_bruta - K.receita_total
        kpi("Gap Total", fmt_brl(gap),
            sub=f"{gap/K.receita_bruta*100:.1f}% da receita bruta",
            sub_type="down", color="red", icon="📉")

    section("Evolução da Receita Mensal")
    if not receita.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=receita["periodo_str"], y=receita["receita"],
            mode="lines+markers",
            line=dict(color=C["blue"], width=2.5),
            marker=dict(size=4, color=C["blue"]),
            fill="tozeroy", fillcolor="rgba(56,189,248,0.07)",
            name="Receita Mensal",
            hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>",
        ))
        # média móvel 3 meses
        if len(receita) >= 3:
            mm = receita["receita"].rolling(3, center=True).mean()
            fig.add_trace(go.Scatter(
                x=receita["periodo_str"], y=mm,
                mode="lines", line=dict(color=C["yellow"], width=1.5, dash="dot"),
                name="Média Móvel 3m",
                hovertemplate="<b>%{x}</b><br>MM3: R$ %{y:,.0f}<extra></extra>",
            ))
        media = receita["receita"].mean()
        fig.add_hline(y=media, line_dash="dash", line_color=C["muted"],
                      annotation_text=f"Média: R$ {media/1e6:.2f}M",
                      annotation_font_color=C["muted"])
        fig.update_layout(**LAYOUT, height=360,
            xaxis_tickangle=-45, xaxis_nticks=24,
            yaxis_tickprefix="R$ ", yaxis_tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        section("Receita por Trimestre (Cohort)")
        if not cohort.empty:
            fig = px.bar(cohort, x="trimestre", y="receita",
                color_discrete_sequence=[C["blue"]])
            fig.update_layout(**LAYOUT, height=300, showlegend=False,
                xaxis_tickangle=-45, yaxis_tickprefix="R$ ", yaxis_tickformat=",.0f")
            fig.update_traces(hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Ticket Médio por Trimestre")
        if not cohort.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=cohort["trimestre"], y=cohort["ticket"],
                mode="lines+markers",
                line=dict(color=C["green"], width=2.5),
                marker=dict(size=6, color=C["green"],
                            line=dict(color=C["bg"], width=2)),
                fill="tozeroy", fillcolor="rgba(52,211,153,0.06)",
                hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>",
            ))
            fig.update_layout(**LAYOUT, height=300, showlegend=False,
                xaxis_tickangle=-45, yaxis_tickprefix="R$ ", yaxis_tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

    section("Receita por Categoria e Modalidade (matrículas filtradas)")
    if not mf.empty and "categoria" in mf.columns and "valor_liquido" in mf.columns:
        col1, col2 = st.columns(2)
        with col1:
            rc = mf.groupby("categoria")["valor_liquido"].sum().reset_index()
            rc = rc.sort_values("valor_liquido", ascending=False)
            fig = px.bar(rc, x="categoria", y="valor_liquido",
                color="categoria", color_discrete_sequence=SEQ)
            fig.update_layout(**LAYOUT, height=300, showlegend=False,
                xaxis_tickangle=-20, yaxis_tickprefix="R$ ", yaxis_tickformat=",.0f")
            fig.update_traces(hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            if "modalidade" in mf.columns:
                rm = mf.groupby("modalidade")["valor_liquido"].sum().reset_index()
                fig = px.pie(rm, names="modalidade", values="valor_liquido",
                    color_discrete_sequence=SEQ, hole=0.5)
                fig.update_layout(**LAYOUT, height=300)
                fig.update_traces(hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f} (%{percent})<extra></extra>")
                st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# ACADÊMICO
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🎓  Acadêmico":
    header("🎓", "Análise Acadêmica", "Evasão, conclusão, qualidade e recompra")

    # ── gauges de qualidade ──────────────────────────────────────────────
    section("Indicadores de Qualidade")
    c1, c2, c3, c4 = st.columns(4)
    with c1: gauge(K.nps_medio, "NPS Médio", 0, 100, [40, 70])
    with c2: gauge(K.nota_satis, "Satisfação", 0, 100, [50, 75])
    with c3: gauge(K.nota_prof, "Nota Professor", 0, 100, [60, 80])
    with c4: gauge(K.nota_plat, "Nota Plataforma", 0, 100, [60, 80])

    # ── KPIs ─────────────────────────────────────────────────────────────
    section("KPIs Acadêmicos")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi("Total Matrículas", fmt_n(K.total_matriculas), icon="📚", color="blue")
    with c2: kpi("Alunos Únicos",    fmt_n(K.total_alunos),     icon="👤", color="blue")
    with c3: kpi("Taxa Conclusão",   fmt_pct(K.taxa_conclusao), sub="✔ Saudável",        sub_type="up",   icon="✅", color="green")
    with c4: kpi("Taxa Evasão",      fmt_pct(K.taxa_evasao),   sub="⚠ Acima do ideal",  sub_type="down", icon="🚪", color="red")
    with c5: kpi("Taxa Recompra",    fmt_pct(K.taxa_recompra), sub="✔ Boa fidelização", sub_type="up",   icon="🔄", color="green")

    col1, col2 = st.columns(2)
    with col1:
        section("Evasão por Modalidade e Categoria")
        if not evasao.empty:
            ev = evasao.groupby(["modalidade", "categoria"])["taxa_evasao"].mean().reset_index()
            fig = px.bar(ev, x="categoria", y="taxa_evasao", color="modalidade",
                barmode="group", color_discrete_sequence=SEQ)
            fig.update_layout(**LAYOUT, height=340, xaxis_tickangle=-20,
                yaxis_tickformat=".0%", legend_title="Modalidade")
            fig.update_traces(hovertemplate="<b>%{x}</b> · %{fullData.name}<br>Evasão: %{y:.1%}<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Conclusão × Evasão por Modalidade")
        if not evasao.empty:
            ev2 = evasao.groupby("modalidade")[["taxa_evasao", "taxa_conclusao"]].mean().reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Conclusão", x=ev2["modalidade"],
                y=ev2["taxa_conclusao"], marker_color=C["green"]))
            fig.add_trace(go.Bar(name="Evasão", x=ev2["modalidade"],
                y=ev2["taxa_evasao"], marker_color=C["red"]))
            fig.update_layout(**LAYOUT, height=340, barmode="group",
                yaxis_tickformat=".0%", legend_title=None)
            st.plotly_chart(fig, use_container_width=True)

    section("Churn Risk e Distribuição de Notas")
    col1, col2, col3 = st.columns(3)
    with col1:
        if not mf.empty and "canal_aquisicao" in mf.columns and "churn_risk" in mf.columns:
            cr = mf.groupby("canal_aquisicao")["churn_risk"].mean().reset_index()
            cr = cr.sort_values("churn_risk")
            fig = px.bar(cr, x="churn_risk", y="canal_aquisicao", orientation="h",
                color="churn_risk",
                color_continuous_scale=[[0, C["green"]], [0.5, C["yellow"]], [1, C["red"]]])
            fig.update_layout(**LAYOUT, height=300,
                showlegend=False, coloraxis_showscale=False,
                xaxis_title="Churn Risk Médio", yaxis_title=None)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if not mf.empty and "nota_final" in mf.columns:
            fig = px.histogram(mf, x="nota_final", nbins=20,
                color_discrete_sequence=[C["blue"]])
            fig.update_layout(**LAYOUT, height=300, showlegend=False,
                xaxis_title="Nota Final", yaxis_title="Frequência")
            fig.update_traces(hovertemplate="Nota %{x}<br>%{y} alunos<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)

    with col3:
        if not mf.empty and "presenca" in mf.columns:
            fig = px.histogram(mf, x="presenca", nbins=20,
                color_discrete_sequence=[C["green"]])
            fig.update_layout(**LAYOUT, height=300, showlegend=False,
                xaxis_title="Presença", yaxis_title="Frequência",
                xaxis_tickformat=".0%")
            st.plotly_chart(fig, use_container_width=True)

    section("Cohort — Evasão ao Longo do Tempo")
    if not cohort.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cohort["trimestre"], y=cohort["evasao"],
            mode="lines+markers",
            line=dict(color=C["red"], width=2.5),
            marker=dict(size=7, color=C["red"],
                        line=dict(color=C["bg"], width=2)),
            fill="tozeroy", fillcolor="rgba(248,113,113,0.07)",
            hovertemplate="<b>%{x}</b><br>Evasão: %{y:.1%}<extra></extra>",
        ))
        media_ev = cohort["evasao"].mean()
        fig.add_hline(y=media_ev, line_dash="dot", line_color=C["muted"],
                      annotation_text=f"Média: {media_ev:.1%}",
                      annotation_font_color=C["muted"])
        fig.update_layout(**LAYOUT, height=280, showlegend=False,
            xaxis_tickangle=-45, yaxis_tickformat=".1%")
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# MARKETING
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📣  Marketing":
    header("📣", "Marketing e Canais", "Performance de captação, conversão e ROI por canal")

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Total Leads",    fmt_n(K.total_leads),          color="blue",   icon="🎯")
    with c2: kpi("Conversão",      fmt_pct(K.taxa_conversao),     color="green",  icon="✅")
    with c3: kpi("CAC Médio",      f"R$ {K.cac_medio:,.0f}",      color="purple", icon="💸")
    with c4: kpi("ROI Médio",      f"{K.roi_medio_camp:.2f}x",    color="purple", icon="📈")

    col1, col2 = st.columns(2)
    with col1:
        section("ROI por Canal de Marketing")
        if not marketing.empty:
            mk = marketing.sort_values("roi_medio")
            colors_roi = [C["red"] if v < 2 else C["yellow"] if v < 2.5 else C["green"]
                          for v in mk["roi_medio"]]
            fig = go.Figure(go.Bar(
                x=mk["roi_medio"], y=mk["canal"], orientation="h",
                marker_color=colors_roi,
                text=[f"{v:.2f}x" for v in mk["roi_medio"]],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>ROI: %{x:.2f}x<extra></extra>",
            ))
            fig.add_vline(x=marketing["roi_medio"].mean(), line_dash="dot",
                          line_color=C["muted"],
                          annotation_text="Média",
                          annotation_font_color=C["muted"])
            fig.update_layout(**LAYOUT, height=320,
                xaxis_title=None, yaxis_title=None, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("CPL vs Taxa de Conversão (tamanho = leads gerados)")
        if not marketing.empty:
            fig = px.scatter(marketing, x="cpl", y="taxa_conv",
                size="leads_gerados", color="canal",
                color_discrete_sequence=SEQ, hover_name="canal")
            fig.update_layout(**LAYOUT, height=320,
                xaxis_title="Custo por Lead (R$)",
                yaxis_title="Taxa de Conversão",
                yaxis_tickformat=".1%", legend_title=None)
            fig.update_traces(
                hovertemplate="<b>%{hovertext}</b><br>CPL: R$ %{x:.0f}<br>Conv: %{y:.1%}<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)

    section("Tabela Completa de Canais")
    if not marketing.empty:
        mkt = marketing.copy()
        mkt["investimento"]  = mkt["investimento"].apply(lambda x: f"R$ {x:,.0f}")
        mkt["leads_gerados"] = mkt["leads_gerados"].apply(lambda x: f"{int(x):,}")
        mkt["conversoes"]    = mkt["conversoes"].apply(lambda x: f"{int(x):,}")
        mkt["roi_medio"]     = mkt["roi_medio"].apply(lambda x: f"{x:.2f}x")
        mkt["cpl"]           = mkt["cpl"].apply(lambda x: f"R$ {x:.2f}")
        mkt["taxa_conv"]     = mkt["taxa_conv"].apply(lambda x: f"{x*100:.1f}%")
        mkt.columns          = ["Canal", "Investimento", "Leads", "Conversões", "ROI", "CPL", "Conversão"]
        st.dataframe(mkt, use_container_width=True, hide_index=True)

    section("Funil de Leads por Temperatura")
    if not leads.empty and "temperatura_lead" in leads.columns:
        col1, col2, col3 = st.columns(3)
        with col1:
            temp = leads["temperatura_lead"].value_counts().reset_index()
            temp.columns = ["temp", "qtd"]
            CMAP_T = {"Quente": C["red"], "Morno": C["yellow"], "Frio": C["blue"]}
            fig = go.Figure(go.Pie(
                labels=temp["temp"], values=temp["qtd"],
                marker_colors=[CMAP_T.get(t, "#888") for t in temp["temp"]],
                hole=0.55, textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>%{value:,} leads<extra></extra>",
            ))
            fig.update_layout(**LAYOUT, height=280, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            conv_t = leads.groupby("temperatura_lead")["conversao"].mean().reset_index()
            fig = px.bar(conv_t, x="temperatura_lead", y="conversao",
                color="temperatura_lead",
                color_discrete_map=CMAP_T)
            fig.update_layout(**LAYOUT, height=280, showlegend=False,
                xaxis_title=None, yaxis_title="Taxa de Conversão",
                yaxis_tickformat=".0%")
            fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:.1%}<extra></extra>")
            st.plotly_chart(fig, use_container_width=True)

        with col3:
            if "score_lead" in leads.columns:
                fig = px.box(leads, x="temperatura_lead", y="score_lead",
                    color="temperatura_lead",
                    color_discrete_map=CMAP_T)
                fig.update_layout(**LAYOUT, height=280, showlegend=False,
                    xaxis_title=None, yaxis_title="Score do Lead")
                st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# INADIMPLÊNCIA
# ═══════════════════════════════════════════════════════════════════════════
elif page == "⚠️  Inadimplência":
    header("⚠️", "Inadimplência", "Aging de inadimplência e análise de risco financeiro")

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Total Inadimplente",  fmt_brl(K.valor_inad_total),        color="red",    icon="⚠️")
    with c2: kpi("Taxa Inadimplência",  fmt_pct(K.taxa_inadimplencia),       color="yellow", icon="📊")
    with c3:
        if not aging.empty:
            rec = aging.iloc[0]["valor"]
            kpi("Recuperável (≤30d)", fmt_brl(rec),
                sub=f"{rec/K.valor_inad_total*100:.1f}% do total — aja agora",
                sub_type="up", color="green", icon="✅")
    with c4:
        if not aging.empty:
            crit = aging[aging["faixa"].str.contains("61|91|180", na=False)]["valor"].sum()
            kpi("Em risco alto (>60d)", fmt_brl(crit),
                sub=f"{crit/K.valor_inad_total*100:.1f}% — baixa recuperação",
                sub_type="down", color="red", icon="🔴")

    col1, col2 = st.columns([3, 2])
    with col1:
        section("Aging — Valor por Faixa de Atraso")
        if not aging.empty:
            CMAP_A = {0: C["green"], 1: C["yellow"], 2: C["orange"], 3: C["red"], 4: "#7f1d1d"}
            cores = [CMAP_A.get(i, C["red"]) for i in range(len(aging))]
            fig = go.Figure(go.Bar(
                x=aging["faixa"], y=aging["valor"],
                marker_color=cores,
                text=[f"R$ {v/1e6:.2f}M<br>{int(q)} casos"
                      for v, q in zip(aging["valor"], aging["qtd"])],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>R$ %{y:,.0f}<extra></extra>",
            ))
            fig.update_layout(**LAYOUT, height=340,
                xaxis_title=None, yaxis_title=None, showlegend=False,
                yaxis_tickprefix="R$ ", yaxis_tickformat=",.0f")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Distribuição % por Faixa")
        if not aging.empty:
            CMAP_A2 = [C["green"], C["yellow"], C["orange"], C["red"], "#7f1d1d"]
            fig = go.Figure(go.Pie(
                labels=aging["faixa"], values=aging["valor"],
                marker_colors=CMAP_A2[:len(aging)],
                hole=0.55, textinfo="percent",
                hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<br>%{percent}<extra></extra>",
            ))
            total_v = aging["valor"].sum()
            fig.update_layout(**LAYOUT, height=340, showlegend=True,
                legend=LEGEND,
                annotations=[dict(text=fmt_brl(total_v), x=0.5, y=0.55,
                                  font_size=16, font_color=C["text"],
                                  font_family="Inter", showarrow=False),
                             dict(text="total", x=0.5, y=0.42,
                                  font_size=11, font_color=C["muted"],
                                  font_family="Inter", showarrow=False)])
            st.plotly_chart(fig, use_container_width=True)

    section("Detalhamento e Alertas")
    col1, col2 = st.columns(2)
    with col1:
        if not aging.empty:
            ag = aging.copy()
            ag["valor"] = ag["valor"].apply(lambda x: f"R$ {x:,.2f}")
            ag["qtd"]   = ag["qtd"].apply(lambda x: f"{int(x):,}")
            ag["% do total"] = (aging["valor"] / aging["valor"].sum() * 100).apply(lambda x: f"{x:.1f}%")
            ag.columns = ["Faixa", "Valor em Atraso", "Casos", "% do Total"]
            st.dataframe(ag, use_container_width=True, hide_index=True)
    with col2:
        insight("Aja <b>imediatamente</b> nos casos da faixa Até 30d — chance de recuperação alta com simples lembrete de cobrança.", "green")
        insight("58% do valor está em faixas >60 dias — baixa recuperabilidade. Considere negociação com desconto para fechar esses casos.", "red")
        insight("Taxa de inadimplência de 6,1% é relativamente baixa — a evasão de 26,5% não é motivada principalmente por dificuldade financeira.", "blue")
        insight("Priorize a régua de cobrança nos primeiros 30 dias. Evitar que a dívida envelheça é mais eficiente do que tentar recuperar dívidas antigas.", "yellow")


# ═══════════════════════════════════════════════════════════════════════════
# RANKING CURSOS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🏆  Ranking Cursos":
    header("🏆", "Ranking de Cursos", "Análise comparativa de todos os cursos por múltiplos critérios")

    if cursos.empty:
        st.warning("Arquivo 05_cursos.csv não encontrado.")
    else:
        metrica = st.radio("Ordenar por", ["NPS", "ROI", "Taxa de Evasão", "Ticket Médio", "Margem de Lucro"],
                           horizontal=True)

        MAP_COL = {
            "NPS":             ("NPS",           False, C["blue"],   lambda v: f"{v:.1f}",   100),
            "ROI":             ("roi",            False, C["green"],  lambda v: f"{v:.2f}x",  cursos["roi"].max() if "roi" in cursos.columns else 10),
            "Taxa de Evasão":  ("taxa_evasao",    True,  C["red"],    lambda v: f"{v:.1%}",   1),
            "Ticket Médio":    ("ticket_medio",   False, C["purple"], lambda v: f"R$ {v:,.0f}", cursos["ticket_medio"].max() if "ticket_medio" in cursos.columns else 1),
            "Margem de Lucro": ("margem_lucro",   False, C["yellow"], lambda v: f"{v:.1%}",   1),
        }

        col_key, asc, cor, fmt_fn, max_v = MAP_COL[metrica]

        if col_key in cursos.columns and "curso" in cursos.columns:
            top = cursos.sort_values(col_key, ascending=asc).head(20)

            col1, col2 = st.columns([1, 2])
            with col1:
                section(f"Top 20 — {metrica}")
                rows = [(row["curso"][:35], row[col_key], fmt_fn(row[col_key]))
                        for _, row in top.iterrows()]
                ranking_html(rows, max_v if max_v != 1 else top[col_key].max())

            with col2:
                section("Scatter — NPS vs Taxa de Evasão (todos os cursos)")
                if "NPS" in cursos.columns and "taxa_evasao" in cursos.columns:
                    fig = px.scatter(cursos,
                        x="NPS", y="taxa_evasao",
                        size="ticket_medio" if "ticket_medio" in cursos.columns else None,
                        color="modalidade" if "modalidade" in cursos.columns else None,
                        hover_name="curso" if "curso" in cursos.columns else None,
                        color_discrete_sequence=SEQ)
                    fig.update_layout(**LAYOUT, height=460,
                        xaxis_title="NPS do Curso",
                        yaxis_title="Taxa de Evasão",
                        yaxis_tickformat=".0%",
                        legend_title="Modalidade")
                    fig.update_traces(
                        hovertemplate="<b>%{hovertext}</b><br>NPS: %{x}<br>Evasão: %{y:.1%}<extra></extra>")
                    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# EXPLORAR
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🔍  Explorar":
    header("🔍", "Explorar Dados", "Monte sua própria análise a partir das matrículas filtradas")

    st.info(f"**{len(mf):,} matrículas** selecionadas com os filtros da sidebar.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        eixo_x = st.selectbox("Agrupar por (eixo X)", [
            "canal_aquisicao", "categoria", "modalidade",
            "status", "ano", "trimestre", "mes"])
    with col2:
        eixo_y = st.selectbox("Métrica (eixo Y)", [
            "valor_liquido", "churn_risk", "nota_final",
            "presenca", "lifetime_value", "desconto"])
    with col3:
        agr = st.selectbox("Agregação", ["Soma", "Média", "Contagem", "Máximo", "Mínimo"])
    with col4:
        tipo_graf = st.selectbox("Tipo de gráfico", ["Barras", "Linha", "Área", "Pizza"])

    if not mf.empty and eixo_x in mf.columns and eixo_y in mf.columns:
        fn_map = {"Soma": "sum", "Média": "mean", "Contagem": "count",
                  "Máximo": "max", "Mínimo": "min"}
        df_p = mf.groupby(eixo_x)[eixo_y].agg(fn_map[agr]).reset_index()
        df_p = df_p.sort_values(eixo_y, ascending=False)

        if tipo_graf == "Barras":
            fig = px.bar(df_p, x=eixo_x, y=eixo_y,
                color=eixo_x, color_discrete_sequence=SEQ)
        elif tipo_graf == "Linha":
            fig = px.line(df_p, x=eixo_x, y=eixo_y,
                markers=True, color_discrete_sequence=[C["blue"]])
        elif tipo_graf == "Área":
            fig = px.area(df_p, x=eixo_x, y=eixo_y,
                color_discrete_sequence=[C["blue"]])
        else:
            fig = px.pie(df_p, names=eixo_x, values=eixo_y,
                color_discrete_sequence=SEQ, hole=0.4)

        fig.update_layout(**LAYOUT, height=400, showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    section("Dados filtrados (até 500 linhas)")
    cols_show = ["matricula_id", "status", "canal_aquisicao", "categoria", "modalidade",
                 "valor_liquido", "churn_risk", "nota_final", "presenca",
                 "recompra", "inadimplente", "trimestre"]
    cols_ok = [c for c in cols_show if c in mf.columns]
    st.dataframe(mf[cols_ok].head(500), use_container_width=True, hide_index=True)
    st.caption(f"Mostrando até 500 de {len(mf):,} linhas · Use os filtros da sidebar para refinar")
    from plotly.offline import plot

    ###python -m streamlit run dashboard/dashboard.py