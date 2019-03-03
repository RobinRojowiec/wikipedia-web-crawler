import json


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


def extract_wiki_page(url):
    return url.split("/")[-1]
