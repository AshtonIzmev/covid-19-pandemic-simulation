"""End to end tests of the three command line entry points.

These drive `main(argv)` exactly the way `python -m simulator.run ...` does, so
a broken argument name, a missing output directory or an unwired scenario id is
caught here rather than the first time somebody runs the project.
"""
import os
import unittest
from unittest import mock

import numpy as np
import pytest

import scenario.run
import simulator.run
import simulator.run_benchmark
from scenario.example import animate_base_lockdown, benchmark_base_lockdown
from simulator.constants.keys import STA_K, nday_key, nindividual_key
from simulator.helper.environment import get_environment_simulation
from simulator.helper.simulation import get_default_params

SMALL = ["--nind", "150", "--nday", "12"]
DAY_STAT_KEYS = ("hea", "inf", "hos", "dea", "imm", "iso", "con", "R0d", "new", "loc")


@pytest.fixture(autouse=True)
def _isolated_dirs(tmp_path, monkeypatch):
    """Keep generated pngs and cached environments out of the working tree."""
    monkeypatch.setattr("simulator.helper.plot.OUTPUT_DIR", str(tmp_path / "images"))
    monkeypatch.setattr("scenario.run.ENV_MODEL_DIR", str(tmp_path / "env_models"))


class TestSimulatorRun(unittest.TestCase):

    def test_run_returns_statistics_for_the_requested_horizon(self):
        stats = simulator.run.main(SMALL)
        self.assertEqual(sorted(stats), sorted(DAY_STAT_KEYS))
        for key in DAY_STAT_KEYS:
            self.assertEqual(stats[key].shape, (1, 12), key)

    def test_run_honours_nrun(self):
        stats = simulator.run.main([*SMALL, "--nrun", "3"])
        self.assertEqual(stats["hea"].shape, (3, 12))

    def test_run_draws_and_saves_the_requested_graphs(self):
        from simulator.helper import plot
        simulator.run.main([*SMALL, "--nrun", "2", "--draw", "pop", "new"])
        produced = sorted(os.listdir(plot.OUTPUT_DIR))
        self.assertEqual(len(produced), 2, produced)
        self.assertTrue(any("-pop-" in name for name in produced))
        self.assertTrue(any("-new-" in name for name in produced))

    def test_run_writes_nothing_when_no_graph_is_requested(self):
        from simulator.helper import plot
        simulator.run.main(SMALL)
        self.assertFalse(os.path.isdir(plot.OUTPUT_DIR))

    def test_run_is_reproducible_for_a_given_seed(self):
        first = simulator.run.main([*SMALL, "--random-seed", "7"])
        second = simulator.run.main([*SMALL, "--random-seed", "7"])
        np.testing.assert_array_equal(first["dea"], second["dea"])

    def test_run_benchmark_reports_its_timings(self):
        stats = simulator.run_benchmark.main(SMALL)
        self.assertEqual(stats["hea"].shape, (1, 12))


class TestBenchmarkScenario(unittest.TestCase):

    def test_profiling_is_off_by_default(self):
        params = get_default_params()
        params[nindividual_key], params[nday_key] = 100, 8
        env_dic = get_environment_simulation(params)
        with mock.patch("builtins.print") as mock_print:
            benchmark_base_lockdown.launch_run(params, env_dic)
        self.assertFalse(mock_print.called)

    def test_profiling_prints_one_line_per_step(self):
        params = get_default_params()
        params[nindividual_key], params[nday_key] = 100, 8
        env_dic = get_environment_simulation(params)
        with mock.patch("builtins.print") as mock_print:
            benchmark_base_lockdown.launch_run(params, env_dic, profile=True)
        self.assertEqual(mock_print.call_count, len(benchmark_base_lockdown.STEP_NAMES))


class TestAnimateScenario(unittest.TestCase):

    def test_it_records_one_snapshot_per_day(self):
        params = get_default_params()
        params[nindividual_key], params[nday_key] = 100, 9
        env_dic = get_environment_simulation(params)
        ind_works, ind_stos, stas = animate_base_lockdown.launch_run(params, env_dic)
        self.assertEqual(len(ind_works), 9)
        self.assertEqual(len(ind_stos), 9)
        self.assertEqual(len(stas), 9)

    def test_snapshots_are_copies_not_aliases_of_the_live_state(self):
        # They used to be appended by reference, so the whole history read back
        # as nine copies of the final day.
        params = get_default_params()
        params[nindividual_key], params[nday_key] = 200, 25
        env_dic = get_environment_simulation(params)
        _, _, stas = animate_base_lockdown.launch_run(params, env_dic)
        self.assertNotEqual(stas[0], stas[-1], "every snapshot is the same object")

    def test_it_does_not_accumulate_across_calls(self):
        # The three lists used to be module level globals.
        params = get_default_params()
        params[nindividual_key], params[nday_key] = 100, 6
        env_dic = get_environment_simulation(params)
        animate_base_lockdown.launch_run(params, env_dic)
        _, _, stas = animate_base_lockdown.launch_run(params, env_dic)
        self.assertEqual(len(stas), 6)


