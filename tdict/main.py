import argparse
import asyncio

from rich import print
from rich.panel import Panel
from rich.table import Table

from ._loop import loop_first_last
from .app import TDictApp
from .db import api as db_api
from .services import Youdao


async def query_word(word: str) -> None:
    async with Youdao() as youdao:
        result = await youdao.query(word)
        print(youdao.format(result))
    w = db_api.query_word(word)
    if w:
        print("  REVIEW: {}  FORGET: {}".format(
            w["review_count"], w["forget_count"]))


def print_word_list(offset: int = 0, limit: int = 20) -> None:
    table = Table(box=None)
    table.add_column("SCHEDULE", justify="right")
    table.add_column("WORD", justify="right", style="green bold")
    table.add_column("REVIEW", justify="right")
    table.add_column("MASTER", justify="right")
    table.add_column("FORGET", justify="right", style="red")
    for w in db_api.list_words(offset=offset, limit=limit):
        table.add_row(str(w["schedule_day"]), w["word"],
                      str(w["review_count"]), str(w["master_count"]),
                      str(w["forget_count"]),)
    print(table)


def show_review_history(year: str) -> None:
    total_days, reviewed_days, reviewed_words = 0, 0, 0
    lines = [[] for i in range(7)]
    n = 0
    for first, last, (date, word_count) in loop_first_last(
            db_api.list_review_history(year).items()):
        if first:
            while n < date.weekday():
                lines[n].append("~~")
                n += 1

        total_days += 1
        if word_count > 0:
            reviewed_days += 1
            reviewed_words += word_count
            lines[n].append("[r]  [/]")
        else:
            lines[n].append("  ")

        if last:
            while n < 6:
                n += 1
                lines[n].append("~~")

        n = n + 1 if n < 6 else 0

    title = f"Word Review in {year}" if year else "Word Review in last year"
    subtitle = "Review Rate: {:.2f}% ({}/{})  Avg words/day: {:.2f}".format(
            100 * reviewed_days / total_days, reviewed_days, total_days,
            reviewed_words / total_days)
    content = "\n".join(["".join(line) for line in lines])
    print(Panel.fit(content, title=title, subtitle=subtitle))


def show_review_schedule() -> None:
    table = Table(title="SCHEDULE", box=None)
    row = []
    for month, count in db_api.get_review_schedule():
        table.add_column(month, justify="right")
        row.append(count)
    row.append(sum(row))
    row = [str(v) for v in row]
    table.add_column("TOTAL", justify="right", style="green bold")
    table.add_row(*row)
    print(table)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("word", nargs='?', help="The word to query.")
    parser.add_argument("-l", dest="list", nargs='?', const="0,20", help="List words.")
    parser.add_argument("-a", dest="add", help="Add word.")
    parser.add_argument("-d", dest="delete", help="Delete word.")
    parser.add_argument("-s", "--summary", action="store_true", help="Summary.")
    parser.add_argument("-y", dest="year", type=int, help="Depend on summary.")
    args = parser.parse_args()

    if args.list:
        try:
            offset, limit = args.list.split(',')
        except ValueError:
            offset, limit = 0, int(args.list)
        print_word_list(offset=offset, limit=limit)
    elif args.add:
        db_api.add_word(args.add)
    elif args.delete:
        db_api.delete_word(args.delete)
    elif args.word:
        asyncio.run(query_word(args.word))
        Youdao.play_voice(args.word, block=True)
    elif args.summary:
        show_review_history(args.year)
        show_review_schedule()
    else:
        TDictApp().run()


if __name__ == '__main__':
    main()
