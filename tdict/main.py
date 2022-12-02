import argparse
import asyncio

from rich import print
from rich.table import Table

from tdict.app import TDictApp
from tdict.db import api as db_api
from tdict.services import Youdao


async def query_word(word: str) -> None:
    async with Youdao() as youdao:
        result = await youdao.query(word)
        print(youdao.format(result))


def print_word_list() -> None:
    table = Table(box=None)
    table.add_column("SCHEDULE", justify="right")
    table.add_column("WORD", justify="right", style="green bold")
    table.add_column("REVIEW", justify="right")
    table.add_column("MASTER", justify="right")
    table.add_column("FORGET", justify="right", style="red")
    for w in db_api.list_words():
        table.add_row(str(w["schedule_day"]), w["word"],
                      str(w["review_count"]), str(w["master_count"]),
                      str(w["forget_count"]),)
    print(table)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("word", nargs='?', help="The word to query.")
    parser.add_argument("-l", "--list", action="store_true", help="List words.")
    parser.add_argument("-a", "--add", action="store_true", help="Add word.")
    parser.add_argument("-d", "--delete", action="store_true", help="Delete word.")
    args = parser.parse_args()

    if args.list:
        print_word_list()
        return

    if args.add:
        db_api.add_word(args.word)
        return

    if args.delete:
        db_api.delete_word(args.word)
        return

    if args.word:
        asyncio.run(query_word(args.word))
        return

    TDictApp().run()


if __name__ == '__main__':
    main()
