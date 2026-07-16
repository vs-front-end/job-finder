from app.collectors.values import html_to_text


def test_html_to_text_preserves_blocks_without_breaking_inline_content() -> None:
    value = """
    <p>Build <strong>mobile applications</strong> with
    <a href="https://example.com">our team</a>.</p>
    <h2>Requirements</h2>
    <ul><li>React Native</li><li>Three years of experience</li></ul>
    """

    result = html_to_text(value)

    assert "Build mobile applications with our team." in result
    assert "\n\nRequirements\n" in result
    assert "• React Native\n• Three years of experience" in result
