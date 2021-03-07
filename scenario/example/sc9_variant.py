import random

import numpy as np
import ray

from scenario.helper.scenario import get_zero_run_stats, is_weekend
from simulator.constants.keys import *
from simulator.helper.dynamic import propagate_to_stores, propagate_to_houses, propagate_to_workplaces, \
    increment_pandemic_1_day, update_run_stat, propagate_to_transportation
from simulator.helper.simulation import get_virus_simulation_t0
from ray.actor import ActorHandle


@ray.remote
def do_parallel_run(env_dic, params, run_id, specific_seed, pba: ActorHandle):
    run_stats = get_zero_run_stats(params)
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

    # Variant parameters
    variant_contagiosity = 1
    variant_mortality = 1
    variant_hospitalization = 1

    params[house_infect_key] = 0.5 * variant_contagiosity
    params[work_infection_key] = 0.05 * variant_contagiosity
    params[store_infection_key] = 0.02 * variant_contagiosity
    params[transport_infection_key] = 0.01 * variant_contagiosity
    params[variant_mortality_k] = variant_mortality
    params[variant_hospitalization_k] = variant_hospitalization
    params[innoculation_number_key] = 5
    available_beds = params[icu_bed_per_thousand_individual_key] * params[nindividual_key] / 1000
    virus_dic = get_virus_simulation_t0(params)

    for day in range(params[nday_key]):
        pba.update.remote(1)
        old_healthy = [(k, env_dic[IAG_K][k]) for k, v in virus_dic[STA_K].items() if v == HEALTHY_V]
        nb_indiv_vaccinated = max(0, int(params[nindividual_key] * rate_daily_vaccinated * (1-day/100)))
        if len(old_healthy) > nb_indiv_vaccinated:
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
