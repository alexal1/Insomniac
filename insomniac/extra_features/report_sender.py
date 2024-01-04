import json
import pathlib
import uuid
from datetime import timezone

from insomniac import activation_controller, network
from insomniac.db_models import get_actions_count_for_profiles, get_actions_count_within_hours_for_profiles, db, \
    LikeAction, CommentAction, FollowAction, DirectMessageAction
from insomniac.utils import *


def send_report(is_bot_enabled: bool):
    print_debug(f"Sending report (is_bot_enabled={is_bot_enabled}")
    activation_code = activation_controller.activation_code
    mac = uuid.getnode()
    timestamp = datetime.now(timezone.utc)

    with db.connection_context():
        stats = get_actions_count_for_profiles()
        stats_1_hour = get_actions_count_within_hours_for_profiles(hours=1)
        stats_24_hours = get_actions_count_within_hours_for_profiles(hours=24)

    likes_count_1h = 0
    likes_count_24h = 0
    likes_count_all = 0
    for acc_stats in stats_1_hour.values():
        likes_count_1h += acc_stats.get(LikeAction.__name__) or 0
    for acc_stats in stats_24_hours.values():
        likes_count_24h += acc_stats.get(LikeAction.__name__) or 0
    for acc_stats in stats.values():
        likes_count_all += acc_stats.get(LikeAction.__name__) or 0

    comments_count_1h = 0
    comments_count_24h = 0
    comments_count_all = 0
    for acc_stats in stats_1_hour.values():
        comments_count_1h += acc_stats.get(CommentAction.__name__) or 0
    for acc_stats in stats_24_hours.values():
        comments_count_24h += acc_stats.get(CommentAction.__name__) or 0
    for acc_stats in stats.values():
        comments_count_all += acc_stats.get(CommentAction.__name__) or 0

    follows_count_1h = 0
    follows_count_24h = 0
    follows_count_all = 0
    for acc_stats in stats_1_hour.values():
        follows_count_1h += acc_stats.get(FollowAction.__name__) or 0
    for acc_stats in stats_24_hours.values():
        follows_count_24h += acc_stats.get(FollowAction.__name__) or 0
    for acc_stats in stats.values():
        follows_count_all += acc_stats.get(FollowAction.__name__) or 0

    dms_count_1h = 0
    dms_count_24h = 0
    dms_count_all = 0
    for acc_stats in stats_1_hour.values():
        dms_count_1h += acc_stats.get(DirectMessageAction.__name__) or 0
    for acc_stats in stats_24_hours.values():
        dms_count_24h += acc_stats.get(DirectMessageAction.__name__) or 0
    for acc_stats in stats.values():
        dms_count_all += acc_stats.get(DirectMessageAction.__name__) or 0

    data_set = {
        "activation_code": activation_code,
        "mac": str(mac),
        "is_bot_enabled": is_bot_enabled,
        "timestamp": str(timestamp),
        
        "likes_count_1h": likes_count_1h,
        "comments_count_1h": comments_count_1h,
        "follows_count_1h": follows_count_1h,
        "dms_count_1h": dms_count_1h,

        "likes_count_24h": likes_count_24h,
        "comments_count_24h": comments_count_24h,
        "follows_count_24h": follows_count_24h,
        "dms_count_24h": dms_count_24h,

        "likes_count_all": likes_count_all,
        "comments_count_all": comments_count_all,
        "follows_count_all": follows_count_all,
        "dms_count_all": dms_count_all,
    }

    network.post("https://insomniac-bot.com/report/", data_set)


def notify_interaction_targets_finished(username):
    if not notification_chat_bot.init():
        return

    folder_name = pathlib.Path(__file__).parts[-4]
    notification_chat_bot.send_message(f"Interaction targets for `{username}` are finished! `{folder_name}`.")


def notify_unfollow_targets_finished(username):
    if not notification_chat_bot.init():
        return

    folder_name = pathlib.Path(__file__).parts[-4]
    notification_chat_bot.send_message(f"Unfollow targets for `{username}` are finished! `{folder_name}`.")


class NotificationChatBot:
    CONFIG_FILENAME = "telegram_notification_chat_bot_config.json"
    CONFIG_KEY_TOKEN = "token"
    CONFIG_KEY_CHAT_ID = "chat_id"

    is_initialized = False
    is_initialization_failed = False
    token = ""
    chat_id = ""
    bot = None

    def init(self) -> bool:
        if self.is_initialized:
            return True

        if self.is_initialization_failed:
            return False

        try:
            from telegram import Bot

            with open(self.CONFIG_FILENAME, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                self.token = data[self.CONFIG_KEY_TOKEN]
                self.chat_id = data[self.CONFIG_KEY_CHAT_ID]

            self.bot = Bot(self.token)
        except Exception as e:
            print_debug(COLOR_FAIL + f"Failed initialization of NotificationChatBot: {e}" + COLOR_ENDC)
            self.is_initialization_failed = True
            return False

        self.is_initialized = True
        return True

    def send_message(self, text):
        print_debug(f"Sending message in NotificationChatBot: \"{text}\"")
        from telegram import ParseMode
        self.bot.send_message(chat_id=self.chat_id, text=text, timeout=10, parse_mode=ParseMode.MARKDOWN)


notification_chat_bot = NotificationChatBot()
