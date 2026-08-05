"""
Template do Relatório Executivo Diário — NTICS Projetos
Padrão visual estabelecido em 25/06/2026.

Variáveis esperadas no escopo de quem fizer exec() deste arquivo:
  - data_str        : str  — ex: "25 de Junho de 2026"
  - dia_semana      : str  — ex: "Quinta-feira"
  - semana_num      : str  — ex: "26/2026"
  - sumario         : list[str] — 3 bullets do sumário executivo
  - dolar_valor     : str  — ex: "R$ 5,2006"
  - dolar_delta     : str  — ex: "▲ +0,28% (24/06)"
  - dolar_nota      : str  — ex: "Maior nível em 13 meses"
  - ibov_valor      : str  — ex: "170.506 pts"
  - ibov_delta      : str  — ex: "▼ −0,44% (24/06)"
  - ibov_vol        : str  — ex: "Vol. R$ 27,2 bi"
  - selic_valor     : str  — ex: "14,25% a.a."
  - selic_nota      : str  — ex: "Ata Copom: postura restritiva"
  - dolar_tend_semana  : str — tendência semanal em texto
  - dolar_fatores_alta : list[str] — bullets de pressão altista
  - dolar_fatores_queda: list[str] — bullets que podem segurar/baixar
  - bloco1          : list[dict] — newsletters
  - bloco2_mercado  : list[dict] — portais de mercado
  - bloco2_ma       : list[dict] — deals M&A
  - bloco3          : list[dict] — ESG
  - bloco4_ntics    : list[dict] — clipping NEST (pode ser vazio)
  - data_segunda_clipping : str — ex: "22/06/2026"
  - hora_geracao    : str  — ex: "06:45"
  - output_path     : str  — caminho completo onde salvar o HTML

Estrutura de bloco1 (newsletters):
  [{"fonte": "Agro Espresso", "cor": "#2E6B30", "data": "25/06/2026",
    "noticias": [{"titulo": "...", "resumo": "...", "link": "", "importante": True, "update": False}]}]

Estrutura de bloco2_ma (M&A):
  [{"deal": "Suzano × KMB", "partes": "...", "valor": "US$ 3,4 bi",
    "contexto": "...", "importante": True}]

Estrutura de bloco3 (ESG):
  [{"portal": "ESG / Regulatório", "cor": "#2E7D5A", "data": "jun/2026",
    "noticias": [{"titulo": "...", "resumo": "...", "link": "", "importante": False}]}]

Estrutura de bloco4_ntics (clipping):
  [] se sem menções. Com menções:
  [{"empresa": "NTICS Projetos", "fonte": "Portal XYZ", "titulo": "...",
    "resumo": "...", "link": ""}]
"""

import os
import glob as _glob
from datetime import date

# ── helpers ────────────────────────────────────────────────────────────────────

def _badge_imp():
    return '<span class="badge-importante">Importante</span>'

def _badge_upd():
    return '<span class="badge-update">Atualização</span>'

def _render_noticias(noticias):
    html = ""
    for n in noticias:
        title_inner = f'<a href="{n["link"]}" target="_blank">{n["titulo"]}</a>' if n.get("link") else n["titulo"]
        badges = (_badge_imp() if n.get("importante") else "") + (_badge_upd() if n.get("update") else "")
        html += f"""
      <div class="noticia">
        <h3 class="news-title">{title_inner}{badges}</h3>
        <p class="news-resumo">{n["resumo"]}</p>
      </div>"""
    return html

def _render_bullets(items):
    return "".join(f"<br>• {i}" for i in items).lstrip("<br>")

# ── CSS (único, centralizado) ───────────────────────────────────────────────────

