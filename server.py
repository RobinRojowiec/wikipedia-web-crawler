import glob
import os
import uuid

import jsonpickle
from flask import Flask, request, send_file

from wikipedia_crawler import WikipediaCrawler
from wikipedia_page import extract_wiki_page

app = Flask(__name__)
directory = "data"
file_limit = 50

if not os.path.exists(directory):
    os.makedirs(directory)


@app.route('/clear')
def clear_corpus():
    print("clearing temporary files")
    files = glob.glob(directory + "/*")
    for f in files:
        os.remove(f)

    return "Done!"


def filecount(dir_name):
    file_list = [f for f in os.listdir(dir_name)]
    return len(file_list)


def check_and_clear():
    if filecount(directory + "/") > file_limit:
        clear_corpus()


@app.route('/download/<id>')
def download(id):
    file_path = directory + "/" + id + ".json"
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, attachment_filename=id + ".json", mimetype="application/json")


@app.route('/crawl')
def analyze():
    check_and_clear()

    host = "https://en.wikipedia.org/wiki/"
    wiki_page: str = request.args.get('wiki_page')
    if wiki_page is None:
        url: str = request.args.get('url')
        wiki_page = extract_wiki_page(url)
    else:
        url: "" = host + wiki_page
    depth: int = request.args.get('depth', 0, int)

    crawler: WikipediaCrawler = WikipediaCrawler(directory, depth)
    pages = crawler.crawl(url)

    json_string = jsonpickle.encode(pages, unpicklable=False)
    id = str(uuid.uuid4())
    file_path = directory + "/" + id + ".json"

    with open(file_path, 'w+', encoding="utf-8") as file:
        file.write(json_string)

    response = {"page": wiki_page, "download_url": "/download/" + id}
    return jsonpickle.encode(response, unpicklable=False)


if __name__ == '__main__':
    port = os.getenv("PORT", 3330)
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
