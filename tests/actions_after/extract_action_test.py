from dataclasses import dataclass

from omtool.actions_after import extract_action
from omtool.core.utils import BaseTestCase


@dataclass
class nested:
    attr = "value"


@dataclass
class x:
    field = 5
    nest_field = nested()


class TestExtractAction(BaseTestCase):
    def test_keep_old(self):
        data = {"field1": x()}

        actual = extract_action(data, field2="field1.field")
        expected = {"field1": x(), "field2": 5}

        self.assertEqual(actual, expected)

    def test_nesting(self):
        data = {"field1": x()}

        actual = extract_action(data, field2="field1.nest_field.attr")
        expected = {"field1": x(), "field2": "value"}

        self.assertEqual(actual, expected)

    def test_not_keep_old(self):
        data = {"field1": x()}

        actual = extract_action(data, keep_old=False, field2="field1.field")
        expected = {"field2": 5}

        self.assertEqual(actual, expected)

    def test_no_kwargs(self):
        data = {"field1": x()}
        actual = extract_action(data)
        expected = {"field1": x()}

        self.assertEqual(actual, expected)

    def test_no_such_key(self):
        data = {"field1": x()}
        self.assertRaises(KeyError, extract_action, data, field2="nonexistent_field.field")

    def test_no_such_field(self):
        data = {"field1": x()}
        self.assertRaises(AttributeError, extract_action, data, field2="field1.nonexistent_field")
