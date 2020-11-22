from collections import defaultdict
from enum import Enum, unique

from insomniac.actions_impl import is_private_account, do_have_story
from insomniac.extra_features.filters_impl import _has_business_category, \
    _get_posts_count, _get_followers, _get_followings, _get_profile_biography, _find_alphabet, _get_fullname
from insomniac.utils import *

FILENAME_CONDITIONS = "filter.json"


class FiltersManager(object):
    """This class manages the profiles-filters of an insomniac-session"""

    FILTERS_ARGS = {
        "filters": {
            "help": 'add this argument if you want to pass filters as an argument and not from '
                    'filters.json file'
        }
    }

    filters = {}
    filters_by_tags = defaultdict(list)

    def __init__(self):
        for clazz in get_filters_classes():
            instance = clazz()
            for filter_id in instance.FILTER_IDS:
                self.filters[filter_id] = instance

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
            self.filters[filter_key].set_filter(filter_key, value)

    def check_filters(self, device, username, filters_tags=None):
        for filter_key, profile_filter in self.filters.items():
            profile_filter.reset_filter()

        if filters_tags is not None:
            for tag in filters_tags:
                for profile_filter in self.filters_by_tags[tag]:
                    if not profile_filter.check_cached_filter(device, username):
                        return False
        else:
            for filter_key, profile_filter in self.filters.items():
                if not profile_filter.check_cached_filter(device, username):
                    return False

        return True


class Filter(object):
    """An interface for filter object"""

    FILTER_IDS = {"OVERRIDE_KEY": "OVERRIDE_VALUE"}
    FILTER_TAGS = []
    RESULT = None

    def set_filter(self, key, val):
        self.FILTER_IDS[key] = val

    def reset_filter(self):
        self.RESULT = None

    def check_cached_filter(self, device, username):
        if self.RESULT is not None:
            return self.RESULT

        self.RESULT = self.check_filter(device, username)
        return self.RESULT

    def check_filter(self, device, username):
        raise NotImplementedError()


class SkipBusinessFilter(Filter):
    FILTER_IDS = {"skip_business": None,
                  "skip_non_business": None}
    FILTER_TAGS = []

    def check_filter(self, device, username):
        if self.FILTER_IDS['skip_business'] is None and \
                self.FILTER_IDS['skip_non_business'] is None:
            return True

        has_business_category = _has_business_category(device)

        if self.FILTER_IDS['skip_business'] is not None:
            if self.FILTER_IDS['skip_business'] and has_business_category:
                print(COLOR_OKGREEN + "@" + username + " has business account, skip." + COLOR_ENDC)
                return False

        if self.FILTER_IDS['skip_non_business'] is not None:
            if self.FILTER_IDS['skip_non_business'] and not has_business_category:
                print(COLOR_OKGREEN + "@" + username + " has non business account, skip." + COLOR_ENDC)
                return False

        return True


class MinMaxFollowersFilter(Filter):
    FILTER_IDS = {"min_followers": None,
                  "max_followers": None}
    FILTER_TAGS = []

    def check_filter(self, device, username):
        if self.FILTER_IDS['min_followers'] is None and \
                self.FILTER_IDS['max_followers'] is None:
            return True

        followers = _get_followers(device)

        if self.FILTER_IDS['min_followers'] is not None:
            if followers < self.FILTER_IDS['min_followers']:
                print(COLOR_OKGREEN + "@" + username + " has less than " + str(self.FILTER_IDS['min_followers']) +
                      " followers, skip." + COLOR_ENDC)
                return False

        if self.FILTER_IDS['max_followers'] is not None:
            if followers > self.FILTER_IDS['max_followers']:
                print(COLOR_OKGREEN + "@" + username + " has more than " + str(self.FILTER_IDS['max_followers']) +
                      " followers, skip." + COLOR_ENDC)
                return False

        return True


