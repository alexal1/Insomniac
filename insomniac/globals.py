# These constants can be set by the external UI-layer process, don't change them manually
is_ui_process = False
execution_id = ''
task_id = ''
executable_name = 'insomniac'
do_location_permission_dialog_checks = True  # no need in these checks if location permission is denied beforehand


def callback(profile_name):
    pass


hardban_detected_callback = callback
softban_detected_callback = callback


def is_insomniac():
    return execution_id == ''
