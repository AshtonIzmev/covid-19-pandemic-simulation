from initiator.core import build_individual_houses_map, build_house_individual_map, build_individual_work_map, \
    build_individual_adult_map, build_workplace_individual_map, build_individual_age_map, build_house_adult_map, \
    build_house_store_map, build_store_house_map, \
    build_geo_positions_house, build_geo_positions_store, build_geo_positions_workplace
from initiator.helper import get_r
from initiator.parameters import NB_STO_PER_HOU, PROBA_SAME_HOUSE_RATE
from simulator.helper import propagate_to_stores, propagate_to_houses, propagate_to_workplaces, \
    get_default_infection_parameters, increment_pandemic_1_day, \
    get_healthy_people, get_deadpeople, get_infected_people, get_immune_people
from simulator.helper import draw_population_state_daily, draw_new_daily_cases

# Main parameters
N_INDIVIDUALS = 1000  # number of people
N_DAYS = 100  # Number of simulated days

inn_ind_cov = dict(zip(range(N_INDIVIDUALS), [int(get_r() <= 0.005) for i in range(N_INDIVIDUALS)]))

# Infection dictionnary initialization
all_ind_inf = dict(zip(range(N_INDIVIDUALS), [-1] * N_INDIVIDUALS))
all_ind_con = dict(zip(range(N_INDIVIDUALS), [-1] * N_INDIVIDUALS))
ind_infected_init = [k for k,v in inn_ind_cov.items() if v == 1]

for ind in ind_infected_init:
    incubation, contagiosity = get_default_infection_parameters()
    all_ind_inf[ind] = incubation
    all_ind_con[ind] = contagiosity


all_ind_hou = build_individual_houses_map(N_INDIVIDUALS, PROBA_SAME_HOUSE_RATE)
all_hou_ind = build_house_individual_map(all_ind_hou)
all_ind_adu = build_individual_adult_map(all_ind_hou)
all_ind_age = build_individual_age_map(all_ind_hou)

all_ind_wor = build_individual_work_map(all_ind_adu)
all_wor_ind = build_workplace_individual_map(all_ind_wor)
all_hou_adu = build_house_adult_map(all_ind_hou, all_ind_adu)

geo_hou = build_geo_positions_house(len(all_hou_ind))
geo_wor = build_geo_positions_workplace(len(all_wor_ind))
geo_sto = build_geo_positions_store(int(len(all_hou_ind)/NB_STO_PER_HOU))

all_hou_sto = build_house_store_map(geo_sto, geo_hou)
all_sto_hou = build_store_house_map(all_hou_sto)


stats = []
for _ in range(N_DAYS):
    # INFECTION AT HOME
    propagate_to_houses(all_ind_hou, all_hou_ind, all_ind_inf, all_ind_con)
    if not (((_ - 5) % 7 == 0) or ((_ - 6) % 7 == 0)):
        propagate_to_workplaces(all_ind_wor, all_wor_ind, all_ind_inf, all_ind_con)
    propagate_to_stores(all_ind_hou, all_hou_sto, all_sto_hou, all_hou_adu, all_ind_inf, all_ind_con)
    increment_pandemic_1_day(all_ind_inf, all_ind_age, all_ind_con)
    stats.append((len(get_healthy_people(all_ind_inf)),
                  len(get_infected_people(all_ind_inf)),
                  len(get_deadpeople(all_ind_inf)),
                  len(get_immune_people(all_ind_inf))))


# draw_population_state_daily(stats, N_DAYS, N_INDIVIDUALS)

draw_new_daily_cases(stats, N_DAYS)
