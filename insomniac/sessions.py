from insomniac.database_engine import get_database, add_sessions

FILENAME_SESSIONS = "sessions.json"  # deprecated


class Sessions(list):

    def persist(self, username):
        """
        Save the sessions list to the database and then clear this list.
        """
        if username:
            database = get_database(username)
            add_sessions(database, [self[-1]])
