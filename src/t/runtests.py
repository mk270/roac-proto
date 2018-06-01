#!/usr/bin/env python3

import os
import sys
import uuid
import json
import tempfile
import shutil

TEST_DIR = os.path.dirname(__file__)

sys.path.append(os.path.join(TEST_DIR, os.pardir))

import ingest
import database
import unittest

class IngestTestCase(unittest.TestCase):
    def setUp(self):
        database.clear_db()

    def getPathForMetadataCSV(self):
        return os.path.join(TEST_DIR, "test-metadata.csv")

    def allBookDatas(self):
        test_data_path = self.getPathForMetadataCSV()
        with open(test_data_path) as f:
            return [ b for b in ingest.books(f) ]

    def saveBookDataToDB(self):
        test_data_path = self.getPathForMetadataCSV()
        with open(test_data_path) as f:
            ingest.save_to_db(f)

    def testBasicCSVReader(self):
        bb = self.allBookDatas()
        self.assertEqual(len(bb), 3)

    def testTitleSmoke(self):
        bb = self.allBookDatas()
        b = bb[0]
        title = b.to_dict()["ONIXMessage"]["Product"]["Title"]["TitleText"]
        self.assertEqual(title,
                         "That Greece Might Still Be Free")

    def testTitleInDB(self):
        self.saveBookDataToDB()
        book = database.get_book_by_doi("doi.10.11647/OBP.0002")
        self.assertEqual(book.isbn, "9781906924034")

    # DEDUPE

    def testReadFromDB(self):
        params = {
            "title": "The End of the World",
            "subtitle": "Apocalypse and its Aftermath in Western Culture",
            "publisher": "OBP",
            "book_uuid": str(uuid.uuid4()),
            "isbn1": "9781906924508",
            "page_count": 219,
            "bisac_subject_code_1": "LIT004260",
            "doi": "doi.10.11647/OBP.0015"   
        }
        def book_stream():
            yield params
        database._dump_to_db(book_stream)
        book = database.get_book_by_doi("doi.10.11647/OBP.0015")
        self.assertEqual(book.isbn, "9781906924508")

    def testGenerateJSON(self):
        self.saveBookDataToDB()
        book = database.get_book_by_doi("doi.10.11647/OBP.0002")
        j = book.make_json()
        decoded = json.loads(j)
        self.assertEqual(decoded["Product"]["NumberOfPages"], 344)
        self.assertEqual(decoded["Product"]["ProductIdentifier"]["IDValue"],
                         "9781906924034")

    def testGenerateJSONDir(self):
        try:
            tmp = tempfile.mkdtemp()
            self.saveBookDataToDB()
            ingest.dump_db_to_dir(tmp)

            data = {}
            for filename in os.listdir(tmp):
                path = os.path.join(tmp, filename)
                with open(path) as f:
                    data[filename] = json.load(f)

            found = False
            for filename in data.keys():
                doi = data[filename]['Product']['RecordReference']
                if doi == 'doi.10.11647/OBP.0001':
                    found = True
                    break
            self.assertEqual(found, True)

        finally:
            shutil.rmtree(tmp)

    def testIngestDir(self):
        fake_data_dir = os.path.join(TEST_DIR, "fake-data")
        ingest.ingest_dir(fake_data_dir)
        book = database.get_book_by_doi("doi.10.11647/OBP.0002")
        title = book.to_dict()["ONIXMessage"]["Product"]["Title"]["TitleText"]
        self.assertEqual(title, "The Alerting Eye")

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()
