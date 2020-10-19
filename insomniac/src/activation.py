import urllib.request
from urllib.error import HTTPError, URLError

from ..src.utils import *

HOST = "https://insomniac-bot.com"
PATH_VALIDATE = "/validate"
MAX_FREE_INTERACTIONS_PER_DAY = 50


class ActivationController:
    is_activated = False
    last_day_interactions_count = 0

    def validate(self, activation_code):
        if activation_code == "":
            return

        if _validate(activation_code):
            self.is_activated = True

    def notify_interaction_made(self):
        self.last_day_interactions_count += 1
        if not self.is_activated and self.last_day_interactions_count >= MAX_FREE_INTERACTIONS_PER_DAY:
            raise ActivationRequiredException(f"\nSorry, but only {MAX_FREE_INTERACTIONS_PER_DAY} interactions per day "
                                              f"are allowed without activation.\n"
                                              f"Please activate your bot if you like it\n"
                                              f"https://insomniac-bot.com/activate/\n")


def _validate(activation_code):
    reason = None
    try:
        with urllib.request.urlopen(f"{HOST}{PATH_VALIDATE}?activation_code={activation_code}") as response:
            code = response.code
    except HTTPError as e:
        code = e.code
        reason = e.reason
    except URLError as e:
        code = -1
        reason = e.reason

    if code == 200:
        print("Your activation code is confirmed, welcome!")
        return True

    if reason is None:
        reason = "Unknown response code"

    print(COLOR_FAIL + f"Activation code is not confirmed: {code} ({reason})" + COLOR_ENDC)
    return False


class ActivationRequiredException(Exception):
    pass
