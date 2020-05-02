import random
import unittest

from simulator.helper.simulation import get_infection_parameters
from simulator.helper.dynamic import increment_pandemic_1_day, decide_hospitalization
from tests.constant import *


class TestSimulation(unittest.TestCase):

    @classmethod
    def setUp(cls):
        random.seed(12)

    @staticmethod
    def look_for_good_seed(self):
        for i in range(100):
            random.seed(i)
            print(i, random.random())

    def test_increment_pandemic_1_day(self):
        random.seed(22)
        env_dic = {
            HI_K: {0: [0, 1, 2, 3], 1: [4, 5, 6, 7], 2: [8, 9]},
            IAG_K: {0: 26, 1: 51, 2: 13, 3: 2, 4: 35, 5: 33, 6: 6, 7: 1, 8: 27, 9: 20},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
        }

        def get_infection_params():
            return get_infection_parameters(2, 7, 7, 21, 21, 39, 30, 60)

        virus_dic = {
            CON_K: {0: 4, 1: -2, 2: -5, 3: -4, 4: 6, 5: -9, 6: -3, 7: 2, 8: -9, 9: 5},
            HOS_K: {0: 12, 1: 12, 2: 20, 3: 1, 4: 16, 5: 12, 6: 14, 7: 13, 8: -7, 9: 8},
            DEA_K: {0: 31, 1: 1, 2: 0, 3: 22, 4: 22, 5: 0, 6: 1, 7: 22, 8: -4, 9: 38},
            IMM_K: {0: 53, 1: 47, 2: 52, 3: 51, 4: 58, 5: 58, 6: 44, 7: 53, 8: 1, 9: 55},
            STA_K: {0: H, 1: F, 2: D, 3: F, 4: F, 5: M, 6: F, 7: F, 8: M, 9: H},
            FN_K: get_infection_params
        }
        env_dic[IAG_K][3] = 82
        increment_pandemic_1_day(env_dic, virus_dic, 100)
        self.assertEqual(virus_dic[CON_K][0], 4)
        self.assertEqual(virus_dic[HOS_K][0], 12)
        self.assertEqual(virus_dic[DEA_K][0], 31)
        self.assertEqual(virus_dic[STA_K][0], H)

        self.assertEqual(virus_dic[CON_K][1], -3)
        self.assertEqual(virus_dic[HOS_K][1], 11)
        self.assertEqual(virus_dic[DEA_K][1], 0)
        self.assertEqual(virus_dic[STA_K][1], M)

        self.assertEqual(virus_dic[CON_K][2], -5)
        self.assertEqual(virus_dic[HOS_K][2], 20)
        self.assertEqual(virus_dic[DEA_K][2], 0)
        self.assertEqual(virus_dic[STA_K][2], D)

        self.assertEqual(virus_dic[CON_K][3], -5)
        self.assertEqual(virus_dic[HOS_K][3], 0)
        self.assertEqual(virus_dic[DEA_K][3], 21)
        self.assertEqual(virus_dic[STA_K][3], F)

        self.assertEqual(virus_dic[CON_K][5], -9)
        self.assertEqual(virus_dic[DEA_K][5], 0)
        self.assertEqual(virus_dic[STA_K][5], M)

        self.assertEqual(virus_dic[CON_K][6], -4)
        self.assertEqual(virus_dic[HOS_K][6], 13)
        self.assertEqual(virus_dic[DEA_K][6], 0)
        self.assertEqual(virus_dic[STA_K][6], M)

        # Parameters have been reset
        self.assertEqual(virus_dic[CON_K][8], 6)
        self.assertEqual(virus_dic[HOS_K][8], 9)
        self.assertEqual(virus_dic[DEA_K][8], 23)
        self.assertEqual(virus_dic[IMM_K][8], 49)
        self.assertEqual(virus_dic[STA_K][8], H)

    def test_decide_hospitalization_isolated_cases(self):
        # i3 is going to be hospitalized
        # i3 lives in house h0
        # i1, i2 and i3 live in h0
        # i0 is infected, thus will be tested and isolated
        # i1 is immune and must stay like this and i2 is dead
        random.seed(89)
        env_dic = {
            HI_K: {0: [0, 1, 2, 3], 1: [4, 5, 6, 7]},
            IAG_K: {0: 26, 1: 51, 2: 13, 3: 92, 4: 35, 5: 33, 6: 6, 7: 1},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1},
        }

        virus_dic = {
            CON_K: {0: 4, 1: -2, 2: -5, 3: -4, 4: 6, 5: -9, 6: -3, 7: 2},
            HOS_K: {0: 1, 1: 12, 2: 20, 3: 0, 4: 16, 5: 12, 6: 14, 7: 13},
            DEA_K: {0: 31, 1: 1, 2: 0, 3: 22, 4: 22, 5: 0, 6: 1, 7: 22},
            IMM_K: {0: 53, 1: 47, 2: 52, 3: 51, 4: 58, 5: 58, 6: 44, 7: 53},
            STA_K: {0: F, 1: M, 2: D, 3: F, 4: F, 5: M, 6: F, 7: F}
        }
        decide_hospitalization(env_dic, virus_dic, 3)

        self.assertEqual(virus_dic[STA_K][3], P)
        self.assertEqual(virus_dic[STA_K][0], S)
        self.assertEqual(virus_dic[STA_K][1], M)
        self.assertEqual(virus_dic[STA_K][2], D)

    def test_increment_pandemic_1_day_isolated_cases(self):
        # i3 is going to be hospitalized
        # i3 lives in house h0
        # i1, i2 and i3 live in h0
        # i0 is infected, thus will be tested and isolated
        # i1 is immune and must stay like this and i2 is dead
        random.seed(14)
        env_dic = {
            HI_K: {0: [0, 1, 2, 3], 1: [4, 5, 6, 7], 2: [8, 9]},
            IAG_K: {0: 26, 1: 51, 2: 13, 3: 82, 4: 35, 5: 33, 6: 6, 7: 1, 8: 27, 9: 20},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
        }

        def get_infection_params():
            return get_infection_parameters(2, 7, 7, 21, 21, 39, 30, 60)

        virus_dic = {
            CON_K: {0: 4, 1: -2, 2: -5, 3: -4, 4: 6, 5: -9, 6: -3, 7: 2, 8: -9, 9: 5},
            HOS_K: {0: 2, 1: 12, 2: 20, 3: 1, 4: 16, 5: 12, 6: 14, 7: 13, 8: -7, 9: 8},
            DEA_K: {0: 31, 1: 1, 2: 0, 3: 22, 4: 22, 5: 0, 6: 1, 7: 22, 8: -4, 9: 38},
            IMM_K: {0: 53, 1: 47, 2: 52, 3: 51, 4: 58, 5: 58, 6: 44, 7: 53, 8: 1, 9: 55},
            STA_K: {0: F, 1: F, 2: D, 3: F, 4: F, 5: M, 6: F, 7: F, 8: M, 9: H},
            FN_K: get_infection_params
        }
        increment_pandemic_1_day(env_dic, virus_dic, 100)
        # person 0 will be isolated since a member of his family(person 3)is hospitalized (what a sad story for him)
        self.assertEqual(virus_dic[STA_K][0], S)
        self.assertEqual(virus_dic[STA_K][1], M)
        self.assertEqual(virus_dic[STA_K][2], D)
        self.assertEqual(virus_dic[STA_K][3], P)

    def test_increment_pandemic_1_day_hospitals_empty(self):
        # i0 and i1 are infected
        # Hospitals are empty and their mortality rate are low
        # They survive and become immune
        random.seed(22)
        env_dic = {
            HI_K: {0: [0, 1, 2, 3], 1: [4, 5, 6, 7], 2: [8, 9]},
            IAG_K: {0: 26, 1: 51, 2: 13, 3: 2, 4: 35, 5: 33, 6: 6, 7: 1, 8: 27, 9: 20},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
        }

        def get_infection_params():
            return get_infection_parameters(2, 7, 7, 21, 21, 39, 30, 60)

        virus_dic = {
            CON_K: {0: -8, 1: -9, 2: -5, 3: -4, 4: 6, 5: -9, 6: -3, 7: 2, 8: -9, 9: 5},
            HOS_K: {0: -5, 1: -6, 2: 20, 3: 1, 4: 16, 5: 12, 6: 14, 7: 13, 8: -7, 9: 8},
            DEA_K: {0: 1, 1: 1, 2: 0, 3: 22, 4: 22, 5: 0, 6: 1, 7: 22, 8: -4, 9: 38},
            IMM_K: {0: 53, 1: 47, 2: 52, 3: 51, 4: 58, 5: 58, 6: 44, 7: 53, 8: 1, 9: 55},
            STA_K: {0: F, 1: F, 2: P, 3: P, 4: P, 5: P, 6: P, 7: P, 8: P, 9: P},
            FN_K: get_infection_params
        }
        env_dic[IAG_K][0] = 82
        env_dic[IAG_K][1] = 15
        increment_pandemic_1_day(env_dic, virus_dic, 1)
        self.assertEqual(virus_dic[STA_K][0], M)
        self.assertEqual(virus_dic[STA_K][1], M)

    def test_increment_pandemic_1_day_hospitals_almost_full(self):
        # i0 and i1 are infected
        # Hospitals are almost full but i0 and i1 are not hospitalized
        # They survive and become immune
        random.seed(22)
        env_dic = {
            HI_K: {0: [0, 1, 2, 3], 1: [4, 5, 6, 7], 2: [8, 9]},
            IAG_K: {0: 26, 1: 51, 2: 13, 3: 2, 4: 35, 5: 33, 6: 6, 7: 1, 8: 27, 9: 20},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
        }

        def get_infection_params():
            return get_infection_parameters(2, 7, 7, 21, 21, 39, 30, 60)

        virus_dic = {
            CON_K: {0: -8, 1: -9, 2: -5, 3: -4, 4: 6, 5: -9, 6: -3, 7: 2, 8: -9, 9: 5},
            HOS_K: {0: -5, 1: -6, 2: 20, 3: 1, 4: 16, 5: 12, 6: 14, 7: 13, 8: -7, 9: 8},
            DEA_K: {0: 1, 1: 1, 2: 0, 3: 22, 4: 22, 5: 0, 6: 1, 7: 22, 8: -4, 9: 38},
            IMM_K: {0: 53, 1: 47, 2: 52, 3: 51, 4: 58, 5: 58, 6: 44, 7: 53, 8: 1, 9: 55},
            STA_K: {0: F, 1: F, 2: P, 3: P, 4: P, 5: P, 6: P, 7: P, 8: P, 9: P},
            FN_K: get_infection_params
        }
        env_dic[IAG_K][0] = 82
        env_dic[IAG_K][1] = 15
        increment_pandemic_1_day(env_dic, virus_dic, 0.06)
        self.assertEqual(virus_dic[STA_K][0], M)
        self.assertEqual(virus_dic[STA_K][1], M)

    def test_increment_pandemic_1_day_hospitals_almost_full_indiv_hospitalized(self):
        # i0 and i1 are hospitalized
        # i0 is 82 year old
        # Hospitals are completely full and i0's mortality rate are high
        # i1 survive and become immune but i0 dies
        random.seed(22)
        env_dic = {
            HI_K: {0: [0, 1, 2, 3], 1: [4, 5, 6, 7], 2: [8, 9]},
            IAG_K: {0: 26, 1: 51, 2: 13, 3: 2, 4: 35, 5: 33, 6: 6, 7: 1, 8: 27, 9: 20},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
        }

        def get_infection_params():
            return get_infection_parameters(2, 7, 7, 21, 21, 39, 30, 60)

        virus_dic = {
            CON_K: {0: -8, 1: -9, 2: -5, 3: -4, 4: 6, 5: -9, 6: -3, 7: 2, 8: -9, 9: 5},
            HOS_K: {0: -5, 1: -6, 2: 20, 3: 1, 4: 16, 5: 12, 6: 14, 7: 13, 8: -7, 9: 8},
            DEA_K: {0: 1, 1: 1, 2: 0, 3: 22, 4: 22, 5: 0, 6: 1, 7: 22, 8: -4, 9: 38},
            IMM_K: {0: 53, 1: 47, 2: 52, 3: 51, 4: 58, 5: 58, 6: 44, 7: 53, 8: 1, 9: 55},
            # Two hospitalized people (going to decision next day)
            STA_K: {0: P, 1: P, 2: P, 3: P, 4: P, 5: P, 6: P, 7: P, 8: P, 9: P},
            FN_K: get_infection_params
        }
        env_dic[IAG_K][0] = 82
        env_dic[IAG_K][1] = 15
        increment_pandemic_1_day(env_dic, virus_dic, 1.5)
        self.assertEqual(virus_dic[STA_K][0], D)
        self.assertEqual(virus_dic[STA_K][1], M)

    def test_increment_pandemic_1_day_hospitals_completely_full(self):
        # i0 and i1 are hospitalized
        # Hospitals are completely full
        # They both die
        random.seed(22)
        env_dic = {
            HI_K: {0: [0, 1, 2, 3], 1: [4, 5, 6, 7], 2: [8, 9]},
            IAG_K: {0: 26, 1: 51, 2: 13, 3: 2, 4: 35, 5: 33, 6: 6, 7: 1, 8: 27, 9: 20},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
        }

        def get_infection_params():
            return get_infection_parameters(2, 7, 7, 21, 21, 39, 30, 60)

        virus_dic = {
            CON_K: {0: -8, 1: -9, 2: -5, 3: -4, 4: 6, 5: -9, 6: -3, 7: 2, 8: -9, 9: 5},
            HOS_K: {0: -5, 1: -6, 2: 20, 3: 1, 4: 16, 5: 12, 6: 14, 7: 13, 8: -7, 9: 8},
            DEA_K: {0: 1, 1: 1, 2: 0, 3: 22, 4: 22, 5: 0, 6: 1, 7: 22, 8: -4, 9: 38},
            IMM_K: {0: 53, 1: 47, 2: 52, 3: 51, 4: 58, 5: 58, 6: 44, 7: 53, 8: 1, 9: 55},
            STA_K: {0: P, 1: P, 2: P, 3: P, 4: P, 5: P, 6: P, 7: P, 8: P, 9: P},
            FN_K: get_infection_params
        }
        env_dic[IAG_K][0] = 82
        env_dic[IAG_K][1] = 15
        increment_pandemic_1_day(env_dic, virus_dic, 0.005)
        self.assertEqual(virus_dic[STA_K][0], D)
        self.assertEqual(virus_dic[STA_K][1], D)


if __name__ == '__main__':
    unittest.main()
