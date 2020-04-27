import random
import unittest

import numpy as np

from simulator.dynamic_helper import propagate_to_stores
from tests.constant import *


class TestSimulation(unittest.TestCase):

    @classmethod
    def setUp(cls):
        random.seed(12)
        np.random.seed(seed=12)

    def test_propagate_to_stores_child(self):
        env_dic = {
            HA_K: {0: [0, 1], 1: [4, 5], 2: [8, 9]},
            HS_K: {0: [0, 0, 0], 1: [1, 1, 1], 2: [0, 0, 0]},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
            IBE_K: {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1},
        }
        virus_dic = {
            CON_K: {0: 4, 1: 3, 2: 2, 3: 2, 4: -5, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            STA_K: {0: H, 1: H, 2: H, 3: F, 4: D, 5: H, 6: H, 7: H, 8: H, 9: H},
            NC_K: 0
        }
        propagate_to_stores(env_dic, virus_dic, 0.99, 0.95)
        # children do not go to stores
        self.assertEqual(virus_dic[STA_K][0], H)
        self.assertEqual(virus_dic[STA_K][1], H)
        self.assertEqual(virus_dic[STA_K][2], H)
        self.assertEqual(virus_dic[STA_K][8], H)
        self.assertEqual(virus_dic[STA_K][9], H)

    def test_propagate_to_stores_adult_notcontagious(self):
        env_dic = {
            HA_K: {0: [0, 1], 1: [4, 5], 2: [8, 9]},
            HS_K: {0: [0, 0, 0], 1: [1, 1, 1], 2: [0, 0, 0]},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
            IBE_K: {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1},
        }
        virus_dic = {
            CON_K: {0: 4, 1: 3, 2: 2, 3: 2, 4: -5, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            STA_K: {0: H, 1: F, 2: H, 3: H, 4: H, 5: H, 6: H, 7: H, 8: H, 9: H},
            NC_K: 0
        }
        propagate_to_stores(env_dic, virus_dic, 0.99, 0.95)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][0], H)
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][5], H)
        self.assertEqual(virus_dic[STA_K][8], H)
        self.assertEqual(virus_dic[STA_K][9], H)

    def test_propagate_to_stores_adult_contagious(self):
        env_dic = {
            HA_K: {0: [0, 1], 1: [4, 5], 2: [8, 9]},
            HS_K: {0: [0, 0, 0], 1: [1, 1, 1], 2: [0, 0, 0]},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
            IBE_K: {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}
        }
        virus_dic = {
            CON_K: {0: 4, 1: -2, 2: 2, 3: 2, 4: -5, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            STA_K: {0: H, 1:  F, 2: H, 3: H, 4:  H, 5: H, 6: H, 7: H, 8: H, 9: H},
            NC_K: 0
        }
        propagate_to_stores(env_dic, virus_dic, 0.99, 0.95)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][0], H)
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][5], H)
        self.assertEqual(virus_dic[STA_K][8], H)
        self.assertEqual(virus_dic[STA_K][9], F)

    def test_propagate_to_stores_adult_contagious_bad_gobal_behavior(self):
        env_dic = {
            HA_K: {0: [0, 1], 1: [4, 5], 2: [8, 9]},
            HS_K: {0: [1, 0, 0], 1: [1, 1, 1], 2: [1, 0, 0]},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
            IBE_K: {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}
        }
        virus_dic = {
            CON_K: {0: 4, 1: -2, 2: 2, 3: 2, 4: -5, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            STA_K: {0: H, 1:  F, 2: H, 3: H, 4:  H, 5: H, 6: H, 7: H, 8: H, 9: H},
            NC_K: 0
        }
        propagate_to_stores(env_dic, virus_dic, 0.99, 0.01)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][0], H)
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][5], H)
        self.assertEqual(virus_dic[STA_K][8], H)
        self.assertEqual(virus_dic[STA_K][9], F)

    def test_propagate_to_stores_adult_contagious_bad_individual_behavior(self):
        # Individual 1 has bad behavior and goes to a store he should not go to
        env_dic = {
            HA_K: {0: [0, 1], 1: [4, 5], 2: [8, 9]},
            HS_K: {0: [1, 0, 0], 1: [1, 1, 1], 2: [0, 0, 0]},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
            IBE_K: {0: 1, 1: 100, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}
        }
        virus_dic = {
            CON_K: {0: 4, 1: -2, 2: 2, 3: 2, 4: -5, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            STA_K: {0: H, 1:  F, 2: H, 3: H, 4:  H, 5: H, 6: H, 7: H, 8: H, 9: H},
            NC_K: 0
        }
        propagate_to_stores(env_dic, virus_dic, 0.99, 0.95)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][0], H)
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][5], H)
        self.assertEqual(virus_dic[STA_K][8], H)
        self.assertEqual(virus_dic[STA_K][9], F)

    def test_propagate_to_stores_adult_contagious_bad_2individual_behavior(self):
        # Both individual 1 and 9 has bad behavior and go to a store they should not go to
        env_dic = {
            HA_K: {0: [0, 1], 1: [4, 5], 2: [8, 9]},
            HS_K: {0: [1, 0, 0], 1: [1, 1, 1], 2: [1, 0, 0]},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
            IBE_K: {0: 1, 1: 100, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 100}
        }
        virus_dic = {
            CON_K: {0: 4, 1: -2, 2: 2, 3: 2, 4: -5, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            STA_K: {0: H, 1:  F, 2: H, 3: H, 4:  H, 5: H, 6: H, 7: H, 8: H, 9: H},
            NC_K: 0
        }
        propagate_to_stores(env_dic, virus_dic, 0.99, 0.95)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][0], H)
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][5], H)
        self.assertEqual(virus_dic[STA_K][8], H)
        self.assertEqual(virus_dic[STA_K][9], F)

    def test_propagate_to_2_stores_adult_contagious(self):
        # A corriger
        env_dic = {
            HA_K: {0: [0, 1], 1: [4, 5], 2: [8, 9]},
            HS_K: {0: [0, 0, 0], 1: [1, 1, 1], 2: [0, 0, 0]},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
            IBE_K: {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}
        }
        virus_dic = {
            CON_K: {0: 4, 1: -2, 2: -3, 3: 2, 4: -5, 5: -4, 6: 4, 7: 2, 8: 6, 9: 5},
            STA_K: {0: H, 1: F, 2: F, 3: H, 4: H, 5: F, 6: H, 7: H, 8: H, 9: H},
            NC_K: 0
        }
        propagate_to_stores(env_dic, virus_dic, 0.99, 0.95)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][0], H)
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][5], F)
        self.assertEqual(virus_dic[STA_K][8], H)
        self.assertEqual(virus_dic[STA_K][9], F)


if __name__ == '__main__':
    unittest.main()
