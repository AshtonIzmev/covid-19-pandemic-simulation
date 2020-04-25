import random
import sys
import time
from scenario.example import simple_lockdown_removal_scenario_1, yoyo_lockdown_removal_scenario, \
    base_lockdown_scenario_0, base_just_a_flu_scenario_X
from simulator.parameters import *
from simulator.plot_helper import chose_draw_plot
from simulator.run_helper import get_parser

if __name__ == '__main__':
    args = get_parser().parse_args()
    for arg in vars(args):
        v = getattr(args, arg)
        if arg in params and v is not None:
            params[arg] = v

    random.seed(params[random_seed_key])

    t_start = time.time()

    # params[scenario_id_key] = -1
    # params[nrun_key] = 20
    # params[draw_graph_key] = ['examples']

    if params[scenario_id_key] == -1:
        stats_result = base_just_a_flu_scenario_X.launch_run()
    elif params[scenario_id_key] == 0:  # Total lockdown
        stats_result = base_lockdown_scenario_0.launch_run()
    elif params[scenario_id_key] == 1:  # Lockdown removal after N days
        stats_result = simple_lockdown_removal_scenario_1.launch_run()
    elif params[scenario_id_key] == 2:  # Yoyo lockdown removal
        stats_result = yoyo_lockdown_removal_scenario.launch_run()
    else:
        sys.exit(0)
    print("It took : %.2f seconds" % (time.time() - t_start))

    chose_draw_plot(params[draw_graph_key], stats_result)
