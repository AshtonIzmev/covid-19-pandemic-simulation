import math
import random

import pandas as pd
from scipy.stats import truncnorm

from initiator.parameters import covid_mortality_rate, covid_hospitalization_rate, world_age_distribution, \
    TPE_MAX_EMPLOYEES, PME_MAX_EMPLOYEES, GE_MAX_EMPLOYEES


def get_r():
    return random.random()


def get_moroccan_household_distribution():
    return get_clipped_gaussian_number(1, 10, 4.52, math.sqrt(4.71)).astype(int)


def get_lockdown_behavior_distribution():
    return get_clipped_gaussian_number(0.5, 1.5, 1, 0.25)


def get_clipped_gaussian_number(lower_clip_arg, upper_clip_arg, mean_arg, std_arg):
    a, b = (lower_clip_arg - mean_arg) / std_arg, (upper_clip_arg - mean_arg) / std_arg
    return truncnorm.rvs(a, b, loc=mean_arg, scale=std_arg)


def get_random_choice_list(list_of_list_arg):
    result = []
    for list_arg in list_of_list_arg:
        if len(list_arg) > 0:
            result.append(random.choice(list_arg))
    return result


def get_random_sample(iterable_arg, cap):
    return random.sample(iterable_arg, min(cap, len(iterable_arg)))


def get_infection_parameters(lower_contagion_bound, upper_contagion_bound,
                             lower_hospitalization_bound, upper_hospitalization_bound,
                             lower_death_bound, upper_death_bound,
                             lower_immunity_bound, upper_immunity_bound):
    # Time to death/immunity , Time to contagiosity
    return int(lower_contagion_bound + (upper_contagion_bound - lower_contagion_bound) * get_r()), \
           int(lower_hospitalization_bound + (upper_hospitalization_bound - lower_hospitalization_bound) * get_r()), \
           int(lower_death_bound + (upper_death_bound - lower_death_bound) * get_r()), \
           int(lower_immunity_bound + (upper_immunity_bound - lower_immunity_bound) * get_r())


def get_mortalty_rate(age):
    i = next(x for x in enumerate(list(covid_mortality_rate.keys())) if x[1] <= age / 10)
    return covid_mortality_rate[i[1]]


def get_hospitalization_rate(age):
    i = next(x for x in enumerate(list(covid_hospitalization_rate.keys())) if x[1] <= age / 10)
    return covid_hospitalization_rate[i[1]]


def flatten(list_arg):
    return [item for sublist in list_arg for item in sublist]


def invert_map(dic_arg):
    inverted_dic_arg = {}
    for k, v in dic_arg.items():
        inverted_dic_arg[v] = inverted_dic_arg.get(v, [])
        inverted_dic_arg[v].append(k)
    return inverted_dic_arg


def invert_map_list(dic_arg):
    inverted_dic_arg = {}
    for k, v in dic_arg.items():
        for el in v:
            inverted_dic_arg[el] = inverted_dic_arg.get(el, [])
            inverted_dic_arg[el].append(k)
    return inverted_dic_arg


def get_age_distribution():
    # Source https://www.populationpyramid.net/world/2019/
    age_distribution = pd.DataFrame(world_age_distribution, columns=['age', 'nb_men', 'nb_women'])
    age_distribution['nb'] = age_distribution['nb_men'] + age_distribution['nb_women']
    age_distribution['pct'] = age_distribution['nb'] / age_distribution['nb'].sum()
    age_distribution['min_age'] = age_distribution['age'].map(lambda s: int(s.split('-')[0]))
    age_distribution['max_age'] = age_distribution['age'].map(lambda s: int(s.split('-')[1]))
    # We did a cut to 25 years old for adult
    age_distribution_children = age_distribution.iloc[:7]
    age_distribution_adults = age_distribution.iloc[4:]
    age_distribution_children_cumsum = \
        age_distribution_children['pct'].cumsum() / age_distribution_children['pct'].cumsum().max()
    age_distribution_adults_cumsum = \
        age_distribution_adults['pct'].cumsum() / age_distribution_adults['pct'].cumsum().max()
    return age_distribution_children, age_distribution_children_cumsum, age_distribution_adults, \
           age_distribution_adults_cumsum


age_dist_children, age_dist_children_cs, age_dist_adults, age_dist_adults_cs = get_age_distribution()


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


def get_center_squized_random():
    u = get_r()
    return 4 * (u - 0.5) * (u - 0.5) * (u - 0.5) + 0.5


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


# Recursive Manhattan walk
def rec_get_manhattan_walk(result, p1, p2):
    i, j = p1
    k, l = p2
    if i == k and j == l:
        return result + [p1]
    if j == l:
        if i < k:
            return rec_get_manhattan_walk(result + [p1, p2], (k, l), (i + 1, j))
        else:
            return rec_get_manhattan_walk(result + [p1, p2], (k + 1, l), (i, j))
    else:
        if j < l:
            return rec_get_manhattan_walk(result + [p1, p2], (i, j + 1), (k, l))
        else:
            return rec_get_manhattan_walk(result + [p1, p2], (k, l + 1), (i, j))


def reduce_multiply_by_key(tuple_list):
    result_dic = {}
    for (k, v) in tuple_list:
        result_dic[k] = v * (result_dic[k] if k in result_dic else 1)
    return result_dic


def choose_weight_order(list_arg, prob):
    try:
        return next(x[1] for x in enumerate(list_arg) if get_r() <= prob)
    except StopIteration:
        return list_arg[-1]
