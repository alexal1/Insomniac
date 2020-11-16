from datetime import timedelta
from enum import Enum, unique

from insomniac.utils import *

FILENAME_INTERACTED_USERS = "interacted_users.json"
FILENAME_SCRAPPED_USERS = "scrapped_users.json"
USER_LAST_INTERACTION = "last_interaction"
USER_FOLLOWING_STATUS = "following_status"
USER_SCRAPPING_STATUS = "scrapping_status"

FILENAME_WHITELIST = "whitelist.txt"
FILENAME_BLACKLIST = "blacklist.txt"
FILENAME_TARGETS = "targets.txt"
FILENAME_FOLLOWERS = "followers.txt"


class Storage:
    interacted_users_path = None
    interacted_users = {}
    scrapped_users = {}
    whitelist = []
    blacklist = []
    targets = []
    account_followers = {}

    def __init__(self, my_username, args):
        scrape_for_account = args.__dict__.get('scrape_for_account', None)
        if my_username is None:
            print(COLOR_FAIL + "No username, thus the script won't get access to interacted users and sessions data" +
                  COLOR_ENDC)
            return

        if not os.path.exists(my_username):
            os.makedirs(my_username)
        self.interacted_users_path = my_username + "/" + FILENAME_INTERACTED_USERS
        if os.path.exists(self.interacted_users_path):
            with open(self.interacted_users_path, encoding="utf-8") as json_file:
                self.interacted_users = json.load(json_file)
        self.scrapped_users_path = my_username + "/" + FILENAME_SCRAPPED_USERS
        if os.path.exists(self.scrapped_users_path):
            with open(self.scrapped_users_path, encoding="utf-8") as json_file:
                self.scrapped_users = json.load(json_file)
        whitelist_path = my_username + "/" + FILENAME_WHITELIST
        if os.path.exists(whitelist_path):
            with open(whitelist_path, encoding="utf-8") as file:
                self.whitelist = [line.rstrip() for line in file]
        blacklist_path = my_username + "/" + FILENAME_BLACKLIST
        if os.path.exists(blacklist_path):
            with open(blacklist_path, encoding="utf-8") as file:
                self.blacklist = [line.rstrip() for line in file]
        targets_path = my_username + "/" + FILENAME_TARGETS
        if os.path.exists(targets_path):
            with open(targets_path, encoding="utf-8") as file:
                self.targets = [line.rstrip() for line in file]

        if scrape_for_account is not None:
            if not os.path.isdir(scrape_for_account):
                os.makedirs(scrape_for_account)
            self.targets_path = scrape_for_account + "/" + FILENAME_TARGETS
            if os.path.exists(self.targets_path):
                with open(self.targets_path, encoding="utf-8") as file:
                    self.targets = [line.rstrip() for line in file]

            self.followers_path = scrape_for_account + "/" + FILENAME_FOLLOWERS
            if os.path.exists(self.followers_path):
                with open(self.followers_path, encoding="utf-8") as json_file:
                    self.account_followers = json.load(json_file)

    def check_user_was_interacted(self, username):
        return not self.interacted_users.get(username) is None

    def check_user_was_interacted_recently(self, username):
        user = self.interacted_users.get(username)
        if user is None:
            return False

        last_interaction = datetime.strptime(user[USER_LAST_INTERACTION], '%Y-%m-%d %H:%M:%S.%f')
        return datetime.now() - last_interaction <= timedelta(days=3)

    def check_user_was_scrapped(self, username):
        return not self.scrapped_users.get(username) is None

    def get_following_status(self, username):
        user = self.interacted_users.get(username)
        return user is None and FollowingStatus.NONE or FollowingStatus[user[USER_FOLLOWING_STATUS].upper()]

    def add_interacted_user(self, username, followed=False, unfollowed=False):
        user = self.interacted_users.get(username, {})
        user[USER_LAST_INTERACTION] = str(datetime.now())

        if followed:
            user[USER_FOLLOWING_STATUS] = FollowingStatus.FOLLOWED.name.lower()
        elif unfollowed:
            user[USER_FOLLOWING_STATUS] = FollowingStatus.UNFOLLOWED.name.lower()
        else:
            user[USER_FOLLOWING_STATUS] = FollowingStatus.NONE.name.lower()

        self.interacted_users[username] = user
        self._update_file()

    def add_scrapped_user(self, username, success=False):
        user = self.scrapped_users.get(username, {})
        user[USER_LAST_INTERACTION] = str(datetime.now())

        if success:
            user[USER_SCRAPPING_STATUS] = ScrappingStatus.SCRAPED.name.lower()
        else:
            user[USER_FOLLOWING_STATUS] = ScrappingStatus.NOT_SCRAPED.name.lower()

        self.scrapped_users[username] = user
        self._update_scrapped_file()

    def add_target_user(self, username):
        if username in self.targets:
            return

        if self.targets_path is not None:
            with open(self.targets_path, 'a', encoding="utf-8") as outfile:
                outfile.write(username + '\n')

    def save_followers_for_today(self, followers_list, override=False):
        curr_day = str(datetime.date(datetime.now()))
        if curr_day in self.account_followers:
            if not override:
                return

        self.account_followers[curr_day] = followers_list

        if self.followers_path is not None:
            with open(self.followers_path, 'w', encoding="utf-8") as outfile:
                json.dump(self.account_followers, outfile, indent=4, sort_keys=False)

    def is_user_in_whitelist(self, username):
        return username in self.whitelist

    def is_user_in_blacklist(self, username):
        return username in self.blacklist

    def _get_last_day_interactions_count(self):
        count = 0
        users_list = list(self.interacted_users.values())
        for user in users_list:
            last_interaction = datetime.strptime(user[USER_LAST_INTERACTION], '%Y-%m-%d %H:%M:%S.%f')
            is_last_day = datetime.now() - last_interaction <= timedelta(days=1)
            if is_last_day:
                count += 1
        return count

    def _update_file(self):
        if self.interacted_users_path is not None:
            with open(self.interacted_users_path, 'w', encoding="utf-8") as outfile:
                json.dump(self.interacted_users, outfile, indent=4, sort_keys=False)

    def _update_scrapped_file(self):
        if self.scrapped_users_path is not None:
            with open(self.scrapped_users_path, 'w', encoding="utf-8") as outfile:
                json.dump(self.scrapped_users, outfile, indent=4, sort_keys=False)


@unique
class FollowingStatus(Enum):
    NONE = 0
    FOLLOWED = 1
    UNFOLLOWED = 2


@unique
class ScrappingStatus(Enum):
    SCRAPED = 0
    NOT_SCRAPED = 1
