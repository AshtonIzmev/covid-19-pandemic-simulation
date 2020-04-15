from initiator.core import build_individual_houses_map, build_house_individual_map, build_individual_work_map, \
    build_individual_adult_map, build_workplace_individual_map, build_individual_age_map, build_house_adult_map, \
    build_house_store_map, build_store_house_map, \
    build_geo_positions_house, build_geo_positions_store, build_geo_positions_workplace
from initiator.helper import get_r
from simulator.dynamic_helper import get_default_infection_parameters
from simulator.keys import *
from simulator.parameters import HEALTHY_V, INFECTED_V


def get_environment_simulation(number_of_individuals_arg, same_house_rate_arg, number_store_per_house_arg):
    all_ind_hou = build_individual_houses_map(number_of_individuals_arg, same_house_rate_arg)
    all_hou_ind = build_house_individual_map(all_ind_hou)
    all_ind_adu = build_individual_adult_map(all_ind_hou)
    all_ind_age = build_individual_age_map(all_ind_hou)

    all_ind_wor = build_individual_work_map(all_ind_adu)
    all_wor_ind = build_workplace_individual_map(all_ind_wor)
    all_hou_adu = build_house_adult_map(all_ind_hou, all_ind_adu)

    geo_hou = build_geo_positions_house(len(all_hou_ind))
    geo_wor = build_geo_positions_workplace(len(all_wor_ind))
    geo_sto = build_geo_positions_store(int(len(all_hou_ind) / number_store_per_house_arg))

    all_hou_sto = build_house_store_map(geo_sto, geo_hou)
    all_sto_hou = build_store_house_map(all_hou_sto)

    return {
        IH_K: all_ind_hou,
        HI_K: all_hou_ind,
        IAD_K: all_ind_adu,
        IAG_K: all_ind_age,
        IW_K: all_ind_wor,
        WI_K: all_wor_ind,
        HA_K: all_hou_adu,
        HS_K: all_hou_sto,
        SH_K: all_sto_hou
    }


# TIME_TO_DECISION  : time between infection and decision (immunity/death)
# TIME_TO_CONTAGION : time between infection and contagiosity
def get_virus_simulation_t0(number_of_individuals_arg, infection_initialization_rate_arg):
    inn_ind_cov = dict(zip(range(number_of_individuals_arg),
                           [int(get_r() <= infection_initialization_rate_arg) for i in range(number_of_individuals_arg)]))

    life_state = dict(zip(range(number_of_individuals_arg), [HEALTHY_V] * number_of_individuals_arg))

    time_to_decision = dict(zip(range(number_of_individuals_arg),
                                [get_default_infection_parameters()[0] for _ in range(number_of_individuals_arg)]))
    time_to_contagion = dict(zip(range(number_of_individuals_arg),
                                 [get_default_infection_parameters()[1] for _ in range(number_of_individuals_arg)]))

    infected_individual_init = [k for k, v in inn_ind_cov.items() if v == 1]

    for individual in infected_individual_init:
        life_state[individual] = INFECTED_V

    return {
        DEC_K: time_to_decision,
        CON_K: time_to_contagion,
        STA_K: life_state
    }
