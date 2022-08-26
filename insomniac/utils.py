import base64
import os
import random
import re
import shutil
import string
import subprocess
import sys
import traceback
from datetime import datetime, timedelta
from random import randint
from subprocess import PIPE
from time import sleep
from typing import Optional

import colorama
from colorama import Fore, Style, AnsiToWin32

import insomniac.__version__ as __version__
import insomniac.globals as insomniac_globals

random.seed()
# Init colorama but set "wrap" to False to not replace sys.stdout with a proxy object. It's meaningless as
# sys.stdout is set to a custom Logger object in utils.py
colorama.init(wrap=False)


COLOR_HEADER = Fore.MAGENTA
COLOR_OKBLUE = Fore.BLUE
COLOR_OKGREEN = Fore.GREEN
COLOR_REPORT = Fore.YELLOW
COLOR_FAIL = Fore.RED
COLOR_ENDC = Style.RESET_ALL
COLOR_BOLD = Style.BRIGHT

ENGINE_LOGS_DIR_NAME = 'logs'
UI_LOGS_DIR_NAME = 'ui-logs'

INSTAGRAM_MAIN_ACTIVITY = "{0}/com.instagram.mainactivity.MainActivity"
APP_REOPEN_WARNING = "Warning: Activity not started, intent has been delivered to currently running top-most instance."


def get_instagram_version(device_id, app_id):
    stream = os.popen("adb" + ("" if device_id is None else " -s " + device_id) +
                      f" shell dumpsys package {app_id}")
    output = stream.read()
    version_match = re.findall('versionName=(\\S+)', output)
    if len(version_match) == 1:
        version = version_match[0]
    else:
        version = "not found"
    stream.close()
    return version


def versiontuple(v):
    return tuple(map(int, (v.split("."))))


def get_connected_devices_adb_ids():
    stream = os.popen('adb devices')
    output = stream.read()
    devices_count = len(re.findall('device\n', output))
    stream.close()

    if devices_count == 0:
        return []

    devices = set()
    for line in output.split('\n'):
        if '\tdevice' in line:
            devices.add(line.split('\t')[0])

    return devices


def check_adb_connection(device_id, wait_for_device):
    is_device_id_provided = device_id is not None

    while True:
        print_timeless("Looking for ADB devices...")
        stream = os.popen('adb devices')
        output = stream.read()
        devices_count = len(re.findall('device\n', output))
        stream.close()

        if not wait_for_device:
            break

        if devices_count == 0:
            print_timeless(COLOR_HEADER + "Couldn't find any ADB-device available, sleeping a bit and trying again..." + COLOR_ENDC)
            sleep(10)
            continue

        if not is_device_id_provided:
            break

        found_device = False
        for line in output.split('\n'):
            if device_id in line and 'device' in line:
                found_device = True
                break

        if found_device:
            break

        print_timeless(COLOR_HEADER + "Couldn't find ADB-device " + device_id + " available, sleeping a bit and trying again..." + COLOR_ENDC)
        sleep(10)
        continue

    is_ok = True
    message = "That's ok."
    if devices_count == 0:
        is_ok = False
        message = "Cannot proceed."
    elif devices_count > 1 and not is_device_id_provided:
        is_ok = False
        message = "Use --device to specify a device."

    print_timeless(("" if is_ok else COLOR_FAIL) + "Connected devices via adb: " + str(devices_count) + ". " + message +
                   COLOR_ENDC)
    return is_ok


def open_instagram(device_id, app_id) -> bool:
    """
    :return: true if IG app was opened, false if it was already opened
    """
    print("Open Instagram app")
    cmd = ("adb" + ("" if device_id is None else " -s " + device_id) +
           f" shell am start -n {INSTAGRAM_MAIN_ACTIVITY.format(app_id)}")

    cmd_res = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, shell=True, encoding="utf8")
    err = cmd_res.stderr.strip()
    if err:
        if err == APP_REOPEN_WARNING:
            return False
        else:
            print(COLOR_FAIL + err + COLOR_ENDC)
    return True


def open_instagram_with_url(device_id, app_id, url):
    print("Open Instagram app with url: {}".format(url))
    cmd = ("adb" + ("" if device_id is None else " -s " + device_id) +
           f" shell am start -a android.intent.action.VIEW -d {url} {app_id}")
    cmd_res = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, shell=True, encoding="utf8")
    err = cmd_res.stderr.strip()

    if err and err != APP_REOPEN_WARNING:
        print(COLOR_FAIL + err + COLOR_ENDC)
        return False

    return True


def close_instagram(device_id, app_id):
    print(f"Close Instagram app {app_id}")
    os.popen("adb" + ("" if device_id is None else " -s " + device_id) +
             f" shell am force-stop {app_id}").close()
    # Press HOME to leave a possible state of opened system dialog(s)
    os.popen("adb" + ("" if device_id is None else " -s " + device_id) +
             f" shell input keyevent 3").close()


def clear_instagram_data(device_id, app_id):
    print("Clear Instagram data")
    os.popen("adb" + ("" if device_id is None else " -s " + device_id) +
             f" shell pm clear {app_id}").close()


