import unicodedata

from insomniac.extra_features.face_detector import FaceDetector
from insomniac.utils import *
from insomniac.views import ProfileView


def has_business_category(device):
    return ProfileView(device).has_business_category()


def get_posts_count(device):
    return ProfileView(device).get_posts_count() or 0


def get_followers(device):
    return ProfileView(device).get_followers_count() or 0


def get_followings(device):
    return ProfileView(device).get_following_count() or 0


def get_profile_biography(device):
    return ProfileView(device).get_profile_biography()


def find_alphabet(biography, ignore_charsets=None):
    if ignore_charsets is None:
        ignore_charsets = []

    a_dict = {}
    max_alph = ""
    for x in range(0, len(biography)):
        if biography[x].isalpha():
            a = unicodedata.name(biography[x]).split(" ")[0]
            if a not in ignore_charsets:
                if a in a_dict:
                    a_dict[a] += 1
                else:
                    a_dict[a] = 1
    if bool(a_dict):
        max_alph = max(a_dict, key=lambda k: a_dict[k])

    return max_alph


def get_fullname(device):
    return ProfileView(device).get_full_name()


def is_face_on_profile_image(device, face_detector) -> bool:
    profile_image = ProfileView(device).get_profile_image()
    if profile_image is None:
        print(COLOR_FAIL + "Cannot find profile image" + COLOR_ENDC)
        return False
    return face_detector.is_face_on_image(profile_image)


def get_gender_by_profile_image(device, face_detector) -> (Optional['FaceDetector.Gender'], float):
    profile_image = ProfileView(device).get_profile_image()
    if profile_image is None:
        print(COLOR_FAIL + "Cannot find profile image" + COLOR_ENDC)
        return None, 0.5
    return face_detector.get_gender(profile_image)
