import random
import unittest

import numpy as np

from simulator.constants.keys import (
    CON_INIT_K,
    CON_K,
    DEA_INIT_K,
    DEA_K,
    DEAD_V,
    HEALTHY_V,
    HOS_INIT_K,
    HOS_K,
    HOSPITALIZED_V,
    IMM_INIT_K,
    IMM_K,
    IMMUNE_V,
    INFECTED_V,
    ISOLATED_V,
    NC_K,
    STA_K,
    contagion_bounds_key,
    death_bounds_key,
    hospitalization_bounds_key,
    immunity_bounds_key,
    innoculation_number_key,
    nday_key,
    nindividual_key,
    variant_hospitalization_k,
    variant_mortality_k,
)
from simulator.helper.dynamic import update_infection_period
from simulator.helper.simulation import get_default_params, get_virus_simulation_t0
from tests.utils import make_virus_dic

BOUNDS_PARAMS = {
    nindividual_key: 200,
    innoculation_number_key: 20,
    contagion_bounds_key: (2, 7),
    hospitalization_bounds_key: (7, 21),
    death_bounds_key: (21, 39),
    immunity_bounds_key: (35, 65),
}


class TestVirusInitialisation(unittest.TestCase):

    def setUp(self):
        random.seed(12)
        np.random.seed(seed=12)

    def test_build_virus_dic_shape(self):
        result = get_virus_simulation_t0(BOUNDS_PARAMS)
        population = list(range(BOUNDS_PARAMS[nindividual_key]))
        for key in (CON_K, HOS_K, DEA_K, IMM_K, CON_INIT_K, HOS_INIT_K, DEA_INIT_K, IMM_INIT_K, STA_K):
            self.assertEqual(sorted(result[key]), population, f"{key} does not cover the population")
        self.assertEqual(result[NC_K], 0)

    def test_build_virus_dic_periods_respect_their_bounds(self):
        result = get_virus_simulation_t0(BOUNDS_PARAMS)
        for key, (low, high) in ((CON_K, (2, 7)), (HOS_K, (7, 21)), (DEA_K, (21, 39)), (IMM_K, (35, 65))):
            values = list(result[key].values())
            self.assertTrue(all(low <= v <= high for v in values), f"{key} out of bounds")
            self.assertTrue(all(isinstance(v, int) for v in values))

    def test_build_virus_dic_init_snapshots_are_independent_copies(self):
        # The live countdowns are decremented every day; the *_INIT_K ones are what
        # an individual is reset to when immunity wears off, and must not follow.
        result = get_virus_simulation_t0(BOUNDS_PARAMS)
        self.assertEqual(result[CON_K], result[CON_INIT_K])
        result[CON_K][0] -= 5
        self.assertNotEqual(result[CON_K][0], result[CON_INIT_K][0])

    def test_build_virus_dic_only_healthy_or_infected_at_day_zero(self):
        result = get_virus_simulation_t0(BOUNDS_PARAMS)
        self.assertEqual(set(result[STA_K].values()) - {HEALTHY_V, INFECTED_V}, set())

    def test_build_virus_dic_innoculates_about_the_requested_number(self):
        totals = []
        for seed in range(30):
            random.seed(seed)
            result = get_virus_simulation_t0(BOUNDS_PARAMS)
            totals.append(sum(1 for s in result[STA_K].values() if s == INFECTED_V))
        # 20 innoculations drawn out of 200 individuals: binomial around 20.
        self.assertLess(abs(np.mean(totals) - 20), 5)

    def test_build_virus_dic_without_innoculation(self):
        params = dict(BOUNDS_PARAMS, **{innoculation_number_key: 0})
        result = get_virus_simulation_t0(params)
        self.assertTrue(all(s == HEALTHY_V for s in result[STA_K].values()))

    def test_build_virus_dic_defaults_the_variant_factors_to_neutral(self):
        result = get_virus_simulation_t0(BOUNDS_PARAMS)
        self.assertEqual(result[variant_mortality_k], 1)
        self.assertEqual(result[variant_hospitalization_k], 1)

    def test_build_virus_dic_carries_the_variant_factors_over(self):
        params = dict(BOUNDS_PARAMS, **{variant_mortality_k: 1.4, variant_hospitalization_k: 0.7})
        result = get_virus_simulation_t0(params)
        self.assertEqual(result[variant_mortality_k], 1.4)
        self.assertEqual(result[variant_hospitalization_k], 0.7)

    def test_build_virus_dic_periods_are_drawn_independently(self):
        # Each individual draws its own four periods; they must not all be equal.
        result = get_virus_simulation_t0(dict(BOUNDS_PARAMS, **{nindividual_key: 500}))
        self.assertGreater(len(set(result[CON_K].values())), 1)
        self.assertGreater(len(set(result[DEA_K].values())), 1)
        # ... and the four series must not be copies of one another.
        self.assertNotEqual(list(result[CON_K].values()), list(result[HOS_K].values()))


