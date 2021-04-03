import json

from insomniac.db_models import DATABASE_NAME
from insomniac.session_state import SessionState
from insomniac.sessions import FILENAME_SESSIONS, Sessions
from insomniac.storage import *
from insomniac.utils import *

FILENAME_INTERACTED_USERS = "interacted_users.json"  # deprecated
FILENAME_SCRAPPED_USERS = "scrapped_users.json"  # deprecated
FILENAME_FILTERED_USERS = "filtered_users.json"  # deprecated
USER_LAST_INTERACTION = "last_interaction"  # deprecated
USER_INTERACTIONS_COUNT = "interactions_count"  # deprecated
USER_FILTERED_AT = "filtered_at"  # deprecated
USER_FOLLOWING_STATUS = "following_status"  # deprecated
USER_SCRAPPING_STATUS = "scrapping_status"  # deprecated


def get_db(user_name):
    if check_database_exists(user_name):
        return None

    database = get_database(user_name)
    return database


def migrate_from_json_to_sql(my_username):
    """
    Migration from JSON storage (v3.4.2) to SQL storage (v3.5.0).
    """
    if my_username is None:
        return

    interacted_users_path = os.path.join(my_username, FILENAME_INTERACTED_USERS)
    if os.path.exists(interacted_users_path):
        try:
            database = get_db(my_username)
            if database is None:
                return
            print(f"[Migration] Loading data from {FILENAME_INTERACTED_USERS}...")
            with open(interacted_users_path, encoding="utf-8") as json_file:
                interacted_users = json.load(json_file)
                usernames = []
                last_interactions = []
                following_statuses = []
                sources = []
                interaction_types = []
                providers = []
                for username in interacted_users.keys():
                    usernames.append(username)
                    user = interacted_users[username]
                    last_interactions.append(datetime.strptime(user[USER_LAST_INTERACTION], '%Y-%m-%d %H:%M:%S.%f'))
                    following_statuses.append(FollowingStatus[user[USER_FOLLOWING_STATUS].upper()])
                    sources.append(None)
                    interaction_types.append(None)
                    providers.append(Provider.UNKNOWN)

                update_interacted_users(database, usernames, last_interactions, following_statuses, sources, interaction_types, providers)
                print(COLOR_BOLD + f"[Migration] Done! You can now delete {FILENAME_INTERACTED_USERS}" + COLOR_ENDC)
        except ValueError as e:
            print(COLOR_FAIL + f"[Migration] Cannot load {FILENAME_INTERACTED_USERS}: {e}" + COLOR_ENDC)

    scrapped_users_path = os.path.join(my_username, FILENAME_SCRAPPED_USERS)
    if os.path.exists(scrapped_users_path):
        try:
            database = get_db(my_username)
            if database is None:
                return
            print(f"[Migration] Loading data from {FILENAME_SCRAPPED_USERS}...")
            with open(scrapped_users_path, encoding="utf-8") as json_file:
                scrapped_users = json.load(json_file)
                usernames = []
                last_interactions = []
                scraping_statuses = []
                for username in scrapped_users.keys():
                    usernames.append(username)
                    user = scrapped_users[username]
                    last_interactions.append(datetime.strptime(user[USER_LAST_INTERACTION], '%Y-%m-%d %H:%M:%S.%f'))
                    scraping_statuses.append(ScrappingStatus[user[USER_SCRAPPING_STATUS].upper()])

                update_scraped_users(database, usernames, last_interactions, scraping_statuses)
                print(COLOR_BOLD + f"[Migration] Done! You can now delete {FILENAME_SCRAPPED_USERS}" + COLOR_ENDC)
        except ValueError as e:
            print(COLOR_FAIL + f"[Migration] Cannot load {FILENAME_SCRAPPED_USERS}: {e}" + COLOR_ENDC)

    filtered_users_path = os.path.join(my_username, FILENAME_FILTERED_USERS)
    if os.path.exists(filtered_users_path):
        try:
            database = get_db(my_username)
            if database is None:
                return
            print(f"[Migration] Loading data from {FILENAME_FILTERED_USERS}...")
            with open(filtered_users_path, encoding="utf-8") as json_file:
                filtered_users = json.load(json_file)
                usernames = []
                filtered_at_list = []
                for username in filtered_users.keys():
                    usernames.append(username)
                    user = filtered_users[username]
                    filtered_at_list.append(datetime.strptime(user[USER_FILTERED_AT], '%Y-%m-%d %H:%M:%S.%f'))

                update_filtered_users(database, usernames, filtered_at_list)
                print(COLOR_BOLD + f"[Migration] Done! You can now delete {FILENAME_FILTERED_USERS}" + COLOR_ENDC)
        except ValueError as e:
            print(COLOR_FAIL + f"[Migration] Cannot load {FILENAME_FILTERED_USERS}: {e}" + COLOR_ENDC)

    sessions_path = os.path.join(my_username, FILENAME_SESSIONS)
    if os.path.exists(sessions_path):
        try:
            database = get_db(my_username)
            if database is None:
                return
            print(f"[Migration] Loading data from {FILENAME_SESSIONS}...")
            sessions_persistent_list = Sessions()
            with open(sessions_path, encoding="utf-8") as json_file:
                sessions = json.load(json_file)
                for session in sessions:
                    session_state = SessionState()
                    session_state.id = session["id"]
                    session_state.args = str(session["args"])
                    session_state.app_version = session.get("app_version", "")
                    session_state.my_username = my_username
                    session_state.my_followers_count = session["profile"].get("followers", 0)
                    session_state.my_following_count = session["profile"].get("following", 0)
                    session_state.totalInteractions = {None: session["total_interactions"]}
                    session_state.successfulInteractions = {None: session["successful_interactions"]}
                    session_state.totalFollowed = {None: session["total_followed"]}
                    session_state.totalScraped = session.get("total_scraped", {})
                    session_state.totalLikes = session["total_likes"]
                    session_state.totalGetProfile = session.get("total_get_profile", 0)
                    session_state.totalUnfollowed = session.get("total_unfollowed", 0)
                    session_state.totalStoriesWatched = session.get("total_stories_watched", 0)
                    if "removed_mass_followers" in session:
                        session_state.removedMassFollowers = session["removed_mass_followers"]
                    if "total_removed_mass_followers" in session:
                        session_state.removedMassFollowers = session["total_removed_mass_followers"]
                    session_state.startTime = datetime.strptime(session["start_time"], '%Y-%m-%d %H:%M:%S.%f')
                    if session.get("finish_time") != "None":
                        session_state.finishTime = datetime.strptime(session["finish_time"], '%Y-%m-%d %H:%M:%S.%f')

                    sessions_persistent_list.append(session_state)
                sessions_persistent_list.persist(my_username)
                print(COLOR_BOLD + f"[Migration] Done! You can now delete {FILENAME_SESSIONS}" + COLOR_ENDC)
        except ValueError as e:
            print(COLOR_FAIL + f"[Migration] Cannot load {FILENAME_SESSIONS}: {e}" + COLOR_ENDC)


