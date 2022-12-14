from textual import events
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button

from tdict.db import api as db_api
from tdict.services import youdao


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
    #word {
        width: 100%;
        height: 100%;
        column-span: 2;
        content-align: center bottom;
        text-style: bold;
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
        yield Static(id="word")
        yield Button("Yes", id="yes", variant="primary")
        yield Button("No", id="no", variant="error")

    async def on_mount(self) -> None:
        self.word_generator = db_api.list_today_words()
        self.word = None
        self.explanation = None
        await self.next_word()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.word is None:
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
            return
        self.query_one("#word").update(self.word["word"])
        self.explanation = await youdao.query(self.word["word"])
