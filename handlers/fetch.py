from services.http_service import fetch_remote


def fetch_url(request):
    url = request.args.get("url", "http://example.com")
    return {"url": url, "body": fetch_remote(url)}
