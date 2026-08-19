import unittest

from scenario.helper.ray import merge_run_stat, resolve_num_cpus
from scenario.helper.scenario import (
    CONFINED_PARAMS,
    NORMAL_LIFE_PARAMS,
    apply_unlock_progress,
    get_zero_run_stats,
    get_zero_stats,
    get_zero_stats_variant,
    is_weekend,
    measure_lockdown_strength,
    parse_bool,
    read_extra_params,
    soften_full_lockdown,
    soften_propagation_lockdown,
    tighten_full_lockdown,
    tighten_propagation_lockdown,
)
from simulator.constants.keys import (
    additional_scenario_params_key,
    house_infect_key,
    nday_key,
    nrun_key,
    nvariant_key,
    remote_work_key,
    store_infection_key,
    store_preference_key,
    transport_infection_key,
    work_infection_key,
)

LOCKDOWN_PARAMS = {
    house_infect_key: 0.25,
    transport_infection_key: 0.04,
    work_infection_key: 0.09,
    store_infection_key: 0.16,
    store_preference_key: 0.81,
    remote_work_key: 0.64,
}


class TestWeekend(unittest.TestCase):

    def test_is_weekend(self):
        # Day 0 is a Monday, so days 5 and 6 are the weekend.
        self.assertEqual([is_weekend(d) for d in range(7)],
                         [False, False, False, False, False, True, True])

    def test_is_weekend_repeats_every_week(self):
        for day in range(0, 200):
            self.assertEqual(is_weekend(day), is_weekend(day + 7))

    def test_two_weekend_days_per_week(self):
        self.assertEqual(sum(is_weekend(d) for d in range(70)), 20)


class TestLockdownMath(unittest.TestCase):

    def test_soften_propagation_raises_every_infection_probability(self):
        params = dict(LOCKDOWN_PARAMS)
        soften_propagation_lockdown(params)
        for key in (house_infect_key, transport_infection_key, work_infection_key, store_infection_key):
            self.assertGreater(params[key], LOCKDOWN_PARAMS[key], key)

    def test_tighten_propagation_lowers_every_infection_probability(self):
        params = dict(LOCKDOWN_PARAMS)
        tighten_propagation_lockdown(params)
        for key in (house_infect_key, transport_infection_key, work_infection_key, store_infection_key):
            self.assertLess(params[key], LOCKDOWN_PARAMS[key], key)

    def test_soften_then_tighten_returns_to_the_starting_point(self):
        params = dict(LOCKDOWN_PARAMS)
        soften_full_lockdown(params)
        tighten_full_lockdown(params)
        for key, value in LOCKDOWN_PARAMS.items():
            self.assertAlmostEqual(params[key], value, places=9, msg=key)

    def test_probabilities_stay_in_range_under_repeated_softening(self):
        params = dict(LOCKDOWN_PARAMS)
        for _ in range(20):
            soften_full_lockdown(params)
        self.assertTrue(all(0 <= v <= 1 for v in params.values()), params)

    def test_measure_lockdown_strength_decreases_when_lockdown_is_lifted(self):
        tight = dict(LOCKDOWN_PARAMS)
        loose = dict(LOCKDOWN_PARAMS)
        soften_full_lockdown(loose)
        self.assertGreater(measure_lockdown_strength(tight), measure_lockdown_strength(loose))

    def test_measure_lockdown_strength_is_positive(self):
        self.assertGreater(measure_lockdown_strength(dict(LOCKDOWN_PARAMS)), 0)


