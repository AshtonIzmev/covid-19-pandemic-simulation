from simulator.dynamic_helper import get_pandemic_statistics
from simulator.dynamic_helper import propagate_to_stores, propagate_to_houses, propagate_to_workplaces, \
    increment_pandemic_1_day
from simulator.plot_helper import draw_new_daily_cases, draw_population_state_daily
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


env_dic = get_environment_simulation(N_INDIVIDUALS, PROBA_SAME_HOUSE_RATE, NB_STORE_PER_HOUSE)
virus_dic = get_virus_simulation_t0(N_INDIVIDUALS, INITIAL_INNOCULATION_PCT)

stats = []
for _ in range(N_DAYS):
    propagate_to_houses(env_dic, virus_dic, PROB_HOUSE_INFECTION)
    if not (((_ - 5) % 7 == 0) or ((_ - 6) % 7 == 0)):
        propagate_to_workplaces(env_dic, virus_dic, PROB_WORK_INFECTION)
    propagate_to_stores(env_dic, virus_dic, PROB_STORE_INFECTION)
    increment_pandemic_1_day(env_dic, virus_dic)
    stats.append(get_pandemic_statistics(virus_dic))


draw_population_state_daily(stats, N_DAYS, N_INDIVIDUALS)

#draw_new_daily_cases(stats, N_DAYS)
