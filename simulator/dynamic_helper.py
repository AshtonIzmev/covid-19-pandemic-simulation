from initiator.helper import flatten, get_random_choice_list
from initiator.helper import get_r, get_mortalty_rate, get_hospitalization_rate, reduce_multiply_by_key, \
    reduce_list_multiply_by_key
from simulator.keys import *


# Assuming 0 is Monday
def is_weekend(i):
    return ((i - 5) % 7 == 0) or ((i - 6) % 7 == 0)


def update_infection_period(newly_infected_individuals_arg, virus_dic):
    for i in newly_infected_individuals_arg:
        if virus_dic[STA_K][i] == HEALTHY_V:
            virus_dic[STA_K][i] = INFECTED_V
            virus_dic[NC_K] = virus_dic[NC_K] + 1


# ICU factor is used to raise death probability when hospitals are saturated
def increment_pandemic_1_day(env_dic, virus_dic, available_beds):
    icu_factor = max(1.0, len(get_hospitalized_people(virus_dic)) / (2*available_beds))
    for i in get_infected_people(virus_dic) + get_hospitalized_people(virus_dic)+ get_isolated_people(virus_dic):
        # Contagion and decision periods are decremented
        virus_dic[CON_K][i] = virus_dic[CON_K][i] - 1
        virus_dic[HOS_K][i] = virus_dic[HOS_K][i] - 1
        virus_dic[DEA_K][i] = virus_dic[DEA_K][i] - 1
        # Even if hospitals are full, sick people are being parked in artisanal lacking care "hospitals"
        if virus_dic[HOS_K][i] == 0 and get_r() < get_hospitalization_rate(env_dic[IAG_K][i]):
            virus_dic[STA_K][i] = HOSPITALIZED_V
        # Decide over life
        if virus_dic[DEA_K][i] == 0:
            if get_r() < get_mortalty_rate(env_dic[IAG_K][i]) * icu_factor:
                virus_dic[STA_K][i] = DEAD_V
            else:
                virus_dic[STA_K][i] = IMMUNE_V
    for i in get_immune_people(virus_dic):
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

def get_isolated_people(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == ISOLATED_V]

def get_hospitalized_people(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == HOSPITALIZED_V]


def get_infected_people(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == INFECTED_V]


def get_deadpeople(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == DEAD_V]


def get_healthy_people(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == HEALTHY_V]


def get_immune_people(virus_dic):
    return [k for k, v in virus_dic[STA_K].items() if v == IMMUNE_V]


def get_pandemic_statistics(virus_dic):
    results = (len(get_healthy_people(virus_dic)), len(get_infected_people(virus_dic)),
               len(get_hospitalized_people(virus_dic)), len(get_deadpeople(virus_dic)),
               len(get_immune_people(virus_dic)), virus_dic[NC_K],len(get_isolated_people(virus_dic)))
    # Reset new cases counter
    virus_dic[NC_K] = 0
    return results


def is_contagious(individual_arg, virus_dic):
    return virus_dic[STA_K][individual_arg] == INFECTED_V and virus_dic[CON_K][individual_arg] < 0


def is_alive(individual_arg, virus_dic):
    return virus_dic[STA_K][individual_arg] != DEAD_V

def get_new_hospitalized_people(old_virus_dic,new_virus_dic):
    return list(set(get_hospitalized_people(new_virus_dic)).difference(set(get_hospitalized_people(old_virus_dic))))



def get_families(persons_index,env_dic):
    families_members=[]
    for person in persons_index:
        house_index=env_dic[IH_K][person]
        families_members=families_members+env_dic[HI_K][house_index]
    return list(set(families_members))


def update_isolation_state(old_virus_dic,new_virus_dic,env_dic):
    new_hospitalized_cases=get_new_hospitalized_people(old_virus_dic,new_virus_dic)
    families_members=get_families(new_hospitalized_cases,env_dic)
    new_virus_dic[STA_K].update((k, ISOLATED_V) for k, v in new_virus_dic[STA_K].items() if (v == INFECTED_V and (k in families_members)) )



def propagate_to_houses(env_dic, virus_dic, probability_home_infection_arg):
    # Houses that contain an infected and contagious person with an associated behavior weight
    # ( (1, 1.5), (1, 2), (2, 1) )
    # House 1 with 1.5 and 2 weights and House 2 with weight 1
    infected_houses_behavior = [(env_dic[IH_K][i], env_dic[IBE_K][i]) for i in get_infected_people(virus_dic)
                                if is_contagious(i, virus_dic)]

    # We reduce_multiply_by_key multiply it to get
    # { 1: 1.5 * 2  ,   2: 1 }
    infected_houses_behavior_dic = reduce_multiply_by_key(infected_houses_behavior)

    # We build people at those houses
    # [ ([1, 2, 3], 1), ([4, 5, 6], 2), ([1, 2, 3], 2) ]
    # And then we reduce_list_multiply_by_key this
    # { 1: 1*2, 2: 1*2, 3: 1*2, 4: 2, 5: 2, 6: 2 }
    people_in_infected_houses = reduce_list_multiply_by_key(
        [(env_dic[HI_K][hou], beh_p) for (hou, beh_p) in infected_houses_behavior_dic.items()]
    )

    # From which we designate newly infected people using weights beh_p
    infected_athome = [i for (i, beh_p) in people_in_infected_houses.items()
                       if get_r() < probability_home_infection_arg * beh_p]

    # INFECTION STATE UPDATE
    update_infection_period(infected_athome, virus_dic)