class TestApplyUnlockProgress(unittest.TestCase):

    def test_zero_progress_gives_the_confined_values(self):
        params = apply_unlock_progress({}, 0)
        self.assertEqual(params, CONFINED_PARAMS)

    def test_full_progress_gives_the_normal_life_values(self):
        params = apply_unlock_progress({}, 1)
        for key, value in NORMAL_LIFE_PARAMS.items():
            self.assertAlmostEqual(params[key], value, msg=key)

    def test_half_progress_is_halfway(self):
        params = apply_unlock_progress({}, 0.5)
        for key in CONFINED_PARAMS:
            expected = (CONFINED_PARAMS[key] + NORMAL_LIFE_PARAMS[key]) / 2
            self.assertAlmostEqual(params[key], expected, msg=key)

    def test_lockdown_never_zeroes_out_the_infection_probabilities(self):
        # The old formula collapsed to `normal * progress`, so a full lockdown
        # made every propagation probability 0 and no epidemic could start.
        params = apply_unlock_progress({}, 0)
        for key in (house_infect_key, transport_infection_key, work_infection_key, store_infection_key):
            self.assertGreater(params[key], 0, key)

    def test_progress_moves_monotonically_between_the_two_regimes(self):
        series = [apply_unlock_progress({}, p / 10)[work_infection_key] for p in range(11)]
        self.assertEqual(series, sorted(series))

    def test_it_updates_the_dict_in_place(self):
        params = {"unrelated": 1}
        returned = apply_unlock_progress(params, 0.3)
        self.assertIs(returned, params)
        self.assertEqual(params["unrelated"], 1)


class TestExtraParams(unittest.TestCase):

    def test_parse_bool_truthy_and_falsy_spellings(self):
        for value in ("True", "true", "1", "yes", "Y"):
            self.assertTrue(parse_bool(value), value)
        for value in ("False", "false", "0", "no", "N"):
            self.assertFalse(parse_bool(value), value)

    def test_parse_bool_rejects_nonsense(self):
        with self.assertRaises(ValueError):
            parse_bool("maybe")

    def test_parse_bool_passes_actual_booleans_through(self):
        self.assertTrue(parse_bool(True))
        self.assertFalse(parse_bool(False))

    def test_read_extra_params_converts_each_position(self):
        params = {additional_scenario_params_key: ["14", "2.5", "True"]}
        self.assertEqual(read_extra_params(params, int, float, parse_bool), (14, 2.5, True))

    def test_read_extra_params_ignores_the_extra_ones(self):
        params = {additional_scenario_params_key: ["1", "2", "3"]}
        self.assertEqual(read_extra_params(params, int), (1,))

    def test_read_extra_params_complains_when_there_are_too_few(self):
        with self.assertRaises(ValueError) as ctx:
            read_extra_params({additional_scenario_params_key: ["1"]}, int, int)
        self.assertIn("needs 2", str(ctx.exception))

    def test_read_extra_params_handles_a_missing_or_empty_list(self):
        with self.assertRaises(ValueError):
            read_extra_params({}, int)
        with self.assertRaises(ValueError):
            read_extra_params({additional_scenario_params_key: None}, int)


class TestZeroStats(unittest.TestCase):

    def test_zero_stats_variant_is_indexed_by_variant(self):
        stats = get_zero_stats_variant({nrun_key: 3, nvariant_key: 5})
        self.assertEqual(stats["dea"].shape, (3, 5))

    def test_merge_run_stat_writes_one_row(self):
        params = {nrun_key: 3, nday_key: 4}
        stats = get_zero_stats(params)
        run_stats = get_zero_run_stats(params)
        run_stats["dea"][:] = [1, 2, 3, 4]
        merge_run_stat(stats, run_stats, 2)
        self.assertEqual(list(stats["dea"][2]), [1, 2, 3, 4])
        self.assertEqual(list(stats["dea"][0]), [0, 0, 0, 0])


class TestResolveNumCpus(unittest.TestCase):

    def test_zero_means_one_core(self):
        self.assertEqual(resolve_num_cpus(0), 1)

    def test_a_positive_value_is_capped_by_the_machine(self):
        self.assertEqual(resolve_num_cpus(1), 1)
        self.assertLessEqual(resolve_num_cpus(1000), 1000)
        self.assertGreaterEqual(resolve_num_cpus(1000), 1)

    def test_a_negative_value_leaves_cores_free(self):
        # It used to *subtract* the negative number, asking for more cores than
        # the machine has instead of fewer.
        self.assertLessEqual(resolve_num_cpus(-1), resolve_num_cpus(1000))
        self.assertLessEqual(resolve_num_cpus(-4), resolve_num_cpus(-1))

    def test_it_never_returns_less_than_one(self):
        for ncpu in (-1000, -8, -1, 0, 1, 4):
            self.assertGreaterEqual(resolve_num_cpus(ncpu), 1, ncpu)


if __name__ == '__main__':
    unittest.main()
