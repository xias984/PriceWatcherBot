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

def format_product_info(result_row, diff_price_row=None):
    name = result_row[1]
    price = result_row[2]
    url = result_row[3]
    asin = result_row[4]
    category = result_row[5]

    message = f"<b>NOME</b>: <a href='{url}'>{name}</a>\n<b>ASIN</b>: {asin}\n<b>CATEGORIA</b>: {category}"

    if diff_price_row and diff_price_row[0] is not None:
        current, previous, updated_at = diff_price_row
        try:
            updated_at_str = datetime.strptime(str(updated_at), "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y")
        except Exception:
            updated_at_str = str(updated_at)

        price_info = format_price_info(current, previous, updated_at_str)
        discount = format_discount(current, previous)
        message += f"\n{price_info}{discount}"
    else:
        message += f"\n<b>PREZZO</b>: {price} €"

    return message
