import os
from datetime import date

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.screen import Screen, ModalScreen
from textual.widgets import Static, Button, Input

from .db import api as db_api
from .services import youdao


class SpellScreen(ModalScreen):

    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Try to spell")

    async def on_mount(self) -> None:
        self.query_one(Input).focus()

    async def on_input_changed(self, message: Input.Changed) -> None:
        if self.app.word["word"].lower().startswith(message.value.lower()):
            self.query_one(Input).styles.color = "green"
        else:
            self.query_one(Input).styles.color = "red"

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if self.app.word["word"].lower() == event.value.lower():
            db_api.master_word(self.app.word["word"])
            self.app.pop_screen()
            self.app.push_screen(DetailScreen())
        else:
            self.query_one(Input).styles.color = "red"


class DetailScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Static(self.app.word["word"], id="title")
        yield Static(youdao.format(self.app.explanation))

    async def on_mount(self) -> None:
        youdao.play_voice(self.app.word["word"])

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.app.pop_screen()
            await self.app.next_word()
        elif event.key == "d":
            db_api.delete_word(self.app.word["word"])
            self.app.pop_screen()
            await self.app.next_word()
        elif event.key == "n":
            # Add a forget option
            word = db_api.query_word(self.app.word["word"])
            if word["schedule_day"] > date.today():
                db_api.forget_word(self.app.word["word"])
            self.app.pop_screen()
            await self.app.next_word()
        elif event.key == "p":
            youdao.play_voice(self.app.word["word"])


class TDictApp(App):

    CSS_PATH = "tdict.tcss"

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

    async def on_key(self, event: events.Key) -> None:
        if self.word is not None:
            if event.key == "d":
                db_api.delete_word(self.word["word"])
                await self.next_word()
            elif event.key == "p":
                youdao.play_voice(self.word["word"])

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.word is None:
            return await self.action_quit()

        if event.button.id == "yes":
            if os.environ.get("TDICT_SPELL_ENABLE", "0").lower() in ("true", "1",):
                self.push_screen(SpellScreen())
                return
            else:
                db_api.master_word(self.word["word"])
        elif event.button.id == "no":
            db_api.forget_word(self.word["word"])

        self.push_screen(DetailScreen())

        # NOTE: push_screen can not block, so move next_word action to DetailScreen
        # await self.next_word()

    async def next_word(self) -> None:
        try:
            self.word = next(self.word_generator)
            self.word_count += 1
        except StopIteration:
            self.word = None
            self.query_one("#word").update("Well done! Hope to see you tomorrow :)")
            self.query_one("#stats").update("")
            return

        self.explanation = await youdao.query(self.word["word"])
        if len(self.explanation.get('explanation', [])) > 0:
            tips = '\n'.join(self.explanation['explanation'])
            self.query_one("#word").update('[green]' + tips)
        else:
            self.query_one("#word").update(self.word["word"])

        stats = "MASTER: {}  FORGET: {}".format(self.word["master_count"],
                                                self.word["forget_count"])
        self.query_one("#stats").update(stats)

        youdao.play_voice(self.word["word"])

    async def action_quit(self) -> None:
        """Override parent App method. Ctrl+C can be captured."""
        db_api.append_review_history(self.word_count)
        self.exit()
