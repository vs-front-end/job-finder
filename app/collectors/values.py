from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import UTC, datetime
from html import unescape

from bs4 import BeautifulSoup


def text(value: object, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def identifier(value: object) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    return ""


def number(value: object) -> float | None:
    if isinstance(value, int | float) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", ""))
        except ValueError:
            return None
    return None


def mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, dict) else {}


def list_of_mappings(value: object) -> list[Mapping[str, object]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def list_of_text(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def parse_datetime(value: object) -> datetime | None:
    if isinstance(value, int | float) and not isinstance(value, bool):
        divisor = 1000 if value > 10_000_000_000 else 1
        try:
            return datetime.fromtimestamp(value / divisor, tz=UTC)
        except (OverflowError, OSError, ValueError):
            return None
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
        return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed
    except ValueError:
        for pattern in ("%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%d", "%d %b %Y"):
            try:
                parsed = datetime.strptime(value.strip(), pattern)
                return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed
            except ValueError:
                continue
    return None


def html_to_text(value: object) -> str:
    raw = text(value)
    if not raw:
        return ""
    paragraph = "__JOB_FINDER_PARAGRAPH__"
    line = "__JOB_FINDER_LINE__"
    soup = BeautifulSoup(unescape(raw), "html.parser")
    for node in soup.find_all("br"):
        node.replace_with(line)
    for node in soup.find_all("li"):
        node.insert_before(f"{line}• ")
        node.append(line)
    for node in soup.find_all(
        ["p", "div", "section", "article", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol"]
    ):
        node.append(paragraph)
    result = soup.get_text(" ", strip=True).replace(paragraph, "\n\n").replace(line, "\n")
    result = re.sub(r"[ \t\xa0]+", " ", result)
    result = re.sub(r" *\n *", "\n", result)
    result = re.sub(r"\n{2,}(?=• )", "\n", result)
    result = re.sub(r"\n{3,}", "\n\n", result)
    result = re.sub(r"\(\s+", "(", result)
    result = re.sub(r"\s+\)", ")", result)
    return re.sub(r"\s+([,.;:!?])", r"\1", result).strip()
