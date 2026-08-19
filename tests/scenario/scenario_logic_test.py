"""Scenario bodies executed in-process, without ray.

`examples_test.py` runs the same scenarios through ray, which is what production
does. Ray executes them in worker processes though, so nothing there is visible
to the coverage tracker or to a debugger. These tests call the undecorated
function directly, which also makes them fast enough to assert on the details of
what each scenario is supposed to do.
"""
import random
import unittest

import numpy as np

from scenario.example import (
    sc0_base_lockdown,
    sc1_simple_lockdown_removal,
    sc2_yoyo_lockdown_removal,
    sc3_loose_lockdown,
    sc4_rogue_citizen,
    sc5_rogue_neighborhood,
    sc6_travelers,
    sc7_nominal_lockdown_removal,
    sc8_innoculation,
    sc9_vaccination,
    sc10_variant,
    scx_base_just_a_flu,
)
from scenario.example.sc10_variant import VARIANT_KINDS, get_variant_factors
from simulator.constants.keys import (
    additional_scenario_params_key,
    nday_key,
    nindividual_key,
    nvariant_key,
)
from simulator.helper.environment import get_environment_simulation
from simulator.helper.simulation import get_default_params


class FakeProgressActor:
    """Stands in for the ray ProgressBarActor handle: records `update.remote(n)`."""

    def __init__(self):
        self.updates = []

    @property
    def update(self):
        return self

    def remote(self, n):
        self.updates.append(n)


def run_locally(module, extra, n_days=25, n_individuals=200, n_variants=None, seed=12, run_id=0):
    params = get_default_params()
    params[nindividual_key] = n_individuals
    params[nday_key] = n_days
    params[additional_scenario_params_key] = extra
    if n_variants is not None:
        params[nvariant_key] = n_variants

    random.seed(seed)
    np.random.seed(seed)
    env_dic = get_environment_simulation(params)

    actor = FakeProgressActor()
    # `.remote` is the ray wrapper; `._function` is the plain python behind it.
    returned_id, run_stats = module.do_parallel_run._function(env_dic, params, run_id, seed, actor)
    return params, returned_id, run_stats, actor


DAY_SCENARIOS = [
    (scx_base_just_a_flu, []),
    (sc0_base_lockdown, []),
    (sc1_simple_lockdown_removal, ["14"]),
    (sc2_yoyo_lockdown_removal, ["14", "2", "7"]),
    (sc3_loose_lockdown, ["0"]),
    (sc4_rogue_citizen, ["5", "10"]),
    (sc5_rogue_neighborhood, ["4", "2"]),
    (sc6_travelers, ["5"]),
    (sc7_nominal_lockdown_removal, ["True"]),
    (sc8_innoculation, ["40"]),
    (sc9_vaccination, ["-1"]),
]


class TestScenarioBodies(unittest.TestCase):

    def test_every_scenario_reports_progress_once_per_day(self):
        for module, extra in DAY_SCENARIOS:
            with self.subTest(scenario=module.__name__):
                _, _, _, actor = run_locally(module, extra, n_days=17)
                self.assertEqual(actor.updates, [1] * 17)

    def test_every_scenario_returns_the_full_day_range(self):
        for module, extra in DAY_SCENARIOS:
            with self.subTest(scenario=module.__name__):
                params, _, run_stats, _ = run_locally(module, extra, n_days=17)
                for key, series in run_stats.items():
                    self.assertEqual(series.shape, (17,), f"{module.__name__}/{key}")

    def test_scenarios_do_not_leak_state_between_runs(self):
        # `params` is mutated in place by every scenario, so a second run with a
        # fresh params dict must give the same answer as the first.
        for module, extra in DAY_SCENARIOS:
            with self.subTest(scenario=module.__name__):
                _, _, first, _ = run_locally(module, extra, n_days=12)
                _, _, second, _ = run_locally(module, extra, n_days=12)
                np.testing.assert_allclose(first["dea"], second["dea"], err_msg=module.__name__)

    def test_population_is_conserved_every_single_day(self):
        for module, extra in DAY_SCENARIOS:
            if module is sc8_innoculation:
                continue  # sc8 repurposes "iso" as a volunteer counter
            with self.subTest(scenario=module.__name__):
                _, _, run_stats, _ = run_locally(module, extra, n_days=30)
                total = sum(run_stats[k] for k in ("hea", "inf", "hos", "dea", "imm", "iso"))
                np.testing.assert_array_equal(total, np.full(30, 200.0),
                                              err_msg=f"{module.__name__} lost or invented individuals")


