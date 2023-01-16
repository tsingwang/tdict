import argparse
import asyncio

from rich import print
from rich.panel import Panel
from rich.table import Table

from tdict.app import TDictApp
from tdict.db import api as db_api
from tdict.services import Youdao


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
    i = 0
    for date, word_count in db_api.list_review_history(year).items():
        total_days += 1
        if word_count > 0:
            reviewed_days += 1
            reviewed_words += word_count
            lines[i].append("[r]  [/r]")
        else:
            lines[i].append("  ")
        i = i + 1 if i < 6 else 0

    if year:
        title = f"Word Review in {year}"
    else:
        title = "Word Review in last year"
    subtitle = "Review Rate: {:.2f}%  Avg words/day: {:.2f}".format(
            reviewed_days/total_days, reviewed_words/total_days)
    content = "\n".join(["".join(line) for line in lines])
    print(Panel.fit(content, title=title, subtitle=subtitle))


def show_review_progress() -> None:
    total = 0
    for month, count in db_api.query_review_progress():
        print(f"{month} {count}")
        total += count
    print(f" Total: {total}")


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
    elif args.summary:
        show_review_history(args.year)
        show_review_progress()
    else:
        TDictApp().run()


if __name__ == '__main__':
    main()
