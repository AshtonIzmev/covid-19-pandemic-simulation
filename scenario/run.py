import os
import time

import joblib

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
from scenario.helper.ray import launch_parallel_byday, launch_parallel_byvariant
from simulator.constants.keys import draw_graph_key, ncpu_key, scenario_id_key, show_plot_key
from simulator.helper.environment import get_clean_env_params, get_environment_simulation_p
from simulator.helper.parser import parse_params
from simulator.helper.plot import chose_draw_plot

SCENARIO_BY_DAY = {
    -1: scx_base_just_a_flu,
    0: sc0_base_lockdown,
    1: sc1_simple_lockdown_removal,
    2: sc2_yoyo_lockdown_removal,
    3: sc3_loose_lockdown,
    4: sc4_rogue_citizen,
    5: sc5_rogue_neighborhood,
    6: sc6_travelers,
    7: sc7_nominal_lockdown_removal,
    8: sc8_innoculation,
    9: sc9_vaccination,
}

SCENARIO_BY_VARIANT = {
    10: sc10_variant,
}

ENV_MODEL_DIR = os.environ.get("PANDEMIC_SIMULATION_ENV_DIR", "env_models")


def get_or_build_environment(params):
    """Environments are expensive to build and depend only on the structural
    parameters, so they are cached on disk under their parameter signature."""
    params_env, key_env = get_clean_env_params(params)
    env_file = os.path.join(ENV_MODEL_DIR, "env_" + key_env + ".joblib")
    if os.path.exists(env_file):
        print(f"Using existing environment model {key_env}")
        return joblib.load(env_file)
    print(f"Building new environment model {key_env}")
    env_dic = get_environment_simulation_p(params_env)
    os.makedirs(ENV_MODEL_DIR, exist_ok=True)
    joblib.dump(env_dic, env_file)
    return env_dic


def run_scenario(params, env_dic):
    scenario_id = params[scenario_id_key]
    if scenario_id in SCENARIO_BY_DAY:
        return launch_parallel_byday(params, env_dic, SCENARIO_BY_DAY[scenario_id].do_parallel_run, params[ncpu_key])
    if scenario_id in SCENARIO_BY_VARIANT:
        return launch_parallel_byvariant(params, env_dic, SCENARIO_BY_VARIANT[scenario_id].do_parallel_run,
                                         params[ncpu_key])
    raise KeyError(f"Unknown scenario {scenario_id}, expected one of "
                   f"{sorted(SCENARIO_BY_DAY) + sorted(SCENARIO_BY_VARIANT)}")


def main(argv=None):
    params = parse_params(argv)
    t_start = time.time()
    env_dic = get_or_build_environment(params)
    stats_result = run_scenario(params, env_dic)
    print(f"It took : {time.time() - t_start:.2f} seconds")
    chose_draw_plot(params[draw_graph_key], stats_result, params[show_plot_key])
    return stats_result


if __name__ == '__main__':
    main()
