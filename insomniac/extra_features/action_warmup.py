from insomniac.actions_impl import interact_with_feed
from insomniac.actions_types import LikeAction
from insomniac.navigation import navigate
from insomniac.sleeper import sleeper
from insomniac.utils import *
from insomniac.views import PostsViewList, TabBarTabs, PostsGridView, OpenedPostView

LIKE_CHANCE = 5  # chance is one of this amount each time


def warmup(device, warmup_time_mins, on_action):
    print_timeless("")
    warmup_time_secs = int(get_float_value(warmup_time_mins, "Warmup time before session starts: {:.2f} minutes", 2.0) * 60)

    # Warmup has two stages: 1. Scrolling and liking your feed and 2. Scrolling and liking Explore. So we will divide
    # available time into two parts randomly between 1/3 and 2/3 of the whole time.
    feed_time_secs = random.randint(round(warmup_time_secs / 3), round(warmup_time_secs * 2 / 3))
    explore_time_secs = warmup_time_secs - feed_time_secs

    _warmup_feed(device, feed_time_secs, on_action)
    _warmup_explore(device, explore_time_secs, on_action)

    print("Warmup is done. Time to work!")
    print_timeless("")
    navigate(device, TabBarTabs.PROFILE)
    sleeper.random_sleep()


def _warmup_feed(device, time_secs, on_action):
    print("Scrolling and liking the feed")
    start_time = datetime.now()

    def navigate_to_feed():
        navigate(device, TabBarTabs.HOME)
        sleeper.random_sleep()
        posts_views_list = PostsViewList(device)
        return posts_views_list

    def should_continue():
        diff_in_secs = int((datetime.now() - start_time).total_seconds())
        return diff_in_secs < time_secs

    def interact_with_feed_post(posts_views_list):
        if randint(1, LIKE_CHANCE) == LIKE_CHANCE:
            print_debug("Like post")
            opened_post_view = posts_views_list.get_current_post()
            author_name = opened_post_view.get_author_name()
            if author_name is not None:
                opened_post_view.like()
                on_action(LikeAction(source_name=None, source_type=None, user=author_name))

        return True

    interact_with_feed(navigate_to_feed, should_continue, interact_with_feed_post)


def _warmup_explore(device, time_secs, on_action):
    print("Scrolling and liking Explore")
    start_time = datetime.now()

    def navigate_to_feed():
        navigate(device, TabBarTabs.SEARCH)
        sleeper.random_sleep()
        posts_grid_view = PostsGridView(device)
        posts_views_list = posts_grid_view.open_random_post()
        return posts_views_list

    def should_continue():
        diff_in_secs = int((datetime.now() - start_time).total_seconds())
        return diff_in_secs < time_secs

    def interact_with_feed_post(posts_views_list):
        if randint(1, LIKE_CHANCE) == LIKE_CHANCE:
            print_debug("Like post")
            opened_post_view = OpenedPostView(device)
            author_name = opened_post_view.get_author_name()
            if author_name is not None:
                opened_post_view.like()
                on_action(LikeAction(source_name=None, source_type=None, user=author_name))

        return True

    interact_with_feed(navigate_to_feed, should_continue, interact_with_feed_post)
