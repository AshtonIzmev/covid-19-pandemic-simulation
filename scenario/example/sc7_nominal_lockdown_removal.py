import ray

from scenario.helper.scenario import get_zero_run_stats, is_weekend
from simulator.constants.keys import nindividual_key, nday_key, innoculation_number_key, remote_work_key, \
    store_preference_key, house_infect_key, work_infection_key, store_infection_key, transport_infection_key, \
    transport_contact_cap_key, icu_bed_per_thousand_individual_key, NC_K
from simulator.helper.dynamic import propagate_to_stores, propagate_to_houses, propagate_to_workplaces, \
    increment_pandemic_1_day, update_run_stat, propagate_to_transportation
from simulator.helper.simulation import get_virus_simulation_t0


@ray.remote
def do_parallel_run(env_dic, params, run_id):
    run_stats = get_zero_run_stats(params)

    params[innoculation_number_key] = 5

    days_with_no_cases = 0
    days_to_lockdown_change = 0
    days_to_lockdown_loosening = 14
    lock_init = 0

    pcn = (0.98, 0.5, 0.01, 0.01, 0.02, 0.95)
    #pcn = (0.78, 0.5, 0.05, 0.05, 0.1, 0.55)
    pvn = (0.58, 0.5, 0.05, 0.05, 0.1, 0.30)

    params[remote_work_key] = pcn[0] * lock_init + (pvn[0] - pcn[0]) * lock_init
    params[house_infect_key] = pcn[1] * lock_init + (pvn[1] - pcn[1]) * lock_init
    params[transport_infection_key] = pcn[2] * lock_init + (pvn[2] - pcn[2]) * lock_init
    params[work_infection_key] = pcn[3] * lock_init + (pvn[3] - pcn[3]) * lock_init
    params[store_infection_key] = pcn[4] * lock_init + (pvn[4] - pcn[4]) * lock_init
    params[store_preference_key] = pcn[5] * lock_init + (pvn[5] - pcn[5]) * lock_init

    params[innoculation_number_key] = 5
    available_beds = params[icu_bed_per_thousand_individual_key] * params[nindividual_key] / 1000

    virus_dic = get_virus_simulation_t0(params)

    for day in range(params[nday_key]):

        params[remote_work_key] = pcn[0] * lock_init + (pvn[0] - pcn[0]) * lock_init
        params[house_infect_key] = pcn[1] * lock_init + (pvn[1] - pcn[1]) * lock_init
        params[transport_infection_key] = pcn[2] * lock_init + (pvn[2] - pcn[2]) * lock_init
        params[work_infection_key] = pcn[3] * lock_init + (pvn[3] - pcn[3]) * lock_init
        params[store_infection_key] = pcn[4] * lock_init + (pvn[4] - pcn[4]) * lock_init
        params[store_preference_key] = pcn[5] * lock_init + (pvn[5] - pcn[5]) * lock_init

        propagate_to_houses(env_dic, virus_dic, params[house_infect_key])
        if not is_weekend(day):
            propagate_to_transportation(env_dic, virus_dic, params[transport_infection_key],
                                        params[remote_work_key], params[transport_contact_cap_key])
            propagate_to_workplaces(env_dic, virus_dic, params[work_infection_key], params[remote_work_key])
        if is_weekend(day):
            propagate_to_stores(env_dic, virus_dic, params[store_infection_key], params[store_preference_key])
        increment_pandemic_1_day(env_dic, virus_dic, available_beds)

        days_to_lockdown_change += 1

        if virus_dic[NC_K] == 0:
            days_with_no_cases += 1
        else:
            days_with_no_cases = 0

        if days_with_no_cases >= days_to_lockdown_loosening and days_to_lockdown_change >= 14:
            days_with_no_cases = 0
            days_to_lockdown_change = 0
            lock_init = min(1, lock_init+0.2)

        if virus_dic[NC_K] >= available_beds and days_to_lockdown_change >= 14:
            days_to_lockdown_change = 0
            lock_init = max(0, lock_init-0.2)

        update_run_stat(virus_dic, run_stats, day)
        run_stats["loc"][day] = (1-lock_init)  # measure_lockdown_strength(params)

    return run_id, run_stats
