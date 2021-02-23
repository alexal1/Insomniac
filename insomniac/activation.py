import base64
import zlib

from insomniac import network
from insomniac.__version__ import __version__
from insomniac.network import HTTP_OK
from insomniac.utils import *

HOST = "https://insomniac-bot.com"
PATH_VALIDATE = "/validate"
PATH_ACTIVATE = "/activate/"
PATH_EXTRA_FEATURE = "/extra-feature/"
PATH_UI_EXTRA_FEATURE = "/extra-feature/ui/"


class ActivationController:
    activation_code = ""
    is_activated = False

    def validate(self, activation_code, ui=False):
        self.activation_code = activation_code
        if not activation_code == "" and _validate(activation_code, ui):
            self.is_activated = True

        if not self.is_activated:
            dot = '\n    - '
            print_timeless(f"Hi! Since of v3.1.0 all core features in this project are free to use.\n"
                           f"You may want to get more fine grained control over the bot via these features:"
                           f"{dot}{COLOR_BOLD}Filtering{COLOR_ENDC} - skip unwanted accounts by various parameters"
                           f"{dot}{COLOR_BOLD}Scrapping{COLOR_ENDC} - technique that makes interactions "
                           f"significantly safer and faster"
                           f"{dot}{COLOR_BOLD}Working hours{COLOR_ENDC} - the script will wait till specified hours "
                           f"before each session"
                           f"{dot}{COLOR_BOLD}Removing mass followers{COLOR_ENDC} - automate \"cleaning\" you account"
                           f"{dot}{COLOR_BOLD}Analytics tool{COLOR_ENDC} - build presentation that shows your growth\n"
                           f"Activate by supporting our small team: {COLOR_BOLD}{HOST}{PATH_ACTIVATE}{COLOR_ENDC}\n")

    def get_extra_feature(self, module, ui=False):
        print_debug_ui(f"Getting extra-feature, module: {module}, is ui: {ui} ")
        extra_feature_path = PATH_UI_EXTRA_FEATURE if ui else PATH_EXTRA_FEATURE
        code, body, fail_reason = network.get(f"{HOST}{extra_feature_path}{module}"
                                              f"?activation_code={self.activation_code}"
                                              f"&version={__version__}")
        if code == HTTP_OK and body is not None:
            return base64.b64decode(zlib.decompress(body))

        print(COLOR_FAIL + f"Cannot get {'ui-' if ui else ''}module {module} from v{__version__}: "
                           f"{code} ({fail_reason})" + COLOR_ENDC)
        return None


def print_activation_required_to(action):
    print_timeless(COLOR_FAIL + f"\nActivate the bot to {action}:\n" + COLOR_BOLD + f"{HOST}{PATH_ACTIVATE}" +
                   COLOR_ENDC)


def _validate(activation_code, ui):
    code, _, fail_reason = network.get(f"{HOST}{PATH_VALIDATE}?activation_code={activation_code}{'&ui=true' if ui else ''}")
    if code == HTTP_OK:
        print(COLOR_OKGREEN + "Your activation code is confirmed, welcome!" + COLOR_ENDC)
        return True

    print(COLOR_FAIL + f"Activation code is not confirmed: {code} ({fail_reason})" + COLOR_ENDC)
    return False


class ActivationRequiredException(Exception):
    pass


activation_controller = ActivationController()
