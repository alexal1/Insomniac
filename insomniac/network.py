import socket
import ssl
import urllib.request
from urllib.error import HTTPError, URLError

import insomniac.__version__ as __version__
from insomniac.utils import *

INSOMNIAC_USER_AGENT = f"Insomniac/{__version__.__version__}"
INITIAL_TIMEOUT = 2  # seconds
MAX_ATTEMPTS = 5  # number of attempts to make a request after timeout errors
HTTP_OK = 200


def get(url, user_agent=INSOMNIAC_USER_AGENT):
    """
    Perform HTTP GET request.

    :param url: URL to request for
    :param user_agent: optional custom user-agent
    :return: tuple of: response code, body (if response has one), and fail reason which is None if code is 200
    """
    headers = {
        'User-Agent': user_agent
    }
    request = urllib.request.Request(url, headers=headers)
    body = None
    attempt = 0
    while True:
        attempt += 1
        timeout = INITIAL_TIMEOUT ** attempt
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
