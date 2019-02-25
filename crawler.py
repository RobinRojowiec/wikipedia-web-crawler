# /bin/sh

from wikipedia import WikipediaParser

# first, read source URLs from file
sources = []
with open("sources.txt", "r", encoding="utf8") as source_file:
    for line in source_file:
        sources.append(line.strip("\n"))


directory = "corpus"
parser = WikipediaParser()
for source_url in sources:
    # try:
    pages = parser.parse(source_url)
    for page in pages:
        page.store(directory)
# except Exception as ex:
#    print(ex)
#    print("Couldn't download and parse page: " + source_url)
