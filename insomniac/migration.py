from insomniac.session_state import SessionState
from insomniac.sessions import FILENAME_SESSIONS, Sessions
from insomniac.storage import *
from insomniac.utils import *


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
