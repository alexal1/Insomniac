from collections import namedtuple
from enum import unique, Enum

GetProfileAction = namedtuple('GetProfileAction', 'user')
LikeAction = namedtuple('LikeAction', 'source_name source_type user')
FollowAction = namedtuple('FollowAction', 'source_name source_type user')
StoryWatchAction = namedtuple('StoryWatchAction', 'source_name source_type user')
CommentAction = namedtuple('CommentAction', 'source_name source_type user comment')
DirectMessageAction = namedtuple('DirectMessageAction', 'user message')
DirectMessageBackdateAction = namedtuple('DirectMessageAction', 'user message')
UnfollowAction = namedtuple('UnfollowAction', 'user')
ScrapeAction = namedtuple('ScrapeAction', 'source_name source_type user')
FilterAction = namedtuple('FilterAction', 'user')
InteractAction = namedtuple('InteractAction', 'source_name source_type user succeed')
RemoveMassFollowerAction = namedtuple('RemoveMassFollowerAction', 'user')
StartSessionAction = namedtuple('StartSessionAction', '')


@unique
class SourceType(Enum):
    BLOGGER = "blogger"
    HASHTAG = "hashtag"
    PLACE = "place"


@unique
class BloggerInteractionType(Enum):
    FOLLOWERS = 'followers'
    FOLLOWING = 'following'


@unique
class HashtagInteractionType(Enum):
    TOP_LIKERS = 'top-likers'
    RECENT_LIKERS = 'recent-likers'
    RECENT_POSTS = 'recent-posts'
    TOP_POSTS = 'top-posts'


@unique
class PlaceInteractionType(Enum):
    TOP_LIKERS = 'top-likers'
    RECENT_LIKERS = 'recent-likers'
    RECENT_POSTS = 'recent-posts'
    TOP_POSTS = 'top-posts'


@unique
class TargetType(Enum):
    URL = 'url'
    USERNAME = 'username'
