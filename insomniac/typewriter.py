import base64

import insomniac
from insomniac.utils import *

# Typewriter uses Android application (apk file) built from this repo: https://github.com/alexal1/InsomniacAutomator
# It provides IME (Input Method Editor) that replaces virtual keyboard with it's own one, which listens to specific
# broadcast messages and simulates key presses.
ADB_KEYBOARD_IME = "com.alexal1.adbkeyboard/.AdbIME"
ADB_KEYBOARD_APK = "ADBKeyboard.apk"
DELAY_MEAN = 200
DELAY_DEVIATION = 100
IME_MESSAGE_B64 = "ADB_INPUT_B64"
IME_CLEAR_TEXT = "ADB_CLEAR_TEXT"
EXTRA_MESSAGE = "msg"
EXTRA_DELAY_MEAN = "delay_mean"
EXTRA_DELAY_DEVIATION = "delay_deviation"


class Typewriter:
    is_adb_keyboard_set = False
    device_id = None

    def __init__(self, device_id):
        self.is_adb_keyboard_set = False
        self.device_id = device_id

    def set_adb_keyboard(self):
        if not self._is_adb_ime_existing():
            print("Installing ADB Keyboard to enable typewriting...")
            apk_path = os.path.join(os.path.dirname(os.path.abspath(insomniac.__file__)), "apk", ADB_KEYBOARD_APK)
            os.popen("adb" + ("" if self.device_id is None else " -s " + self.device_id)
                     + f" install {apk_path}").close()
        self.is_adb_keyboard_set = self._set_adb_ime()
        if not self.is_adb_keyboard_set:
            print(COLOR_FAIL + "Cannot setup ADB Keyboard. Don't worry! Fallback to text copy-pasting will be used."
                  + COLOR_ENDC)

    def write(self, view, text) -> bool:
        if not self.is_adb_keyboard_set:
            return False
        view.click()
        if not self.clear():
            return False
        text_b64 = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        extras = {
            EXTRA_MESSAGE: text_b64,
            EXTRA_DELAY_MEAN: DELAY_MEAN,
            EXTRA_DELAY_DEVIATION: DELAY_DEVIATION
        }
        self._send_broadcast(IME_MESSAGE_B64, extras)
        sleep_millis = DELAY_MEAN * len(text) + DELAY_DEVIATION
        sleep_secs = sleep_millis / 1000.0
        print_debug(f"Wait until text is typed: {sleep_secs} seconds")
        sleep(sleep_secs)
        return True

    def clear(self) -> bool:
        if not self.is_adb_keyboard_set:
            return False
        self._send_broadcast(IME_CLEAR_TEXT)
        return True

    def _set_adb_ime(self):
        attempts_count = 0
        while not self._is_adb_ime_existing():
            attempts_count += 1
            if attempts_count == 5:
                return False
            sleep(2)
        stream = os.popen("adb" + ("" if self.device_id is None else " -s " + self.device_id)
                          + f" shell ime set {ADB_KEYBOARD_IME}")
        output = stream.read()
        succeed = "selected" in output
        stream.close()
        return succeed

    def _is_adb_ime_existing(self):
        stream = os.popen("adb" + ("" if self.device_id is None else " -s " + self.device_id) + " shell ime list -a")
        output = stream.read()
        result = ADB_KEYBOARD_IME in output
        stream.close()
        return result

    def _send_broadcast(self, action, extras=None):
        command = "adb" + ("" if self.device_id is None else " -s " + self.device_id) \
                  + f" shell am broadcast -a {action}"
        if extras is not None:
            for key, value in extras.items():
                if isinstance(value, str):
                    command += f" --es {key} '{value}'"
                elif isinstance(value, int):
                    command += f" --ei {key} {value}"
                else:
                    print_debug(COLOR_FAIL + f"Unexpected broadcast extra: {value}" + COLOR_ENDC)
                    continue
        os.popen(command).close()
