import json
from urllib.parse import urlparse

from insomniac import network, HTTP_OK
from insomniac.utils import *


PROFILE_VALIDATION_SERVICE_URL = 'https://emailsverified.herokuapp.com/checkinstagram/?username={0}'
PROFILE_STATUS_FIELD = 'status'
PROFILE_TAKEN = 'taken'
PROFILE_AVAILABLE = 'available'

should_validate_profile_existence = True


def validate_ig_profile_existence(profile_name):
    if not should_validate_profile_existence:
        return True

    print(f"Validating profile {profile_name} existence")

    try:
        code, body, fail_reason = network.get(PROFILE_VALIDATION_SERVICE_URL.format(profile_name),
                                              random.choice(network.PUBLIC_USER_AGENTS))
        if code == HTTP_OK and body is not None:
            response = body.decode('utf-8')
            print_debug(f"Received IG-profile-name query response for {profile_name}: {response}")
            profile_name_info = json.loads(response)
            return profile_name_info[PROFILE_STATUS_FIELD] == PROFILE_TAKEN
        else:
            print_debug(COLOR_FAIL + f"IG-profile-name {profile_name} query failed. code: {code}, error: {fail_reason}" + COLOR_ENDC)
    except Exception as ex:
        print_debug(COLOR_FAIL + f"IG-profile-name {profile_name} query failed." + COLOR_ENDC)
        print_debug(COLOR_FAIL + describe_exception(ex) + COLOR_ENDC)

    return False


def validate_url(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc, result.path])
    except Exception as e:
        print(COLOR_FAIL + f"Error validating URL {x}. Error: {e}" + COLOR_ENDC)
        return False
