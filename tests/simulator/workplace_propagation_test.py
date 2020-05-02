import random
import unittest

from simulator.helper.dynamic import propagate_to_workplaces
from tests.constant import *


class TestSimulation(unittest.TestCase):

    @classmethod
    def setUp(cls):
        random.seed(12)

    def test_propagate_to_workplaces_contagious(self):
        # i4 is infected and works at w1 like i1
        # i1 gets infected
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
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_workplaces_contagious_remote_work(self):
        # i4 is infected and works at w1 like i1
        # But both are working remote
        # Nobody gets infected
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
        self.assertEqual(virus_dic[STA_K][1], H)
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_workplaces_dangerous(self):
        # i4 is infected and works at w1 like i1
        # They should not be in touch but i4 has a very bad behavior
        # i1 gets infected
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
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_workplaces_carefull(self):
        # i4 is infected and works at w1 like i1
        # They work closely together but i4 has a very good behavior
        # i1 stays healthy
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
        propagate_to_workplaces(env_dic, virus_dic, 0.99, 0)
        self.assertEqual(virus_dic[STA_K][1], H)
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_workplaces_notcontagious(self):
        # i4 is infected but not contagious and works at w1 like i1
        # i1 stays healthy
        env_dic = {
            IW_K: {1: 1, 4: 1, 5: 0},
            WI_K: {0: [5], 1: [4, 1]},
            IBE_K: {1: 1, 4: 1, 5: 1}
        }
        virus_dic = {
            CON_K: {1: 8, 4: 1, 5: 4},
            STA_K: {1: H, 4: F, 5: H},
            NC_K: 0
        }
        propagate_to_workplaces(env_dic, virus_dic, 0.99, 0)
        self.assertEqual(virus_dic[STA_K][1], H)
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_workplaces_noworkers(self):
        # Everyone is healthy and stays like that
        env_dic = {
            IW_K: {1: 1, 4: 1, 5: 0},
            WI_K: {0: [5], 1: [4, 1]},
            IBE_K: {1: 1, 4: 1, 5: 1}
        }
        virus_dic = {
            CON_K: {1: 8, 4: 1, 5: 4},
            STA_K: {1: H, 4: H, 5: H},
            NC_K: 0
        }
        propagate_to_workplaces(env_dic, virus_dic, 0.99, 0)
        self.assertEqual(virus_dic[STA_K][1], H)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_workplaces_bad_behavior(self):
        # Nobody should go to work (remote parameter high
        # But i1 and i4 have bad behavior
        # And since i1 is contagious, i4 gets infected
        env_dic = {
            IW_K: {1: 1, 4: 1, 5: 0},
            WI_K: {0: [5], 1: [4, 1]},
            IBE_K: {1: 100, 4: 100, 5: 1}
        }
        virus_dic = {
            CON_K: {1: -2, 4: 1, 5: 4},
            STA_K: {1: F, 4: H, 5: H},
            NC_K: 0
        }
        propagate_to_workplaces(env_dic, virus_dic, 0.99, 0.98)
        self.assertEqual(virus_dic[STA_K][1], F)
        self.assertEqual(virus_dic[STA_K][4], F)
        self.assertEqual(virus_dic[STA_K][5], H)


if __name__ == '__main__':
    unittest.main()
