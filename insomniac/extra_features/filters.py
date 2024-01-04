import json
from collections import defaultdict
from enum import Enum, unique

from insomniac.actions_impl import is_private_account, do_have_story, is_already_followed
from insomniac.actions_types import FilterAction
from insomniac.extra_features.face_detector import FaceDetector
from insomniac.extra_features.filters_impl import has_business_category, \
    get_posts_count, get_followers, get_followings, get_profile_biography, find_alphabet, get_fullname, \
    is_face_on_profile_image, get_gender_by_profile_image
from insomniac.extra_features.profile_info_fetcher import fetch_user_info
from insomniac.utils import *

FILENAME_CONDITIONS = "filter.json"


class FiltersManager(object):
    """This class manages the profiles-filters of an insomniac-session"""

    FILTERS_ARGS = {
        "filters": {
            "help": 'add this argument if you want to pass filters as an argument and not from '
                    'filters.json file',
            "default": None
        }
    }

    filters = {}
    filters_by_tags = defaultdict(list)
    curr_profile_fetched_info = None
    is_profile_info_fetched = False
    fetch_profiles_from_net = False
    is_filters_enabled = False

    def __init__(self, on_action):
        self.on_action = on_action

        for clazz in get_filters_classes():
            instance = clazz()
            for filter_id in instance.FILTER_IDS:
                self.filters[filter_id] = instance

            for tag in instance.FILTER_TAGS:
                self.filters_by_tags[tag].append(instance)

    def get_filters_args(self):
        return self.FILTERS_ARGS

    def disable_all_filters(self):
        for tag in self.filters_by_tags:
            for profile_filter in self.filters_by_tags[tag]:
                profile_filter.disable_filter()

        for filter_key, profile_filter in self.filters.items():
            profile_filter.disable_filter()

        self.is_filters_enabled = False

    def set_filters(self, args):
        loaded_filters = None
        self.disable_all_filters()

        if args.filters is not None:
            loaded_filters = args.filters
        elif os.path.exists(FILENAME_CONDITIONS):
            with open(FILENAME_CONDITIONS, encoding="utf-8") as json_file:
                loaded_filters = json.load(json_file)

        if loaded_filters is not None:
            self.is_filters_enabled = True

            for filter_key, value in loaded_filters.items():
                self.filters[filter_key].set_filter(filter_key, value)

    def is_all_filters_already_satisfied(self):
        for filter_key, profile_filter in self.filters.items():
            if not profile_filter.is_already_satisfied():
                return False

        return True

    def check_filters(self, device, username, reset=True, filters_tags=None):
        if not self.is_filters_enabled:
            return True, True

        if reset:
            for filter_key, profile_filter in self.filters.items():
                profile_filter.reset_filter()
            self.is_profile_info_fetched = False

        if not self.is_profile_info_fetched and self.fetch_profiles_from_net:
            try:
                self.curr_profile_fetched_info = fetch_user_info(username)
            except Exception as e:
                print(COLOR_FAIL + f"Couldn't get user-details ahead of time." + COLOR_ENDC)
                print(COLOR_FAIL + describe_exception(e) + COLOR_ENDC)
                self.curr_profile_fetched_info = None

            self.is_profile_info_fetched = True

        if filters_tags is not None:
            for tag in filters_tags:
                for profile_filter in self.filters_by_tags[tag]:
                    if not profile_filter.check_cached_filter(device, username, tag, self.curr_profile_fetched_info):
                        self.on_action(FilterAction(user=username))
                        return False, False
        else:
            for filter_key, profile_filter in self.filters.items():
                if not profile_filter.check_cached_filter(device, username, None, self.curr_profile_fetched_info):
                    self.on_action(FilterAction(user=username))
                    return False, False

        return True, self.is_all_filters_already_satisfied()

    def set_fetch_profiles_from_net(self, value):
        self.fetch_profiles_from_net = value


