from functools import partial

from insomniac.action_runners.actions_runners_manager import ActionState
from insomniac.actions_impl import interact_with_user, InteractionStrategy
from insomniac.actions_types import LikeAction, FollowAction, InteractAction, GetProfileAction, StoryWatchAction, \
    BloggerInteractionType, CommentAction, FilterAction, SourceType
from insomniac.limits import process_limits
from insomniac.report import print_short_report, print_interaction_types
from insomniac.sleeper import sleeper
from insomniac.softban_indicator import softban_indicator
from insomniac.storage import FollowingStatus
from insomniac.utils import *
from insomniac.views import TabBarView, ProfileView


def extract_blogger_instructions(source):
    split_idx = source.find('-')
    if split_idx == -1:
        print("There is no special interaction-instructions for " + source + ". Working with " + source + " followers.")
        return source, BloggerInteractionType.FOLLOWERS

    selected_instruction = None
    source_profile_name = source[:split_idx]
    interaction_instructions_str = source[split_idx+1:]

    for blogger_instruction in BloggerInteractionType:
        if blogger_instruction.value == interaction_instructions_str:
            selected_instruction = blogger_instruction
            break

    if selected_instruction is None:
        print("Couldn't use interaction-instructions " + interaction_instructions_str +
              ". Working with " + source + " followers.")
        selected_instruction = BloggerInteractionType.FOLLOWERS

    return source_profile_name, selected_instruction


def handle_blogger(device,
                   username,
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
    is_myself = username == session_state.my_username
    source_type = f'{SourceType.BLOGGER.value}-{instructions.value}'
    interaction = partial(interact_with_user,
                          device=device,
                          user_source=username,
                          source_type=source_type,
                          my_username=session_state.my_username,
                          on_action=on_action)

    search_view = TabBarView(device).navigate_to_search()
    blogger_profile_view = search_view.navigate_to_username(username, on_action)

    if blogger_profile_view is None:
        return

    sleeper.random_sleep()
    is_profile_empty = softban_indicator.detect_empty_profile(device)

    if is_profile_empty:
        return

    followers_following_list_view = None
    if instructions == BloggerInteractionType.FOLLOWERS:
        followers_following_list_view = blogger_profile_view.navigate_to_followers()
    elif instructions == BloggerInteractionType.FOLLOWING:
        followers_following_list_view = blogger_profile_view.navigate_to_following()

    if is_myself:
        followers_following_list_view.scroll_to_bottom()
        followers_following_list_view.scroll_to_top()

    def pre_conditions(follower_name, follower_name_view):
        if storage.is_user_in_blacklist(follower_name):
            print("@" + follower_name + " is in blacklist. Skip.")
            return False
        elif storage.check_user_was_filtered(follower_name):
            print("@" + follower_name + ": already filtered in past. Skip.")
            return False
        elif not is_myself and storage.check_user_was_interacted(follower_name):
            print("@" + follower_name + ": already interacted. Skip.")
            return False
        elif is_myself and storage.check_user_was_interacted_recently(follower_name):
            print("@" + follower_name + ": already interacted in the last week. Skip.")
            return False

        return True

    def interact_with_follower(follower_name, follower_name_view):
        """
        :return: whether we should continue interaction with other users after this one
        """
        is_interact_limit_reached, interact_reached_source_limit, interact_reached_session_limit = \
            is_limit_reached(InteractAction(source_name=username, source_type=source_type, user=follower_name, succeed=True), session_state)

        if not process_limits(is_interact_limit_reached, interact_reached_session_limit,
                              interact_reached_source_limit, action_status, "Interaction"):
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
                on_action(FilterAction(user=follower_name))
                return True

            if not is_all_filters_satisfied:
                print_debug("Not all filters are satisfied with filter-ahead, continue filtering inside the profile-page")

        print("@" + follower_name + ": interact")
        follower_name_view.click()
        on_action(GetProfileAction(user=follower_name))

        sleeper.random_sleep()
        is_profile_empty = softban_indicator.detect_empty_profile(device)

        if is_profile_empty:
            print("Back to followers list")
            device.back()
            return True

        follower_profile_view = ProfileView(device, follower_name == session_state.my_username)

        if is_passed_filters is not None:
            if not is_all_filters_satisfied:
                should_continue, _ = is_passed_filters(device, follower_name, reset=False)
                if not should_continue:
                    on_action(FilterAction(user=follower_name))
                    # Continue to next follower
                    print("Back to profiles list")
                    device.back()
                    return True

        is_like_limit_reached, like_reached_source_limit, like_reached_session_limit = \
            is_limit_reached(LikeAction(source_name=username, source_type=source_type, user=follower_name), session_state)

        is_follow_limit_reached, follow_reached_source_limit, follow_reached_session_limit = \
            is_limit_reached(FollowAction(source_name=username, source_type=source_type, user=follower_name), session_state)

        is_watch_limit_reached, watch_reached_source_limit, watch_reached_session_limit = \
            is_limit_reached(StoryWatchAction(source_name=username, source_type=source_type,user=follower_name), session_state)

        is_comment_limit_reached, comment_reached_source_limit, comment_reached_session_limit = \
            is_limit_reached(CommentAction(source_name=username, source_type=source_type, user=follower_name, comment=""), session_state)

        is_private = follower_profile_view.is_private_account()
        if is_private:
            if is_passed_filters is None:
                print(COLOR_OKGREEN + "@" + follower_name + " has private account, won't interact." + COLOR_ENDC)
                on_action(FilterAction(user=follower_name))
                on_action(InteractAction(source_name=username, source_type=source_type, user=follower_name, succeed=False))
                print("Back to profiles list")
                device.back()
                return True
            print("@" + follower_name + ": Private account - images wont be liked.")

        do_have_stories = follower_profile_view.is_story_available()
        if not do_have_stories:
            print("@" + follower_name + ": seems there are no stories to be watched.")

        is_likes_enabled = likes_count != '0'
        is_stories_enabled = stories_count != '0'
        is_follow_enabled = follow_percentage != 0
        is_comment_enabled = comment_percentage != 0

        likes_value = get_value(likes_count, "Likes count: {}", 2, max_count=12)
        stories_value = get_value(stories_count, "Stories to watch: {}", 1)

        can_like = not is_like_limit_reached and not is_private and likes_value > 0
        can_follow = (not is_follow_limit_reached) and storage.get_following_status(follower_name) == FollowingStatus.NONE and follow_percentage > 0
        can_watch = (not is_watch_limit_reached) and do_have_stories and stories_value > 0
        can_comment = (not is_comment_limit_reached) and not is_private and comment_percentage > 0
        can_interact = can_like or can_follow or can_watch or can_comment

        if not can_interact:
            print("@" + follower_name + ": Cant be interacted (due to limits / already followed). Skip.")
            on_action(InteractAction(source_name=username, source_type=source_type, user=follower_name, succeed=False))
        else:
            print_interaction_types(follower_name, can_like, can_follow, can_watch, can_comment)
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

            is_liked, is_followed, is_watch, is_commented = interaction(username=follower_name, interaction_strategy=interaction_strategy)
            if is_liked or is_followed or is_watch or is_commented:
                on_action(InteractAction(source_name=username, source_type=source_type, user=follower_name, succeed=True))
                print_short_report(f"@{username}", session_state)
            else:
                on_action(InteractAction(source_name=username, source_type=source_type, user=follower_name, succeed=False))

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

        print("Back to profiles list")
        device.back()

        return can_continue

    followers_following_list_view.iterate_over_followers(is_myself, interact_with_follower, pre_conditions)
