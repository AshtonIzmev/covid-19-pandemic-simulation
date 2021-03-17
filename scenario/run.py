import os
import random
import sys
import time

import joblib
import numpy

from scenario.example import sc1_simple_lockdown_removal, sc2_yoyo_lockdown_removal, sc0_base_lockdown, \
    scx_base_just_a_flu, sc3_loose_lockdown, sc4_rogue_citizen, sc5_rogue_neighborhood, sc6_travelers, \
    sc7_nominal_lockdown_removal, sc8_innoculation, sc9_vaccination, sc10_variant
from scenario.helper.ray import launch_parallel_byday, launch_parallel_byvariant
from simulator.constants.keys import scenario_id_key, random_seed_key, draw_graph_key, ncpu_key, show_plot_key
from simulator.helper.environment import get_environment_simulation_p, get_clean_env_params
from simulator.helper.parser import get_parser
from simulator.helper.plot import chose_draw_plot
from simulator.helper.simulation import get_default_params

if __name__ == '__main__':
    params = get_default_params()

    args = get_parser().parse_args()
    for arg in vars(args):
        v = getattr(args, arg)
        if arg in params and v is not None:
            params[arg] = v
    random.seed(params[random_seed_key])
    numpy.random.seed(params[random_seed_key])

    t_start = time.time()

    params_env, key_env = get_clean_env_params(params)
    env_file = "env_models/env_" + key_env + ".joblib"

    if os.path.exists(env_file):
        print("Using existing environment model %s" % key_env)
        env_dic = joblib.load(env_file)
    else:
        print("Building new environment model %s" % key_env)
        env_dic = get_environment_simulation_p(params_env)
        joblib.dump(env_dic, env_file)

    scenario_day_dic = {
        -1: scx_base_just_a_flu.do_parallel_run,
        0:  sc0_base_lockdown.do_parallel_run,
        1:  sc1_simple_lockdown_removal.do_parallel_run,
        2:  sc2_yoyo_lockdown_removal.do_parallel_run,
        3:  sc3_loose_lockdown.do_parallel_run,
        4:  sc4_rogue_citizen.do_parallel_run,
        5:  sc5_rogue_neighborhood.do_parallel_run,
        6:  sc6_travelers.do_parallel_run,
        7:  sc7_nominal_lockdown_removal.do_parallel_run,
        8:  sc8_innoculation.do_parallel_run,
        9:  sc9_vaccination.do_parallel_run
    }

    scenario_variant_dic = {
        10: sc10_variant.do_parallel_run
    }

    if params[scenario_id_key] in scenario_day_dic:
        stats_result = launch_parallel_byday(params, env_dic, scenario_day_dic[params[scenario_id_key]],
                                             params[ncpu_key])
    elif params[scenario_id_key] in scenario_variant_dic:
        stats_result = launch_parallel_byvariant(params, env_dic, scenario_variant_dic[params[scenario_id_key]],
                                                 params[ncpu_key])
    else:
        raise KeyError("Unknown scenario")
    print("It took : %.2f seconds" % (time.time() - t_start))
    chose_draw_plot(params[draw_graph_key], stats_result, params[show_plot_key])
