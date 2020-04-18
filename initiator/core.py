import random

from scipy import spatial

from initiator.helper import get_r, invert_map, pick_age, get_center_squized_random, pick_random_company_size


def build_individual_houses_map(number_individual_arg, proba_same_house_rate):
    # Individual -> House
    all_ind_hou = {}
    i_hou = 0
    i_ind = 0
    is_first_person = True
    prob_keep_hou = get_r()
    while i_ind < number_individual_arg:
        if is_first_person:
            all_ind_hou[i_ind] = i_hou  # Attach first person to the house
            i_ind = i_ind + 1  # GOTO next person
            is_first_person = False
            continue
        if prob_keep_hou > proba_same_house_rate:
            all_ind_hou[i_ind] = i_hou  # Attach Next person
            i_ind = i_ind + 1  # GOTO next person
            prob_keep_hou = prob_keep_hou / 2  # Divide probability keep_foy
        else:
            i_hou = i_hou + 1  # GOTO next house
            prob_keep_hou = get_r()  # RESET keep_hou probability
            is_first_person = True  # New house needs a first person
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


def build_geo_positions_store(number_store_arg):
    return [(get_r(), get_r()) for i in range(number_store_arg)]


def build_geo_positions_workplace(number_workpolace_arg):
    return [(get_center_squized_random(), get_center_squized_random()) for i in range(number_workpolace_arg)]


def get_store_index(indexes, prob_preference_store):
    return [index[0] if get_r()<prob_preference_store else index[1]  for index in indexes]


def build_house_store_map(geo_position_store_arg, geo_position_house_arg,prob_preference_store):
    distance, indexes = spatial.KDTree(geo_position_store_arg).query(geo_position_house_arg,k=2)
    all_hou_sto = dict(zip(range(len(geo_position_house_arg)), get_store_index(indexes, prob_preference_store)))
    return all_hou_sto


def build_store_house_map(house_store_map_arg):
    # Grocerie store -> List of House
    return invert_map(house_store_map_arg)


def build_individual_work_map(individual_adult_map_arg):
    # Only adults work, and only half of them
    workers = list([i for i in range(len(individual_adult_map_arg)) if get_r() < 0.5
                    and individual_adult_map_arg[i] == 1])
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
