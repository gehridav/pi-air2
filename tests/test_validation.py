import unittest

from os import sys
sys.path.append('./pi_air2')

from pi_air2.carbon_count_uart import Sensor

validate = Sensor.validate

class TestValidation(unittest.TestCase):
    def test_validate_return_newVal_when_smaller_2x_ref_value(self):
        refValue = 100
        newValue = 110
        result = validate(Sensor, refValue, newValue)
        self.assertEqual(result, newValue)

    def test_validate_return_refVal_when_bigger_2x_ref_value(self):
        refValue = 100
        newValue = 200
        result = validate(Sensor, refValue, newValue)
        self.assertEqual(result, refValue)

    def test_validate_return_refVal_when_0(self):
        refValue = 100
        newValue = ''
        result = validate(Sensor, refValue, newValue)
        self.assertEqual(result, refValue)


if __name__ == '__main__':
    unittest.main()