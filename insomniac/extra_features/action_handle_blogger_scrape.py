from insomniac.actions_impl import open_user_followers, \
    scroll_to_bottom, iterate_over_followers, open_user_followings
from insomniac.actions_types import GetProfileAction, ScrapeAction, BloggerInteractionType, SourceType
from insomniac.limits import process_limits
from insomniac.report import print_short_scrape_report
from insomniac.sleeper import sleeper
from insomniac.softban_indicator import softban_indicator
from insomniac.utils import *


def handle_blogger_scrape(device,
                          username,
                          instructions,
                          session_state,
                          storage,
                          on_action,
                          is_limit_reached,
                          is_passed_filters,
                          action_status):
    is_myself = username == session_state.my_username
    source_type = f'{SourceType.BLOGGER.value}-{instructions.value}'

    if instructions == BloggerInteractionType.FOLLOWERS:
        if not open_user_followers(device=device, username=username, on_action=on_action):
            return
    elif instructions == BloggerInteractionType.FOLLOWING:
        if not open_user_followings(device=device, username=username, on_action=on_action):
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
        elif storage.check_user_was_filtered(follower_name):
            print("@" + follower_name + ": already filtered. Skip.")
            return False

        return True

    def scrape_profile(follower_name, follower_name_view):
        is_scrape_limit_reached, scrape_reached_source_limit, scrape_reached_session_limit = \
            is_limit_reached(ScrapeAction(source_name=username, source_type=source_type, user=follower_name), session_state)

        if not process_limits(is_scrape_limit_reached, scrape_reached_session_limit,
                              scrape_reached_source_limit, action_status, "Scrapping"):
            return False

        is_get_profile_limit_reached, get_profile_reached_source_limit, get_profile_reached_session_limit = \
            is_limit_reached(GetProfileAction(user=follower_name), session_state)

        if not process_limits(is_get_profile_limit_reached, get_profile_reached_session_limit,
                              get_profile_reached_source_limit, action_status, "Get-Profile"):
            return False

        is_all_filters_satisfied = False
        if is_passed_filters is not None:
            print_debug(f"Running filter-ahead on @{follower_name}")
            should_continue, is_all_filters_satisfied = is_passed_filters(device, follower_name, reset=True,
                                                                          filters_tags=['BEFORE_PROFILE_CLICK'])
            if not should_continue:
                return True

            if not is_all_filters_satisfied:
                print_debug("Not all filters are satisfied with filter-ahead, continue filtering inside the profile-page")

        print("@" + follower_name + ": scrape")
        if not is_all_filters_satisfied:
            follower_name_view.click()
            on_action(GetProfileAction(user=follower_name))

            if softban_indicator.detect_empty_profile(device):
                print("Back to followers list")
                device.back()
                return True

            if is_passed_filters is not None:
                should_continue, _ = is_passed_filters(device, follower_name, reset=False)
                if not should_continue:
                    # Continue to next follower
                    print("Back to followers list")
                    device.back()
                    return True

            print("Back to followers list")
            device.back()

        on_action(ScrapeAction(source_name=username, source_type=source_type, user=follower_name))
        print("@" + follower_name + ": Scraped.")
        print_short_scrape_report(session_state)

        return True

    iterate_over_followers(device, is_myself, scrape_profile, pre_conditions)
