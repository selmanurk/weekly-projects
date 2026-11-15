import unittest

from llm_contract_validator import validate


CONTRACT = {
    "required": {"summary": "string", "confidence": "number", "tags": "array"},
    "allow_extra": False,
}


class ContractValidatorTests(unittest.TestCase):
    def test_valid_payload(self):
        self.assertEqual(validate({"summary": "Ready", "confidence": 0.9, "tags": ["release"]}, CONTRACT), [])

    def test_missing_required_field(self):
        errors = validate({"summary": "Ready", "tags": []}, CONTRACT)
        self.assertEqual(errors[0]["path"], "$.confidence")
        self.assertEqual(errors[0]["code"], "missing")

    def test_wrong_type_and_boolean_is_not_number(self):
        errors = validate({"summary": "Ready", "confidence": True, "tags": "release"}, CONTRACT)
        self.assertEqual({error["path"] for error in errors}, {"$.confidence", "$.tags"})

    def test_extra_field_is_rejected(self):
        errors = validate({"summary": "Ready", "confidence": 1, "tags": [], "debug": "x"}, CONTRACT)
        self.assertEqual(errors[0]["code"], "extra")

    def test_non_object_payload(self):
        self.assertEqual(validate(["unexpected"], CONTRACT)[0]["path"], "$")


if __name__ == "__main__":
    unittest.main()
