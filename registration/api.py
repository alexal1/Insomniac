# This file provides the way of getting a phone number and an SMS confirmation code in "registration" process.
# The only two methods that should be exposed from this file are "get_phone_number" and "get_confirmation_code".
# You can find them at the end of this file. Choose one of ready-to-use implementations or create your own.
import json
from typing import Optional

from insomniac import network, HTTP_OK
from insomniac.sleeper import sleeper
from insomniac.utils import *

CONFIRMATION_CODE_MAX_ATTEMPTS_COUNT = 5  # times to retry requesting of confirmation code
SMSPVA_COUNTRY_CODE = "RU"  # or "US" or "ID" or any other else
SMSPVA_API_KEY = "your-api-key"  # more info on the official smspva site http://smspva.com/new_theme_api.html
SMS_ACTIVATE_COUNTRY_CODE = 0  # 0 is Russia, other codes are listed in the docs https://sms-activate.ru/en/api2#number
SMS_ACTIVATE_API_KEY = "your-api-key"  # more info on the official sms-activate.ru site https://sms-activate.ru/en/


class PhoneNumberData:
    response_id = None
    country_code = None
    phone_number = None

    def __init__(self, response_id, country_code, phone_number):
        self.response_id = response_id
        self.country_code = country_code
        self.phone_number = phone_number


# -------- Simple implementation --------

def _get_phone_number_simple() -> Optional[PhoneNumberData]:
    data = PhoneNumberData(0, None, None)
    while data.country_code is None or data.phone_number is None:
        user_input = input('Enter mobile phone (format "+7 1234567890"): ')
        try:
            data.country_code, data.phone_number = user_input.split(' ')
        except ValueError:
            continue
        if data.country_code[0] != '+':
            data.country_code = None
    return data


def _get_confirmation_code_simple(_) -> Optional[str]:
    return input("Enter confirmation code: ")


# -------- smspva.com API --------

def _get_phone_number_smspva() -> Optional[PhoneNumberData]:
    url = f"http://smspva.com/priemnik.php?metod=get_number&service=opt16" \
          f"&country={SMSPVA_COUNTRY_CODE}" \
          f"&apikey={SMSPVA_API_KEY}"
    code, body, fail_reason = network.get(url, 'Mozilla/5.0')
    if code == HTTP_OK and body is not None:
        json_data = json.loads(body)
    else:
        print(COLOR_FAIL + f"Cannot get phone number via smspva.com API: {code} ({fail_reason})" + COLOR_ENDC)
        return None

    response_id = json_data["id"]
    country_code = json_data["CountryCode"]
    phone_number = json_data["number"]
    phone_number_data = PhoneNumberData(response_id, country_code, phone_number)
    return phone_number_data


def _get_confirmation_code_smspva(response_id) -> Optional[str]:
    url = f"http://smspva.com/priemnik.php?metod=get_sms&service=opt16" \
          f"&country={SMSPVA_COUNTRY_CODE}" \
          f"&id={response_id}" \
          f"&apikey={SMSPVA_API_KEY}"
    attempts_count = 0
    while True:
        sleeper.random_sleep(multiplier=8.0)
        code, body, fail_reason = network.get(url, 'Mozilla/5.0')
        attempts_count += 1
        if code == HTTP_OK and body is not None:
            json_data = json.loads(body)
        else:
            print(COLOR_FAIL + f"Cannot get confirmation code via smspva.com API: {code} ({fail_reason})" + COLOR_ENDC)
            return None

        confirmation_code = json_data["sms"]
        if confirmation_code is None:
            if attempts_count >= CONFIRMATION_CODE_MAX_ATTEMPTS_COUNT:
                print("Well, looks like Instagram isn't going to send SMS to this phone number")
                return None
            print("Let's wait a bit more: confirmation code isn't received yet")
        else:
            break
    return confirmation_code


# -------- sms-activate.ru API --------

def _get_phone_number_sms_activate() -> Optional[PhoneNumberData]:
    try:
        import phonenumbers
    except ImportError:
        print(COLOR_FAIL + f"Using sms-activate.ru API requires phonenumbers library." + COLOR_ENDC)
        print(COLOR_FAIL + COLOR_BOLD + f"python3 -m pip install phonenumbers" + COLOR_ENDC)
        return None
    url = f"https://sms-activate.ru/stubs/handler_api.php" \
          f"?api_key={SMS_ACTIVATE_API_KEY}" \
          f"&country={SMS_ACTIVATE_COUNTRY_CODE}" \
          f"&action=getNumber" \
          f"&service=ig"
    code, body, fail_reason = network.get(url, 'Mozilla/5.0')
    if code != HTTP_OK or body is None:
        print(COLOR_FAIL + f"Cannot get phone number via sms-activate.ru API: {code} ({fail_reason})" + COLOR_ENDC)
        return None

    response_regex = re.compile(r'ACCESS_NUMBER:(\d+):(\d+)')
    match = response_regex.match(body.decode('utf-8'))
    if match:
        response_id = match.group(1)
        full_phone_number = match.group(2)
    else:
        print(COLOR_FAIL + f"Cannot parse sms-activate.ru response: {str(body)})" + COLOR_ENDC)
        return None

    phone_number_object = phonenumbers.parse(f'+{full_phone_number}', None)
    country_code = str(phone_number_object.country_code)
    phone_number = str(phone_number_object.national_number)
    phone_number_data = PhoneNumberData(response_id, country_code, phone_number)
    return phone_number_data


def _get_confirmation_code_sms_activate(response_id) -> Optional[str]:
    url = f"https://sms-activate.ru/stubs/handler_api.php" \
          f"?api_key={SMS_ACTIVATE_API_KEY}" \
          f"&id={response_id}" \
          f"&country={SMSPVA_COUNTRY_CODE}" \
          f"&action=getStatus"
    attempts_count = 0
    while True:
        sleeper.random_sleep(multiplier=8.0)
        code, body, fail_reason = network.get(url, 'Mozilla/5.0')
        attempts_count += 1
        if code != HTTP_OK or body is None:
            print(COLOR_FAIL + f"Cannot get confirmation code via sms-activate.ru API: {code} ({fail_reason})" + COLOR_ENDC)
            return None

        response_regex = re.compile(r'STATUS_OK:(\d+)')
        match = response_regex.match(body.decode('utf-8'))
        if match:
            confirmation_code = match.group(1)
            return confirmation_code
        else:
            if attempts_count >= CONFIRMATION_CODE_MAX_ATTEMPTS_COUNT:
                print("Well, looks like Instagram isn't going to send SMS to this phone number")
                return None
            print("Let's wait a bit more: confirmation code isn't received yet")


# Choose either "simple" implementation (asks you to enter phone number and confirmation code in the terminal manually)
# or implementation via smspva.com API (automatically gets confirmation code from a remote SIM card).
#
# You can also write your own implementation! It just has to follow these rules: 1) get_phone_number() returns
# PhoneNumberData object and 2) get_confirmation_code(response_id) takes response_id argument from PhoneNumberData and
# returns confirmation code (string).
get_phone_number = _get_phone_number_simple  # or _get_phone_number_smspva or _get_phone_number_sms_activate
get_confirmation_code = _get_confirmation_code_simple  # or _get_confirmation_code_smspva or _get_confirmation_code_sms_activate
