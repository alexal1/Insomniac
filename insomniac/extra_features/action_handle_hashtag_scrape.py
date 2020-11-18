from insomniac.actions_impl import ScrollEndDetector, open_likers, iterate_over_likers
from insomniac.actions_types import GetProfileAction, ScrapeAction
from insomniac.device_facade import DeviceFacade
from insomniac.limits import process_limits
from insomniac.navigation import search_for
from insomniac.utils import *


def handle_hashtag_scrape(device,
                          hashtag,
                          session_state,
                          storage,
                          on_action,
                          is_limit_reached,
                          is_passed_filters,
                          action_status):
    scrape_source = "#{0}".format(hashtag)

    def pre_conditions(liker_username, liker_username_view):
        if storage.is_user_in_blacklist(liker_username):
            print("@" + liker_username + " is in blacklist. Skip.")
            return False
        elif storage.check_user_was_scrapped(liker_username):
            print("@" + liker_username + ": already scraped. Skip.")
            return False
        elif is_passed_filters is not None:
            if not is_passed_filters(device, liker_username, ['BEFORE_PROFILE_CLICK']):
                storage.add_scrapped_user(username=liker_username, success=False)
                return False

        return True

    def scrape_liker(liker_username, liker_username_view):
        is_scrape_limit_reached, scrape_reached_source_limit, scrape_reached_session_limit = \
            is_limit_reached(ScrapeAction(source=scrape_source, user=liker_username), session_state)

        if not process_limits(is_scrape_limit_reached, scrape_reached_session_limit,
                              scrape_reached_source_limit, action_status, "Scrapping"):
            return False

        is_get_profile_limit_reached, get_profile_reached_source_limit, get_profile_reached_session_limit = \
            is_limit_reached(GetProfileAction(user=liker_username), session_state)

        if not process_limits(is_get_profile_limit_reached, get_profile_reached_session_limit,
                              get_profile_reached_source_limit, action_status, "Get-Profile"):
            return False

        print("@" + liker_username + ": scrape")
        liker_username_view.click()
        on_action(GetProfileAction(user=liker_username))

        if is_passed_filters is not None:
            if not is_passed_filters(device, liker_username):
                storage.add_scrapped_user(username=liker_username, success=False)
                # Continue to next follower
                print("Back to followers list")
                device.back()
                return True

        storage.add_target_user(liker_username)
        storage.add_scrapped_user(username=liker_username, success=True)
        on_action(ScrapeAction(source=scrape_source, user=liker_username))
        print("@" + liker_username + ": Scraped.")

        print("Back to followers list")
        device.back()

        return True

    extract_hashtag_likers_and_scrape(device, hashtag, scrape_liker, pre_conditions, on_action)


def extract_hashtag_likers_and_scrape(device, hashtag, iteration_callback, iteration_callback_pre_conditions, on_action):
    print("Scrapping #{0} recent-likers".format(hashtag))

    if not search_for(device, hashtag=hashtag, on_action=on_action):
        return

    # Switch to Recent tab
    print("Switching to Recent tab")
    tab_layout = device.find(resourceId='com.instagram.android:id/tab_layout',
                             className='android.widget.LinearLayout')
    tab_layout.child(index=1).click()
    random_sleep()

    # Open first post
    print("Opening the first post")
    first_post_view = device.find(resourceId='com.instagram.android:id/image_button',
                                  className='android.widget.ImageView',
                                  index=1)
    first_post_view.click()
    random_sleep()

    posts_list_view = device.find(resourceId='android:id/list',
                                  className='androidx.recyclerview.widget.RecyclerView')
    posts_end_detector = ScrollEndDetector(repeats_to_end=2)

    def pre_conditions(liker_username, liker_username_view):
        posts_end_detector.notify_username_iterated(liker_username)
        return iteration_callback_pre_conditions(liker_username, liker_username_view)

    while True:
        if not open_likers(device):
            print(COLOR_OKGREEN + "No likes, let's scroll down." + COLOR_ENDC)
            posts_list_view.scroll(DeviceFacade.Direction.BOTTOM)
            continue

        print("List of likers is opened.")
        posts_end_detector.notify_new_page()
        random_sleep()

        iterate_over_likers(device, iteration_callback, pre_conditions)

        if posts_end_detector.is_the_end():
            break
        else:
            posts_list_view.scroll(DeviceFacade.Direction.BOTTOM)