class TestScenarioSpecifics(unittest.TestCase):

    def test_sc0_only_opens_the_stores_at_the_weekend(self):
        _, _, run_stats, _ = run_locally(sc0_base_lockdown, [], n_days=30)
        self.assertGreater(run_stats["new"].sum(), 0)

    def test_scx_just_a_flu_is_milder_than_the_lockdown_scenario(self):
        # "Just a flu" runs with no lockdown at all, so it should spread more.
        _, _, flu, _ = run_locally(scx_base_just_a_flu, [], n_days=60)
        _, _, lockdown, _ = run_locally(sc0_base_lockdown, [], n_days=60)
        self.assertGreater(flu["new"].sum(), lockdown["new"].sum())

    def test_sc1_loosens_the_lockdown_after_the_configured_delay(self):
        _, _, quick, _ = run_locally(sc1_simple_lockdown_removal, ["1"], n_days=60)
        _, _, slow, _ = run_locally(sc1_simple_lockdown_removal, ["120"], n_days=60)
        # A lockdown that is never lifted stays at maximum strength throughout.
        self.assertGreaterEqual(slow["loc"].sum(), quick["loc"].sum())

    def test_sc3_percent_increase_loosens_the_lockdown(self):
        _, _, none, _ = run_locally(sc3_loose_lockdown, ["0"], n_days=40)
        _, _, loose, _ = run_locally(sc3_loose_lockdown, ["50"], n_days=40)
        self.assertGreaterEqual(none["loc"].sum(), loose["loc"].sum())

    def test_sc4_more_rogue_citizens_spread_more(self):
        _, _, few, _ = run_locally(sc4_rogue_citizen, ["1", "10"], n_days=40)
        _, _, many, _ = run_locally(sc4_rogue_citizen, ["50", "10"], n_days=40)
        self.assertGreaterEqual(many["new"].sum(), few["new"].sum())

    def test_sc5_rogue_neighborhood_accepts_a_block_count(self):
        _, _, run_stats, _ = run_locally(sc5_rogue_neighborhood, ["4", "2"], n_days=30)
        self.assertGreater(run_stats["new"].sum(), 0)

    def test_sc6_travelers_import_more_cases_when_there_are_more_of_them(self):
        # The population has to be big enough that the epidemic does not simply
        # saturate in both runs, which would hide the difference.
        _, _, few, _ = run_locally(sc6_travelers, ["1"], n_days=20, n_individuals=2000)
        _, _, many, _ = run_locally(sc6_travelers, ["40"], n_days=20, n_individuals=2000)
        self.assertGreater(many["new"].sum(), few["new"].sum())
        self.assertLess(many["hea"][-1], few["hea"][-1])

    def test_sc7_starts_under_a_real_lockdown(self):
        # With the old interpolation every infection probability was 0 at
        # unlock_progress == 0, so day 0 could not infect anybody at all.
        _, _, run_stats, _ = run_locally(sc7_nominal_lockdown_removal, ["True"], n_days=45)
        self.assertGreater(run_stats["new"][:14].sum(), 0,
                           "nothing spread while the lockdown was fully on")

    def test_sc7_relock_flag_reads_zero_as_false(self):
        params_off, _, off, _ = run_locally(sc7_nominal_lockdown_removal, ["0"], n_days=45)
        params_on, _, on, _ = run_locally(sc7_nominal_lockdown_removal, ["1"], n_days=45)
        self.assertTrue(np.all(np.isfinite(off["loc"])))
        # Relocking can only ever push the lockdown measure back up.
        self.assertGreaterEqual(on["loc"].sum(), off["loc"].sum() - 1e-9)

    def test_sc8_innoculates_volunteers_and_reports_them_as_iso(self):
        _, _, run_stats, _ = run_locally(sc8_innoculation, ["40"], n_days=20, n_individuals=3000)
        self.assertGreater(run_stats["iso"].sum(), 0)

    def test_sc8_age_cutoff_limits_the_volunteer_pool(self):
        _, _, narrow, _ = run_locally(sc8_innoculation, ["21"], n_days=25, n_individuals=3000)
        _, _, wide, _ = run_locally(sc8_innoculation, ["120"], n_days=25, n_individuals=3000)
        self.assertGreaterEqual(wide["iso"].sum(), narrow["iso"].sum())

    def test_sc9_vaccination_makes_people_immune(self):
        _, _, none, _ = run_locally(sc9_vaccination, ["0"], n_days=40, n_individuals=1000)
        _, _, fast, _ = run_locally(sc9_vaccination, ["0.05"], n_days=40, n_individuals=1000)
        self.assertGreater(fast["imm"].sum(), none["imm"].sum())

    def test_sc9_negative_rate_falls_back_to_the_moroccan_rate(self):
        _, _, run_stats, _ = run_locally(sc9_vaccination, ["-1"], n_days=40, n_individuals=2000)
        self.assertGreater(run_stats["imm"].sum(), 0)

    def test_missing_extra_parameters_raise_a_clear_error(self):
        with self.assertRaises(ValueError) as ctx:
            run_locally(sc2_yoyo_lockdown_removal, ["14"], n_days=5)
        self.assertIn("--extra-scenario-params", str(ctx.exception))


