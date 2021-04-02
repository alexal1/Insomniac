from insomniac import db_models
from insomniac.actions_types import TargetType
from insomniac.database_engine import *
from insomniac.db_models import get_ig_profile_by_profile_name, ProfileStatus
from insomniac.utils import *

FILENAME_WHITELIST = "whitelist.txt"
FILENAME_BLACKLIST = "blacklist.txt"
FILENAME_TARGETS = "targets.txt"


STORAGE_ARGS = {
    "reinteract_after": {
        "help": "set a time (in hours) to wait before re-interact with an already interacted profile, "
                "disabled by default (won't interact again). "
                "It can be a number (e.g. 48) or a range (e.g. 50-80)",
        "metavar": "150"
    },
    "refilter_after": {
        "help": "set a time (in hours) to wait before re-filter an already filtered profile, "
                "disabled by default (will drop the profile and won't filter again). "
                "It can be a number (e.g. 48) or a range (e.g. 50-80)",
        "metavar": "150"
    },
    "recheck_follow_status_after": {
        "help": "set a time (in hours) to wait before re-check follow status of a profile, "
                "disabled by default (will check every time when needed)."
                "It can be a number (e.g. 48) or a range (e.g. 50-80)",
        "metavar": "150"
    }
}


IS_USING_DATABASE = False


def database_api(func):
    def wrap(*args, **kwargs):
        if IS_USING_DATABASE:
            return func(*args, **kwargs)

        return None
    return wrap


