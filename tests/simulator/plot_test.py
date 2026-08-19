import unittest
from unittest import mock

import matplotlib.pyplot as plt
import numpy as np
import pytest

from simulator.helper.plot import (
    DRAW_PREFIXES,
    chose_draw_plot,
    contains_substring,
    draw_examples,
    draw_lockdown_state_daily,
    draw_meta_simulation,
    draw_new_daily_cases,
    draw_population_state_daily,
    draw_r0_daily_evolution,
    draw_r0_evolution,
    draw_specific_population_state_daily,
    draw_summary,
    print_progress_bar,
    rolling_max,
    sem_or_zero,
)

NRUN = 10
NDAY = 100


def get_stats(is_empty=True, nrun=NRUN, nday=NDAY):
    """A statistics dict shaped like the one a scenario run produces."""
    rng = np.random.RandomState(4)
    return {
        "hea": np.zeros((nrun, nday)) if is_empty else 1000 - rng.randint(0, 50, (nrun, nday)),
        "inf": rng.random_sample((nrun, nday)),
        "hos": rng.random_sample((nrun, nday)),
        "dea": rng.random_sample((nrun, nday)),
        "imm": rng.random_sample((nrun, nday)),
        "iso": rng.random_sample((nrun, nday)),
        "con": rng.random_sample((nrun, nday)),
        "R0d": rng.random_sample((nrun, nday)),
        "new": rng.random_sample((nrun, nday)),
        "loc": rng.random_sample((nrun, nday)),
    }


ALL_DRAWERS = [
    (draw_population_state_daily, {}),
    (draw_specific_population_state_daily, {}),
    (draw_lockdown_state_daily, {}),
    (draw_new_daily_cases, {}),
    (draw_summary, {}),
    (draw_examples, {}),
    (draw_r0_daily_evolution, {}),
    (draw_r0_evolution, {}),
]


class TestDrawersShow(unittest.TestCase):
    """With show_plot=True nothing must reach the filesystem."""

    @mock.patch("simulator.helper.plot.plt.show")
    def test_every_drawer_shows_a_figure(self, mock_show):
        for drawer, kwargs in ALL_DRAWERS:
            with self.subTest(drawer=drawer.__name__):
                mock_show.reset_mock()
                self.assertIsNone(drawer(get_stats(is_empty=False), True, **kwargs))
                self.assertTrue(mock_show.called, f"{drawer.__name__} did not show anything")
                plt.close("all")

    @mock.patch("simulator.helper.plot.plt.show")
    def test_draw_meta_simulation_shows_a_figure(self, mock_show):
        draw_meta_simulation({"dea": np.array([[10.0, 20.0, 30.0], [12.0, 18.0, 33.0]])}, True)
        self.assertTrue(mock_show.called)
        plt.close("all")

    @mock.patch("simulator.helper.plot.plt.show")
    def test_every_style_of_the_specific_plot(self, mock_show):
        for style in ("P", "I", "D", "M", "H"):
            with self.subTest(style=style):
                draw_specific_population_state_daily(get_stats(is_empty=False), True, style=style)
                self.assertTrue(mock_show.called)
                plt.close("all")

    def test_an_empty_population_is_rejected_rather_than_drawn(self):
        # A run where nobody is ever healthy means the statistics are broken;
        # matplotlib should not be asked to build ticks out of it.
        with self.assertRaises(ValueError):
            draw_population_state_daily(get_stats(is_empty=True), True)
        plt.close("all")

    def test_draw_examples_needs_enough_runs_for_the_grid(self):
        with self.assertRaises(AssertionError):
            draw_examples(get_stats(is_empty=False, nrun=4), True)
        plt.close("all")


@pytest.mark.usefixtures("output_dir")
class TestDrawersSave(unittest.TestCase):
    """With show_plot=False every drawer writes one png and closes its figure."""

    @pytest.fixture(autouse=True)
    def _output_dir(self, output_dir):
        self.output_dir = output_dir

    def test_every_drawer_writes_a_png(self):
        for drawer, kwargs in ALL_DRAWERS:
            with self.subTest(drawer=drawer.__name__):
                path = drawer(get_stats(is_empty=False), False, **kwargs)
                self.assertTrue(path.endswith(".png"))
                self.assertTrue(self.output_dir.joinpath(path.split("/")[-1]).exists())

    def test_the_output_directory_is_created_on_demand(self):
        self.assertFalse(self.output_dir.exists())
        draw_new_daily_cases(get_stats(is_empty=False), False)
        self.assertTrue(self.output_dir.is_dir())

    def test_saved_figures_are_closed(self):
        plt.close("all")
        for _ in range(5):
            draw_new_daily_cases(get_stats(is_empty=False), False)
        self.assertEqual(plt.get_fignums(), [], "figures are leaking between draws")


