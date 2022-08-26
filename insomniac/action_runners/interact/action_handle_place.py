from functools import partial

from insomniac.action_runners.actions_runners_manager import ActionState
from insomniac.actions_impl import interact_with_user, ScrollEndDetector, open_likers, iterate_over_likers, \
    is_private_account, InteractionStrategy, do_have_story, interact_with_feed
from insomniac.actions_types import InteractAction, LikeAction, FollowAction, GetProfileAction, StoryWatchAction, \
    PlaceInteractionType, CommentAction, FilterAction, SourceType
from insomniac.limits import process_limits
from insomniac.navigation import search_for
from insomniac.report import print_short_report, print_interaction_types
from insomniac.safely_runner import RestartJobRequiredException
from insomniac.sleeper import sleeper
from insomniac.softban_indicator import softban_indicator
from insomniac.storage import FollowingStatus
from insomniac.utils import *
from insomniac.views import PostsGridView


def extract_place_instructions(source):
    source = source.replace('_', ' ')
    selected_instruction = None
    source_place_name = None
    for place_instruction in PlaceInteractionType:
        if source.endswith(f'-{place_instruction.value}'):
            selected_instruction = place_instruction
            source_place_name = source[:len(source) - len(place_instruction.value) - 1]
            break

    if selected_instruction is None:
        print("There is no special interaction-instructions for " + source + ". Working with " + source + " recent-likers.")
        return source, PlaceInteractionType.RECENT_LIKERS

    return source_place_name, selected_instruction


