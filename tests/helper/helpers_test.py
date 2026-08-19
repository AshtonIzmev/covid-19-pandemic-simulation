import math
import random
import unittest

from simulator.helper.environment import get_hospitalization_rate, get_mortality_rate, get_symptom_rate
from simulator.helper.simulation import get_infection_parameters
from simulator.helper.utils import (
    choose_weight_order,
    get_center_squized_random,
    get_clipped_gaussian_number,
    get_r,
    get_random_choice_list,
    get_random_sample,
    invert_map,
    invert_map_list,
    rec_get_manhattan_walk,
    reduce_multiply_by_key,
)


class TestHelpers(unittest.TestCase):

    def setUp(self):
        random.seed(12)

    def test_invert_map(self):
        result = invert_map({0: 1, 1: 1, 2: 2})
        self.assertEqual(list(result.keys()), [1, 2])
        self.assertEqual(result[1], [0, 1])
        self.assertEqual(result[2], [2])

    def test_invert_map_empty(self):
        self.assertEqual(invert_map({}), {})

    def test_invert_map_is_reversible(self):
        original = {i: i % 4 for i in range(40)}
        rebuilt = {i: house for house, members in invert_map(original).items() for i in members}
        self.assertEqual(rebuilt, original)

    def test_invert_map_list(self):
        input_dic = {0: [(1, 2), (2, 1)], 1: [(2, 1)], 2: [(1, 3), (2, 1)]}
        result = invert_map_list(input_dic)
        self.assertEqual(list(result.keys()), [(1, 2), (2, 1), (1, 3)])
        self.assertEqual(result[(1, 2)], [0])
        self.assertEqual(result[(2, 1)], [0, 1, 2])
        self.assertEqual(result[(1, 3)], [2])

    def test_invert_map_list_empty_values(self):
        self.assertEqual(invert_map_list({0: [], 1: []}), {})

    def test_get_random_choice_list(self):
        result = list(get_random_choice_list([[1, 2], [0], [1, 3], []]))
        # One pick per non-empty sub-list, empty ones are dropped.
        self.assertEqual(len(result), 3)
        self.assertIn(result[0], [1, 2])
        self.assertEqual(result[1], 0)
        self.assertIn(result[2], [1, 3])

    def test_get_random_choice_list_only_empty(self):
        self.assertEqual(get_random_choice_list([[], []]), [])

    def test_get_random_choice_list_stays_in_range(self):
        # get_r() can return values very close to 1, the index must never overflow.
        for _ in range(500):
            (picked,) = get_random_choice_list([[0, 1, 2, 3, 4]])
            self.assertIn(picked, [0, 1, 2, 3, 4])

    def test_get_random_sample_caps_the_size(self):
        self.assertEqual(len(get_random_sample(list(range(100)), 7)), 7)
        self.assertEqual(len(get_random_sample(list(range(3)), 7)), 3)

    def test_get_random_sample_accepts_sets_and_dict_views(self):
        # random.sample() has refused non-sequences since python 3.11, and both
        # of these are passed by the environment and propagation code.
        self.assertEqual(sorted(get_random_sample({1, 2, 3}, 3)), [1, 2, 3])
        self.assertEqual(sorted(get_random_sample({1: 'a', 2: 'b'}.keys(), 5)), [1, 2])
        self.assertEqual(get_random_sample(set(), 4), [])

    def test_get_random_sample_draws_without_replacement(self):
        sample = get_random_sample(set(range(50)), 20)
        self.assertEqual(len(sample), len(set(sample)))

    def test_get_r_is_a_unit_probability(self):
        for _ in range(200):
            value = get_r()
            self.assertGreaterEqual(value, 0.0)
            self.assertLess(value, 1.0)

    def test_get_center_squized_random_stays_in_unit_range(self):
        values = [get_center_squized_random() for _ in range(2000)]
        self.assertTrue(all(0 <= v <= 1 for v in values))
        # The cubic squeezes draws towards the centre: more than a uniform would.
        near_centre = sum(1 for v in values if 0.35 < v < 0.65)
        self.assertGreater(near_centre / len(values), 0.30)

    def test_get_clipped_gaussian_number_respects_bounds(self):
        for _ in range(200):
            value = get_clipped_gaussian_number(1, 10, 4.52, math.sqrt(4.71))
            self.assertGreaterEqual(value, 1)
            self.assertLessEqual(value, 10)

    def test_get_clipped_gaussian_number_returns_a_plain_float(self):
        # It feeds dictionaries that get compared and serialised, a numpy scalar
        # would leak into every one of them.
        self.assertIs(type(get_clipped_gaussian_number(0.5, 1.5, 1, 0.25)), float)

    def test_get_infection_parameters_orders_and_bounds(self):
        for _ in range(100):
            contagion, hospital, death, immunity = get_infection_parameters(2, 7, 7, 21, 21, 39, 30, 60)
            self.assertTrue(2 <= contagion <= 7)
            self.assertTrue(7 <= hospital <= 21)
            self.assertTrue(21 <= death <= 39)
            self.assertTrue(30 <= immunity <= 60)
            self.assertTrue(all(isinstance(v, int) for v in (contagion, hospital, death, immunity)))

    def test_get_infection_parameters_degenerate_bounds(self):
        self.assertEqual(get_infection_parameters(5, 5, 6, 6, 7, 7, 8, 8), (5, 6, 7, 8))

    def test_get_mortality_rate(self):
        self.assertEqual(get_mortality_rate(62), 0.036)
        self.assertEqual(get_mortality_rate(31), 0.02)
        self.assertEqual(get_mortality_rate(0), 0)
        self.assertEqual(get_mortality_rate(9), 0)
        self.assertEqual(get_mortality_rate(85), 0.148)

    def test_get_mortality_rate_grows_with_age_above_fifty(self):
        rates = [get_mortality_rate(age) for age in (50, 60, 70, 80)]
        self.assertEqual(rates, sorted(rates))

    def test_get_hospitalization_rate(self):
        self.assertEqual(get_hospitalization_rate(44), 0.025)
        self.assertEqual(get_hospitalization_rate(19), 0.01)
        self.assertEqual(get_hospitalization_rate(88), 0.172)

    def test_get_symptom_rate(self):
        self.assertAlmostEqual(get_symptom_rate(44), 0.06108)
        self.assertAlmostEqual(get_symptom_rate(19), 0.009045)
        self.assertEqual(get_symptom_rate(5), 0.0)

    def test_rates_are_defined_and_are_probabilities_for_every_age(self):
        for age in range(0, 126):
            for rate in (get_mortality_rate(age), get_hospitalization_rate(age), get_symptom_rate(age)):
                self.assertIsInstance(rate, float)
                self.assertGreaterEqual(rate, 0.0)
                self.assertLessEqual(rate, 1.0)

    def test_rec_get_manhattan_walk(self):
        result = rec_get_manhattan_walk([], (1, 1), (3, 3))
        self.assertEqual(result, [(1, 1), (1, 2), (1, 3), (2, 3), (3, 3)])

    def test_rec_get_manhattan_walk_backward(self):
        result = rec_get_manhattan_walk([], (3, 3), (1, 1))
        self.assertEqual(result, [(3, 3), (3, 2), (3, 1), (2, 1), (1, 1)])

    def test_rec_get_manhattan_walk_same_block(self):
        self.assertEqual(rec_get_manhattan_walk([], (1, 1), (1, 1)), [(1, 1)])

    def test_rec_get_manhattan_walk_length_is_the_manhattan_distance(self):
        for start, end in (((0, 0), (4, 7)), ((9, 2), (1, 1)), ((3, 3), (3, 8))):
            walk = rec_get_manhattan_walk([], start, end)
            distance = abs(start[0] - end[0]) + abs(start[1] - end[1])
            self.assertEqual(len(walk), distance + 1)
            self.assertEqual(walk[0], start)
            self.assertEqual(walk[-1], end)
            # Every step moves exactly one block along one axis.
            for a, b in zip(walk, walk[1:]):
                self.assertEqual(abs(a[0] - b[0]) + abs(a[1] - b[1]), 1)

    def test_reduce_multiply_by_key(self):
        result = reduce_multiply_by_key([(0, 2), (0, 1.5), (1, 2), ('a', 5), (99, 0), (99, 12)])
        self.assertEqual(result, {0: 3, 1: 2, 'a': 5, 99: 0})

    def test_reduce_multiply_by_key_empty(self):
        self.assertEqual(reduce_multiply_by_key([]), {})

    def test_choose_weight_order(self):
        self.assertEqual(choose_weight_order(list(range(100)), 0.001), 99)
        self.assertEqual(choose_weight_order(list(range(100)), 0.999), 0)
        self.assertEqual(choose_weight_order(list(range(100)), 200), 0)

    def test_choose_weight_order_always_returns_a_member(self):
        options = ['a', 'b', 'c']
        for probability in (0.0, 0.25, 0.5, 0.75, 1.0):
            for _ in range(50):
                self.assertIn(choose_weight_order(options, probability), options)

    def test_choose_weight_order_prefers_the_head_when_probability_is_high(self):
        picks = [choose_weight_order([0, 1, 2], 0.9) for _ in range(400)]
        self.assertGreater(picks.count(0) / len(picks), 0.8)

    def test_choose_weight_order_single_element(self):
        self.assertEqual(choose_weight_order(['only'], 0.0), 'only')


if __name__ == '__main__':
    unittest.main()
