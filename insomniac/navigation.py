from insomniac.utils import *
from insomniac.views import TabBarView, ProfileView, TabBarTabs, LanguageNotEnglishException, DialogView

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


def close_instagram_and_system_dialogs(device):
    close_instagram(device.device_id, device.app_id)
    # If the app crashed there will be a system dialog
    DialogView(device).close_not_responding_dialog_if_visible()


class LanguageChangedException(Exception):
    pass
