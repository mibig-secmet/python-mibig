import unittest

from mibig.errors import ValidationError
from mibig.converters.shared import common


class TestCitation(unittest.TestCase):
    def test_init(self):
        for database, value in (
            ("pubmed", "12345"),
            ("doi", "10.12345/t0tally-valid_DOI(here)"),
            ("patent", "whatver"),
            ("url", "https://example.com/link_here.html"),
        ):
            cit = common.Citation(database, value)

            assert cit.database == database
            assert cit.value == value

    def test_from_json(self):
        for database, value in (
            ("pubmed", "12345"),
            ("doi", "10.12345/t0tally-valid_DOI(here)"),
            ("patent", "whatver"),
            ("url", "https://example.com/link_here.html"),
        ):
            raw = f"{database}:{value}"
            cit = common.Citation.from_json(raw)

            assert cit.database == database
            assert cit.value == value

    def test_validate(self):
        cit = common.Citation("pubmed", "12345")
        cit.value = "bob"
        errors = cit.validate()
        assert errors
        self.assertRegex(errors[0].message, r"Invalid .* for database 'pubmed'")

        cit.database = "alice"
        errors = cit.validate()
        assert errors
        self.assertRegex(errors[0].message, r"Invalid database type 'alice'")


class TestSubmitterId(unittest.TestCase):
    def test_init(self):
        common.SubmitterID("AAAAAAAAAAAAAAAAAAAAAAAA")
        with self.assertRaises(ValidationError):
            common.SubmitterID("Bob")

    def test_validate(self):
        submitter = common.SubmitterID("Bob", validate=False)
        errors = submitter.validate()
        assert errors
        assert errors[0].message == "invalid length"

        submitter = common.SubmitterID("AAAAAAAAAAAAAAAAAAAAAAA%", validate=False)
        errors = submitter.validate()
        assert errors
        assert errors[0].message == "invalid characters"

    def test_to_json(self):
        assert (
            common.SubmitterID("AAAAAAAAAAAAAAAAAAAAAAAA").to_json()
            == "AAAAAAAAAAAAAAAAAAAAAAAA"
        )

    def test_from_json(self):
        common.SubmitterID.from_json("AAAAAAAAAAAAAAAAAAAAAAAA")
        with self.assertRaises(ValidationError):
            common.SubmitterID.from_json("Bob")


class TestReleaseVersion(unittest.TestCase):
    def test_init(self):
        common.ReleaseVersion("1.0")
        common.ReleaseVersion("next")
        with self.assertRaises(ValidationError):
            common.ReleaseVersion("Bob")
