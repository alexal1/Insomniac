from enum import unique, Enum

from insomniac.utils import *
from insomniac.views import ProfileView, FollowersFollowingListView, DialogView

EMPTY_LIST_TRESHOLD = 5
EMPTY_PROFILE_TRESHOLD = 5
ACTION_BLOCKED_DIALOG_TRESHOLD = 1


should_indicate_softban = True


def check_softban_feature_flag(func):
    def wrap(*args, **kwargs):
        is_indication_exists = False
        if should_indicate_softban:
            is_indication_exists = func(*args, **kwargs)
        return is_indication_exists
    return wrap


class ActionBlockedError(Exception):
    pass


@unique
class IndicationType(Enum):
    EMPTY_LISTS = 'empty-lists'
    EMPTY_PROFILES = 'empty-profiles'
    ACTION_BLOCKED_DIALOGS = 'action-block-dialogs'


class SoftBanIndicator:
    def __init__(self):
        self.indications = {
            IndicationType.EMPTY_LISTS: {"curr": 0, "treshold": EMPTY_LIST_TRESHOLD},
            IndicationType.EMPTY_PROFILES: {"curr": 0, "treshold": EMPTY_PROFILE_TRESHOLD},
            IndicationType.ACTION_BLOCKED_DIALOGS: {"curr": 0, "treshold": ACTION_BLOCKED_DIALOG_TRESHOLD},
        }

    def indicate_block(self):
        for indicator, stats in self.indications.items():
            if stats['curr'] >= stats['treshold']:
                block_indication_message = f"Instagram-block indicated after finding {stats['curr']} {indicator.value}. " \
                                           f"Seems that action is blocked. Consider reinstalling Instagram app and " \
                                           f"be more careful with limits!"
                raise ActionBlockedError(block_indication_message)

    @check_softban_feature_flag
    def detect_empty_list(self, device):
        list_view = FollowersFollowingListView(device)
        is_list_empty_from_profiles = list_view.is_list_empty()
        if is_list_empty_from_profiles:
            print(COLOR_FAIL + "List of followers seems to be empty. "
                               "Counting that as a soft-ban indicator!" + COLOR_ENDC)
            self.indications[IndicationType.EMPTY_LISTS]["curr"] += 1
            self.indicate_block()

        return is_list_empty_from_profiles

    @check_softban_feature_flag
    def detect_empty_profile(self, device):
        profile_view = ProfileView(device)
        is_loaded = profile_view.wait_until_visible()
        if not is_loaded:
            print(COLOR_FAIL + "A profile-page seems to be empty. "
                               "Counting that as a soft-ban indicator!" + COLOR_ENDC)
            self.indications[IndicationType.EMPTY_PROFILES]["curr"] += 1
            self.indicate_block()
            return True
        return False

    @check_softban_feature_flag
    def detect_action_blocked_dialog(self, device):
        is_blocked = DialogView(device).is_visible()
        if is_blocked:
            print(COLOR_FAIL + "Probably block dialog is shown. "
                               "Counting that as a soft-ban indicator!" + COLOR_ENDC)
            self.indications[IndicationType.ACTION_BLOCKED_DIALOGS]["curr"] += 1
            self.indicate_block()

        return is_blocked


softban_indicator = SoftBanIndicator()
