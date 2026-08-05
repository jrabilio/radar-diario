#!/usr/bin/env python3
"""
enviar_relatorio.py — NTICS Projetos
Envia o Relatório Executivo Diário via Gmail SMTP (smtplib.SMTP_SSL).
Mesmo padrão do enviar_pmo_diario.py.
Chamado pelo LaunchAgent com.ntics.relatoriodiario.plist às 07:30.

Variáveis de ambiente (definidas no plist):
    GMAIL_USER          — ex: abilio@ntics.com.br
    GMAIL_APP_PASSWORD  — App Password do Google (sem espaços)

Uso manual:
    GMAIL_USER=abilio@ntics.com.br GMAIL_APP_PASSWORD=xxxx python3 /Users/abiliomartins/Projetos/ABILIO'S SPACE/automacoes/relatorio-diario/enviar_relatorio.py
"""

import os
import sys
import smtplib
import time
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# ── Configuração ──────────────────────────────────────────────────────────────
DESTINATARIO    = "abilio@ntics.com.br"
DIARIO_DIR      = Path.home() / "Desktop" / "CLAUDE" / "Diario"
LOG_DIR         = Path.home() / "Desktop" / "CLAUDE" / "automacoes" / "logs"
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

    # Credenciais via variáveis de ambiente (definidas no plist)
    gmail_user = os.environ.get("GMAIL_USER", "abilio@ntics.com.br")
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD", "")

    # Fallback: lê a senha do plist do pmodiario (fonte única de verdade)
    # Assim, quando a App Password é atualizada no pmodiario, o relatorio
    # automaticamente usa a mesma senha sem precisar atualizar dois plists.
    if not gmail_pass:
        pmodiario_plists = [
            Path.home() / "Library" / "LaunchAgents" / "com.ntics.pmodiario.plist",
            Path.home() / "automacoes" / "com.ntics.pmodiario.plist",
            Path.home() / "Desktop" / "CLAUDE" / "automacoes" / "com.ntics.pmodiario.plist",
        ]
        for plist in pmodiario_plists:
            if plist.exists():
                try:
                    import subprocess as _sp
                    r = _sp.run(
                        ["/usr/libexec/PlistBuddy", "-c",
                         "Print :EnvironmentVariables:GMAIL_APP_PASSWORD", str(plist)],
                        capture_output=True, text=True
                    )
                    if r.returncode == 0 and r.stdout.strip():
                        gmail_pass = r.stdout.strip()
                        log(f"Senha lida de: {plist.name}")
                        break
                except Exception:
                    pass

    if not gmail_pass:
        log("ERRO: GMAIL_APP_PASSWORD não encontrada em variável de ambiente nem no plist do pmodiario.")
        log("Execute com: GMAIL_USER=abilio@ntics.com.br GMAIL_APP_PASSWORD=xxxx python3 enviar_relatorio.py")
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
    assunto = f"Relatório Executivo NTICS — {dia}, {hoje.strftime('%d/%m/%Y')}"

    html = relatorio.read_text(encoding="utf-8")
    log(f"HTML carregado: {len(html):,} bytes")
    log(f"Remetente: {gmail_user}")
    log(f"Enviando para: {DESTINATARIO}")
    log(f"Assunto: {assunto}")

    ok = enviar_via_gmail(gmail_user, gmail_pass, DESTINATARIO, assunto, html)

    if ok:
        log("✅ E-mail enviado com sucesso!")
    else:
        log("❌ Falha no envio. Veja erros acima.")
        sys.exit(1)


if __name__ == "__main__":
    main()
