import random
import unittest

import numpy as np

from simulator.dynamic_helper import propagate_to_workplaces
from tests.constant import *


class TestSimulation(unittest.TestCase):

    @classmethod
    def setUp(cls):
        random.seed(12)
        np.random.seed(seed=12)

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
        propagate_to_workplaces(env_dic, virus_dic, 0.99, 0.1)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_workplaces_contagious_remote_work(self):
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
        propagate_to_workplaces(env_dic, virus_dic, 0.99, 0.99)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][1], H)
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
        propagate_to_workplaces(env_dic, virus_dic, 0.01, 0.1)
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
        propagate_to_workplaces(env_dic, virus_dic, 0.99, 0.98)
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
            STA_K: {1: H, 4: F, 5: H},
            NC_K: 0
        }
        propagate_to_workplaces(env_dic, virus_dic, 0.99, 0.98)
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
            STA_K: {1: H, 4: H, 5: H},
            NC_K: 0
        }
        propagate_to_workplaces(env_dic, virus_dic, 0.99, 0.98)
        # adults who go to the store propagate the virus
        self.assertEqual(virus_dic[STA_K][1], H)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], H)


if __name__ == '__main__':
    unittest.main()
