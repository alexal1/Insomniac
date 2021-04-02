import uuid
from datetime import datetime

from insomniac.storage import Storage
from insomniac.actions_types import LikeAction, InteractAction, FollowAction, GetProfileAction, ScrapeAction, \
    UnfollowAction, RemoveMassFollowerAction, StoryWatchAction, CommentAction, DirectMessageAction, FilterAction


class SessionState:
    id = None
    args = {}
    app_id = None
    app_version = None
    my_username = None
    my_followers_count = None
    my_following_count = None
    totalInteractions = {}
    successfulInteractions = {}
    totalFollowed = {}
    totalComments = 0
    totalDirectMessages = 0
    totalLikes = 0
    totalUnfollowed = 0
    totalStoriesWatched = 0
    removedMassFollowers = []
    startTime = None
    finishTime = None
    storage: Storage = None

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.args = {}
        self.app_id = None
        self.app_version = None
        self.my_username = None
        self.my_followers_count = None
        self.my_following_count = None
        self.totalInteractions = {}
        self.successfulInteractions = {}
        self.totalFollowed = {}
        self.totalScraped = {}
        self.totalComments = 0
        self.totalDirectMessages = 0
        self.totalLikes = 0
        self.totalGetProfile = 0
        self.totalUnfollowed = 0
        self.totalStoriesWatched = 0
        self.removedMassFollowers = []
        self.startTime = datetime.now()
        self.finishTime = None
        self.storage = None

    def set_storage_layer(self, storage_instance):
        self.storage = storage_instance
        session_id = self.storage.start_session(self.app_id, self.app_version, self.args,
                                                self.my_followers_count, self.my_following_count)
        if session_id is not None:
            self.id = session_id

    def end_session(self):
        self.finishTime = datetime.now()  # For metadata-in-memory only
        self.storage.end_session(self.id)

    def add_action(self, action):
        if type(action) == GetProfileAction:
            self.totalGetProfile += 1
            self.storage.log_get_profile_action(self.id, action.user)

        if type(action) == LikeAction:
            self.totalLikes += 1
            self.storage.log_like_action(self.id, action.user, action.source_type, action.source_name)

        if type(action) == FollowAction:
            if self.totalFollowed.get(action.source_name) is None:
                self.totalFollowed[action.source_name] = 1
            else:
                self.totalFollowed[action.source_name] += 1

            self.storage.log_follow_action(self.id, action.user, action.source_type, action.source_name)

        if type(action) == StoryWatchAction:
            self.totalStoriesWatched += 1
            self.storage.log_story_watch_action(self.id, action.user, action.source_type, action.source_name)

        if type(action) == CommentAction:
            self.totalComments += 1
            self.storage.log_comment_action(self.id, action.user, action.comment, action.source_type, action.source_name)

        if type(action) == DirectMessageAction:
            self.totalDirectMessages += 1
            self.storage.log_direct_message_action(self.id, action.user, action.message)

        if type(action) == UnfollowAction:
            self.totalUnfollowed += 1
            self.storage.log_unfollow_action(self.id, action.user)

        if type(action) == ScrapeAction:
            if self.totalScraped.get(action.source_name) is None:
                self.totalScraped[action.source_name] = 1
            else:
                self.totalScraped[action.source_name] += 1

            self.storage.log_scrape_action(self.id, action.user, action.source_type, action.source_name)
            self.storage.publish_scrapped_account(action.user)

        if type(action) == FilterAction:
            self.storage.log_filter_action(self.id, action.user)

        if type(action) == InteractAction:
            if self.totalInteractions.get(action.source_name) is None:
                self.totalInteractions[action.source_name] = 1
            else:
                self.totalInteractions[action.source_name] += 1

            if self.successfulInteractions.get(action.source_name) is None:
                self.successfulInteractions[action.source_name] = 1 if action.succeed else 0
            else:
                if action.succeed:
                    self.successfulInteractions[action.source_name] += 1

        if type(action) == RemoveMassFollowerAction:
            self.removedMassFollowers.append(action.user)

    def is_finished(self):
        return self.finishTime is not None
