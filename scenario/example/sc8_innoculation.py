import random

import numpy as np
import ray

from scenario.helper.scenario import get_zero_run_stats, is_weekend, measure_lockdown_strength
from simulator.constants.keys import nindividual_key, nday_key, innoculation_number_key, remote_work_key, \
    store_preference_key, house_infect_key, work_infection_key, store_infection_key, transport_infection_key, \
    transport_contact_cap_key, icu_bed_per_thousand_individual_key, STA_K, \
    IAG_K, ISOLATED_V, HEALTHY_V, additional_scenario_params_key, IAD_K
from simulator.helper.dynamic import propagate_to_stores, propagate_to_houses, propagate_to_workplaces, \
    increment_pandemic_1_day, update_run_stat, propagate_to_transportation, get_hospitalized_people
from simulator.helper.simulation import get_virus_simulation_t0
from ray.actor import ActorHandle


@ray.remote
def do_parallel_run(env_dic, params, run_id, specific_seed, pba: ActorHandle):
    run_stats = get_zero_run_stats(params)
    random.seed(specific_seed)
    np.random.seed(specific_seed)

    if len(params[additional_scenario_params_key]) < 1:
        raise AssertionError("Need more additional_scenario parameter")

    age_cutoff = int(params[additional_scenario_params_key][0])

    params[innoculation_number_key] = 5

    days_to_lockdown_change = 0
    unlock_progress = 0

    pcn = (0.98, 0.5, 0.01, 0.01, 0.02, 0.95)
    pvn = (0.58, 0.5, 0.05, 0.05, 0.1, 0.30)

    params[remote_work_key] = pcn[0] * unlock_progress + (pvn[0] - pcn[0]) * unlock_progress
    params[house_infect_key] = pcn[1] * unlock_progress + (pvn[1] - pcn[1]) * unlock_progress
    params[transport_infection_key] = pcn[2] * unlock_progress + (pvn[2] - pcn[2]) * unlock_progress
    params[work_infection_key] = pcn[3] * unlock_progress + (pvn[3] - pcn[3]) * unlock_progress
    params[store_infection_key] = pcn[4] * unlock_progress + (pvn[4] - pcn[4]) * unlock_progress
    params[store_preference_key] = pcn[5] * unlock_progress + (pvn[5] - pcn[5]) * unlock_progress

    params[innoculation_number_key] = 5
    available_beds = params[icu_bed_per_thousand_individual_key] * params[nindividual_key] / 1000

    virus_dic = get_virus_simulation_t0(params)

    for day in range(params[nday_key]):
        pba.update.remote(1)
        params[remote_work_key] = pcn[0] * unlock_progress + (pvn[0] - pcn[0]) * unlock_progress
        params[house_infect_key] = pcn[1] * unlock_progress + (pvn[1] - pcn[1]) * unlock_progress
        params[transport_infection_key] = pcn[2] * unlock_progress + (pvn[2] - pcn[2]) * unlock_progress
        params[work_infection_key] = pcn[3] * unlock_progress + (pvn[3] - pcn[3]) * unlock_progress
        params[store_infection_key] = pcn[4] * unlock_progress + (pvn[4] - pcn[4]) * unlock_progress
        params[store_preference_key] = pcn[5] * unlock_progress + (pvn[5] - pcn[5]) * unlock_progress

        propagate_to_houses(env_dic, virus_dic, params[house_infect_key])
        if not is_weekend(day):
            propagate_to_transportation(env_dic, virus_dic, params[transport_infection_key],
                                        params[remote_work_key], params[transport_contact_cap_key])
            propagate_to_workplaces(env_dic, virus_dic, params[work_infection_key], params[remote_work_key])
        if is_weekend(day):
            propagate_to_stores(env_dic, virus_dic, params[store_infection_key], params[store_preference_key])
        increment_pandemic_1_day(env_dic, virus_dic, available_beds)

        days_to_lockdown_change += 1

        young_healthy = [k for k, v in virus_dic[STA_K].items() if v == HEALTHY_V
                         and env_dic[IAD_K][k] == 1 and env_dic[IAG_K][k] <= age_cutoff]

        young_unlucky = np.random.choice(young_healthy,
                                         size=int(min(len(young_healthy), params[nindividual_key]/1000)),
                                         replace=False)
        virus_dic[STA_K].update((y, ISOLATED_V) for y in young_unlucky)

        if len(get_hospitalized_people(virus_dic)) == 0 and days_to_lockdown_change >= 14:
            days_to_lockdown_change = 0
            unlock_progress = min(1, unlock_progress + 0.2)

        if len(get_hospitalized_people(virus_dic)) >= available_beds and days_to_lockdown_change >= 14:
            days_to_lockdown_change = 0
            unlock_progress = max(0, unlock_progress - 0.2)

        update_run_stat(virus_dic, run_stats, day)
        # Override isolation to calculate
        run_stats["iso"][day] = len(young_unlucky)
        run_stats["loc"][day] = (1-unlock_progress)

    return run_id, run_stats
