from kivy.app import App
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
from kivy.core.window import Window
import json
import os

Window.softinput_mode = "below_target"
os.environ['KIVY_KEYBOARD'] = 'system'

# Force portrait on Android
try:
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    ActivityInfo = autoclass('android.content.pm.ActivityInfo')
    PythonActivity.mActivity.setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT)
except Exception:
    pass

API_URL = "https://aria-finance.onrender.com/chat"
PING_URL = "https://aria-finance.onrender.com/"
MAX_RETRIES = 5

class AriaApp(App):
    def build(self):
        self.pending_message = ""
        self.retry_count = 0
        self.server_awake = False
        Clock.schedule_once(self._ping_server, 2)  # ping on startup to wake Render
        return Builder.load_file('aria.kv')

    def _ping_server(self, dt):
        UrlRequest(
            PING_URL,
            on_success=self._ping_success,
            on_failure=self._ping_fail,
            on_error=self._ping_fail,
            timeout=60
        )

    def _ping_success(self, req, result):
        self.server_awake = True

    def _ping_fail(self, req, err):
        Clock.schedule_once(self._ping_server, 20)

    def on_resume(self):
        logs = self.root.ids.chat_logs
        logs.text = "[b][color=00cc88]ARIA:[/color][/b] Good day! I'm your Advanced Retail Investment Advisor. 📈\n\nAsk me about any stock on NSE or US markets (e.g. [i]RELIANCE.NS[/i] or [i]TSLA[/i])."
        self.root.ids.user_input.text = ""
        self.retry_count = 0
        self.pending_message = ""
        self.server_awake = False
        Clock.schedule_once(self._ping_server, 1)

    def send_message(self):
        user_message = self.root.ids.user_input.text.strip()
        if not user_message:
            return

        self.pending_message = user_message
        self.retry_count = 0
        self.root.ids.user_input.text = ""

        self.add_chat_line(f"[b][color=5599ff]You:[/color][/b] {user_message}")
        self.add_chat_line("[b][color=aaaaaa]ARIA:[/color][/b] [i]Waking up server, please wait...[/i]")

        self._do_request()

    def _do_request(self):
        params = json.dumps({"message": self.pending_message})
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        UrlRequest(
            API_URL,
            on_success=self.handle_success,
            on_failure=self.handle_failure,
            on_error=self.handle_error,
            req_body=params,
            req_headers=headers,
            timeout=180
        )

    def handle_success(self, request, result):
        self.server_awake = True
        response_text = result.get("response", "No response.")
        self.replace_last_line(f"[b][color=00cc88]ARIA:[/color][/b] {response_text}")
        self.retry_count = 0

    def handle_failure(self, request, result):
        self._retry()

    def handle_error(self, request, error):
        self._retry()

    def _retry(self):
        self.retry_count += 1
        if self.retry_count < MAX_RETRIES:
            self.replace_last_line(f"[b][color=aaaaaa]ARIA:[/color][/b] [i]Retrying... (attempt {self.retry_count + 1}/{MAX_RETRIES})[/i]")
            Clock.schedule_once(lambda dt: self._do_request(), 20)
        else:
            self.replace_last_line("[b][color=ff4444]ARIA:[/color][/b] Server is sleeping. Please wait 30 seconds and try again.")
            self.retry_count = 0
            Clock.schedule_once(self._ping_server, 10)

    def add_chat_line(self, text):
        logs = self.root.ids.chat_logs
        logs.text += ("\n\n" if logs.text else "") + text
        self._scroll_bottom()

    def replace_last_line(self, new_text):
        logs = self.root.ids.chat_logs
        lines = logs.text.rsplit("\n\n", 1)
        logs.text = lines[0] + "\n\n" + new_text if len(lines) > 1 else new_text
        self._scroll_bottom()

    def _scroll_bottom(self):
        scroll = self.root.ids.chat_scroll
        Clock.schedule_once(lambda dt: setattr(scroll, 'scroll_y', 0), 0.1)

    def exit_app(self):
        import sys
        sys.exit(0)

if __name__ == "__main__":
    AriaApp().run()