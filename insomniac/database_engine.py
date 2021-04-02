# This file is deprecated. We use peewee models (see db_models.py) since v3.7.1

import sqlite3
from enum import Enum, unique

from insomniac.actions_providers import Provider
from insomniac.utils import *

DB_NAME = "interaction_data.db"
DB_VERSIONS = {'3.5.0': 1,
               '3.5.18': 2}

SQL_SELECT_FROM_METADATA = "SELECT * from metadata"
SQL_SELECT_MAX_VERSION_FROM_METADATA = "SELECT MAX(version) from metadata"
SQL_SELECT_FROM_FOLLOW_STATUS_BY_USERNAME = "SELECT * from users_follow_status WHERE username = :username"
SQL_SELECT_FROM_INTERACTED_USERS_BY_USERNAME = "SELECT * from interacted_users WHERE username = :username"
SQL_SELECT_TARGETS_FROM_INTERACTED_USERS = "SELECT * from interacted_users WHERE " \
                                           "provider = 'TARGETS_LIST' OR provider = 'SCRAPING'"
SQL_COUNT_LOADED_TARGETS_FROM_INTERACTED_USERS_BY_SCRAPE = "SELECT COUNT(*) from interacted_users WHERE provider = 'SCRAPING'"
SQL_COUNT_LOADED_TARGETS_FROM_INTERACTED_USERS_BY_TARGETS_LIST = "SELECT COUNT(*) from interacted_users WHERE provider = 'TARGETS_LIST'"
SQL_COUNT_LOADED_NOT_INTERACTED_TARGETS_FROM_INTERACTED_USERS_BY_SCRAPE = "SELECT COUNT(*) from interacted_users WHERE " \
                                                                          "provider = 'SCRAPING' AND interactions_count = 0"
SQL_COUNT_LOADED_NOT_INTERACTED_TARGETS_FROM_INTERACTED_USERS_BY_TARGETS_LIST = "SELECT COUNT(*) from interacted_users WHERE " \
                                                                                "provider = 'TARGETS_LIST' AND interactions_count = 0"
SQL_SELECT_FROM_FILTERED_USERS_BY_USERNAME = "SELECT * from filtered_users WHERE username = :username"
SQL_SELECT_FROM_SCRAPED_USERS_BY_USERNAME = "SELECT * from scraped_users WHERE username = :username"
SQL_SELECT_ALL_SESSIONS = "SELECT * from sessions INNER JOIN profiles ON sessions.profile_id = profiles.id"
SQL_SELECT_ALL_INTERACTED_USERS = "SELECT * from interacted_users"
SQL_SELECT_ALL_FILTERED_USERS = "SELECT * from filtered_users"
SQL_SELECT_ALL_SCRAPED_USERS = "SELECT * from scraped_users"
SQL_SELECT_PROFILE_BY_ID = "SELECT * from profiles WHERE id = :profile_id"

SQL_INSERT_DEFAULT_INTO_METADATA = "INSERT INTO metadata DEFAULT VALUES"
SQL_INSERT_INTO_METADATA = "INSERT INTO metadata (version) VALUES (?)"
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
SQL_INSERT_INTO_FOLLOW_STATUS = "INSERT INTO users_follow_status (username, is_follow_me, " \
                                   "do_i_follow_him, updated_at) VALUES (?, ?, ?, ?)"

SQL_DELETE_FROM_TARGETS_BY_USERNAME = "DELETE from targets WHERE username = :username"

SQL_UPDATE_INTERACTED_USER = "UPDATE interacted_users set following_status = ?, last_interaction = ?, " \
                             "interactions_count = ?, source = ?, interaction_type = ?, provider = ? where username = ?"
SQL_UPDATE_INTERACTED_USER_INTERACTIONS_COUNT = "UPDATE interacted_users set interactions_count = ? where username = ?"
SQL_UPDATE_FILTERED_USER = "UPDATE filtered_users set filtered_at = ? where username = ?"
SQL_UPDATE_SCRAPED_USER = "UPDATE scraped_users set scraping_status = ?, last_interaction = ? where username = ?"
SQL_UPDATE_FOLLOW_STATUS = "UPDATE users_follow_status set is_follow_me = ?, do_i_follow_him = ?, " \
                           "updated_at = ? where username = ?"

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

