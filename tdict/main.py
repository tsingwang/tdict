import argparse
import asyncio

from rich.console import Console

from services import youdao


def show(result):
    console = Console()
    if len(result.get('hints', [])) > 0:
        console.print('    [not b]404: not found')
        for item in result['hints']:
            console.print('    [green][not b]' + item)
    if result.get('pronounce', None):
        console.print()
        console.print('    [green][not b]' + result['pronounce'].replace('[', '\['))
    if result.get('explanation', None):
        console.print()
        for item in result['explanation']:
            console.print('    [green][not b]' + item)
    if result.get('related', None):
        console.print()
        for item in result['related']:
            console.print('    [green][not b]' + item)
    if result.get('phrases', None):
        console.print()
        for item in result['phrases']:
            phrase, trans = item.rsplit(' ', 1)
            console.print('    [blue][b]' + phrase + ' [green][not b]' + trans)
    if result.get('sentences', None):
        console.print()
        for item in result['sentences']:
            console.print('    [green][not b]' + item['orig'])
            console.print('    [magenta][not b]' + item['trans'])


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("word", help="The word to query.")
    args = parser.parse_args()
    result = await youdao.fetch_word(args.word)
    show(result)


if __name__ == '__main__':
    asyncio.run(main())
