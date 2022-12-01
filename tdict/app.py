from textual.app import App, ComposeResult
from textual.widgets import Static, Button

from tdict.db import api as db_api


class TDictApp(App):
    CSS_PATH = "tdict.css"

    def compose(self) -> ComposeResult:
        yield Static(id="word")
        yield Button("Yes", id="yes", variant="primary")
        yield Button("No", id="no", variant="error")

    def on_mount(self) -> None:
        self.word_generator = db_api.list_today_words()
        self.word = None
        self.next_word()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            db_api.master_word(self.word["word"])
        elif event.button.id == "no":
            db_api.forget_word(self.word["word"])
        self.next_word()

    def next_word(self) -> None:
        self.word = next(self.word_generator)
        self.query_one("#word").update(self.word["word"])
