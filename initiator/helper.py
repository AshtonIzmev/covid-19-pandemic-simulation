import random

import pandas as pd

from initiator.parameters import covid_mortality_rate, world_age_distribution, \
    TPE_MAX_EMPLOYEES, PME_MAX_EMPLOYEES, GE_MAX_EMPLOYEES


def get_r():
    return random.random()


def get_random_choice_list(list_of_list_arg):
    result = []
    for list_arg in list_of_list_arg:
        if len(list_arg) > 0:
            result.append(random.choice(list_arg))
    return result


def get_infection_parameters(lower_infection_bound, upper_infection_bound,
                             lower_contagion_bound, upper_contagion_bound):
    # Time to death/immunity , Time to contagiosity
    return int(lower_infection_bound + (upper_infection_bound - lower_infection_bound) * get_r()), \
           int(lower_contagion_bound + (upper_contagion_bound - lower_contagion_bound) * get_r())


def get_mortalty_rate(age):
    i = next(x for x in enumerate(list(covid_mortality_rate.keys())) if x[1] <= age / 10)
    return covid_mortality_rate[i[1]]


def flatten(list_arg):
    return [item for sublist in list_arg for item in sublist]


def invert_map(dic_arg):
    inverted_dic_arg = {}
    for k, v in dic_arg.items():
        inverted_dic_arg[v] = inverted_dic_arg.get(v, [])
        inverted_dic_arg[v].append(k)
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
