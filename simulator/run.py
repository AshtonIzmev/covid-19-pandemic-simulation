from simulator.dynamic_helper import propagate_to_stores, propagate_to_houses, propagate_to_workplaces, \
    increment_pandemic_1_day, is_weekend, get_pandemic_statistics
from simulator.parameters import *
from simulator.plot_helper import draw_new_daily_cases, draw_population_state_daily, print_progress_bar, \
    draw_specific_population_state_daily, draw_summary
from simulator.run_helper import get_parser
from simulator.simulation_helper import get_environment_simulation, get_virus_simulation_t0


def launch_run():
    print('Preparing environment...')
    env_dic = get_environment_simulation(params[nindividual_key], params[same_house_p_key],
                                         params[store_per_house_key])
    print('Preparing virus conditions...')
    virus_dic = get_virus_simulation_t0(params[nindividual_key], params[innoculation_pct_key],
                                        params[contagion_bounds_key], params[hospitalization_bounds_key],
                                        params[death_bounds_key], params[immunity_bounds_key])

    stats = []
    print_progress_bar(0, params[nday_key], prefix='Progress:', suffix='Complete', length=50)
    for r in range(params[nrun_key]):
        for i in range(params[nday_key]):
            print_progress_bar(i + 1, params[nday_key] * params[nrun_key], prefix='Progress:', suffix='Complete', length=50)
            propagate_to_houses(env_dic, virus_dic, params[house_infect_key])
            if not is_weekend(i):
                propagate_to_workplaces(env_dic, virus_dic, params[work_infection_key])
            if is_weekend(i):
                propagate_to_stores(env_dic, virus_dic, params[store_infection_key])
            increment_pandemic_1_day(env_dic, virus_dic)
            stats.append(get_pandemic_statistics(virus_dic))

    return stats


if __name__ == '__main__':
    args = get_parser().parse_args()
    for arg in vars(args):
        v = getattr(args, arg)
        if arg in params and v is not None:
            params[arg] = v

    stats_result = launch_run()
    if args.new_cases:
        draw_new_daily_cases(stats_result, params[nrun_key], params[nday_key], params[nindividual_key])
    if args.hospitalized_cases:
        draw_specific_population_state_daily(stats_result, params[nrun_key], params[nday_key], params[nindividual_key])
    if args.population_state:
        draw_population_state_daily(stats_result, params[nrun_key], params[nday_key], params[nindividual_key])
    if args.summary:
        draw_summary(stats_result, params[nrun_key], params[nday_key], params[nindividual_key])

