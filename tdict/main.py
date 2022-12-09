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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("word", nargs='?', help="The word to query.")
    parser.add_argument("-l", dest="list", nargs='?', const="0,20", help="List words.")
    parser.add_argument("-a", dest="add", help="Add word.")
    parser.add_argument("-d", dest="delete", help="Delete word.")
    args = parser.parse_args()

    if args.list:
        try:
            offset, limit = args.list.split(',')
        except ValueError:
            offset, limit = 0, int(args.list)
        print_word_list(offset=offset, limit=limit)
        return

    if args.add:
        db_api.add_word(args.add)
        return

    if args.delete:
        db_api.delete_word(args.delete)
        return

    if args.word:
        asyncio.run(query_word(args.word))
        return

    TDictApp().run()


if __name__ == '__main__':
    main()
