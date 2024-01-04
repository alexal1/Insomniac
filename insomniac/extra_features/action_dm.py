from random import choice

from insomniac.actions_impl import open_user_followers, iterate_over_my_followers_no_swipes
from insomniac.actions_types import DirectMessageAction, GetProfileAction, DirectMessageBackdateAction
from insomniac.extra_features.views import ChatView
from insomniac.limits import process_limits
from insomniac.navigation import switch_to_english, LanguageChangedException
from insomniac.sleeper import sleeper
from insomniac.storage import FollowingStatus
from insomniac.tools.spintax import spin
from insomniac.utils import *
from insomniac.views import ProfileView


def send_dms_to_new_followers(device,
                              on_action,
                              storage,
                              is_limit_reached,
                              session_state,
                              action_status,
                              dm_list,
                              is_dm_to_followed_by_bot_only,
                              max_old_followers_in_a_row):
    if not open_user_followers(device=device, username=None, on_action=on_action):
        return
    sleeper.random_sleep()

    stop_detector = StopDetector(max_old_followers_in_a_row)

    def iteration_callback_pre_conditions(follower_name, follower_name_view, remove_button_view):
        """
        :return: True to send DM to this user, False to skip
        """
        is_myself = follower_name == session_state.my_username
        if is_myself:
            print(f"@{follower_name} is you, skip.")
            return False

        is_dm_already_sent = storage.is_dm_sent_to(follower_name)
        if is_dm_already_sent:
            print(f"Already sent a DM to @{follower_name}, skip.")
            stop_detector.notify_old_follower()
            return False

        if is_dm_to_followed_by_bot_only:
            was_followed_by_bot = storage.get_following_status(follower_name) is not FollowingStatus.NONE
            if not was_followed_by_bot:
                print(f"@{follower_name} was not followed by bot, skip.")
                stop_detector.notify_old_follower()
                return False

        print(f"@{follower_name} is a new follower, open profile.")
        stop_detector.notify_new_follower()
        return True

    def iteration_callback(follower_name, follower_name_view, remove_button_view):
        """
        :return: True to continue sending DMs after given user, False to stop
        """
        message = spin(choice(dm_list))

        is_dm_limit_reached, dm_reached_source_limit, dm_reached_session_limit = \
            is_limit_reached(DirectMessageAction(user=follower_name, message=message), session_state)

        if not process_limits(is_dm_limit_reached, dm_reached_session_limit,
                              dm_reached_source_limit, action_status, "Sending direct message"):
            return False

        is_get_profile_limit_reached, get_profile_reached_source_limit, get_profile_reached_session_limit = \
            is_limit_reached(GetProfileAction(user=follower_name), session_state)

        if not process_limits(is_get_profile_limit_reached, get_profile_reached_session_limit,
                              get_profile_reached_source_limit, action_status, "Get-Profile"):
            return False

        follower_name_view.click()
        sleeper.random_sleep()
        profile_view = ProfileView(device)
        if profile_view.is_visible():
            on_action(GetProfileAction(user=follower_name))
            storage.update_follow_status(follower_name, is_follow_me=True)
        else:
            print(COLOR_FAIL + "Cannot open profile!" + COLOR_ENDC)
            return True

        print("Go to the chat.")
        chat_view = _open_chat(device, profile_view)
        # Retry because sometimes it doesn't open chat
        retry_count = 3
        while not chat_view.is_visible():
            print(COLOR_OKGREEN + "Couldn't open the chat, trying again...")
            sleeper.random_sleep()
            chat_view = _open_chat(device, profile_view)
            retry_count -= 1
            if retry_count == 1:
                break
        if not chat_view.is_visible():
            print(COLOR_FAIL + "Cannot open chat!" + COLOR_ENDC)
            device.back()
            return True

        sleeper.random_sleep()
        chat_view = ChatView(device)
        if not chat_view.is_message_exists():
            print(f"Send a message: \"{message}\"")
            if ChatView(device).send_message(message):
                print("Successfully sent!")
                on_action(DirectMessageAction(user=follower_name, message=message))
            else:
                print("Error while sending, skip this follower.")
        else:
            print("There already are 1 or more messages in this chat, skip this follower.")
            # Mark that DM was sent, but not now, long time ago instead.
            # This is a hack to not open this user again and also to not break stats.
            on_action(DirectMessageBackdateAction(user=follower_name, message=''))

        device.back()
        device.back()
        return True

    try:
        iterate_over_my_followers_no_swipes(device, iteration_callback, iteration_callback_pre_conditions)
    except StopDetector.ReachedMaxOldFollowersException:
        print(COLOR_OKGREEN + f"{stop_detector.max_old_followers_in_a_row} old followers in a row, "
                              f"seems that new followers are over. Finishing." + COLOR_ENDC)


def _open_chat(device, profile_view: 'ProfileView') -> 'ChatView':
    if not profile_view.open_messages():
        if profile_view.is_private_account():
            opened_messages = profile_view.navigate_to_actions().open_messages()
        else:
            opened_messages = False

        if not opened_messages:
            print(COLOR_FAIL + 'Cannot find "Message" button. Maybe not English language is set?' + COLOR_ENDC)
            save_crash(device)
            switch_to_english(device)
            raise LanguageChangedException()
    return ChatView(device)


class StopDetector:
    # We use the number of old followers in a row as a stop criteria for iterating over followers:
    # if it reaches MAX_OLD_FOLLOWERS_IN_A_ROW, we stop.
    max_old_followers_in_a_row = 0
    old_followers_in_a_row = 0

    def __init__(self, max_old_followers_in_a_row):
        self.max_old_followers_in_a_row = max_old_followers_in_a_row
        self.old_followers_in_a_row = 0

    def notify_new_follower(self):
        self.old_followers_in_a_row = 0

    def notify_old_follower(self):
        self.old_followers_in_a_row += 1
        if self.old_followers_in_a_row > self.max_old_followers_in_a_row:
            raise StopDetector.ReachedMaxOldFollowersException()

    class ReachedMaxOldFollowersException(Exception):
        pass
