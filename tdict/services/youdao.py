import httpx
from lxml import html


default_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
}


def is_chinese(word):
    if '\u4e00' <= word[0] <= '\u9fff':
        return True
    return False


class Youdao:

    def __init__(self):
        self.session = httpx.AsyncClient()

    async def fetch_word(self, word):
        url = 'https://dict.youdao.com/w/' + word
        r = await self.session.get(url, headers=default_headers)
        tree = html.fromstring(r.text)
        if is_chinese(word):
            return {}
        hints = self._parse_hints(tree)
        if len(hints) > 0:
            return {'hints': hints}
        return {
            'pronounce': self._parse_pronounce(tree),
            'explanation': self._parse_explanation(tree),
            'related': self._parse_related(tree),
            'phrases': self._parse_phrases(tree),
            'sentences': self._parse_sentences(tree),
        }

    def _parse_pronounce(self, tree):
        div = tree.cssselect('div.baav')[0]
        return ' '.join(div.text_content().split())

    def _parse_explanation(self, tree):
        res = []
        div = tree.cssselect('div.trans-container')[0]
        for li in div.getchildren()[0].getchildren():
            res.append(li.text)
        if len(div.getchildren()) > 1:
            p = div.getchildren()[1]
            res.append(' '.join(p.text.split()))
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
        div = tree.cssselect('div#bilingual')[0]
        for li in div.cssselect('li'):
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


youdao = Youdao()
