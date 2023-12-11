import unittest
import json
from rest_VariantValidator.utils import input_formatting


class TestFormatInput(unittest.TestCase):

    def test_json_input(self):
        data_string = '[1, 2, 3]'
        result = input_formatting.format_input(data_string)
        self.assertEqual(result, '[1, 2, 3]')

    def test_string_input(self):
        data_string = '1|2|3'
        result = input_formatting.format_input(data_string)
        self.assertEqual(result, '["1", "2", "3"]')

    def test_json_array_input(self):
        data_string = '["a", "b", "c"]'
        result = input_formatting.format_input(data_string)
        self.assertEqual(result, '["a", "b", "c"]')

    def test_mixed_input(self):
        data_string = '[1, 2, 3]|4|5'
        result = input_formatting.format_input(data_string)
        self.assertEqual(result, '["[1, 2, 3]", "4", "5"]')

    def test_pipe_and_special_characters(self):
        data_string = 'a|b|c|gomd|e|lomf'
        result = input_formatting.format_input(data_string)
        self.assertEqual(result, '["a", "b", "c|gomd", "e|lomf"]')

    def test_empty_input(self):
        data_string = ''
        result = input_formatting.format_input(data_string)
        self.assertEqual(result, '[""]')

    def test_multiple_pipe_symbols(self):
        data_string = 'a||b||c'
        result = input_formatting.format_input(data_string)
        self.assertEqual(result, '["a", "", "b", "", "c"]')

    def test_json_array_string_input(self):
        data_string = '["apple", "banana", "cherry"]'
        result = input_formatting.format_input(data_string)
        self.assertEqual(result, '["apple", "banana", "cherry"]')

    def test_result_is_json(self):
        data_string = '[1, 2, 3]'
        result = input_formatting.format_input(data_string)
        self.assertIsInstance(result, str)
        json_result = json.loads(result)
        self.assertEqual(json_result, [1, 2, 3])


