## Registration Flow

Insomniac gives the possibility to create Instagram accounts automatically. This can be done via `--register registration/users.txt` argument. Insomniac will do the following:
1. Open the app and **create new identity** if you're using a clone via [appcloner.app](https://appcloner.app), or just clear app data if you're not.
2. Fill in a **phone number and a confirmation code** using two appropriate methods from [api.py](https://github.com/alexal1/Insomniac/blob/master/registration/api.py). Default methods are just requesting phone numbers and confirmation codes via user input in Terminal. But it doesn't make sense since we're doing automation, so there's also implementation of these methods via [smspva.com](http://smspva.com/) API. But smspva is a paid service, so if you like, you can rent numbers for Instagram and then edit [api.py](https://github.com/alexal1/Insomniac/blob/master/registration/api.py) accordingly (enter your API key, country code, and uncomment smspva methods).
3. Fill in **Full Name, Password, and Username** taken from [users.txt](https://github.com/alexal1/Insomniac/blob/master/registration/users.txt). You can put any amount of users there. Registered users' rows will be marked as `DONE`. Just run the script with `--repeat 0` to register all users from users.txt one by one without a hitch.
4. Finish registration and skip all suggested users to follow.
5. **Log Out**.

You can watch the record of the whole process in this video:
https://www.youtube.com/watch?v=Zgv8wN7X7mM

So, how to get started with the registration flow?
1. [Activate Insomniac](https://insomniac-bot.com/activate/), since `--register` is an extra feature.
2. [Download](https://github.com/alexal1/Insomniac/archive/master.zip) the whole Insomniac project, because you need to have "registration" folder near start.py.
3. Change your device language to English (bot sometimes relies on English text on the screen).
4. Consider installing [appcloner.app](https://appcloner.app) to use their "New identity" feature ([read more here](https://appcloner.blog/2020/08/29/new-identity/)).
5. Edit [api.py](https://github.com/alexal1/Insomniac/blob/master/registration/api.py) according to your needs:
   * To enter phone number and confirmation codes manually – do nothing.
   * To use [smspva.com](http://smspva.com/) API – put your key into `SMSPVA_API_KEY`, put your country code into `SMSPVA_COUNTRY_CODE`, set `get_phone_number = _get_phone_number_smspva` and `get_confirmation_code = _get_confirmation_code_smspva`.
   * To use any other API – write your own implementation for `get_phone_number` and `get_confirmation_code`.
6. Put full names, passwords and usernames of your future users into [users.txt](https://github.com/alexal1/Insomniac/blob/master/registration/users.txt).
