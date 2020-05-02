import random
import time

from scenario.example import sc0_base_lockdown
from simulator.constants.keys import random_seed_key, draw_graph_key
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
    stats_result = sc0_base_lockdown.launch_run()
    print("It took : %.2f seconds" % (time.time() - t_start))
    chose_draw_plot(params[draw_graph_key], stats_result)
