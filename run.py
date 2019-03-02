# /bin/sh

import argparse
import glob
import os

from tqdm import tqdm

from wikipedia_crawler import WikipediaCrawler

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('depth', help='depth of crawling', type=int)
parser.add_argument('--source_url', dest="source", help='source url to crawl (if not given, sources.txt is used)',
                    type=str, default=None)
parser.add_argument('--clean', dest="clean", help='removes all stored pages before crawling', type=bool, default=False)
parser.add_argument('--dir', dest="directory", help='directory to store pages', type=str, default="corpus")
args = parser.parse_args()

if args.clean:
    files = glob.glob(args.directory + "/*")
    for f in files:
        os.remove(f)

if args.source is None:
    sources = []
    with open("sources.txt", "r", encoding='utf-8') as source_file:
        for line in tqdm(source_file):
            sources.append(line.strip("\n"))
else:
    sources = [args.source]

crawler = WikipediaCrawler(args.directory, args.depth)
for source_url in sources:
    pages = crawler.crawl(source_url)
