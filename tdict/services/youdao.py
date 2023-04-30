import os

import httpx
from lxml import html
from playsound import playsound


default_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
}


def is_chinese(word: str) -> bool:
    if '\u4e00' <= word[0] <= '\u9fff':
        return True
    return False


class Youdao:

    def __init__(self):
        self.session = httpx.AsyncClient()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Without this, there will be a ResourceWarning
        await self.session.aclose()

    async def query(self, word: str) -> dict:
        url = 'https://dict.youdao.com/w/' + word
        r = await self.session.get(url, headers=default_headers)
        tree = html.fromstring(r.text)
        if is_chinese(word):
            return {'trans': self._parse_chinese(tree)}
        return {
            'hints': self._parse_hints(tree),
            'pronounce': self._parse_pronounce(tree),
            'explanation': self._parse_explanation(tree),
            'related': self._parse_related(tree),
            'phrases': self._parse_phrases(tree),
            'sentences': self._parse_sentences(tree),
            'trans': self._parse_trans(tree),
        }

    @classmethod
    def format(cls, result: dict) -> str:
        res = []
        if result.get('hints', None):
            res.append('  [not b]404: not found')
            for item in result['hints']:
                res.append('  [green][not b]' + item)
        if result.get('trans', None):
            res.append('')
            for item in result['trans']:
                res.append('  [green][not b]' + item)
        if result.get('pronounce', None):
            res.append('')
            res.append('  [green][not b]' + result['pronounce'].replace('[', '\['))
        if result.get('explanation', None):
            res.append('')
            for item in result['explanation']:
                res.append('  [green][not b]' + item)
        if result.get('related', None):
            res.append('')
            for item in result['related']:
                res.append('  [green][not b]' + item)
        if result.get('phrases', None):
            res.append('')
            for item in result['phrases']:
                phrase, trans = item.rsplit(' ', 1)
                res.append('  [blue][b]' + phrase + ' [green][not b]' + trans)
        if result.get('sentences', None):
            res.append('')
            for item in result['sentences']:
                res.append('  [green][not b]' + item['orig'])
                res.append('  [magenta][not b]' + item['trans'])
        res.append('')
        return '\n'.join(res)

    def _parse_pronounce(self, tree):
        query = tree.cssselect('div.baav')
        if len(query) > 0:
            return ' '.join(query[0].text_content().split())
        return ''

    def _parse_explanation(self, tree):
        res = []
        query = tree.cssselect('div#phrsListTab')
        if len(query) > 0:
            for li in query[0].cssselect('li'):
                res.append(' '.join(li.text_content().split()))
            for p in query[0].cssselect('p.additional'):
                res.append(' '.join(p.text_content().split()))
        return res

    def _parse_related(self, tree):
        res = []
        query = tree.cssselect('div#relWordTab')
        if len(query) > 0:
            for p in query[0].getchildren():
                res.append(' '.join(p.text_content().split()))
        return res

    def _parse_phrases(self, tree):
        res = []
        query = tree.cssselect('div#wordGroup')
        if len(query) > 0:
            for p in query[0].getchildren():
                res.append(' '.join(p.text_content().split()))
        return res[:5]

    def _parse_sentences(self, tree):
        res = []
        query = tree.cssselect('div#bilingual')
        if len(query) > 0:
            for li in query[0].cssselect('li'):
                orig = ' '.join(li.getchildren()[0].text_content().split())
                trans = ' '.join(li.getchildren()[1].text_content().split())
                res.append({'orig': orig, 'trans': trans})
        return res

    def _parse_hints(self, tree):
        res = []
        query = tree.cssselect('div.error-typo')
        if len(query) > 0:
            for p in query[0].cssselect('p'):
                res.append(' '.join(p.text_content().split()))
        return res

    def _parse_trans(self, tree):
        res = []
        query = tree.cssselect('div#fanyiToggle')
        if len(query) > 0:
            for p in query[0].cssselect('p'):
                res.append(' '.join(p.text_content().split()))
        return res

    def _parse_chinese(self, tree):
        res = []
        query = tree.cssselect('div#phrsListTab')
        if len(query) > 0:
            for p in query[0].cssselect('p.wordGroup'):
                res.append(' '.join(p.text_content().split()))
        res += self._parse_trans(tree)
        return res

    @classmethod
    def play_voice(cls, word: str) -> str:
        if os.environ.get("TDICT_VOICE_ENABLE", "0").lower() in ("true", "1",):
            url = 'https://dict.youdao.com/dictvoice?audio={}&type=2'.format(word)
            playsound(url, block=False)


youdao = Youdao()
