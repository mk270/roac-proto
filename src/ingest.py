#!/usr/bin/env python3

import os
import csv
import sys
import json

from bookdata import BookData
import database

from argparse import ArgumentParser

## DEDUPE

def map_obp_csv_columns(row):
    return {
        "title": row["Title"],
        "doi_prefix": row["DOI prefix"],
        "doi_suffix": row["DOI suffix"],
        "isbn": row["ISBN 1"],
        "no_of_pages": int(row["no of pages"]),
        "subtitle": row["Subtitle"],
        "bisac_subject_code": row["BISAC subject code 1"]
    }

def books(input_stream):
    reader = csv.DictReader(input_stream)

    for row in reader:
        if row["Title"] == "":
            continue # ignore blank line
        row_data = map_obp_csv_columns(row)
        yield BookData(**row_data)

def write_book_json(output_dir, book):
    filename = os.path.join(output_dir, str(book.uuid) + ".json")
    with open(filename, "w") as f:
        f.write(book.make_json())
        f.write("\n\n")

def dump_json(output_dir):
    for book in books(sys.stdin):
        write_book_json(output_dir, book)

def dump_db_to_dir(output_dir):
    for book in database.read_from_db():
        write_book_json(output_dir, book)

def save_to_db(input_stream):
    all_books = [ book.make_clean_dict() for book in books(input_stream) ]
    return database.dump_to_db(all_books)

def ingest_dir(path):
    def get_data():
        for fn in os.listdir(path):
            if not fn.endswith(".json"):
                continue
            if len(fn) != 41:
                continue
            with open(os.path.join(path, fn)) as f:
                data = json.load(f)
                yield data
    payload = [ p for p in get_data() ]
    database.dump_to_db(payload)

def run():
    p = ArgumentParser()
    p.add_argument("--output-json", action="store_true", dest="json_out")
    p.add_argument("--save-to-db", action="store_true", dest="save_to_db")
    p.add_argument("--dir", action="store", dest="output_dir")
    p.add_argument("--ingest-dir", action="store", dest="ingest_dir")
    p.add_argument("--dump-db", action="store_true", dest="dump_db")

    options = p.parse_args()
    if options.json_out:
        assert options.output_dir
        return dump_json(options.output_dir)
    elif options.save_to_db:
        return save_to_db(sys.stdin)
    elif options.ingest_dir:
        return ingest_dir(options.ingest_dir)
    elif options.dump_db:
        assert options.output_dir
        return dump_db_to_dir(options.output_dir)
    else:
        print("unknown usage")
        sys.exit(1)

if __name__ == '__main__':
    run()