CSS = """
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; color: #222; }

  /* HEADER */
  .header {
    background: linear-gradient(135deg, #1A2744 0%, #2E4A8A 100%);
    color: white; padding: 28px 32px 22px;
    display: flex; align-items: center; justify-content: space-between;
  }
  .header-logo { font-size: 22px; font-weight: 800; letter-spacing: 1px; }
  .header-logo span { color: #7EC8E3; }
  .header-date { font-size: 14px; opacity: 0.85; text-align: right; }
  .header-date strong { display: block; font-size: 18px; opacity: 1; }

  /* DÓLAR TICKER */
  .dolar-ticker {
    background: #fff; border-bottom: 3px solid #1A2744;
    padding: 0 32px; display: flex; align-items: stretch; flex-wrap: wrap;
  }
  .ticker-item {
    padding: 12px 20px 10px; border-right: 1px solid #eee;
    display: flex; flex-direction: column; gap: 2px; min-width: 130px;
  }
  .ticker-item:last-child { border-right: none; }
  .ticker-label { font-size: 10px; color: #888; text-transform: uppercase; letter-spacing: 0.7px; font-weight: 600; }
  .ticker-value { font-size: 20px; font-weight: 800; color: #1A2744; }
  .ticker-delta { font-size: 12px; font-weight: 600; }
  .ticker-delta.up   { color: #C0392B; }
  .ticker-delta.down { color: #27AE60; }
  .ticker-trend { font-size: 11px; color: #666; margin-top: 1px; }

  /* TENDÊNCIA DÓLAR */
  .dolar-tendencia {
    background: #fff; border-left: 5px solid #2E4A8A;
    margin: 16px 32px 0; padding: 14px 18px;
    border-radius: 0 6px 6px 0; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }
  .dolar-tendencia h3 {
    font-size: 11px; text-transform: uppercase; letter-spacing: 1px;
    color: #2E4A8A; margin-bottom: 8px; font-weight: 700;
  }
  .tendencia-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
  .tend-item .tend-label {
    font-size: 10px; color: #888; text-transform: uppercase;
    font-weight: 600; letter-spacing: 0.5px; margin-bottom: 3px;
  }
  .tend-item .tend-valor { font-size: 13px; color: #222; line-height: 1.45; }
  .tend-item .tend-valor strong { color: #1A2744; }

  /* SUMÁRIO */
  .sumario {
    background: #fff; border-left: 5px solid #1A2744;
    margin: 16px 32px 0; padding: 16px 20px;
    border-radius: 0 6px 6px 0; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }
  .sumario h2 {
    font-size: 11px; text-transform: uppercase; letter-spacing: 1px;
    color: #2E4A8A; margin-bottom: 10px; font-weight: 700;
  }
  .sumario ul { list-style: none; }
  .sumario ul li {
    padding: 6px 0 6px 20px; position: relative;
    font-size: 13.5px; border-bottom: 1px solid #f0f0f0; line-height: 1.5;
  }
  .sumario ul li:last-child { border-bottom: none; }
  .sumario ul li::before {
    content: "▶"; color: #2E4A8A;
    position: absolute; left: 0; font-size: 9px; top: 9px;
  }

  /* SEÇÃO */
  .section { margin: 20px 32px 0; }
  .section-header {
    display: flex; align-items: center; gap: 10px;
    background: #1A2744; color: white;
    padding: 10px 18px; border-radius: 6px 6px 0 0;
    font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
  }
  .section-header .bloco-num {
    background: rgba(255,255,255,0.2); border-radius: 50%;
    width: 22px; height: 22px;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 800;
  }
  .section-body {
    background: white; border-radius: 0 0 6px 6px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07); overflow: hidden;
  }

  /* FONTE CARD */
  .fonte-card { border-bottom: 1px solid #f0f0f0; }
  .fonte-card:last-child { border-bottom: none; }
  .fonte-header {
    padding: 9px 18px; font-size: 11px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.5px;
    color: white; display: flex; align-items: center; gap: 8px;
  }
  .fonte-header .dot { width: 7px; height: 7px; background: rgba(255,255,255,0.55); border-radius: 50%; flex-shrink: 0; }
  .fonte-header .fonte-date { margin-left: auto; opacity: 0.7; font-size: 10px; letter-spacing: 0; font-weight: 400; }

  /* NOTÍCIA */
  .noticia { padding: 12px 18px; border-bottom: 1px dashed #f0f0f0; }
  .noticia:last-child { border-bottom: none; }
  .news-title { font-size: 14px; font-weight: 700; color: #1A2744; margin-bottom: 5px; line-height: 1.4; }
  .news-title a { color: #1A2744; text-decoration: none; }
  .news-title a:hover { text-decoration: underline; color: #2E4A8A; }
  .news-resumo { font-size: 13px; color: #444; line-height: 1.6; }
  .badge-importante {
    display: inline-block; background: #C0392B; color: white;
    font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 3px;
    margin-left: 6px; vertical-align: middle; text-transform: uppercase; letter-spacing: 0.5px;
  }
  .badge-update {
    display: inline-block; background: #E67E22; color: white;
    font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 3px;
    margin-left: 6px; vertical-align: middle; text-transform: uppercase;
  }

  /* MERCADO BAR */
  .mercado-bar {
    background: #f8f9fa; border-bottom: 1px solid #e8e8e8;
    padding: 10px 18px; display: flex; gap: 28px; flex-wrap: wrap;
  }
  .mercado-item { display: flex; flex-direction: column; }
  .mercado-label { font-size: 10px; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }
  .mercado-value { font-size: 15px; font-weight: 700; }
  .mercado-value.down { color: #C0392B; }
  .mercado-value.up   { color: #27AE60; }
  .mercado-delta { font-size: 11px; }
  .mercado-delta.down { color: #C0392B; }
  .mercado-delta.up   { color: #27AE60; }

  /* M&A TABLE */
  .ma-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .ma-table th {
    background: #f4f6f9; font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.5px; color: #888;
    padding: 8px 14px; text-align: left; border-bottom: 1px solid #e8e8e8;
  }
  .ma-table td {
    padding: 10px 14px; border-bottom: 1px solid #f4f4f4;
    vertical-align: top; color: #333; line-height: 1.45;
  }
  .ma-table tr:last-child td { border-bottom: none; }
  .ma-table tr:hover td { background: #f8f9fa; }
  .ma-table td strong { color: #1A2744; }

  /* CLIPPING SEM MENÇÕES */
  .no-mention {
    padding: 16px 18px; font-size: 13px; color: #999; font-style: italic;
    border-left: 3px solid #e0e0e0; margin: 12px 18px;
    background: #fafafa; border-radius: 3px;
  }
  .no-mention strong { color: #777; font-style: normal; }

  /* FOOTER */
  .footer {
    margin: 24px 32px 32px;
    background: #1A2744; color: rgba(255,255,255,0.65);
    border-radius: 6px; padding: 14px 20px;
    font-size: 12px; display: flex; justify-content: space-between;
    align-items: center; flex-wrap: wrap; gap: 8px;
  }
  .footer strong { color: white; }

  @media print {
    .header, .fonte-header, .section-header, .footer {
      -webkit-print-color-adjust: exact; print-color-adjust: exact;
    }
  }
"""

