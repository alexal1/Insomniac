from functools import partial

from insomniac.action_runners.actions_runners_manager import ActionState
from insomniac.actions_impl import interact_with_user, InteractionStrategy, is_private_account, open_user, do_have_story
from insomniac.actions_types import LikeAction, FollowAction, InteractAction, GetProfileAction, StoryWatchAction, \
    CommentAction, TargetType, FilterAction
from insomniac.limits import process_limits
from insomniac.report import print_short_report, print_interaction_types
from insomniac.sleeper import sleeper
from insomniac.storage import FollowingStatus
from insomniac.utils import *
from insomniac.views import OpenedPostView

is_all_filters_satisfied = False


def handle_target(device,
                  target,
                  target_type,
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
    source_type = None  # Must be None, so targeted-actions wont record any action-source on the database
    interaction = partial(interact_with_user,
                          device=device,
                          user_source=target,
                          source_type=source_type,
                          my_username=session_state.my_username,
                          on_action=on_action)

    def pre_conditions(target_name, target_name_view):
        if is_passed_filters is not None:
            global is_all_filters_satisfied
            should_continue, is_all_filters_satisfied = is_passed_filters(device, target_name, reset=True,
                                                                          filters_tags=['BEFORE_PROFILE_CLICK'])
            if not should_continue:
                on_action(FilterAction(user=target_name))
                return False

            if not is_all_filters_satisfied:
                print_debug("Not all filters are satisfied with filter-ahead, continue filtering inside the profile-page")

        return True

    def interact_with_username_target(target_name, target_name_view):
        is_interact_limit_reached, interact_reached_source_limit, interact_reached_session_limit = \
            is_limit_reached(InteractAction(source_name=target, source_type=source_type, user=target_name, succeed=True), session_state)

        if not process_limits(is_interact_limit_reached, interact_reached_session_limit,
                              interact_reached_source_limit, action_status, "Interaction"):
            return

        is_get_profile_limit_reached, get_profile_reached_source_limit, get_profile_reached_session_limit = \
            is_limit_reached(GetProfileAction(user=target_name), session_state)

        if not process_limits(is_get_profile_limit_reached, get_profile_reached_session_limit,
                              get_profile_reached_source_limit, action_status, "Get-Profile"):
            return

        print("@" + target_name + ": interact")

        if is_passed_filters is not None:
            if not is_all_filters_satisfied:
                should_continue, _ = is_passed_filters(device, target_name, reset=False)
                if not should_continue:
                    on_action(FilterAction(user=target_name))
                    print("Moving to next target")
                    return

        is_like_limit_reached, like_reached_source_limit, like_reached_session_limit = \
            is_limit_reached(LikeAction(source_name=target, source_type=source_type, user=target_name), session_state)

        is_follow_limit_reached, follow_reached_source_limit, follow_reached_session_limit = \
            is_limit_reached(FollowAction(source_name=target, source_type=source_type, user=target_name), session_state)

        is_watch_limit_reached, watch_reached_source_limit, watch_reached_session_limit = \
            is_limit_reached(StoryWatchAction(source_name=target, source_type=source_type, user=target_name), session_state)

        is_comment_limit_reached, comment_reached_source_limit, comment_reached_session_limit = \
            is_limit_reached(CommentAction(source_name=target, source_type=source_type, user=target_name, comment=""), session_state)

        is_private = is_private_account(device)
        if is_private:
            if is_passed_filters is None:
                print(COLOR_OKGREEN + "@" + target_name + " has private account, won't interact." + COLOR_ENDC)
                on_action(InteractAction(source_name=target, source_type=source_type, user=target_name, succeed=False))
                print("Moving to next target")
                return
            print("@" + target_name + ": Private account - images wont be liked.")

        do_have_stories = do_have_story(device)
        if not do_have_stories:
            print("@" + target_name + ": seems there are no stories to be watched.")

        is_likes_enabled = likes_count != '0'
        is_stories_enabled = stories_count != '0'
        is_follow_enabled = follow_percentage != 0
        is_comment_enabled = comment_percentage != 0

        likes_value = get_value(likes_count, "Likes count: {}", 2, max_count=12)
        stories_value = get_value(stories_count, "Stories to watch: {}", 1)

        can_like = not is_like_limit_reached and not is_private and likes_value > 0
        can_follow = (not is_follow_limit_reached) and storage.get_following_status(target_name) == FollowingStatus.NONE and follow_percentage > 0
        can_watch = (not is_watch_limit_reached) and do_have_stories and stories_value > 0
        can_comment = (not is_comment_limit_reached) and not is_private and comment_percentage > 0
        can_interact = can_like or can_follow or can_watch or can_comment

        if not can_interact:
            print("@" + target_name + ": Cant be interacted (due to limits / already followed). Skip.")
            on_action(InteractAction(source_name=target, source_type=source_type, user=target_name, succeed=False))
        else:
            print_interaction_types(target_name, can_like, can_follow, can_watch, can_comment)
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

            is_liked, is_followed, is_watch, is_commented = interaction(username=target_name, interaction_strategy=interaction_strategy)
            if is_liked or is_followed or is_watch or is_commented:
                on_action(InteractAction(source_name=target, source_type=source_type, user=target_name, succeed=True))
                print_short_report(target_name, session_state)
            else:
                on_action(InteractAction(source_name=target, source_type=source_type, user=target_name, succeed=False))

        if ((is_like_limit_reached and is_likes_enabled) or not is_likes_enabled) and \
           ((is_follow_limit_reached and is_follow_enabled) or not is_follow_enabled) and \
           ((is_comment_limit_reached and is_comment_enabled) or not is_comment_enabled) and \
           ((is_watch_limit_reached and is_stories_enabled) or not is_stories_enabled):
            # If one of the limits reached for source-limit, move to next source
            if (like_reached_source_limit is not None and like_reached_session_limit is None) or \
                    (follow_reached_source_limit is not None and follow_reached_session_limit is None):
                action_status.set_limit(ActionState.SOURCE_LIMIT_REACHED)

            # If all of the limits reached for session-limit, finish the session
            if ((like_reached_session_limit is not None and is_likes_enabled) or not is_likes_enabled) and \
                    ((follow_reached_session_limit is not None and is_follow_enabled) or not is_follow_enabled):
                action_status.set_limit(ActionState.SESSION_LIMIT_REACHED)

        print("Moving to next target")
        return

    def interact_with_post_id_target(target_post, target_username, target_name_view):
        is_interact_limit_reached, interact_reached_source_limit, interact_reached_session_limit = \
            is_limit_reached(InteractAction(source_name=target_username, source_type=source_type, user=target_username, succeed=True), session_state)

        if not process_limits(is_interact_limit_reached, interact_reached_session_limit,
                              interact_reached_source_limit, action_status, "Interaction"):
            return

        print(f"@{target_username} - {target_post}: interact")

        is_like_limit_reached, like_reached_source_limit, like_reached_session_limit = \
            is_limit_reached(LikeAction(source_name=target_username, source_type=source_type, user=target_username), session_state)

        can_like = not is_like_limit_reached
        can_interact = can_like

        if not can_interact:
            print(f"@{target_username} - {target_post}: Cant be interacted (due to limits / already interacted). Skip.")
            on_action(InteractAction(source_name=target_username, source_type=source_type, user=target_username, succeed=False))
        else:
            print_interaction_types(f"{target_username} - {target_post}", can_like, False, False, False)

            is_liked = opened_post_view.like_post()

            if is_liked:
                print(COLOR_OKGREEN + f"@{target_username} - {target_post} - photo been liked." + COLOR_ENDC)
                on_action(LikeAction(source_name=target_username, source_type=source_type, user=target_username))
                on_action(InteractAction(source_name=target_username, source_type=source_type, user=target_username, succeed=True))
                print_short_report(f"@{target_username} - {target_post}", session_state)
            else:
                on_action(InteractAction(source_name=target_username, source_type=source_type, user=target_username, succeed=False))

        if is_like_limit_reached:
            # If one of the limits reached for source-limit, move to next source
            if like_reached_source_limit is not None and like_reached_session_limit is None:
                action_status.set_limit(ActionState.SOURCE_LIMIT_REACHED)

            # If all of the limits reached for session-limit, finish the session
            if like_reached_session_limit is not None:
                action_status.set_limit(ActionState.SESSION_LIMIT_REACHED)

        print("Moving to next target")
        return

    if target_type == TargetType.USERNAME:
        is_myself = target == session_state.my_username

        if is_myself:
            print(COLOR_FAIL + "Target handling was started for yourself. Abort." + COLOR_ENDC)
            return

        if pre_conditions(target, None):
            if open_user(device=device, username=target, refresh=False, on_action=on_action):
                interact_with_username_target(target, None)
            else:
                print("@" + target + " profile couldn't be opened. Skip.")
                on_action(InteractAction(source_name=target, source_type=source_type, user=target, succeed=False))
    else:
        url = target.strip()
        if validate_url(url) and "instagram.com/p/" in url:
            if open_instagram_with_url(device_id=device.device_id, url=url) is True:
                sleeper.random_sleep()
                opened_post_view = OpenedPostView(device)
                username = opened_post_view.get_user_name()
                if username is None:
                    print(url + " target user-name couldn't be processed. Skip.")
                    return

                interact_with_post_id_target(url, username, None)
        else:
            print(url + " target couldn't be opened. Skip.")
