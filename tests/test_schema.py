"""Negative schema regression cases and fail-closed schema evolution."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_catalog import load, validate_schema

class QuestionSchemaTests(unittest.TestCase):
    def setUp(self):
        self.schema = load('schemas/questions.schema.json')
        self.question = load('questions.json')[0]

    def test_valid_complete_question(self):
        validate_schema([self.question], self.schema)

    def test_invalid_records(self):
        for field, value in [('id', True), ('id', '1'), ('chapter', ''), ('text', ''),
                             ('page', -1), ('answers', [-1]), ('answers', [0, 0]),
                             ('options', ['A', 'B']), ('correctCount', 0),
                             ('assessmentStatus', 'pretend-verified')]:
            with self.subTest(field=field, value=value):
                q = copy.deepcopy(self.question)
                q[field] = value
                with self.assertRaises(AssertionError):
                    validate_schema([q], self.schema)

    def test_missing_field_and_unsupported_schema(self):
        q = copy.deepcopy(self.question)
        del q['answers']
        with self.assertRaises(AssertionError):
            validate_schema([q], self.schema)
        with self.assertRaises(AssertionError):
            validate_schema([], {'type': 'array', 'unimplementedConstraint': True})

if __name__ == '__main__':
    unittest.main()
