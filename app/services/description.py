from __future__ import annotations

import json
from html import unescape
from urllib.parse import urlsplit

from bs4 import BeautifulSoup, Comment

ALLOWED_TAGS = {
    "a",
    "b",
    "blockquote",
    "br",
    "code",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "i",
    "li",
    "ol",
    "p",
    "pre",
    "strong",
    "u",
    "ul",
}
BLOCKED_TAGS = {
    "button",
    "embed",
    "form",
    "iframe",
    "input",
    "noscript",
    "object",
    "script",
    "style",
    "svg",
}


def description_fields(source: str) -> tuple[str, ...]:
    if source.startswith("greenhouse:"):
        return ("content",)
    if source.startswith("ashby:"):
        return ("descriptionHtml", "descriptionPlain")
    if source.startswith("manual:"):
        return ("description",)
    fields = {
        "arc": ("description",),
        "arbeitnow": ("description",),
        "get_on_board": ("description",),
        "hacker_news": ("comment_text",),
        "himalayas": ("description",),
        "jobicy": ("jobDescription",),
        "remote_ok": ("description",),
        "remotive": ("description",),
        "startup_jobs": ("description",),
        "the_muse": ("contents",),
        "we_work_remotely": ("summary",),
    }
    return fields.get(source, ())


def rich_description(source_payloads: list[tuple[str, str | None]]) -> str | None:
    for source, raw in source_payloads:
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        markup = _markup(source, payload)
        sanitized = sanitize_description(markup)
        if sanitized:
            return sanitized
    return None


def sanitize_description(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    soup = BeautifulSoup(unescape(value), "html.parser")
    if not soup.find(list(ALLOWED_TAGS)):
        return None
    for node in soup.find_all(BLOCKED_TAGS):
        node.decompose()
    for comment in soup.find_all(string=lambda item: isinstance(item, Comment)):
        comment.extract()
    for node in soup.find_all(True):
        if node.name == "b":
            node.name = "strong"
        if node.name == "i":
            node.name = "em"
        if node.name not in ALLOWED_TAGS:
            node.unwrap()
            continue
        if node.name == "a":
            href = node.attrs.get("href")
            node.attrs = {"href": href} if isinstance(href, str) and _safe_href(href) else {}
            continue
        node.attrs = {}
    return "".join(str(node) for node in soup.contents).strip() or None


def _markup(source: str, payload: dict[str, object]) -> str | None:
    if source.startswith("lever:"):
        parts = [payload.get("description"), payload.get("additional")]
        lists = payload.get("lists")
        if isinstance(lists, list):
            for section in lists:
                if not isinstance(section, dict):
                    continue
                title = section.get("text")
                content = section.get("content")
                if isinstance(title, str):
                    parts.append(f"<h3>{title}</h3>")
                parts.append(content)
        markup = "".join(part for part in parts if isinstance(part, str))
        return markup or None
    for field in description_fields(source):
        value = payload.get(field)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _safe_href(value: str) -> bool:
    return urlsplit(value.strip()).scheme.lower() in {"http", "https", "mailto"}
