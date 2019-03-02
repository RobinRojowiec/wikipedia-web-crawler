import glob
import os

import jsonpickle
from flask import Flask, request, Response

from wikipedia_crawler import WikipediaCrawler, extract_wiki_page

app = Flask(__name__)
directory = "corpus"


@app.route('/clear')
def clear_corpus():
    files = glob.glob(directory + "/*")
    for f in files:
        os.remove(f)

    return "Done!"


@app.route('/crawl')
def analyze():
    host = "https://en.wikipedia.org/wiki/"
    wiki_page: str = request.args.get('wiki_page')
    if wiki_page is None:
        url: str = request.args.get('url')
        wiki_page = extract_wiki_page(url)
    else:
        url: "" = host + wiki_page
    depth: int = request.args.get('depth', 0, int)

    crawler: WikipediaCrawler = WikipediaCrawler("corpus", depth)
    pages = crawler.crawl(url)

    json_string = jsonpickle.encode(pages, unpicklable=False)

    return Response(json_string,
                    mimetype='application/json',
                    headers={'Content-Disposition': 'attachment;filename=crawl_' + wiki_page + '.json'})


if __name__ == '__main__':
    port = os.getenv("PORT", 3330)
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
