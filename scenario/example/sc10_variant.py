import random

import numpy as np
import ray

from scenario.helper.scenario import get_zero_run_stats, is_weekend
from simulator.constants.keys import *
from simulator.helper.dynamic import propagate_to_stores, propagate_to_houses, propagate_to_workplaces, \
    increment_pandemic_1_day, update_run_stat, propagate_to_transportation, get_deadpeople
from simulator.helper.simulation import get_virus_simulation_t0
from ray.actor import ActorHandle


@ray.remote
def do_parallel_run(env_dic, params, run_id, specific_seed, pba: ActorHandle):

    random.seed(specific_seed)
    np.random.seed(specific_seed)

    if len(params[additional_scenario_params_key]) < 3:
        raise AssertionError("Need more additional_scenario parameter")
    else:
        assert(params[additional_scenario_params_key][2] in ["False", "True"])
        rate_daily_vaccinated = int(params[additional_scenario_params_key][0])
        variant_kind = params[additional_scenario_params_key][1]
        restrict_genetic_cost = params[additional_scenario_params_key][2] == "True"

    if rate_daily_vaccinated < 0:
        # Morrocan daily rate of vaccination
        rate_daily_vaccinated = 0.00428

    params[store_preference_key] = 0.5
    params[remote_work_key] = 0.5
    params[innoculation_number_key] = 5
    available_beds = params[icu_bed_per_thousand_individual_key] * params[nindividual_key] / 1000

    # Variant parameters
    variant_contagiosity = 1
    variant_immunization = 1
    variant_mortality = 1  # tradeoff parameter
    variant_hospital = 1  # tradeoff parameter

    death_stat = []

    for param_variant_iter in range(params[nvariant_key]):
        # Update parameters
        # Range [0.25, 1.75] with a 1/param step (+/- 75%)
        if variant_kind == "C":
            variant_contagiosity = 0.25 + 1.5 * param_variant_iter / params[nvariant_key]
        if variant_kind == "I":
            variant_immunization = 1 + 2 * param_variant_iter / params[nvariant_key]
        if variant_kind == "M":
            variant_mortality = 0.25 + 1.5 * param_variant_iter / params[nvariant_key]
        if variant_kind == "H":
            variant_hospital = 0.25 + 1.5 * param_variant_iter / params[nvariant_key]
        if variant_kind == "MH" or variant_kind == "HM":
            variant_mortality = 0.25 + 1.5 * param_variant_iter / params[nvariant_key]
            variant_hospital = 1.75 - 1.5 * param_variant_iter / params[nvariant_key]

        if restrict_genetic_cost:
            variant_total_cost = variant_contagiosity + variant_immunization + variant_mortality + variant_hospital
            variant_contagiosity /= variant_total_cost
            variant_immunization /= variant_total_cost
            variant_mortality /= variant_total_cost
            variant_hospital /= variant_total_cost

        params[house_infect_key] = 0.5 * variant_contagiosity
        params[work_infection_key] = 0.05 * variant_contagiosity
        params[store_infection_key] = 0.02 * variant_contagiosity
        params[transport_infection_key] = 0.01 * variant_contagiosity

        params[variant_mortality_k] = variant_mortality
        params[death_bounds_key] = (8 / variant_mortality, 31 / variant_mortality)

        params[variant_hospitalization_k] = variant_hospital
        params[hospitalization_bounds_key] = (8 / variant_hospital, 16 / variant_hospital)

        # assuming about a year of immunity (~flu)
        params[immunity_bounds_key] = (int(270/variant_immunization), int(450/variant_immunization))
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

        death_stat.append(len(get_deadpeople(virus_dic)))
    return run_id, {"dea": np.array(death_stat)}
