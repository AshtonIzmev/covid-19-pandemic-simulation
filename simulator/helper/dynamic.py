from simulator.constants.keys import *
from simulator.constants.parameters import covid_mortality_rate, covid_hospitalization_rate
from simulator.helper.utils import get_random_sample, get_r, reduce_multiply_by_key, choose_weight_order, \
    get_random_choice_list


# Assuming 0 is Monday
def is_weekend(i):
    return ((i - 5) % 7 == 0) or ((i - 6) % 7 == 0)


def update_infection_period(newly_infected_individuals_arg, virus_dic):
    for i in newly_infected_individuals_arg:
        if virus_dic[STA_K][i] == HEALTHY_V:
            virus_dic[STA_K][i] = INFECTED_V
            virus_dic[NC_K] = virus_dic[NC_K] + 1


def update_immunity_state(virus_dic, i):
    # Losing immunity
    virus_dic[IMM_K][i] = virus_dic[IMM_K][i] - 1
    if virus_dic[IMM_K][i] == 0:
        virus_dic[STA_K][i] = HEALTHY_V
        # I am not proud of this hack, otherwise it meant changing too many APIs
        con, hos, dea, imm = virus_dic[FN_K]()
        virus_dic[CON_K][i] = con
        virus_dic[HOS_K][i] = hos
        virus_dic[DEA_K][i] = dea
        virus_dic[IMM_K][i] = imm


def decide_life_immunity(env_dic, virus_dic, individual, icu_factor):
    if virus_dic[DEA_K][individual] == 0:
        # icu_factor only applies on hospitalized people
        if get_r() < get_mortalty_rate(env_dic[IAG_K][individual]) * \
                (icu_factor if (virus_dic[STA_K][individual] == HOSPITALIZED_V) else 1):
            virus_dic[STA_K][individual] = DEAD_V
        else:
            virus_dic[STA_K][individual] = IMMUNE_V


def decide_hospitalization(env_dic, virus_dic, individual_arg):
    if virus_dic[HOS_K][individual_arg] == 0 and get_r() < get_hospitalization_rate(env_dic[IAG_K][individual_arg]):
        virus_dic[STA_K][individual_arg] = HOSPITALIZED_V
        family = env_dic[HI_K][env_dic[IH_K][individual_arg]]
        virus_dic[STA_K].update((fm, ISOLATED_V) for fm in family if (virus_dic[STA_K][fm] == INFECTED_V))


def increment_infection(virus_dic, individual_arg):
    virus_dic[CON_K][individual_arg] = virus_dic[CON_K][individual_arg] - 1
    virus_dic[HOS_K][individual_arg] = virus_dic[HOS_K][individual_arg] - 1
    virus_dic[DEA_K][individual_arg] = virus_dic[DEA_K][individual_arg] - 1


def increment_pandemic_1_day(env_dic, virus_dic, available_beds):
    # ICU factor is used to raise death probability when hospitals are saturated
    icu_factor = max(1.0, len(get_hospitalized_people(virus_dic)) / available_beds)

    for individual in get_virus_carrier_people(virus_dic):
        # Contagion, decision and hospitalization periods are decremented
        increment_infection(virus_dic, individual)

    for individual in get_infected_people(virus_dic):
        # Do INFECTED -> HOSPITALIZED
        # Do INFECTED -> ISOLATED for family members
        decide_hospitalization(env_dic, virus_dic, individual)

    for individual in get_virus_carrier_people(virus_dic):
        # Do {INFECTED, ISOLATED, HOSPITALIZED} -> {DEAD, IMMUNE} decision transition
        decide_life_immunity(env_dic, virus_dic, individual, icu_factor)

    # Do IMMUNE -> HEALTHY for no longer immune people
    for individual in get_immune_people(virus_dic):
        update_immunity_state(virus_dic, individual)


def get_virus_carrier_people(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == ISOLATED_V or v == HOSPITALIZED_V or v == INFECTED_V]


def get_isolated_people(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == ISOLATED_V]


