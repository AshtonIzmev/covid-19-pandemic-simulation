import math
import numpy as np

from simulator.dynamic_helper import propagate_to_stores, propagate_to_houses, propagate_to_workplaces, \
    increment_pandemic_1_day, is_weekend, get_pandemic_statistics, propagate_to_transportation
from simulator.parameters import *
from simulator.plot_helper import print_progress_bar
from simulator.simulation_helper import get_environment_simulation, get_virus_simulation_t0
from scenario.scenario_helper import tighten_lockdown, soften_lockdown, measure_lockdown_strength


# This scenario is a lockdown loosening every DAYS_WAIT_FOR_LOCKDOWN_REMOVAL after the last new case
def launch_run():
    print('Preparing environment...')
    env_dic = get_environment_simulation(params)

    stats = np.zeros((params[nrun_key], params[nday_key], 7))
    loosening_day = np.zeros((params[nrun_key]))
    print_progress_bar(0, params[nrun_key] * params[nday_key], prefix='Progress:', suffix='Complete', length=50)
    for r in range(params[nrun_key]):

        params[store_preference_key] = 0.95
        params[remote_work_key] = 0.98
        params[house_infect_key] = 0.5
        params[work_infection_key] = 0.01
        params[store_infection_key] = 0.02
        params[transport_infection_key] = 0.01
        params[innoculation_number_key] = 5
        available_beds = params[icu_bed_per_thousand_individual_key] * params[nindividual_key] / 1000

        if len(params[additional_scenario_params_key]) < 1:
            raise AssertionError("Need an additional_scenario parameter")
        days_to_lockdown_loosening = params[additional_scenario_params_key][0]

        days_with_no_cases = 0

        first_day_lockdown_loosening = -1

        virus_dic = get_virus_simulation_t0(params)
        for i in range(params[nday_key]):
            print_progress_bar(r * params[nday_key] + i + 1, params[nrun_key] * params[nday_key],
                               prefix='Progress:', suffix='Complete', length=50)
            propagate_to_houses(env_dic, virus_dic, params[house_infect_key])
            if not is_weekend(i):
                propagate_to_transportation(env_dic, virus_dic, params[transport_infection_key], params[remote_work_key])
                propagate_to_workplaces(env_dic, virus_dic, params[work_infection_key], params[remote_work_key])
            if is_weekend(i):
                propagate_to_stores(env_dic, virus_dic, params[store_infection_key], params[store_preference_key])
            increment_pandemic_1_day(env_dic, virus_dic, available_beds)
            stats[r][i][0], stats[r][i][1], stats[r][i][2], stats[r][i][3], stats[r][i][4], stats[r][i][5] = \
                get_pandemic_statistics(virus_dic)
            stats[r][i][6] = measure_lockdown_strength(params)

            if stats[r][i][5] == 0:
                days_with_no_cases += 1
            else:
                days_with_no_cases = 0

            if (days_with_no_cases % days_to_lockdown_loosening == 0) and days_with_no_cases > 0:
                if first_day_lockdown_loosening == -1:
                    first_day_lockdown_loosening = i
                soften_lockdown(params)
        loosening_day[r] = first_day_lockdown_loosening

    loosening_day_ok = [l_v for l_v in loosening_day if l_v != -1]
    print("Lockdown removal occured %d times in average after %.2f days"
          % (len(loosening_day_ok), sum(loosening_day_ok)/len(loosening_day_ok)))
    return stats