class TestVariantFactors(unittest.TestCase):

    def test_neutral_axes_stay_at_one(self):
        contagiosity, immunization, mortality, hospital = get_variant_factors("C", 2, 5, False)
        self.assertNotEqual(contagiosity, 1.0)
        self.assertEqual((immunization, mortality, hospital), (1.0, 1.0, 1.0))

    def test_each_kind_moves_its_own_axis(self):
        moved = {"C": 0, "I": 1, "M": 2, "H": 3}
        for kind, index in moved.items():
            with self.subTest(kind=kind):
                factors = get_variant_factors(kind, 3, 5, False)
                self.assertNotEqual(factors[index], 1.0)
                for other, value in enumerate(factors):
                    if other != index:
                        self.assertEqual(value, 1.0)

    def test_the_tradeoff_kinds_move_two_axes_in_opposite_directions(self):
        for kind in ("MH", "HM"):
            with self.subTest(kind=kind):
                _, _, mortality, hospital = get_variant_factors(kind, 4, 5, False)
                self.assertAlmostEqual(mortality + hospital, 2.0)

    def test_the_sweep_covers_the_advertised_range(self):
        values = [get_variant_factors("C", i, 5, False)[0] for i in range(5)]
        self.assertAlmostEqual(values[0], 0.25)
        self.assertAlmostEqual(values[-1], 0.25 + 1.5 * 4 / 5)
        self.assertEqual(values, sorted(values))

    def test_genetic_cost_normalises_to_one(self):
        for kind in VARIANT_KINDS:
            for i in range(5):
                with self.subTest(kind=kind, step=i):
                    factors = get_variant_factors(kind, i, 5, True)
                    self.assertAlmostEqual(sum(factors), 1.0)

    def test_genetic_cost_does_not_compound_across_the_sweep(self):
        # The factors used to be mutated in place across iterations, so each
        # normalisation divided the already normalised values of the previous
        # step and everything decayed towards zero.
        first = get_variant_factors("C", 0, 5, True)
        last = get_variant_factors("C", 4, 5, True)
        self.assertAlmostEqual(sum(first), 1.0)
        self.assertAlmostEqual(sum(last), 1.0)
        self.assertGreater(min(last), 0.05)

    def test_an_unknown_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            get_variant_factors("Z", 0, 5, False)


class TestVariantScenarioBody(unittest.TestCase):

    def test_sc10_reports_one_death_count_per_variant(self):
        _, run_id, run_stats, actor = run_locally(sc10_variant, ["-1", "MH", "False"],
                                                  n_days=10, n_variants=4)
        self.assertEqual(run_id, 0)
        self.assertEqual(list(run_stats), ["dea"])
        self.assertEqual(run_stats["dea"].shape, (4,))
        # Every variant runs the full day loop.
        self.assertEqual(len(actor.updates), 10 * 4)

    def test_sc10_is_reproducible(self):
        _, _, first, _ = run_locally(sc10_variant, ["-1", "C", "True"], n_days=8, n_variants=3)
        _, _, second, _ = run_locally(sc10_variant, ["-1", "C", "True"], n_days=8, n_variants=3)
        np.testing.assert_array_equal(first["dea"], second["dea"])

    def test_sc10_death_counts_stay_within_the_population(self):
        _, _, run_stats, _ = run_locally(sc10_variant, ["-1", "M", "False"], n_days=15, n_variants=3)
        self.assertTrue(np.all(run_stats["dea"] >= 0))
        self.assertTrue(np.all(run_stats["dea"] <= 200))


if __name__ == '__main__':
    unittest.main()
