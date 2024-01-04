from insomniac.actions_impl import ScrollEndDetector, open_likers, iterate_over_likers
from insomniac.actions_types import GetProfileAction, ScrapeAction, HashtagInteractionType, SourceType
from insomniac.limits import process_limits
from insomniac.navigation import search_for
from insomniac.report import print_short_scrape_report
from insomniac.safely_runner import RestartJobRequiredException
from insomniac.sleeper import sleeper
from insomniac.softban_indicator import softban_indicator
from insomniac.utils import *
from insomniac.views import PostsGridView


def handle_hashtag_scrape(device,
                          hashtag,
                          instructions,
                          session_state,
                          storage,
                          on_action,
                          is_limit_reached,
                          is_passed_filters,
                          action_status):
    source_type = f'{SourceType.HASHTAG.value}-{instructions.value}'

    def pre_conditions(liker_username, liker_username_view):
        if storage.is_user_in_blacklist(liker_username):
            print("@" + liker_username + " is in blacklist. Skip.")
            return False
        elif storage.check_user_was_scrapped(liker_username):
            print("@" + liker_username + ": already scraped. Skip.")
            return False
        elif storage.check_user_was_filtered(liker_username):
            print("@" + liker_username + ": already filtered. Skip.")
            return False

        return True

    def scrape_profile(liker_username, liker_username_view):
        is_scrape_limit_reached, scrape_reached_source_limit, scrape_reached_session_limit = \
            is_limit_reached(ScrapeAction(source_name=hashtag, source_type=source_type, user=liker_username), session_state)

        if not process_limits(is_scrape_limit_reached, scrape_reached_session_limit,
                              scrape_reached_source_limit, action_status, "Scrapping"):
            return False

        is_get_profile_limit_reached, get_profile_reached_source_limit, get_profile_reached_session_limit = \
            is_limit_reached(GetProfileAction(user=liker_username), session_state)

        if not process_limits(is_get_profile_limit_reached, get_profile_reached_session_limit,
                              get_profile_reached_source_limit, action_status, "Get-Profile"):
            return False

        is_all_filters_satisfied = False
        if is_passed_filters is not None:
            print_debug(f"Running filter-ahead on @{liker_username}")
            should_continue, is_all_filters_satisfied = is_passed_filters(device, liker_username, reset=True,
                                                                          filters_tags=['BEFORE_PROFILE_CLICK'])
            if not should_continue:
                return True

            if not is_all_filters_satisfied:
                print_debug("Not all filters are satisfied with filter-ahead, continue filtering inside the profile-page")

        print("@" + liker_username + ": scrape")
        if not is_all_filters_satisfied:
            liker_username_view.click()
            on_action(GetProfileAction(user=liker_username))

            if softban_indicator.detect_empty_profile(device):
                print("Back to followers list")
                device.back()
                return True

            if is_passed_filters is not None:
                should_continue, _ = is_passed_filters(device, liker_username, reset=False)
                if not should_continue:
                    # Continue to next follower
                    print("Back to followers list")
                    device.back()
                    return True

            print("Back to followers list")
            device.back()

        on_action(ScrapeAction(source_name=hashtag, source_type=source_type, user=liker_username))
        print("@" + liker_username + ": Scraped.")
        print_short_scrape_report(session_state)

        return True

    extract_hashtag_likers_and_scrape(device, hashtag, instructions, scrape_profile, pre_conditions, on_action)


def extract_hashtag_likers_and_scrape(device, hashtag, instructions, iteration_callback,
                                      iteration_callback_pre_conditions, on_action):
    print("Scrapping #{0}-{1}".format(hashtag, instructions.value))

    if not search_for(device, hashtag=hashtag, on_action=on_action):
        return

    # Switch to Recent tab
    if instructions == HashtagInteractionType.RECENT_LIKERS:
        print("Switching to Recent tab")
        tab_layout = device.find(resourceId=f'{device.app_id}:id/tab_layout',
                                 className='android.widget.LinearLayout')
        if tab_layout.exists():
            tab_layout.child(index=1).click()
        else:
            print("Can't Find recent tab. Interacting with Popular.")

    # Sleep longer because posts loading takes time
    sleeper.random_sleep(multiplier=2.0)

    # Open post
    posts_view_list = PostsGridView(device).open_random_post()
    if posts_view_list is None:
        return

    posts_end_detector = ScrollEndDetector(repeats_to_end=2)

    def pre_conditions(liker_username, liker_username_view):
        posts_end_detector.notify_username_iterated(liker_username)
        return iteration_callback_pre_conditions(liker_username, liker_username_view)

    no_likes_count = 0

    while True:
        if not open_likers(device):
            no_likes_count += 1
            print(COLOR_OKGREEN + "No likes, let's scroll down." + COLOR_ENDC)
            posts_view_list.scroll_down()
            if no_likes_count == 10:
                print(COLOR_FAIL + "Seen this message too many times. Lets restart the job." + COLOR_ENDC)
                raise RestartJobRequiredException

            continue

        no_likes_count = 0
        print("List of likers is opened.")
        posts_end_detector.notify_new_page()
        sleeper.random_sleep()

        should_continue_using_source = iterate_over_likers(device, iteration_callback, pre_conditions)

        if not should_continue_using_source:
            break

        if posts_end_detector.is_the_end():
            break
        else:
            posts_view_list.scroll_down()
