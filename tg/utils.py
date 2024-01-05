__markdown_v2_escape_characters = (
    '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!')


def markdown_v2_escape(s: str):
    if s is None:
        return s

    for character in __markdown_v2_escape_characters:
        s = s.replace(character, '\\' + character)
    return s


def markdown_v2_bold(s: str):
    if s is None:
        return s
    return '*' + markdown_v2_escape(s) + '*'
