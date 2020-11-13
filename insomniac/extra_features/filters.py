from collections import defaultdict

from insomniac.actions_impl import is_private_account
from insomniac.extra_features.filters_impl import _has_business_category, \
    _get_posts_count, _get_followers, _get_followings
from insomniac.utils import *

FILENAME_CONDITIONS = "filter.json"


class FiltersManager(object):
    """This class manages the profiles-filters of an insomniac-session"""

    FILTERS_ARGS = {
        "filters": {
            "help": 'add this argument if you want to pass filters as an argument and not from '
                    'filters.txt file'
        }
    }

    filters = {}
    filters_by_tags = defaultdict(list)

    def __init__(self):
        for clazz in get_filters_classes():
            instance = clazz()
            self.filters[instance.FILTER_ID] = instance

            for tag in instance.FILTER_TAGS:
                self.filters_by_tags[tag].append(instance)

    def get_filters_args(self):
        return self.FILTERS_ARGS

    def set_filters(self, args):
        filters = {}

        if args.filters:
            filters = args.filters
        elif os.path.exists(FILENAME_CONDITIONS):
            with open(FILENAME_CONDITIONS, encoding="utf-8") as json_file:
                filters = json.load(json_file)

        for filter_key, value in filters.items():
            self.filters[filter_key].set_filter(value)

    def check_filters(self, device, username, filters_tags=None):
        if filters_tags is not None:
            for tag in filters_tags:
                for profile_filter in self.filters_by_tags[tag]:
                    if not profile_filter.check_filter(device, username):
                        return False
        else:
            for filter_key, profile_filter in self.filters.items():
                if not profile_filter.check_filter(device, username):
                    return False

        return True


class Filter(object):
    """An interface for filter object"""

    FILTER_ID = "OVERRIDE"
    FILTER_TAGS = []

    def set_filter(self, val):
        raise NotImplementedError()

    def check_filter(self, device, username):
        raise NotImplementedError()


class SkipBusinessFilter(Filter):
    FILTER_ID = "skip_business"
    FILTER_TAGS = []

    def __init__(self):
        self.should_skip_business = None

    def set_filter(self, val):
        self.should_skip_business = val

    def check_filter(self, device, username):
        if self.should_skip_business is None:
            return True

        has_business_category = _has_business_category(device)
        if self.should_skip_business and has_business_category:
            print(COLOR_OKGREEN + "@" + username + " has business account, skip." + COLOR_ENDC)
            return False

        return True


class SkipNonBusinessFilter(Filter):
    FILTER_ID = "skip_non_business"
    FILTER_TAGS = []

    def __init__(self):
        self.should_skip_non_business = None

    def set_filter(self, val):
        self.should_skip_non_business = val

    def check_filter(self, device, username):
        if self.should_skip_non_business is None:
            return True

        has_business_category = _has_business_category(device)
        if self.should_skip_non_business and not has_business_category:
            print(COLOR_OKGREEN + "@" + username + " has non business account, skip." + COLOR_ENDC)
            return False

        return True


class MinFollowersFilter(Filter):
    FILTER_ID = "min_followers"
    FILTER_TAGS = []

    def __init__(self):
        self.min_followers = None

    def set_filter(self, val):
        self.min_followers = val

    def check_filter(self, device, username):
        if self.min_followers is None:
            return True

        followers = _get_followers(device)
        if followers < self.min_followers:
            print(COLOR_OKGREEN + "@" + username + " has less than " + str(self.min_followers) +
                  " followers, skip." + COLOR_ENDC)
            return False

        return True


class MaxFollowersFilter(Filter):
    FILTER_ID = "max_followers"
    FILTER_TAGS = []

    def __init__(self):
        self.max_followers = None

    def set_filter(self, val):
        self.max_followers = val

    def check_filter(self, device, username):
        if self.max_followers is None:
            return True

        followers = _get_followers(device)
        if followers > self.max_followers:
            print(COLOR_OKGREEN + "@" + username + " has more than " + str(self.max_followers) +
                  " followers, skip." + COLOR_ENDC)
            return False

        return True


class MinFollowingsFilter(Filter):
    FILTER_ID = "min_followings"
    FILTER_TAGS = []

    def __init__(self):
        self.min_followings = None

    def set_filter(self, val):
        self.min_followings = val

    def check_filter(self, device, username):
        if self.min_followings is None:
            return True

        followings = _get_followings(device)
        if followings < self.min_followings:
            print(COLOR_OKGREEN + "@" + username + " has less than " + str(self.min_followings) +
                  " followings, skip." + COLOR_ENDC)
            return False

        return True


class MaxFollowingsFilter(Filter):
    FILTER_ID = "max_followings"
    FILTER_TAGS = []

    def __init__(self):
        self.max_followings = None

    def set_filter(self, val):
        self.max_followings = val

    def check_filter(self, device, username):
        if self.max_followings is None:
            return True

        followings = _get_followings(device)
        if followings > self.max_followings:
            print(COLOR_OKGREEN + "@" + username + " has more than " + str(self.max_followings) +
                  " followings, skip." + COLOR_ENDC)
            return False

        return True


class MinPostsFilter(Filter):
    FILTER_ID = "min_posts"
    FILTER_TAGS = []

    def __init__(self):
        self.min_posts = None

    def set_filter(self, val):
        self.min_posts = val

    def check_filter(self, device, username):
        if self.min_posts is None:
            return True

        posts_count = _get_posts_count(device)
        if posts_count < int(self.min_posts):
            print(COLOR_OKGREEN + "@" + username + " has less than " + str(self.min_posts) +
                  " posts, skip." + COLOR_ENDC)
            return False

        return True


class MinPotencyRatioFilter(Filter):
    FILTER_ID = "min_potency_ratio"
    FILTER_TAGS = []

    def __init__(self):
        self.min_potency_ratio = None

    def set_filter(self, val):
        self.min_potency_ratio = val

    def check_filter(self, device, username):
        if self.min_potency_ratio is None:
            return True

        followers = _get_followers(device)
        followings = _get_followings(device)
        if int(followings) == 0 or followers / followings < float(self.min_potency_ratio):
            print(COLOR_OKGREEN + "@" + username + "'s potency ratio is less than " +
                  str(self.min_potency_ratio) + ", skip." + COLOR_ENDC)
            return False

        return True


class MaxDigitsInProfileNameFilter(Filter):
    FILTER_ID = "max_digits_in_profile_name"
    FILTER_TAGS = ['BEFORE_PROFILE_CLICK']

    def __init__(self):
        self.max_digits_in_profile_name = None

    def set_filter(self, val):
        self.max_digits_in_profile_name = val

    def check_filter(self, device, username):
        if self.max_digits_in_profile_name is None:
            return True

        if get_count_of_nums_in_str(username) > int(self.max_digits_in_profile_name):
            print(COLOR_OKGREEN + "@" + username + " has more than " + str(self.max_digits_in_profile_name) +
                  " digits in profile-name, skip." + COLOR_ENDC)
            return False

        return True


class FollowPrivateOrEmptyFilter(Filter):
    FILTER_ID = "follow_private_or_empty"
    FILTER_TAGS = []

    def __init__(self):
        self.follow_private_or_empty = None

    def set_filter(self, val):
        self.follow_private_or_empty = val

    def check_filter(self, device, username):
        is_private = is_private_account(device)

        if not is_private:
            return True

        if self.follow_private_or_empty is None or not self.follow_private_or_empty:
            print(COLOR_OKGREEN + "@" + username + " is private, skip." + COLOR_ENDC)
            return False

        return True


def get_filters_classes():
    return Filter.__subclasses__()
