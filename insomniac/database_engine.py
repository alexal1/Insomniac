import sqlite3

from insomniac.actions_providers import Provider
from insomniac.utils import *

DB_NAME = "interaction_data.db"
DB_VERSIONS = {'3.5.0': 1}

SQL_SELECT_FROM_METADATA = "SELECT * from metadata"
SQL_SELECT_FROM_INTERACTED_USERS_BY_USERNAME = "SELECT * from interacted_users WHERE username = :username"
SQL_SELECT_TARGETS_FROM_INTERACTED_USERS = "SELECT * from interacted_users WHERE interactions_count = 0 " \
                                           "AND (provider = 'TARGETS_LIST' OR provider = 'SCRAPING')"
SQL_SELECT_FROM_FILTERED_USERS_BY_USERNAME = "SELECT * from filtered_users WHERE username = :username"
SQL_SELECT_FROM_SCRAPED_USERS_BY_USERNAME = "SELECT * from scraped_users WHERE username = :username"

SQL_INSERT_INTO_METADATA = "INSERT INTO metadata DEFAULT VALUES"
SQL_INSERT_INTO_INTERACTED_USERS = "INSERT INTO interacted_users (username, last_interaction, " \
                                   "source, interaction_type, provider) VALUES (?, ?, ?, ?, ?)"
SQL_INSERT_INTO_FILTERED_USERS = "INSERT INTO filtered_users (username, filtered_at) VALUES (?, ?)"
SQL_INSERT_INTO_SCRAPED_USERS = "INSERT INTO scraped_users (username, last_interaction) VALUES (?, ?)"
SQL_INSERT_INTO_PROFILES = "INSERT INTO profiles (followers, following) VALUES (?, ?)"
SQL_INSERT_INTO_SESSIONS = """
    INSERT INTO sessions (
        app_version,
        total_interactions,
        successful_interactions,
        total_followed,
        total_likes,
        total_unfollowed,
        total_stories_watched,
        total_get_profile,
        total_scraped,
        removed_mass_followers,
        start_time,
        finish_time,
        args,
        profile_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

SQL_DELETE_FROM_TARGETS_BY_USERNAME = "DELETE from targets WHERE username = :username"

SQL_UPDATE_INTERACTED_USER = "UPDATE interacted_users set following_status = ?, last_interaction = ?, " \
                             "interactions_count = ?, source = ?, interaction_type = ?, provider = ? where username = ?"
SQL_UPDATE_INTERACTED_USER_INTERACTIONS_COUNT = "UPDATE interacted_users set interactions_count = ? where username = ?"
SQL_UPDATE_FILTERED_USER = "UPDATE filtered_users set filtered_at = ? where username = ?"
SQL_UPDATE_SCRAPED_USER = "UPDATE scraped_users set scraping_status = ?, last_interaction = ? where username = ?"

SQL_CREATE_METADATA_TABLE = f"""
    CREATE TABLE IF NOT EXISTS `metadata` (
        `version` INTEGER PRIMARY KEY DEFAULT {max(DB_VERSIONS.values())});"""

SQL_CREATE_INTERACTED_USERS_TABLE = """
    CREATE TABLE IF NOT EXISTS `interacted_users` (
        `username` TEXT PRIMARY KEY,
        `following_status` TEXT CHECK(`following_status` IN ('NONE', 'FOLLOWED', 'UNFOLLOWED')) NOT NULL DEFAULT 'NONE',
        `last_interaction` DATETIME NOT NULL,
        `interactions_count` INTEGER NOT NULL DEFAULT 0,
        `source` TEXT,
        `interaction_type` TEXT,
        `provider` TEXT CHECK(`provider` IN ('UNKNOWN', 'INTERACTION', 'SCRAPING', 'TARGETS_LIST')));"""

SQL_CREATE_SCRAPED_USERS_TABLE = """
    CREATE TABLE IF NOT EXISTS `scraped_users` (
        `username` TEXT PRIMARY KEY,
        `scraping_status` TEXT CHECK(`scraping_status` IN ('SCRAPED','NOT_SCRAPED')) NOT NULL DEFAULT 'NOT_SCRAPED',
        `last_interaction` DATETIME NOT NULL);"""

SQL_CREATE_FILTERED_USERS_TABLE = """
    CREATE TABLE IF NOT EXISTS `filtered_users` (
        `username` TEXT PRIMARY KEY,
        `filtered_at` DATETIME NOT NULL);"""

SQL_CREATE_PROFILE_TABLE = """
    CREATE TABLE IF NOT EXISTS `profiles` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `followers` INTEGER,
        `following` INTEGER);"""

SQL_CREATE_SESSIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS `sessions` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `app_version` TEXT NOT NULL,
        `total_interactions` INTEGER NOT NULL,
        `successful_interactions` INTEGER NOT NULL,
        `total_followed` INTEGER NOT NULL,
        `total_likes` INTEGER NOT NULL,
        `total_unfollowed` INTEGER NOT NULL,
        `total_stories_watched` INTEGER NOT NULL,
        `total_get_profile` INTEGER NOT NULL,
        `total_scraped` INTEGER NOT NULL,
        `removed_mass_followers` TEXT NOT NULL,
        `start_time` DATETIME NOT NULL,
        `finish_time` DATETIME,
        `args` TEXT NOT NULL,
        `profile_id` INTEGER REFERENCES `profiles` (id));"""


