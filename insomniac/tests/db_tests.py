import unittest
from datetime import timedelta

from peewee import SqliteDatabase

from insomniac import db_models
from insomniac.actions_types import SourceType
from insomniac.db_models import get_ig_profile_by_profile_name, ProfileStatus, MODELS
from insomniac.utils import *

TEST_DATABASE_FILE = 'test.db'
test_db = SqliteDatabase(TEST_DATABASE_FILE, autoconnect=False)


class DatabaseTests(unittest.TestCase):

    def setUp(self):
        print("Creating test database with tables")
        db_models.db = test_db
        test_db.bind(MODELS)
        test_db.connect()
        test_db.create_tables(MODELS)
        test_db.close()

    def test_is_interacted(self):
        my_account1 = "my_account1"
        my_account2 = "my_account2"
        username1 = "username1"
        username2 = "username2"
        username3 = "username3"
        username4 = "username4"
        username5 = "username5"

        def job_interact(profile, session_id):
            print(COLOR_BOLD + f"Check users are not interacted by default" + COLOR_ENDC)
            assert profile.is_interacted(username1) is False

            print(COLOR_BOLD + f"Check users are not \"used to follow\" by default" + COLOR_ENDC)
            assert profile.used_to_follow(username1) is False

            print(COLOR_BOLD + f"Check interaction counted for {username1} after a \"get profile\"" + COLOR_ENDC)
            profile.log_get_profile_action(session_id, username1)
            assert profile.is_interacted(username1) is True

            print(COLOR_BOLD + f"Check interaction counted for {username2} after a like" + COLOR_ENDC)
            profile.log_like_action(session_id, username2, SourceType.BLOGGER.name, "some_blogger")
            assert profile.is_interacted(username2) is True

            print(COLOR_BOLD + f"Check interaction counted for {username3} after a comment" + COLOR_ENDC)
            profile.log_comment_action(session_id, username3, "Wow!", SourceType.BLOGGER.name, "some_blogger")
            assert profile.is_interacted(username3) is True

            print(COLOR_BOLD + f"Check interaction counted for {username4} after multiple actions" + COLOR_ENDC)
            profile.log_get_profile_action(session_id, username4)
            profile.log_like_action(session_id, username4, SourceType.BLOGGER.name, "some_blogger")
            profile.log_like_action(session_id, username4, SourceType.HASHTAG.name, "some_hashtag")
            profile.log_comment_action(session_id, username4, "Wow!", SourceType.PLACE.name, "some_place")
            assert profile.is_interacted(username4) is True

            print(COLOR_BOLD + f"Check interaction is NOT counted for {username5} after "
                               f"follow / story watch / unfollow / filter actions" + COLOR_ENDC)
            profile.log_follow_action(session_id, username5, None, None)
            profile.log_story_watch_action(session_id, username5, None, None)
            profile.log_unfollow_action(session_id, username5)
            profile.log_filter_action(session_id, username5)
            assert profile.is_interacted(username5) is False

            print(COLOR_BOLD + f"Check \"used to follow\" is True after following" + COLOR_ENDC)
            assert profile.used_to_follow(username5) is True
        self._run_inside_session(my_account1, job_interact)

        def job_interact(profile, _):
            print(COLOR_BOLD + f"Check interaction is not counted for {username1} under another account" + COLOR_ENDC)
            assert profile.is_interacted(username1) is False

            print(COLOR_BOLD + f"Check interaction is not counted for {username2} under another account" + COLOR_ENDC)
            assert profile.is_interacted(username2) is False

            print(COLOR_BOLD + f"Check interaction is not counted for {username3} under another account" + COLOR_ENDC)
            assert profile.is_interacted(username3) is False

            print(COLOR_BOLD + f"Check interaction is not counted for {username4} under another account" + COLOR_ENDC)
            assert profile.is_interacted(username4) is False

            print(COLOR_BOLD + f"Check interaction is not counted for {username5} under another account" + COLOR_ENDC)
            assert profile.is_interacted(username5) is False
        self._run_inside_session(my_account2, job_interact)

        def job_interact(profile, session_id):
            print(COLOR_BOLD + f"Check interaction is not counted for {username1} if was too long ago" + COLOR_ENDC)
            profile.log_like_action(session_id, username1, SourceType.BLOGGER.name, "some_blogger", datetime.now() - timedelta(hours=48))
            assert profile.is_interacted(username1) is True
            assert profile.is_interacted(username1, hours=24) is False
        self._run_inside_session(my_account2, job_interact)

    def test_is_filtered(self):
        my_account1 = "my_account1"
        my_account2 = "my_account2"
        username1 = "username1"
        username2 = "username2"

        def job_interact(profile, session_id):
            print(COLOR_BOLD + f"Check users are not filtered by default" + COLOR_ENDC)
            assert profile.is_filtered(username1) is False

            print(COLOR_BOLD + f"Check that filter works" + COLOR_ENDC)
            profile.log_filter_action(session_id, username1)
            assert profile.is_filtered(username1) is True

            print(COLOR_BOLD + f"Check that filter NOT works if filtered too long ago" + COLOR_ENDC)
            profile.log_filter_action(session_id, username2, datetime.now() - timedelta(hours=48))
            assert profile.is_filtered(username2) is True
            assert profile.is_filtered(username2, hours=24) is False
        self._run_inside_session(my_account1, job_interact)

        def job_interact(profile, _):
            print(COLOR_BOLD + f"Check that filter NOT works if filtered under another account" + COLOR_ENDC)
            assert profile.is_filtered(username1) is False
        self._run_inside_session(my_account2, job_interact)

    def test_following_status(self):
        my_account1 = "my_account1"
        my_account2 = "my_account2"
        username1 = "username1"

        def job_interact(profile, _):
            print(COLOR_BOLD + f"Check is_follow_me is None by default" + COLOR_ENDC)
            assert profile.is_follow_me(username1) is None

            print(COLOR_BOLD + f"Check do_i_follow is None by default" + COLOR_ENDC)
            assert profile.do_i_follow(username1) is None

            print(COLOR_BOLD + f"Check that last status is actual one" + COLOR_ENDC)
            profile.update_follow_status(username1, is_follow_me=True, do_i_follow_him=True)
            sleep(1)
            profile.update_follow_status(username1, is_follow_me=False, do_i_follow_him=True)
            assert profile.is_follow_me(username1) is False
            assert profile.do_i_follow(username1) is True
        self._run_inside_session(my_account1, job_interact)

        def job_interact(profile, _):
            print(COLOR_BOLD + f"Check that status is saved only for one account" + COLOR_ENDC)
            assert profile.is_follow_me(username1) is None
            assert profile.do_i_follow(username1) is None
        self._run_inside_session(my_account2, job_interact)

    def test_scraping(self):
        real_account_username = "real"
        scraper_account_username = "scraper"
        username1 = "username1"
        username2 = "username2"
        username3 = "username3"
        username4 = "username4"
        username5 = "username5"
        username6 = "username6"
        username7 = "username7"

        def job_scraper(profile, _):
            print(COLOR_BOLD + "Scraper: check accounts are not scraped by default" + COLOR_ENDC)
            assert profile.is_scrapped(username1, [real_account_username]) is False

            print("Scraper: publishing scrapped accounts")
            profile.publish_scrapped_account(username1, [real_account_username])
            profile.publish_scrapped_account(username1, [real_account_username])  # check with double insert
            profile.publish_scrapped_account(username2, [real_account_username])
            profile.publish_scrapped_account(username3, [real_account_username])
            profile.publish_scrapped_account(username4, [real_account_username])
            profile.publish_scrapped_account(username5, [real_account_username])
            profile.publish_scrapped_account(username6, [real_account_username])

            print(COLOR_BOLD + f"Scraper: check {username1} counts as scrapped" + COLOR_ENDC)
            assert profile.is_scrapped(username1, [real_account_username]) is True
            print(COLOR_BOLD + f"Scraper: check {username1} NOT counts as scrapped for another account" + COLOR_ENDC)
            assert profile.is_scrapped(username1, [real_account_username, "some_another_account"]) is False
        self._run_inside_session(scraper_account_username, job_scraper)

        def job_real(profile, session_id):
            print(COLOR_BOLD + "Real: check scraped accounts count is correct BEFORE interaction" + COLOR_ENDC)
            assert profile.count_scrapped_profiles_for_interaction() == 6

            print(COLOR_BOLD + "Real: check order is FIFO" + COLOR_ENDC)
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username1

            print(COLOR_BOLD + "Real: check idempotence" + COLOR_ENDC)
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username1

            print(COLOR_BOLD + "Real: check account is excluded after \"get profile action\"" + COLOR_ENDC)
            profile.log_get_profile_action(session_id, username1)
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username2

            print(COLOR_BOLD + "Real: check account is excluded after like-interaction" + COLOR_ENDC)
            profile.log_like_action(session_id, username2, SourceType.BLOGGER.name, "some_blogger")
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username3

            print(COLOR_BOLD + "Real: check account is excluded after follow-interaction" + COLOR_ENDC)
            profile.log_follow_action(session_id, username3, SourceType.HASHTAG.name, "some_hashtag")
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username4

            print(COLOR_BOLD + "Real: check account is excluded after story-watch-interaction" + COLOR_ENDC)
            profile.log_story_watch_action(session_id, username4, SourceType.BLOGGER.name, "some_blogger")
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username5

            print(COLOR_BOLD + "Real: check account is excluded after comment-interaction" + COLOR_ENDC)
            profile.log_comment_action(session_id, username5, "Wow!", SourceType.PLACE.name, "some_place")
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username6

            print(COLOR_BOLD + "Real: check account is NOT excluded after unfollow / filter actions" + COLOR_ENDC)
            profile.log_unfollow_action(session_id, username4)
            profile.log_filter_action(session_id, username4)
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username6

            profile.log_like_action(session_id, username6, SourceType.BLOGGER.name, "some_blogger")
            profile.log_like_action(session_id, username6, SourceType.BLOGGER.name, "some_blogger")  # double action check

            print(COLOR_BOLD + "Real: check scraped accounts count is correct AFTER interaction" + COLOR_ENDC)
            assert profile.count_scrapped_profiles_for_interaction() == 0
        self._run_inside_session(real_account_username, job_real)

        def job_scraper(profile, _):
            print("Scraper: publishing scrapped accounts")
            profile.publish_scrapped_account(username1, [real_account_username])
        self._run_inside_session(scraper_account_username, job_scraper)

        def job_real(profile, _):
            print(COLOR_BOLD + "Real: check account is still excluded after being interacted and scraped again" + COLOR_ENDC)
            username = profile.get_scrapped_profile_for_interaction()
            assert username is None
        self._run_inside_session(real_account_username, job_real)

        def job_scraper(profile, _):
            print("Scraper: publishing scrapped accounts")
            profile.publish_scrapped_account(username7, ["some_another_account"])
        self._run_inside_session(scraper_account_username, job_scraper)

        def job_real(profile, _):
            print(COLOR_BOLD + "Real: check account is excluded if scraped for another account" + COLOR_ENDC)
            username = profile.get_scrapped_profile_for_interaction()
            assert username is None
        self._run_inside_session(real_account_username, job_real)

        def job_scraper(profile, _):
            print("Scraper: publishing scrapped accounts")
            profile.publish_scrapped_account(username7, [real_account_username, "some_another_account"])
        self._run_inside_session(scraper_account_username, job_scraper)

        def job_real(profile, _):
            print(COLOR_BOLD + "Real: check account is accepted if scraped again but for real account" + COLOR_ENDC)
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username7
        self._run_inside_session(real_account_username, job_real)

        def job_real(profile, session_id):
            print(f"Real: interact with {username7} from another account")
            profile.log_get_profile_action(session_id, username7)
            profile.log_like_action(session_id, username7, SourceType.BLOGGER.name, "some_blogger")
            profile.log_follow_action(session_id, username7, SourceType.HASHTAG.name, "some_hashtag")
            profile.log_story_watch_action(session_id, username7, SourceType.BLOGGER.name, "some_blogger")
            profile.log_comment_action(session_id, username7, "Wow!", SourceType.PLACE.name, "some_place")
        self._run_inside_session("some_another_account", job_real)

        def job_real(profile, _):
            print(COLOR_BOLD + "Real: check account is still accepted after interacted by another account" + COLOR_ENDC)
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username7
        self._run_inside_session(real_account_username, job_real)

    def tearDown(self):
        print("Deleting test database")
        os.remove(TEST_DATABASE_FILE)

    def _run_inside_session(self, username, action):
        print(f"Starting session for {username}")
        profile = get_ig_profile_by_profile_name(username)
        session_id = profile.start_session(None, "", "", ProfileStatus.VALID, 2200, 500)
        print(f"session_id = {session_id}")
        action(profile, session_id)
        print(f"Ending session for {username}")
        profile.end_session(session_id)

