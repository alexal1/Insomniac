from insomniac.utils import *
from insomniac.views import TabBarView, ProfileView, TabBarTabs, LanguageNotEnglishException, DialogView, OpenedPostView

SEARCH_CONTENT_DESC_REGEX = '[Ss]earch and [Ee]xplore'


def navigate(device, tab, switch_to_english_on_exception=True):
    try:
        TabBarView(device).navigate_to(tab)
    except LanguageNotEnglishException as ex:
        if not switch_to_english_on_exception:
            raise ex
        save_crash(device, ex)
        switch_to_english(device)
        raise LanguageChangedException()


def search_for(device, username=None, hashtag=None, place=None, on_action=None):
    search_view = TabBarView(device).navigate_to_search()
    target_view = None

    if username is not None:
        target_view = search_view.navigate_to_username(username, on_action)

    if hashtag is not None:
        target_view = search_view.navigate_to_hashtag(hashtag)

    if place is not None:
        target_view = search_view.navigate_to_place(place)

    return target_view is not None


def switch_to_english(device):
    print(COLOR_OKGREEN + "Switching to English locale" + COLOR_ENDC)
    navigate(device, TabBarTabs.PROFILE, switch_to_english_on_exception=False)
    ProfileView(device) \
        .navigate_to_options() \
        .navigate_to_settings() \
        .switch_to_english()


def open_instagram_with_network_check(device) -> bool:
    """
    :return: true if IG app was opened, false if it was already opened
    """
    print("Open Instagram app with network check")
    device_id = device.device_id
    app_id = device.app_id

    # Try via starter
    cmd = ("adb" + ("" if device_id is None else " -s " + device_id) +
           f" shell am start -a com.alexal1.starter.CHECK_CONNECTION_AND_LAUNCH_APP --es \"package\" \"{app_id}\"")
    cmd_res = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, shell=True, encoding="utf8")
    err = cmd_res.stderr.strip()
    if err:
        # Fallback to standard way
        print(COLOR_FAIL + "Didn't work :(" + COLOR_ENDC)
        return open_instagram(device_id, app_id)

    # Wait until Instagram is actually opened
    max_attempts = 10
    attempt = 0
    while True:
        sleep(5)
        attempt += 1
        resumed_activity_output = execute_command("adb" + ("" if device_id is None else " -s " + device_id) +
                                                  f" shell dumpsys activity | grep 'mResumedActivity'",
                                                  error_allowed=False)
        if resumed_activity_output is None:
            # Fallback to standard way
            print(COLOR_FAIL + "Didn't work :(" + COLOR_ENDC)
            return open_instagram(device_id, app_id)
        if app_id in resumed_activity_output:
            break

        if attempt < max_attempts:
            print(COLOR_OKGREEN + "Instagram is not yet opened, waiting..." + COLOR_ENDC)
            sleep(10)
        else:
            return open_instagram_with_network_check(device)
    return True


def close_instagram_and_system_dialogs(device):
    close_instagram(device.device_id, device.app_id)
    # If the app crashed there will be a system dialog
    DialogView(device).close_not_responding_dialog_if_visible()


def is_user_exists(device, username):
    return TabBarView(device).navigate_to_search().find_username(username)


def is_post_exists(device, post_link):
    if not open_instagram_with_url(device.device_id, device.app_id, post_link):
        return False
    is_post_opened = OpenedPostView(device).is_visible()
    device.back()
    return is_post_opened


class LanguageChangedException(Exception):
    pass


class InstagramOpener:

    INSTANCE = None

    device = None
    is_with_connection_check = False

    def __init__(self, device, is_with_connection_check):
        self.device = device
        self.is_with_connection_check = is_with_connection_check

    def open_instagram(self):
        if self.is_with_connection_check:
            open_instagram_with_network_check(self.device)
        else:
            open_instagram(self.device.device_id, self.device.app_id)
