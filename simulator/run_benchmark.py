import time

from scenario.example import benchmark_base_lockdown
from simulator.helper.environment import get_environment_simulation
from simulator.helper.parser import parse_params


def main(argv=None):
    params = parse_params(argv)

    t_start = time.time()
    env_dic = get_environment_simulation(params)
    print(f"Environment built in : {time.time() - t_start:.2f} seconds")

    t_start = time.time()
    stats_result = benchmark_base_lockdown.launch_run(params, env_dic, profile=True)
    print(f"It took : {time.time() - t_start:.2f} seconds")
    return stats_result


if __name__ == '__main__':
    main()