def execute_command(cmd, error_allowed=True) -> Optional[str]:
    try:
        cmd_res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf8")
    except IndexError:
        # There's a bug in some Python versions that raises this error https://github.com/python/cpython/pull/24777
        return None
    err = cmd_res.stderr
    out = cmd_res.stdout
    if err is not None:
        err = err.strip()
        if len(err) > 0:
            print(COLOR_FAIL + err.strip() + COLOR_ENDC)
            if not error_allowed:
                return None
    if out is not None:
        return out.strip()
    return None


def save_crash(device, ex=None):
    global print_log

    try:
        device.wake_up()

        directory_name = "Crash-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        try:
            os.makedirs(os.path.join("crashes", directory_name), exist_ok=False)
        except OSError:
            print(COLOR_FAIL + "Directory " + directory_name + " already exists." + COLOR_ENDC)
            return

        screenshot_format = ".png" if device.is_old() else ".jpg"
        try:
            device.screenshot(os.path.join("crashes", directory_name, "screenshot" + screenshot_format))
        except RuntimeError:
            print(COLOR_FAIL + "Cannot save screenshot." + COLOR_ENDC)

        view_hierarchy_format = ".xml"
        try:
            device.dump_hierarchy(os.path.join("crashes", directory_name, "view_hierarchy" + view_hierarchy_format))
        except RuntimeError:
            print(COLOR_FAIL + "Cannot save view hierarchy." + COLOR_ENDC)

        with open(os.path.join("crashes", directory_name, "logs.txt"), 'w', encoding="utf-8") as outfile:
            outfile.write(print_log)

            if ex:
                outfile.write("\n")
                outfile.write(describe_exception(ex))

        shutil.make_archive(os.path.join("crashes", directory_name), 'zip', os.path.join("crashes", directory_name))
        shutil.rmtree(os.path.join("crashes", directory_name))

        if insomniac_globals.is_insomniac():
            print(COLOR_OKGREEN + "Crash saved as \"crashes/" + directory_name + ".zip\"." + COLOR_ENDC)
            print(COLOR_OKGREEN + "Please attach this file if you gonna report the crash at" + COLOR_ENDC)
            print(COLOR_OKGREEN + "https://github.com/alexal1/Insomniac/issues\n" + COLOR_ENDC)
    except Exception as e:
        print(COLOR_FAIL + f"Could not save crash after an error. Crash-save-error: {str(e)}" + COLOR_ENDC)
        print(COLOR_FAIL + describe_exception(e) + COLOR_ENDC)


def print_copyright():
    if insomniac_globals.is_insomniac():
        print_timeless("\nIf you like this bot, please " + COLOR_BOLD + "give us a star" + COLOR_ENDC + ":")
        print_timeless(COLOR_BOLD + "https://github.com/alexal1/Insomniac\n" + COLOR_ENDC)


def _print_with_time_decorator(standard_print, print_time, debug, ui_log):
    def wrapper(*args, **kwargs):
        if insomniac_globals.is_ui_process and not ui_log:
            return

        if debug and not __version__.__debug_mode__:
            return

        global print_log
        if print_time:
            time = datetime.now().strftime("%m/%d %H:%M:%S")
            print_log += re.sub(r"\[\d+m", '', ("[" + time + "] " + str(*args, **kwargs) + "\n"))
            return standard_print("[" + time + "]", *args, **kwargs)
        else:
            print_log += re.sub(r"\[\d+m", '', (str(*args, **kwargs) + "\n"))
            return standard_print(*args, **kwargs)

    return wrapper


def get_value(count: str, name: str, default: int, max_count=None):
    return _get_value(count, name, default, max_count, is_float=False)


def get_float_value(count: str, name: str, default: float, max_count=None):
    return _get_value(count, name, default, max_count, is_float=True)


def _get_value(count, name, default, max_count, is_float):
    def print_error():
        print(COLOR_FAIL + name.format(default) + f". Using default value instead of \"{count}\", because it must be "
                                                  "either a number (e.g. 2) or a range (e.g. 2-4)." + COLOR_ENDC)

    parts = count.split("-")
    if len(parts) <= 0:
        value = default
        print_error()
    elif len(parts) == 1:
        try:
            value = float(count) if is_float else int(count)
            print(COLOR_BOLD + name.format(value, "%.2f") + COLOR_ENDC)
        except ValueError:
            value = default
            print_error()
    elif len(parts) == 2:
        try:
            value = random.uniform(float(parts[0]), float(parts[1])) if is_float \
                else randint(int(parts[0]), int(parts[1]))
            print(COLOR_BOLD + name.format(value, "%.2f") + COLOR_ENDC)
        except ValueError:
            value = default
            print_error()
    else:
        value = default
        print_error()

    if max_count is not None and value > max_count:
        print(COLOR_FAIL + name.format(max_count) + f". This is max value." + COLOR_ENDC)
        value = max_count
    return value


def is_zero_value(count: str) -> bool:
    parts = count.split("-")
    if len(parts) == 1:
        try:
            return float(count) == 0
        except ValueError:
            pass
    return False


