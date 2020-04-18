import random
import unittest

from initiator.helper import invert_map, flatten, get_random_choice_list, get_infection_parameters, \
    get_mortalty_rate, get_hospitalization_rate


class TestHelpers(unittest.TestCase):

    @classmethod
    def setUp(cls):
        random.seed(12)

    def test_invert_map(self):
        input_dic = {0: 1, 1: 1, 2: 2}
        result = invert_map(input_dic)
        self.assertEqual(list(result.keys()), [1, 2])
        self.assertEqual(result[1], [0, 1])
        self.assertEqual(result[2], [2])

    def test_flatten(self):
        input_list = [[1, 2], [0], [1, 3]]
        result = flatten(input_list)
        self.assertEqual(result, [1, 2, 0, 1, 3])

    def test_get_random_choice_list(self):
        input_list_list = [[1, 2], [0], [1, 3]]
        result = list(get_random_choice_list(input_list_list))
        self.assertEqual(len(result), 3)
        self.assertTrue(0 in result)
        self.assertEqual(result, [2, 0, 3])

    def test_get_infection_parameters(self):
        result = get_infection_parameters(2, 7, 7, 21, 21, 39, 30, 60)
        self.assertEqual(result[0], 4)
        self.assertEqual(result[1], 16)
        self.assertEqual(result[2], 32)
        self.assertEqual(result[3], 34)

    def test_get_mortalty_rate(self):
        self.assertEqual(get_mortalty_rate(62), 0.036)
        self.assertEqual(get_mortalty_rate(31), 0.02)

    def test_get_mortalty_rate2(self):
        self.assertEqual(get_hospitalization_rate(44), 0.025)
        self.assertEqual(get_hospitalization_rate(19), 0.01)


if __name__ == '__main__':
    unittest.main()