class MinMaxFollowingsFilter(Filter):
    FILTER_IDS = {"min_followings": None,
                  "max_followings": None}
    FILTER_TAGS = []

    def check_filter(self, device, username):
        if self.FILTER_IDS['min_followings'] is None and \
                self.FILTER_IDS['max_followings'] is None:
            return True

        followings = _get_followings(device)

        if self.FILTER_IDS['min_followings'] is not None:
            if followings < self.FILTER_IDS['min_followings']:
                print(COLOR_OKGREEN + "@" + username + " has less than " + str(self.FILTER_IDS['min_followings']) +
                      " followings, skip." + COLOR_ENDC)
                return False

        if self.FILTER_IDS['max_followings'] is not None:
            if followings > self.FILTER_IDS['max_followings']:
                print(COLOR_OKGREEN + "@" + username + " has more than " + str(self.FILTER_IDS['max_followings']) +
                      " followings, skip." + COLOR_ENDC)
                return False

        return True


class MinPostsFilter(Filter):
    FILTER_IDS = {"min_posts": None}
    FILTER_TAGS = []

    def check_filter(self, device, username):
        if self.FILTER_IDS['min_posts'] is None:
            return True

        posts_count = _get_posts_count(device)

        if posts_count < self.FILTER_IDS['min_posts']:
            print(COLOR_OKGREEN + "@" + username + " has less than " + str(self.FILTER_IDS['min_posts']) +
                  " posts, skip." + COLOR_ENDC)
            return False

        return True


class MinMaxPotencyRatioFilter(Filter):
    FILTER_IDS = {"min_potency_ratio": None,
                  "max_potency_ratio": None}
    FILTER_TAGS = []

    def check_filter(self, device, username):
        if self.FILTER_IDS['min_potency_ratio'] is None and \
                self.FILTER_IDS['max_potency_ratio'] is None:
            return True

        followers = _get_followers(device)
        followings = _get_followings(device)

        if self.FILTER_IDS['min_potency_ratio'] is not None:
            if followings == 0 or followers / followings < self.FILTER_IDS['min_potency_ratio']:
                print(COLOR_OKGREEN + "@" + username + "'s potency ratio is less than " +
                      str(self.FILTER_IDS['min_potency_ratio']) + ", skip." + COLOR_ENDC)
                return False

        if self.FILTER_IDS['max_potency_ratio'] is not None:
            if followings == 0 or followers / followings > self.FILTER_IDS['max_potency_ratio']:
                print(COLOR_OKGREEN + "@" + username + "'s potency ratio is higher than " +
                      str(self.FILTER_IDS['max_potency_ratio']) + ", skip." + COLOR_ENDC)
                return False

        return True


class MaxDigitsInProfileNameFilter(Filter):
    FILTER_IDS = {"max_digits_in_profile_name": None}
    FILTER_TAGS = ['BEFORE_PROFILE_CLICK']

    def check_filter(self, device, username):
        if self.FILTER_IDS["max_digits_in_profile_name"] is None:
            return True

        if get_count_of_nums_in_str(username) > self.FILTER_IDS["max_digits_in_profile_name"]:
            print(COLOR_OKGREEN + "@" + username + " has more than " + str(self.FILTER_IDS["max_digits_in_profile_name"]) +
                  " digits in profile-name, skip." + COLOR_ENDC)
            return False

        return True


class PrivacyRelationFilter(Filter):
    @unique
    class Relation(Enum):
        PRIVATE_AND_PUBLIC = "private_and_public"
        ONLY_PUBLIC = "only_public"
        ONLY_PRIVATE = "only_private"

    FILTER_IDS = {"privacy_relation": Relation.ONLY_PUBLIC}
    FILTER_TAGS = []

    def set_filter(self, key, val):
        if val == PrivacyRelationFilter.Relation.PRIVATE_AND_PUBLIC.value:
            self.FILTER_IDS["privacy_relation"] = PrivacyRelationFilter.Relation.PRIVATE_AND_PUBLIC
        elif val == PrivacyRelationFilter.Relation.ONLY_PUBLIC.value:
            self.FILTER_IDS["privacy_relation"] = PrivacyRelationFilter.Relation.ONLY_PUBLIC
        elif val == PrivacyRelationFilter.Relation.ONLY_PRIVATE.value:
            self.FILTER_IDS["privacy_relation"] = PrivacyRelationFilter.Relation.ONLY_PRIVATE
        else:
            print_timeless(COLOR_FAIL + f"Unexpected privacy_relation filter value: {val}. "
                                        f"Using default ({PrivacyRelationFilter.Relation.ONLY_PUBLIC.value})." +
                           COLOR_ENDC)
            self.FILTER_IDS["privacy_relation"] = PrivacyRelationFilter.Relation.ONLY_PUBLIC

    def check_filter(self, device, username):
        if self.FILTER_IDS["privacy_relation"] == PrivacyRelationFilter.Relation.PRIVATE_AND_PUBLIC:
            return True

        is_private = is_private_account(device)

        if is_private and self.FILTER_IDS["privacy_relation"] == PrivacyRelationFilter.Relation.ONLY_PUBLIC:
            print(COLOR_OKGREEN + "@" + username + " is private, skip." + COLOR_ENDC)
            return False

        if not is_private and self.FILTER_IDS["privacy_relation"] == PrivacyRelationFilter.Relation.ONLY_PRIVATE:
            print(COLOR_OKGREEN + "@" + username + " is public, skip." + COLOR_ENDC)
            return False

        return True


