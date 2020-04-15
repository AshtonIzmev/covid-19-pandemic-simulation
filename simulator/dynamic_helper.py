from initiator.helper import flatten, get_random_choice_list
from initiator.helper import get_infection_parameters
from initiator.helper import get_r, get_mortalty_rate
from simulator.keys import *


# Assuming 0 is Monday
def is_weekend(i):
    return ((i - 5) % 7 == 0) or ((i - 6) % 7 == 0)


def update_infection_period(newly_infected_individuals_arg, virus_dic):
    for i in newly_infected_individuals_arg:
        if virus_dic[STA_K][i] == HEALTHY_V:
            virus_dic[STA_K][i] = INFECTED_V


def increment_pandemic_1_day(env_dic, virus_dic):
    for i in get_infected_people(virus_dic):
        # Contagion and decision periods are decremented
        virus_dic[CON_K][i] = virus_dic[CON_K][i] - 1
        virus_dic[DEC_K][i] = virus_dic[DEC_K][i] - 1
        # Decide over life
        if virus_dic[DEC_K][i] == 0:
            if get_r() < get_mortalty_rate(env_dic[IAG_K][i]):
                virus_dic[STA_K][i] = DEAD_V
            else:
                virus_dic[STA_K][i] = IMMUNE_V


def get_infected_people(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == INFECTED_V]


def get_deadpeople(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == DEAD_V]


def get_healthy_people(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == HEALTHY_V]


def get_immune_people(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == IMMUNE_V]


def get_pandemic_statistics(virus_dic):
    return (len(get_healthy_people(virus_dic)), len(get_infected_people(virus_dic)),
            len(get_deadpeople(virus_dic)), len(get_immune_people(virus_dic)))


def is_contagious(individual_arg, virus_dic):
    return virus_dic[STA_K][individual_arg] == INFECTED_V and virus_dic[CON_K][individual_arg] < 0


def is_alive(individual_arg, virus_dic):
    return virus_dic[STA_K][individual_arg] != DEAD_V


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
    individuals_gotostore = get_random_choice_list([[i for i in env_dic[HA_K][h] if is_alive(i, virus_dic)]
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

