import os
import logging
import psycopg2
import psycopg2.extras
from bookdata import BookData

HOST = os.environ['POSTGRES_HOST']
USER = os.environ['POSTGRES_USER']
PWD = os.environ['POSTGRES_PASSWORD']
DB = os.environ['POSTGRES_DB']

DSN = "dbname="+DB+" host="+HOST+" user="+USER+" password="+PWD

def clear_db():
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as curs:
            curs.execute("delete from book;")

# DEDUPE

def params_of_book_dict(b):
    return {
        "title": b["Product"]["Title"]["TitleText"],
        "subtitle": b["Product"]["Title"]["Subtitle"],
        "publisher": b["Header"]["FromCompany"],
        "book_uuid": b["uuid"],
        "isbn1": b["Product"]["ProductIdentifier"]["IDValue"],
        "page_count": b["Product"]["NumberOfPages"],
        "bisac_subject_code_1": b["Product"]["Subject"]["SubjectCode"],
        "doi": b["Product"]["RecordReference"]
    }

# DEDUPE

def _dump_to_db(book_params):
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as curs:
            curs.execute("delete from book;")
            sql = """insert into book (title, publisher, book_uuid,
                                       isbn1, subtitle, page_count,
                                       bisac_subject_code_1, doi
                                       )
                       values (%(title)s, %(publisher)s, %(book_uuid)s,
                               %(isbn1)s, %(subtitle)s, %(page_count)s,
                               %(bisac_subject_code_1)s, %(doi)s
                              )
                       ;"""
            for params in book_params():
                curs.execute(sql, params)

def dump_to_db(all_books):
    def book_params():
        for b in all_books:
            yield params_of_book_dict(b)

    _dump_to_db(book_params)

## DEDUPE

def db_row_to_book_columns(row):
    doi = row["doi"]
    assert doi.startswith("doi.")
    doi_prefix, doi_suffix = doi[4:].split("/", 1)
    return {
        "doi_prefix": doi_prefix,
        "doi_suffix": doi_suffix,
        "isbn": row["isbn1"],
        "title": row["title"],
        "subtitle": row["subtitle"],
        "no_of_pages": int(row["page_count"]),
        "bisac_subject_code": row["bisac_subject_code_1"]
    }

def read_from_db():
    with psycopg2.connect(DSN) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
            sql = """select book_uuid, title, publisher,
                            doi, isbn1, subtitle, page_count,
                            bisac_subject_code_1
                       from book;"""
            curs.execute(sql)
            for row in curs.fetchall():
                row_data = db_row_to_book_columns(row)
                yield BookData(**row_data)

def get_book_by_doi(doi):
    with psycopg2.connect(DSN) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
            sql = """select book_uuid, title, publisher,
                            doi, isbn1, subtitle, page_count,
                            bisac_subject_code_1
                       from book where doi = %(doi)s;"""
            curs.execute(sql, {"doi": doi})
            row = curs.fetchone()
            row_data = db_row_to_book_columns(row)
            return BookData(**row_data)
