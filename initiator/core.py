import random

from scipy import spatial

from initiator.helper import get_r, get_moroccan_household_distribution, invert_map, pick_age, \
    get_center_squized_random, pick_random_company_size, rec_get_manhattan_walk, invert_map_list, \
    get_lockdown_behavior_distribution


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


def build_house_store_map(geo_position_store_arg, geo_position_house_arg,prob_preference_store):
    distance, indexes = spatial.KDTree(geo_position_store_arg).query(geo_position_house_arg, k=2)
    all_hou_sto = dict(zip(range(len(geo_position_house_arg)), get_store_index(indexes, prob_preference_store)))
    return all_hou_sto


def build_store_house_map(house_store_map_arg):
    # Grocerie store -> List of House
    return invert_map(house_store_map_arg)


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


def build_individual_individual_transport_map(individual_transport_block_map_arg, transport_block_individual_map_arg):
    individual_individual_transport_dic = {}
    for ind, blocks in individual_transport_block_map_arg.items():
        for block in blocks:
            individual_individual_transport_dic[ind] = individual_individual_transport_dic.get(ind, set())
            individual_individual_transport_dic[ind].update(set(transport_block_individual_map_arg[block]))
    return individual_individual_transport_dic
