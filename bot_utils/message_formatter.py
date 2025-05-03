from datetime import datetime

def format_discount(current, previous):
    if current < previous:
        sconto = int(round((previous - current) / previous * 100))
        return f"\n<b>🔥 SCONTO {sconto}%</b>"
    elif current > previous:
        aumento = int(round((current - previous) / previous * 100))
        return f"\n<b>📈 AUMENTATO DEL {aumento}%</b>"
    return ""

def format_price_info(current, previous, updated_at):
    try:
        updated_at_str = datetime.strptime(str(updated_at), "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y")
    except Exception:
        updated_at_str = str(updated_at)

    info = f"<b>PREZZO ATTUALE</b>: {current} € <i>(aggiornato il {updated_at_str})</i>\n"
    info += f"<b>PREZZO PRECEDENTE</b>: {previous} €"
    return info
