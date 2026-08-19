"""The progress bar plumbing, driven directly rather than through ray."""
import asyncio
import unittest
from unittest import mock

import numpy as np

from scenario.helper.progressbar_actor import ProgressBarActor
from scenario.helper.ray import launch_run
from scenario.helper.scenario import get_zero_run_stats, get_zero_stats
from simulator.constants.keys import nday_key, nrun_key

# The @ray.remote decorator wraps the class; this is the plain one underneath.
PlainProgressBarActor = ProgressBarActor.__ray_metadata__.modified_class


class TestProgressBarActor(unittest.TestCase):

    def setUp(self):
        self.actor = PlainProgressBarActor()

    def test_it_starts_empty(self):
        self.assertEqual(self.actor.get_counter(), 0)

    def test_update_accumulates(self):
        self.actor.update(3)
        self.actor.update(4)
        self.assertEqual(self.actor.get_counter(), 7)

    def test_wait_for_update_returns_the_delta_and_the_total(self):
        self.actor.update(2)
        delta, counter = asyncio.run(self.actor.wait_for_update())
        self.assertEqual((delta, counter), (2, 2))

    def test_the_delta_resets_between_waits_but_the_counter_does_not(self):
        self.actor.update(2)
        asyncio.run(self.actor.wait_for_update())
        self.actor.update(5)
        delta, counter = asyncio.run(self.actor.wait_for_update())
        self.assertEqual((delta, counter), (5, 7))


class TestSequentialLaunchRun(unittest.TestCase):
    """`launch_run` is the single-process path, used when ray is not wanted."""

    @staticmethod
    def fake_run(env_dic, params, run_id):
        run_stats = get_zero_run_stats(params)
        run_stats["dea"][:] = run_id + 1
        return run_id, run_stats

    def test_it_merges_every_run_into_the_right_row(self):
        params = {nrun_key: 3, nday_key: 4}
        with mock.patch("scenario.helper.ray.print_progress_bar"):
            stats = launch_run(params, {}, self.fake_run)
        self.assertEqual(stats["dea"].shape, (3, 4))
        for run_id in range(3):
            np.testing.assert_array_equal(stats["dea"][run_id], np.full(4, run_id + 1.0))

    def test_it_reports_progress_once_per_run(self):
        params = {nrun_key: 5, nday_key: 2}
        with mock.patch("scenario.helper.ray.print_progress_bar") as mock_bar:
            launch_run(params, {}, self.fake_run)
        self.assertEqual(mock_bar.call_count, 5)

    def test_progress_can_be_silenced(self):
        params = {nrun_key: 2, nday_key: 2}
        with mock.patch("scenario.helper.ray.print_progress_bar") as mock_bar:
            launch_run(params, {}, self.fake_run, display_progress=False)
        self.assertFalse(mock_bar.called)

    def test_it_returns_the_same_keys_as_the_parallel_path(self):
        params = {nrun_key: 1, nday_key: 3}
        stats = launch_run(params, {}, self.fake_run, display_progress=False)
        self.assertEqual(sorted(stats), sorted(get_zero_stats(params)))


if __name__ == '__main__':
    unittest.main()
