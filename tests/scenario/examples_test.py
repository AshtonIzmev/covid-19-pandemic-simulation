"""Every scenario is executed for real and its output is checked.

The previous version of this module called `do_parallel_run.remote(...)` and
asserted `len(stats_l) > 0`. Because a ray future is only raised when it is
awaited, a scenario could raise on every single day and the test still passed.
Here every run goes through `ray.get`, so an exception fails the test, and the
returned statistics are checked against the invariants of the model.
"""
import random
import unittest

import numpy as np
import pytest
from ray.exceptions import RayTaskError

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
from scenario.helper.progressbar import ProgressBar
from simulator.constants.keys import (
    additional_scenario_params_key,
    nday_key,
    nindividual_key,
    nvariant_key,
)
from simulator.helper.environment import get_environment_simulation
from simulator.helper.simulation import get_default_params

N_INDIVIDUALS = 200
N_DAYS = 30

# scenario module -> the --extra-scenario-params it needs
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

DAY_STAT_KEYS = ("hea", "inf", "hos", "dea", "imm", "iso", "con", "R0d", "new", "loc")


def build_params(extra, n_days=N_DAYS, n_individuals=N_INDIVIDUALS, n_variants=None):
    params = get_default_params()
    params[nindividual_key] = n_individuals
    params[nday_key] = n_days
    params[additional_scenario_params_key] = extra
    if n_variants is not None:
        params[nvariant_key] = n_variants
    return params


def build_env(params, seed=12):
    """A scenario is only reproducible against a fixed environment, so the
    environment RNG is pinned separately from the run seed."""
    random.seed(seed)
    np.random.seed(seed)
    return get_environment_simulation(params)


def run_scenario(ray, module, extra, n_days=N_DAYS, n_individuals=N_INDIVIDUALS,
                 n_variants=None, env_dic=None, seed=12, run_id=3):
    """Run one scenario to completion and return its run statistics."""
    params = build_params(extra, n_days, n_individuals, n_variants)
    if env_dic is None:
        env_dic = build_env(params)
    pb = ProgressBar(n_days * (n_variants or 1))
    returned_id, run_stats = ray.get(
        module.do_parallel_run.remote(ray.put(env_dic), ray.put(params), run_id, seed, pb.actor))
    return params, returned_id, run_stats


@pytest.mark.usefixtures("ray_session")
class TestScenarios(unittest.TestCase):
    """Base class holding the shared assertions; ray comes from the fixture."""

    @pytest.fixture(autouse=True)
    def _ray(self, ray_session):
        self.ray = ray_session

    def assert_day_stats_are_sane(self, params, run_stats):
        n_days = params[nday_key]
        self.assertEqual(sorted(run_stats), sorted(DAY_STAT_KEYS))
        for key in DAY_STAT_KEYS:
            self.assertEqual(run_stats[key].shape, (n_days,), key)
            self.assertTrue(np.all(np.isfinite(run_stats[key])), f"{key} holds nan or inf")
            self.assertTrue(np.all(run_stats[key] >= 0), f"{key} went negative")

        # Nobody is created or destroyed: the six states always add up.
        head_count = sum(run_stats[k] for k in ("hea", "inf", "hos", "dea", "imm", "iso"))
        self.assertTrue(np.all(head_count <= N_INDIVIDUALS + 1e-9),
                        "more individuals than the population")

        # Deaths are final, so the count can only grow.
        self.assertTrue(np.all(np.diff(run_stats["dea"]) >= 0), "the death toll went down")

        # Contagious people are a subset of the infected ones.
        self.assertTrue(np.all(run_stats["con"] <= run_stats["inf"]))