class TestDefaultParams(unittest.TestCase):

    def test_default_params_are_self_consistent(self):
        params = get_default_params()
        self.assertGreater(params[nindividual_key], 0)
        self.assertGreater(params[nday_key], 0)
        self.assertLessEqual(params[innoculation_number_key], params[nindividual_key])
        for key in (contagion_bounds_key, hospitalization_bounds_key, death_bounds_key, immunity_bounds_key):
            low, high = params[key]
            self.assertLessEqual(low, high, f"{key} bounds are inverted")
            self.assertGreater(low, 0)

    def test_default_params_probabilities_are_in_range(self):
        params = get_default_params()
        for key in ("PROB_HOUSE_INFECTION", "PROB_WORK_INFECTION", "PROB_STORE_INFECTION",
                    "PROB_TRANSPORT_INFECTION", "REMOTE_WORK_PERCENT", "PROB_PREFERENCE_STORE"):
            self.assertTrue(0 <= params[key] <= 1, f"{key} is not a probability")

    def test_default_params_are_a_fresh_dict_each_time(self):
        first = get_default_params()
        first[nindividual_key] = 1
        self.assertNotEqual(get_default_params()[nindividual_key], 1)

    def test_default_params_build_a_usable_virus_dic(self):
        result = get_virus_simulation_t0(get_default_params())
        self.assertEqual(len(result[STA_K]), get_default_params()[nindividual_key])


class TestUpdateInfectionPeriod(unittest.TestCase):

    def test_update_infection_period(self):
        # 4 is already infected, 1 and 9 are about to be, 6 is immune.
        virus_dic = make_virus_dic([HEALTHY_V] * 4 + [INFECTED_V] + [HEALTHY_V] + [IMMUNE_V] + [HEALTHY_V] * 3)
        update_infection_period([1, 9, 6], virus_dic)
        self.assertEqual(virus_dic[STA_K][1], INFECTED_V)
        self.assertEqual(virus_dic[STA_K][2], HEALTHY_V)
        self.assertEqual(virus_dic[STA_K][4], INFECTED_V)
        self.assertEqual(virus_dic[STA_K][6], IMMUNE_V)
        self.assertEqual(virus_dic[STA_K][9], INFECTED_V)
        self.assertEqual(virus_dic[NC_K], 2)

    def test_update_infection_period_only_infects_the_healthy(self):
        virus_dic = make_virus_dic([HEALTHY_V, INFECTED_V, IMMUNE_V, DEAD_V, HOSPITALIZED_V, ISOLATED_V])
        update_infection_period([0, 1, 2, 3, 4, 5], virus_dic)
        self.assertEqual(list(virus_dic[STA_K].values()),
                         [INFECTED_V, INFECTED_V, IMMUNE_V, DEAD_V, HOSPITALIZED_V, ISOLATED_V])
        self.assertEqual(virus_dic[NC_K], 1)

    def test_update_infection_period_counts_a_duplicate_once(self):
        virus_dic = make_virus_dic([HEALTHY_V, HEALTHY_V])
        update_infection_period([0, 0, 0, 1], virus_dic)
        self.assertEqual(virus_dic[NC_K], 2)

    def test_update_infection_period_with_nobody_to_infect(self):
        virus_dic = make_virus_dic([HEALTHY_V, HEALTHY_V])
        update_infection_period([], virus_dic)
        self.assertEqual(virus_dic[NC_K], 0)
        self.assertTrue(all(s == HEALTHY_V for s in virus_dic[STA_K].values()))


if __name__ == '__main__':
    unittest.main()
