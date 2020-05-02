import math
import random

from scipy import spatial

from simulator.constants.keys import nindividual_key, store_per_house_key, nb_1d_block_key, store_nb_choice_key, \
    transport_contact_cap_key, IH_K, HI_K, IAD_K, IAG_K, IW_K, WI_K, HA_K, HS_K, ITI_K, HB_K, IBE_K
from simulator.constants.parameters import TPE_MAX_EMPLOYEES, PME_MAX_EMPLOYEES, GE_MAX_EMPLOYEES
from simulator.constants.parameters import age_dist_adults_cs, age_dist_adults, \
    age_dist_children, age_dist_children_cs
from simulator.helper.utils import invert_map, get_r, get_center_squized_random, rec_get_manhattan_walk, \
    invert_map_list, \
    get_random_sample, get_clipped_gaussian_number


def get_environment_simulation(params_arg):
    number_of_individuals_arg = params_arg[nindividual_key]
    number_store_per_house_arg = params_arg[store_per_house_key]
    nb_1d_block_arg = params_arg[nb_1d_block_key]
    nb_store_choice = params_arg[store_nb_choice_key]
    transportation_cap = params_arg[transport_contact_cap_key]

    indiv_house = build_individual_houses_map(number_of_individuals_arg)
    house_indiv = build_house_individual_map(indiv_house)
    indiv_adult = build_individual_adult_map(indiv_house)
    indiv_age = build_individual_age_map(indiv_house)

    indiv_workplace = build_individual_work_map(indiv_adult)
    workplace_indiv = build_workplace_individual_map(indiv_workplace)
    house_adult = build_house_adult_map(indiv_house, indiv_adult)

    geo_house = build_geo_positions_house(len(house_indiv))
    geo_workplace = build_geo_positions_workplace(len(workplace_indiv))
    geo_store = build_geo_positions_store(int(len(house_indiv) / number_store_per_house_arg))

    house_store = build_house_store_map(geo_store, geo_house, nb_store_choice)

    house_block = build_block_assignment(geo_house, nb_1d_block_arg)
    workplace_block = build_block_assignment(geo_workplace, nb_1d_block_arg)

    indiv_behavior = build_1d_item_behavior(number_of_individuals_arg)

    indiv_transport_block = build_individual_workblock_map(indiv_house, indiv_workplace, house_block, workplace_block)
    transport_block_indiv = build_workblock_individual_map(indiv_transport_block)

    indiv_transport_indiv = build_individual_individual_transport_map(indiv_transport_block, transport_block_indiv,
                                                                      transportation_cap)

    return {
        IH_K: indiv_house,
        HI_K: house_indiv,
        IAD_K: indiv_adult,
        IAG_K: indiv_age,
        IW_K: indiv_workplace,
        WI_K: workplace_indiv,
        HA_K: house_adult,
        HS_K: house_store,
        ITI_K: indiv_transport_indiv,
        HB_K: house_block,
        IBE_K: indiv_behavior
    }


def build_individual_houses_map(number_individual_arg):
    # Individual -> House
    all_ind_hou = {}
    i_hou = 0
    i_ind = 0
    while i_ind < number_individual_arg:
        family_members = get_moroccan_household_distribution()
        individulas = list(range(i_ind, i_ind+family_members))
        index_house = [i_hou]*family_members
        one_house = dict(zip(individulas, index_house))
        all_ind_hou.update(one_house)
        i_ind = i_ind+family_members
        i_hou += 1
    # eliminate side effects
    for i in range((len(all_ind_hou)-1), number_individual_arg-1, -1):
        del all_ind_hou[i]
    return all_ind_hou


def build_house_individual_map(individual_house_map_arg):
    # House -> List of individuals
    return invert_map(individual_house_map_arg)


def build_individual_adult_map(individual_house_map_arg):
    all_ind_adu = {0: 1}  # We track who is adult to further affect a work
    incr_ind = 1
    i_ind = 1
    while i_ind < len(individual_house_map_arg):
        if individual_house_map_arg[i_ind] != individual_house_map_arg[i_ind-1]:  # We have a new house
            incr_ind = 0
        # First two persons in a house are adults since children cannot live alone
        # Could be extended to monoparental families but anyway ...
        if incr_ind < 2:
            all_ind_adu[i_ind] = 1
        else:
            all_ind_adu[i_ind] = 0
        incr_ind = incr_ind + 1
        i_ind = i_ind + 1
    return all_ind_adu


def build_individual_age_map(individual_house_map_arg):
    all_ind_age = {0: pick_age(is_child=False)}
    incr_ind = 1
    i_ind = 1
    while i_ind < len(individual_house_map_arg):
        if individual_house_map_arg[i_ind] != individual_house_map_arg[i_ind-1]: # We have a new house
            incr_ind = 0
        if incr_ind < 2:
            all_ind_age[i_ind] = pick_age(is_child=False)
        else:
            all_ind_age[i_ind] = pick_age(is_child=True)
        incr_ind = incr_ind + 1
        i_ind = i_ind + 1
    return all_ind_age