def get_hospitalized_people(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == HOSPITALIZED_V]


def get_infected_people(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == INFECTED_V]


def get_contagious_people(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == INFECTED_V and virus_dic[CON_K][k] < 0]


def get_deadpeople(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == DEAD_V]


def get_healthy_people(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == HEALTHY_V]


def get_immune_people(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == IMMUNE_V]


def is_isolated(individual_arg, virus_dic):
    return virus_dic[STA_K][individual_arg] == ISOLATED_V


def is_contagious(individual_arg, virus_dic):
    return virus_dic[STA_K][individual_arg] == INFECTED_V and virus_dic[CON_K][individual_arg] < 0


def is_alive(individual_arg, virus_dic):
    return virus_dic[STA_K][individual_arg] != DEAD_V


def propagate_to_houses(env_dic, virus_dic, probability_home_infection_arg):
    # Houses that contain an infected and contagious person with an associated behavior weight
    # ( (1, 1.5), (1, 2), (2, 1) )
    # House 1 with 1.5 and 2 weights and House 2 with weight 1
    infected_houses_behavior = [(env_dic[IH_K][i], env_dic[IBE_K][i]) for i in get_infected_people(virus_dic)
                                if is_contagious(i, virus_dic)]

    # We reduce_multiply_by_key multiply it to get
    # { 1: 1.5 * 2  ,   2: 1 }
    infected_houses_behavior_dic = reduce_multiply_by_key(infected_houses_behavior)

    # We build people at those houses with the house behavior
    # [ ([1, 2, 3], 1), ([4, 5, 6], 2), ([1, 2, 3], 2) ]
    people_in_infected_houses = [(env_dic[HI_K][hou], beh_p) for (hou, beh_p) in infected_houses_behavior_dic.items()]

    # From which we designate newly infected people using weights beh_p
    infected_athome = [i for people, beh_p in people_in_infected_houses for i in people
                       if get_r() < probability_home_infection_arg * beh_p]

    # INFECTION STATE UPDATE
    update_infection_period(infected_athome, virus_dic)


def propagate_to_workplaces(env_dic, virus_dic, probability_work_infection_arg, probability_remote_work_arg):
    # [1, 2, 3] go to work
    # Contagious people who will go to work
    infected_gotowork = [i for i in get_contagious_people(virus_dic) if i in env_dic[IW_K].keys()
                         and get_r() < (1-probability_remote_work_arg) * env_dic[IBE_K][i]]
    # Infected workplaces
    # [ (1, 1.1), (2, 1), (1, 1.4) ]
    infected_workplaces_behavior = [(env_dic[IW_K][i], env_dic[IBE_K][i]) for i in infected_gotowork]

    # Infected workplaces
    # { 1: 1.1* 1.4, 2: 1 }
    infected_workplaces_behavior_dic = reduce_multiply_by_key(infected_workplaces_behavior)

    # We build people at those workplaces
    # [ ([1, 2, 3], 1), ([4, 5, 6], 2), ([1, 2, 3], 2) ]
    exposed_individuals_at_work = [(env_dic[WI_K][k], beh_p) for (k, beh_p) in infected_workplaces_behavior_dic.items()]

    # People who have gone to work (not isolated) and got infected
    infected_backfromwork = [i for people, beh_p in exposed_individuals_at_work for i in people
                             if get_r() < probability_work_infection_arg * beh_p]

    # INFECTION STATE UPDATE
    update_infection_period(infected_backfromwork, virus_dic)


def propagate_to_transportation(env_dic, virus_dic, probability_transport_infection_arg,
                                probability_remote_work_arg, transportation_cap_arg):
    # Contagious people who will go to work
    # [1, 2, 3] go to work
    infected_who_goto_work = [i for i in get_contagious_people(virus_dic) if i in env_dic[IW_K].keys()
                              and get_r() < (1-probability_remote_work_arg) * env_dic[IBE_K][i]]

    # Infected public transportation blocks with cap 2
    # individuals 1, 2, 3 are in an infected block
    # same for 4, 5, 6
    # Result : [ ({1, 3}, 1), ({5, 6}, 1.5) ] with random sample
    people_sharing_transportation = [(get_random_sample(env_dic[ITI_K][i], transportation_cap_arg), env_dic[IBE_K][i])
                                     for i in infected_who_goto_work]

    infected_bad_luck_transport = [i for people, beh_p in people_sharing_transportation for i in people
                                   if get_r() < probability_transport_infection_arg * beh_p]

    # INFECTION STATE UPDATE
    update_infection_period(infected_bad_luck_transport, virus_dic)


