import random

import numpy as np
import ray
from ray.actor import ActorHandle

from scenario.helper.scenario import is_weekend, parse_bool, read_extra_params
from simulator.constants.keys import (
    HEALTHY_V,
    IAG_K,
    IMMUNE_V,
    STA_K,
    death_bounds_key,
    hospitalization_bounds_key,
    house_infect_key,
    icu_bed_per_thousand_individual_key,
    immunity_bounds_key,
    innoculation_number_key,
    nday_key,
    nindividual_key,
    nvariant_key,
    remote_work_key,
    store_infection_key,
    store_preference_key,
    transport_contact_cap_key,
    transport_infection_key,
    variant_hospitalization_k,
    variant_mortality_k,
    work_infection_key,
)
from simulator.helper.dynamic import (
    get_deadpeople,
    increment_pandemic_1_day,
    propagate_to_houses,
    propagate_to_stores,
    propagate_to_transportation,
    propagate_to_workplaces,
)
from simulator.helper.simulation import get_virus_simulation_t0

VARIANT_KINDS = ("C", "I", "M", "H", "MH", "HM")


def get_variant_factors(variant_kind, variant_iter, nb_variants, restrict_genetic_cost):
    """The four factors describing one variant along the studied axis.

    Contagiosity, mortality and hospitalisation sweep [0.25, 1.75] (+/- 75%) and
    immunisation escape sweeps [1, 3]; the untouched axes stay neutral at 1.

    The factors used to be initialised once outside the sweep and mutated in
    place, so under `restrict_genetic_cost` each iteration re-normalised the
    already-normalised values of the previous one and they decayed towards 0.
    """
    if variant_kind not in VARIANT_KINDS:
        raise ValueError(f"Unknown variant kind {variant_kind!r}, expected one of {list(VARIANT_KINDS)}")

    step = variant_iter / nb_variants
    contagiosity, immunization, mortality, hospital = 1.0, 1.0, 1.0, 1.0

    if variant_kind == "C":
        contagiosity = 0.25 + 1.5 * step
    elif variant_kind == "I":
        immunization = 1 + 2 * step
    elif variant_kind == "M":
        mortality = 0.25 + 1.5 * step
    elif variant_kind == "H":
        hospital = 0.25 + 1.5 * step
    else:  # "MH" / "HM" : deadlier but less hospitalising, and the other way round
        mortality = 0.25 + 1.5 * step
        hospital = 1.75 - 1.5 * step

    if restrict_genetic_cost:
        # A variant only has so much genome to spend: normalise so the four
        # advantages always sum to 1.
        total_cost = contagiosity + immunization + mortality + hospital
        contagiosity, immunization, mortality, hospital = (contagiosity / total_cost, immunization / total_cost,
                                                           mortality / total_cost, hospital / total_cost)

    return contagiosity, immunization, mortality, hospital


@ray.remote
def do_parallel_run(env_dic, params, run_id, specific_seed, pba: ActorHandle):

    random.seed(specific_seed)
    np.random.seed(specific_seed)

    rate_daily_vaccinated, variant_kind, restrict_genetic_cost = read_extra_params(
        params, float, str, parse_bool)
    if rate_daily_vaccinated < 0:
        # Morrocan daily rate of vaccination
        rate_daily_vaccinated = 0.00428

    params[store_preference_key] = 0.5
    params[remote_work_key] = 0.5
    params[innoculation_number_key] = 5
    available_beds = params[icu_bed_per_thousand_individual_key] * params[nindividual_key] / 1000

    death_stat = []

    for param_variant_iter in range(params[nvariant_key]):
        variant_contagiosity, variant_immunization, variant_mortality, variant_hospital = \
            get_variant_factors(variant_kind, param_variant_iter, params[nvariant_key], restrict_genetic_cost)

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
