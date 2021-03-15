import random

import numpy as np
import ray

from scenario.helper.scenario import measure_lockdown_strength, get_zero_run_stats, is_weekend
from simulator.constants.keys import IBE_K, HB_K, HI_K, nindividual_key, nday_key, innoculation_number_key, \
    nb_1d_block_key, remote_work_key, store_preference_key, house_infect_key, work_infection_key, store_infection_key, \
    transport_infection_key, transport_contact_cap_key, icu_bed_per_thousand_individual_key, \
    additional_scenario_params_key
from simulator.helper.dynamic import propagate_to_stores, propagate_to_houses, propagate_to_workplaces, \
    increment_pandemic_1_day, update_run_stat, propagate_to_transportation
from simulator.helper.simulation import get_virus_simulation_t0
from ray.actor import ActorHandle


@ray.remote
# This scenario is the basic one with a classic dynamic
def do_parallel_run(env_dic, params, run_id, specific_seed, pba: ActorHandle):
    pba.update.remote(1)
    run_stats = get_zero_run_stats(params)
    random.seed(specific_seed)
    np.random.seed(specific_seed)

    if len(params[additional_scenario_params_key]) < 2:
        raise AssertionError("Need more additional_scenario parameter")

    nb_bloc = int(params[additional_scenario_params_key][0])
    rogue_factor = float(params[additional_scenario_params_key][1])

    rogues_blocks_x = np.random.choice(range(params[nb_1d_block_key]), nb_bloc)
    rogues_blocks_y = np.random.choice(range(params[nb_1d_block_key]), nb_bloc)
    affected_people = 0
    for b in range(nb_bloc):
        houses = [h for h, v in enumerate(env_dic[HB_K]) if v[0] == rogues_blocks_x[b]
                  and v[1] == rogues_blocks_y[b]]
        for h in houses:
            for i in env_dic[HI_K][h]:
                affected_people += 1
                env_dic[IBE_K][i] *= rogue_factor

    params[store_preference_key] = 0.95
    params[remote_work_key] = 0.98
    params[house_infect_key] = 0.5
    params[work_infection_key] = 0.01
    params[store_infection_key] = 0.001
    params[transport_infection_key] = 0.01
    params[innoculation_number_key] = 50
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