SQL_CREATE_USERS_FOLLOW_STATUS_TABLE = """
    CREATE TABLE IF NOT EXISTS `users_follow_status` (
        `username` TEXT PRIMARY KEY,
        `is_follow_me` TEXT CHECK(`is_follow_me` IN ('UNKNOWN', 'TRUE', 'FALSE')) NOT NULL DEFAULT 'UNKNOWN',
        `do_i_follow_him` TEXT CHECK(`do_i_follow_him` IN ('UNKNOWN', 'TRUE', 'FALSE')) NOT NULL DEFAULT 'UNKNOWN',
        `updated_at` DATETIME NOT NULL);"""


def get_database(username):
    address = os.path.join(username, DB_NAME)
    if not check_database_exists(username):
        create_database(address)
    else:
        migrate_database_if_needed(address)
    return address


def check_database_exists(username, create_db_dir=True):
    address = os.path.join(username, DB_NAME)
    verify_database_directories(address, create_db_dir)
    return os.path.isfile(address)


def migrate_database_if_needed(address):
    connection = None
    try:
        connection = sqlite3.connect(address)
        with connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            _run_migrations(cursor)
            connection.commit()
    except DatabaseMigrationFailedException as e:
        raise e
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot create/open database at {address}: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()


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
                    "targets",
                    "users_follow_status"
                ]
            )
            cursor.execute(SQL_INSERT_DEFAULT_INTO_METADATA)
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

    if "users_follow_status" in tables:
        cursor.execute(SQL_CREATE_USERS_FOLLOW_STATUS_TABLE)


def verify_database_directories(address, create_db_dir=True):
    db_dir = os.path.dirname(address)
    if not os.path.exists(db_dir) and create_db_dir:
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


def get_all_interacted_users(address):
    connection = None
    interacted_users = None
    try:
        connection = sqlite3.connect(address)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        cursor.execute(SQL_SELECT_ALL_INTERACTED_USERS)
        interacted_users = cursor.fetchall()
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot get all interacted users: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()

    return list(interacted_users) if interacted_users is not None else ()


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


def get_user_follow_status(address, username):
    connection = None
    follow_status = None
    try:
        connection = sqlite3.connect(address)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        follow_status = _select_follow_status_by_username(cursor, username)
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot get user's follow status of {username}: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()

    return dict(follow_status) if follow_status is not None else None


def update_user_follow_status(address,
                              username,
                              is_follow_me,
                              do_i_follow_him,
                              updated_at):
    connection = None
    try:
        connection = sqlite3.connect(address)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        interacted_user = _select_follow_status_by_username(cursor, username)
        if interacted_user is None:
            cursor.execute(SQL_INSERT_INTO_FOLLOW_STATUS, (username, 'UNKNOWN', 'UNKNOWN', updated_at))
        cursor.execute(
            SQL_UPDATE_FOLLOW_STATUS,
            (
                'TRUE' if is_follow_me else 'FALSE',
                'TRUE' if do_i_follow_him else 'FALSE',
                updated_at,
                username
            )
        )
        connection.commit()
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot update user's follow-status: {e}" + COLOR_ENDC)
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


def get_all_filtered_users(address):
    connection = None
    filtered_users = None
    try:
        connection = sqlite3.connect(address)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        cursor.execute(SQL_SELECT_ALL_FILTERED_USERS)
        filtered_users = cursor.fetchall()
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot get all filtered users: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()

    return list(filtered_users) if filtered_users is not None else ()


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


def get_all_scraped_users(address):
    connection = None
    scraped_users = None
    try:
        connection = sqlite3.connect(address)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        cursor.execute(SQL_SELECT_ALL_FILTERED_USERS)
        scraped_users = cursor.fetchall()
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot get all filtered users: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()

    return list(scraped_users) if scraped_users is not None else ()


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


def get_target(address, user_false_validators):
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
        while target is not None:
            is_user_validated = True
            for validator in user_false_validators:
                if validator(target["username"]):
                    is_user_validated = False
                    break

            if is_user_validated:
                # Wasn't filtered before / blacklisted so returning that one
                break

            target = cursor.fetchone()

    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot pop target: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()

    target_username = None
    provider = None
    if target is not None:
        target_username = target["username"]
        provider = Provider.SCRAPING if target["provider"] == "SCRAPING" else Provider.TARGETS_LIST
    return target_username, provider


