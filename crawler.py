# /bin/sh
import ssl
from urllib.request import urlopen

from wikipedia_page import WikipediaPage

# first, read source URLs from file
sources = []
with open("sources.txt", "r", encoding="utf8") as source_file:
    for line in source_file:
        sources.append(line.strip("\n"))

# second, download page, extract data and store it in corpus folder
context = ssl.create_default_context()


def download_page(url):
    """
    Returns HTML Content of page
    :param url:
    :return:
    """
    return urlopen(url, context=context).read()


directory = "corpus"
for source_url in sources:
    try:
        page_content = download_page(source_url)
        page = WikipediaPage.parse(page_content)
        page.store(directory)
    except Exception as ex:
        print(ex)
        print("Couldn't download and parse page: " + source_url)
