import random

from scipy.stats import truncnorm


def invert_map_list(dic_arg):
    inverted_dic_arg = {}
    for k, v in dic_arg.items():
        for el in v:
            inverted_dic_arg[el] = inverted_dic_arg.get(el, [])
            inverted_dic_arg[el].append(k)
    return inverted_dic_arg


def invert_map(dic_arg):
    inverted_dic_arg = {}
    for k, v in dic_arg.items():
        inverted_dic_arg[v] = inverted_dic_arg.get(v, [])
        inverted_dic_arg[v].append(k)
    return inverted_dic_arg


def flatten(list_arg):
    return [item for sublist in list_arg for item in sublist]


def get_random_sample(iterable_arg, cap):
    return random.sample(iterable_arg, min(cap, len(iterable_arg)))


def get_r():
    return random.random()


def get_center_squized_random():
    u = get_r()
    return 4 * (u - 0.5) * (u - 0.5) * (u - 0.5) + 0.5


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


def rec_get_manhattan_walk(result, p1, p2):
    # Recursive Manhattan walk
    i, j = p1
    k, l = p2
    if i == k and j == l:
        return result + [p1]
    if j == l:
        if i < k:
            return rec_get_manhattan_walk(result + [p1], (i + 1, j), (k, l))
        else:
            return rec_get_manhattan_walk(result + [p1], (i - 1, j), (k, l))
    else:
        if j < l:
            return rec_get_manhattan_walk(result + [p1], (i, j + 1), (k, l))
        else:
            return rec_get_manhattan_walk(result + [p1], (i, j - 1), (k, l))


def get_random_choice_list(list_of_list_arg):
    return [li[int(get_r()*len(li))] for li in list_of_list_arg if len(li) > 0]


def get_clipped_gaussian_number(lower_clip_arg, upper_clip_arg, mean_arg, std_arg):
    a, b = (lower_clip_arg - mean_arg) / std_arg, (upper_clip_arg - mean_arg) / std_arg
    return truncnorm.rvs(a, b, loc=mean_arg, scale=std_arg)