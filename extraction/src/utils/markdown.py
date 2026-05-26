
def strip_markdown_fences(input_str: str) -> str:
    """
    Removes markdown fences from input string
    :param input_str: text with possible markdown fences
    :return: text without markdown fences
    """
    input_str = input_str.strip()
    if input_str.startswith("```"):
        input_str = input_str[input_str.index("\n") + 1:]
        input_str = input_str.strip().removesuffix("```")
    return input_str.strip()
