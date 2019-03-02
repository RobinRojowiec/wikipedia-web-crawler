import os

import jsonpickle
from flask import Flask, request

from wikipedia import WikipediaCrawler

app = Flask(__name__)


@app.route('/crawl')
def analyze():
    url: "" = request.args.get('url')
    depth: int = int(request.args.get('depth'))

    crawler: WikipediaCrawler = WikipediaCrawler("corpus", depth)
    pages = crawler.parse(url)

    json = jsonpickle.encode(pages)

    return json


if __name__ == '__main__':
    port = os.getenv("PORT", 3330)
    app.run(debug=False, host='0.0.0.0', port=port)
