import random
import sys
import time

from scenario.example import sc1_simple_lockdown_removal, sc2_yoyo_lockdown_removal, sc0_base_lockdown, \
    scx_base_just_a_flu, sc3_loose_lockdown, sc4_rogue_citizen, sc5_rogue_neighborhood
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

    if params[scenario_id_key] == -1:
        stats_result = scx_base_just_a_flu.launch_run()
    elif params[scenario_id_key] == 0:  # Total lockdown
        stats_result = sc0_base_lockdown.launch_run()
    elif params[scenario_id_key] == 1:  # Lockdown removal after N days
        stats_result = sc1_simple_lockdown_removal.launch_run()
    elif params[scenario_id_key] == 2:  # Yoyo lockdown removal
        stats_result = sc2_yoyo_lockdown_removal.launch_run()
    elif params[scenario_id_key] == 3:  # Yoyo lockdown removal
        stats_result = sc3_loose_lockdown.launch_run()
    elif params[scenario_id_key] == 4:  # Rogue citizen
        stats_result = sc4_rogue_citizen.launch_run()
    elif params[scenario_id_key] == 5:  # Rogue block
        stats_result = sc5_rogue_neighborhood.launch_run()
    else:
        sc5_rogue_neighborhood.launch_run()
        sys.exit(0)
    print("It took : %.2f seconds" % (time.time() - t_start))

    chose_draw_plot(params[draw_graph_key], stats_result)
