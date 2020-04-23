import random
import numpy as np
import unittest

from initiator.helper import get_infection_parameters
from simulator.dynamic_helper import update_infection_period, increment_pandemic_1_day, \
    propagate_to_houses, propagate_to_stores, propagate_to_workplaces, propagate_to_transportation
from simulator.keys import *
from simulator.simulation_helper import get_environment_simulation, get_virus_simulation_t0
from simulator.parameters import *

H = HEALTHY_V
F = INFECTED_V
M = IMMUNE_V
D = DEAD_V
P = HOSPITALIZED_V


class TestSimulation(unittest.TestCase):

    @classmethod
    def setUp(cls):
        random.seed(12)
        np.random.seed(seed=12)

    @staticmethod
    def get_virus_dic():
        return {
            CON_K: {0: 4, 1: 2, 2: 2, 3: 6, 4: 4, 5: 2, 6: 5, 7: 2, 8: 4, 9: 5},
            DEA_K: {0: 34, 1: 21, 2: 30, 3: 35, 4: 29, 5: 37, 6: 26, 7: 33, 8: 33, 9: 28},
            IMM_K: {0: 53, 1: 47, 2: 52, 3: 51, 4: 58, 5: 58, 6: 44, 7: 53, 8: 46, 9: 55},
            HOS_K: {0: 12, 1: 10, 2: 14, 3: 14, 4: 17, 5: 16, 6: 15, 7: 10, 8: 20, 9: 9},
            STA_K: {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            NC_K: 0
        }

    @staticmethod
    def get_10_01_virus_dic():
        return {
            CON_K: {0: 4, 1: 3, 2: 2, 3: 2, 4: 6, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            HOS_K: {0: 12, 1: 12, 2: 20, 3: 11, 4: 16, 5: 12, 6: 14, 7: 13, 8: 12, 9: 8},
            DEA_K: {0: 31, 1: 23, 2: 23, 3: 22, 4: 22, 5: 27, 6: 36, 7: 22, 8: 30, 9: 38},
            STA_K: {0: H, 1: H, 2: H, 3: H, 4: F, 5: H, 6: M, 7: H, 8: H, 9: H},
            NC_K: 0
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
            WI_K: {0: [5], 1: [4, 1]},
            ITI_K: {1: {1, 4, 5}, 4: {1, 4, 5}, 5: {1, 4, 5}},
            IBE_K: {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}
        }
        # to avoid changing all the test values, I added this Dict to test "get_environment_simulation"
        # and the other tests will be done with the old values =>get_10_01_2_environment_dic

    @staticmethod
    def get_10_01_2_environment_new_house_map_dic():
        return {
            IH_K: {0: 0, 1: 0, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 2, 8: 2, 9: 2},
            HI_K: {0: [0, 1], 1: [2, 3, 4, 5, 6], 2: [7, 8, 9]},
            IAD_K: {0: 1, 1: 1, 2: 1, 3: 1, 4: 0, 5: 0, 6: 0, 7: 1, 8: 1, 9: 0},
            IAG_K: {0: 35, 1: 47, 2: 33, 3: 23, 4: 2, 5: 15, 6: 13, 7: 26, 8: 37, 9: 0},
            IW_K: {2: 0, 1: 1},
            WI_K: {0: [2], 1: [1]},
            HA_K: {0: [0, 1], 1: [2, 3], 2: [7, 8]},
            HS_K: {0: 0, 1: 0, 2: 0},
            SH_K: {0: [0, 1, 2]},
            ITI_K: {2: {1, 2}, 1: {1, 2}}
        }

    def test_build_environment_dic(self):
        params_test = {
            nindividual_key: 10,
            store_per_house_key: 2,
            store_preference_key: 1,
            nb_1d_block_key: 5,
            remote_work_key: 0.5
        }

        result = get_environment_simulation(params_test)
        expected_result = TestSimulation.get_10_01_2_environment_new_house_map_dic()
        self.assertTrue(IBE_K in result.keys())
        self.assertTrue(HB_K in result.keys())
        # We delete them in order to avoid including 100 values dictionnary in the test
        # we verified they exists it should be enough
        del result[IBE_K]
        del result[HB_K]
        self.assertEqual(result, expected_result)

    def test_build_virus_dic(self):
        params_dic = {
            nindividual_key: 10,
            innoculation_number_key: 2,
            contagion_bounds_key: (2, 7),
            hospitalization_bounds_key: (7, 21),
            death_bounds_key: (21, 39),
            immunity_bounds_key: (35, 65)
        }
        result = get_virus_simulation_t0(params_dic)
        expected_result = TestSimulation.get_virus_dic()
        self.assertEqual(result[CON_K], expected_result[CON_K])
        self.assertEqual(result[HOS_K], expected_result[HOS_K])
        self.assertEqual(result[DEA_K], expected_result[DEA_K])
        self.assertEqual(result[STA_K], expected_result[STA_K])

    def test_update_infection_period(self):
        virus_dic = TestSimulation.get_10_01_virus_dic()
        # 4 is already infected
        # 1 and 9 are going to be infected
        update_infection_period([1, 9, 6], virus_dic)
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][2], H)
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][6], M)
        self.assertEqual(virus_dic[STA_K][9], F)
        self.assertEqual(virus_dic[NC_K], 2)

    def test_increment_pandemic_1_day(self):
        random.seed(22)
        env_dic = TestSimulation.get_10_01_2_environment_dic()

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
        increment_pandemic_1_day(env_dic, virus_dic)
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
        self.assertEqual(virus_dic[STA_K][3], P)

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

    def test_propagate_to_houses_contagious_people(self):
        env_dic = TestSimulation.get_10_01_2_environment_dic()
        virus_dic = {
            CON_K: {0: -9, 1: 3, 2: 2, 3: 2, 4: -9, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            HOS_K: {0: 12, 1: 12, 2: 20, 3: 11, 4: 16, 5: 12, 6: 14, 7: 13, 8: 12, 9: 8},
            DEA_K: {0: -5, 1: 23, 2: 23, 3: 22, 4: -5, 5: 27, 6: 36, 7: 22, 8: 30, 9: 38},
            IMM_K: {0: 53, 1: 47, 2: 52, 3: 51, 4: 58, 5: 58, 6: 44, 7: 53, 8: 46, 9: 55},
            STA_K: {0: F, 1: H, 2: H, 3: H, 4: D, 5: H, 6: H, 7: H, 8: M, 9: H},
            NC_K: 0
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

    def test_propagate_to_houses_careful_daddy_people(self):
        env_dic = TestSimulation.get_10_01_2_environment_dic()
        virus_dic = {
            CON_K: {0: -9, 1: 3, 2: 2, 3: 2, 4: -9, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            HOS_K: {0: 12, 1: 12, 2: 20, 3: 11, 4: 16, 5: 12, 6: 14, 7: 13, 8: 12, 9: 8},
            DEA_K: {0: -5, 1: 23, 2: 23, 3: 22, 4: -5, 5: 27, 6: 36, 7: 22, 8: 30, 9: 38},
            IMM_K: {0: 53, 1: 47, 2: 52, 3: 51, 4: 58, 5: 58, 6: 44, 7: 53, 8: 46, 9: 55},
            STA_K: {0: F, 1: H, 2: H, 3: H, 4: D, 5: H, 6: H, 7: H, 8: M, 9: H},
            NC_K: 0
        }
        env_dic[IBE_K] = {0: 0.01, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}
        propagate_to_houses(env_dic, virus_dic, 0.99)

        self.assertEqual(virus_dic[STA_K][0], F)
        # careful people do not contaminate
        self.assertEqual(virus_dic[STA_K][1], H)
        self.assertEqual(virus_dic[STA_K][2], H)
        self.assertEqual(virus_dic[STA_K][3], H)

    def test_propagate_to_houses_dangerous_daddy_people(self):
        env_dic = {
            HI_K: {0: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            IBE_K: {0: 0.9, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}
        }
        virus_dic = {
            CON_K: {0: -9, 1: 3, 2: 2, 3: 2, 4: -9, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            STA_K: {0: F, 1: H, 2: H, 3: H, 4: H, 5: H, 6: H, 7: H, 8: H, 9: H},
            NC_K: 0
        }
        propagate_to_houses(env_dic, virus_dic, 0.5)
        self.assertEqual(virus_dic[STA_K][0], F)
        self.assertEqual(sum(virus_dic[STA_K].values()), 5)

    def test_propagate_to_houses_very_carefull_daddy_people(self):
        env_dic = {
            HI_K: {0: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            IBE_K: {0: 0.0000001, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}
        }
        virus_dic = {
            CON_K: {0: -9, 1: 3, 2: 2, 3: 2, 4: -9, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            STA_K: {0: F, 1: H, 2: H, 3: H, 4: H, 5: H, 6: H, 7: H, 8: H, 9: H},
            NC_K: 0
        }
        propagate_to_houses(env_dic, virus_dic, 0.99)
        self.assertEqual(virus_dic[STA_K][0], F)
        self.assertEqual(sum(virus_dic[STA_K].values()), 1)

    def test_propagate_to_houses_very_dangerous_daddy_people(self):
        env_dic = {
            HI_K: {0: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            IBE_K: {0: 0.99, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}
        }
        virus_dic = {
            CON_K: {0: -9, 1: 3, 2: 2, 3: 2, 4: -9, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            STA_K: {0: F, 1: H, 2: H, 3: H, 4: H, 5: H, 6: H, 7: H, 8: H, 9: H},
            NC_K: 0
        }
        propagate_to_houses(env_dic, virus_dic, 0.99)
        self.assertEqual(virus_dic[STA_K][0], F)
        self.assertEqual(sum(virus_dic[STA_K].values()), 10)

    def test_propagate_to_houses_noncontagious_people(self):
        env_dic = TestSimulation.get_10_01_2_environment_dic()
        virus_dic = {
            CON_K: {0: 4, 1: 3, 2: 2, 3: 2, 4: 6, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            HOS_K: {0: 12, 1: 12, 2: 20, 3: 11, 4: 16, 5: 12, 6: 14, 7: 13, 8: 12, 9: 8},
            DEA_K: {0: 31, 1: 23, 2: 23, 3: 22, 4: 22, 5: 27, 6: 36, 7: 22, 8: 30, 9: 38},
            IMM_K: {0: 53, 1: 47, 2: 52, 3: 51, 4: 58, 5: 58, 6: 44, 7: 53, 8: 46, 9: 55},
            STA_K: {0: F, 1: H, 2: H, 3: H, 4: D, 5: H, 6: H, 7: H, 8: M, 9: H},
            NC_K: 0
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
            CON_K: {0: 4, 1: 3, 2: 2, 3: 2, 4: -5, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            HOS_K: {0: 12, 1: 12, 2: 20, 3: 11, 4: 16, 5: 12, 6: 14, 7: 13, 8: 12, 9: 8},
            DEA_K: {0: 31, 1: 23, 2: 23, 3: 22, 4: -2, 5: 27, 6: 36, 7: 22, 8: 30, 9: 38},
            IMM_K: {0: 53, 1: 47, 2: 52, 3: 51, 4: 58, 5: 58, 6: 44, 7: 53, 8: 46, 9: 55},
            STA_K: {0: H, 1: H, 2: H, 3: F, 4: D, 5: H, 6: H, 7: H, 8: H, 9: H},
            NC_K: 0
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
            CON_K: {0: 4, 1: 3, 2: 2, 3: 2, 4: -5, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            HOS_K: {0: 12, 1: 12, 2: 20, 3: 11, 4: 16, 5: 12, 6: 14, 7: 13, 8: 12, 9: 8},
            DEA_K: {0: 31, 1: 23, 2: 23, 3: 22, 4: -2, 5: 27, 6: 36, 7: 22, 8: 30, 9: 38},
            IMM_K: {0: 53, 1: 47, 2: 52, 3: 51, 4: 58, 5: 58, 6: 44, 7: 53, 8: 46, 9: 55},
            STA_K: {0: H, 1: F, 2: H, 3: H, 4: H, 5: H, 6: H, 7: H, 8: H, 9: H},
            NC_K: 0
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
            CON_K: {0: 4, 1: -2, 2: 2, 3: 2, 4: -5, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            HOS_K: {0: 12, 1: 12, 2: 20, 3: 11, 4: 16, 5: 12, 6: 14, 7: 13, 8: 12, 9: 8},
            DEA_K: {0: 31, 1: 23, 2: 23, 3: 22, 4: -2, 5: 27, 6: 36, 7: 22, 8: 30, 9: 38},
            IMM_K: {0: 53, 1: 47, 2: 52, 3: 51, 4: 58, 5: 58, 6: 44, 7: 53, 8: 46, 9: 55},
            STA_K: {0: H, 1: F, 2: H, 3: H, 4: H, 5: H, 6: H, 7: H, 8: H, 9: H},
            NC_K: 0
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
            IW_K: {1: 1, 4: 1, 5: 0},
            WI_K: {0: [5], 1: [4, 1]},
            IBE_K: {1: 1, 4: 1, 5: 1}
        }
        virus_dic = {
            CON_K: {1: -2, 4: -5, 5: 4},
            STA_K: {1: H, 4: F, 5: H},
            NC_K: 0
        }
        propagate_to_workplaces(env_dic, virus_dic, 0.99)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_workplaces_dangerous(self):
        env_dic = {
            IW_K: {1: 1, 4: 1, 5: 0},
            WI_K: {0: [5], 1: [4, 1]},
            IBE_K: {1: 1, 4: 100, 5: 1}
        }
        virus_dic = {
            CON_K: {1: -2, 4: -5, 5: 4},
            STA_K: {1: H, 4: F, 5: H},
            NC_K: 0
        }
        propagate_to_workplaces(env_dic, virus_dic, 0.01)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_workplaces_carefull(self):
        env_dic = {
            IW_K: {1: 1, 4: 1, 5: 0},
            WI_K: {0: [5], 1: [4, 1]},
            IBE_K: {1: 1, 4: 0.0001, 5: 1}
        }
        virus_dic = {
            CON_K: {1: -2, 4: -5, 5: 4},
            STA_K: {1: H, 4: F, 5: H},
            NC_K: 0
        }
        propagate_to_workplaces(env_dic, virus_dic, 0.99)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][1], H)
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_workplaces_notcontagious(self):
        env_dic = {
            IW_K: {1: 1, 4: 1, 5: 0},
            WI_K: {0: [5], 1: [4, 1]},
            IBE_K: {1: 1, 4: 1, 5: 1}
        }
        virus_dic = {
            CON_K: {1: -2, 4: 1, 5: 4},
            STA_K: {1: H,  4: F, 5: H},
            NC_K: 0
        }
        propagate_to_workplaces(env_dic, virus_dic, 0.99)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][1], H)
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_workplaces_noworkers(self):
        env_dic = {
            IW_K: {1: 1, 4: 1, 5: 0},
            WI_K: {0: [5], 1: [4, 1]},
            IBE_K: {1: 1, 4: 1, 5: 1}
        }
        virus_dic = {
            CON_K: {1: -2, 4: 1, 5: 4},
            STA_K: {1: H,  4: H, 5: H},
            NC_K: 0
        }
        propagate_to_workplaces(env_dic, virus_dic, 0.99)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][1], H)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_transportation(self):
        env_dic = {
            IW_K: {0: 1, 1: 1, 4: 1, 5: 0},
            ITI_K: {0: {0, 5}, 4: {4}, 5: {0, 5}},
            IBE_K: {0: 1, 1: 1, 4: 1, 5: 1}
        }
        virus_dic = {
            CON_K: {0: -2, 1: -2, 4: 1, 5: 4},
            STA_K: {0:  F, 1:  H, 4: H, 5: H},
            NC_K: 0
        }
        propagate_to_transportation(env_dic, virus_dic, 1)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], F)

    def test_propagate_to_transportation_carefull_people(self):
        env_dic = {
            IW_K: {0: 1, 1: 1, 4: 1, 5: 0},
            ITI_K: {0: {0, 5}, 4: {4}, 5: {0, 5}},
            IBE_K: {0: 0.00001, 1: 1, 4: 1, 5: 1}
        }
        virus_dic = {
            CON_K: {0: -2, 1: -2, 4: 1, 5: 4},
            STA_K: {0:  F, 1:  H, 4: H, 5: H},
            NC_K: 0
        }
        propagate_to_transportation(env_dic, virus_dic, 1)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_transportation_dangerous_people(self):
        env_dic = {
            IW_K: {0: 1, 1: 1, 4: 1, 5: 0},
            ITI_K: {0: {0, 5}, 4: {4}, 5: {0, 5}},
            IBE_K: {0: 999, 1: 1, 4: 1, 5: 1}
        }
        virus_dic = {
            CON_K: {0: -2, 1: -2, 4: 1, 5: 4},
            STA_K: {0:  F, 1:  H, 4: H, 5: H},
            NC_K: 0
        }
        propagate_to_transportation(env_dic, virus_dic, 0.001)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], F)


if __name__ == '__main__':
    unittest.main()
