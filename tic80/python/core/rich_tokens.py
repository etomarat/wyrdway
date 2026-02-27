def rich_token_match(text: str, index: int) -> tuple[int, int, int]:
    """Parses rich token at position.

    Returns tuple: (kind, glyph, next_index)
    - kind=0: no token at index (next_index advances by 1)
    - kind=1: glyph token `{g:<int>}`; glyph holds parsed id
    - kind=2: gap token `{gap}`
    - kind=3: separator token `{sep}`
    """
    s = str(text)
    n = len(s)
    i = int(index)
    if i < 0:
        i = 0
    if i >= n:
        return 0, -1, i + 1

    if s[i] != "{":
        return 0, -1, i + 1

    if i + 5 <= n and s[i:i + 5] == "{gap}":
        return 2, -1, i + 5
    if i + 5 <= n and s[i:i + 5] == "{sep}":
        return 3, -1, i + 5

    if i + 4 > n:
        return 0, -1, i + 1
    if s[i + 1] != "g" or s[i + 2] != ":":
        return 0, -1, i + 1

    j = i + 3
    if j >= n or s[j] < "0" or s[j] > "9":
        return 0, -1, i + 1
    while j < n and s[j] >= "0" and s[j] <= "9":
        j += 1
    if j >= n or s[j] != "}":
        return 0, -1, i + 1
    return 1, int(s[i + 3:j]), j + 1
