from insomniac.actions_impl import open_user_followers, iterate_over_followers, scroll_to_bottom
from insomniac.actions_types import RemoveMassFollowerAction, GetProfileAction
from insomniac.extra_features.actions_impl import remove_mass_follower
from insomniac.limits import process_limits
from insomniac.sleeper import sleeper
from insomniac.softban_indicator import softban_indicator
from insomniac.utils import *
from insomniac.views import ProfileView


def remove_mass_followers(device,
                          storage,
                          is_limit_reached,
                          session_state,
                          action_status,
                          max_following,
                          on_action):
    if not open_user_followers(device=device, username=None):
        return

    scroll_to_bottom(device)

    # noinspection PyUnusedLocal
    # follower_name_view is a standard callback argument
    def iteration_callback_pre_conditions(follower_name, follower_name_view):
        """
        :return: True to check whether user is mass follower, False to skip
        """
        if storage.is_user_in_whitelist(follower_name):
            print(f"@{follower_name} is in whitelist. Skip.")
            return False

        return True

    def iteration_callback(follower_name, follower_name_view):
        """
        :return: True to continue searching for mass followers after given user, False to stop
        """
        is_interact_limit_reached, interact_reached_source_limit, interact_reached_session_limit = \
            is_limit_reached(RemoveMassFollowerAction(user=follower_name), session_state)

        if not process_limits(is_interact_limit_reached, interact_reached_session_limit,
                              interact_reached_source_limit, action_status, "Removing mass followers"):
            return False

        is_get_profile_limit_reached, get_profile_reached_source_limit, get_profile_reached_session_limit = \
            is_limit_reached(GetProfileAction(user=follower_name), session_state)

        if not process_limits(is_get_profile_limit_reached, get_profile_reached_session_limit,
                              get_profile_reached_source_limit, action_status, "Get-Profile"):
            return False

        print("Open @" + follower_name)
        follower_name_view.click()
        on_action(GetProfileAction(user=follower_name))

        if softban_indicator.detect_empty_profile(device):
            print("Back to following list")
            device.back()
            return True

        is_mass_follower = _is_mass_follower(device, follower_name, max_following)
        device.back()

        if is_mass_follower:
            print(COLOR_OKGREEN + "@" + follower_name + " is mass follower, remove." + COLOR_ENDC)
            if not remove_mass_follower(device, follower_name_view):
                return False
            on_action(RemoveMassFollowerAction(user=follower_name))

        return True

    iterate_over_followers(device,
                           is_myself=True,
                           iteration_callback_pre_conditions=iteration_callback_pre_conditions,
                           iteration_callback=iteration_callback,
                           check_item_was_removed=True)


def _is_mass_follower(device, username, max_following):
    profile_view = ProfileView(device)
    followings = profile_view.get_following_count()
    print("@" + username + " has " + str(followings) + " followings")
    return followings is not None and followings > max_following
