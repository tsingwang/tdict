import argparse
import asyncio

from tdict.db import api as db_api
from tdict.services import youdao


async def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("word", nargs='?', help="The word to query.")
    parser.add_argument("-l", "--list", action="store_true", help="List words.")
    parser.add_argument("-a", "--add", action="store_true", help="Add word.")
    parser.add_argument("-d", "--delete", action="store_true", help="Delete word.")
    args = parser.parse_args()

    if args.list:
        db_api.list_words()
        return

    if args.add:
        db_api.add_word(args.word)
        return

    if args.delete:
        db_api.delete_word(args.word)
        return

    result = await youdao.fetch_word(args.word)
    youdao.print(result)


def main():
    asyncio.run(_main())


if __name__ == '__main__':
    main()
