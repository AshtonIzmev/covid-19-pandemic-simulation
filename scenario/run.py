import random
import sys
import time

from scenario.example import sc1_simple_lockdown_removal, sc2_yoyo_lockdown_removal, sc0_base_lockdown, \
    scx_base_just_a_flu, sc3_loose_lockdown, sc4_rogue_citizen, sc5_rogue_neighborhood, sc6_travelers, \
    sc7_nominal_lockdown_removal
from scenario.helper.ray import launch_parallel_run
from simulator.constants.keys import scenario_id_key, random_seed_key, draw_graph_key, ncpu_key
from simulator.helper.environment import get_environment_simulation
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

    t_start = time.time()

    env_dic = get_environment_simulation(params)

    launch_fun = launch_parallel_run

    scenario_dic = {
        -1: scx_base_just_a_flu.do_parallel_run,
        0:  sc0_base_lockdown.do_parallel_run,
        1:  sc1_simple_lockdown_removal.do_parallel_run,
        2:  sc2_yoyo_lockdown_removal.do_parallel_run,
        3:  sc3_loose_lockdown.do_parallel_run,
        4:  sc4_rogue_citizen.do_parallel_run,
        5:  sc5_rogue_neighborhood.do_parallel_run,
        6:  sc6_travelers.do_parallel_run,
        7:  sc7_nominal_lockdown_removal.do_parallel_run
    }

    if params[scenario_id_key] in scenario_dic:
        stats_result = launch_parallel_run(params, env_dic, scenario_dic[params[scenario_id_key]], params[ncpu_key])
        print("It took : %.2f seconds" % (time.time() - t_start))
        chose_draw_plot(params[draw_graph_key], stats_result)
    else:
        sys.exit(0)
