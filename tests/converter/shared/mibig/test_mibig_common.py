import unittest

from mibig.errors import ValidationError
from mibig.converters.shared.mibig import common


class TestSubstrateEvidence(unittest.TestCase):

    def test_json(self):
        raw = {
            "method": "NMR",
            "references": ["pubmed:123456"],
        }
        evidence = common.SubstrateEvidence.from_json(raw)
        assert evidence.to_json() == raw


        raw["method"] = "Bob"

        with self.assertRaises(ValidationError):
            common.SubstrateEvidence.from_json(raw)