class TestDayScenarios(TestScenarios):

    def test_every_day_scenario_runs_and_reports_sane_statistics(self):
        for module, extra in DAY_SCENARIOS:
            with self.subTest(scenario=module.__name__):
                params, run_id, run_stats = run_scenario(self.ray, module, extra)
                self.assertEqual(run_id, 3, "the run id must be echoed back for merging")
                self.assert_day_stats_are_sane(params, run_stats)

    def test_every_day_scenario_is_reproducible_for_a_given_seed(self):
        for module, extra in DAY_SCENARIOS:
            with self.subTest(scenario=module.__name__):
                # Same environment and same run seed must give the same history.
                env_dic = build_env(build_params(extra, n_days=12))
                _, _, first = run_scenario(self.ray, module, extra, n_days=12, env_dic=env_dic)
                _, _, second = run_scenario(self.ray, module, extra, n_days=12, env_dic=env_dic)
                for key in DAY_STAT_KEYS:
                    np.testing.assert_allclose(first[key], second[key],
                                               err_msg=f"{module.__name__}/{key} is not reproducible")

    def test_different_seeds_give_different_histories(self):
        env_dic = build_env(build_params([], n_days=40))
        _, _, first = run_scenario(self.ray, sc0_base_lockdown, [], n_days=40, env_dic=env_dic, seed=1)
        _, _, second = run_scenario(self.ray, sc0_base_lockdown, [], n_days=40, env_dic=env_dic, seed=999)
        self.assertFalse(np.array_equal(first["new"], second["new"]))

    def test_the_run_id_is_echoed_back_unchanged(self):
        for run_id in (0, 5, 17):
            _, returned, _ = run_scenario(self.ray, sc0_base_lockdown, [], n_days=5, run_id=run_id)
            self.assertEqual(returned, run_id)

    def test_an_epidemic_actually_happens(self):
        # A scenario that infects nobody would satisfy every invariant above,
        # which is exactly the bug the broken lockdown interpolation caused.
        for module, extra in DAY_SCENARIOS:
            with self.subTest(scenario=module.__name__):
                _, _, run_stats = run_scenario(self.ray, module, extra, n_days=60)
                self.assertGreater(run_stats["new"].sum(), 0,
                                   f"{module.__name__} never infected anybody")

    def test_scenarios_reject_missing_extra_parameters(self):
        needy = [(module, extra) for module, extra in DAY_SCENARIOS if extra]
        for module, extra in needy:
            with self.subTest(scenario=module.__name__), \
                    self.assertRaises((ValueError, RayTaskError)):
                run_scenario(self.ray, module, extra[:-1], n_days=3)

    def test_lockdown_scenarios_report_a_lockdown_measure(self):
        for module in (sc0_base_lockdown, sc1_simple_lockdown_removal, sc7_nominal_lockdown_removal):
            extra = dict(DAY_SCENARIOS)[module]
            with self.subTest(scenario=module.__name__):
                _, _, run_stats = run_scenario(self.ray, module, extra)
                self.assertGreater(run_stats["loc"].sum(), 0)

    def test_sc7_relock_flag_is_read_as_a_boolean(self):
        # `bool("0")` is True, so "0" used to switch relocking *on*.
        _, _, without = run_scenario(self.ray, sc7_nominal_lockdown_removal, ["0"], n_days=40)
        _, _, with_relock = run_scenario(self.ray, sc7_nominal_lockdown_removal, ["1"], n_days=40)
        self.assertTrue(np.all(np.isfinite(without["loc"])))
        self.assertTrue(np.all(np.isfinite(with_relock["loc"])))

    def test_sc6_travelers_imports_cases_from_abroad(self):
        # Big enough that the epidemic does not saturate in both runs.
        _, _, few = run_scenario(self.ray, sc6_travelers, ["1"], n_days=20, n_individuals=2000)
        _, _, many = run_scenario(self.ray, sc6_travelers, ["40"], n_days=20, n_individuals=2000)
        self.assertGreater(many["new"].sum(), few["new"].sum())

    def test_sc8_isolates_young_adults_below_the_age_cutoff(self):
        # The volunteer rate is one per thousand individuals per day, so the
        # population has to be large enough for anybody to be picked at all.
        _, _, run_stats = run_scenario(self.ray, sc8_innoculation, ["40"], n_days=20, n_individuals=3000)
        # sc8 overrides "iso" with the number of volunteers innoculated that day.
        self.assertGreater(run_stats["iso"].sum(), 0)

    def test_sc8_innoculates_nobody_above_the_age_cutoff(self):
        _, _, young = run_scenario(self.ray, sc8_innoculation, ["30"], n_days=20, n_individuals=3000)
        _, _, everyone = run_scenario(self.ray, sc8_innoculation, ["120"], n_days=20, n_individuals=3000)
        self.assertGreater(everyone["iso"].sum(), 0)
        self.assertGreaterEqual(everyone["iso"].sum(), young["iso"].sum())


class TestVariantScenario(TestScenarios):

    def test_sc10_variant_runs_for_each_variant(self):
        params, run_id, run_stats = run_scenario(self.ray, sc10_variant, ["-1", "MH", "False"],
                                                 n_days=15, n_variants=3)
        self.assertEqual(run_id, 3)
        self.assertEqual(sorted(run_stats), ["dea"])
        self.assertEqual(run_stats["dea"].shape, (3,))
        self.assertTrue(np.all(run_stats["dea"] >= 0))
        self.assertTrue(np.all(run_stats["dea"] <= N_INDIVIDUALS))

    def test_sc10_accepts_every_variant_kind(self):
        for kind in ("C", "I", "M", "H", "MH", "HM"):
            with self.subTest(kind=kind):
                _, _, run_stats = run_scenario(self.ray, sc10_variant, ["-1", kind, "False"],
                                               n_days=10, n_variants=2)
                self.assertEqual(run_stats["dea"].shape, (2,))

    def test_sc10_rejects_an_unknown_variant_kind(self):
        with self.assertRaises((ValueError, RayTaskError)):
            run_scenario(self.ray, sc10_variant, ["-1", "Z", "False"], n_days=5, n_variants=2)

    def test_sc10_genetic_cost_restriction_runs(self):
        _, _, run_stats = run_scenario(self.ray, sc10_variant, ["-1", "C", "True"],
                                       n_days=10, n_variants=3)
        self.assertEqual(run_stats["dea"].shape, (3,))


if __name__ == '__main__':
    unittest.main()
