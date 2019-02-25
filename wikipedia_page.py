import copy
import json

from bs4 import BeautifulSoup


class WikipediaPage:
    def __init__(self):
        """
        a wrapper for wikipedia page content
        """
        self.title = []
        self.full_html = ""
        self.table_of_contents = []
        self.graphics = []
        self.paragraphs = []
        self.links = []

    @staticmethod
    def parse(page_content):
        page = WikipediaPage()
        soup = BeautifulSoup(page_content, 'lxml', from_encoding="utf8")

        # extract wikipedia links
        links = soup.find_all('a')
        for link in links:
            if link.get('href') is not None and link.get('href').startswith("/"):
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
                current_paragraph["title"] = child.text

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

        page.title = soup.find(id="firstHeading").string
        page.table_of_contents = list(filter(lambda x: x != "", soup.find(id="toc").text.split("\n")[1:]))
        page.full_html = soup.prettify()

        return page

    def store(self, directory):
        file_name = self.title.replace(" ", "_")
        with open(directory + "/" + file_name + '.json', 'w+') as file:
            json.dump(self.__dict__, file, indent=4, sort_keys=True)