class TestChoseDrawPlot(unittest.TestCase):

    @mock.patch("simulator.helper.plot.plt.show")
    def test_each_token_selects_its_own_drawer(self, mock_show):
        for token, expected in (("pop", "pop"), ("new", "new"), ("hos", "hos"), ("summ", "sum"),
                                ("lock", "loc"), ("exa", "ex"), ("R0", "R0")):
            with self.subTest(token=token):
                self.assertEqual(chose_draw_plot([token], get_stats(is_empty=False), True), [expected])
                plt.close("all")

    @mock.patch("simulator.helper.plot.plt.show")
    def test_r0d_does_not_also_trigger_the_sliding_r0(self, mock_show):
        # "R0d" starts with "R0", so the old chain drew both graphs.
        self.assertEqual(chose_draw_plot(["R0d"], get_stats(is_empty=False), True), ["R0d"])
        plt.close("all")

    @mock.patch("simulator.helper.plot.plt.show")
    def test_metasimu_is_reachable(self, mock_show):
        # It used to hang off an `elif` on the R0 branch, so `--draw R0 metasimu`
        # silently skipped it.
        drawn = chose_draw_plot(["metasimu"], {"dea": np.array([[1.0, 2.0], [3.0, 4.0]])}, True)
        self.assertEqual(drawn, ["metasimu"])
        plt.close("all")

    @mock.patch("simulator.helper.plot.plt.show")
    def test_several_tokens_draw_several_graphs(self, mock_show):
        drawn = chose_draw_plot(["exa", "pop", "summ", "R0"], get_stats(is_empty=False), True)
        self.assertEqual(sorted(drawn), sorted(["ex", "pop", "sum", "R0"]))
        plt.close("all")

    @mock.patch("simulator.helper.plot.plt.show")
    def test_a_repeated_token_only_draws_once(self, mock_show):
        self.assertEqual(chose_draw_plot(["pop", "population"], get_stats(is_empty=False), True), ["pop"])
        plt.close("all")

    def test_no_token_draws_nothing(self):
        self.assertEqual(chose_draw_plot([], get_stats(is_empty=False), True), [])
        self.assertEqual(chose_draw_plot(None, get_stats(is_empty=False), True), [])

    def test_an_unknown_token_is_reported(self):
        with self.assertRaises(KeyError):
            chose_draw_plot(["not-a-graph"], get_stats(is_empty=False), True)

    def test_every_advertised_prefix_is_selectable(self):
        for prefix, _ in DRAW_PREFIXES:
            match = max((p for p in DRAW_PREFIXES if prefix.startswith(p[0])), key=lambda p: len(p[0]))
            self.assertEqual(match[0], prefix)


class TestPlotUtilities(unittest.TestCase):

    def test_contains_substring(self):
        self.assertTrue(contains_substring("pop", ["population"]))
        self.assertTrue(contains_substring("R0", ["exa", "R0"]))
        self.assertFalse(contains_substring("pop", ["exa", "summ"]))
        self.assertFalse(contains_substring("pop", []))

    def test_sem_or_zero_matches_scipy_for_several_runs(self):
        from scipy import stats as scipy_stats
        values = np.random.RandomState(0).random_sample((6, 20))
        np.testing.assert_allclose(sem_or_zero(values), scipy_stats.sem(values, axis=0))

    def test_sem_or_zero_returns_zeros_for_a_single_run(self):
        # scipy returns nan here, which makes matplotlib drop the error bars.
        result = sem_or_zero(np.ones((1, 8)))
        self.assertEqual(result.shape, (8,))
        self.assertTrue(np.all(result == 0))

    def test_rolling_max(self):
        # Sliding windows of 3: [1,3,2] [3,2,5] [2,5,4] [5,4,0]
        np.testing.assert_array_equal(rolling_max(np.array([1, 3, 2, 5, 4, 0]), 3),
                                      np.array([3, 5, 5, 5]))

    def test_rolling_max_window_of_one_is_the_identity(self):
        values = np.array([4, 1, 7, 2])
        np.testing.assert_array_equal(rolling_max(values, 1), values)

    def test_rolling_max_never_decreases_within_a_window(self):
        values = np.random.RandomState(1).randint(0, 100, 40)
        result = rolling_max(values, 7)
        self.assertEqual(len(result), len(values) - 7 + 1)
        for i, maximum in enumerate(result):
            self.assertEqual(maximum, values[i:i + 7].max())

    def test_print_progress_bar(self, ):
        with mock.patch("builtins.print") as mock_print:
            print_progress_bar(5, 10, prefix="Progress:", length=10)
            self.assertTrue(mock_print.called)
            self.assertIn("50.0%", mock_print.call_args[0][0])

    def test_print_progress_bar_terminates_the_line_when_complete(self):
        with mock.patch("builtins.print") as mock_print:
            print_progress_bar(10, 10, length=10)
            self.assertEqual(mock_print.call_count, 2)
            self.assertIn("100.0%", mock_print.call_args_list[0][0][0])


if __name__ == '__main__':
    unittest.main()