def propagate_to_workplaces(env_dic, virus_dic, probability_work_infection_arg):
    # Contagious people who will go to work
    # [1, 2, 3] go to work
    infected_gotowork = [i for i in get_infected_people(virus_dic) if i in env_dic[IW_K].keys()
                         and is_contagious(i, virus_dic)]
    # Infected workplaces
    # [ (1, 1.1), (2, 1), (1, 1.4) ]
    infected_workplaces_behavior = [(env_dic[IW_K][i], env_dic[IBE_K][i]) for i in infected_gotowork]

    # Infected workplaces
    # { 1: 1.1* 1.4, 2: 1 }
    infected_workplaces_behavior_dic = reduce_multiply_by_key(infected_workplaces_behavior)

    # We build people at those workplaces
    # [ ([1, 2, 3], 1), ([4, 5, 6], 2), ([1, 2, 3], 2) ]
    # And then we reduce_list_multiply_by_key this
    # { 1: 1*2, 2: 1*2, 3: 1*2, 4: 2, 5: 2, 6: 2 }
    exposed_individuals_at_work = reduce_list_multiply_by_key(
        [(env_dic[WI_K][k], beh_p) for (k, beh_p) in infected_workplaces_behavior_dic.items()]
    )

    # From which we designate newly infected people using weights beh_p
    infected_backfromwork = [i for (i, beh_p) in exposed_individuals_at_work.items()
                             if get_r() < probability_work_infection_arg * beh_p]

    # INFECTION STATE UPDATE
    update_infection_period(infected_backfromwork, virus_dic)


def propagate_to_transportation(env_dic, virus_dic, probability_transport_infection_arg):
    # Contagious people who will go to work
    # [1, 2, 3] go to work
    infected_who_goto_work = [i for i in get_infected_people(virus_dic) if i in env_dic[IW_K].keys()
                              and is_contagious(i, virus_dic)]

    # Infected public transportation blocks
    # individuals 1, 2, 3 are in an infected block
    # same for 4, 5, 6
    # Reduce this : [ ({1, 2, 3}, 1), ({4, 5, 6}, 1.5) ]
    # which gives  { 1: 1, 2: 1, 3: 2, 4: 1.5, 5: 1.5, 6: 1.5 }
    people_sharing_transportation = reduce_list_multiply_by_key(
        [(env_dic[ITI_K][i], env_dic[IBE_K][i]) for i in infected_who_goto_work]
    )

    infected_bad_luck_transport = [i for (i, beh_p) in people_sharing_transportation.items()
                                   if get_r() < probability_transport_infection_arg * beh_p]

    # INFECTION STATE UPDATE
    update_infection_period(infected_bad_luck_transport, virus_dic)


def propagate_to_stores(env_dic, virus_dic, probability_store_infection_arg):
    # Filter on living people because we have a random choice to make in each house
    # People who will go to their store (one person per house as imposed by lockdown)
    # [1, 2, 3, 4, 5, 6] go to the store
    individuals_gotostore = get_random_choice_list([
        [i for i in env_dic[HA_K][h] if is_alive(i, virus_dic)] for h in range(len(env_dic[HA_K]))
    ])

    # Contagious people who will go to their store
    # [1, 4, 5] are infected and going to the store
    individuals_infected_gotostore = [i for i in individuals_gotostore if is_contagious(i, virus_dic)]

    # Stores that will be visited by a contagious person
    # [ (0, 1), (0, 1.3), (2, 1.2)] where stores 0 and 2 are infected
    infected_stores = [(env_dic[HS_K][env_dic[IH_K][i]], env_dic[IBE_K][i]) for i in individuals_infected_gotostore]

    # { 0: 1*1.3, 2: 1.2 } are the weights of each infected store
    infected_stores_dic = reduce_multiply_by_key(infected_stores)

    # People who live in a house that goes to a contagious store
    # We have [ ([1, 4, 9], 1*1.3), ([2, 6, 7], 1.2) ]
    # Then reduced the following people { 1: 1.3, 4: 1.3, 9: 1.3, 2: 1.2, 6: 1.2, 7: 1.2 }
    individuals_attachedto_infected_store = reduce_list_multiply_by_key(
        flatten([[(env_dic[HA_K][h], beh_p) for h in env_dic[SH_K][s]] for (s, beh_p) in infected_stores_dic.items()])
    )

    # People who did go to that contagious store
    # { 1: 1.3, 4: 1.3, 2: 1.2, 6: 1.2 } ## 9 and 7 have been removed since they did not go to the store that day

    individuals_goto_infected_store = {
        k: individuals_attachedto_infected_store[k]
        for k in (individuals_gotostore & individuals_attachedto_infected_store.keys())
    }
    # People who got infected from going to their store
    infected_backfromstore = [i for (i, beh_p) in individuals_goto_infected_store.items()
                              if get_r() < probability_store_infection_arg * beh_p]

    # INFECTION STATE UPDATE
    update_infection_period(infected_backfromstore, virus_dic)