class Filter(object):
    """An interface for filter object"""

    FILTER_IDS = {"OVERRIDE_KEY": "OVERRIDE_VALUE"}
    FILTER_TAGS = []
    IS_ENABLED = False
    RESULT = None

    def disable_filter(self):
        self.IS_ENABLED = False

    def set_filter(self, key, val):
        self.IS_ENABLED = True
        self.FILTER_IDS[key] = val

    def reset_filter(self):
        self.RESULT = None

    def is_already_satisfied(self):
        if not self.IS_ENABLED:
            return True

        return self.RESULT is True

    def check_cached_filter(self, device, username, trigger_tag, fetched_profile_info):
        if self.RESULT is not None:
            return self.RESULT

        if not self.IS_ENABLED:
            return True

        result = self.check_filter(device, username, trigger_tag, fetched_profile_info)
        if result is None:
            return True

        self.RESULT = result
        return self.RESULT

    def check_filter(self, device, username, trigger_tag, fetched_profile_info):
        raise NotImplementedError()


class SkipBusinessFilter(Filter):
    FILTER_IDS = {"skip_business": None,
                  "skip_non_business": None}
    FILTER_TAGS = ['BEFORE_PROFILE_CLICK']

    def check_filter(self, device, username, trigger_tag, fetched_profile_info):
        if trigger_tag == 'BEFORE_PROFILE_CLICK':
            if fetched_profile_info is None:
                return None

            is_business = fetched_profile_info['is_business_account']
        else:
            is_business = has_business_category(device)

        if self.FILTER_IDS['skip_business'] is not None:
            if self.FILTER_IDS['skip_business'] and is_business:
                print(COLOR_OKGREEN + "@" + username + " has business account, skip." + COLOR_ENDC)
                return False

        if self.FILTER_IDS['skip_non_business'] is not None:
            if self.FILTER_IDS['skip_non_business'] and not is_business:
                print(COLOR_OKGREEN + "@" + username + " has non business account, skip." + COLOR_ENDC)
                return False

        return True


class MinMaxFollowersFilter(Filter):
    FILTER_IDS = {"min_followers": None,
                  "max_followers": None}
    FILTER_TAGS = ['BEFORE_PROFILE_CLICK']

    def check_filter(self, device, username, trigger_tag, fetched_profile_info):
        if trigger_tag == 'BEFORE_PROFILE_CLICK':
            if fetched_profile_info is None:
                return None

            followers = fetched_profile_info['followers']
        else:
            followers = get_followers(device)

        if self.FILTER_IDS['min_followers'] is not None:
            if followers < int(self.FILTER_IDS['min_followers']):
                print(COLOR_OKGREEN + "@" + username + " has less than " + str(self.FILTER_IDS['min_followers']) +
                      " followers, skip." + COLOR_ENDC)
                return False

        if self.FILTER_IDS['max_followers'] is not None:
            if followers > int(self.FILTER_IDS['max_followers']):
                print(COLOR_OKGREEN + "@" + username + " has more than " + str(self.FILTER_IDS['max_followers']) +
                      " followers, skip." + COLOR_ENDC)
                return False

        return True


class MinMaxFollowingsFilter(Filter):
    FILTER_IDS = {"min_followings": None,
                  "max_followings": None}
    FILTER_TAGS = ['BEFORE_PROFILE_CLICK']

    def check_filter(self, device, username, trigger_tag, fetched_profile_info):
        if trigger_tag == 'BEFORE_PROFILE_CLICK':
            if fetched_profile_info is None:
                return None

            followings = fetched_profile_info['following']
        else:
            followings = get_followings(device)

        if self.FILTER_IDS['min_followings'] is not None:
            if followings < int(self.FILTER_IDS['min_followings']):
                print(COLOR_OKGREEN + "@" + username + " has less than " + str(self.FILTER_IDS['min_followings']) +
                      " followings, skip." + COLOR_ENDC)
                return False

        if self.FILTER_IDS['max_followings'] is not None:
            if followings > int(self.FILTER_IDS['max_followings']):
                print(COLOR_OKGREEN + "@" + username + " has more than " + str(self.FILTER_IDS['max_followings']) +
                      " followings, skip." + COLOR_ENDC)
                return False

        return True


class MinPostsFilter(Filter):
    FILTER_IDS = {"min_posts": None}
    FILTER_TAGS = ['BEFORE_PROFILE_CLICK']

    def check_filter(self, device, username, trigger_tag, fetched_profile_info):
        if trigger_tag == 'BEFORE_PROFILE_CLICK':
            if fetched_profile_info is None:
                return None

            posts_count = fetched_profile_info['posts_count']
        else:
            posts_count = get_posts_count(device)

        if posts_count < int(self.FILTER_IDS['min_posts']):
            print(COLOR_OKGREEN + "@" + username + " has less than " + str(self.FILTER_IDS['min_posts']) +
                  " posts, skip." + COLOR_ENDC)
            return False

        return True


