import random
import unittest

import numpy as np

from simulator.dynamic_helper import propagate_to_transportation
from tests.constant import *


class TestSimulation(unittest.TestCase):

    @classmethod
    def setUp(cls):
        random.seed(12)
        np.random.seed(seed=12)

    def test_propagate_to_transportation(self):
        env_dic = {
            IW_K: {0: 1, 1: 1, 4: 1, 5: 0},
            ITI_K: {0: {0, 5}, 4: {4}, 5: {0, 5}},
            IBE_K: {0: 1, 1: 1, 4: 1, 5: 1}
        }
        virus_dic = {
            CON_K: {0: -2, 1: -2, 4: 1, 5: 4},
            STA_K: {0: F, 1: H, 4: H, 5: H},
            NC_K: 0
        }
        propagate_to_transportation(env_dic, virus_dic, 1, 0.1)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], F)

    def test_propagate_to_transportation_remote_work(self):
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
        propagate_to_transportation(env_dic, virus_dic, 1, 0.99)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_transportation_carefull_people(self):
        env_dic = {
            IW_K: {0: 1, 1: 1, 4: 1, 5: 0},
            ITI_K: {0: {0, 5}, 4: {4}, 5: {0, 5}},
            IBE_K: {0: 0.00001, 1: 1, 4: 1, 5: 1}
        }
        virus_dic = {
            CON_K: {0: -2, 1: -2, 4: 1, 5: 4},
            STA_K: {0: F, 1: H, 4: H, 5: H},
            NC_K: 0
        }
        propagate_to_transportation(env_dic, virus_dic, 1, 0.98)
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
            STA_K: {0: F, 1: H, 4: H, 5: H},
            NC_K: 0
        }
        propagate_to_transportation(env_dic, virus_dic, 0.001, 0.1)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], F)


if __name__ == '__main__':
    unittest.main()
