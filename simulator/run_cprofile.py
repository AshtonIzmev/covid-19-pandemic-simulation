import random
import time

from scenario.example import base_just_a_flu_scenario_X
from simulator.parameters import *
from simulator.plot_helper import chose_draw_plot
from simulator.run_helper import get_parser

if __name__ == '__main__':
    args = get_parser().parse_args()
    for arg in vars(args):
        v = getattr(args, arg)
        if arg in params and v is not None:
            params[arg] = v

    params[nindividual_key] = 35000

    random.seed(params[random_seed_key])
    t_start = time.time()
    stats_result = base_just_a_flu_scenario_X.launch_run()
    print("It took : %.2f seconds" % (time.time() - t_start))
    chose_draw_plot(params[draw_graph_key], stats_result)
