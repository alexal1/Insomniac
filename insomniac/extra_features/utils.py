from croniter import croniter

import insomniac
from insomniac.utils import *

INSTAGRAM_CLONE_PREFIX = "com.insta"
AAPT_BINARY_NAME = "aapt"
DEVICE_AAPT_PATH = "/data/local/tmp/"


def new_identity(device_id, app_id):
    print("Send broadcast to create new identity")
    cmd = ("adb" + ("" if device_id is None else " -s " + device_id) +
           f" shell am broadcast -p com.applisto.appcloner -a com.applisto.appcloner.api.action.NEW_IDENTITY "
           f"--es package_name {app_id} "
           f"--ez clear_cache true "
           f"--ez delete_app_data true")
    cmd_res = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, shell=True, encoding="utf8")
    output = cmd_res.stdout.strip()
    print(output)


def is_at_working_hour(working_hours):
    start_work_hour, stop_work_hour = 1, 24

    if working_hours:
        start_work_hour, stop_work_hour = get_left_right_values(working_hours, "Working hours {}", (9, 21))

        if not (1 <= start_work_hour <= 24):
            print(COLOR_FAIL + "Working-hours left-boundary ({0}) is not valid. "
                               "Using (9) instead".format(start_work_hour) + COLOR_ENDC)
            start_work_hour = 9

        if not (1 <= stop_work_hour <= 24):
            print(COLOR_FAIL + "Working-hours right-boundary ({0}) is not valid. "
                               "Using (21) instead".format(stop_work_hour) + COLOR_ENDC)
            stop_work_hour = 21

    now = datetime.now()

    if not (start_work_hour <= now.hour < stop_work_hour):
        print("Current Time: {0} which is out of working-time range ({1}-{2})"
              .format(now.strftime("%H:%M:%S"), start_work_hour, stop_work_hour))
        next_execution = '0 {0} * * *'.format(start_work_hour)

        time_till_next_execution_seconds = (croniter(next_execution, now).get_next(datetime) - now).seconds + 60

        return False, time_till_next_execution_seconds

    return True, 0


def get_package_by_name(device_id, name) -> Optional[str]:
    """
    For cloned apps: lets you find package name by app name.
    """
    packages_command_output = execute_command("adb" + ("" if device_id is None else " -s " + device_id) +
                                              " shell pm list packages")
    if packages_command_output is None:
        return None
    packages = packages_command_output.split("\n")
    for package in packages:
        if not package.startswith(f"package:{INSTAGRAM_CLONE_PREFIX}"):
            continue
        package = package.replace("package:", "")

        # Find apk path for this package
        path = execute_command("adb" + ("" if device_id is None else " -s " + device_id) +
                               f" shell pm path {package}")
        if path is None:
            continue
        path = path.replace("package:", "")

        # Find app name via aapt (make sure aapt binary is in /data/local/tmp on the device)
        # Binaries are here https://github.com/Calsign/APDE/tree/master/APDE/src/main/assets/aapt-binaries
        app_name = execute_command("adb" + ("" if device_id is None else " -s " + device_id) +
                                   f" shell {DEVICE_AAPT_PATH}{AAPT_BINARY_NAME} d badging {path} "
                                   f"| grep \"application: label\" "
                                   f"| sed -n \"s/.*label\='\([^']*\)'.*/\\1/p\"")
        if app_name == name:
            return package
    return None


def count_installed_clones(device_id):
    packages_command_output = execute_command("adb" + ("" if device_id is None else " -s " + device_id) +
                                              " shell pm list packages")
    if packages_command_output is None:
        return 0
    packages = packages_command_output.split("\n")
    count = 0
    for package in packages:
        if package.startswith(f"package:{INSTAGRAM_CLONE_PREFIX}"):
            count += 1
    return count


def close_all_instagram_apps(device_id):
    all_apps_packages_ids = execute_command("adb" + ("" if device_id is None else " -s " + device_id) +
                                            f" shell ps " +
                                            f"| grep {INSTAGRAM_CLONE_PREFIX} " +
                                            "|  awk '{print $9}'")
    all_apps_packages_ids = {package_id.split(':')[0] for package_id in all_apps_packages_ids.split('\n') if package_id}
    for package_id in all_apps_packages_ids:
        if package_id:
            close_instagram(device_id, package_id)


def install_aapt_if_needed(device_id):
    """
    AAPT (Android Asset Packaging Tool) is a binary executable utility that helps us to gather more information from an
    apk file, such us app name. This function checks whether AAPT is installed and installs it if not.
    """
    if _is_aapt_working(device_id):
        return
    print("AAPT is missing, installing...")
    aapt_path = os.path.join(os.path.dirname(os.path.abspath(insomniac.__file__)), "assets", AAPT_BINARY_NAME)
    execute_command("adb" + ("" if device_id is None else " -s " + device_id) +
                    f" push {aapt_path} {DEVICE_AAPT_PATH}")
    # Make it executable
    execute_command("adb" + ("" if device_id is None else " -s " + device_id) +
                    f" shell chmod 755 {DEVICE_AAPT_PATH}{AAPT_BINARY_NAME}")


def _is_aapt_working(device_id) -> bool:
    aapt_test_output = execute_command("adb" + ("" if device_id is None else " -s " + device_id) +
                                       f" shell {DEVICE_AAPT_PATH}{AAPT_BINARY_NAME} v")
    return aapt_test_output is not None and len(aapt_test_output) > 0
