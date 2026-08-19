import math

import numpy as np

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


def get_zero_stats(params_arg):
    return {
        "hea": np.zeros((params_arg[nrun_key], params_arg[nday_key])),
        "inf": np.zeros((params_arg[nrun_key], params_arg[nday_key])),
        "hos": np.zeros((params_arg[nrun_key], params_arg[nday_key])),
        "dea": np.zeros((params_arg[nrun_key], params_arg[nday_key])),
        "imm": np.zeros((params_arg[nrun_key], params_arg[nday_key])),
        "iso": np.zeros((params_arg[nrun_key], params_arg[nday_key])),
        "con": np.zeros((params_arg[nrun_key], params_arg[nday_key])),
        "R0d": np.zeros((params_arg[nrun_key], params_arg[nday_key])),
        "new": np.zeros((params_arg[nrun_key], params_arg[nday_key])),
        "loc": np.zeros((params_arg[nrun_key], params_arg[nday_key]))
    }


def get_zero_stats_variant(params_arg):
    return {
        "dea": np.zeros((params_arg[nrun_key], params_arg[nvariant_key])),
    }


def get_zero_run_stats(params_arg):
    return {
        "hea": np.zeros(params_arg[nday_key]),
        "inf": np.zeros(params_arg[nday_key]),
        "hos": np.zeros(params_arg[nday_key]),
        "dea": np.zeros(params_arg[nday_key]),
        "imm": np.zeros(params_arg[nday_key]),
        "iso": np.zeros(params_arg[nday_key]),
        "con": np.zeros(params_arg[nday_key]),
        "R0d": np.zeros(params_arg[nday_key]),
        "new": np.zeros(params_arg[nday_key]),
        "loc": np.zeros(params_arg[nday_key])
    }


def soften_full_lockdown(params_arg):
    params_arg[store_preference_key] = math.pow(params_arg[store_preference_key], 2)
    params_arg[remote_work_key] = math.pow(params_arg[remote_work_key], 2)
    soften_propagation_lockdown(params_arg)


def tighten_full_lockdown(params_arg):
    params_arg[store_preference_key] = math.sqrt(params_arg[store_preference_key])
    params_arg[remote_work_key] = math.sqrt(params_arg[remote_work_key])
    tighten_propagation_lockdown(params_arg)


def soften_propagation_lockdown(params_arg):
    params_arg[house_infect_key] = math.sqrt(params_arg[house_infect_key])
    params_arg[transport_infection_key] = math.sqrt(params_arg[transport_infection_key])
    params_arg[work_infection_key] = math.sqrt(params_arg[work_infection_key])
    params_arg[store_infection_key] = math.sqrt(params_arg[store_infection_key])


def tighten_propagation_lockdown(params_arg):
    params_arg[house_infect_key] = math.pow(params_arg[house_infect_key], 2)
    params_arg[transport_infection_key] = math.pow(params_arg[transport_infection_key], 2)
    params_arg[work_infection_key] = math.pow(params_arg[work_infection_key], 2)
    params_arg[store_infection_key] = math.pow(params_arg[store_infection_key], 2)


def measure_lockdown_strength(params_arg):
    return 1/(math.log(1+params_arg[house_infect_key]) + math.log(1+params_arg[transport_infection_key]) +
              math.log(1+params_arg[work_infection_key]) + math.log(1+params_arg[store_infection_key]) +
              math.log(2-params_arg[store_preference_key]) + math.log(2-params_arg[remote_work_key]))


# Assuming 0 is Monday
def is_weekend(i):
    return ((i - 5) % 7 == 0) or ((i - 6) % 7 == 0)


# Confined ("pcn") and back-to-normal ("pvn") values for the six parameters that
# scenarios 7 and 8 move as lockdown is progressively lifted.
CONFINED_PARAMS = {
    remote_work_key: 0.98,
    house_infect_key: 0.5,
    transport_infection_key: 0.01,
    work_infection_key: 0.01,
    store_infection_key: 0.02,
    store_preference_key: 0.95,
}

NORMAL_LIFE_PARAMS = {
    remote_work_key: 0.58,
    house_infect_key: 0.5,
    transport_infection_key: 0.05,
    work_infection_key: 0.05,
    store_infection_key: 0.1,
    store_preference_key: 0.30,
}


def apply_unlock_progress(params_arg, unlock_progress):
    """Interpolate the lockdown parameters between full lockdown and normal life.

    unlock_progress == 0 gives the confined values, 1 gives the back-to-normal ones.

    This used to read `confined * u + (normal - confined) * u`, which simplifies to
    `normal * u`: every infection probability was 0 while the lockdown was fully on,
    so the epidemic could not start at all until the first unlock step.
    """
    for key, confined in CONFINED_PARAMS.items():
        normal = NORMAL_LIFE_PARAMS[key]
        params_arg[key] = confined + (normal - confined) * unlock_progress
    return params_arg


def parse_bool(value):
    """argparse hands scenarios raw strings, so bool("0") would be True."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ("true", "1", "yes", "y"):
            return True
        if normalized in ("false", "0", "no", "n"):
            return False
        raise ValueError(f"Cannot read {value!r} as a boolean")
    return bool(value)


def read_extra_params(params_arg, *types):
    """Read and convert the --extra-scenario-params a scenario needs.

    Raises a ValueError naming the scenario's requirement instead of an
    IndexError several lines later.
    """
    extra = params_arg.get(additional_scenario_params_key) or []
    if len(extra) < len(types):
        raise ValueError(
            f"This scenario needs {len(types)} --extra-scenario-params, got {len(extra)}: {list(extra)}")
    return tuple(caster(value) for caster, value in zip(types, extra))
