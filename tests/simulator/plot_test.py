import random
import unittest
from unittest import mock

import numpy as np

from simulator.helper.plot import draw_population_state_daily, draw_specific_population_state_daily, \
    draw_lockdown_state_daily, draw_new_daily_cases, draw_summary, draw_examples, draw_r0_evolution, chose_draw_plot


class TestSimulation(unittest.TestCase):

    @classmethod
    def setUp(cls):
        random.seed(12)

    @staticmethod
    def get_stats(is_empty=True):
        nrun = 10
        nday = 100
        return {
            "hea": (0 if is_empty else 1000) + np.zeros((nrun, nday)),
            "inf": np.zeros((nrun, nday)),
            "hos": np.zeros((nrun, nday)),
            "dea": np.zeros((nrun, nday)),
            "imm": np.zeros((nrun, nday)),
            "iso": np.zeros((nrun, nday)),
            "R0": np.zeros((nrun, nday)),
            "new": np.zeros((nrun, nday)),
            "loc": np.zeros((nrun, nday))
        }

    @mock.patch("simulator.helper.plot.plt.show")
    def test_error_in_stats(self, mock_plt):
        try:
            draw_population_state_daily(self.get_stats())
        except ValueError:
            self.assertTrue(True)
            return
        self.assertTrue(False)
        assert mock_plt.called

    @mock.patch("simulator.helper.plot.plt.show")
    def test_draw_population_state_daily(self, mock_plt):
        draw_population_state_daily(self.get_stats(is_empty=False))
        assert mock_plt.called

    @mock.patch("simulator.helper.plot.plt.show")
    def test_draw_specific_population_state_daily(self, mock_plt):
        draw_specific_population_state_daily(self.get_stats(is_empty=False))
        assert mock_plt.called

    @mock.patch("simulator.helper.plot.plt.show")
    def test_draw_lockdown_state_daily(self, mock_plt):
        draw_lockdown_state_daily(self.get_stats(is_empty=False))
        assert mock_plt.called

    @mock.patch("simulator.helper.plot.plt.show")
    def test_draw_new_daily_cases(self, mock_plt):
        draw_new_daily_cases(self.get_stats(is_empty=False))
        assert mock_plt.called

    @mock.patch("simulator.helper.plot.plt.show")
    def test_draw_summary(self, mock_plt):
        draw_summary(self.get_stats(is_empty=False))
        assert mock_plt.called

    @mock.patch("simulator.helper.plot.plt.show")
    def test_draw_examples(self, mock_plt):
        draw_examples(self.get_stats(is_empty=False))
        assert mock_plt.called

    @mock.patch("simulator.helper.plot.plt.show")
    def test_draw_r0_evolution(self, mock_plt):
        draw_r0_evolution(self.get_stats(is_empty=False))
        assert mock_plt.called

    @mock.patch("simulator.helper.plot.plt.show")
    def test_chose_draw_plot(self, mock_plt):
        chose_draw_plot(["pop"], self.get_stats(is_empty=False))
        assert mock_plt.called
        chose_draw_plot(["R0"], self.get_stats(is_empty=False))
        assert mock_plt.called
        chose_draw_plot(["summ"], self.get_stats(is_empty=False))
        assert mock_plt.called
        chose_draw_plot(["lock"], self.get_stats(is_empty=False))
        assert mock_plt.called
        chose_draw_plot(["new"], self.get_stats(is_empty=False))
        assert mock_plt.called
        chose_draw_plot(["hos"], self.get_stats(is_empty=False))
        assert mock_plt.called


if __name__ == '__main__':
    unittest.main()

