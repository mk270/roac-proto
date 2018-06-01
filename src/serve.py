#!/usr/bin/env python3

import os
import logging
from bottle import route, run, static_file

import database

ROOT_DIR = os.path.join(os.path.dirname(__file__),
                        os.pardir,
                        "static")

@route('/data/all.json')
def all_json():
    books = [ b.make_clean_dict() for b in database.read_from_db() ]
    return {
        "book": books
    }

@route("/onix/<doi:path>")
def onix_doi(doi):
    book = database.get_book_by_doi(doi)
    return book.make_xml()

@route("/json/<doi:path>")
def json_doi(doi):
    book = database.get_book_by_doi(doi)
    return book.make_clean_dict()

@route('/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=ROOT_DIR)

def main():
    config = {
        "host": "0.0.0.0",
        "port": 8080,
        "debug": True,
        "reloader": True
    }
    run(**config)

if __name__ == '__main__':
    main()
