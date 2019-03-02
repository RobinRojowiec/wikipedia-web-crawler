import copy
import json
import re
import ssl
from urllib.parse import urlparse
from urllib.request import urlopen

from bs4 import BeautifulSoup


class WikipediaCrawler:
    def __init__(self, directory, max_depth):
        self.wiki_page_link_pattern = re.compile("/wiki/[\w]+$")
        self.category_link_pattern = re.compile("/wiki/Category:[\w]+$")

        self.ssl_context = ssl.create_default_context()
        self.max_depth = max_depth
        self.store_after_parsing = True
        self.directory = directory
        self.crawled_pages = set()
        self.valid_origins = ["https://en.wikipedia.org"]

    def register_page(self, url):
        """
        register a page in the local registry
        :param url:
        :return:
        """
        if not url in self.crawled_pages:
            self.crawled_pages.add(url)
            return True
        else:
            return False

    def download_page(self, url):
        """
        Returns HTML Content of page
        :param url:
        :return:
        """
        try:
            if self.register_page(url):
                print("Downloading page: ", url)
                return urlopen(url, context=self.ssl_context).read().decode('utf-8')
        except Exception as ex:
            print("Failed to download page", ex)
        return None

    def parse_category(self, url, depth):
        """
        Collects the links from a category and downloads/parses them
        :param url:
        :param depth:
        :return:
        """
        page_content = self.download_page(url)
        if page_content is None:
            return []

        base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url))
        soup = BeautifulSoup(page_content, 'lxml')

        pages = []
        links = list(filter(lambda x: x.get('href') is not None, soup.find_all('a')))
        for link in links:
            url = link.get('href')
            pages.extend(self.parse(base_url + url, depth + 1))

        return pages

    def parse_page(self, url, depth=0):
        """
        Downloads and parses a Wikipedia page and stores it if required
        :param url:
        :return:
        """
        print("Parsing page: ", url)
        page_content = self.download_page(url)
        if page_content is None:
            return []

        soup = BeautifulSoup(page_content, 'lxml')
        pages = []
        page = WikipediaPage(url)

        # extract wikipedia links
        links = soup.find_all('a')
        for link in links:
            link_url = link.get('href')
            if link_url is not None:
                if self.wiki_page_link_pattern.match(link_url):
                    base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url))
                    page.links.append(base_url + link_url)
                    pages.extend(self.parse(base_url + link_url, depth + 1))

        # extract paragraphs
        text_container = soup.find('div', {'class': 'mw-parser-output'})
        zero_paragaph = {"title": "", "text": ""}

        current_paragraph = copy.deepcopy(zero_paragaph)
        for child in text_container.children:
            if child.name == "p":
                current_paragraph["text"] += child.text + "\n"
            elif child.name == "h2":
                page.paragraphs.append(current_paragraph)
                current_paragraph = copy.deepcopy(zero_paragaph)
                current_paragraph["title"] = next(child.children).text

        page.paragraphs = list(filter(lambda x: x["text"] != "", page.paragraphs))

        # extract graphics
        image_container = soup.find_all('div', {'class': 'thumbinner'})
        zero_graphic = {"url": "", "caption": ""}

        for image in image_container:
            current_graphic = copy.deepcopy(zero_graphic)

            for child in image.children:
                if child.name == "a":
                    current_graphic["url"] = child.get('href')

                elif child.name == "div":
                    current_graphic["caption"] = child.text

            page.graphics.append(current_graphic)

        toc_element = soup.find(id="toc")
        if toc_element is not None:
            page.table_of_contents = list(filter(lambda x: x != "", toc_element.text.split("\n")[1:]))

        page.title = soup.find(id="firstHeading").text
        page.html = str(soup)

        if self.store_after_parsing:
            page.store(self.directory)
        pages.append(page)
        return pages

    def parse(self, initial_link, depth=0):
        if depth <= self.max_depth:
            base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(initial_link))
            if base_url in self.valid_origins:
                if self.category_link_pattern.match(initial_link[len(base_url):]):
                    return self.parse_category(initial_link, depth)
                elif self.wiki_page_link_pattern.match(initial_link[len(base_url):]):
                    return self.parse_page(initial_link, depth)
        return []


class WikipediaPage:
    def __init__(self, url):
        """
        a wrapper for wikipedia page content
        """
        self.url = url
        self.title = []
        self.html = ""
        self.table_of_contents = []
        self.graphics = []
        self.paragraphs = []
        self.links = []

    def store(self, directory):
        """
        Save the page content in JSON format
        :param directory:
        :return:
        """
        file_name = self.title.replace(" ", "_")
        with open(directory + "/" + file_name + '.json', 'w+', encoding='utf-8') as file:
            fields = self.__dict__
            json.dump(fields, file, indent=4, ensure_ascii=False)

    @staticmethod
    def load(self, filename):
        with open(filename, "r", encoding='utf-8') as file:
            self.__dict__ = json.load(file)
