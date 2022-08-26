import unittest

from peewee import SqliteDatabase

from insomniac import db_models
from insomniac.actions_types import SourceType, LikeAction, FollowAction
from insomniac.db_models import get_ig_profile_by_profile_name, MODELS, get_actions_count_for_profiles, \
    get_session_count_from_to, get_ig_profiles_by_profiles_names, get_actions_count_within_hours_for_profiles
from insomniac.storage import ProfileStatus, SessionPhase
from insomniac.utils import *

TEST_DATABASE_FILE = 'test.db'
test_db = SqliteDatabase(TEST_DATABASE_FILE, autoconnect=False)

# Uncomment to test on PostgreSQL:
# from peewee import PostgresqlDatabase
# test_db = PostgresqlDatabase('your_database_name', user='your_username', password='your_password', host='localhost', port=5432, autoconnect=False)


class DatabaseTests(unittest.TestCase):

    def setUp(self):
        print("Creating test database with tables")
        db_models.db = test_db
        test_db.bind(MODELS)
        test_db.connect()
        test_db.create_tables(MODELS)
        test_db.close()

    def test_validate_profile_info(self):
        my_account = "my_account"
        start_time1 = (datetime.now() - timedelta(hours=1)).replace(microsecond=0)
        start_time2 = datetime.now().replace(microsecond=0)

        def job_interact(profile, session_id):
            pass  # just empty job to make a "profile info" record
        self._run_inside_session(my_account, job_interact, start_time=start_time1)

        def job_interact(profile, session_id):
            print(COLOR_BOLD + f"Validate last profile info's timestamp " + COLOR_ENDC)
            profile_info = profile.get_latsest_profile_info()
            assert profile_info.timestamp == start_time2
        self._run_inside_session(my_account, job_interact, start_time=start_time2)

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
            profile.log_get_profile_action(session_id, SessionPhase.TASK_LOGIC.value, username1)
            assert profile.is_interacted(username1) is True

            print(COLOR_BOLD + f"Check interaction counted for {username2} after a like" + COLOR_ENDC)
            profile.log_like_action(session_id, SessionPhase.TASK_LOGIC.value, username2, SourceType.BLOGGER.name, "some_blogger")
            assert profile.is_interacted(username2) is True

            print(COLOR_BOLD + f"Check interaction counted for {username3} after a comment" + COLOR_ENDC)
            profile.log_comment_action(session_id, SessionPhase.TASK_LOGIC.value, username3, "Wow!", SourceType.BLOGGER.name, "some_blogger")
            assert profile.is_interacted(username3) is True

            print(COLOR_BOLD + f"Check interaction counted for {username4} after multiple actions" + COLOR_ENDC)
            profile.log_get_profile_action(session_id, SessionPhase.TASK_LOGIC.value, username4)
            profile.log_like_action(session_id, SessionPhase.TASK_LOGIC.value, username4, SourceType.BLOGGER.name, "some_blogger")
            profile.log_like_action(session_id, SessionPhase.TASK_LOGIC.value, username4, SourceType.HASHTAG.name, "some_hashtag")
            profile.log_comment_action(session_id, SessionPhase.TASK_LOGIC.value, username4, "Wow!", SourceType.PLACE.name, "some_place")
            assert profile.is_interacted(username4) is True

            print(COLOR_BOLD + f"Check interaction is NOT counted for {username5} after "
                               f"follow / story watch / unfollow / filter actions" + COLOR_ENDC)
            profile.log_follow_action(session_id, SessionPhase.TASK_LOGIC.value, username5, None, None)
            profile.log_story_watch_action(session_id, SessionPhase.TASK_LOGIC.value, username5, None, None)
            profile.log_unfollow_action(session_id, SessionPhase.TASK_LOGIC.value, username5)
            profile.log_filter_action(session_id, SessionPhase.TASK_LOGIC.value, username5)
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
            profile.log_like_action(session_id, SessionPhase.TASK_LOGIC.value, username1, SourceType.BLOGGER.name, "some_blogger", timestamp=datetime.now()-timedelta(hours=48))
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
            profile.log_filter_action(session_id, SessionPhase.TASK_LOGIC.value, username1)
            assert profile.is_filtered(username1) is True

            print(COLOR_BOLD + f"Check that filter NOT works if filtered too long ago" + COLOR_ENDC)
            profile.log_filter_action(session_id, SessionPhase.TASK_LOGIC.value, username2, timestamp=datetime.now()-timedelta(hours=48))
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
        username8 = "username8"

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
            profile.publish_scrapped_account(username7, [real_account_username])

            print(COLOR_BOLD + f"Scraper: check {username1} counts as scrapped" + COLOR_ENDC)
            assert profile.is_scrapped(username1, [real_account_username]) is True
            print(COLOR_BOLD + f"Scraper: check {username1} NOT counts as scrapped for another account" + COLOR_ENDC)
            assert profile.is_scrapped(username1, [real_account_username, "some_another_account"]) is False
        self._run_inside_session(scraper_account_username, job_scraper)

        def job_real(profile, session_id):
            print(COLOR_BOLD + "Real: check scraped accounts count is correct BEFORE interaction" + COLOR_ENDC)
            assert profile.count_scrapped_profiles_for_interaction() == 7

            print(COLOR_BOLD + "Real: check order is FIFO" + COLOR_ENDC)
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username1

            print(COLOR_BOLD + "Real: check idempotence" + COLOR_ENDC)
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username1

            print(COLOR_BOLD + "Real: check account is excluded after \"get profile action\"" + COLOR_ENDC)
            profile.log_get_profile_action(session_id, SessionPhase.TASK_LOGIC.value, username1)
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username2

            print(COLOR_BOLD + "Real: check account is excluded after like-interaction" + COLOR_ENDC)
            profile.log_like_action(session_id, SessionPhase.TASK_LOGIC.value, username2, SourceType.BLOGGER.name, "some_blogger")
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username3

            print(COLOR_BOLD + "Real: check account is excluded after follow-interaction" + COLOR_ENDC)
            profile.log_follow_action(session_id, SessionPhase.TASK_LOGIC.value, username3, SourceType.HASHTAG.name, "some_hashtag")
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username4

            print(COLOR_BOLD + "Real: check account is excluded after story-watch-interaction" + COLOR_ENDC)
            profile.log_story_watch_action(session_id, SessionPhase.TASK_LOGIC.value, username4, SourceType.BLOGGER.name, "some_blogger")
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username5

            print(COLOR_BOLD + "Real: check account is excluded after comment-interaction" + COLOR_ENDC)
            profile.log_comment_action(session_id, SessionPhase.TASK_LOGIC.value, username5, "Wow!", SourceType.PLACE.name, "some_place")
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username6

            print(COLOR_BOLD + "Real: check account is excluded after being filtered" + COLOR_ENDC)
            profile.log_filter_action(session_id, SessionPhase.TASK_LOGIC.value, username6)
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username7

            print(COLOR_BOLD + "Real: check account is NOT excluded after unfollow / change profile info actions" + COLOR_ENDC)
            profile.log_unfollow_action(session_id, SessionPhase.TASK_LOGIC.value, username4)
            profile.log_change_profile_info_action(session_id, SessionPhase.TASK_LOGIC.value, "some_url", "some_name", "some_description")
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username7

            profile.log_like_action(session_id, SessionPhase.TASK_LOGIC.value, username7, SourceType.BLOGGER.name, "some_blogger")
            profile.log_like_action(session_id, SessionPhase.TASK_LOGIC.value, username7, SourceType.BLOGGER.name, "some_blogger")  # double action check

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
            profile.publish_scrapped_account(username8, ["some_another_account"])
        self._run_inside_session(scraper_account_username, job_scraper)

        def job_real(profile, _):
            print(COLOR_BOLD + "Real: check account is excluded if scraped for another account" + COLOR_ENDC)
            username = profile.get_scrapped_profile_for_interaction()
            assert username is None
        self._run_inside_session(real_account_username, job_real)

        def job_scraper(profile, _):
            print("Scraper: publishing scrapped accounts")
            profile.publish_scrapped_account(username8, [real_account_username, "some_another_account"])
        self._run_inside_session(scraper_account_username, job_scraper)

        def job_real(profile, _):
            print(COLOR_BOLD + "Real: check account is accepted if scraped again but for real account" + COLOR_ENDC)
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username8
        self._run_inside_session(real_account_username, job_real)

        def job_real(profile, session_id):
            print(f"Real: interact with {username8} from another account")
            profile.log_get_profile_action(session_id, SessionPhase.TASK_LOGIC.value, username8)
            profile.log_like_action(session_id, SessionPhase.TASK_LOGIC.value, username8, SourceType.BLOGGER.name, "some_blogger")
            profile.log_follow_action(session_id, SessionPhase.TASK_LOGIC.value, username8, SourceType.HASHTAG.name, "some_hashtag")
            profile.log_story_watch_action(session_id, SessionPhase.TASK_LOGIC.value, username8, SourceType.BLOGGER.name, "some_blogger")
            profile.log_comment_action(session_id, SessionPhase.TASK_LOGIC.value, username8, "Wow!", SourceType.PLACE.name, "some_place")
        self._run_inside_session("some_another_account", job_real)

        def job_real(profile, _):
            print(COLOR_BOLD + "Real: check account is still accepted after interacted by another account" + COLOR_ENDC)
            username = profile.get_scrapped_profile_for_interaction()
            assert username == username8
        self._run_inside_session(real_account_username, job_real)

    def test_statistics(self):
        my_account1 = "my_account1"
        my_account2 = "my_account2"
        username1 = "username1"
        username2 = "username2"
        profiles = list(get_ig_profiles_by_profiles_names([my_account1, my_account2]).values())

        def job_interact(profile, session_id):
            profile.log_like_action(session_id, SessionPhase.TASK_LOGIC.value, username1, SourceType.BLOGGER.name, "some_blogger")
            profile.log_like_action(session_id, SessionPhase.TASK_LOGIC.value, username2, SourceType.BLOGGER.name, "some_blogger", timestamp=datetime.now()-timedelta(hours=2))
            profile.log_follow_action(session_id, SessionPhase.TASK_LOGIC.value, username2, None, None)
        self._run_inside_session(my_account1, job_interact)

        def job_interact(profile, session_id):
            profile.log_like_action(session_id, SessionPhase.TASK_LOGIC.value, username1, SourceType.BLOGGER.name, "some_blogger")
        self._run_inside_session(my_account2, job_interact)

        with test_db.connection_context():
            stats = get_actions_count_for_profiles(profiles=profiles)
            stats_1_hour = get_actions_count_within_hours_for_profiles(profiles=profiles, hours=1)
            stats_24_hours = get_actions_count_within_hours_for_profiles(profiles=profiles, hours=24)
            sessions = get_session_count_from_to(profiles=profiles)

        assert stats[my_account1][LikeAction.__name__] == 2
        assert stats[my_account1][FollowAction.__name__] == 1

        assert stats_1_hour[my_account1][LikeAction.__name__] == 1
        assert stats_1_hour[my_account1][FollowAction.__name__] == 1

        assert stats_24_hours[my_account1][LikeAction.__name__] == 2
        assert stats_24_hours[my_account1][FollowAction.__name__] == 1

        assert sum(sessions.values()) == 2

    def test_session_time(self):
        my_account1 = "my_account1"
        my_account2 = "my_account2"
        username = "username"

        def job_interact(profile, session_id):
            profile.log_get_profile_action(session_id, SessionPhase.TASK_LOGIC.value, username)
            profile.log_like_action(session_id, SessionPhase.TASK_LOGIC.value, username, SourceType.BLOGGER.name, "some_blogger")

        # Account 1: interact yesterday (10 hour)
        start_time = datetime.now() - timedelta(hours=34)
        end_time = datetime.now() - timedelta(hours=24)
        self._run_inside_session(my_account1, job_interact, start_time, end_time)

        # Account 1: interact today (1 hour)
        start_time = datetime.now() - timedelta(hours=3)
        end_time = datetime.now() - timedelta(hours=2)
        self._run_inside_session(my_account1, job_interact, start_time, end_time)

        # Account 1: interact today (1 hour)
        start_time = datetime.now() - timedelta(hours=2)
        end_time = datetime.now() - timedelta(hours=1)
        self._run_inside_session(my_account1, job_interact, start_time, end_time)

        # Account 2: interact today (10 hours)
        start_time = datetime.now() - timedelta(hours=11)
        end_time = datetime.now() - timedelta(hours=1)
        self._run_inside_session(my_account2, job_interact, start_time, end_time)

        def job_get_session_time(profile, session_id):
            print(COLOR_BOLD + f"Check session time for last 24 hours" + COLOR_ENDC)
            assert profile.get_session_time_in_seconds_within_minutes(60 * 24) == 3 * 60 * 60
        start_time = datetime.now() - timedelta(hours=1)
        self._run_inside_session(my_account1, job_get_session_time, start_time)

    def test_get_oldest_followed_username(self):
        my_account1 = "my_account1"
        my_account2 = "my_account2"
        username1 = "username1"
        username2 = "username2"
        username3 = "username3"
        username4 = "username4"
        username5 = "username5"

        # Test that initially returns nothing
        def job_get_oldest_followed_username(profile, session_id):
            oldest_followed_username, oldest_followed_date = profile.get_oldest_followed_username()
            assert oldest_followed_username is None and oldest_followed_date is None
        self._run_inside_session(my_account2, job_get_oldest_followed_username)

        # Do some follow from my_account1 which shouldn't make any sense
        def job_do_follow(profile, session_id):
            # Follow username3
            profile.log_follow_action(session_id, SessionPhase.TASK_LOGIC.value, username3, None, None)
            profile.update_follow_status(username3, do_i_follow_him=True, is_follow_me=False)
            sleep(1)
        self._run_inside_session(my_account1, job_do_follow)

        def job_do_follows_unfollows(profile, session_id):
            # Fake follow username4
            profile.update_follow_status(username4, do_i_follow_him=True, is_follow_me=False)
            sleep(1)

            # Follow username1
            profile.log_follow_action(session_id, SessionPhase.TASK_LOGIC.value, username1, None, None)
            profile.update_follow_status(username1, do_i_follow_him=True, is_follow_me=False)
            sleep(1)

            # Follow username2
            profile.log_follow_action(session_id, SessionPhase.TASK_LOGIC.value, username2, None, None)
            profile.update_follow_status(username2, do_i_follow_him=True, is_follow_me=False)
            sleep(1)

            # Unfollow username1
            profile.log_unfollow_action(session_id, SessionPhase.TASK_LOGIC.value, username1)
            profile.update_follow_status(username1, do_i_follow_him=False, is_follow_me=False)
            sleep(1)

            # Follow username5
            profile.log_follow_action(session_id, SessionPhase.TASK_LOGIC.value, username5, None, None)
            profile.update_follow_status(username5, do_i_follow_him=True, is_follow_me=False)
            sleep(1)
        self._run_inside_session(my_account2, job_do_follows_unfollows)

        def job_get_oldest_followed_username(profile, session_id):
            oldest_followed_username, _ = profile.get_oldest_followed_username()
            assert oldest_followed_username == username2
        self._run_inside_session(my_account2, job_get_oldest_followed_username)

    def tearDown(self):
        print("Deleting test database")
        with test_db.connection_context():
            test_db.drop_tables(MODELS)
        try:
            os.remove(TEST_DATABASE_FILE)
        except FileNotFoundError:
            pass

    def _run_inside_session(self, username, action, start_time=None, end_time=None):
        print(f"Starting session for {username}")
        profile = get_ig_profile_by_profile_name(username)
        session_id = profile.start_session(None, "", "", ProfileStatus.VALID.value, 2200, 500, start_time)
        print(f"session_id = {session_id}")
        action(profile, session_id)
        print(f"Ending session for {username}")
        profile.end_session(session_id, end_time)