# ── RENDER ─────────────────────────────────────────────────────────────────────

def render_relatorio():
    # ── Bloco 1 ──
    b1_html = ""
    for fonte in bloco1:
        b1_html += f"""
    <div class="fonte-card">
      <div class="fonte-header" style="background:{fonte['cor']};">
        <span class="dot"></span> {fonte['fonte']}
        <span class="fonte-date">{fonte.get('data','')}</span>
      </div>
      {_render_noticias(fonte['noticias'])}
    </div>"""

    # ── Bloco 2 mercado ──
    b2m_html = ""
    for portal in bloco2_mercado:
        b2m_html += f"""
    <div class="fonte-card">
      <div class="fonte-header" style="background:{portal['cor']};">
        <span class="dot"></span> {portal['portal']}
        <span class="fonte-date">{portal.get('data','')}</span>
      </div>
      {_render_noticias(portal['noticias'])}
    </div>"""

    # ── Bloco 2 M&A ──
    ma_rows = ""
    for d in bloco2_ma:
        imp = _badge_imp() if d.get("importante") else ""
        ma_rows += f"""
            <tr>
              <td><strong>{d['deal']}</strong>{imp}</td>
              <td>{d['partes']}</td>
              <td>{d['valor']}</td>
              <td>{d['contexto']}</td>
            </tr>"""

    # ── Bloco 3 ESG ──
    b3_html = ""
    for portal in bloco3:
        b3_html += f"""
    <div class="fonte-card">
      <div class="fonte-header" style="background:{portal['cor']};">
        <span class="dot"></span> {portal['portal']}
        <span class="fonte-date">{portal.get('data','')}</span>
      </div>
      {_render_noticias(portal['noticias'])}
    </div>"""

    # ── Bloco 4 Clipping ──
    hoje_str = date.today().strftime("%d/%m/%Y")
    if not bloco4_ntics:
        b4_html = f"""
    <div class="fonte-card">
      <div class="fonte-header" style="background:#0f766e;">
        <span class="dot"></span> Monitoramento Semanal — {data_segunda_clipping} a {hoje_str}
      </div>
      <div class="no-mention">
        <strong>Sem menções identificadas esta semana.</strong><br>
        Período: {data_segunda_clipping} a {hoje_str} — 6 queries executadas em portais regionais, imprensa local e web geral.<br>
        Empresas monitoradas: NTICS Projetos · Ecotransforma · Ecotransforma SB ·
        Sustentabilidade e Cultura Produções · Cultura Ambiental Produções · Oliveira Produções.
      </div>
    </div>"""
    else:
        from collections import defaultdict
        por_empresa = defaultdict(list)
        for m in bloco4_ntics:
            por_empresa[m["empresa"]].append(m)
        b4_html = ""
        for empresa, mencoes in por_empresa.items():
            noticias_fmt = [{"titulo": m["titulo"], "resumo": f'<strong>{m["fonte"]}</strong> — {m["resumo"]}',
                             "link": m.get("link",""), "importante": False} for m in mencoes]
            b4_html += f"""
    <div class="fonte-card">
      <div class="fonte-header" style="background:#0f766e;">
        <span class="dot"></span> {empresa}
        <span class="fonte-date">{data_segunda_clipping} a {hoje_str}</span>
      </div>
      {_render_noticias(noticias_fmt)}
    </div>"""

    # ── Sumário bullets ──
    sumario_li = "".join(f"<li>{s}</li>" for s in sumario)

    # ── Fatores dólar ──
    fatores_alta_html  = _render_bullets(dolar_fatores_alta)
    fatores_queda_html = _render_bullets(dolar_fatores_queda)

    # ── HTML final ──
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Relatório Executivo — {data_str}</title>
<style>{CSS}</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <div class="header-logo">NTICS <span>Projetos</span><br>
    <small style="font-size:11px;font-weight:400;opacity:0.7;letter-spacing:0">Relatório Executivo de Notícias</small>
  </div>
  <div class="header-date">
    <strong>{data_str}</strong>
    {dia_semana} &nbsp;|&nbsp; Semana {semana_num}
  </div>