def get_database(username):
    address = os.path.join(username, DB_NAME)
    if not check_database_exists(username):
        create_database(address)
    return address


def check_database_exists(username):
    address = os.path.join(username, DB_NAME)
    verify_database_directories(address)
    return os.path.isfile(address)


def create_database(address):
    connection = None
    try:
        connection = sqlite3.connect(address)
        with connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            create_tables(
                cursor,
                [
                    "metadata",
                    "interacted_users",
                    "scraped_users",
                    "filtered_users",
                    "profiles",
                    "sessions",
                    "targets"
                ]
            )
            _update_database(cursor)
            connection.commit()
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot create/open database at {address}: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()


def create_tables(cursor, tables):
    if "metadata" in tables:
        cursor.execute(SQL_CREATE_METADATA_TABLE)

    if "interacted_users" in tables:
        cursor.execute(SQL_CREATE_INTERACTED_USERS_TABLE)

    if "scraped_users" in tables:
        cursor.execute(SQL_CREATE_SCRAPED_USERS_TABLE)

    if "filtered_users" in tables:
        cursor.execute(SQL_CREATE_FILTERED_USERS_TABLE)

    if "profiles" in tables:
        cursor.execute(SQL_CREATE_PROFILE_TABLE)

    if "sessions" in tables:
        cursor.execute(SQL_CREATE_SESSIONS_TABLE)


def verify_database_directories(address):
    db_dir = os.path.dirname(address)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)


def get_interacted_user(address, username):
    connection = None
    interacted_user = None
    try:
        connection = sqlite3.connect(address)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        interacted_user = _select_interacted_user_by_username(cursor, username)
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot get interacted user {username}: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()

    return dict(interacted_user) if interacted_user is not None else None


def update_interacted_users(address,
                            usernames,
                            last_interactions,
                            following_statuses,
                            sources,
                            interaction_types,
                            providers):
    connection = None
    try:
        connection = sqlite3.connect(address)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        for i, username in enumerate(usernames):
            last_interaction = last_interactions[i]
            following_status = following_statuses[i]
            source = sources[i]
            interaction_type = interaction_types[i]
            provider = providers[i]

            interacted_user = _select_interacted_user_by_username(cursor, username)
            if interacted_user is None:
                cursor.execute(SQL_INSERT_INTO_INTERACTED_USERS, (username, last_interaction, source, interaction_type, provider.name))
            cursor.execute(
                SQL_UPDATE_INTERACTED_USER,
                (
                    following_status.name,
                    last_interaction,
                    interacted_user["interactions_count"] + 1 if interacted_user is not None else 1,
                    source if source is not None else (interacted_user["source"] if interacted_user is not None else None),
                    interaction_type if interaction_type is not None else (interacted_user["interaction_type"] if interacted_user is not None else None),
                    provider.name if provider is not None else (interacted_user["provider"] if interacted_user is not None else Provider.UNKNOWN),
                    username
                )
            )
        connection.commit()
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot update interacted users: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()


def get_filtered_user(address, username):
    connection = None
    filtered_user = None
    try:
        connection = sqlite3.connect(address)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        filtered_user = _select_filtered_user_by_username(cursor, username)
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot get filtered user {username}: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()

    return dict(filtered_user) if filtered_user is not None else None


def update_filtered_users(address, usernames, filtered_at_list):
    connection = None
    try:
        connection = sqlite3.connect(address)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        for i, username in enumerate(usernames):
            filtered_at = filtered_at_list[i]

            filtered_user = _select_filtered_user_by_username(cursor, username)
            if filtered_user is None:
                cursor.execute(SQL_INSERT_INTO_FILTERED_USERS, (username, filtered_at))
            cursor.execute(SQL_UPDATE_FILTERED_USER, (filtered_at, username))
        connection.commit()
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot update filtered users: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()


