from insomniac.navigation import switch_to_english, LanguageChangedException
from insomniac.utils import *


def parse(device, text):
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
    try:
        count = int(float(text) * multiplier)
    except ValueError as ex:
        print_timeless(COLOR_FAIL + "Cannot parse \"" + text + "\". Probably wrong language, will set English now." +
                       COLOR_ENDC)
        save_crash(device, ex)
        switch_to_english(device)
        raise LanguageChangedException()
    return count