class MustHaveStoriesFilter(Filter):
    FILTER_IDS = {"skip_profiles_without_stories": None}
    FILTER_TAGS = []

    def check_filter(self, device, username):
        if self.FILTER_IDS["skip_profiles_without_stories"] is None:
            return True

        do_have_stories = do_have_story(device)

        if self.FILTER_IDS["skip_profiles_without_stories"] and not do_have_stories:
            print(COLOR_OKGREEN + "@" + username + " has no stories to watch, skip." + COLOR_ENDC)
            return False

        return True


class BiographyFilter(Filter):
    FILTER_IDS = {"blacklist_words": [],
                  "mandatory_words": [],
                  "specific_alphabet": []}
    FILTER_TAGS = []
    IGNORE_CHARSETS = ["MATHEMATICAL"]

    def check_filter(self, device, username):
        if len(self.FILTER_IDS['blacklist_words']) == 0 and \
                len(self.FILTER_IDS['mandatory_words']) == 0 and \
                self.FILTER_IDS['specific_alphabet'] is None:
            return True

        biography = _get_profile_biography(device)

        if len(self.FILTER_IDS['blacklist_words']) > 0:
            # If we found a blacklist word return False
            for w in self.FILTER_IDS['blacklist_words']:
                blacklist_words = re.compile(r"\b({0})\b".format(w), flags=re.IGNORECASE).search(biography)
                if blacklist_words is not None:
                    print(COLOR_OKGREEN + "@" + username +
                          f" found a blacklisted word '{w}' in biography, skip." + COLOR_ENDC)
                    return False

        if len(self.FILTER_IDS['mandatory_words']) > 0:
            mandatory_words = [w for w in self.FILTER_IDS['mandatory_words']
                               if re.compile(r"\b({0})\b".format(w),
                                             flags=re.IGNORECASE).search(biography) is not None]

            if not mandatory_words:
                print(COLOR_OKGREEN + "@" + username + " mandatory words not found in biography, skip." + COLOR_ENDC)
                return False

        if len(self.FILTER_IDS['specific_alphabet']) > 0:
            if biography != "":
                biography = biography.replace("\n", "")
                alphabet = _find_alphabet(biography, self.IGNORE_CHARSETS)

                if alphabet not in self.FILTER_IDS['specific_alphabet'] and alphabet != "":
                    print(
                        COLOR_OKGREEN + "@" + username +
                        f"'s biography alphabet ({alphabet}) is not "
                        f"in requested alphabets {self.FILTER_IDS['specific_alphabet']}, skip." + COLOR_ENDC)
                    return False
            else:
                fullname = _get_fullname(device)

                if fullname != "":
                    alphabet = _find_alphabet(fullname)
                    if alphabet not in self.FILTER_IDS['specific_alphabet'] and alphabet != "":
                        print(
                            COLOR_OKGREEN + "@" + username +
                            f"'s name alphabet ({alphabet}) is not "
                            f"in requested alphabets {self.FILTER_IDS['specific_alphabet']}, skip." + COLOR_ENDC)
                        return False

        return True


def get_filters_classes():
    return Filter.__subclasses__()
