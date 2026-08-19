import unittest

import numpy as np

from scenario.helper.scenario import get_zero_run_stats, get_zero_stats
from simulator.constants.keys import (
    DEAD_V,
    HEALTHY_V,
    HOSPITALIZED_V,
    IMMUNE_V,
    INFECTED_V,
    ISOLATED_V,
    NC_K,
    STA_K,
    nday_key,
    nrun_key,
)
from simulator.helper.dynamic import (
    get_contagious_people,
    get_deadpeople,
    get_healthy_people,
    get_hospitalized_people,
    get_immune_people,
    get_infected_people,
    get_isolated_people,
    get_pandemic_statistics,
    get_r0_daily,
    get_virus_carrier_people,
    is_contagious,
    is_eligible_tostore,
    update_run_stat,
    update_stats,
)
from tests.utils import make_virus_dic

# One individual in each of the six states, plus a second infected one.
MIXED_STATES = [HEALTHY_V, INFECTED_V, IMMUNE_V, DEAD_V, HOSPITALIZED_V, ISOLATED_V, INFECTED_V]
# 1 is past its contagion countdown, 6 is not yet contagious.
MIXED_CONTAGION = [3, -2, 3, 3, -1, -4, 5]


def mixed_virus_dic(new_cases=0):
    return make_virus_dic(MIXED_STATES, contagion=MIXED_CONTAGION, new_cases=new_cases)


class TestPopulationSelectors(unittest.TestCase):

    def setUp(self):
        self.virus_dic = mixed_virus_dic()

    def test_selectors_partition_the_population(self):
        groups = [get_healthy_people(self.virus_dic), get_infected_people(self.virus_dic),
                  get_immune_people(self.virus_dic), get_deadpeople(self.virus_dic),
                  get_hospitalized_people(self.virus_dic), get_isolated_people(self.virus_dic)]
        flat = [i for group in groups for i in group]
        self.assertEqual(sorted(flat), sorted(self.virus_dic[STA_K]))
        self.assertEqual(len(flat), len(set(flat)), "an individual is counted in two states")

    def test_each_selector_picks_its_own_state(self):
        self.assertEqual(get_healthy_people(self.virus_dic), [0])
        self.assertEqual(get_infected_people(self.virus_dic), [1, 6])
        self.assertEqual(get_immune_people(self.virus_dic), [2])
        self.assertEqual(get_deadpeople(self.virus_dic), [3])
        self.assertEqual(get_hospitalized_people(self.virus_dic), [4])
        self.assertEqual(get_isolated_people(self.virus_dic), [5])

    def test_virus_carriers_are_the_infected_isolated_and_hospitalized(self):
        self.assertEqual(sorted(get_virus_carrier_people(self.virus_dic)), [1, 4, 5, 6])

    def test_contagious_needs_infected_and_an_elapsed_countdown(self):
        # 4 and 5 also have a negative countdown but are no longer INFECTED.
        self.assertEqual(get_contagious_people(self.virus_dic), [1])
        self.assertTrue(is_contagious(1, self.virus_dic))
        self.assertFalse(is_contagious(6, self.virus_dic))
        self.assertFalse(is_contagious(4, self.virus_dic))

    def test_contagion_countdown_boundary_is_strict(self):
        virus_dic = make_virus_dic([INFECTED_V, INFECTED_V, INFECTED_V], contagion=[1, 0, -1])
        self.assertEqual(get_contagious_people(virus_dic), [2])

    def test_is_eligible_tostore(self):
        # The isolated stay home and the dead do not shop.
        eligible = [i for i in self.virus_dic[STA_K] if is_eligible_tostore(self.virus_dic, i)]
        self.assertEqual(eligible, [0, 1, 2, 4, 6])

    def test_selectors_on_an_empty_population(self):
        empty = make_virus_dic([])
        for selector in (get_healthy_people, get_infected_people, get_immune_people, get_deadpeople,
                         get_hospitalized_people, get_isolated_people, get_contagious_people,
                         get_virus_carrier_people):
            self.assertEqual(selector(empty), [])


class TestR0(unittest.TestCase):

    def test_r0_daily_is_new_cases_over_contagious_people(self):
        virus_dic = mixed_virus_dic(new_cases=4)
        # 1 contagious individual, the +1 keeps it defined when there are none.
        self.assertAlmostEqual(get_r0_daily(virus_dic), 4 / 2)

    def test_r0_daily_is_zero_without_new_cases(self):
        self.assertEqual(get_r0_daily(mixed_virus_dic(new_cases=0)), 0)

    def test_r0_daily_never_divides_by_zero(self):
        virus_dic = make_virus_dic([HEALTHY_V, HEALTHY_V], new_cases=7)
        self.assertEqual(get_r0_daily(virus_dic), 7)


class TestPandemicStatistics(unittest.TestCase):

    def test_statistics_count_every_state(self):
        result = get_pandemic_statistics(mixed_virus_dic(new_cases=3))
        self.assertEqual(result["hea"], 1)
        self.assertEqual(result["inf"], 2)
        self.assertEqual(result["imm"], 1)
        self.assertEqual(result["dea"], 1)
        self.assertEqual(result["hos"], 1)
        self.assertEqual(result["iso"], 1)
        self.assertEqual(result["con"], 1)
        self.assertEqual(result["new"], 3)

    def test_statistics_reset_the_new_case_counter(self):
        virus_dic = mixed_virus_dic(new_cases=3)
        get_pandemic_statistics(virus_dic)
        self.assertEqual(virus_dic[NC_K], 0)
        self.assertEqual(get_pandemic_statistics(virus_dic)["new"], 0)

    def test_statistics_state_counts_sum_to_the_population(self):
        result = get_pandemic_statistics(mixed_virus_dic())
        total = sum(result[k] for k in ("hea", "inf", "imm", "dea", "hos", "iso"))
        self.assertEqual(total, len(MIXED_STATES))

    def test_update_run_stat_fills_one_day(self):
        params = {nrun_key: 2, nday_key: 5}
        run_stats = get_zero_run_stats(params)
        update_run_stat(mixed_virus_dic(new_cases=3), run_stats, 2)
        self.assertEqual(run_stats["hea"][2], 1)
        self.assertEqual(run_stats["new"][2], 3)
        # The other days are untouched.
        self.assertEqual(list(run_stats["hea"]), [0, 0, 1, 0, 0])

    def test_update_stats_fills_one_run_and_day(self):
        params = {nrun_key: 2, nday_key: 5}
        stats = get_zero_stats(params)
        update_stats(mixed_virus_dic(new_cases=3), stats, 1, 4)
        self.assertEqual(stats["hea"][1][4], 1)
        self.assertEqual(stats["dea"][1][4], 1)
        self.assertTrue(np.all(stats["hea"][0] == 0))

    def test_zero_stats_shapes(self):
        params = {nrun_key: 3, nday_key: 7}
        stats = get_zero_stats(params)
        run_stats = get_zero_run_stats(params)
        self.assertEqual(sorted(stats), sorted(run_stats))
        for key in stats:
            self.assertEqual(stats[key].shape, (3, 7))
            self.assertEqual(run_stats[key].shape, (7,))


if __name__ == '__main__':
    unittest.main()
