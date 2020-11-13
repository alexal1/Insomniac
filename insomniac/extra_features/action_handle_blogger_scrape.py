from functools import partial

from insomniac.actions_impl import interact_with_user, open_user_followers, \
    scroll_to_bottom, iterate_over_followers, InteractionStrategy, is_private_account
from insomniac.actions_runners import ActionState
from insomniac.actions_types import LikeAction, FollowAction, InteractAction, GetProfileAction, ScrapeAction
from insomniac.limits import process_limits
from insomniac.storage import FollowingStatus
from insomniac.utils import *


def handle_blogger_scrape(device,
                          username,
                          session_state,
                          storage,
                          on_action,
                          is_limit_reached,
                          is_passed_filters,
                          action_status):
    is_myself = username == session_state.my_username

    if not open_user_followers(device=device, username=username, on_action=on_action):
        return

    if is_myself:
        scroll_to_bottom(device)

    def pre_conditions(follower_name, follower_name_view):
        if storage.is_user_in_blacklist(follower_name):
            print("@" + follower_name + " is in blacklist. Skip.")
            return False
        elif storage.check_user_was_scrapped(follower_name):
            print("@" + follower_name + ": already scraped. Skip.")
            return False
        elif is_passed_filters is not None:
            if not is_passed_filters(device, follower_name, ['BEFORE_PROFILE_CLICK']):
                return False

        return True

    def scrape_follower(follower_name, follower_name_view):
        is_scrape_limit_reached, scrape_reached_source_limit, scrape_reached_session_limit = \
            is_limit_reached(ScrapeAction(source=username, user=follower_name), session_state)

        if not process_limits(is_scrape_limit_reached, scrape_reached_session_limit,
                              scrape_reached_source_limit, action_status, "Scrapping"):
            return False

        is_get_profile_limit_reached, get_profile_reached_source_limit, get_profile_reached_session_limit = \
            is_limit_reached(GetProfileAction(user=follower_name), session_state)

        if not process_limits(is_get_profile_limit_reached, get_profile_reached_session_limit,
                              get_profile_reached_source_limit, action_status, "Get-Profile"):
            return False

        print("@" + follower_name + ": scrape")
        follower_name_view.click()
        on_action(GetProfileAction(user=follower_name))

        if is_passed_filters is not None:
            if not is_passed_filters(device, follower_name):
                storage.add_scrapped_user(username=follower_name, success=False)
                # Continue to next follower
                print("Back to followers list")
                device.back()
                return True

        storage.add_target_user(follower_name)
        storage.add_scrapped_user(username=follower_name, success=True)
        on_action(ScrapeAction(source=username, user=follower_name))
        print("@" + follower_name + ": Scraped.")

        print("Back to followers list")
        device.back()

        return True

    iterate_over_followers(device, is_myself, scrape_follower, pre_conditions)
