from abc import ABC

from insomniac.actions_types import LikeAction, InteractAction, FollowAction, GetProfileAction, ScrapeAction, \
    UnfollowAction, RemoveMassFollowerAction, StoryWatchAction, CommentAction, DirectMessageAction, FilterAction, \
    DirectMessageBackdateAction
from insomniac.storage import Storage, InsomniacStorage, SessionPhase
from insomniac.utils import *


class SessionState(ABC):
    id = None
    args = {}
    startTime = None
    finishTime = None
    storage: Optional[Storage] = None

    def __init__(self):
        self.id = None
        self.args = {}
        self.startTime = None
        self.finishTime = None
        self.storage = None

    def set_storage_layer(self, storage_instance):
        self.storage = storage_instance

    def start_session(self):
        self.startTime = datetime.now()
        self.start_session_impl()
        print_timeless(COLOR_REPORT + "\n-------- START: " + str(self.startTime) + " --------" + COLOR_ENDC)

    def start_session_impl(self):
        raise NotImplementedError

    def end_session(self):
        if not self.is_started():
            return

        self.finishTime = datetime.now()  # For metadata-in-memory only
        if self.storage is not None:
            self.storage.end_session(self.id)

        print_timeless(COLOR_REPORT + "-------- FINISH: " + str(self.finishTime) + " --------" + COLOR_ENDC)

    def is_started(self):
        return self.startTime is not None

    def is_finished(self):
        return self.finishTime is not None


class InsomniacSessionState(SessionState):
    SOURCE_NAME_TARGETS = "targets"

    storage: Optional[InsomniacStorage] = None
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
    session_phase = SessionPhase.TASK_LOGIC

    def __init__(self):
        super().__init__()
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
        self.session_phase = SessionPhase.TASK_LOGIC

    def start_session_impl(self):
        session_id = self.storage.start_session(self.args, self.app_id, self.app_version,
                                                self.my_followers_count, self.my_following_count)
        if session_id is not None:
            self.id = session_id

    def start_warmap(self):
        self.session_phase = SessionPhase.WARMUP

    def end_warmap(self):
        self.session_phase = SessionPhase.TASK_LOGIC

    def add_action(self, action):
        if type(action) == GetProfileAction:
            self.totalGetProfile += 1
            self.storage.log_get_profile_action(self.id, self.session_phase, action.user)

        if type(action) == LikeAction:
            self.totalLikes += 1
            self.storage.log_like_action(self.id, self.session_phase, action.user, action.source_type, action.source_name)

        if type(action) == FollowAction:
            source_name = action.source_name if action.source_type is not None else self.SOURCE_NAME_TARGETS
            if self.totalFollowed.get(source_name) is None:
                self.totalFollowed[source_name] = 1
            else:
                self.totalFollowed[source_name] += 1

            self.storage.log_follow_action(self.id, self.session_phase, action.user, action.source_type, action.source_name)
            self.storage.update_follow_status(action.user, do_i_follow_him=True)

        if type(action) == StoryWatchAction:
            self.totalStoriesWatched += 1
            self.storage.log_story_watch_action(self.id, self.session_phase, action.user, action.source_type, action.source_name)

        if type(action) == CommentAction:
            self.totalComments += 1
            self.storage.log_comment_action(self.id, self.session_phase, action.user, action.comment, action.source_type, action.source_name)

        if type(action) == DirectMessageAction:
            self.totalDirectMessages += 1
            self.storage.log_direct_message_action(self.id, self.session_phase, action.user, action.message)

        if type(action) == DirectMessageBackdateAction:
            old_time_ago = datetime(2000, 1, 1, 0, 0, 0)
            self.storage.log_direct_message_action(self.id, self.session_phase, action.user, action.message, old_time_ago)

        if type(action) == UnfollowAction:
            self.totalUnfollowed += 1
            self.storage.log_unfollow_action(self.id, self.session_phase, action.user)
            self.storage.update_follow_status(action.user, do_i_follow_him=False)

        if type(action) == ScrapeAction:
            if self.totalScraped.get(action.source_name) is None:
                self.totalScraped[action.source_name] = 1
            else:
                self.totalScraped[action.source_name] += 1

            self.storage.log_scrape_action(self.id, self.session_phase, action.user, action.source_type, action.source_name)
            self.storage.publish_scrapped_account(action.user)

        if type(action) == FilterAction:
            self.storage.log_filter_action(self.id, self.session_phase, action.user)

        if type(action) == InteractAction:
            source_name = action.source_name if action.source_type is not None else self.SOURCE_NAME_TARGETS
            if self.totalInteractions.get(source_name) is None:
                self.totalInteractions[source_name] = 1
            else:
                self.totalInteractions[source_name] += 1

            if self.successfulInteractions.get(source_name) is None:
                self.successfulInteractions[source_name] = 1 if action.succeed else 0
            else:
                if action.succeed:
                    self.successfulInteractions[source_name] += 1

        if type(action) == RemoveMassFollowerAction:
            self.removedMassFollowers.append(action.user)
