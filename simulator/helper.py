import matplotlib.pyplot as plt
import numpy as np

from initiator.helper import flatten, get_random_choice_list
from initiator.helper import get_infection_parameters
from initiator.helper import get_r, get_mortalty_rate
from simulator.parameters import LOWER_CONTAGION_BOUND, LOWER_INFECTION_BOUND, \
    UPPER_CONTAGION_BOUND, UPPER_INFECTION_BOUND, HEALTHY_STATE, DEAD_STATE, IMMUNE_STATE
from simulator.parameters import PROB_INFECTION_AT_HOME, PROB_INFECTION_AT_WORK, PROB_INFECTION_AT_STORE


def get_default_infection_parameters():
    return get_infection_parameters(LOWER_INFECTION_BOUND, UPPER_INFECTION_BOUND,
                                    LOWER_CONTAGION_BOUND, UPPER_CONTAGION_BOUND)


def update_infection_period(who_is_infected, incubation_dic, contagion_dic):
    for i in who_is_infected:
        if incubation_dic[i] == HEALTHY_STATE:  # If has never been infected
            incubation, contagion = get_default_infection_parameters()
            incubation_dic[i] = incubation
            contagion_dic[i] = contagion


def increment_pandemic_1_day(incubation_dic, age_dic, contagion_dic):
    for i in get_infected_people(incubation_dic):
        contagion_dic[i] = contagion_dic[i] -1
        if incubation_dic[i] > DEAD_STATE + 1:
            incubation_dic[i] = incubation_dic[i] -1
        if incubation_dic[i] == DEAD_STATE + 1: # Decide over life
            if get_r() < get_mortalty_rate(age_dic[i]):
                incubation_dic[i] = 0
            else:
                incubation_dic[i] = -2  # Grant immunity


def get_infected_people(incubation_dic):
    return [k for k, v in incubation_dic.items() if v > DEAD_STATE]


def get_deadpeople(incubation_dic):
    return [k for k, v in incubation_dic.items() if v == DEAD_STATE]


def get_healthy_people(incubation_dic):
    return [k for k, v in incubation_dic.items() if v == HEALTHY_STATE]


def get_immune_people(incubation_dic):
    return [k for k, v in incubation_dic.items() if v == IMMUNE_STATE]


def is_contagious(ind, contagion_dic):
    return contagion_dic[ind] < 0


def propagate_to_houses(map_individuals_houses, map_houses_individuals, infection_state, contagion_state):
    # Houses that contain an infected and contagious person
    infected_houses = [map_individuals_houses[i] for i in get_infected_people(infection_state)
                       if is_contagious(i, contagion_state)]

    # People infected (not necessarily contagious) from a contagious person living in their house
    infected_athome = [i for i in flatten([map_houses_individuals[hou] for hou in infected_houses])
                       if get_r() < PROB_INFECTION_AT_HOME]

    # INFECTION STATE UPDATE
    update_infection_period(infected_athome, infection_state, contagion_state)


def propagate_to_workplaces(map_individual_workers, map_workplace_individual, infection_state, contagion_state):
    # Contagious people who will go to work
    infected_gotowork = [i for i in get_infected_people(infection_state) if i in map_individual_workers.keys()
                         and is_contagious(i, contagion_state)]
    # Infected workplaces
    infected_workplaces = [map_individual_workers[ind] for ind in infected_gotowork]
    infected_backfromwork = [i for i in flatten([map_workplace_individual[k] for k in infected_workplaces])
                             if get_r() < PROB_INFECTION_AT_WORK]

    # INFECTION STATE UPDATE
    update_infection_period(infected_backfromwork, infection_state, contagion_state)


def propagate_to_stores(map_individuals_houses, map_houses_stores, map_stores_houses, map_houses_adults,
                        infection_state, contagion_state):
    # Filter on living people because we have a random choice to make in each house
    # People who will go to their store (one person per house as imposed by lockdown)
    individuals_gotostore = get_random_choice_list([[i for i in map_houses_adults[h] if infection_state[i] != DEAD_STATE]
                                                    for h in range(len(map_houses_adults))])

    # Contagious people who will go to their store
    individuals_infected_gotostore = [i for i in individuals_gotostore if is_contagious(i, contagion_state)]

    # Stores that will be visited by a contagious person
    infected_stores = [map_houses_stores[map_individuals_houses[i]] for i in individuals_infected_gotostore]

    # People who live in a house that goes to a contagious store
    individuals_attachedto_infected_store = flatten(flatten(
        [[map_houses_adults[h] for h in map_stores_houses[s]] for s in infected_stores]))

    # People who did go to that contagious store
    individuals_goto_infected_store = list(set(individuals_attachedto_infected_store)
                                           .intersection(set(individuals_gotostore)))

    # People who got infected from going to their store
    infected_backfromstore = [i for i in individuals_goto_infected_store if get_r() < PROB_INFECTION_AT_STORE]

    # INFECTION STATE UPDATE
    update_infection_period(infected_backfromstore, infection_state, contagion_state)


def draw_population_state_daily(stats_arg, n_days_arg, n_individuals_arg):
    fig, ax = plt.subplots(figsize=(15, 10))

    healthy_serie = [stats_arg[i][0] for i in range(n_days_arg)]
    infected_serie = [stats_arg[i][1] for i in range(n_days_arg)]
    dead_serie = [stats_arg[i][2] for i in range(n_days_arg)]
    dead_serie_stacked = [stats_arg[i][0] + stats_arg[i][1] for i in range(n_days_arg)]
    immune_serie = [stats_arg[i][3] for i in range(n_days_arg)]
    immune_serie_stacked = [stats_arg[i][0] + stats_arg[i][1] + stats_arg[i][2] for i in range(n_days_arg)]

    indices = np.arange(n_days_arg)
    width = 0.6

    p1 = plt.bar(indices, healthy_serie, width, color="#3F88C5")
    p2 = plt.bar(indices, infected_serie, width, bottom=healthy_serie, color="#A63D40")
    p3 = plt.bar(indices, dead_serie, width, bottom=dead_serie_stacked, color="#151515")
    p4 = plt.bar(indices, immune_serie, width, bottom=immune_serie_stacked, color="#90A959")

    plt.ylabel('Population')
    plt.title('Pandemic evolution')
    plt.xticks(np.arange(0, n_days_arg, int(n_days_arg/10)), tuple([('Day ' + str(10*i))
                                                                    for i in range(int(n_days_arg/10))]))
    plt.yticks(np.arange(0, n_individuals_arg, n_individuals_arg/25))
    plt.legend((p1[0], p2[0], p3[0], p4[0]), ('Healthy', 'Infected', 'Dead', 'Immune'))

    plt.show()


def draw_new_daily_cases(stats_arg, n_days_arg):
    fig, ax = plt.subplots(figsize=(15, 10))

    healthy_serie = [stats_arg[i][0] for i in range(n_days_arg)]
    new_cases_serie = list([j-i for (i,j) in zip(healthy_serie[1:], healthy_serie[:-1] )])

    indices = np.arange(n_days_arg-1)
    width = 0.6

    p1 = plt.bar(indices, new_cases_serie, width, color="#44A1A0")

    plt.ylabel('Population')
    plt.title('New infected cases evolution')
    plt.xticks(np.arange(0, n_days_arg-1, int(n_days_arg/10)), tuple([('Day ' + str(10*i))
                                                                      for i in range(int(n_days_arg/10))]))
    plt.yticks(np.arange(0, int(max(new_cases_serie)*1.1), 5))
    plt.legend((p1[0],), ('New cases',))
    plt.show()

