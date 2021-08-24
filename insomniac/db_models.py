import uuid
from collections import defaultdict
from typing import Optional

from peewee import *
from playhouse.migrate import SqliteMigrator, migrate

from insomniac.utils import *
from insomniac.globals import executable_name

DATABASE_NAME = f'{executable_name}.db'
DATABASE_VERSION = 3

db = SqliteDatabase(DATABASE_NAME, autoconnect=False)


class InsomniacModel(Model):
    class Meta:
        database = db


class InstagramProfile(InsomniacModel):
    name = TextField(unique=True)

    class Meta:
        db_table = 'instagram_profiles'

    def start_session(self, app_id, app_version, args, profile_status, followers_count, following_count) -> uuid.UUID:
        """
        Create InstagramProfileInfo record
        Create SessionInfo record
        Return the session id
        """
        with db.connection_context():
            profile_info = InstagramProfileInfo.create(profile=self,
                                                       status=profile_status,
                                                       followers=followers_count,
                                                       following=following_count)

            session = SessionInfo.create(app_id=app_id,
                                         app_version=app_version,
                                         args=args,
                                         profile_info=profile_info)
        return session.id

    def end_session(self, session_id):
        """
        Add end-timestamp to the SessionInfo record
        """
        with db.connection_context():
            session_info = SessionInfo.get(SessionInfo.id == session_id)
            session_info.end = datetime.now()
            session_info.save()

    def add_session(self, app_id, app_version, args, profile_status, followers_count, following_count, start, end):
        """
        For migration only!
        """
        with db.connection_context():
            profile_info = InstagramProfileInfo.create(profile=self,
                                                       status=profile_status,
                                                       followers=followers_count,
                                                       following=following_count)

            SessionInfo.create(app_id=app_id,
                               app_version=app_version,
                               args=args,
                               profile_info=profile_info,
                               start=start,
                               end=end)

    def update_profile_info(self, profile_status, followers_count, following_count):
        """
        Create a new InstagramProfileInfo record

        Can't see any usage for that right now, maybe we will use it later just in order to update profile info without
        running an insomniac-session.
        """
        with db.connection_context():
            InstagramProfileInfo.create(profile=self,
                                        status=profile_status,
                                        followers=followers_count,
                                        following=following_count)

    def log_get_profile_action(self, session_id, phase, username, task_id='', execution_id='', timestamp=None):
        """
        Create InsomniacAction record
        Create GetProfileAction record
        """
        with db.connection_context():
            session = SessionInfo.get(SessionInfo.id == session_id)
            action = InsomniacAction.create(actor_profile=self,
                                            type=GetProfileAction.__name__,
                                            task_id=task_id,
                                            execution_id=execution_id,
                                            session=session,
                                            phase=phase,
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            GetProfileAction.create(action=action,
                                    target_user=username)

    def log_like_action(self, session_id, phase, username, source_type, source_name, task_id='', execution_id='', timestamp=None):
        """
        Create InsomniacAction record
        Create LikeAction record
        Create InsomniacActionSource record
        """
        with db.connection_context():
            session = SessionInfo.get(SessionInfo.id == session_id)
            action = InsomniacAction.create(actor_profile=self,
                                            type=LikeAction.__name__,
                                            task_id=task_id,
                                            execution_id=execution_id,
                                            session=session,
                                            phase=phase,
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            LikeAction.create(action=action,
                              target_user=username)
            if source_type is not None and source_name is not None:
                InsomniacActionSource.create(action=action,
                                             type=source_type,
                                             name=source_name)

    def log_follow_action(self, session_id, phase, username, source_type, source_name, task_id='', execution_id='', timestamp=None):
        """
        Create InsomniacAction record
        Create FollowAction record
        Create InsomniacActionSource record
        """
        with db.connection_context():
            session = SessionInfo.get(SessionInfo.id == session_id)
            action = InsomniacAction.create(actor_profile=self,
                                            type=FollowAction.__name__,
                                            task_id=task_id,
                                            execution_id=execution_id,
                                            session=session,
                                            phase=phase,
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            FollowAction.create(action=action,
                                target_user=username)
            if source_type is not None and source_name is not None:
                InsomniacActionSource.create(action=action,
                                             type=source_type,
                                             name=source_name)

    def log_story_watch_action(self, session_id, phase, username, source_type, source_name, task_id='', execution_id='', timestamp=None):
        """
        Create InsomniacAction record
        Create StoryWatchAction record
        Create InsomniacActionSource record
        """
        with db.connection_context():
            session = SessionInfo.get(SessionInfo.id == session_id)
            action = InsomniacAction.create(actor_profile=self,
                                            type=StoryWatchAction.__name__,
                                            task_id=task_id,
                                            execution_id=execution_id,
                                            session=session,
                                            phase=phase,
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            StoryWatchAction.create(action=action,
                                    target_user=username)
            if source_type is not None and source_name is not None:
                InsomniacActionSource.create(action=action,
                                             type=source_type,
                                             name=source_name)

    def log_comment_action(self, session_id, phase, username, comment, source_type, source_name, task_id='', execution_id='', timestamp=None):
        """
        Create InsomniacAction record
        Create CommentAction record
        Create InsomniacActionSource record
        """
        with db.connection_context():
            session = SessionInfo.get(SessionInfo.id == session_id)
            action = InsomniacAction.create(actor_profile=self,
                                            type=CommentAction.__name__,
                                            task_id=task_id,
                                            execution_id=execution_id,
                                            session=session,
                                            phase=phase,
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            CommentAction.create(action=action,
                                 target_user=username,
                                 comment=comment)
            if source_type is not None and source_name is not None:
                InsomniacActionSource.create(action=action,
                                             type=source_type,
                                             name=source_name)

    def log_direct_message_action(self, session_id, phase, username, message, task_id='', execution_id='', timestamp=None):
        """
        Create InsomniacAction record
        Create DirectMessageAction record
        """
        with db.connection_context():
            session = SessionInfo.get(SessionInfo.id == session_id)
            action = InsomniacAction.create(actor_profile=self,
                                            type=DirectMessageAction.__name__,
                                            task_id=task_id,
                                            execution_id=execution_id,
                                            session=session,
                                            phase=phase,
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            DirectMessageAction.create(action=action,
                                       target_user=username,
                                       message=message)

    def log_unfollow_action(self, session_id, phase, username, task_id='', execution_id='', timestamp=None):
        """
        Create InsomniacAction record
        Create UnfollowAction record
        """
        with db.connection_context():
            session = SessionInfo.get(SessionInfo.id == session_id)
            action = InsomniacAction.create(actor_profile=self,
                                            type=UnfollowAction.__name__,
                                            task_id=task_id,
                                            execution_id=execution_id,
                                            session=session,
                                            phase=phase,
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            UnfollowAction.create(action=action,
                                  target_user=username)

    def log_scrape_action(self, session_id, phase, username, source_type, source_name, task_id='', execution_id='', timestamp=None):
        """
        Create InsomniacAction record
        Create ScrapeAction record
        Create InsomniacActionSource record
        """
        with db.connection_context():
            session = SessionInfo.get(SessionInfo.id == session_id)
            action = InsomniacAction.create(actor_profile=self,
                                            type=ScrapeAction.__name__,
                                            task_id=task_id,
                                            execution_id=execution_id,
                                            session=session,
                                            phase=phase,
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            ScrapeAction.create(action=action,
                                target_user=username)
            if source_type is not None and source_name is not None:
                InsomniacActionSource.create(action=action,
                                             type=(source_type if source_type is not None else None),
                                             name=source_name)

    def log_filter_action(self, session_id, phase, username, task_id='', execution_id='', timestamp=None):
        """
        Create InsomniacAction record
        Create FilterAction record
        """
        with db.connection_context():
            session = SessionInfo.get(SessionInfo.id == session_id)
            action = InsomniacAction.create(actor_profile=self,
                                            type=FilterAction.__name__,
                                            task_id=task_id,
                                            execution_id=execution_id,
                                            session=session,
                                            phase=phase,
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            FilterAction.create(action=action,
                                target_user=username)

    def log_change_profile_info_action(self, session_id, phase, profile_pic_url, name, description, task_id='', execution_id='', timestamp=None):
        """
        Create InsomniacAction record
        Create ChangeProfileInfoAction record
        """
        with db.connection_context():
            session = SessionInfo.get(SessionInfo.id == session_id)
            action = InsomniacAction.create(actor_profile=self,
                                            type=ChangeProfileInfoAction.__name__,
                                            task_id=task_id,
                                            execution_id=execution_id,
                                            session=session,
                                            phase=phase,
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            ChangeProfileInfoAction.create(action=action,
                                           profile_pic_url=profile_pic_url,
                                           name=name,
                                           description=description)

    def publish_scrapped_account(self, username, scrape_for_account_list):
        """
        Use this function when you are a scrapper and you have found a profile according to filters.
        Create ScrappedProfile record for each target-real-bot-profile
        """
        with db.connection_context():
            for target_actor_username in scrape_for_account_list:
                target_actor_profile, created = InstagramProfile.get_or_create(name=target_actor_username)
                if ScrappedProfile.get_or_none(target_actor_profile=target_actor_profile, name=username) is None:
                    ScrappedProfile.create(target_actor_profile=target_actor_profile, name=username)

    def update_follow_status(self, username, is_follow_me, do_i_follow_him):
        """
        Create or update FollowStatus record
        """
        with db.connection_context():
            FollowStatus.create(actor_profile=self,
                                profile=username,
                                is_follow_me=is_follow_me,
                                do_i_follow_him=do_i_follow_him)

    def _get_follow_status(self, username, hours=None):
        with db.connection_context():
            follow_statuses = FollowStatus.select() \
                .where((FollowStatus.profile == username)
                       & (FollowStatus.actor_profile == self)
                       & ((datetime.now().timestamp() - FollowStatus.updated_at <= timedelta(hours=hours).total_seconds()) if hours is not None else True)) \
                .order_by(FollowStatus.updated_at.desc()) \
                .limit(1)
            return follow_statuses[0] if len(follow_statuses) > 0 else None

    def is_follow_me(self, username, hours=None):
        follow_status = self._get_follow_status(username, hours)
        return follow_status.is_follow_me if follow_status is not None else None

    def is_dm_sent_to(self, username):
        with db.connection_context():
            if len(DirectMessageAction.select()
                   .join(InsomniacAction, join_type=JOIN.LEFT_OUTER)
                   .where((DirectMessageAction.target_user == username)
                          & (InsomniacAction.actor_profile == self))
                   .limit(1)) > 0:
                return True
        return False

    def do_i_follow(self, username, hours=None):
        follow_status = self._get_follow_status(username, hours)
        return follow_status.do_i_follow_him if follow_status is not None else None

    def used_to_follow(self, username):
        """
        Whether I used to follow this username or am following right now.
        """
        with db.connection_context():
            return len(FollowAction.select()
                       .join(InsomniacAction, join_type=JOIN.LEFT_OUTER)
                       .where((FollowAction.target_user == username)
                              & (InsomniacAction.actor_profile == self))
                       .limit(1)) > 0

    def is_interacted(self, username, hours=None) -> bool:
        with db.connection_context():
            if len(GetProfileAction.select(GetProfileAction.target_user)
                    .join(InsomniacAction, join_type=JOIN.LEFT_OUTER)
                    .where((GetProfileAction.target_user == username)
                           & (InsomniacAction.actor_profile == self)
                           & ((datetime.now().timestamp() - InsomniacAction.timestamp <= timedelta(hours=hours).total_seconds()) if hours is not None else True))
                    .limit(1)) > 0:
                return True

            if len(LikeAction.select(LikeAction.target_user)
                    .join(InsomniacAction, join_type=JOIN.LEFT_OUTER)
                    .where((LikeAction.target_user == username)
                           & (InsomniacAction.actor_profile == self)
                           & ((datetime.now().timestamp() - InsomniacAction.timestamp <= timedelta(hours=hours).total_seconds()) if hours is not None else True))
                    .limit(1)) > 0:
                return True

            if len(CommentAction.select(CommentAction.target_user)
                    .join(InsomniacAction, join_type=JOIN.LEFT_OUTER)
                    .where((CommentAction.target_user == username)
                           & (InsomniacAction.actor_profile == self)
                           & ((datetime.now().timestamp() - InsomniacAction.timestamp <= timedelta(hours=hours).total_seconds()) if hours is not None else True))
                    .limit(1)) > 0:
                return True
        return False

    def is_filtered(self, username, hours=None) -> bool:
        with db.connection_context():
            if len(FilterAction.select(FilterAction.target_user)
                    .join(InsomniacAction, join_type=JOIN.LEFT_OUTER)
                    .where((FilterAction.target_user == username)
                           & (InsomniacAction.actor_profile == self)
                           & ((datetime.now().timestamp() - InsomniacAction.timestamp <= timedelta(hours=hours).total_seconds()) if hours is not None else True))
                    .limit(1)) > 0:
                return True
        return False

    def is_scrapped(self, username, scrape_for_account_list) -> bool:
        """
        Return True if "username" is scrapped for ALL accounts from "scrape_for_account_list", False otherwise.
        """
        with db.connection_context():
            for target_actor_profile in scrape_for_account_list:
                if len(ScrappedProfile.select()
                       .where(ScrappedProfile.name == username)
                       .join(InstagramProfile, join_type=JOIN.LEFT_OUTER)
                       .where(InstagramProfile.name == target_actor_profile)
                       .limit(1)) == 0:
                    return False
            return True

    def count_scrapped_profiles_for_interaction(self):
        with db.connection_context():
            return len(self._get_scrapped_profiles_query())

    def get_scrapped_profile_for_interaction(self) -> Optional[str]:
        """
        Use this function when you are interacting with targets, and you are looking for the next scrapped target
        """
        with db.connection_context():
            scrapped_profiles = self._get_scrapped_profiles_query() \
                .order_by(ScrappedProfile.timestamp.desc()) \
                .limit(1)
            return scrapped_profiles[0].name if len(scrapped_profiles) > 0 else None

    def get_actions_count_within_hours(self, action_type, hours) -> int:
        """
        Returns the amount of actions by 'action_type', within the last 'hours'
        """
        with db.connection_context():
            return get_actions_count_within_hours(action_type, hours, profile=self)

    def get_session_time_in_seconds_within_minutes(self, minutes) -> int:
        """
        Returns the amount of active-session-seconds, within the last 'minutes'
        """
        with db.connection_context():
            return get_session_time_in_seconds_within_minutes_for_profile(minutes, profile=self)

    def get_session_count_within_hours(self, hours) -> int:
        """
        Returns the amount of sessions, within the last 'hours'
        """
        with db.connection_context():
            return get_session_count_within_hours_for_profile(hours, profile=self)

    def _get_scrapped_profiles_query(self):
        def get_profiles_reached_by_action(action):
            return (action
                    .select(action.target_user)
                    .join(InsomniacAction)
                    .where(InsomniacAction.actor_profile == self))

        profiles_reached_by_get_profile = get_profiles_reached_by_action(GetProfileAction)
        profiles_reached_by_like = get_profiles_reached_by_action(LikeAction)
        profiles_reached_by_follow = get_profiles_reached_by_action(FollowAction)
        profiles_reached_by_story_watch = get_profiles_reached_by_action(StoryWatchAction)
        profiles_reached_by_comment = get_profiles_reached_by_action(CommentAction)
        profiles_reached_by_filter = get_profiles_reached_by_action(FilterAction)

        return (ScrappedProfile.select(ScrappedProfile.name)
                .where(ScrappedProfile.target_actor_profile == self)
                .join(profiles_reached_by_get_profile, join_type=JOIN.LEFT_OUTER, on=(ScrappedProfile.name == profiles_reached_by_get_profile.c.target_user))
                .switch(ScrappedProfile)
                .join(profiles_reached_by_like, join_type=JOIN.LEFT_OUTER, on=(ScrappedProfile.name == profiles_reached_by_like.c.target_user))
                .switch(ScrappedProfile)
                .join(profiles_reached_by_follow, join_type=JOIN.LEFT_OUTER, on=(ScrappedProfile.name == profiles_reached_by_follow.c.target_user))
                .switch(ScrappedProfile)
                .join(profiles_reached_by_story_watch, join_type=JOIN.LEFT_OUTER, on=(ScrappedProfile.name == profiles_reached_by_story_watch.c.target_user))
                .switch(ScrappedProfile)
                .join(profiles_reached_by_comment, join_type=JOIN.LEFT_OUTER, on=(ScrappedProfile.name == profiles_reached_by_comment.c.target_user))
                .switch(ScrappedProfile)
                .join(profiles_reached_by_filter, join_type=JOIN.LEFT_OUTER, on=(ScrappedProfile.name == profiles_reached_by_filter.c.target_user))
                .where(
                    profiles_reached_by_get_profile.c.target_user.is_null()
                    & profiles_reached_by_like.c.target_user.is_null()
                    & profiles_reached_by_follow.c.target_user.is_null()
                    & profiles_reached_by_story_watch.c.target_user.is_null()
                    & profiles_reached_by_comment.c.target_user.is_null()
                    & profiles_reached_by_filter.c.target_user.is_null()
                ))


class InstagramProfileInfo(InsomniacModel):
    profile = ForeignKeyField(InstagramProfile, backref='profile_info_records')
    status = TextField()
    followers = BigIntegerField(null=True)
    following = BigIntegerField(null=True)
    timestamp = TimestampField(default=datetime.now)

    class Meta:
        db_table = 'instagram_profiles_info'


class SessionInfo(InsomniacModel):
    app_id = TextField(null=True)
    app_version = TextField(null=True)
    start = TimestampField(default=datetime.now)
    end = TimestampField(null=True)
    args = TextField()
    profile_info = ForeignKeyField(InstagramProfileInfo, backref='session_info')

    class Meta:
        db_table = 'sessions_info'


class InsomniacAction(InsomniacModel):
    actor_profile = ForeignKeyField(InstagramProfile, backref='actions')
    type = TextField()
    timestamp = TimestampField(default=datetime.now)
    task_id = UUIDField()
    execution_id = UUIDField()
    session = ForeignKeyField(SessionInfo, backref='session_actions')
    phase = TextField(default='task')

    class Meta:
        db_table = 'actions_log'


class InsomniacActionSource(InsomniacModel):
    action = ForeignKeyField(InsomniacAction, backref='action_source')
    type = TextField()
    name = TextField()

    class Meta:
        db_table = 'actions_sources'


class GetProfileAction(InsomniacModel):
    action = ForeignKeyField(InsomniacAction, backref='get_profile_action_info')
    target_user = TextField()

    class Meta:
        db_table = 'get_profile_actions'


class LikeAction(InsomniacModel):
    action = ForeignKeyField(InsomniacAction, backref='like_action_info')
    target_user = TextField()

    class Meta:
        db_table = 'like_actions'


class FollowAction(InsomniacModel):
    action = ForeignKeyField(InsomniacAction, backref='follow_action_info')
    target_user = TextField()

    class Meta:
        db_table = 'follow_actions'


class StoryWatchAction(InsomniacModel):
    action = ForeignKeyField(InsomniacAction, backref='story_watch_action_info')
    target_user = TextField()

    class Meta:
        db_table = 'story_watch_actions'


class CommentAction(InsomniacModel):
    action = ForeignKeyField(InsomniacAction, backref='comment_action_info')
    target_user = TextField()
    comment = TextField()

    class Meta:
        db_table = 'comment_actions'


class DirectMessageAction(InsomniacModel):
    action = ForeignKeyField(InsomniacAction, backref='direct_message_action_info')
    target_user = TextField()
    message = TextField()

    class Meta:
        db_table = 'direct_message_actions'


class UnfollowAction(InsomniacModel):
    action = ForeignKeyField(InsomniacAction, backref='unfollow_action_info')
    target_user = TextField()

    class Meta:
        db_table = 'unfollow_actions'


class ScrapeAction(InsomniacModel):
    action = ForeignKeyField(InsomniacAction, backref='scrape_action_info')
    target_user = TextField()

    class Meta:
        db_table = 'scrape_actions'


class FilterAction(InsomniacModel):
    action = ForeignKeyField(InsomniacAction, backref='filter_action_info')
    target_user = TextField()

    class Meta:
        db_table = 'filter_actions'


class ChangeProfileInfoAction(InsomniacModel):
    action = ForeignKeyField(InsomniacAction, backref='change_profile_info_action_info')
    profile_pic_url = TextField()
    name = TextField()
    description = TextField()

    class Meta:
        db_table = 'change_profile_info_actions'


class ScrappedProfile(InsomniacModel):
    # "target actor" is a profile which will actually do the interaction with the target
    target_actor_profile = ForeignKeyField(InstagramProfile, backref='scrapped_profiles')
    name = TextField()
    timestamp = TimestampField(default=datetime.now)

    class Meta:
        db_table = 'scrapped_profiles'


class FollowStatus(InsomniacModel):
    # "actor" is a profile that actually did the interaction and now updates he database
    actor_profile = ForeignKeyField(InstagramProfile)
    profile = TextField()
    is_follow_me = BooleanField(null=True, default=None)
    do_i_follow_him = BooleanField(null=True, default=None)
    updated_at = TimestampField(default=datetime.now)

    class Meta:
        db_table = 'follow_status'


class SchemaVersion(InsomniacModel):
    version = SmallIntegerField(default=DATABASE_VERSION)
    updated_at = TimestampField(default=datetime.now)

    class Meta:
        db_table = 'schema_version'


MODELS = [
    SchemaVersion,
    InstagramProfile,
    InstagramProfileInfo,
    SessionInfo,
    InsomniacAction,
    InsomniacActionSource,
    GetProfileAction,
    LikeAction,
    FollowAction,
    StoryWatchAction,
    CommentAction,
    DirectMessageAction,
    UnfollowAction,
    ScrapeAction,
    FilterAction,
    ChangeProfileInfoAction,
    ScrappedProfile,
    FollowStatus
]


def init():
    """
    Initialize database.
    """
    with db.connection_context():
        if len(db.get_tables()) == 0:
            print(f"Creating tables in {DATABASE_NAME}...")
            db.create_tables(MODELS)
            SchemaVersion.create()
            return

        # Migration logic
        current_db_version = _get_db_version()
        if current_db_version is None:
            print(COLOR_FAIL + "Cannot read database version from SchemaVersion table!" + COLOR_ENDC)
            return

        if current_db_version > DATABASE_VERSION:
            raise Exception("Bot version is too low, cannot work with the current database! "
                            "Please update the bot or delete the database!")

        if current_db_version < DATABASE_VERSION:
            print(f"[Database] Going to migrate database to a newer version...")
            while current_db_version < DATABASE_VERSION:
                migrator = SqliteMigrator(db)
                _migrate(current_db_version, migrator)
                current_db_version = _get_db_version()


def get_ig_profile_by_profile_name(profile_name) -> InstagramProfile:
    with db.connection_context():
        profile, is_created = InstagramProfile.get_or_create(name=profile_name)
    return profile


def get_ig_profiles_by_profiles_names(profiles_names) -> dict:
    profiles_names_to_objects = {}

    with db.connection_context():
        for name in profiles_names:
            profile_obj, _ = InstagramProfile.get_or_create(name=name)
            profiles_names_to_objects[name] = profile_obj
    return profiles_names_to_objects


def is_ig_profile_exists(profile_name) -> bool:
    with db.connection_context():
        is_exists = InstagramProfile.select().where(InstagramProfile.name == profile_name).exists()
    return is_exists


def get_session_time_in_seconds_within_minutes_for_profile(minutes=None, profile=None) -> int:
    """Returns the amount of session time in seconds per profile, on the last 'minutes' for 'profiles'"""

    total_session_time_by_profile_name = get_session_time_in_seconds_within_minutes(minutes, [profile] if profile is not None else None)

    session_time_secs = sum(total_session_time_by_profile_name.values())

    return session_time_secs


def get_session_time_in_seconds_within_minutes(minutes=None, profiles=None) -> dict:
    """Returns the amount of session time in seconds per profile, on the last 'minutes' for 'profiles'"""

    timestamp_from, timestamp_to = None, None
    if minutes is not None:
        timestamp_from, timestamp_to = get_from_to_timestamps_by_minutes(minutes)

    return get_session_time_in_seconds_from_to(timestamp_from, timestamp_to, profiles)


def get_session_time_in_seconds_from_to(timestamp_from=None, timestamp_to=None, profiles=None) -> dict:
    """Returns the amount of session time in seconds per profile, from 'timestamp_from' to 'timestamp_to' for 'profiles'"""

    # Taking every session that started during the specified time
    profiles_sessions = InstagramProfile.select(InstagramProfile.name, SessionInfo.start.alias('start'), SessionInfo.end.alias('end')) \
                                        .join(InstagramProfileInfo, join_type=JOIN.LEFT_OUTER) \
                                        .where(InstagramProfileInfo.profile.in_(profiles) if profiles else True) \
                                        .join(SessionInfo, join_type=JOIN.LEFT_OUTER) \
                                        .where((SessionInfo.start >= timestamp_from if timestamp_from else True) &
                                               (SessionInfo.start <= timestamp_to if timestamp_to else True))

    total_session_time_by_profile_name = defaultdict(int)

    for session in profiles_sessions.dicts():
        if not session['start'] or not session['end']:
            # Not counting sessions that stopped without a end_session function call
            continue

        session_time = session['end'] - session['start']

        total_session_time_by_profile_name[session['name']] += session_time.total_seconds()

    return total_session_time_by_profile_name


def get_session_count_within_hours_for_profile(hours=None, profile=None) -> int:
    """Returns the amount of session time in seconds per profile, on the last 'minutes' for 'profiles'"""

    session_count_by_profile_name = get_session_count_within_hours(hours, [profile] if profile is not None else None)

    session_count = sum(session_count_by_profile_name.values())

    return session_count


def get_session_count_within_hours(hours=None, profiles=None) -> dict:
    """
    Returns the amount of session, within the last 'hours' for 'profiles'
    """
    timestamp_from, timestamp_to = None, None
    if hours is not None:
        timestamp_from, timestamp_to = get_from_to_timestamps_by_hours(hours)

    return get_session_count_from_to(timestamp_from, timestamp_to, profiles)


def get_session_count_from_to(timestamp_from=None, timestamp_to=None, profiles=None) -> dict:
    """
    Returns the amount of session, from 'timestamp_from' to 'timestamp_to' for 'profiles'
    """
    # Taking every session that started during the specified time
    profiles_sessions = InstagramProfile.select(InstagramProfile.name) \
                                        .join(InstagramProfileInfo, join_type=JOIN.LEFT_OUTER) \
                                        .where(InstagramProfileInfo.profile.in_(profiles) if profiles else True) \
                                        .join(SessionInfo, join_type=JOIN.LEFT_OUTER) \
                                        .where((SessionInfo.start >= timestamp_from if timestamp_from else True) &
                                               (SessionInfo.start <= timestamp_to if timestamp_to else True))

    total_session_count_by_profile_name = defaultdict(int)

    for session in profiles_sessions.dicts():
        total_session_count_by_profile_name[session['name']] += 1

    return total_session_count_by_profile_name


def get_actions_count_within_hours(action_type=None, hours=None, profile=None, task_id=None) -> int:
    """
    Returns the amount of actions by 'action_type', within the last 'hours'
    """
    actions_count = 0
    actions_per_profile = get_actions_count_within_hours_for_profiles(action_types=[action_type] if action_type else None,
                                                                      hours=hours if hours else None,
                                                                      profiles=[profile] if profile else None,
                                                                      task_ids=[task_id] if task_id else None)

    for actions in actions_per_profile.values():
        for count in actions.values():
            actions_count += count

    return actions_count


def get_actions_count_within_hours_for_profiles(action_types=None, hours=None,
                                                profiles=None, task_ids=None, session_phases=None) -> dict:
    timestamp_from, timestamp_to = None, None
    if hours is not None:
        timestamp_from, timestamp_to = get_from_to_timestamps_by_hours(hours)

    return get_actions_count_for_profiles(action_types=action_types,
                                          timestamp_from=timestamp_from,
                                          timestamp_to=timestamp_to,
                                          profiles=profiles,
                                          task_ids=task_ids,
                                          session_phases=session_phases)


def get_actions_count_for_profiles(action_types=None, timestamp_from=None, timestamp_to=None,
                                   profiles=None, task_ids=None, session_phases=None) -> dict:
    """
    Returns the amount of actions by 'action_type', within the last 'hours', that been done by 'profiles'
    """
    action_types_names = [at.__name__ for at in action_types] if action_types else None
    session_phases_values = [sp.value for sp in session_phases] if session_phases else None

    profiles_actions = defaultdict(dict)

    query = InsomniacAction.select(InsomniacAction.actor_profile, InsomniacAction.type, fn.COUNT(InsomniacAction.id).alias('ct'))\
                           .where((InsomniacAction.actor_profile.in_(profiles) if profiles else True) &
                                  (InsomniacAction.task_id.in_(task_ids) if task_ids else True) &
                                  (InsomniacAction.phase.in_(session_phases_values) if session_phases_values else True) &
                                  (InsomniacAction.type.in_(action_types_names) if action_types_names else True) &
                                  (InsomniacAction.timestamp >= timestamp_from if timestamp_from else True) &
                                  (InsomniacAction.timestamp <= timestamp_to if timestamp_to else True))\
                           .group_by(InsomniacAction.actor_profile, InsomniacAction.type)

    for obj in query:
        profiles_actions[obj.actor_profile.name][obj.type] = obj.ct

    return profiles_actions


def _get_db_version() -> Optional[int]:
    versions = SchemaVersion.select() \
        .order_by(SchemaVersion.updated_at.desc()) \
        .limit(1)
    return versions[0].version if len(versions) > 0 else None


def _migrate_db_from_version_1_to_2(migrator):
    """
    Changes added on DB version 2:

        * Made InstagramProfileInfo.followers nullable
        * Made InstagramProfileInfo.followings nullable
        * Made SessionInfo.app_info nullable
    """
    migrate(
        migrator.drop_not_null('instagram_profiles_info', 'followers'),
        migrator.drop_not_null('instagram_profiles_info', 'following'),
        migrator.drop_not_null('sessions_info', 'app_version')
    )


def _migrate_db_from_version_2_to_3(migrator):
    """
    Changes added on DB version 3:

        * Added InsomniacAction.phase field
    """
    migrate(
        migrator.add_column('actions_log', 'phase', TextField(default='task')),
    )


def _migrate(curr_version, migrator):
    print(f"[Database] Going to run database migration from version {curr_version} to {curr_version+1}")
    migration_method = database_migrations[f"{curr_version}->{curr_version + 1}"]
    with db.atomic():
        migration_method(migrator)
    print(f"[Database] database migration from version {curr_version} to {curr_version+1} has been done successfully")
    print(f"[Database] Updating database version to be {curr_version + 1}")
    SchemaVersion.create(version=curr_version+1)


database_migrations = {
    "1->2": _migrate_db_from_version_1_to_2,
    "2->3": _migrate_db_from_version_2_to_3
}
