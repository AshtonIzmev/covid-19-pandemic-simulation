import random

import numpy as np
import ray
from ray.actor import ActorHandle

from scenario.helper.scenario import get_zero_run_stats, is_weekend
from simulator.constants.keys import *
from simulator.helper.dynamic import propagate_to_stores, propagate_to_houses, propagate_to_workplaces, \
    increment_pandemic_1_day, update_run_stat, propagate_to_transportation
from simulator.helper.simulation import get_virus_simulation_t0


@ray.remote
def do_parallel_run(env_dic, params, run_id, specific_seed, pba: ActorHandle):

    random.seed(specific_seed)
    np.random.seed(specific_seed)

    if len(params[additional_scenario_params_key]) < 1:
        raise AssertionError("Need more additional_scenario parameter")
    else:
        rate_daily_vaccinated = int(params[additional_scenario_params_key][0])

    if rate_daily_vaccinated < 0:
        # Morrocan daily rate of vaccination
        rate_daily_vaccinated = 0.00428

    params[store_preference_key] = 0.5
    params[remote_work_key] = 0.5
    params[innoculation_number_key] = 5
    available_beds = params[icu_bed_per_thousand_individual_key] * params[nindividual_key] / 1000

    run_stats = get_zero_run_stats(params)

    params[house_infect_key] = 0.5
    params[work_infection_key] = 0.05
    params[store_infection_key] = 0.02
    params[transport_infection_key] = 0.01

    params[immunity_bounds_key] = (270, 450)  # assuming about a year of immunity (~flu)
    virus_dic = get_virus_simulation_t0(params)

    for day in range(params[nday_key]):
        pba.update.remote(1)
        old_healthy = [(k, env_dic[IAG_K][k]) for k, v in virus_dic[STA_K].items() if v == HEALTHY_V]
        nb_indiv_vaccinated = max(0, int(params[nindividual_key] * rate_daily_vaccinated * (1-day/100)))
        if len(old_healthy) > nb_indiv_vaccinated and day <= 100:
            old_sorted = sorted(old_healthy, key=lambda kv: -kv[1])
            old_lucky = [o[0] for o in old_sorted[:nb_indiv_vaccinated]]
            virus_dic[STA_K].update((o, IMMUNE_V) for o in old_lucky)

        propagate_to_houses(env_dic, virus_dic, params[house_infect_key])
        if not is_weekend(day):
            propagate_to_transportation(env_dic, virus_dic, params[transport_infection_key],
                                        params[remote_work_key], params[transport_contact_cap_key])
            propagate_to_workplaces(env_dic, virus_dic, params[work_infection_key], params[remote_work_key])
        if is_weekend(day):
            propagate_to_stores(env_dic, virus_dic, params[store_infection_key], params[store_preference_key])
        increment_pandemic_1_day(env_dic, virus_dic, available_beds)

        update_run_stat(virus_dic, run_stats, day)
    return run_id, run_stats
