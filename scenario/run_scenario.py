import random

from scenario import basic_scenario
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

    stats_result = basic_scenario.launch_run()
    chose_draw_plot(args, basic_scenario.launch_run())