@pytest.mark.usefixtures("ray_session")
class TestScenarioRun(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def _ray(self, ray_session):
        self.ray = ray_session

    def test_every_scenario_id_is_reachable_from_the_command_line(self):
        for scenario_id, extra in ((-1, []), (0, []), (1, ["14"]), (2, ["14", "2", "7"]),
                                   (3, ["0"]), (4, ["5", "10"]), (5, ["4", "2"]), (6, ["5"]),
                                   (7, ["1"]), (8, ["40"]), (9, ["-1"])):
            with self.subTest(scenario_id=scenario_id):
                argv = ["--nind", "150", "--nday", "8", "--nrun", "2",
                        "--ncpu", "1", "--sce", str(scenario_id)]
                if extra:
                    argv += ["--extra-scenario-params", *extra]
                stats = scenario.run.main(argv)
                self.assertEqual(stats["hea"].shape, (2, 8))

    def test_the_variant_scenario_returns_one_death_count_per_variant(self):
        stats = scenario.run.main(["--nind", "150", "--nday", "6", "--nrun", "2", "--ncpu", "1",
                                   "--nvariant", "3", "--sce", "10",
                                   "--extra-scenario-params", "-1", "MH", "False"])
        self.assertEqual(sorted(stats), ["dea"])
        self.assertEqual(stats["dea"].shape, (2, 3))

    def test_an_unknown_scenario_id_is_reported(self):
        with self.assertRaises(KeyError):
            scenario.run.main(["--nind", "150", "--nday", "4", "--sce", "99"])

    def test_the_environment_model_is_cached_and_reused(self):
        argv = ["--nind", "150", "--nday", "5", "--nrun", "1", "--ncpu", "1", "--sce", "0"]
        scenario.run.main(argv)
        cached = os.listdir(scenario.run.ENV_MODEL_DIR)
        self.assertEqual(cached, ["env_150-20-20-3-10.joblib"])

        # A second run must reuse the file rather than rebuild the environment.
        with mock.patch("scenario.run.get_environment_simulation_p") as mock_build:
            scenario.run.main(argv)
        self.assertFalse(mock_build.called)

    def test_a_different_population_gets_its_own_cache_entry(self):
        base = ["--nday", "5", "--nrun", "1", "--ncpu", "1", "--sce", "0"]
        scenario.run.main([*base, "--nind", "150"])
        scenario.run.main([*base, "--nind", "180"])
        self.assertEqual(sorted(os.listdir(scenario.run.ENV_MODEL_DIR)),
                         ["env_150-20-20-3-10.joblib", "env_180-20-20-3-10.joblib"])

    def test_a_scenario_run_can_draw_its_graphs(self):
        from simulator.helper import plot
        scenario.run.main(["--nind", "150", "--nday", "8", "--nrun", "2", "--ncpu", "1",
                           "--sce", "0", "--draw", "summ", "lock"])
        produced = sorted(os.listdir(plot.OUTPUT_DIR))
        self.assertEqual(len(produced), 2, produced)


class TestSanityOfTheWholePipeline(unittest.TestCase):

    def test_a_full_run_keeps_the_population_constant(self):
        stats = simulator.run.main(["--nind", "300", "--nday", "40", "--nrun", "2"])
        total = sum(stats[k] for k in ("hea", "inf", "hos", "dea", "imm", "iso"))
        np.testing.assert_array_equal(total, np.full((2, 40), 300.0))

    def test_a_full_run_produces_a_real_epidemic(self):
        stats = simulator.run.main(["--nind", "500", "--nday", "60", "--nrun", "1"])
        self.assertGreater(stats["new"].sum(), 0)
        self.assertLess(stats["hea"][0][-1], stats["hea"][0][0])

    def test_the_virus_state_covers_the_whole_population(self):
        params = get_default_params()
        params[nindividual_key], params[nday_key] = 120, 5
        env_dic = get_environment_simulation(params)
        _, _, stas = animate_base_lockdown.launch_run(params, env_dic)
        self.assertEqual(sorted(stas[-1]), list(range(120)))
        self.assertEqual(sorted(env_dic[STA_K] if STA_K in env_dic else stas[-1]), list(range(120)))


if __name__ == '__main__':
    unittest.main()
