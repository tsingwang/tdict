import argparse
import asyncio

from rich import print
from rich.columns import Columns

from tdict.app import TDictApp
from tdict.db import api as db_api
from tdict.services import youdao


async def query_word(word):
    result = await youdao.query(word)
    print(youdao.format(result))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("word", nargs='?', help="The word to query.")
    parser.add_argument("-l", "--list", action="store_true", help="List words.")
    parser.add_argument("-a", "--add", action="store_true", help="Add word.")
    parser.add_argument("-d", "--delete", action="store_true", help="Delete word.")
    args = parser.parse_args()

    if args.list:
        words = ['[green]' + w['word'] for w in db_api.list_words()]
        print(Columns(words))
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
