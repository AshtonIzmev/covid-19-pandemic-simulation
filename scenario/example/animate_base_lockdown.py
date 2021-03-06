import numpy as np

from simulator.constants.keys import nindividual_key, nday_key, innoculation_number_key, remote_work_key, \
    store_preference_key, house_infect_key, work_infection_key, store_infection_key, transport_infection_key, \
    transport_contact_cap_key, icu_bed_per_thousand_individual_key, STA_K
from simulator.helper.dynamic import propagate_to_stores, propagate_to_houses, propagate_to_workplaces, \
    increment_pandemic_1_day, propagate_to_transportation
from simulator.helper.simulation import get_virus_simulation_t0

ind_works = []
ind_stos = []
stas = []


# This scenario is the basic one with a classic dynamic
def launch_run(params, env_dic):
    params[store_preference_key] = 0.95
    params[remote_work_key] = 0.98
    params[innoculation_number_key] = 5
    available_beds = params[icu_bed_per_thousand_individual_key] * params[nindividual_key] / 1000

    virus_dic = get_virus_simulation_t0(params)
    for day in range(params[nday_key]):
        propagate_to_houses(env_dic, virus_dic, params[house_infect_key])
        propagate_to_transportation(env_dic, virus_dic, params[transport_infection_key],
                                    params[remote_work_key], params[transport_contact_cap_key])
        ind_work = propagate_to_workplaces(env_dic, virus_dic, params[work_infection_key], params[remote_work_key])
        ind_sto = propagate_to_stores(env_dic, virus_dic, params[store_infection_key], params[store_preference_key])
        increment_pandemic_1_day(env_dic, virus_dic, available_beds)
        ind_works.append(ind_work)
        ind_stos.append(ind_sto)
        stas.append(virus_dic[STA_K])


