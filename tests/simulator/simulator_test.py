import random
import unittest

import numpy as np

from simulator.constants.keys import *
from simulator.constants.keys import nindividual_key, innoculation_number_key, nb_1d_block_key, remote_work_key, \
    store_per_house_key, store_preference_key, store_nb_choice_key, transport_contact_cap_key, contagion_bounds_key, \
    hospitalization_bounds_key, death_bounds_key, immunity_bounds_key
from simulator.helper.dynamic import update_infection_period
from simulator.helper.environment import get_environment_simulation
from simulator.helper.simulation import get_virus_simulation_t0

H = HEALTHY_V
F = INFECTED_V
M = IMMUNE_V
D = DEAD_V
P = HOSPITALIZED_V
I = ISOLATED_V


class TestSimulation(unittest.TestCase):

    @classmethod
    def setUp(cls):
        random.seed(12)
        np.random.seed(seed=12)

    def test_build_environment_dic(self):
        params_test = {
            nindividual_key: 10,
            store_per_house_key: 2,
            store_preference_key: 1,
            nb_1d_block_key: 5,
            remote_work_key: 0.5,
            store_nb_choice_key: 3,
            transport_contact_cap_key: 10
        }
        result = get_environment_simulation(params_test)
        self.assertTrue(IH_K in result.keys())
        self.assertTrue(HI_K in result.keys())
        self.assertTrue(IAD_K in result.keys())
        self.assertTrue(IAG_K in result.keys())
        self.assertTrue(IW_K in result.keys())
        self.assertTrue(WI_K in result.keys())
        self.assertTrue(HA_K in result.keys())
        self.assertTrue(HS_K in result.keys())
        self.assertTrue(ITI_K in result.keys())
        self.assertTrue(IDEA_K in result.keys())
        self.assertTrue(IHOS_K in result.keys())

    def test_build_virus_dic(self):
        params_dic = {
            nindividual_key: 10,
            innoculation_number_key: 2,
            contagion_bounds_key: (2, 7),
            hospitalization_bounds_key: (7, 21),
            death_bounds_key: (21, 39),
            immunity_bounds_key: (35, 65),
        }
        result = get_virus_simulation_t0(params_dic)
        expected_result = {
            CON_K: {0: 4, 1: 2, 2: 2, 3: 6, 4: 4, 5: 2, 6: 5, 7: 2, 8: 4, 9: 5},
            DEA_K: {0: 34, 1: 21, 2: 30, 3: 35, 4: 29, 5: 37, 6: 26, 7: 33, 8: 33, 9: 28},
            IMM_K: {0: 53, 1: 47, 2: 52, 3: 51, 4: 58, 5: 58, 6: 44, 7: 53, 8: 46, 9: 55},
            HOS_K: {0: 12, 1: 10, 2: 14, 3: 14, 4: 17, 5: 16, 6: 15, 7: 10, 8: 20, 9: 9},
            STA_K: {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0},
            NC_K: 0
        }
        self.assertEqual(result[CON_K], expected_result[CON_K])
        self.assertEqual(result[HOS_K], expected_result[HOS_K])
        self.assertEqual(result[DEA_K], expected_result[DEA_K])
        self.assertEqual(result[STA_K], expected_result[STA_K])

    def test_update_infection_period(self):
        # 4 is already infected
        # 1 and 9 are going to be infected
        # There are going to be 2 new cases
        virus_dic = {
            STA_K: {0: H, 1: H, 2: H, 3: H, 4: F, 5: H, 6: M, 7: H, 8: H, 9: H},
            NC_K: 0
        }
        update_infection_period([1, 9, 6], virus_dic)
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][2], H)
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][6], M)
        self.assertEqual(virus_dic[STA_K][9], F)
        self.assertEqual(virus_dic[NC_K], 2)


if __name__ == '__main__':
    unittest.main()
