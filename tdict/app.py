from datetime import date

import click
from rich.markdown import Markdown
from textual import events, work
from textual.app import App, ComposeResult
from textual.containers import Vertical, Grid
from textual.screen import Screen, ModalScreen
from textual.widgets import Static, Button, Input, Header, Footer

from .db import api as db_api
from .profile import profile
from .services import youdao


class ExploreScreen(Screen):

    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        yield Grid(Input(placeholder="Search", id="search"),
                   Button("Add", id="add", variant="success"))
        yield Static(id="result")
        yield Footer()

    async def on_mount(self) -> None:
        self.query_one(Input).focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        word = event.value.strip()
        if word:
            w = db_api.query_word(word)
            result = "  REVIEW: {}  MASTER: {}  FORGET: {}\n".format(
                w["review_count"], w["master_count"], w["forget_count"]) if w else ''
            result += youdao.format(await youdao.query(word))
            self.query_one("#result").update(result)
            youdao.play_voice(word)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        word = self.query_one("#search").value.strip()
        if not word:
            return
        if event.button.id == "add":
            db_api.add_word(word)
            self.query_one("#search").value = ""
            self.query_one("#search").focus()


class SpellScreen(ModalScreen):

    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def __init__(self, word: str) -> None:
        super().__init__()
        self.word = word

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Try to spell")

    async def on_mount(self) -> None:
        self.query_one(Input).focus()

    async def on_input_changed(self, message: Input.Changed) -> None:
        # NOTE: Prevent my child from trying with the prompts
        #if self.word.lower().startswith(message.value.lower()):
        #    self.query_one(Input).styles.color = "green"
        #else:
        #    self.query_one(Input).styles.color = "red"
        self.query_one(Input).styles.color = "green"

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if self.word.lower() == event.value.lower():
            self.dismiss(True)
        else:
            self.query_one(Input).styles.color = "red"


class DetailScreen(Screen):

    BINDINGS = [
        ("e", "app.push_screen('explore')", "Explore"),
        ("D", "delete_word", "Delete"),
        ("p", "play_voice", "Pronounce"),
        ("n", "note", "Note"),
        ("enter", "next_word", "Enter"),
    ]

    def __init__(self, word: dict, explanation: dict) -> None:
        super().__init__()
        self.word = word
        self.explanation = explanation

    def compose(self) -> ComposeResult:
        yield Static(self.word["word"], id="title")
        yield Grid(Static(youdao.format(self.explanation), id="explanation"),
                   Static(Markdown(self.word["note"]), id="note"))
        yield Footer()

    async def on_mount(self) -> None:
        youdao.play_voice(self.word["word"])

    async def action_delete_word(self) -> None:
        db_api.delete_word(self.word["word"])
        self.dismiss(True)

    async def action_play_voice(self) -> None:
        youdao.play_voice(self.word["word"])

    async def action_note(self) -> None:
        self.app._driver.stop_application_mode()
        note = click.edit(self.word["note"])
        self.app._driver.start_application_mode()
        if note is not None:
            db_api.update_note(self.word["word"], note)
            self.word["note"] = note
            self.query_one("#note").update(Markdown(note))

    async def action_next_word(self) -> None:
        self.dismiss(True)


class MainScreen(Screen):

    BINDINGS = [
        ("e", "app.push_screen('explore')", "Explore"),
        ("D", "delete_word", "Delete"),
        ("p", "play_voice", "Pronounce"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(Static(id="word"),
                       Static(id="stats"),
                       classes="info")
        yield Button("Yes", id="yes", variant="success")
        yield Button("No", id="no", variant="error")
        yield Footer()

    async def on_mount(self) -> None:
        self.word_generator = db_api.list_today_words()
        self.word = None
        self.explanation = None
        r = db_api.get_review_history()
        self.total_master = r.get("total_master", 0) if r else 0
        self.total_forget = r.get("total_forget", 0) if r else 0
        await self.next_word()

    @work
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.word is None:
            return await self.app.action_quit()

        if event.button.id == "yes":
            if await self.app.push_screen_wait(SpellScreen(self.word["word"])):
                db_api.master_word(self.word["word"])
                self.total_master += 1
            else:
                return
        elif event.button.id == "no":
            db_api.forget_word(self.word["word"])
            self.total_forget += 1
            self.query_one("#yes").focus()

        await self.app.push_screen_wait(DetailScreen(self.word, self.explanation))
        await self.next_word()

    async def next_word(self) -> None:
        try:
            self.word = next(self.word_generator)
        except StopIteration:
            # Refresh today word list
            self.word_generator = db_api.list_today_words()
            try:
                self.word = next(self.word_generator)
            except StopIteration:
                self.word = None
                return self.show_today_summary()

        self.explanation = await youdao.query(self.word["word"])
        if len(self.explanation.get('explanation', [])) > 0:
            tips = '\n'.join(self.explanation['explanation'])
            self.query_one("#word").update('[green]' + tips)
        elif len(self.explanation.get('trans', [])) > 1:
            self.query_one("#word").update('[green]' + self.explanation['trans'][1])
        else:
            self.query_one("#word").update(self.word["word"])

        stats = "MASTER: {}  FORGET: {}".format(self.word["master_count"],
                                                self.word["forget_count"])
        self.query_one("#stats").update(stats)

        youdao.play_voice(self.word["word"])

    def show_today_summary(self) -> None:
        if self.total_master + self.total_forget == 0:
            self.query_one("#word").update("No schedule today, please add word.")
            return
        self.query_one("#word").update("Well done! See you tomorrow :)")
        summary = "Accuracy: {}/{} = {:.2f}%".format(
            self.total_master, self.total_master + self.total_forget,
            100 * self.total_master / (self.total_master + self.total_forget)
        )
        self.query_one("#stats").update(summary)

    async def action_delete_word(self) -> None:
        if self.word is not None:
            db_api.delete_word(self.word["word"])
            await self.next_word()

    async def action_play_voice(self) -> None:
        if self.word is not None:
            youdao.play_voice(self.word["word"])

    async def action_quit(self) -> None:
        db_api.update_review_history(self.total_master, self.total_forget)


class TDictApp(App):

    TITLE = "TDict ({})".format(profile.current_user)

    CSS_PATH = "tdict.tcss"

    SCREENS = {
        "main": MainScreen,
        "explore": ExploreScreen,
    }

    async def on_mount(self) -> None:
        self.push_screen("main")

    async def action_quit(self) -> None:
        """Override parent App method. Ctrl+C can be captured."""
        await self.get_screen("main").action_quit()
        self.exit()