def propagate_to_stores(env_dic, virus_dic, probability_store_infection_arg, same_store_preference):
    # Filter on living people because we have a random choice to make in each house
    # People who will go to their store (one person per house as imposed by lockdown)
    # [1, 2, 3, 4, 5, 6] go to the store
    individuals_gotostore = get_random_choice_list([
        [i for i in env_dic[HA_K][h] if (is_alive(i, virus_dic) and not (is_isolated(i, virus_dic)))] for h in
        range(len(env_dic[HA_K]))
    ])

    # Contagious people who will go to their store
    # [1, 4, 5] are infected and going to the store
    individuals_infected_gotostore = [i for i in individuals_gotostore if is_contagious(i, virus_dic)]

    # [(2, 0), (3, 1), (6, 2)]  2, 3 and 6 are infected and going to the stores 0, 1 and 2
    # we divide same_store_preference by behavior since high behavior value is bad behavior
    individuals_healthy_gotostore = [
        (i, choose_weight_order(env_dic[HS_K][env_dic[IH_K][i]], same_store_preference / env_dic[IBE_K][i]))
        for i in individuals_gotostore if not is_contagious(i, virus_dic)
    ]

    # Stores that will be visited by a contagious person
    # [ (0, 1), (0, 1.3), (2, 1.2)] where stores 0 and 2 are infected with 1, 1.3 and 1.2 weights
    infected_stores = [
        (choose_weight_order(env_dic[HS_K][env_dic[IH_K][i]], same_store_preference / env_dic[IBE_K][i]), env_dic[IBE_K][i])
        for i in individuals_infected_gotostore
    ]

    # { 0: 1*1.3, 2: 1.2 } are the weights of each infected store
    infected_stores_dic = reduce_multiply_by_key(infected_stores)

    # We get the list of people who are healty + have chosen an infected store + get bad luck with get_r
    # [2, 6] got infected
    gonna_be_infected = [ind for (ind, s) in individuals_healthy_gotostore if s in infected_stores_dic.keys()
                         and get_r() < probability_store_infection_arg * env_dic[IBE_K][ind] * infected_stores_dic[s]]

    # INFECTION STATE UPDATE
    update_infection_period(gonna_be_infected, virus_dic)


def get_r0(virus_dic):
    return virus_dic[NC_K] / (1 + len(get_contagious_people(virus_dic)))


def get_pandemic_statistics(virus_dic):
    results = {
        "hea": len(get_healthy_people(virus_dic)),
        "inf": len(get_infected_people(virus_dic)),
        "hos": len(get_hospitalized_people(virus_dic)),
        "dea": len(get_deadpeople(virus_dic)),
        "imm": len(get_immune_people(virus_dic)),
        "iso": len(get_isolated_people(virus_dic)),
        "R0": get_r0(virus_dic),
        "new": virus_dic[NC_K]
    }
    # Reset new cases counter
    virus_dic[NC_K] = 0
    return results


def update_stats(virus_dic, stats, r, d):
    for k, v in get_pandemic_statistics(virus_dic).items():
        stats[k][r][d] = v


def get_mortalty_rate(age):
    i = next(x for x in enumerate(list(covid_mortality_rate.keys())) if x[1] <= age / 10)
    return covid_mortality_rate[i[1]]


def get_hospitalization_rate(age):
    i = next(x for x in enumerate(list(covid_hospitalization_rate.keys())) if x[1] <= age / 10)
    return covid_hospitalization_rate[i[1]]