class MinMaxPotencyRatioFilter(Filter):
    FILTER_IDS = {"min_potency_ratio": None,
                  "max_potency_ratio": None}
    FILTER_TAGS = ['BEFORE_PROFILE_CLICK']

    def check_filter(self, device, username, trigger_tag, fetched_profile_info):
        if trigger_tag == 'BEFORE_PROFILE_CLICK':
            if fetched_profile_info is None:
                return None

            followers = fetched_profile_info['followers']
            followings = fetched_profile_info['following']
        else:
            followers = get_followers(device)
            followings = get_followings(device)

        if self.FILTER_IDS['min_potency_ratio'] is not None:
            if followings == 0 or followers / followings < float(self.FILTER_IDS['min_potency_ratio']):
                print(COLOR_OKGREEN + "@" + username + "'s potency ratio is less than " +
                      str(self.FILTER_IDS['min_potency_ratio']) + ", skip." + COLOR_ENDC)
                return False

        if self.FILTER_IDS['max_potency_ratio'] is not None:
            if followings == 0 or followers / followings > float(self.FILTER_IDS['max_potency_ratio']):
                print(COLOR_OKGREEN + "@" + username + "'s potency ratio is higher than " +
                      str(self.FILTER_IDS['max_potency_ratio']) + ", skip." + COLOR_ENDC)
                return False

        return True


class MaxDigitsInProfileNameFilter(Filter):
    FILTER_IDS = {"max_digits_in_profile_name": None}
    FILTER_TAGS = ['BEFORE_PROFILE_CLICK']

    def check_filter(self, device, username, trigger_tag, fetched_profile_info):
        if get_count_of_nums_in_str(username) > int(self.FILTER_IDS["max_digits_in_profile_name"]):
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
    FILTER_TAGS = ['BEFORE_PROFILE_CLICK']

    def set_filter(self, key, val):
        super(PrivacyRelationFilter, self).set_filter(key, val)
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

    def check_filter(self, device, username, trigger_tag, fetched_profile_info):
        if self.FILTER_IDS["privacy_relation"] == PrivacyRelationFilter.Relation.PRIVATE_AND_PUBLIC:
            return True

        if trigger_tag == 'BEFORE_PROFILE_CLICK':
            if fetched_profile_info is None:
                return None

            is_private = fetched_profile_info['is_private']
        else:
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

    def check_filter(self, device, username, trigger_tag, fetched_profile_info):
        do_have_stories = do_have_story(device)

        if self.FILTER_IDS["skip_profiles_without_stories"] and not do_have_stories:
            print(COLOR_OKGREEN + "@" + username + " has no stories to watch, skip." + COLOR_ENDC)
            return False

        return True


class BiographyFilter(Filter):
    FILTER_IDS = {"blacklist_words": [],
                  "mandatory_words": [],
                  "specific_alphabet": []}
    FILTER_TAGS = ['BEFORE_PROFILE_CLICK']
    IGNORE_CHARSETS = ["MATHEMATICAL"]

    def check_filter(self, device, username, trigger_tag, fetched_profile_info):
        if trigger_tag == 'BEFORE_PROFILE_CLICK':
            if fetched_profile_info is None:
                return None

            biography = fetched_profile_info['bio']
        else:
            biography = get_profile_biography(device)

        if len(self.FILTER_IDS['blacklist_words']) > 0:
            # If we found a blacklist word return False
            splitted_blacklist_words_list = split_list_items_with_separator(self.FILTER_IDS['blacklist_words'], ',')
            for w in splitted_blacklist_words_list:
                blacklist_words = re.compile(r"\b({0})\b".format(w), flags=re.IGNORECASE).search(biography)
                if blacklist_words is not None:
                    print(COLOR_OKGREEN + "@" + username +
                          f" found a blacklisted word '{w}' in biography, skip." + COLOR_ENDC)
                    return False

        if len(self.FILTER_IDS['mandatory_words']) > 0:
            splitted_mandatory_words_list = split_list_items_with_separator(self.FILTER_IDS['mandatory_words'], ',')
            mandatory_words = [w for w in splitted_mandatory_words_list
                               if re.compile(r"\b({0})\b".format(w),
                                             flags=re.IGNORECASE).search(biography) is not None]

            if not mandatory_words:
                print(COLOR_OKGREEN + "@" + username + " mandatory words not found in biography, skip." + COLOR_ENDC)
                return False

        if len(self.FILTER_IDS['specific_alphabet']) > 0:
            if biography != "":
                biography = biography.replace("\n", "")
                alphabet = find_alphabet(biography, self.IGNORE_CHARSETS)

                if alphabet not in self.FILTER_IDS['specific_alphabet'] and alphabet != "":
                    print(
                        COLOR_OKGREEN + "@" + username +
                        f"'s biography alphabet ({alphabet}) is not "
                        f"in requested alphabets {self.FILTER_IDS['specific_alphabet']}, skip." + COLOR_ENDC)
                    return False
            else:
                fullname = get_fullname(device)

                if fullname != "":
                    alphabet = find_alphabet(fullname)
                    if alphabet not in self.FILTER_IDS['specific_alphabet'] and alphabet != "":
                        print(
                            COLOR_OKGREEN + "@" + username +
                            f"'s name alphabet ({alphabet}) is not "
                            f"in requested alphabets {self.FILTER_IDS['specific_alphabet']}, skip." + COLOR_ENDC)
                        return False

        return True


