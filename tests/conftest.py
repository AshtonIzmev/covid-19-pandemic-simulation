"""Shared pytest configuration.

Two things matter for this suite:

* matplotlib must never try to open a window (CI has no display);
* ray must be started once for the whole session, not once per test, because
  spinning a cluster up and down is what made the old suite slow.
"""
import logging
import os
import random

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")

# Every drawing test goes through this directory instead of ./images/output.
os.environ.setdefault("PANDEMIC_SIMULATION_OUTPUT_DIR", "")

TEST_SEED = 12


@pytest.fixture(autouse=True)
def deterministic_seeds():
    """Every test starts from the same RNG state."""
    random.seed(TEST_SEED)
    np.random.seed(TEST_SEED)


@pytest.fixture(scope="session")
def ray_session():
    """A single local ray instance shared by every scenario test."""
    ray = pytest.importorskip("ray")
    ray.init(include_dashboard=False, logging_level=logging.ERROR, num_cpus=2,
             ignore_reinit_error=True, log_to_driver=False)
    yield ray
    ray.shutdown()


@pytest.fixture
def output_dir(tmp_path, monkeypatch):
    """Point the plot helpers at a throwaway directory."""
    from simulator.helper import plot

    target = tmp_path / "output"
    monkeypatch.setattr(plot, "OUTPUT_DIR", str(target))
    return target
