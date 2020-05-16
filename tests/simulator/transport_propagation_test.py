import random
import unittest

from simulator.helper.dynamic import propagate_to_transportation
from tests.constant import *
from tests.utils import g_d


class TestSimulation(unittest.TestCase):

    @classmethod
    def setUp(cls):
        random.seed(12)

    def test_propagate_to_transportation(self):
        # i0 is infected and goes to work
        # He meets i5 in transportation and infects him
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
        propagate_to_transportation(env_dic, virus_dic, 1, 0.1, 10)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], F)

    def test_propagate_to_transportation_isolated(self):
        # i0 is isolated
        # Everyone stays safe
        env_dic = {
            IW_K: {0: 1, 1: 1, 4: 1, 5: 0},
            ITI_K: {0: {0, 5}, 4: {4}, 5: {0, 5}},
            IBE_K: {0: 1, 1: 1, 4: 1, 5: 1}
        }
        virus_dic = {
            CON_K: {0: -2, 1: -2, 4: 1, 5: 4},
            STA_K: {0: S, 1: H, 4: H, 5: H},
            NC_K: 0
        }
        propagate_to_transportation(env_dic, virus_dic, 1, 0.1, 10)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_transportation_remote_work(self):
        # i0 is infected and contagious but he is working from hom (99% remote parameter)
        # Nobody is infected
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
        propagate_to_transportation(env_dic, virus_dic, 1, 0.99, 10)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_transportation_carefull_people(self):
        # i0 is infected and contagious but he is very carefull
        # Nobody is infected
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
        propagate_to_transportation(env_dic, virus_dic, 1, 0.98, 10)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_transportation_dangerous_people(self):
        # i0 is infected and contagious and has a very bad behavior
        # he infects i5
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
        propagate_to_transportation(env_dic, virus_dic, 0.001, 0.1, 10)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], F)

    def test_propagate_to_transportation_bad_behavior(self):
        # i0 is infected and contagious and has a very bad behavior
        # he infects i5
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
        propagate_to_transportation(env_dic, virus_dic, 0.001, 0.999, 10)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], F)

    def test_propagate_to_transportation2(self):
        # i0 is infected and goes to work
        # He meets i5 in transportation and infects him
        env_dic = {
            IW_K: g_d([1, 1, 2, 2, 1, 0]),
            ITI_K: g_d([[0, 5], [4, 2], [1, 1], [2, 2], [0, 5], [3, 4]]),
            IBE_K: g_d([1, 1, 1, 1, 1, 1])
        }
        virus_dic = {
            CON_K: g_d([-2, -2, 1, 1, 1, 4]),
            STA_K: g_d([F, H, H, H, H, H]),
            NC_K: 0
        }
        propagate_to_transportation(env_dic, virus_dic, 1, 0.1, 2)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], F)

    def test_propagate_to_transportation_isolated2(self):
        # i0 is isolated
        # Everyone stays safe
        env_dic = {
            IW_K: g_d([1, 1, 2, 2, 1, 0]),
            ITI_K: g_d([[0, 5], [4, 2], [1, 1], [2, 2], [0, 5], [3, 4]]),
            IBE_K: g_d([1, 1, 1, 1, 1, 1])
        }
        virus_dic = {
            CON_K: g_d([-2, -2, 1, 1, 1, 4]),
            STA_K: g_d([S, H, H, H, H, H]),
            NC_K: 0
        }
        propagate_to_transportation(env_dic, virus_dic, 1, 0.1, 2)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_transportation_remote_work2(self):
        # i0 is infected and contagious but he is working from hom (99% remote parameter)
        # Nobody is infected
        env_dic = {
            IW_K: g_d([1, 1, 2, 2, 1, 0]),
            ITI_K: g_d([[0, 5], [4, 2], [1, 1], [2, 2], [0, 5], [3, 4]]),
            IBE_K: g_d([1, 1, 1, 1, 1, 1])
        }
        virus_dic = {
            CON_K: g_d([-2, -2, 1, 1, 1, 4]),
            STA_K: g_d([F, H, H, H, H, H]),
            NC_K: 0
        }
        propagate_to_transportation(env_dic, virus_dic, 1, 0.99, 2)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_transportation_carefull_people2(self):
        # i0 is infected and contagious but he is very carefull
        # Nobody is infected
        env_dic = {
            IW_K: g_d([1, 1, 2, 2, 1, 0]),
            ITI_K: g_d([[0, 5], [4, 2], [1, 1], [2, 2], [0, 5], [3, 4]]),
            IBE_K: g_d([0.0001, 1, 1, 1, 1, 1])
        }
        virus_dic = {
            CON_K: g_d([-2, -2, 1, 1, 1, 4]),
            STA_K: g_d([F, H, H, H, H, H]),
            NC_K: 0
        }
        propagate_to_transportation(env_dic, virus_dic, 1, 0.98, 2)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], H)

    def test_propagate_to_transportation_dangerous_people2(self):
        # i0 is infected and contagious and has a very bad behavior
        # he infects i5
        env_dic = {
            IW_K: g_d([1, 1, 2, 2, 1, 0]),
            ITI_K: g_d([[0, 5], [4, 2], [1, 1], [2, 2], [0, 5], [3, 4]]),
            IBE_K: g_d([999, 1, 1, 1, 1, 1])
        }
        virus_dic = {
            CON_K: g_d([-2, -2, 1, 1, 1, 4]),
            STA_K: g_d([F, H, H, H, H, H]),
            NC_K: 0
        }
        propagate_to_transportation(env_dic, virus_dic, 0.001, 0.1, 2)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], F)

    def test_propagate_to_transportation_bad_behavior2(self):
        # i0 is infected and contagious and has a very bad behavior
        # he infects i5
        env_dic = {
            IW_K: g_d([1, 1, 2, 2, 1, 0]),
            ITI_K: g_d([[0, 5], [4, 2], [1, 1], [2, 2], [0, 5], [3, 4]]),
            IBE_K: g_d([999, 1, 1, 1, 1, 1])
        }
        virus_dic = {
            CON_K: g_d([-2, -2, 1, 1, 1, 4]),
            STA_K: g_d([F, H, H, H, H, H]),
            NC_K: 0
        }
        propagate_to_transportation(env_dic, virus_dic, 0.001, 0.1, 2)
        self.assertEqual(virus_dic[STA_K][4], H)
        self.assertEqual(virus_dic[STA_K][5], F)


if __name__ == '__main__':
    unittest.main()