</div>

<!-- DÓLAR TICKER -->
<div class="dolar-ticker">
  <div class="ticker-item">
    <span class="ticker-label">💵 Dólar (USD/BRL)</span>
    <span class="ticker-value">{dolar_valor}</span>
    <span class="ticker-delta up">{dolar_delta}</span>
    <span class="ticker-trend">{dolar_nota}</span>
  </div>
  <div class="ticker-item">
    <span class="ticker-label">📈 Ibovespa</span>
    <span class="ticker-value" style="color:#C0392B">{ibov_valor}</span>
    <span class="ticker-delta up">{ibov_delta}</span>
    <span class="ticker-trend">{ibov_vol}</span>
  </div>
  <div class="ticker-item">
    <span class="ticker-label">🏦 Selic</span>
    <span class="ticker-value">{selic_valor}</span>
    <span class="ticker-delta" style="color:#E67E22">→ Postura restritiva</span>
    <span class="ticker-trend">{selic_nota}</span>
  </div>
</div>

<!-- TENDÊNCIA DÓLAR -->
<div class="dolar-tendencia">
  <h3>📊 Dólar — Tendência &amp; Drivers</h3>
  <div class="tendencia-grid">
    <div class="tend-item">
      <div class="tend-label">Tendência semanal</div>
      <div class="tend-valor">{dolar_tend_semana}</div>
    </div>
    <div class="tend-item">
      <div class="tend-label">Fatores de pressão (alta do dólar)</div>
      <div class="tend-valor">{fatores_alta_html}</div>
    </div>
    <div class="tend-item">
      <div class="tend-label">Fatores que podem segurar / baixar</div>
      <div class="tend-valor">{fatores_queda_html}</div>
    </div>
  </div>
</div>

<!-- SUMÁRIO -->
<div class="sumario">
  <h2>📌 Sumário Executivo</h2>
  <ul>{sumario_li}</ul>
</div>

<!-- BLOCO 1: NEWSLETTERS -->
<div class="section">
  <div class="section-header">
    <span class="bloco-num">1</span> 📬 Newsletters &amp; Boletins Matinais
  </div>
  <div class="section-body">{b1_html}
  </div>
</div>

<!-- BLOCO 2: MERCADO -->
<div class="section">
  <div class="section-header">
    <span class="bloco-num">2</span> 📈 Mercado &amp; M&amp;A
  </div>
  <div class="section-body">
    {b2m_html}
    <div class="fonte-card">
      <div class="fonte-header" style="background:#2E4A8A;">
        <span class="dot"></span> Fusões &amp; Aquisições — Deals em Destaque
      </div>
      <div style="padding:0">
        <table class="ma-table">
          <thead>
            <tr>
              <th>Deal</th><th>Partes</th><th>Valor</th><th>Status &amp; Contexto</th>
            </tr>
          </thead>
          <tbody>{ma_rows}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- BLOCO 3: ESG -->
<div class="section">
  <div class="section-header">
    <span class="bloco-num">3</span> 🌱 ESG &amp; Sustentabilidade
  </div>
  <div class="section-body">{b3_html}
  </div>
</div>

<!-- BLOCO 4: CLIPPING NEST -->
<div class="section">
  <div class="section-header">
    <span class="bloco-num">4</span> 🏢 Clipping Grupo NEST
  </div>
  <div class="section-body">{b4_html}
  </div>
</div>

<!-- FOOTER -->
<div class="footer">
  <div><strong>NTICS Projetos</strong> — Escritório de Projetos</div>
  <div>📧 Envio automático via LaunchAgent · 07:30</div>
  <div>Gerado em {data_str} às {hora_geracao}</div>
</div>

</body>
</html>"""

    # ── Salvar ──
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Relatório salvo em: {output_path}")
    return html

# Executa imediatamente quando chamado via exec()
render_relatorio()