def build_house_adult_map(individual_house_map_arg, individual_adult_map_arg):
    # House -> List of adults (needed to check you goes to the store)
    all_hou_adu = {}
    for k, v in individual_house_map_arg.items():
        all_hou_adu[v] = all_hou_adu.get(v, [])
        if individual_adult_map_arg[k] == 1:
            all_hou_adu[v].append(k)
    return all_hou_adu


def build_geo_positions_house(number_house_arg):
    return [(get_r(), get_r()) for i in range(number_house_arg)]


def build_block_assignment(geo_arg, nb_1d_blocks_arg):
    return [(int(h[0] * nb_1d_blocks_arg), int(h[1] * nb_1d_blocks_arg)) for h in geo_arg]


def build_2d_item_behavior(nb_items):
    item_list = [(i, j) for i in range(nb_items) for j in range(nb_items)]
    behavior_list = [get_lockdown_behavior_distribution() for _ in range(nb_items * nb_items)]
    return dict(zip(item_list, behavior_list))


def build_1d_item_behavior(nb_items):
    behavior_list = [get_lockdown_behavior_distribution() for _ in range(nb_items)]
    return dict(zip(range(nb_items), behavior_list))


def build_geo_positions_store(number_store_arg):
    return [(get_r(), get_r()) for i in range(number_store_arg)]


def build_geo_positions_workplace(number_workpolace_arg):
    return [(get_center_squized_random(), get_center_squized_random()) for i in range(number_workpolace_arg)]


def get_store_index(indexes, prob_preference_store):
    return [index[0] if get_r() < prob_preference_store else index[1] for index in indexes]


def build_house_store_map(geo_position_store_arg, geo_position_house_arg, nb_store_choice):
    _, indexes = spatial.KDTree(geo_position_store_arg).query(geo_position_house_arg, k=nb_store_choice)
    all_hou_sto = dict(zip(range(len(geo_position_house_arg)), [list(i) for i in indexes]))
    return all_hou_sto


def build_individual_work_map(individual_adult_map_arg):
    # Only adults work
    workers = list([ind for ind, is_adult in individual_adult_map_arg.items() if is_adult == 1])
    random.shuffle(workers)
    all_ind_wor = {}
    i_wor = 0
    while len(workers) > 0:
        for j in range(pick_random_company_size()):
            if len(workers) == 0:
                break
            ind = workers.pop()
            all_ind_wor[ind] = i_wor
        i_wor = i_wor + 1
    return all_ind_wor


def build_workplace_individual_map(individual_workplace_map_arg):
    # workplace -> Individuals
    return invert_map(individual_workplace_map_arg)


def build_individual_workblock_map(individual_house_map_arg, individual_workplace_map_arg,
                                   house_block_map_arg, workplace_block_map_arg):
    # Individual to blocks durint public transport
    intermediate_blocks = {}
    for ind, work in individual_workplace_map_arg.items():
        house_block = house_block_map_arg[individual_house_map_arg[ind]]
        workplace_block = workplace_block_map_arg[individual_workplace_map_arg[ind]]
        intermediate_blocks[ind] = list(set(rec_get_manhattan_walk([], house_block, workplace_block)))
    return intermediate_blocks


def build_workblock_individual_map(individual_workblock_map_arg):
    # Blocks to individuals
    return invert_map_list(individual_workblock_map_arg)


def build_individual_individual_transport_map(individual_transport_block_map_arg, transport_block_individual_map_arg,
                                              transportation_cap_arg):
    individual_individual_transport_dic = {}
    for ind, blocks in individual_transport_block_map_arg.items():
        for block in get_random_sample(blocks, transportation_cap_arg):
            if ind not in individual_individual_transport_dic:
                individual_individual_transport_dic[ind] = set()
            individual_individual_transport_dic[ind].update(
                get_random_sample(set(transport_block_individual_map_arg[block]), transportation_cap_arg))
    return individual_individual_transport_dic


def get_moroccan_household_distribution():
    return get_clipped_gaussian_number(1, 10, 4.52, math.sqrt(4.71)).astype(int)


def pick_random_company_size():
    p = get_r()
    if p < 0.44:
        # We picked a TPE
        return int(1 + (TPE_MAX_EMPLOYEES - 1) * get_r())
    elif p < 0.86:
        # We picked a PME
        return int(TPE_MAX_EMPLOYEES + (PME_MAX_EMPLOYEES - TPE_MAX_EMPLOYEES) * get_r())
    else:
        # We picked a PME
        return int(PME_MAX_EMPLOYEES + (GE_MAX_EMPLOYEES - PME_MAX_EMPLOYEES) * get_r())


def get_lockdown_behavior_distribution():
    return get_clipped_gaussian_number(0.5, 1.5, 1, 0.25)


def pick_age(is_child):
    if is_child:
        l_cs = age_dist_children_cs
        l_dis = age_dist_children
    else:
        l_cs = age_dist_adults_cs
        l_dis = age_dist_adults
    i = next(x[0] for x in enumerate(l_cs.values) if x[1] > get_r())
    min_age_i = l_dis.iloc[i]['min_age']
    max_age_i = l_dis.iloc[i]['max_age']
    return int(min_age_i + (max_age_i - min_age_i) * get_r())