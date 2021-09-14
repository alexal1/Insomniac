from insomniac.utils import *


class HardBanError(Exception):
    pass


class HardBanIndicator:

    WEBVIEW_ACTIVITY_NAME = 'com.instagram.simplewebview.SimpleWebViewActivity'

    def detect_webview(self, device):
        """
        While "hard banned" Instagram shows you a webview with CAPTCHA and request to confirm your account. So what we
        need is to simply detect that topmost activity is a webview.
        """
        device_id = device.device_id
        app_id = device.app_id
        resumed_activity_output = execute_command("adb" + ("" if device_id is None else " -s " + device_id) +
                                                  f" shell dumpsys activity | grep 'mResumedActivity'")

        max_attempts = 3
        attempt = 1
        while attempt <= max_attempts:
            sleep(1)
            full_webview_activity_name = f"{app_id}/{self.WEBVIEW_ACTIVITY_NAME}"
            if resumed_activity_output is not None and full_webview_activity_name in resumed_activity_output:
                print(COLOR_FAIL + "WebView is shown. Counting that as a hard-ban indicator!" + COLOR_ENDC)
                self.indicate_ban()
                return
            attempt += 1

    def indicate_ban(self):
        raise HardBanError("Hard ban indicated!")


hardban_indicator = HardBanIndicator()
