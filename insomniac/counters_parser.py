def parse(text) -> int:
    """
    Parses given text.

    :return: parsed value or ValueError if couldn't parse
    """
    multiplier = 1
    text = text.replace(",", "")
    is_dot_in_text = False
    if '.' in text:
        text = text.replace(".", "")
        is_dot_in_text = True
    if "K" in text:
        text = text.replace("K", "")
        multiplier = 1000

        if is_dot_in_text:
            multiplier = 100

    if "M" in text:
        text = text.replace("M", "")
        multiplier = 1000000

        if is_dot_in_text:
            multiplier = 100000

    return int(float(text) * multiplier)
