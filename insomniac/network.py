import socket
import ssl
import urllib.request
import urllib.parse
import json
from urllib.error import HTTPError, URLError

import insomniac.__version__ as __version__
from insomniac.utils import *

INSOMNIAC_USER_AGENT = f"Insomniac/{__version__.__version__}"
INITIAL_TIMEOUT = 2  # seconds
MAX_ATTEMPTS = 5  # number of attempts to make a request after timeout errors
HTTP_OK = 200


PUBLIC_USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393'
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
    'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4'
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
    'Mozilla/5.0 (Linux; U; Android-4.0.3; en-us; Galaxy Nexus Build/IML74K) AppleWebKit/535.7 (KHTML, like Gecko) CrMo/16.0.912.75 Mobile Safari/535.7'
]


def post(url, data, user_agent=INSOMNIAC_USER_AGENT, initial_timeout=INITIAL_TIMEOUT):
    """
    Perform HTTP POST request.

    :param url: URL to request for
    :param data: data to send as the request body
    :param user_agent: optional custom user-agent
    :param initial_timeout: http timeout, increases exponentially on each socket.timeout error
    :return: tuple of: response code, body (if response has one), and fail reason which is None if code is 200
    """

    # parsed_data = urllib.parse.urlencode(data).encode()
    json_data = json.dumps(data)
    json_data_as_bytes = json_data.encode('utf-8')

    headers = {
        'User-Agent': user_agent,
        'Content-Type': 'application/json; charset=utf-8',
        'Content-Length': len(json_data_as_bytes)
    }

    return _request(url=url, data=json_data_as_bytes, headers=headers, initial_timeout=initial_timeout)


def get(url, user_agent=INSOMNIAC_USER_AGENT, initial_timeout=INITIAL_TIMEOUT):
    """
    Perform HTTP GET request.

    :param url: URL to request for
    :param user_agent: optional custom user-agent
    :param initial_timeout: http timeout, increases exponentially on each socket.timeout error
    :return: tuple of: response code, body (if response has one), and fail reason which is None if code is 200
    """
    headers = {
        'User-Agent': user_agent
    }

    return _request(url=url, data=None, headers=headers, initial_timeout=initial_timeout)


def _request(url, data, headers, initial_timeout):
    """
    Perform HTTP GET request.

    :param url: URL to request for
    :param headers: http headers
    :param initial_timeout: http timeout, increases exponentially on each socket.timeout error
    :return: tuple of: response code, body (if response has one), and fail reason which is None if code is 200
    """

    request = urllib.request.Request(url=url, data=data, headers=headers)
    body = None
    attempt = 0
    while True:
        attempt += 1
        timeout = initial_timeout ** attempt
        try:
            with urllib.request.urlopen(request, timeout=timeout, context=ssl.SSLContext()) as response:
                code = response.code
                fail_reason = None
                if code == HTTP_OK:
                    body = response.read()
        except socket.timeout as e:
            code = -1
            fail_reason = e
        except HTTPError as e:
            code = e.code
            fail_reason = e.reason
        except URLError as e:
            code = -1
            fail_reason = e.reason

        if isinstance(fail_reason, socket.timeout):
            if attempt <= MAX_ATTEMPTS:
                print(COLOR_FAIL + f"Timeout ({timeout} sec), retrying..." + COLOR_ENDC)
            else:
                print(COLOR_FAIL + f"Timeout ({timeout} sec), reached max number of attempts." + COLOR_ENDC)
                break
        else:
            break

    if code != HTTP_OK and fail_reason is None:
        fail_reason = Exception("unknown reason")

    return code, body, fail_reason
