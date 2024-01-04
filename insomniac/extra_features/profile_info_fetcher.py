import collections
import json
from datetime import timedelta

from insomniac import network, HTTP_OK
from insomniac.utils import *

INSTAGRAM_GRAPHQL_URL = 'https://www.instagram.com/{0}/?__a=1'

RATE_LIMIT_COOLDOWN_SECONDS = 3
RATE_LIMIT_COOLDOWN_FIXUP = 0.5
LAST_INFO_FETCH_TIME = datetime.now()


def get_page(username):
    global LAST_INFO_FETCH_TIME
    delta_sec_from_last_fetch = datetime.now() - LAST_INFO_FETCH_TIME
    if delta_sec_from_last_fetch <= timedelta(seconds=RATE_LIMIT_COOLDOWN_SECONDS):
        time_to_sleep = RATE_LIMIT_COOLDOWN_SECONDS - delta_sec_from_last_fetch.seconds + RATE_LIMIT_COOLDOWN_FIXUP
        print_debug(f"Sleeping {time_to_sleep} seconds in order to not reach Instagram-graphql rate-limit")
        sleep(time_to_sleep)

    print("Fetching @{0} info...".format(username))
    code, body, fail_reason = network.get(INSTAGRAM_GRAPHQL_URL.format(username), random.choice(network.PUBLIC_USER_AGENTS))
    if code == HTTP_OK and body is not None:
        print("Info fetched successfully".format(username))
        LAST_INFO_FETCH_TIME = datetime.now()
        return body.decode('utf-8')

    print(COLOR_FAIL + "Info couldn't be fetched successfully, code: {0}, error: {1}".format(code, fail_reason) + COLOR_ENDC)
    return None


def sort_list(xlist):
    with_count = dict(collections.Counter(xlist))
    output = {k: v for k, v in sorted(with_count.items(), reverse=True, key=lambda item: item[1])}
    return output


def find_extra_info(resp_js):
    def add_or_extend(obj, target_list):
        if isinstance(obj, list):
            target_list.extend(obj)
        else:
            target_list.append(obj)

    emails_list = []
    email_re = re.findall(r"[_a-z0-9-\.]+[＠@]{1}[a-z0-9]+\.[a-z0-9]+", resp_js.lower())
    add_or_extend(email_re, emails_list)

    tags_list = []
    tags_re = re.findall(r"[＃#]{1}([_a-zA-Z0-9\.\+-]+)", resp_js)
    add_or_extend(tags_re, tags_list)

    mentions_list = []
    mention_re = re.findall(r"[＠@]([_a-zA-Z0-9\.\+-]+)", resp_js)
    for x in mention_re:
        if x.endswith("."):
            x = x.strip(".")
        mentions_list.append(x)

    return emails_list, tags_list, mentions_list


def fetch_user_info(username):
    resp_js = get_page(username)
    if resp_js is None or resp_js == '{}':
        return None

    try:
        js = json.loads(resp_js)
    except json.JSONDecodeError as e:
        print(f"Couldn't decode fetched-profile-info into a json structure, but its ok - using legacy-filters instead.")
        print_debug(COLOR_FAIL + f"Fetched info: {resp_js}" + COLOR_ENDC)
        return None

    js = js['graphql']['user']

    try:
        emails_list, tags_list, mentions_list = find_extra_info(resp_js)
    except Exception as e:
        print(f"Couldn't resolve related info of profile, but its ok - using legacy-filters instead.")
        print_debug(COLOR_FAIL + describe_exception(e) + COLOR_ENDC)
        emails_list, tags_list, mentions_list = [], [], []

    userinfo = {
        'username': js['username'],
        'user_id': js['id'],
        'name': js['full_name'],
        'followers': js['edge_followed_by']['count'],
        'following': js['edge_follow']['count'],
        'posts_count': js['edge_owner_to_timeline_media']['count'],
        'posts_count_video': js['edge_felix_video_timeline']['count'],
        'highlight_reels_count': js['highlight_reel_count'],
        'bio': js['biography'].replace('\n', ', '),
        'external url': js['external_url'],
        'is_private': js['is_private'],
        'is_verified': js['is_verified'],
        'is_business_account': js['is_business_account'],
        'is_joined_recently': js['is_joined_recently'],
        'business_category_name': js['business_category_name'],
        'business_category_enum': js['category_enum'],
        'has_guides': js['has_guides'],
        'related_emails_list': emails_list,
        'related_tags_list': tags_list,
        'related_mentions_list': mentions_list
    }

    return userinfo
