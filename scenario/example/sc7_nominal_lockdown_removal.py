import random

import numpy as np
import ray
from ray.actor import ActorHandle

from scenario.helper.scenario import (
    apply_unlock_progress,
    get_zero_run_stats,
    is_weekend,
    parse_bool,
    read_extra_params,
)
from simulator.constants.keys import (
    house_infect_key,
    icu_bed_per_thousand_individual_key,
    innoculation_number_key,
    nday_key,
    nindividual_key,
    remote_work_key,
    store_infection_key,
    store_preference_key,
    transport_contact_cap_key,
    transport_infection_key,
    work_infection_key,
)
from simulator.helper.dynamic import (
    get_hospitalized_people,
    increment_pandemic_1_day,
    propagate_to_houses,
    propagate_to_stores,
    propagate_to_transportation,
    propagate_to_workplaces,
    update_run_stat,
)
from simulator.helper.simulation import get_virus_simulation_t0


@ray.remote
def do_parallel_run(env_dic, params, run_id, specific_seed, pba: ActorHandle):
    run_stats = get_zero_run_stats(params)
    random.seed(specific_seed)
    np.random.seed(specific_seed)

    (relock_activated,) = read_extra_params(params, parse_bool)

    params[innoculation_number_key] = 5

    days_to_lockdown_change = 0
    unlock_progress = 0

    available_beds = params[icu_bed_per_thousand_individual_key] * params[nindividual_key] / 1000

    virus_dic = get_virus_simulation_t0(params)

    for day in range(params[nday_key]):
        pba.update.remote(1)
        apply_unlock_progress(params, unlock_progress)

        propagate_to_houses(env_dic, virus_dic, params[house_infect_key])
        if not is_weekend(day):
            propagate_to_transportation(env_dic, virus_dic, params[transport_infection_key],
                                        params[remote_work_key], params[transport_contact_cap_key])
            propagate_to_workplaces(env_dic, virus_dic, params[work_infection_key], params[remote_work_key])
        if is_weekend(day):
            propagate_to_stores(env_dic, virus_dic, params[store_infection_key], params[store_preference_key])
        increment_pandemic_1_day(env_dic, virus_dic, available_beds)

        days_to_lockdown_change += 1

        if len(get_hospitalized_people(virus_dic)) == 0 and days_to_lockdown_change >= 14:
            days_to_lockdown_change = 0
            unlock_progress = min(1, unlock_progress + 0.2)

        if relock_activated and len(get_hospitalized_people(virus_dic)) >= available_beds \
                and days_to_lockdown_change >= 14:
            days_to_lockdown_change = 0
            unlock_progress = max(0, unlock_progress - 0.2)

        update_run_stat(virus_dic, run_stats, day)
        run_stats["loc"][day] = 1 - unlock_progress

    return run_id, run_stats
