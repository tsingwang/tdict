from textual import events
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Static, Button

from .db import api as db_api
from .services import youdao


class DetailScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Static(self.app.word["word"], id="title")
        yield Static(youdao.format(self.app.explanation))

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            await self.app.next_word()
            self.app.pop_screen()


class TDictApp(App):

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-gutter: 2;
        padding: 2;
    }
    .info {
        width: 100%;
        height: 100%;
        column-span: 2;
        align: center bottom;
    }
    #word {
        text-style: bold;
        text-align: center;
    }
    #stats {
        text-align: center;
    }
    Button {
        width: 100%;
    }
    DetailScreen {
        layout: vertical;
    }
    DetailScreen > #title {
        padding-left: 2;
        text-style: bold;
    }
    DetailScreen > Static {
        border: solid #808080;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(Static(id="word"),
                       Static(id="stats"),
                       classes="info")
        yield Button("Yes", id="yes", variant="success")
        yield Button("No", id="no", variant="error")

    async def on_mount(self) -> None:
        self.word_generator = db_api.list_today_words()
        self.word = None
        self.explanation = None
        self.word_count = 0
        await self.next_word()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.word is None:
            db_api.append_review_history(self.word_count)
            return self.exit()
        if event.button.id == "yes":
            db_api.master_word(self.word["word"])
        elif event.button.id == "no":
            db_api.forget_word(self.word["word"])

        self.push_screen(DetailScreen())

        # NOTE: push_screen can not block, so move next_word action to DetailScreen
        # await self.next_word()

    async def next_word(self) -> None:
        try:
            self.word = next(self.word_generator)
        except StopIteration:
            self.word = None
            self.query_one("#word").update("Well done! Hope to see you tomorrow :)")
            self.query_one("#stats").update("")
            return

        stats = "REVIEW: {}  FORGET: {}".format(self.word["review_count"],
                                                self.word["forget_count"])
        self.query_one("#word").update(self.word["word"])
        self.query_one("#stats").update(stats)

        self.explanation = await youdao.query(self.word["word"])

        self.word_count += 1
