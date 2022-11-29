import argparse
import asyncio

from tdict.services import youdao


async def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("word", help="The word to query.")
    args = parser.parse_args()
    result = await youdao.fetch_word(args.word)
    youdao.print(result)


def main():
    asyncio.run(_main())


if __name__ == '__main__':
    main()
