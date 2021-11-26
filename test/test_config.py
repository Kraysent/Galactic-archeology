import unittest

from archeology.datamodel.config import Config 

class ConfigTest(unittest.TestCase):
    def test_yaml(self):
        data = {
            'test_str_field': 'test_str',
            'test_int_field': 123,
            'test_float_field': 1.23
        }

        conf = Config(defaults = data)
        
        conf.write_yaml('/home/kraysent/Downloads/test.yaml')

        loaded_data = Config.read_yaml('/home/kraysent/Downloads/test.yaml').to_dict()

        self.assertEqual(data, loaded_data)