from scenario.scenario_helper import measure_lockdown_strength, get_zero_stats
from simulator.dynamic_helper import propagate_to_stores, propagate_to_houses, propagate_to_workplaces, \
    increment_pandemic_1_day, is_weekend, propagate_to_transportation, update_stats
from simulator.parameters import *
from simulator.plot_helper import print_progress_bar
from simulator.simulation_helper import get_environment_simulation, get_virus_simulation_t0


# This scenario is the "just a flu"
def launch_run():
    print('Preparing environment...')
    env_dic = get_environment_simulation(params)

    stats = get_zero_stats()
    print_progress_bar(0, params[nrun_key] * params[nday_key], prefix='Progress:', suffix='Complete', length=50)
    for r in range(params[nrun_key]):

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
            print_progress_bar(r * params[nday_key] + day + 1, params[nrun_key] * params[nday_key],
                               prefix='Progress:', suffix='Complete', length=50)
            propagate_to_houses(env_dic, virus_dic, params[house_infect_key])
            if not is_weekend(day):
                propagate_to_transportation(env_dic, virus_dic, params[transport_infection_key],
                                            params[remote_work_key], params[transport_contact_cap_key])
                propagate_to_workplaces(env_dic, virus_dic, params[work_infection_key], params[remote_work_key])
            if is_weekend(day):
                propagate_to_stores(env_dic, virus_dic, params[store_infection_key], params[store_preference_key])
            increment_pandemic_1_day(env_dic, virus_dic, available_beds)

            update_stats(virus_dic, stats, r, day)
            stats["loc"][r][day] = measure_lockdown_strength(params)

    return stats