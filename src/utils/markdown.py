
"""
Strips mark down tags for LLM output
"""
def strip_markdown_fences(input_str: str) -> str:
    input_str = input_str.strip()
    if input_str.startswith("```"):
        input_str = input_str[input_str.index("\n") + 1:]
        input_str = input_str.strip().removesuffix("```")
    return input_str.strip()
