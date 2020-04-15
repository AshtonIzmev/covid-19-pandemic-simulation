import sys
from simulator.dynamic_helper import get_pandemic_statistics
from simulator.dynamic_helper import propagate_to_stores, propagate_to_houses, propagate_to_workplaces, \
    increment_pandemic_1_day, is_weekend
from simulator.plot_helper import draw_new_daily_cases, draw_population_state_daily, print_progress_bar
from simulator.simulation_helper import get_environment_simulation, get_virus_simulation_t0

# Main parameters
N_INDIVIDUALS = 5000  # number of people
N_DAYS = 120  # Number of simulated days
NB_STORE_PER_HOUSE = 20  # Let's say we have 20 houses for each grocerie store
PROBA_SAME_HOUSE_RATE = 0.1  # probability used to set the number of person per house
INITIAL_INNOCULATION_PCT = 0.005  # Proportion of people innoculated at day 0
PROB_HOUSE_INFECTION = 0.5  # Probabilty of infecting a random family member (same house)
PROB_WORK_INFECTION = 0.1  # Probabilty of infecting a random co-worker
PROB_STORE_INFECTION = 0.05  # Probabilty of infecting someone who goes to the same store


def run_simulation():
    print('Preparing environment...')
    env_dic = get_environment_simulation(N_INDIVIDUALS, PROBA_SAME_HOUSE_RATE, NB_STORE_PER_HOUSE)
    print('Preparing virus conditions...')
    virus_dic = get_virus_simulation_t0(N_INDIVIDUALS, INITIAL_INNOCULATION_PCT)

    stats = []
    print_progress_bar(0, N_DAYS, prefix='Progress:', suffix='Complete', length=50)
    for i in range(N_DAYS):
        print_progress_bar(i + 1, N_DAYS, prefix='Progress:', suffix='Complete', length=50)
        propagate_to_houses(env_dic, virus_dic, PROB_HOUSE_INFECTION)
        if not is_weekend(i):
            propagate_to_workplaces(env_dic, virus_dic, PROB_WORK_INFECTION)
        propagate_to_stores(env_dic, virus_dic, PROB_STORE_INFECTION)
        increment_pandemic_1_day(env_dic, virus_dic)
        stats.append(get_pandemic_statistics(virus_dic))
    return stats


if __name__ == '__main__':
    if len(sys.argv) == 2:
        stats_result = run_simulation()
        if sys.argv[1] == "new":
            draw_new_daily_cases(stats_result, N_DAYS)
        elif sys.argv[1] == "state":
            draw_population_state_daily(stats_result, N_DAYS, N_INDIVIDUALS)