def count_targets(address):
    connection = None
    not_interacted_targets = {"scraped": None, "targets": None}
    total_loaded_targets = {"scraped": None, "targets": None}
    try:
        connection = sqlite3.connect(address)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(SQL_COUNT_LOADED_TARGETS_FROM_INTERACTED_USERS_BY_SCRAPE)
        total_loaded_targets["scraped"] = cursor.fetchone()[0]
        cursor = connection.cursor()
        cursor.execute(SQL_COUNT_LOADED_TARGETS_FROM_INTERACTED_USERS_BY_TARGETS_LIST)
        total_loaded_targets["targets"] = cursor.fetchone()[0]
        cursor = connection.cursor()
        cursor.execute(SQL_COUNT_LOADED_NOT_INTERACTED_TARGETS_FROM_INTERACTED_USERS_BY_SCRAPE)
        not_interacted_targets["scraped"] = cursor.fetchone()[0]
        cursor = connection.cursor()
        cursor.execute(SQL_COUNT_LOADED_NOT_INTERACTED_TARGETS_FROM_INTERACTED_USERS_BY_TARGETS_LIST)
        not_interacted_targets["targets"] = cursor.fetchone()[0]
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot count targets target: {e}" + COLOR_ENDC)
        total_loaded_targets = None
        not_interacted_targets = None
    finally:
        if connection:
            # Close the opened connection
            connection.close()

    return total_loaded_targets, not_interacted_targets


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


def get_all_sessions(address):
    connection = None
    sessions = None
    try:
        connection = sqlite3.connect(address)
        connection.row_factory = dict_factory
        cursor = connection.cursor()
        cursor.execute(SQL_SELECT_ALL_SESSIONS)
        sessions = cursor.fetchall()
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Cannot get all sessions: {e}" + COLOR_ENDC)
    finally:
        if connection:
            # Close the opened connection
            connection.close()

    return list(sessions) if sessions is not None else ()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def _run_migrations(cursor):
    current_version = _get_database_version(cursor)
    latest_version = max(DB_VERSIONS.values())

    if current_version is None:
        return

    if current_version > latest_version:
        raise Exception(f"[Database] Current DB version (v{current_version}) is newer from your Insomniac version and "
                        f"not supported. Please update Insomniac.")

    if current_version < latest_version:
        print(f"[Database] Going to migrate database to a newer version...")
        while current_version < latest_version:
            _migrate(current_version, cursor)
            current_version = _get_database_version(cursor)


def _get_database_version(cursor):
    cursor.execute(SQL_SELECT_MAX_VERSION_FROM_METADATA)
    metadata_row = cursor.fetchone()
    if metadata_row is None:
        print(COLOR_FAIL + f"[Database] Couldn't find database-version on metadata. "
                           f"Using database as is (without trying to migrate)." + COLOR_ENDC)
        return None
    return dict(metadata_row)["MAX(version)"]


def _select_interacted_user_by_username(cursor, username):
    cursor.execute(SQL_SELECT_FROM_INTERACTED_USERS_BY_USERNAME, {"username": username})
    interacted_user = cursor.fetchone()
    return dict(interacted_user) if interacted_user is not None else None


def _select_follow_status_by_username(cursor, username):
    cursor.execute(SQL_SELECT_FROM_FOLLOW_STATUS_BY_USERNAME, {"username": username})
    user_follow_status = cursor.fetchone()
    return dict(user_follow_status) if user_follow_status is not None else None


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


def _migrate_db_from_version_1_to_2(cursor):
    """
    Changes added on DB version 2:
      * Added users_follow_status database

    """

    create_tables(
        cursor,
        [
            "users_follow_status"
        ]
    )


def _migrate(curr_version, cursor):
    print(f"[Database] Going to run database migration from version {curr_version} to {curr_version+1}")

    migration_method = database_migrations[f"{curr_version}->{curr_version + 1}"]
    try:
        migration_method(cursor)
    except Exception as e:
        print(COLOR_FAIL + f"[Database] Got an error while migrating database from version "
                           f"{curr_version} to {curr_version + 1}, Error: {str(e)}" + COLOR_ENDC)
        raise DatabaseMigrationFailedException()

    print(f"[Database] database migration from version {curr_version} to {curr_version+1} has been done successfully")
    print(f"[Database] Updating database version to be {curr_version+1}")
    cursor.execute(SQL_INSERT_INTO_METADATA, (curr_version+1,))


database_migrations = {
    "1->2": _migrate_db_from_version_1_to_2
}


class DatabaseMigrationFailedException(Exception):
    pass


@unique
class ScrappingStatus(Enum):
    SCRAPED = 0
    NOT_SCRAPED = 1
