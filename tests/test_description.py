from app.services.description import rich_description, sanitize_description


def test_sanitizes_description_and_preserves_safe_formatting() -> None:
    value = """
    <p>Build <strong>mobile apps</strong> with <em>care</em>.</p>
    <script>alert('x')</script>
    <a href="javascript:alert('x')">Unsafe</a>
    <a href="https://example.com/job">Apply</a>
    """

    result = sanitize_description(value)

    assert result is not None
    assert "<strong>mobile apps</strong>" in result
    assert "<em>care</em>" in result
    assert "script" not in result
    assert "javascript" not in result
    assert '<a href="https://example.com/job">Apply</a>' in result


def test_reads_rich_description_from_source_payload() -> None:
    result = rich_description(
        [("jobicy", '{"jobDescription":"<p>Hello <strong>world</strong>.</p>"}')]
    )

    assert result == "<p>Hello <strong>world</strong>.</p>"
