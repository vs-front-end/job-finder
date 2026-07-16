from __future__ import annotations

import re
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_PARAMETERS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gh_src",
    "lever-source",
}


def canonicalize_url(value: str) -> str:
    parts = urlsplit(value.strip())
    scheme = parts.scheme.lower() or "https"
    host = parts.hostname.lower() if parts.hostname else ""
    port = f":{parts.port}" if parts.port and parts.port not in {80, 443} else ""
    netloc = f"{parts.username + '@' if parts.username else ''}{host}{port}"
    query_items = [
        (key, item)
        for key, item in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() not in TRACKING_PARAMETERS and not _domain_tracking(host, key)
    ]
    path = parts.path or "/"
    return urlunsplit((scheme, netloc, path, urlencode(query_items, doseq=True), ""))


def _domain_tracking(host: str, key: str) -> bool:
    lowered = key.lower()
    return lowered in {"source", "ref"} and host.endswith(
        ("greenhouse.io", "lever.co", "ashbyhq.com")
    )


def normalize_identity(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", ascii_value.lower()).strip()
