from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

def amazonify(url, affiliate_tag):
    parsed = urlparse(url)
    if not parsed.netloc:
        return None

    # Estrai ASIN se presente nel path
    parts = parsed.path.split('/')
    asin = None
    if 'dp' in parts:
        dp_index = parts.index('dp')
        if dp_index + 1 < len(parts):
            asin = parts[dp_index + 1]

    # Costruisci URL compatto se possibile
    if asin:
        domain = parsed.netloc.split('.')[-1]
        return f"https://www.amazon.{domain}/dp/{asin}?tag={affiliate_tag}"
    
    # Fallback: aggiungi solo il tag alla URL originale
    query = dict(parse_qsl(parsed.query))
    query['tag'] = affiliate_tag
    new_query = urlencode(query)
    new_url = parsed._replace(query=new_query)

    return urlunparse(new_url)