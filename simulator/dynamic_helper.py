from initiator.helper import flatten, get_random_choice_list
from initiator.helper import get_infection_parameters
from initiator.helper import get_r, get_mortalty_rate
from simulator.keys import *
from simulator.parameters import LOWER_CONTAGION_BOUND, LOWER_INFECTION_BOUND, \
    UPPER_CONTAGION_BOUND, UPPER_INFECTION_BOUND, HEALTHY_STATE, DEAD_STATE, IMMUNE_STATE


def get_default_infection_parameters():
    return get_infection_parameters(LOWER_INFECTION_BOUND, UPPER_INFECTION_BOUND,
                                    LOWER_CONTAGION_BOUND, UPPER_CONTAGION_BOUND)


def update_infection_period(who_is_infected, virus_dic):
    for i in who_is_infected:
        if virus_dic[IINC_K][i] == HEALTHY_STATE:  # If has never been infected
            incubation, contagion = get_default_infection_parameters()
            virus_dic[IINC_K][i] = incubation
            virus_dic[ICON_K][i] = contagion


def increment_pandemic_1_day(env_dic, virus_dic):
    for i in get_infected_people(virus_dic):
        virus_dic[ICON_K][i] = virus_dic[ICON_K][i] - 1
        if virus_dic[IINC_K][i] > DEAD_STATE + 1:
            virus_dic[IINC_K][i] = virus_dic[IINC_K][i] - 1
        elif virus_dic[IINC_K][i] == DEAD_STATE + 1:  # Decide over life
            if get_r() < get_mortalty_rate(env_dic[IAG_K][i]):
                virus_dic[IINC_K][i] = 0
            else:
                virus_dic[IINC_K][i] = -2  # Grant immunity


def get_infected_people(virus_dic):
    return [k for k, v in virus_dic[IINC_K].items() if v > DEAD_STATE]


def get_deadpeople(virus_dic):
    return [k for k, v in virus_dic[IINC_K].items() if v == DEAD_STATE]


def get_healthy_people(virus_dic):
    return [k for k, v in virus_dic[IINC_K].items() if v == HEALTHY_STATE]


def get_immune_people(virus_dic):
    return [k for k, v in virus_dic[IINC_K].items() if v == IMMUNE_STATE]


def get_pandemic_statistics(virus_dic):
    return (len(get_healthy_people(virus_dic)), len(get_infected_people(virus_dic)),
            len(get_deadpeople(virus_dic)), len(get_immune_people(virus_dic)))


def is_contagious(individual_arg, virus_dic):
    return virus_dic[ICON_K][individual_arg] < 0


def propagate_to_houses(env_dic, virus_dic, probability_home_infection_arg):
    # Houses that contain an infected and contagious person
    infected_houses = [env_dic[IH_K][i] for i in get_infected_people(virus_dic)
                       if is_contagious(i, virus_dic)]

    # People infected (not necessarily contagious) from a contagious person living in their house
    infected_athome = [i for i in flatten([env_dic[HI_K][hou] for hou in infected_houses])
                       if get_r() < probability_home_infection_arg]

    # INFECTION STATE UPDATE
    update_infection_period(infected_athome, virus_dic)


def propagate_to_workplaces(env_dic, virus_dic, probability_work_infection_arg):
    # Contagious people who will go to work
    infected_gotowork = [i for i in get_infected_people(virus_dic) if i in env_dic[IW_K].keys()
                         and is_contagious(i, virus_dic)]
    # Infected workplaces
    infected_workplaces = [env_dic[IW_K][ind] for ind in infected_gotowork]
    infected_backfromwork = [i for i in flatten([env_dic[WI_K][k] for k in infected_workplaces])
                             if get_r() < probability_work_infection_arg]

    # INFECTION STATE UPDATE
    update_infection_period(infected_backfromwork, virus_dic)


def propagate_to_stores(env_dic, virus_dic, probability_store_infection_arg):
    # Filter on living people because we have a random choice to make in each house
    # People who will go to their store (one person per house as imposed by lockdown)
    individuals_gotostore = get_random_choice_list([[i for i in env_dic[HA_K][h] if virus_dic[IINC_K][i] != DEAD_STATE]
                                                    for h in range(len(env_dic[HA_K]))])

    # Contagious people who will go to their store
    individuals_infected_gotostore = [i for i in individuals_gotostore if is_contagious(i, virus_dic)]

    # Stores that will be visited by a contagious person
    infected_stores = [env_dic[HS_K][env_dic[IH_K][i]] for i in individuals_infected_gotostore]

    # People who live in a house that goes to a contagious store
    individuals_attachedto_infected_store = flatten(flatten(
        [[env_dic[HA_K][h] for h in env_dic[SH_K][s]] for s in infected_stores]))

    # People who did go to that contagious store
    individuals_goto_infected_store = list(set(individuals_attachedto_infected_store)
                                           .intersection(set(individuals_gotostore)))

    # People who got infected from going to their store
    infected_backfromstore = [i for i in individuals_goto_infected_store if get_r() < probability_store_infection_arg]

    # INFECTION STATE UPDATE
    update_infection_period(infected_backfromstore, virus_dic)

