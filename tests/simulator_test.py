import random
import unittest

from simulator.simulation_helper import get_environment_simulation, get_virus_simulation_t0
from simulator.dynamic_helper import update_infection_period, increment_pandemic_1_day, \
    propagate_to_houses, propagate_to_stores, propagate_to_workplaces
from simulator.keys import *

H = HEALTHY_V
F = INFECTED_V
M = IMMUNE_V
D = DEAD_V


class TestSimulation(unittest.TestCase):

    @classmethod
    def setUp(cls):
        random.seed(12)

    @staticmethod
    def get_10_01_virus_dic():
        return {
            CON_K: {0:  4, 1:  3, 2:  2, 3:  2, 4:  6, 5:  4, 6:  4, 7:  2, 8:  6, 9:  5},
            DEC_K: {0: 31, 1: 23, 2: 23, 3: 22, 4: 22, 5: 27, 6: 36, 7: 22, 8: 30, 9: 38},
            STA_K: {0:  H, 1:  H, 2:  H, 3:  H, 4:  F, 5:  H, 6:  H, 7:  H, 8:  H, 9:  H}
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
        result = get_virus_simulation_t0(10, 0.1, (21, 39), (2, 7))
        expected_result = TestSimulation.get_10_01_virus_dic()
        self.assertEqual(result, expected_result)

    def test_update_infection_period(self):
        virus_dic = TestSimulation.get_10_01_virus_dic()
        # 4 is already infected
        # 1 and 9 are going to be infected
        update_infection_period([1, 9], virus_dic)
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][2], H)
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][9], F)

    def test_increment_pandemic_1_day(self):
        env_dic = TestSimulation.get_10_01_2_environment_dic()
        virus_dic = {
            CON_K: {0: 4,  1: -2, 2: -5, 3:  2, 4:  6, 5: -9, 6: -3, 7:  2, 8:  6, 9:  5},
            DEC_K: {0: 31, 1:  1, 2:  0, 3: 22, 4: 22, 5:  0, 6:  1, 7: 22, 8: 30, 9: 38},
            STA_K: {0:  H, 1:  F, 2:  D, 3:  H, 4:  F, 5:  M, 6:  F, 7:  F, 8:  H, 9:  H}
        }
        increment_pandemic_1_day(env_dic, virus_dic)
        self.assertEqual(virus_dic[CON_K][0], 4)
        self.assertEqual(virus_dic[DEC_K][0], 31)
        self.assertEqual(virus_dic[STA_K][0], H)

        self.assertEqual(virus_dic[CON_K][1], -3)
        self.assertEqual(virus_dic[DEC_K][1], 0)
        self.assertEqual(virus_dic[STA_K][1], M)

        self.assertEqual(virus_dic[CON_K][2], -5)
        self.assertEqual(virus_dic[DEC_K][2], 0)
        self.assertEqual(virus_dic[STA_K][2], D)

        self.assertEqual(virus_dic[CON_K][5], -9)
        self.assertEqual(virus_dic[DEC_K][5], 0)
        self.assertEqual(virus_dic[STA_K][5], M)

        self.assertEqual(virus_dic[CON_K][6], -4)
        self.assertEqual(virus_dic[DEC_K][6], 0)
        self.assertEqual(virus_dic[STA_K][6], M)

    def test_propagate_to_houses_contagious_people(self):
        env_dic = TestSimulation.get_10_01_2_environment_dic()
        virus_dic = {
            CON_K: {0: -9, 1:  3, 2:  2, 3:  2, 4: -9, 5:  4, 6:  4, 7:  2, 8:  6, 9:  5},
            DEC_K: {0: -5, 1: 23, 2: 23, 3: 22, 4: -5, 5: 27, 6: 36, 7: 22, 8: 30, 9: 38},
            STA_K: {0:  F, 1:  H, 2:  H, 3:  H, 4:  D, 5:  H, 6:  H, 7:  H, 8:  M, 9:  H}
        }
        propagate_to_houses(env_dic, virus_dic, 0.99)

        self.assertEqual(virus_dic[STA_K][0], F)
        self.assertEqual(virus_dic[STA_K][4], D)
        self.assertEqual(virus_dic[STA_K][8], M)
        # infected people contaminate
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][2], F)
        self.assertEqual(virus_dic[STA_K][3], F)
        # Dead people do not contaminate
        self.assertEqual(virus_dic[STA_K][5], H)
        self.assertEqual(virus_dic[STA_K][6], H)
        self.assertEqual(virus_dic[STA_K][7], H)
        # Immune people do not contaminate
        self.assertEqual(virus_dic[STA_K][9], H)

    def test_propagate_to_houses_noncontagious_people(self):
        env_dic = TestSimulation.get_10_01_2_environment_dic()
        virus_dic = {
            CON_K: {0: 4, 1: 3, 2: 2, 3: 2, 4: 6, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            DEC_K: {0: 31, 1: 23, 2: 23, 3: 22, 4: 22, 5: 27, 6: 36, 7: 22, 8: 30, 9: 38},
            STA_K: {0:  F, 1:  H, 2:  H, 3:  H, 4:  D, 5:  H, 6:  H, 7:  H, 8:  M, 9:  H}
        }
        propagate_to_houses(env_dic, virus_dic, 0.99)

        self.assertEqual(virus_dic[STA_K][1], H)
        self.assertEqual(virus_dic[STA_K][2], H)
        self.assertEqual(virus_dic[STA_K][3], H)

        self.assertEqual(virus_dic[STA_K][5], H)
        self.assertEqual(virus_dic[STA_K][6], H)
        self.assertEqual(virus_dic[STA_K][7], H)

        self.assertEqual(virus_dic[STA_K][9], H)

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
            CON_K: {0: 4,  1:  3, 2:  2, 3:  2, 4: -5, 5:  4, 6:  4, 7:  2, 8:  6, 9:  5},
            DEC_K: {0: 31, 1: 23, 2: 23, 3: 22, 4: -2, 5: 27, 6: 36, 7: 22, 8: 30, 9: 38},
            STA_K: {0:  H, 1:  H, 2:  H, 3:  F, 4:  D, 5:  H, 6:  H, 7:  H, 8:  H, 9:  H}
        }
        propagate_to_stores(env_dic, virus_dic, 0.99)
        # children do not go to stores
        self.assertEqual(virus_dic[STA_K][0], H)
        self.assertEqual(virus_dic[STA_K][1], H)
        self.assertEqual(virus_dic[STA_K][2], H)
        self.assertEqual(virus_dic[STA_K][8], H)
        self.assertEqual(virus_dic[STA_K][9], H)

    def test_propagate_to_stores_adult_notcontagious(self):
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
            CON_K: {0: 4,  1:  3, 2:  2, 3:  2, 4: -5, 5:  4, 6:  4, 7:  2, 8:  6, 9:  5},
            DEC_K: {0: 31, 1: 23, 2: 23, 3: 22, 4: -2, 5: 27, 6: 36, 7: 22, 8: 30, 9: 38},
            STA_K: {0:  H, 1:  F, 2:  H, 3:  H, 4:  H, 5:  H, 6:  H, 7:  H, 8:  H, 9:  H}
        }
        propagate_to_stores(env_dic, virus_dic, 0.99)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][0], H)
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][5], H)
        self.assertEqual(virus_dic[STA_K][8], H)
        self.assertEqual(virus_dic[STA_K][9], H)

    def test_propagate_to_stores_adult_contagious(self):
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
            CON_K: {0: 4,  1: -2, 2:  2, 3:  2, 4: -5, 5:  4, 6:  4, 7:  2, 8:  6, 9:  5},
            DEC_K: {0: 31, 1: 23, 2: 23, 3: 22, 4: -2, 5: 27, 6: 36, 7: 22, 8: 30, 9: 38},
            STA_K: {0:  H, 1:  F, 2:  H, 3:  H, 4:  H, 5:  H, 6:  H, 7:  H, 8:  H, 9:  H}
        }
        propagate_to_stores(env_dic, virus_dic, 0.99)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][0], H)
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][5], H)
        self.assertEqual(virus_dic[STA_K][8], H)
        self.assertEqual(virus_dic[STA_K][9], F)

    def test_propagate_to_workplaces_contagious(self):
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
            CON_K: {0: 4,  1: -2, 2: 2,  3:  2, 4: -5, 5:  4, 6:  4, 7:  2, 8:  6, 9:  5},
            DEC_K: {0: 31, 1: 23, 2: 23, 3: 22, 4: -2, 5: 27, 6: 36, 7: 22, 8: 30, 9: 38},
            STA_K: {0:  H, 1:  H, 2:  H, 3:  H, 4:  F, 5:  H, 6:  H, 7:  H, 8:  H, 9:  H}
        }
        propagate_to_workplaces(env_dic, virus_dic, 0.99)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_workplaces_notcontagious(self):
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
            CON_K: {0: 4,  1: -2, 2: 2,  3:  2, 4:  1, 5:  4, 6:  4, 7:  2, 8:  6, 9:  5},
            DEC_K: {0: 31, 1: 23, 2: 23, 3: 22, 4: 17, 5: 27, 6: 36, 7: 22, 8: 30, 9: 38},
            STA_K: {0:  H, 1:  H, 2:  H, 3:  H, 4:  F, 5:  H, 6:  H, 7:  H, 8:  H, 9:  H}
        }
        propagate_to_workplaces(env_dic, virus_dic, 0.99)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][1], H)
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_workplaces_noworkers(self):
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
            CON_K: {0: -2, 1: -2, 2: -2, 3: -2, 4:  1, 5:  4, 6: -2, 7:  2, 8:  6, 9:  5},
            DEC_K: {0: 31, 1: 23, 2: 23, 3: 22, 4: 17, 5: 27, 6: 36, 7: 22, 8: 30, 9: 38},
            STA_K: {0:  F, 1:  H, 2:  F, 3:  F, 4:  H, 5:  H, 6:  F, 7:  H, 8:  H, 9:  H}
        }
        propagate_to_workplaces(env_dic, virus_dic, 0.99)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][1], H)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], H)


if __name__ == '__main__':
    unittest.main()

