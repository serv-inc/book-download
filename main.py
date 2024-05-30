"""load web novel single pages"""
import os
import random
import time
from dataclasses import dataclass

import cloudscraper
from bs4 import BeautifulSoup


scraper = cloudscraper.create_scraper()

HOST = "https://readnovelfull.com"


@dataclass
class SinglePage:
    """a single page"""

    path: str
    text: str = ""

    @property
    def content(self) -> BeautifulSoup:
        assert self.text, "need to load() first"
        return BeautifulSoup(self.text)

    @property
    def nextpath(self):
        """the path of the next page"""
        return self.content.find(id="next_chap").get("href")

    def next_page(self, reload=5):
        """@return the following page"""
        assert self.nextpath, "no next path in " + self.text
        while reload > 0 and not self.nextpath:
            self.load()
            reload -= 1
        return SinglePage(self.nextpath)

    def load(self):
        """load page from novel site"""
        assert self.path.startswith("/")
        response = scraper.get("https://readnovelfull.com" + self.path)
        assert response.status_code < 400
        self.text = response.text

    def save(self, prefix="/tmp"):
        """save page to disk"""
        assert self.text
        try:
            os.mkdir(os.path.dirname(prefix + self.path))
        except FileExistsError:
            pass
        with open(prefix + self.path, "w", encoding="utf-8") as out:
            out.write(self.text)


def do(previous, count=20, delay=0.1, dot=False):
    """load and save count number of pages, with a delay"""
    current = previous
    while count > 0:
        current = current.next_page()
        time.sleep(random.random() * delay)
        try:
            current.load()
        except AttributeError:
            print("error loading nextpath for " + previous.path)
            return current
        current.save()
        count -= 1
        if dot:
            print(".", end="")
    return current
