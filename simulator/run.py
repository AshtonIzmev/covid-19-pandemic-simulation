import time

from scenario.example import benchmark_base_lockdown
from simulator.constants.keys import draw_graph_key, show_plot_key
from simulator.helper.environment import get_environment_simulation
from simulator.helper.parser import parse_params
from simulator.helper.plot import chose_draw_plot


def main(argv=None):
    params = parse_params(argv)
    env_dic = get_environment_simulation(params)

    t_start = time.time()
    stats_result = benchmark_base_lockdown.launch_run(params, env_dic)
    print(f"It took : {time.time() - t_start:.2f} seconds")
    chose_draw_plot(params[draw_graph_key], stats_result, params[show_plot_key])
    return stats_result


if __name__ == '__main__':
    main()
