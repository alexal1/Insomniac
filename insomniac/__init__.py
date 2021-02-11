import argparse

import insomniac.__version__ as __version__
from insomniac.activation import activation_controller
from insomniac.params import parse_arguments
from insomniac.utils import *


def run(activation_code=""):
    if not __version__.__debug_mode__:
        print_timeless(COLOR_OKGREEN + __version__.__logo__ + COLOR_ENDC)
        print_version()

    activation_code_from_args = _get_activation_code_from_args()
    if activation_code_from_args is not None:
        activation_code = activation_code_from_args

    activation_controller.validate(activation_code)
    if not activation_controller.is_activated:
        from insomniac.session import InsomniacSession
        print_timeless("Using insomniac session-manager without extra-features")
        insomniac_session = InsomniacSession()
    else:
        from insomniac.extra_features.session import ExtendedInsomniacSession
        insomniac_session = ExtendedInsomniacSession()

    insomniac_session.run()


def _get_activation_code_from_args():
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--activation-code')
    try:
        args, _ = parser.parse_known_args()
    except (argparse.ArgumentError, TypeError):
        return None
    return args.activation_code


class ArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        pass
