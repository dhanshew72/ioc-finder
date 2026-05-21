from src.utils.markdown import strip_markdown_fences


def test_no_fences_returns_unchanged():
    assert strip_markdown_fences('{"key": "value"}') == '{"key": "value"}'

def test_json_fence():
    assert strip_markdown_fences("```json\n{}\n```") == "{}\n```"

def test_plain_fences_stripped():
    result = strip_markdown_fences("```\nhello\n```")
    assert result == "hello"

def test_language_specifier_stripped():
    result = strip_markdown_fences("```json\n{}\n")
    assert result == "{}"


def test_leading_trailing_whitespace_stripped():
    result = strip_markdown_fences("  ```\nhello\n```  ")
    assert result == "hello"


def test_inner_whitespace_preserved():
    result = strip_markdown_fences("```\n  indented\n```")
    assert result == "indented"


def test_multiline_content():
    result = strip_markdown_fences("```json\n{\n  \"a\": 1\n}\n```")
    assert result == '{\n  "a": 1\n}'


def test_empty_string():
    assert strip_markdown_fences("") == ""


def test_only_whitespace():
    assert strip_markdown_fences("   ") == ""


def test_fences_with_no_body():
    result = strip_markdown_fences("```\n```")
    assert result == ""


def test_no_closing_fence_returns_content():
    result = strip_markdown_fences("```\nhello")
    assert result == "hello"


def test_non_fence_backticks_unchanged():
    result = strip_markdown_fences("`inline code`")
    assert result == "`inline code`"
