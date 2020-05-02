import random
import unittest

from simulator.helper.dynamic import propagate_to_houses
from tests.constant import *


class TestSimulation(unittest.TestCase):

    @classmethod
    def setUp(cls):
        random.seed(12)

    def test_propagate_to_houses_contagious_people(self):
        # i0 is infected and lives in h0. He infects i1, i2 and i3
        # i4 is dead and does not infect anyone (i5, i6 and i7)
        # i8 is immune and does not infect i9
        env_dic = {
            HI_K: {0: [0, 1, 2, 3], 1: [4, 5, 6, 7], 2: [8, 9]},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
            IBE_K: {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}
        }
        virus_dic = {
            CON_K: {0: -9, 1: 3, 2: 2, 3: 2, 4: -9, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
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
        # i0 is infected and lives with i1, i2 and i3
        # But i0 is very carefull with very good behabior (0.01)
        # He does not infect i1, i2 nor i3
        env_dic = {
            HI_K: {0: [0, 1, 2, 3], 1: [4, 5, 6, 7], 2: [8, 9]},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
            IBE_K: {0: 0.01, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}
        }
        virus_dic = {
            CON_K: {0: -9, 1: 3, 2: 2, 3: 2, 4: -9, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
            STA_K: {0: F, 1: H, 2: H, 3: H, 4: D, 5: H, 6: H, 7: H, 8: M, 9: H},
            NC_K: 0
        }
        propagate_to_houses(env_dic, virus_dic, 0.99)

        self.assertEqual(virus_dic[STA_K][0], F)
        # careful people do not contaminate
        self.assertEqual(virus_dic[STA_K][1], H)
        self.assertEqual(virus_dic[STA_K][2], H)
        self.assertEqual(virus_dic[STA_K][3], H)

    def test_propagate_to_houses_dangerous_daddy_people(self):
        # i0 is infected and lives with i1 to i9
        # But i0 is not really a carefull daddy (0.9 behavior)
        # He does infect half his (big) family
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
        # i0 is infected and lives with i1 to i9
        # But i0 is a very very very carefull daddy (0.00000001)
        # He does not infect anyone in his family
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
        # i0 is infected and lives with i1 to i9
        # But i0 is a very bad daddy (0.99 behavior)
        # He does infect all his (big) family
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
        # i0 is infected and lives with i1, i2 and i3
        # But i0 is not contagious yet
        # He does not infect anyone.
        env_dic = {
            HI_K: {0: [0, 1, 2, 3], 1: [4, 5, 6, 7], 2: [8, 9]},
            IH_K: {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2},
            IBE_K: {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}
        }
        virus_dic = {
            CON_K: {0: 4, 1: 3, 2: 2, 3: 2, 4: 6, 5: 4, 6: 4, 7: 2, 8: 6, 9: 5},
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


if __name__ == '__main__':
    unittest.main()