def get_left_right_values(left_right_str, name, default):
    def print_error():
        print(COLOR_FAIL + name.format(default) + f". Using default value instead of \"{left_right_str}\", because it "
                                                  "must be either a number (e.g. 2) or a range (e.g. 2-4)." + COLOR_ENDC)

    parts = left_right_str.split("-")
    if len(parts) <= 0:
        value = default
        print_error()
    elif len(parts) == 1:
        try:
            value = (int(left_right_str), int(left_right_str))
            print(COLOR_BOLD + name.format(value) + COLOR_ENDC)
        except ValueError:
            value = default
            print_error()
    elif len(parts) == 2:
        try:
            value = (int(parts[0]), int(parts[1]))
            print(COLOR_BOLD + name.format(value) + COLOR_ENDC)
        except ValueError:
            value = default
            print_error()
    else:
        value = default
        print_error()
    return value


def get_from_to_timestamps_by_hours(hours):
    """Returns a tuple of two timestamps: (given number of hours before; current time)"""

    return get_from_to_timestamps_by_minutes(hours*60)


def get_from_to_timestamps_by_minutes(minutes):
    """Returns a tuple of two timestamps: (given number of minutes before; current time)"""

    time_to = datetime.now().timestamp()
    delta = timedelta(minutes=minutes).total_seconds()
    time_from = time_to - delta

    return time_from, time_to


def get_count_of_nums_in_str(str_to_check):
    count = 0
    for i in range(0, 10):
        count += str_to_check.count(str(i))

    return count


def get_random_string(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def describe_exception(ex, with_stacktrace=True, context=None):
    exception_context = f'({context}): ' if context is not None else ''
    trace = ''.join(traceback.format_exception(type(ex), value=ex, tb=ex.__traceback__)) if with_stacktrace else ''
    description = f"{exception_context}Error - {str(ex)}\n{trace}"

    return description


def split_list_items_with_separator(original_list, separator):
    values = []
    for record in original_list:
        for value in record.split(separator):
            stripped_value = value.strip()
            if stripped_value:
                values.append(stripped_value)
    return values


def to_base_64(text):
    text_bytes = text.encode(encoding='UTF-8', errors='strict')
    base64_bytes = base64.b64encode(text_bytes)
    base64_text = base64_bytes.decode(encoding='UTF-8', errors='strict')
    return base64_text


def from_base_64(base64_text):
    base64_bytes = base64_text.encode(encoding='UTF-8', errors='strict')
    text_bytes = base64.b64decode(base64_bytes)
    text = text_bytes.decode(encoding='UTF-8', errors='strict')
    return text


def _get_logs_dir_name():
    if insomniac_globals.is_ui_process:
        return UI_LOGS_DIR_NAME
    return ENGINE_LOGS_DIR_NAME


def _get_log_file_name(logs_directory_name):
    os.makedirs(os.path.join(logs_directory_name), exist_ok=True)
    curr_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    log_name = f"{insomniac_globals.executable_name}_log-{curr_time}{'-'+insomniac_globals.execution_id if insomniac_globals.execution_id != '' else ''}.log"
    log_path = os.path.join(logs_directory_name, log_name)
    return log_path


class Timer:

    duration = None
    start_time = None
    end_time = None

    def __init__(self, seconds):
        self.duration = timedelta(seconds=seconds)
        self.start()

    def start(self):
        self.start_time = datetime.now()
        self.end_time = self.start_time + self.duration

    def is_expired(self):
        return datetime.now() > self.end_time

    def get_seconds_left(self):
        time_since_start = datetime.now() - self.start_time
        if time_since_start >= self.duration:
            return 0
        else:
            return int((self.duration - time_since_start).total_seconds())


class Logger(object):
    is_log_initiated = False

    def __init__(self):
        sys.stdout.reconfigure(encoding='utf-8')
        self.wrapped_stdout = AnsiToWin32(sys.stdout)
        self.terminal = self.wrapped_stdout.stream
        self.log = None

    def _init_log(self):
        if not self.is_log_initiated:
            self.log = AnsiToWin32(open(_get_log_file_name(_get_logs_dir_name()), "a", encoding="utf-8")).stream
            self.is_log_initiated = True

    def write(self, message):
        if not insomniac_globals.is_insomniac():
            message = re.sub("(?i)insomniac", "nomix", message)
        self._init_log()
        self.terminal.write(message)
        self.terminal.flush()
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self._init_log()
        self.terminal.flush()
        self.log.flush()

    def fileno(self):
        return self.wrapped_stdout.wrapped.fileno()


sys.stdout = Logger()
print_log = ""
print_timeless = _print_with_time_decorator(print, False, False, False)
print_timeless_ui = _print_with_time_decorator(print, False, False, True)
print_debug = _print_with_time_decorator(print, True, True, False)
print_ui = _print_with_time_decorator(print, True, False, True)
print_debug_ui = _print_with_time_decorator(print, True, True, True)
print = _print_with_time_decorator(print, True, False, False)
