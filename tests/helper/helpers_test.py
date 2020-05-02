import random
import unittest

from simulator.helper.simulation import get_infection_parameters
from simulator.helper.dynamic import get_mortalty_rate, get_hospitalization_rate
from simulator.helper.utils import invert_map_list, invert_map, flatten, reduce_multiply_by_key, choose_weight_order, \
    rec_get_manhattan_walk, get_random_choice_list


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

    def test_invert_map_list(self):
        input_dic = {0: [(1, 2), (2, 1)], 1: [(2, 1)], 2: [(1, 3), (2, 1)]}
        result = invert_map_list(input_dic)
        self.assertEqual(list(result.keys()), [(1, 2), (2, 1), (1, 3)])
        self.assertEqual(result[(1, 2)], [0])
        self.assertEqual(result[(2, 1)], [0, 1, 2])
        self.assertEqual(result[(1, 3)], [2])

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

    def test_rec_get_manhattan_walk(self):
        result = rec_get_manhattan_walk([], (1, 1), (3, 3))
        self.assertEqual(result, [(1, 1), (3, 3), (1, 2), (3, 3), (1, 3), (3, 3), (3, 3), (2, 3), (3, 3)])

    def test_rec_get_manhattan_walk_same_block(self):
        result = rec_get_manhattan_walk([], (1, 1), (1, 1))
        self.assertEqual(result, [(1, 1)])

    def test_reduce_multiply_by_key(self):
        result = reduce_multiply_by_key([(0, 2), (0, 1.5), (1, 2), ('a', 5), (99, 0), (99, 12)])
        self.assertEqual(result, {
            0: 3,
            1: 2,
            'a': 5,
            99: 0
        })

    def test_choose_weight_order(self):
        self.assertEqual(choose_weight_order(list(range(100)), 0.001), 99)
        self.assertEqual(choose_weight_order(list(range(100)), 0.999), 0)
        self.assertEqual(choose_weight_order(list(range(100)), 0.021), 45)


if __name__ == '__main__':
    unittest.main()
