import copy
import json
import re
import ssl
from urllib.request import urlopen

from bs4 import BeautifulSoup
from tqdm import tqdm


class WikipediaParser:
    def __init__(self):
        self.wiki_page_link_pattern = re.compile("/wiki/[\w]+$")
        self.category_link_pattern = re.compile("https://en.wikipedia.org/wiki/Category:[\w]+")
        self.base_url = "https://en.wikipedia.org"

        # second, download page, extract data and store it in corpus folder
        self.ssl_context = ssl.create_default_context()
        self.max_depth = 1
        self.max_pages = 200

    def download_page(self, url):
        """
        Returns HTML Content of page
        :param url:
        :return:
        """
        return urlopen(url, context=self.ssl_context).read().decode('utf-8')

    def parse_category(self, url):
        page_content = self.download_page(url)
        soup = BeautifulSoup(page_content, 'lxml')

        pages = []
        links = list(filter(lambda x: x.get('href') != None and self.wiki_page_link_pattern.match(x.get('href')),
                            soup.find_all('a')))
        for link in tqdm(links):
            url = link.get('href')
            pages.append(self.parse_page(self.base_url + url))

        return pages

    def parse_page(self, url):
        page_content = self.download_page(url)
        soup = BeautifulSoup(page_content, 'lxml')
        page = WikipediaPage()

        # extract wikipedia links
        links = soup.find_all('a')
        for link in links:
            if link.get('href') is not None and self.wiki_page_link_pattern.match(link.get('href')):
                page.links.append(link.get('href'))

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

        page.title = soup.find(id="firstHeading").string
        page.html = str(soup)

        return page

    def parse(self, initial_link):
        if self.category_link_pattern.match(initial_link):
            return self.parse_category(initial_link)
        else:
            return [self.parse_page(initial_link)]


class WikipediaPage:
    def __init__(self):
        """
        a wrapper for wikipedia page content
        """
        self.title = []
        self.html = ""
        self.table_of_contents = []
        self.graphics = []
        self.paragraphs = []
        self.links = []

    def store(self, directory):
        file_name = self.title.replace(" ", "_")
        with open(directory + "/" + file_name + '.json', 'w+', encoding='utf-8') as file:
            fields = self.__dict__
            json.dump(fields, file, indent=4, ensure_ascii=False)
