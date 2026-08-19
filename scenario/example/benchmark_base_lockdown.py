import time

import numpy as np

from scenario.helper.scenario import get_zero_stats, measure_lockdown_strength
from simulator.constants.keys import (
    house_infect_key,
    icu_bed_per_thousand_individual_key,
    innoculation_number_key,
    nday_key,
    nindividual_key,
    nrun_key,
    remote_work_key,
    store_infection_key,
    store_preference_key,
    transport_contact_cap_key,
    transport_infection_key,
    work_infection_key,
)
from simulator.helper.dynamic import (
    increment_pandemic_1_day,
    propagate_to_houses,
    propagate_to_stores,
    propagate_to_transportation,
    propagate_to_workplaces,
    update_stats,
)
from simulator.helper.simulation import get_virus_simulation_t0

STEP_NAMES = ("houses", "transport", "workplaces", "stores", "day")


# This scenario is the basic one with a classic dynamic.
# `profile` prints the cumulated wall time of each propagation step.
def launch_run(params, env_dic, profile=False):
    prof_stats = np.zeros(len(STEP_NAMES))
    prof_nstats = np.zeros(len(STEP_NAMES))
    stats = get_zero_stats(params)
    for r in range(params[nrun_key]):

        params[store_preference_key] = 0.95
        params[remote_work_key] = 0.98
        params[innoculation_number_key] = 5
        available_beds = params[icu_bed_per_thousand_individual_key] * params[nindividual_key] / 1000

        virus_dic = get_virus_simulation_t0(params)
        for day in range(params[nday_key]):
            time_init = time.time()
            propagate_to_houses(env_dic, virus_dic, params[house_infect_key])
            prof_stats[0] += time.time() - time_init
            prof_nstats[0] += 1
            time_init = time.time()
            propagate_to_transportation(env_dic, virus_dic, params[transport_infection_key],
                                        params[remote_work_key], params[transport_contact_cap_key])
            prof_stats[1] += time.time() - time_init
            prof_nstats[1] += 1
            time_init = time.time()
            propagate_to_workplaces(env_dic, virus_dic, params[work_infection_key], params[remote_work_key])
            prof_stats[2] += time.time() - time_init
            prof_nstats[2] += 1
            time_init = time.time()
            propagate_to_stores(env_dic, virus_dic, params[store_infection_key], params[store_preference_key])
            prof_stats[3] += time.time() - time_init
            prof_nstats[3] += 1
            time_init = time.time()
            increment_pandemic_1_day(env_dic, virus_dic, available_beds)
            prof_stats[4] += time.time() - time_init
            prof_nstats[4] += 1

            update_stats(virus_dic, stats, r, day)
            stats["loc"][r][day] = measure_lockdown_strength(params)

    if profile:
        for name, total, count in zip(STEP_NAMES, prof_stats, prof_nstats):
            print(f"{name:<10} {total:7.3f}s over {int(count)} calls")
    return stats
