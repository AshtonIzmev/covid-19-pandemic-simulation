"""Small helpers shared by the test modules."""
from simulator.constants.keys import (
    CON_INIT_K,
    CON_K,
    DEA_INIT_K,
    DEA_K,
    HEALTHY_V,
    HOS_INIT_K,
    HOS_K,
    IMM_INIT_K,
    IMM_K,
    NC_K,
    STA_K,
    variant_hospitalization_k,
    variant_mortality_k,
)


def g_d(list_arg):
    """[a, b, c] -> {0: a, 1: b, 2: c}."""
    return dict(enumerate(list_arg))


def make_virus_dic(states, contagion=None, hospital=None, death=None, immunity=None,
                   variant_mortality=1, variant_hospitalization=1, new_cases=0):
    """Build a virus dict for `len(states)` individuals.

    Periods default to values far enough in the future that no transition fires
    on its own, so a test only has to spell out the countdowns it cares about.
    """
    n = len(states)

    def periods(given, default):
        if given is None:
            return dict.fromkeys(range(n), default)
        return dict(given) if isinstance(given, dict) else g_d(given)

    contagion_dic = periods(contagion, 5)
    hospital_dic = periods(hospital, 20)
    death_dic = periods(death, 30)
    immunity_dic = periods(immunity, 50)

    return {
        STA_K: g_d(states) if not isinstance(states, dict) else dict(states),
        CON_K: contagion_dic,
        HOS_K: hospital_dic,
        DEA_K: death_dic,
        IMM_K: immunity_dic,
        CON_INIT_K: dict(contagion_dic),
        HOS_INIT_K: dict(hospital_dic),
        DEA_INIT_K: dict(death_dic),
        IMM_INIT_K: dict(immunity_dic),
        variant_mortality_k: variant_mortality,
        variant_hospitalization_k: variant_hospitalization,
        NC_K: new_cases,
    }


def all_healthy(n):
    return [HEALTHY_V] * n


def state_counts(virus_dic):
    """{state_value: number of individuals in it}."""
    counts = {}
    for state in virus_dic[STA_K].values():
        counts[state] = counts.get(state, 0) + 1
    return counts
