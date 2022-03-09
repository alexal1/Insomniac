# These constants can be set by the external UI-layer process, don't change them manually
from typing import Callable

is_ui_process = False
execution_id = ''
task_id = ''
executable_name = 'insomniac'
do_location_permission_dialog_checks = True  # no need in these checks if location permission is denied beforehand

hardban_detected_callback: Callable[[str], None] = lambda profile_name: None  # call when hard ban detected
softban_detected_callback: Callable[[str], None] = lambda profile_name: None  # call when soft ban detected
is_session_allowed_callback: Callable[[str, object], bool] = lambda: True  # call to check whether UI app allows this session


def is_insomniac():
    return execution_id == ''