def migrate_from_sql_to_peewee(my_username):
    """
    Migration from SQL storage (v3.7.0) to peewee ORM (v3.7.1).
    """
    if my_username is None:
        return

    if not check_database_exists(my_username, False):
        return

    if not db_models.init():
        return

    database = get_database(my_username)
    my_profile = get_ig_profile_by_profile_name(my_username)

    print(f"[Migration] Migrating sessions to the {DATABASE_NAME}...")
    for session in get_all_sessions(database):
        my_profile.add_session(None,
                               session["app_version"] or "",
                               session["args"] or "",
                               ProfileStatus.VALID,
                               session["followers"] or -1,
                               session["following"] or -1,
                               datetime.strptime(session["start_time"] or datetime.now(), '%Y-%m-%d %H:%M:%S.%f'),
                               datetime.strptime(session["finish_time"] or datetime.now(), '%Y-%m-%d %H:%M:%S.%f'))

    session_id = my_profile.start_session(None, "Unknown app version: migration", "Unknown args: migration", ProfileStatus.VALID, -1, -1)
    print(f"[Migration] Migrating interacted users to the {DATABASE_NAME}...")
    for interacted_user in get_all_interacted_users(database):
        my_profile.log_like_action(session_id, interacted_user["username"], None, None)
    print(f"[Migration] Migrating filtered users to the {DATABASE_NAME}...")
    for filtered_user in get_all_filtered_users(database):
        my_profile.log_filter_action(session_id, filtered_user["username"])
    print(f"[Migration] Migrating scraped users to the {DATABASE_NAME}...")
    for scraped_user in get_all_scraped_users(database):
        my_profile.publish_scrapped_account(scraped_user["username"], [my_username])
    my_profile.end_session(session_id)

    print(COLOR_BOLD + f"[Migration] Done! Now you can now delete {database}" + COLOR_ENDC)
