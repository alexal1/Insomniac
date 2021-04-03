import uuid
from datetime import timedelta
from enum import Enum, unique
from typing import Optional

from peewee import *

from insomniac.globals import task_id, execution_id
from insomniac.utils import *

DATABASE_NAME = 'insomniac.db'
DATABASE_VERSION = 1

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

    def log_get_profile_action(self, session_id, username, timestamp=None):
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
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            GetProfileAction.create(action=action,
                                    target_user=username)

    def log_like_action(self, session_id, username, source_type, source_name, timestamp=None):
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
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            LikeAction.create(action=action,
                              target_user=username)
            if source_type is not None and source_name is not None:
                InsomniacActionSource.create(action=action,
                                             type=source_type,
                                             name=source_name)

    def log_follow_action(self, session_id, username, source_type, source_name, timestamp=None):
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
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            FollowAction.create(action=action,
                                target_user=username)
            if source_type is not None and source_name is not None:
                InsomniacActionSource.create(action=action,
                                             type=source_type,
                                             name=source_name)

    def log_story_watch_action(self, session_id, username, source_type, source_name, timestamp=None):
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
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            StoryWatchAction.create(action=action,
                                    target_user=username)
            if source_type is not None and source_name is not None:
                InsomniacActionSource.create(action=action,
                                             type=source_type,
                                             name=source_name)

    def log_comment_action(self, session_id, username, comment, source_type, source_name, timestamp=None):
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
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            CommentAction.create(action=action,
                                 target_user=username,
                                 comment=comment)
            if source_type is not None and source_name is not None:
                InsomniacActionSource.create(action=action,
                                             type=source_type,
                                             name=source_name)

    def log_direct_message_action(self, session_id, username, message, timestamp=None):
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
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            DirectMessageAction.create(action=action,
                                       target_user=username,
                                       message=message)

    def log_unfollow_action(self, session_id, username, timestamp=None):
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
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            UnfollowAction.create(action=action,
                                  target_user=username)

    def log_scrape_action(self, session_id, username, source_type, source_name, timestamp=None):
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
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            ScrapeAction.create(action=action,
                                target_user=username)
            if source_type is not None and source_name is not None:
                InsomniacActionSource.create(action=action,
                                             type=(source_type if source_type is not None else None),
                                             name=source_name)

    def log_filter_action(self, session_id, username, timestamp=None):
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
                                            timestamp=(timestamp if timestamp is not None else datetime.now()))
            FilterAction.create(action=action,
                                target_user=username)

    def log_change_profile_info_action(self, session_id, profile_pic_url, name, description, timestamp=None):
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
                .where(
                    profiles_reached_by_get_profile.c.target_user.is_null()
                    & profiles_reached_by_like.c.target_user.is_null()
                    & profiles_reached_by_follow.c.target_user.is_null()
                    & profiles_reached_by_story_watch.c.target_user.is_null()
                    & profiles_reached_by_comment.c.target_user.is_null()
                ))


class InstagramProfileInfo(InsomniacModel):
    profile = ForeignKeyField(InstagramProfile, backref='profile_info_records')
    status = TextField()
    followers = BigIntegerField()
    following = BigIntegerField()
    timestamp = TimestampField(default=datetime.now)

    class Meta:
        db_table = 'instagram_profiles_info'


class SessionInfo(InsomniacModel):
    app_id = TextField(null=True)
    app_version = TextField()
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


@unique
class ProfileStatus(Enum):
    VALID = "valid"
    # TODO: request list of possible statuses from Jey


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


def init() -> bool:
    """
    Initialize database and return whether it was just created.
    """
    with db.connection_context():
        # Migration logic between schema versions can be added here later
        if len(db.get_tables()) == 0:
            print(f"Creating tables in {DATABASE_NAME}...")
            db.create_tables(MODELS)
            SchemaVersion.create()
            return True
    return False


def get_ig_profile_by_profile_name(profile_name) -> InstagramProfile:
    with db.connection_context():
        profile, is_created = InstagramProfile.get_or_create(name=profile_name)
    return profile
