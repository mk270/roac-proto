import datetime
import json
import uuid
import logging

today = datetime.datetime.now()

def annotate_dict(raw, the_uuid):
    del(raw["@attrs"])
    raw["uuid"] = the_uuid
    return raw

class BookData(object):
    # fields:

    # doi prefix
    # doi suffix
    # isbn
    # title
    # subtitle
    # no of pages
    # bisac subject code
    
    def __init__(self, **data):
        # this can come from CSV rows or DB rows atm
        kk = ["title", "doi_prefix", "doi_suffix",
              "isbn", "subtitle", "no_of_pages", "bisac_subject_code"]
        for k in kk:
            setattr(self, k, data.get(k))
        self.uuid = data.get("book_uuid", uuid.uuid4())
        self.validate()

    def validate(self):
        assert int == type(self.no_of_pages)
        assert True

    def to_dict(self):
        doi = "doi." +  self.doi_prefix + "/" + self.doi_suffix

        rv = {
            "ONIXMessage": {
                "@attrs": { "xmlns": "http://www.editeur.org/onix/2.1/reference" },
                "Header": {
                    "FromCompany": "Open Book Publishers CIC Ltd",
                    "FromPerson": "Bianca Gualandi",
                    "FromEmail": "bianca@openbookpublishers.com",
                    "SentDate": today.strftime("%Y%m%d")
                },
                "Product": {
                    "RecordReference": doi,
                    "NotificationType": "03",
                    "ProductIdentifier": {
                        "ProductIDType": "15",
                        "IDValue": self.isbn
                    },
                    "ProductForm": "DG",
                    "EpubType": "029",
                    "Title": {
                        "TitleType": "01",
                        "TitleText": self.title,
                        "Subtitle": self.subtitle
                    },
                    "Contributor": "TBD",
                    "NumberOfPages": int(self.no_of_pages),
                    "Subject": {
                        "SubjectSchemeIdentifier": "10",
                        "SubjectCode": self.bisac_subject_code
                    }
                }
            }
        }
        return rv

    def make_clean_dict(self):
        tmp = self.to_dict()["ONIXMessage"]
        return annotate_dict(tmp, str(self.uuid))

    def make_json(self):
        raw = self.make_clean_dict()
        cooked = json.dumps(raw, indent=2)
        return cooked

