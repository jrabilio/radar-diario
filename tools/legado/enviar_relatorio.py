#!/usr/bin/env python3
"""
enviar_relatorio.py — Relatório Executivo Diário
Envia o relatório via Gmail SMTP (smtplib.SMTP_SSL).

LEGADO: a rotina que chamava este script (LaunchAgent com.ntics.relatoriodiario)
não existe mais. O script foi guardado por ter valor e continua funcionando se
chamado à mão — ver MAPA.md.

Tudo vem do .env da raiz do SPACE (gitignored — este repositório é público):
    GMAIL_USER               — conta que envia
    GMAIL_APP_PASSWORD       — App Password do Google (16 chars, sem espaços)
    RELATORIO_DESTINATARIO   — para quem vai (padrão: o próprio GMAIL_USER)

A App Password precisa ser da MESMA conta do GMAIL_USER: trocar o remetente sem
gerar uma nova App Password naquela conta faz o login SMTP falhar.

Uso manual:
    python3 tools/legado/enviar_relatorio.py
"""

import os
import sys
import smtplib
import time
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

# ── Configuração ──────────────────────────────────────────────────────────────
SPACE = Path(__file__).resolve().parent.parent.parent
load_dotenv(SPACE / ".env")

DIARIO_DIR      = SPACE / ".tmp" / "relatorios-executivos"
LOG_DIR         = SPACE / ".tmp" / "logs"
LOG_FILE        = LOG_DIR / "enviar_relatorio.log"
MAX_IDADE_HORAS = 36


# ── Helpers ───────────────────────────────────────────────────────────────────

def log(msg):
    import datetime
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def achar_relatorio_hoje():
    hoje = date.today()
    candidatos = [
        DIARIO_DIR / f"Relatorio_Executivo_{hoje.strftime('%d-%m-%Y')}.html",
        DIARIO_DIR / f"Relatorio_Executivo_{hoje.strftime('%Y-%m-%d')}.html",
        DIARIO_DIR / f"Relatorio_Executivo_{hoje.strftime('%d%m%Y')}.html",
    ]
    for c in candidatos:
        if c.exists():
            return c

    # Fallback: arquivo mais recente com menos de MAX_IDADE_HORAS
    agora = time.time()
    htmls = sorted(DIARIO_DIR.glob("Relatorio_Executivo_*.html"),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    for h in htmls:
        if (agora - h.stat().st_mtime) / 3600 <= MAX_IDADE_HORAS:
            return h
    return None


def enviar_via_gmail(remetente: str, senha: str, destinatario: str,
                     assunto: str, html_body: str) -> bool:
    """Envia e-mail via Gmail SMTP SSL — mesmo padrão do enviar_pmo_diario.py."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"]    = remetente
    msg["To"]      = destinatario
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(remetente, senha)
            smtp.sendmail(remetente, destinatario, msg.as_string())
        return True
    except smtplib.SMTPAuthenticationError as e:
        log(f"Autenticação Gmail falhou: {e}")
        log("Verifique se GMAIL_APP_PASSWORD está correto e se a App Password ainda é válida.")
        return False
    except Exception as e:
        log(f"Erro ao enviar via Gmail SMTP: {e}")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    log("=" * 60)
    log("Iniciando envio do Relatório Executivo")

    # Tudo vem do .env da raiz. O fallback antigo lia a senha do plist do
    # pmodiario — removido: aqueles plists não existem mais nesta máquina.
    gmail_user = os.environ.get("GMAIL_USER", "")
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD", "")
    destinatario = os.environ.get("RELATORIO_DESTINATARIO", "") or gmail_user

    if not gmail_user or not gmail_pass:
        log("ERRO: GMAIL_USER e/ou GMAIL_APP_PASSWORD ausentes.")
        log(f"Defina as duas no .env da raiz: {SPACE / '.env'}")
        log("A App Password precisa ser da mesma conta do GMAIL_USER —")
        log("gere em https://myaccount.google.com/apppasswords logado nela.")
        sys.exit(1)

    relatorio = achar_relatorio_hoje()
    if relatorio is None:
        log(f"ERRO: Nenhum relatório recente encontrado em {DIARIO_DIR}")
        sys.exit(1)

    log(f"Relatório encontrado: {relatorio.name}")

    hoje = date.today()
    dia_semana_map = {0:"Segunda",1:"Terça",2:"Quarta",3:"Quinta",
                      4:"Sexta",5:"Sábado",6:"Domingo"}
    dia    = dia_semana_map[hoje.weekday()]
    assunto = os.environ.get("RELATORIO_ASSUNTO_PREFIXO", "Relatório Executivo") + \
              f" — {dia}, {hoje.strftime('%d/%m/%Y')}"

    html = relatorio.read_text(encoding="utf-8")
    log(f"HTML carregado: {len(html):,} bytes")
    log(f"Remetente: {gmail_user}")
    log(f"Enviando para: {destinatario}")
    log(f"Assunto: {assunto}")

    ok = enviar_via_gmail(gmail_user, gmail_pass, destinatario, assunto, html)

    if ok:
        log("✅ E-mail enviado com sucesso!")
    else:
        log("❌ Falha no envio. Veja erros acima.")
        sys.exit(1)


if __name__ == "__main__":
    main()
