from initiator.core import build_individual_houses_map, build_house_individual_map, build_individual_work_map, \
    build_individual_adult_map, build_workplace_individual_map, build_individual_age_map, build_house_adult_map, \
    build_house_store_map, build_store_house_map, \
    build_geo_positions_house, build_geo_positions_store, build_geo_positions_workplace, build_block_assignment, \
    build_individual_workblock_map, build_workblock_individual_map, build_individual_individual_transport_map, \
    build_1d_item_behavior, build_2d_item_behavior
from initiator.helper import get_r, get_infection_parameters
from simulator.keys import *
from simulator.parameters import *


def get_environment_simulation(params_arg):
    number_of_individuals_arg = params_arg[nindividual_key]
    number_store_per_house_arg = params_arg[store_per_house_key]
    preference_store_arg = params_arg[store_preference_key]
    nb_1d_block_arg = params_arg[nb_1d_block_key]
    probability_remote_work_arg = params_arg[remote_work_key]

    indiv_house = build_individual_houses_map(number_of_individuals_arg)
    house_indiv = build_house_individual_map(indiv_house)
    indiv_adult = build_individual_adult_map(indiv_house)
    indiv_age = build_individual_age_map(indiv_house)

    indiv_workplace = build_individual_work_map(indiv_adult, probability_remote_work_arg)
    workplace_indiv = build_workplace_individual_map(indiv_workplace)
    house_adult = build_house_adult_map(indiv_house, indiv_adult)

    geo_house = build_geo_positions_house(len(house_indiv))
    geo_workplace = build_geo_positions_workplace(len(workplace_indiv))
    geo_store = build_geo_positions_store(int(len(house_indiv) / number_store_per_house_arg))

    house_store = build_house_store_map(geo_store, geo_house, preference_store_arg)
    store_house = build_store_house_map(house_store)

    house_block = build_block_assignment(geo_house, nb_1d_block_arg)
    workplace_block = build_block_assignment(geo_workplace, nb_1d_block_arg)

    indiv_behavior = build_1d_item_behavior(number_of_individuals_arg)
    block_behavior = build_2d_item_behavior(nb_1d_block_arg)

    indiv_transport_block = build_individual_workblock_map(indiv_house, indiv_workplace, house_block, workplace_block)
    transport_block_indiv = build_workblock_individual_map(indiv_transport_block)

    indiv_transport_indiv = build_individual_individual_transport_map(indiv_transport_block, transport_block_indiv)

    a = 1
    return {
        IH_K: indiv_house,
        HI_K: house_indiv,
        IAD_K: indiv_adult,
        IAG_K: indiv_age,
        IW_K: indiv_workplace,
        WI_K: workplace_indiv,
        HA_K: house_adult,
        HS_K: house_store,
        SH_K: store_house,
        ITI_K: indiv_transport_indiv,
        BBE_K: block_behavior,
        IBE_K: indiv_behavior
    }


def get_virus_simulation_t0(params_arg):
    number_of_individuals_arg = params_arg[nindividual_key]
    infection_initialization_number_arg = params_arg[innoculation_number_key]
    contagion_bound_args = params_arg[contagion_bounds_key]
    hospitalization_args = params_arg[hospitalization_bounds_key]
    death_bound_args = params_arg[death_bounds_key]
    immunity_bound_args = params_arg[immunity_bounds_key]

    inn_ind_cov = dict(zip(range(number_of_individuals_arg),
                           [int(get_r() <= infection_initialization_number_arg / number_of_individuals_arg)
                            for i in range(number_of_individuals_arg)]))

    life_state = dict(zip(range(number_of_individuals_arg), [HEALTHY_V] * number_of_individuals_arg))

    def get_infection_params():
        return get_infection_parameters(contagion_bound_args[0], contagion_bound_args[1],
                                        hospitalization_args[0], hospitalization_args[1],
                                        death_bound_args[0], death_bound_args[1],
                                        immunity_bound_args[0], immunity_bound_args[1])

    time_to_contagion = dict(zip(range(number_of_individuals_arg),
                                 [get_infection_params()[0] for _ in range(number_of_individuals_arg)]))
    time_to_hospital = dict(zip(range(number_of_individuals_arg),
                                [get_infection_params()[1] for _ in range(number_of_individuals_arg)]))
    time_to_death = dict(zip(range(number_of_individuals_arg),
                             [get_infection_params()[2] for _ in range(number_of_individuals_arg)]))
    time_to_end_immunity = dict(zip(range(number_of_individuals_arg),
                                    [get_infection_params()[3] for _ in range(number_of_individuals_arg)]))

    infected_individual_init = [k for k, v in inn_ind_cov.items() if v == 1]

    for individual in infected_individual_init:
        life_state[individual] = INFECTED_V

    return {
        CON_K: time_to_contagion,
        HOS_K: time_to_hospital,
        DEA_K: time_to_death,
        IMM_K: time_to_end_immunity,
        STA_K: life_state,
        FN_K: get_infection_params,
        NC_K: 0
    }