class SkipAlreadyFollowingFilter(Filter):
    FILTER_IDS = {"skip_already_following_profiles": True}
    FILTER_TAGS = []

    def check_filter(self, device, username, trigger_tag, fetched_profile_info):
        if not self.FILTER_IDS['skip_already_following_profiles']:
            return True

        is_already_following = is_already_followed(device)

        if is_already_following:
            print(COLOR_OKGREEN + "already following @" + username + ", skip." + COLOR_ENDC)
            return False

        return True


class HumanRecognitionFilter(Filter):
    FILTER_IDS = {"only_profiles_with_faces": None}
    FILTER_TAGS = []
    face_detector = FaceDetector()

    def set_filter(self, key, val):
        super(HumanRecognitionFilter, self).set_filter(key, val)
        self.face_detector.init()
        if val == FaceDetector.Gender.ANY.value:
            self.FILTER_IDS["only_profiles_with_faces"] = FaceDetector.Gender.ANY
        elif val == FaceDetector.Gender.MALE.value:
            self.FILTER_IDS["only_profiles_with_faces"] = FaceDetector.Gender.MALE
        elif val == FaceDetector.Gender.FEMALE.value:
            self.FILTER_IDS["only_profiles_with_faces"] = FaceDetector.Gender.FEMALE
        else:
            print_timeless(COLOR_FAIL + f"Unexpected only_profiles_with_faces filter value: {val}. "
                                        f"Ignoring this filter." +
                           COLOR_ENDC)
            self.FILTER_IDS["only_profiles_with_faces"] = None

    def check_filter(self, device, username, trigger_tag, fetched_profile_info):
        only_profiles_with_faces = self.FILTER_IDS["only_profiles_with_faces"]

        if only_profiles_with_faces == FaceDetector.Gender.ANY:
            print("Analyzing profile image: if contains face(s) or not...")
            is_face = is_face_on_profile_image(device, self.face_detector)
            if is_face:
                print("Face detected")
            else:
                print(COLOR_OKGREEN + "Face NOT detected. Skip this user" + COLOR_ENDC)
            return is_face

        if only_profiles_with_faces == FaceDetector.Gender.MALE \
                or only_profiles_with_faces == FaceDetector.Gender.FEMALE:
            print(f"Analyzing profile image: if contains {only_profiles_with_faces.value} face(s) or not...")
            gender, confidence = get_gender_by_profile_image(device, self.face_detector)
            if gender == FaceDetector.Gender.MALE or gender == FaceDetector.Gender.FEMALE:
                print(f"Determined gender as \"{gender.value}\" with confidence {confidence}")
                return gender == only_profiles_with_faces
            elif gender == FaceDetector.Gender.NOT_HUMAN:
                print(f"No face found at all")
                return False
            else:
                print(f"Cannot say exactly what's the gender. Confidence is very low: {confidence}")
                return False

        return True


def get_filters_classes():
    return Filter.__subclasses__()
