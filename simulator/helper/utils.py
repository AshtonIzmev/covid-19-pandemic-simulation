import random

from scipy.stats import truncnorm


def invert_map_list(dic_arg):
    """{k: [v1, v2]} -> {v1: [k], v2: [k]}, appending on collision."""
    inverted_dic_arg = {}
    for k, v in dic_arg.items():
        for el in v:
            inverted_dic_arg.setdefault(el, []).append(k)
    return inverted_dic_arg


def invert_map(dic_arg):
    """{k: v} -> {v: [k]}, appending on collision."""
    inverted_dic_arg = {}
    for k, v in dic_arg.items():
        inverted_dic_arg.setdefault(v, []).append(k)
    return inverted_dic_arg


def get_random_sample(iterable_arg, cap):
    # random.sample() has required a sequence since python 3.11, so sets and
    # dict views (which callers do pass) have to be materialised first.
    population = iterable_arg if isinstance(iterable_arg, (list, tuple)) else list(iterable_arg)
    return random.sample(population, min(cap, len(population)))


def get_r():
    return random.random()


def get_center_squized_random():
    u = get_r()
    return 4 * (u - 0.5) * (u - 0.5) * (u - 0.5) + 0.5


def reduce_multiply_by_key(tuple_list):
    """[(k, v), (k, w)] -> {k: v * w}."""
    result_dic = {}
    for (k, v) in tuple_list:
        result_dic[k] = v * result_dic.get(k, 1)
    return result_dic


def choose_weight_order(list_arg, prob):
    """Walk the list and return the first item that wins a `prob` draw, last one otherwise."""
    try:
        return next(x[1] for x in enumerate(list_arg) if get_r() <= prob)
    except StopIteration:
        return list_arg[-1]


def rec_get_manhattan_walk(result, p1, p2):
    # Recursive Manhattan walk
    i, j = p1
    k, m = p2
    if i == k and j == m:
        return result + [p1]
    if j == m:
        if i < k:
            return rec_get_manhattan_walk(result + [p1], (i + 1, j), (k, m))
        else:
            return rec_get_manhattan_walk(result + [p1], (i - 1, j), (k, m))
    else:
        if j < m:
            return rec_get_manhattan_walk(result + [p1], (i, j + 1), (k, m))
        else:
            return rec_get_manhattan_walk(result + [p1], (i, j - 1), (k, m))


def get_random_choice_list(list_of_list_arg):
    return [li[int(get_r() * len(li))] for li in list_of_list_arg if len(li) > 0]


def get_clipped_gaussian_number(lower_clip_arg, upper_clip_arg, mean_arg, std_arg):
    a, b = (lower_clip_arg - mean_arg) / std_arg, (upper_clip_arg - mean_arg) / std_arg
    return float(truncnorm.rvs(a, b, loc=mean_arg, scale=std_arg))
