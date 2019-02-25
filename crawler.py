# /bin/sh

from tqdm import tqdm

from wikipedia import WikipediaParser

# first, read source URLs from file
sources = []
with open("sources.txt", "r", encoding="utf8") as source_file:
    for line in tqdm(source_file):
        sources.append(line.strip("\n"))


directory = "corpus"
parser = WikipediaParser()
for source_url in sources:
    pages = parser.parse(source_url)
