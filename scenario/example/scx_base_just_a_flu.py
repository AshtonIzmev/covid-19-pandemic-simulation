import random

import numpy as np
import ray

from scenario.helper.scenario import measure_lockdown_strength, is_weekend, get_zero_run_stats
from simulator.constants.keys import nindividual_key, nday_key, innoculation_number_key, remote_work_key, \
    store_preference_key, house_infect_key, work_infection_key, store_infection_key, transport_infection_key, \
    transport_contact_cap_key, icu_bed_per_thousand_individual_key
from simulator.helper.dynamic import propagate_to_stores, propagate_to_houses, propagate_to_workplaces, \
    increment_pandemic_1_day, propagate_to_transportation, update_run_stat
from simulator.helper.simulation import get_virus_simulation_t0
from ray.actor import ActorHandle


@ray.remote
def do_parallel_run(env_dic, params, run_id, specific_seed, pba: ActorHandle):
    run_stats = get_zero_run_stats(params)
    random.seed(specific_seed)
    np.random.seed(specific_seed)

    params[store_preference_key] = 0.3
    params[remote_work_key] = 0.58
    params[house_infect_key] = 0.5
    params[work_infection_key] = 0.1
    params[store_infection_key] = 0.2
    params[transport_infection_key] = 0.1
    params[innoculation_number_key] = 5
    available_beds = params[icu_bed_per_thousand_individual_key] * params[nindividual_key] / 1000

    virus_dic = get_virus_simulation_t0(params)
    for day in range(params[nday_key]):
        pba.update.remote(1)
        propagate_to_houses(env_dic, virus_dic, params[house_infect_key])
        if not is_weekend(day):
            propagate_to_transportation(env_dic, virus_dic, params[transport_infection_key],
                                        params[remote_work_key], params[transport_contact_cap_key])
            propagate_to_workplaces(env_dic, virus_dic, params[work_infection_key], params[remote_work_key])
        if is_weekend(day):
            propagate_to_stores(env_dic, virus_dic, params[store_infection_key], params[store_preference_key])
        increment_pandemic_1_day(env_dic, virus_dic, available_beds)
        update_run_stat(virus_dic, run_stats, day)
        run_stats["loc"][day] = measure_lockdown_strength(params)
    return run_id, run_stats

