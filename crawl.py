from bs4 import BeautifulSoup
import requests
import re
import time
import pickle

class Crawler():
    def __init__(self, base):
        base = re.sub('%', '/', base)
        base = re.sub(';', ':', base)
        self.base = base
        if not self.base[-1] == '/':
            self.base += '/'
        self.source = None
        self.pages = list()
        self.content = None

    def get(self, url: str):
        if re.match(self.base, url):
            self.url = url
        else:
            self.url = self.base + url
        res = requests.get(self.url)
        self.source = BeautifulSoup(res.content, 'html5lib')

        return self

    def crawl(self, base: str=None, depth: int=None) -> list:
        if base is None:
            base = self.base

        self.get(base)
        pages = self._get_pages(self.source)
        self.pages += pages

        if depth < 1:
            return self.pages

        step = 0
        while True:
            next_pages = list()
            for page in pages:
                self.get(page)
                next_pages += self._get_pages(self.source)
            next_pages = list(set(next_pages))
            pages = [page for page in next_pages if not page in self.pages]

            step += 1
            self.pages += pages
            time.sleep(3)

            if depth is None:
                if not pages:
                    break
            else:
                if step >= depth or not pages:
                    break

        return self.pages

    def _get_pages(self, source: BeautifulSoup):
        raw_pages = source.find_all('a')
        raw_pages = list(set([page.get('href') for page in raw_pages]))

        pages = []
        for url in raw_pages:
            if re.match('http', url):
                if re.match(r'{}'.format(self.base), url):
                    pages.append(url)
            elif re.match(r'.', url):
                splited = url.split('/')
                count = 0
                for section in splited:
                    if re.match(r'..', section):
                        count += 1
                relative = re.sub('\.+/', '', url)
                url = ''.join(splited[:-count]) + relative

        return pages

if __name__ == "__main__":
    crawler = Crawler('https://yuta0306.github.io/blog/')
    pages = crawler.crawl()
    with open('pages.pkl', 'wb') as f:
        pickle.dump(pages, f)
        