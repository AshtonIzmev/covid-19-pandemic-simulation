import random
import unittest

from simulator.simulation_helper import get_environment_simulation, get_virus_simulation_t0
from simulator.dynamic_helper import update_infection_period, increment_pandemic_1_day, \
    propagate_to_houses, propagate_to_stores, propagate_to_workplaces
from simulator.keys import *


class TestSimulation(unittest.TestCase):

    @classmethod
    def setUp(cls):
        random.seed(12)

    @staticmethod
    def get_10_01_virus_dic():
        return {
            ICON_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 5, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            IINC_K: {0: -1, 1: -1, 2: -1, 3: -1, 4: 31, 5: -1, 6: -1, 7: -1, 8: -1, 9: -1}
        }

    @staticmethod
    def get_10_01_2_environment_dic():
        return {
            HA_K: {0: [0, 1], 1: [4, 5], 2: [8, 9]},
            HI_K: {0: [0, 1, 2, 3], 1: [4, 5, 6, 7], 2: [8, 9]},
            HS_K: {0: 0, 1: 0, 2: 0},
            IAD_K: {0: 1, 1: 1, 2: 0, 3: 0, 4: 1, 5: 1, 6: 0, 7: 0, 8: 1, 9: 1},
            IAG_K: {0: 26, 1: 51, 2: 13, 3: 2, 4: 35, 5: 33, 6: 6, 7: 1, 8: 27, 9: 20},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
            IW_K: {1: 1, 4: 1, 5: 0},
            SH_K: {0: [0, 1, 2]},
            WI_K: {0: [5], 1: [4, 1]}
        }

    def test_build_environment_dic(self):
        result = get_environment_simulation(10, 0.1, 2)
        expected_result = TestSimulation.get_10_01_2_environment_dic()
        self.assertEqual(result, expected_result)

    def test_build_virus_dic(self):
        result = get_virus_simulation_t0(10, 0.1)
        expected_result = TestSimulation.get_10_01_virus_dic()
        self.assertEqual(result, expected_result)

    def test_update_infection_period(self):
        virus_dic = TestSimulation.get_10_01_virus_dic()
        update_infection_period([1, 4, 9], virus_dic)
        self.assertEqual(virus_dic[ICON_K][1], 5)
        self.assertEqual(virus_dic[ICON_K][4], 5)
        self.assertEqual(virus_dic[ICON_K][9], 2)
        self.assertEqual(virus_dic[IINC_K][1], 29)
        self.assertEqual(virus_dic[IINC_K][4], 31)
        self.assertEqual(virus_dic[IINC_K][9], 32)

    def test_increment_pandemic_1_day(self):
        env_dic = TestSimulation.get_10_01_2_environment_dic()
        virus_dic = {
            ICON_K: {0: -1, 1: -1, 2: -1, 3: -1, 4: 5, 5: 1, 6: 1, 7: 0, 8: 0, 9: 3},
            IINC_K: {0: -1, 1: -1, 2: -1, 3: -1, 4: 31, 5: 31, 6: 0, 7: 15, 8: 1, 9: 2}
        }
        increment_pandemic_1_day(env_dic, virus_dic)
        self.assertEqual(virus_dic[ICON_K][4], 4)
        self.assertEqual(virus_dic[ICON_K][5], 0)
        self.assertEqual(virus_dic[ICON_K][6], 1)
        self.assertEqual(virus_dic[ICON_K][7], -1)
        self.assertEqual(virus_dic[ICON_K][8], -1)
        self.assertEqual(virus_dic[ICON_K][9], 2)
        self.assertEqual(virus_dic[IINC_K][4], 30)
        self.assertEqual(virus_dic[IINC_K][5], 30)
        self.assertEqual(virus_dic[IINC_K][6], 0)
        self.assertEqual(virus_dic[IINC_K][7], 14)
        self.assertEqual(virus_dic[IINC_K][8], -2)
        self.assertEqual(virus_dic[IINC_K][9], 1)

    def test_propagate_to_houses_contagious_people(self):
        env_dic = TestSimulation.get_10_01_2_environment_dic()
        virus_dic = {
            ICON_K: {0: -5, 1: -1, 2: -1, 3: -1, 4: -5, 5: -1, 6: -1, 7: -1, 8: -5, 9: -1},
            IINC_K: {0: 10, 1: -1, 2: -1, 3: -1, 4: 0, 5: -1, 6: -1, 7: -1, 8: -2, 9: -1}
        }
        propagate_to_houses(env_dic, virus_dic, 0.99)
        self.assertEqual(virus_dic[IINC_K][0], 10)
        self.assertEqual(virus_dic[IINC_K][4], 0)
        self.assertEqual(virus_dic[IINC_K][8], -2)
        # infected people contaminate
        self.assertEqual(virus_dic[IINC_K][1], 21)
        self.assertEqual(virus_dic[IINC_K][2], 25)
        self.assertEqual(virus_dic[IINC_K][3], 33)
        # Dead people do not contaminate
        self.assertEqual(virus_dic[IINC_K][5], -1)
        self.assertEqual(virus_dic[IINC_K][6], -1)
        self.assertEqual(virus_dic[IINC_K][7], -1)
        # Immune people do not contaminate
        self.assertEqual(virus_dic[IINC_K][9], -1)

    def test_propagate_to_houses_noncontagious_people(self):
        env_dic = TestSimulation.get_10_01_2_environment_dic()
        virus_dic = {
            ICON_K: {0: 2, 1: -1, 2: -1, 3: -1, 4: 3, 5: -1, 6: -1, 7: -1, 8: 0, 9: -1},
            IINC_K: {0: 10, 1: -1, 2: -1, 3: -1, 4: 0, 5: -1, 6: -1, 7: -1, 8: -2, 9: -1}
        }
        propagate_to_houses(env_dic, virus_dic, 0.99)
        self.assertEqual(virus_dic[IINC_K][0], 10)
        self.assertEqual(virus_dic[IINC_K][4], 0)
        self.assertEqual(virus_dic[IINC_K][8], -2)
        # non contagious people do not contaminate
        self.assertEqual(virus_dic[IINC_K][1], -1)
        self.assertEqual(virus_dic[IINC_K][2], -1)
        self.assertEqual(virus_dic[IINC_K][3], -1)
        # Dead and non contagious people do not contaminate
        self.assertEqual(virus_dic[IINC_K][5], -1)
        self.assertEqual(virus_dic[IINC_K][6], -1)
        self.assertEqual(virus_dic[IINC_K][7], -1)
        # Immune and non contagious people do not contaminate
        self.assertEqual(virus_dic[IINC_K][9], -1)

    def test_propagate_to_stores_child(self):
        env_dic = {
            HA_K: {0: [0, 1], 1: [4, 5], 2: [8, 9]},
            HI_K: {0: [0, 1, 2, 3], 1: [4, 5, 6, 7], 2: [8, 9]},
            HS_K: {0: 0, 1: 1, 2: 0},
            IAD_K: {0: 1, 1: 1, 2: 0, 3: 0, 4: 1, 5: 1, 6: 0, 7: 0, 8: 1, 9: 1},
            IAG_K: {0: 26, 1: 51, 2: 13, 3: 2, 4: 35, 5: 33, 6: 6, 7: 1, 8: 27, 9: 20},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
            IW_K: {1: 1, 4: 1, 5: 0},
            SH_K: {0: [0, 2], 1: [1]},
            WI_K: {0: [5], 1: [4, 1]}
        }
        virus_dic = {
            ICON_K: {0: 0, 1: 0, 2: 0, 3: -5, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            IINC_K: {0: -1, 1: -1, 2: -1, 3: 15, 4: -1, 5: -1, 6: -1, 7: -1, 8: -1, 9: -1}
        }
        propagate_to_stores(env_dic, virus_dic, 0.99)
        # children do not go to stores
        self.assertEqual(virus_dic[IINC_K][0], -1)
        self.assertEqual(virus_dic[IINC_K][1], -1)
        self.assertEqual(virus_dic[IINC_K][2], -1)
        self.assertEqual(virus_dic[IINC_K][8], -1)
        self.assertEqual(virus_dic[IINC_K][9], -1)

    def test_propagate_to_stores_adult(self):
        env_dic = {
            HA_K: {0: [0, 1], 1: [4, 5], 2: [8, 9]},
            HI_K: {0: [0, 1, 2, 3], 1: [4, 5, 6, 7], 2: [8, 9]},
            HS_K: {0: 0, 1: 1, 2: 0},
            IAD_K: {0: 1, 1: 1, 2: 0, 3: 0, 4: 1, 5: 1, 6: 0, 7: 0, 8: 1, 9: 1},
            IAG_K: {0: 26, 1: 51, 2: 13, 3: 2, 4: 35, 5: 33, 6: 6, 7: 1, 8: 27, 9: 20},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
            IW_K: {1: 1, 4: 1, 5: 0},
            SH_K: {0: [0, 2], 1: [1]},
            WI_K: {0: [5], 1: [4, 1]}
        }
        virus_dic = {
            ICON_K: {0: 0, 1: -5, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            IINC_K: {0: -1, 1: 15, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1, 8: -1, 9: -1}
        }
        propagate_to_stores(env_dic, virus_dic, 0.99)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[IINC_K][0], -1)
        self.assertEqual(virus_dic[IINC_K][1], 15)
        self.assertEqual(virus_dic[IINC_K][2], -1)
        self.assertEqual(virus_dic[IINC_K][8], -1)
        self.assertEqual(virus_dic[IINC_K][9], 27)

    def test_propagate_to_workplaces(self):
        env_dic = {
            HA_K: {0: [0, 1], 1: [4, 5], 2: [8, 9]},
            HI_K: {0: [0, 1, 2, 3], 1: [4, 5, 6, 7], 2: [8, 9]},
            HS_K: {0: 0, 1: 1, 2: 0},
            IAD_K: {0: 1, 1: 1, 2: 0, 3: 0, 4: 1, 5: 1, 6: 0, 7: 0, 8: 1, 9: 1},
            IAG_K: {0: 26, 1: 51, 2: 13, 3: 2, 4: 35, 5: 33, 6: 6, 7: 1, 8: 27, 9: 20},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
            IW_K: {1: 1, 4: 1, 5: 0},
            SH_K: {0: [0, 2], 1: [1]},
            WI_K: {0: [5], 1: [4, 1]}
        }
        virus_dic = {
            ICON_K: {0: 0, 1: -2, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            IINC_K: {0: -1, 1: 15, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1, 8: -1, 9: -1}
        }
        propagate_to_workplaces(env_dic, virus_dic, 0.99)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[IINC_K][1], 15)
        self.assertEqual(virus_dic[IINC_K][4], 32)
        self.assertEqual(virus_dic[IINC_K][5], -1)


if __name__ == '__main__':
    unittest.main()