def get_scraped_user(address, username):
    connection = None
    scraped_user = None
    try:
        connection = sqlite3.connect(address)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        scraped_user = _select_scraped_user_by_username(cursor, username)
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot get scraped user {username}: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()

    return dict(scraped_user) if scraped_user is not None else None


def update_scraped_users(address, usernames, last_interactions, scraping_statuses):
    connection = None
    try:
        connection = sqlite3.connect(address)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        for i, username in enumerate(usernames):
            last_interaction = last_interactions[i]
            scraping_status = scraping_statuses[i]

            scraped_user = _select_scraped_user_by_username(cursor, username)
            if scraped_user is None:
                cursor.execute(SQL_INSERT_INTO_SCRAPED_USERS, (username, last_interaction))
            cursor.execute(SQL_UPDATE_SCRAPED_USER, (scraping_status.name, last_interaction, username))
        connection.commit()
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot update scraped users: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()


def add_targets(address, usernames, provider, source=None, interaction_type=None):
    connection = None
    try:
        connection = sqlite3.connect(address)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        for username in usernames:
            user = _select_interacted_user_by_username(cursor, username)
            if user is None:
                cursor.execute(
                    SQL_INSERT_INTO_INTERACTED_USERS,
                    (
                        username,
                        datetime.now(),
                        source,
                        interaction_type,
                        provider.name
                    )
                )
        connection.commit()
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot add targets: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()


def get_target(address):
    """
    Takes a user from interacted_user table which satisfies the following conditions:
    1. Has zero interactions_count
    2. Provider is either TARGETS_LIST or SCRAPING
    Then increments interactions_count.

    :return: username or None if no such user found
    """
    connection = None
    target = None
    try:
        connection = sqlite3.connect(address)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(SQL_SELECT_TARGETS_FROM_INTERACTED_USERS)
        target = cursor.fetchone()
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot pop target: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()

    return target["username"] if target is not None else None


def add_sessions(address, session_states):
    connection = None
    try:
        connection = sqlite3.connect(address)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        for session_state in session_states:
            _add_session(cursor, session_state)
        connection.commit()
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot add sessions: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()


def _update_database(cursor):
    current_version = _get_database_version(cursor)
    latest_version = max(DB_VERSIONS.values())
    if current_version is None:
        cursor.execute(SQL_INSERT_INTO_METADATA)
    elif current_version < latest_version:
        # TODO: here we can add migration logic between database versions
        raise NotImplemented()
    elif current_version > latest_version:
        raise Exception(f"[Database] Current DB version (v{current_version}) is not supported. Please update.")


def _get_database_version(cursor):
    cursor.execute(SQL_SELECT_FROM_METADATA)
    metadata_row = cursor.fetchone()
    if metadata_row is None:
        return None
    return dict(metadata_row)["version"]


def _select_interacted_user_by_username(cursor, username):
    cursor.execute(SQL_SELECT_FROM_INTERACTED_USERS_BY_USERNAME, {"username": username})
    interacted_user = cursor.fetchone()
    return dict(interacted_user) if interacted_user is not None else None


def _select_filtered_user_by_username(cursor, username):
    cursor.execute(SQL_SELECT_FROM_FILTERED_USERS_BY_USERNAME, {"username": username})
    filtered_user = cursor.fetchone()
    return filtered_user


def _select_scraped_user_by_username(cursor, username):
    cursor.execute(SQL_SELECT_FROM_SCRAPED_USERS_BY_USERNAME, {"username": username})
    scraped_user = cursor.fetchone()
    return scraped_user


def _add_session(cursor, session_state):
    cursor.execute(SQL_INSERT_INTO_PROFILES, (session_state.my_followers_count, session_state.my_following_count))
    profile_id = cursor.lastrowid
    cursor.execute(
        SQL_INSERT_INTO_SESSIONS,
        (
            session_state.app_version,
            sum(session_state.totalInteractions.values()),
            sum(session_state.successfulInteractions.values()),
            sum(session_state.totalFollowed.values()),
            session_state.totalLikes,
            session_state.totalUnfollowed,
            session_state.totalStoriesWatched,
            session_state.totalGetProfile,
            sum(session_state.totalScraped.values()),
            str(session_state.removedMassFollowers),
            session_state.startTime,
            session_state.finishTime,
            str(session_state.args),
            profile_id
        )
    )