def handle_place(device,
                 place,
                 instructions,
                 session_state,
                 likes_count,
                 stories_count,
                 follow_percentage,
                 like_percentage,
                 comment_percentage,
                 comments_list,
                 storage,
                 on_action,
                 is_limit_reached,
                 is_passed_filters,
                 action_status):
    if not search_for(device, place=place, on_action=on_action):
        return None

    # Switch to Recent tab if needed
    if instructions == PlaceInteractionType.RECENT_LIKERS or instructions == PlaceInteractionType.RECENT_POSTS:
        sleeper.random_sleep()
        print("Switching to Recent tab")
        tab_layout = device.find(resourceId=f'{device.app_id}:id/tab_layout',
                                 className='android.widget.LinearLayout')
        if tab_layout.exists():
            tab_layout.child(index=1).click()
        else:
            print("Can't Find recent tab. Interacting with Popular.")

    # Sleep longer because posts loading takes time
    sleeper.random_sleep(multiplier=2.0)

    source_type = f'{SourceType.PLACE.value}-{instructions.value}'
    interaction = partial(interact_with_user,
                          device=device,
                          user_source=place,
                          source_type=source_type,
                          my_username=session_state.my_username,
                          on_action=on_action)

    def pre_conditions(liker_username, liker_username_view):
        if storage.is_user_in_blacklist(liker_username):
            print("@" + liker_username + " is in blacklist. Skip.")
            return False
        elif storage.check_user_was_filtered(liker_username):
            print("@" + liker_username + ": already filtered in past. Skip.")
            return False
        elif storage.check_user_was_interacted(liker_username):
            print("@" + liker_username + ": already interacted. Skip.")
            return False

        return True

    def interact_with_profile(liker_username, liker_username_view):
        """
        :return: whether we should continue interaction with other users after this one
        """
        is_interact_limit_reached, interact_reached_source_limit, interact_reached_session_limit = \
            is_limit_reached(InteractAction(source_name=place, source_type=source_type, user=liker_username, succeed=True), session_state)

        if not process_limits(is_interact_limit_reached, interact_reached_session_limit,
                              interact_reached_source_limit, action_status, "Interaction"):
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

        print("@" + liker_username + ": interact")
        liker_username_view.click()
        on_action(GetProfileAction(user=liker_username))

        if softban_indicator.detect_empty_profile(device):
            print("Back to likers list")
            device.back()
            return True

        if is_passed_filters is not None:
            if not is_all_filters_satisfied:
                should_continue, _ = is_passed_filters(device, liker_username, reset=False)
                if not should_continue:
                    # Continue to next follower
                    print("Back to likers list")
                    device.back()
                    return True

        is_like_limit_reached, like_reached_source_limit, like_reached_session_limit = \
            is_limit_reached(LikeAction(source_name=place, source_type=source_type, user=liker_username), session_state)

        is_follow_limit_reached, follow_reached_source_limit, follow_reached_session_limit = \
            is_limit_reached(FollowAction(source_name=place, source_type=source_type, user=liker_username), session_state)

        is_watch_limit_reached, watch_reached_source_limit, watch_reached_session_limit = \
            is_limit_reached(StoryWatchAction(source_name=place, source_type=source_type, user=liker_username), session_state)

        is_comment_limit_reached, comment_reached_source_limit, comment_reached_session_limit = \
            is_limit_reached(CommentAction(source_name=place, source_type=source_type, user=liker_username, comment=""), session_state)

        is_private = is_private_account(device)
        if is_private:
            if is_passed_filters is None:
                print(COLOR_OKGREEN + "@" + liker_username + " has private account, won't interact." + COLOR_ENDC)
                on_action(FilterAction(liker_username))
                on_action(InteractAction(source_name=place, source_type=source_type, user=liker_username, succeed=False))
                print("Back to likers list")
                device.back()
                return True
            print("@" + liker_username + ": Private account - images wont be liked.")

        do_have_stories = do_have_story(device)
        if not do_have_stories:
            print("@" + liker_username + ": seems there are no stories to be watched.")

        is_likes_enabled = likes_count != '0'
        is_stories_enabled = stories_count != '0'
        is_follow_enabled = follow_percentage != 0
        is_comment_enabled = comment_percentage != 0

        likes_value = get_value(likes_count, "Likes count: {}", 2, max_count=12)
        stories_value = get_value(stories_count, "Stories to watch: {}", 1)

        can_like = not is_like_limit_reached and not is_private and likes_value > 0
        can_follow = (not is_follow_limit_reached) and storage.get_following_status(liker_username) == FollowingStatus.NONE and follow_percentage > 0
        can_watch = (not is_watch_limit_reached) and do_have_stories and stories_value > 0
        can_comment = (not is_comment_limit_reached) and not is_private and comment_percentage > 0
        can_interact = can_like or can_follow or can_watch or can_comment

        if not can_interact:
            print("@" + liker_username + ": Cant be interacted (due to limits / already followed). Skip.")
            on_action(InteractAction(source_name=place, source_type=source_type, user=liker_username, succeed=False))
        else:
            print_interaction_types(liker_username, can_like, can_follow, can_watch, can_comment)
            interaction_strategy = InteractionStrategy(do_like=can_like,
                                                       do_follow=can_follow,
                                                       do_story_watch=can_watch,
                                                       do_comment=can_comment,
                                                       likes_count=likes_value,
                                                       follow_percentage=follow_percentage,
                                                       like_percentage=like_percentage,
                                                       stories_count=stories_value,
                                                       comment_percentage=comment_percentage,
                                                       comments_list=comments_list)

            is_liked, is_followed, is_watch, is_commented = interaction(username=liker_username, interaction_strategy=interaction_strategy)
            if is_liked or is_followed or is_watch or is_commented:
                on_action(InteractAction(source_name=place, source_type=source_type, user=liker_username, succeed=True))
                print_short_report(f"P-{place}", session_state)
            else:
                on_action(InteractAction(source_name=place, source_type=source_type, user=liker_username, succeed=False))

        can_continue = True

        if ((is_like_limit_reached and is_likes_enabled) or not is_likes_enabled) and \
           ((is_follow_limit_reached and is_follow_enabled) or not is_follow_enabled) and \
           ((is_comment_limit_reached and is_comment_enabled) or not is_comment_enabled) and \
           ((is_watch_limit_reached and is_stories_enabled) or not is_stories_enabled):
            # If one of the limits reached for source-limit, move to next source
            if (like_reached_source_limit is not None and like_reached_session_limit is None) or \
                    (follow_reached_source_limit is not None and follow_reached_session_limit is None):
                can_continue = False
                action_status.set_limit(ActionState.SOURCE_LIMIT_REACHED)

            # If all of the limits reached for session-limit, finish the session
            if ((like_reached_session_limit is not None and is_likes_enabled) or not is_likes_enabled) and \
                    ((follow_reached_session_limit is not None and is_follow_enabled) or not is_follow_enabled):
                can_continue = False
                action_status.set_limit(ActionState.SESSION_LIMIT_REACHED)

        print("Back to followers list")
        device.back()

        return can_continue

    def navigate_to_feed():
        # Open post
        posts_view_list = PostsGridView(device).open_random_post()
        if posts_view_list is None:
            return None

        return posts_view_list

    def should_continue_interact_with_feed():
        return True

    def interact_with_feed_post(posts_views_list):
        is_interact_limit_reached, interact_reached_source_limit, interact_reached_session_limit = \
            is_limit_reached(
                InteractAction(source_name=place, source_type=source_type, user=None, succeed=True),
                session_state)

        if not process_limits(is_interact_limit_reached, interact_reached_session_limit,
                              interact_reached_source_limit, action_status, "Interaction"):
            return False

        is_like_limit_reached, like_reached_source_limit, like_reached_session_limit = \
            is_limit_reached(LikeAction(source_name=place, source_type=source_type, user=None),
                             session_state)

        if not process_limits(is_like_limit_reached, like_reached_session_limit,
                              like_reached_source_limit, action_status, "Likes"):
            return False

        opened_post_view = posts_views_list.get_current_post()
        author_name = opened_post_view.get_author_name()

        like_chance = randint(1, 100)
        if like_chance > like_percentage:
            print("Not going to like image due to like-percentage hit")
            on_action(InteractAction(source_name=place, source_type=source_type, user=author_name, succeed=False))
        else:
            print("Like post")
            opened_post_view.like()
            if author_name is not None:
                on_action(LikeAction(source_name=place, source_type=source_type, user=author_name))
                on_action(InteractAction(source_name=place, source_type=source_type, user=author_name, succeed=True))

        return True

    if instructions == PlaceInteractionType.RECENT_LIKERS or instructions == PlaceInteractionType.TOP_LIKERS:
        extract_place_likers_and_interact(device,
                                          place,
                                          instructions,
                                          navigate_to_feed,
                                          interact_with_profile,
                                          pre_conditions,
                                          on_action)
    elif instructions == PlaceInteractionType.RECENT_POSTS or instructions == PlaceInteractionType.TOP_POSTS:
        interact_with_feed(navigate_to_feed, should_continue_interact_with_feed, interact_with_feed_post)


def extract_place_likers_and_interact(device,
                                      place,
                                      instructions,
                                      navigate_to_feed,
                                      iteration_callback,
                                      iteration_callback_pre_conditions,
                                      on_action):
    print("Interacting with place-{0}-{1}".format(place, instructions.value))

    # Open post
    posts_view_list = navigate_to_feed()
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
