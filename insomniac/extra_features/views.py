from insomniac.hardban_indicator import hardban_indicator
from insomniac.sleeper import sleeper
from insomniac.utils import *
from insomniac.views import InstagramView, DialogView, case_insensitive_re


class SystemDialogView(InstagramView):

    PLAY_PROTECT_TITLE_TEXT_REGEX = case_insensitive_re("Play Protect warning")
    PLAY_PROTECT_TITLE_CLASSNAME = "android.widget.TextView"
    PLAY_PROTECT_BUTTON_TEXT_REGEX = case_insensitive_re("OPEN ANYWAY")
    PLAY_PROTECT_BUTTON_CLASSNAME = "android.widget.Button"

    def close_play_protect(self) -> bool:
        play_protect_title = self.device.find(textMatches=self.PLAY_PROTECT_TITLE_TEXT_REGEX,
                                              classNameMatches=self.PLAY_PROTECT_TITLE_CLASSNAME)
        play_protect_button = self.device.find(textMatches=self.PLAY_PROTECT_BUTTON_TEXT_REGEX,
                                              classNameMatches=self.PLAY_PROTECT_BUTTON_CLASSNAME)
        if play_protect_title.exists() and play_protect_button.exists():
            print("Close Play Protect warning")
            play_protect_button.click()
            return True
        return False


class ChatView(InstagramView):
    MESSAGE_LIST_ID = '{0}:id/message_list'
    MESSAGE_LIST_CLASSNAME = 'androidx.recyclerview.widget.RecyclerView'

    def is_visible(self) -> bool:
        return self.device.find(resourceId=self.MESSAGE_LIST_ID.format(self.device.app_id),
                                className=self.MESSAGE_LIST_CLASSNAME).exists()

    def is_message_exists(self) -> bool:
        message = self.device.find(resourceId=f'{self.device.app_id}:id/direct_text_message_text_view',
                                   className='android.widget.TextView')
        return message.exists()

    def send_message(self, message) -> bool:
        edit_text = self.device.find(resourceId=f'{self.device.app_id}:id/row_thread_composer_edittext',
                                     className='android.widget.EditText')
        send_button = self.device.find(resourceId=f'{self.device.app_id}:id/row_thread_composer_button_send',
                                       className='android.widget.TextView')
        message_text_view = self.device.find(resourceId=f'{self.device.app_id}:id/direct_text_message_text_view',
                                             className='android.widget.TextView',
                                             text=message)

        edit_text.click()
        edit_text.set_text(message)
        sleeper.random_sleep()
        send_button.click()
        sleeper.random_sleep()
        self.device.close_keyboard()

        # Make sure that message is sent
        return message_text_view.exists()


class StartPageView(InstagramView):

    def close_terms_dialog(self):
        dialog_view = DialogView(self.device)
        if dialog_view.is_visible():
            print("Close \"Terms and Data Policy\" dialog")
            dialog_view.click_continue()

    def go_to_log_in(self) -> 'LogInView':
        self.device.find(className="android.widget.Button",
                         resourceId=f"{self.device.app_id}:id/log_in_button").click()
        return LogInView(self.device)


class LogInView(InstagramView):

    def log_in(self, username, password):
        edit_text_username = self.device.find(className="android.widget.EditText",
                                              resourceId=f"{self.device.app_id}:id/login_username")
        edit_text_username.set_text(username)

        edit_text_password = self.device.find(className="android.widget.EditText",
                                              resourceId=f"{self.device.app_id}:id/password")
        edit_text_password.set_text(password)

        button_log_in = self.device.find(className="android.widget.Button",
                                         resourceId=f"{self.device.app_id}:id/button_text")
        button_log_in.click()

        sleeper.random_sleep(multiplier=2.0)
        hardban_indicator.detect_webview(self.device)
