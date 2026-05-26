import unittest
from extraction.utils.markdown import strip_markdown_fences


class TestStripMarkdownFences(unittest.TestCase):

    def test_no_fences_returns_unchanged(self):
        self.assertEqual(strip_markdown_fences('{"key": "value"}'), '{"key": "value"}')

    def test_plain_fences_stripped(self):
        self.assertEqual(strip_markdown_fences("```\nhello\n```"), "hello")

    def test_language_specifier_stripped(self):
        self.assertEqual(strip_markdown_fences("```json\n{}\n"), "{}")

    def test_leading_trailing_whitespace_stripped(self):
        self.assertEqual(strip_markdown_fences("  ```\nhello\n```  "), "hello")

    def test_inner_whitespace_preserved(self):
        self.assertEqual(strip_markdown_fences("```\n  indented\n```"), "indented")

    def test_multiline_content(self):
        self.assertEqual(
            strip_markdown_fences("```json\n{\n  \"a\": 1\n}\n```"),
            '{\n  "a": 1\n}',
        )

    def test_empty_string(self):
        self.assertEqual(strip_markdown_fences(""), "")

    def test_only_whitespace(self):
        self.assertEqual(strip_markdown_fences("   "), "")

    def test_fences_with_no_body(self):
        self.assertEqual(strip_markdown_fences("```\n```"), "")

    def test_no_closing_fence_returns_content(self):
        self.assertEqual(strip_markdown_fences("```\nhello"), "hello")

    def test_non_fence_backticks_unchanged(self):
        self.assertEqual(strip_markdown_fences("`inline code`"), "`inline code`")
