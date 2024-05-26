from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

def amazonify(url, affiliate_tag):
    new_url = urlparse(url)
    if not new_url.netloc:
        return None
    
    query = dict(parse_qsl(new_url.query))
    query['tag'] = affiliate_tag
    new_query = urlencode(query)
    new_url = new_url._replace(query=new_query)

    return urlunparse(new_url)