class Storage:
    profile = None
    scrape_for_account_list = []
    recheck_follow_status_after = None
    whitelist = []
    blacklist = []
    reinteract_after = None
    refilter_after = None
    profiles_targets_list_from_parameters = []
    url_targets_list_from_parameters = []

    def _reset_state(self):
        global IS_USING_DATABASE
        IS_USING_DATABASE = False
        self.profile = None
        self.scrape_for_account_list = []
        self.recheck_follow_status_after = None
        self.whitelist = []
        self.blacklist = []
        self.reinteract_after = None
        self.refilter_after = None
        self.profiles_targets_list_from_parameters = []
        self.url_targets_list_from_parameters = []

    def __init__(self, my_username, args):
        db_models.init()

        self._reset_state()

        if my_username is None:
            print(COLOR_FAIL + "No username, so the script won't read/write from the database" + COLOR_ENDC)
            return

        global IS_USING_DATABASE
        IS_USING_DATABASE = True

        self.profile = get_ig_profile_by_profile_name(my_username)
        scrape_for_account = args.__dict__.get('scrape_for_account', [])
        self.scrape_for_account_list = scrape_for_account if isinstance(scrape_for_account, list) else [scrape_for_account]
        if args.reinteract_after is not None:
            self.reinteract_after = get_value(args.reinteract_after, "Re-interact after {} hours", 168)
        if args.refilter_after is not None:
            self.refilter_after = get_value(args.refilter_after, "Re-filter after {} hours", 168)
        if args.recheck_follow_status_after is not None:
            self.recheck_follow_status_after = get_value(args.recheck_follow_status_after, "Re-check follow status after {} hours", 168)
        self.profiles_targets_list_from_parameters = args.__dict__.get('targets_list', [])
        self.url_targets_list_from_parameters = args.__dict__.get('posts_urls_list', [])
        whitelist_from_parameters = args.__dict__.get('whitelist_profiles', None)
        blacklist_from_parameters = args.__dict__.get('blacklist_profiles', None)

        # Whitelist and Blacklist
        try:
            with open(FILENAME_WHITELIST, encoding="utf-8") as file:
                self.whitelist = [line.rstrip() for line in file]
        except FileNotFoundError:
            print_debug("No whitelist provided")

        try:
            with open(FILENAME_BLACKLIST, encoding="utf-8") as file:
                self.blacklist = [line.rstrip() for line in file]
        except FileNotFoundError:
            print_debug("No blacklist provided")

        if whitelist_from_parameters is not None:
            if isinstance(whitelist_from_parameters, list) and len(whitelist_from_parameters) > 0:
                print("Loading whitelist from profiles_whitelist parameter...")
                self.whitelist.extend(whitelist_from_parameters)

        if blacklist_from_parameters is not None:
            if isinstance(blacklist_from_parameters, list) and len(blacklist_from_parameters) > 0:
                print("Loading blacklist from profiles_blacklist parameter...")
                self.blacklist.extend(blacklist_from_parameters)

        # Print meta data
        if len(self.profiles_targets_list_from_parameters) > 0 or len(self.url_targets_list_from_parameters) > 0:
            count = len(self.profiles_targets_list_from_parameters) + len(self.url_targets_list_from_parameters)
            print(f"Profiles and posts to interact from args: {count}")
        count_from_file = self._count_targets_from_file()
        if count_from_file > 0:
            print(f"Profiles and posts to interact from targets file: {count_from_file}")
        count_from_scrapping = self.profile.count_scrapped_profiles_for_interaction()
        if count_from_scrapping > 0:
            print(f"Profiles to interact from scrapping: {count_from_scrapping}")

    @database_api
    def start_session(self, app_id, app_version, args, followers_count, following_count):
        session_id = self.profile.start_session(app_id, app_version, args, ProfileStatus.VALID,
                                                followers_count, following_count)
        return session_id

    @database_api
    def end_session(self, session_id):
        self.profile.end_session(session_id)

    @database_api
    def check_user_was_interacted(self, username):
        return self.profile.is_interacted(username, hours=self.reinteract_after)

    @database_api
    def check_user_was_interacted(self, username):
        return self.profile.is_interacted(username, hours=72)

    @database_api
    def check_user_was_scrapped(self, username):
        return self.profile.is_scrapped(username, self.scrape_for_account_list)

    @database_api
    def check_user_was_filtered(self, username):
        return self.profile.is_filtered(username, hours=self.refilter_after)

    @database_api
    def get_following_status(self, username):
        if not self.profile.used_to_follow(username):
            return FollowingStatus.NONE
        return FollowingStatus.FOLLOWED if self.profile.do_i_follow(username) else FollowingStatus.UNFOLLOWED

    @database_api
    def is_profile_follows_me_by_cache(self, username):
        """
        Return True if and only if "username" follows me and the last check was within
        "recheck_follow_status_after" hours.
        """
        if self.recheck_follow_status_after is None:
            return False
        return self.profile.is_follow_me(username, hours=self.recheck_follow_status_after) is True

    @database_api
    def update_follow_status(self, username, is_follow_me, do_i_follow_him):
        self.profile.update_follow_status(username, is_follow_me, do_i_follow_him)

    @database_api
    def log_get_profile_action(self, session_id, username):
        self.profile.log_get_profile_action(session_id, username)

    @database_api
    def log_like_action(self, session_id, username, source_type, source_name):
        self.profile.log_like_action(session_id, username, source_type, source_name)

    @database_api
    def log_follow_action(self, session_id, username, source_type, source_name):
        self.profile.log_follow_action(session_id, username, source_type, source_name)

    @database_api
    def log_story_watch_action(self, session_id, username, source_type, source_name):
        self.profile.log_story_watch_action(session_id, username, source_type, source_name)

    @database_api
    def log_comment_action(self, session_id, username, comment, source_type, source_name):
        self.profile.log_comment_action(session_id, username, comment, source_type, source_name)

    @database_api
    def log_direct_message_action(self, session_id, username, message):
        self.profile.log_direct_message_action(session_id, username, message)

    @database_api
    def log_unfollow_action(self, session_id, username):
        self.profile.log_unfollow_action(session_id, username)

    @database_api
    def log_scrape_action(self, session_id, username, source_type, source_name):
        self.profile.log_scrape_action(session_id, username, source_type, source_name)

    @database_api
    def log_filter_action(self, session_id, username):
        self.profile.log_filter_action(session_id, username)

    @database_api
    def log_change_profile_info_action(self, session_id, profile_pic_url, name, description):
        self.profile.log_change_profile_info_action(session_id, profile_pic_url, name, description)

    @database_api
    def publish_scrapped_account(self, username):
        self.profile.publish_scrapped_account(username, self.scrape_for_account_list)

    def get_target(self):
        """
        Get a target from args (users/posts) -> OR from targets file (users/posts) -> OR from scrapping (only users).
        Picks only not yet interacted targets.

        :returns: target and type
        """
        # From args
        try:
            return self.profiles_targets_list_from_parameters.pop(0), TargetType.USERNAME
        except IndexError:
            pass

        try:
            return self.url_targets_list_from_parameters.pop(0), TargetType.URL
        except IndexError:
            pass

        # From file
        try:
            with open(FILENAME_TARGETS, "r+", encoding="utf-8") as file:
                lines = [line.rstrip() for line in file]

                for i, line in enumerate(lines):
                    # Skip comments
                    if line.startswith("#"):
                        continue

                    # Skip already interacted
                    if "DONE" in line:
                        continue

                    data = line.strip()
                    if data.startswith("https://"):
                        target_type = TargetType.URL
                    else:
                        target_type = TargetType.USERNAME
                    lines[i] += " - DONE"
                    file.truncate(0)
                    file.seek(0)
                    file.write("\n".join(lines))
                    return data, target_type
        except FileNotFoundError:
            pass

        # From scrapping
        scrapped_profile = self.profile.get_scrapped_profile_for_interaction()
        if scrapped_profile is not None:
            return scrapped_profile, TargetType.USERNAME
        return None, None

    def is_user_in_whitelist(self, username):
        return username in self.whitelist

    def is_user_in_blacklist(self, username):
        return username in self.blacklist

    def _count_targets_from_file(self):
        count = 0
        try:
            with open(FILENAME_TARGETS, encoding="utf-8") as file:
                lines = [line.rstrip() for line in file]

                for i, line in enumerate(lines):
                    # Skip comments
                    if line.startswith("#"):
                        continue

                    # Skip already interacted
                    if "DONE" in line:
                        continue

                    count += 1
        except FileNotFoundError:
            pass
        return count


@unique
class FollowingStatus(Enum):
    NONE = 0
    FOLLOWED = 1
    UNFOLLOWED = 2
