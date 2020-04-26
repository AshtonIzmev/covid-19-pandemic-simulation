import random
import numpy as np
import unittest

from initiator.core import build_individual_houses_map, build_individual_adult_map, build_individual_age_map, \
    build_house_adult_map, build_house_store_map, build_individual_work_map, build_individual_workblock_map, \
    build_individual_individual_transport_map, build_1d_item_behavior, build_2d_item_behavior
from initiator.helper import invert_map, invert_map_list


class TestInitiation(unittest.TestCase):

    @classmethod
    def setUp(cls):
        random.seed(12)
        np.random.seed(seed=12)

    def test_build_individual_houses_map__first_families(self):
        result = build_individual_houses_map(5)
        self.assertEqual(result, {0: 0, 1: 0, 2: 1, 3: 1, 4: 1})

    def test_build_individual_houses_map__second_families(self):
        result = build_individual_houses_map(10)
        self.assertEqual(result, {0: 0, 1: 0, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 2, 8: 2, 9: 2})

    def test_build_individual_houses_map__average_moroccan_household(self):
        result = build_individual_houses_map(1000)
        mean_family = np.mean([len(v) for k, v in invert_map(result).items()])
        self.assertTrue(abs(mean_family-4.52) < 0.3)

    def test_build_individual_adult_map(self):
        input_individual_houses_map = {
            0: 0, 1: 0, 2: 0, 3: 0,
            4: 1, 5: 1, 6: 1,
            7: 2, 8: 2,
            9: 3
        }
        result = build_individual_adult_map(input_individual_houses_map)
        self.assertEqual(result, {
            0: 1, 1: 1, 2: 0, 3: 0,
            4: 1, 5: 1, 6: 0,
            7: 1, 8: 1,
            9: 1
        })

    def test_build_individual_age_map(self):
        input_individual_houses_map = {
            0: 0, 1: 0, 2: 0, 3: 0,
            4: 1, 5: 1, 6: 1,
            7: 2, 8: 2,
            9: 3
        }
        result = build_individual_age_map(input_individual_houses_map)
        self.assertEqual(result, {
            0: 35, 1: 47, 2: 1, 3: 13,
            4: 22, 5: 35, 6: 13,
            7: 26, 8: 37,
            9: 20
        })

    def test_build_house_adult_map(self):
        input_individual_houses_map = {
            0: 0, 1: 0, 2: 0, 3: 0,
            4: 1, 5: 1, 6: 1,
            7: 2, 8: 2,
            9: 3
        }
        input_individual_adult_map = {
            0: 1, 1: 1, 2: 0, 3: 0,
            4: 1, 5: 1, 6: 0,
            7: 1, 8: 1,
            9: 1
        }
        result = build_house_adult_map(input_individual_houses_map, input_individual_adult_map)
        self.assertEqual(result, {0: [0, 1], 1: [4, 5], 2: [7, 8], 3: [9]})

    def test_build_house_store_map(self):
        geo_position_store = [(6, 6), (5, 5), (4, 4), (3, 3), (2, 2), (1, 1)]
        geo_position_house = [(6.1, 6.2), (5.1, 5.2), (4.1, 4.2), (3.1, 3.2), (2.1, 2.2), (1.1, 1.2)]
        result = build_house_store_map(geo_position_store, geo_position_house,0.5)
        self.assertEqual(result, {0: 0, 1: 0, 2: 1, 3: 3, 4: 4, 5: 5})

    def test_build_individual_work_map(self):
        input_individual_adult_map = {
            0: 1, 1: 1, 2: 0, 3: 0,
            4: 1, 5: 1, 6: 0,
            7: 1, 8: 1,
            9: 1
        }
        result = build_individual_work_map(input_individual_adult_map)
        self.assertEqual(result, {0: 2, 1: 2, 4: 1, 5: 0, 7: 1, 8: 2, 9: 2})

    def test_build_individual_work_blocks(self):
        result = build_individual_workblock_map(
            {0: 0, 1: 0, 2: 1, 3: 1}, {0: 0, 1: 1, 2: 0, 3: 1},
            [(2, 3), (7, 8)], [(3, 1), (9, 5)]
        )
        expected = {
            0: [(3, 2), (3, 1), (2, 3), (3, 3)],
            1: [(5, 5), (4, 5), (7, 5), (2, 3), (9, 5), (2, 5), (8, 5), (2, 4), (6, 5), (3, 5)],
            2: [(7, 8), (3, 2), (3, 3), (6, 8), (4, 8), (3, 1), (3, 8), (3, 6), (3, 7), (3, 4), (5, 8), (3, 5)],
            3: [(9, 8), (8, 8), (9, 6), (9, 5), (7, 8), (9, 7)]
        }
        self.assertEqual(result, expected)

    def test_build_individual_individual_transport_map(self):
        ind_workblock = {
            0: [(1, 1), (1, 2), (1, 3), (2, 3)],
            1: [(0, 3), (1, 3), (1, 4), (1, 5)],
            2: [(0, 1), (0, 2), (1, 2), (2, 2)],
            3: [(8, 8), (8, 7), (7, 7)]
        }
        workblock_ind = invert_map_list(ind_workblock)
        result = build_individual_individual_transport_map(ind_workblock, workblock_ind)
        self.assertEqual(result, {0: {0, 1, 2}, 1: {0, 1}, 2: {0, 2}, 3: {3}})

    def test_build_individual_individual_transport_with_empty_bin_map(self):
        ind_workblock = {
            0: [(1, 1), (1, 2), (1, 3), (2, 3)],
            1: [(0, 3), (1, 3), (1, 4), (1, 5)],
            2: [(0, 1), (0, 2), (1, 2), (2, 2)],
            3: [(8, 8), (8, 7), (7, 7)]
        }
        workblock_ind = invert_map_list(ind_workblock)
        result = build_individual_individual_transport_map(ind_workblock, workblock_ind)
        self.assertEqual(result, {0: {0, 1, 2}, 1: {0, 1}, 2: {0, 2}, 3: {3}})

    def test_build_2d_item_behavior(self):
        result = build_2d_item_behavior(5)
        self.assertEqual(result, {
            (0, 0): 0.7647972552573965, (0, 1): 1.1654420940263253, (0, 2): 0.8543389011587692,
            (0, 3): 1.0278371111535274, (0, 4): 0.5533251730179629,
            (1, 0): 1.3522229649329733, (1, 1): 1.3246291725070376, (1, 2): 0.6013707859371777,
            (1, 3): 1.431700642993975, (1, 4): 0.7481107366604964,
            (2, 0): 0.8689806570530012, (2, 1): 1.0731104988941886, (2, 2): 1.4005948170768656,
            (2, 3): 1.265694653326226, (2, 4): 0.5098287760755669,
            (3, 0): 1.0201385096625208, (3, 1): 1.039144546661878, (3, 2): 0.9981637359640853,
            (3, 3): 1.1875100929432938, (3, 4): 0.7709733255944045,
            (4, 0): 1.1846232304528599, (4, 1): 0.5710131776709169, (4, 2): 0.7460685388593822,
            (4, 3): 0.7258112352923074, (4, 4): 0.8869675168747945
        })

    def test_build_1d_item_behavior(self):
        result = build_1d_item_behavior(5)
        self.assertEqual(result, {
            0: 0.7647972552573965,
            1: 1.1654420940263253,
            2: 0.8543389011587692,
            3: 1.0278371111535274,
            4: 0.5533251730179629
        })

    def test_build_1d_item_behavior_mean(self):
        result = build_1d_item_behavior(5000)
        mean_behavior = np.mean(list(result.values()))
        self.assertTrue(abs(mean_behavior - 1) < 0.05)


if __name__ == '__main__':
    unittest.main()
