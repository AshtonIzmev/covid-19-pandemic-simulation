import random
import unittest

import numpy as np

from simulator.constants.keys import (
    HA_K,
    HB_K,
    HI_K,
    HS_K,
    IAD_K,
    IAG_K,
    IBE_K,
    IDEA_K,
    IH_K,
    IHOS_K,
    IS_K,
    ISYM_K,
    ITB_K,
    ITI_K,
    IW_K,
    SI_K,
    WI_K,
    nb_1d_block_key,
    nindividual_key,
    store_nb_choice_key,
    store_per_house_key,
    transport_contact_cap_key,
)
from simulator.helper.environment import (
    build_1d_item_behavior,
    build_block_assignment,
    build_geo_positions_house,
    build_geo_positions_store,
    build_geo_positions_workplace,
    build_house_adult_map,
    build_house_store_map,
    build_individual_adult_map,
    build_individual_age_map,
    build_individual_death_rate_map,
    build_individual_hospitalization_map,
    build_individual_houses_map,
    build_individual_individual_transport_map,
    build_individual_store_map,
    build_individual_symptom_map,
    build_individual_work_map,
    build_individual_workblock_map,
    build_store_individual_map,
    get_clean_env_params,
    get_environment_simulation,
    get_environment_simulation_p,
    pick_age,
    pick_random_company_size,
)
from simulator.helper.utils import invert_map, invert_map_list
from tests.utils import g_d


class TestInitiation(unittest.TestCase):

    def setUp(self):
        random.seed(12)
        np.random.seed(seed=12)

    # ------------------------------------------------------------------ houses

    def test_build_individual_houses_map__families_are_contiguous(self):
        result = build_individual_houses_map(5)
        self.assertEqual(sorted(result), [0, 1, 2, 3, 4])
        houses = list(result.values())
        # House indices only ever go up, one family at a time.
        self.assertEqual(houses, sorted(houses))
        self.assertEqual(houses[0], 0)

    def test_build_individual_houses_map__exact_population(self):
        # The trailing family is trimmed so the population is exactly what was asked.
        for size in (1, 2, 5, 10, 37, 100):
            result = build_individual_houses_map(size)
            self.assertEqual(len(result), size)
            self.assertEqual(sorted(result), list(range(size)))

    def test_build_individual_houses_map__average_moroccan_household(self):
        result = build_individual_houses_map(5000)
        # The last house is truncated, so it is left out of the average.
        sizes = [len(v) for v in invert_map(result).values()][:-1]
        self.assertLess(abs(np.mean(sizes) - 4.52), 0.3)
        self.assertTrue(all(1 <= s <= 10 for s in sizes))

    def test_build_individual_houses_map__empty_population(self):
        self.assertEqual(build_individual_houses_map(0), {})

    # ------------------------------------------------------------------ adults

    def test_build_individual_adult_map(self):
        input_individual_houses_map = {
            0: 0, 1: 0, 2: 0, 3: 0,
            4: 1, 5: 1, 6: 1,
            7: 2, 8: 2,
            9: 3
        }
        result = build_individual_adult_map(input_individual_houses_map)
        self.assertEqual(result, {
            0: 1, 1: 1, 2: 0, 3: 0,
            4: 1, 5: 1, 6: 0,
            7: 1, 8: 1,
            9: 1
        })

    def test_build_individual_adult_map__at_most_two_adults_per_house(self):
        houses = build_individual_houses_map(400)
        adults = build_individual_adult_map(houses)
        per_house = {}
        for individual, house in houses.items():
            per_house[house] = per_house.get(house, 0) + adults[individual]
        self.assertTrue(all(0 < count <= 2 for count in per_house.values()))

    def test_build_individual_age_map__children_are_younger_than_their_parents(self):
        houses = {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1}
        ages = build_individual_age_map(houses)
        self.assertEqual(sorted(ages), sorted(houses))
        # Positions 0 and 1 of a house are the adults, the rest are children.
        for adult, child in ((0, 2), (0, 3), (1, 2), (4, 6)):
            self.assertGreaterEqual(ages[adult], ages[child])

    def test_build_individual_age_map__stays_in_the_pyramid(self):
        ages = build_individual_age_map({i: i // 5 for i in range(1000)})
        self.assertTrue(all(0 <= age <= 125 for age in ages.values()))

    def test_pick_age_ranges(self):
        for _ in range(300):
            self.assertTrue(0 <= pick_age(is_child=True) <= 34)
            self.assertTrue(20 <= pick_age(is_child=False) <= 125)

    def test_build_house_adult_map(self):
        result = build_house_adult_map(
            {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 2, 8: 2, 9: 3},
            {0: 1, 1: 1, 2: 0, 3: 0, 4: 1, 5: 1, 6: 0, 7: 1, 8: 1, 9: 1})
        self.assertEqual(result, {0: [0, 1], 1: [4, 5], 2: [7, 8], 3: [9]})

    def test_build_house_adult_map__house_without_adult_is_still_listed(self):
        # propagate_to_stores indexes houses by position, so no house may go missing.
        self.assertEqual(build_house_adult_map({0: 0, 1: 0}, {0: 0, 1: 0}), {0: []})

    # ------------------------------------------------------------------ stores

    def test_build_house_store_map(self):
        geo_position_store = [(6, 6), (5, 5), (4, 4), (3, 3), (2, 2), (1, 1)]
        geo_position_house = [(6.1, 6.2), (5.1, 5.2), (4.1, 4.2), (3.1, 3.2), (2.1, 2.2), (1.1, 1.2)]
        result = build_house_store_map(geo_position_store, geo_position_house, 3)
        self.assertEqual(result, {0: [0, 1, 2],
                                  1: [1, 0, 2],
                                  2: [2, 1, 3],
                                  3: [3, 2, 4],
                                  4: [4, 3, 5],
                                  5: [5, 4, 3]})

    def test_build_house_store_map__nearest_store_comes_first(self):
        stores = [(0.0, 0.0), (1.0, 1.0), (0.5, 0.5)]
        result = build_house_store_map(stores, [(0.05, 0.05), (0.95, 0.95)], 3)
        self.assertEqual(result[0][0], 0)
        self.assertEqual(result[1][0], 1)

    def test_build_indiv_store_map(self):
        ind_hou = g_d([0, 0, 0, 0, 1, 1, 1, 1, 2, 2])
        hou_sto = g_d([[0, 1, 2], [1, 2, 3], [4, 5, 3]])
        result = build_individual_store_map(ind_hou, hou_sto)
        self.assertEqual(result, {0: [0, 1, 2], 1: [0, 1, 2], 2: [0, 1, 2], 3: [0, 1, 2],
                                  4: [1, 2, 3], 5: [1, 2, 3], 6: [1, 2, 3], 7: [1, 2, 3],
                                  8: [4, 5, 3], 9: [4, 5, 3]})

    def test_build_store_individual_map(self):
        result = build_store_individual_map({0: [0, 1, 2], 1: [2, 3, 4]})
        self.assertEqual(result, {0: [0], 1: [0], 2: [0, 1], 3: [1], 4: [1]})

    def test_build_store_individual_map2(self):
        result = build_store_individual_map({0: [0, 1], 1: [3, 4]})
        self.assertEqual(result, {0: [0], 1: [0], 3: [1], 4: [1]})

    # --------------------------------------------------------------- workplaces

    def test_build_individual_work_map__only_adults_get_a_job(self):
        adults = {0: 1, 1: 1, 2: 0, 3: 0, 4: 1, 5: 1, 6: 0, 7: 1, 8: 1, 9: 1}
        result = build_individual_work_map(adults)
        self.assertEqual(sorted(result), [i for i, is_adult in adults.items() if is_adult == 1])

    def test_build_individual_work_map__company_sizes_stay_in_range(self):
        workplaces = invert_map(build_individual_work_map(dict.fromkeys(range(600), 1)))
        self.assertTrue(all(1 <= len(staff) <= 50 for staff in workplaces.values()))
        self.assertEqual(sum(len(s) for s in workplaces.values()), 600)

    def test_build_individual_work_map__no_adult(self):
        self.assertEqual(build_individual_work_map({0: 0, 1: 0}), {})

    def test_pick_random_company_size(self):
        sizes = [pick_random_company_size() for _ in range(3000)]
        self.assertTrue(all(1 <= s <= 50 for s in sizes))
        # The distribution is dominated by very small companies (44% TPE).
        self.assertGreater(sum(1 for s in sizes if s <= 3) / len(sizes), 0.35)

    # ---------------------------------------------------------------- geography

    def test_geo_builders_stay_in_the_unit_square(self):
        for builder in (build_geo_positions_house, build_geo_positions_store, build_geo_positions_workplace):
            positions = builder(200)
            self.assertEqual(len(positions), 200)
            self.assertTrue(all(0 <= x <= 1 and 0 <= y <= 1 for x, y in positions))

    def test_build_block_assignment(self):
        result = build_block_assignment([(0.0, 0.0), (0.5, 0.99), (0.99, 0.5)], 10)
        self.assertEqual(result, [(0, 0), (5, 9), (9, 5)])

    def test_build_block_assignment__indices_stay_inside_the_grid(self):
        blocks = build_block_assignment(build_geo_positions_house(500), 20)
        self.assertTrue(all(0 <= i < 20 and 0 <= j < 20 for i, j in blocks))

    # ---------------------------------------------------------------- transport

    def test_build_individual_work_blocks(self):
        result = build_individual_workblock_map(
            {0: 0, 1: 0, 2: 1, 3: 1}, {0: 0, 1: 1, 2: 0, 3: 1},
            [(2, 3), (7, 8)], [(3, 1), (9, 5)]
        )
        expected = {
            0: [(2, 3), (2, 2), (2, 1), (3, 1)],
            1: [(2, 3), (2, 4), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5)],
            2: [(7, 8), (7, 7), (7, 6), (7, 5), (7, 4), (7, 3), (7, 2), (7, 1), (6, 1), (5, 1), (4, 1), (3, 1)],
            3: [(7, 8), (7, 7), (7, 6), (7, 5), (8, 5), (9, 5)]
        }
        self.assertEqual(result, expected)

    def test_build_individual_individual_transport_map(self):
        ind_workblock = {
            0: [(1, 1), (1, 2), (1, 3), (2, 3)],
            1: [(0, 3), (1, 3), (1, 4), (1, 5)],
            2: [(0, 1), (0, 2), (1, 2), (2, 2)],
            3: [(8, 8), (8, 7), (7, 7)]
        }
        result = build_individual_individual_transport_map(ind_workblock, invert_map_list(ind_workblock), 10)
        self.assertEqual(result, {0: {0, 1, 2}, 1: {0, 1}, 2: {0, 2}, 3: {3}})

    def test_build_individual_individual_transport_map__respects_the_cap(self):
        # Everybody shares the same single block, so the cap is what limits contacts.
        ind_workblock = {i: [(0, 0)] for i in range(50)}
        result = build_individual_individual_transport_map(ind_workblock, invert_map_list(ind_workblock), 4)
        self.assertTrue(all(len(contacts) <= 4 for contacts in result.values()))

    def test_build_individual_individual_transport_map__no_commuter(self):
        self.assertEqual(build_individual_individual_transport_map({}, {}, 10), {})

    # ----------------------------------------------------------------- behavior

    def test_build_1d_item_behavior_bounds(self):
        result = build_1d_item_behavior(500)
        self.assertEqual(sorted(result), list(range(500)))
        self.assertTrue(all(0.5 <= v <= 1.5 for v in result.values()))

    def test_build_1d_item_behavior_mean(self):
        result = build_1d_item_behavior(5000)
        self.assertLess(abs(np.mean(list(result.values())) - 1), 0.05)

    # -------------------------------------------------------------------- rates

    def test_build_individual_death_rate_map(self):
        result = build_individual_death_rate_map(g_d([0, 10, 20, 30, 40, 50, 60, 70, 80]))
        self.assertEqual(result, g_d([0, 0.02, 0.02, 0.02, 0.04, 0.013, 0.036, 0.08, 0.148]))

    def test_build_individual_hospitalization_map(self):
        result = build_individual_hospitalization_map(g_d([0, 10, 20, 30, 40, 50, 60, 70, 80]))
        self.assertEqual(result, g_d([0.03, 0.01, 0.025, 0.025, 0.025, 0.074, 0.122, 0.158, 0.172]))

    def test_build_individual_symptom_map(self):
        result = build_individual_symptom_map(g_d([0, 10, 20, 30, 40, 50, 60, 70, 80]))
        self.assertEqual(result, g_d([0.0, 0.009045000000000001, 0.02241, 0.033615, 0.06108, 0.07635,
                                      0.12411, 0.12411, 0.25823999999999997]))

    def test_rate_maps_cover_exactly_the_population(self):
        ages = g_d([5, 25, 45, 65, 85])
        for builder in (build_individual_death_rate_map, build_individual_hospitalization_map,
                        build_individual_symptom_map):
            self.assertEqual(sorted(builder(ages)), sorted(ages))

    # --------------------------------------------------------- whole environment

    def test_get_clean_env_params(self):
        params = {nindividual_key: 1000, store_per_house_key: 20, nb_1d_block_key: 20,
                  store_nb_choice_key: 3, transport_contact_cap_key: 10}
        clean, key = get_clean_env_params(params)
        self.assertEqual(clean, {"number_of_individuals": 1000, "number_store_per_house": 20,
                                 "nb_1d_block": 20, "nb_store_choice": 3, "transportation_cap": 10})
        self.assertEqual(key, "1000-20-20-3-10")

    def test_get_clean_env_params__key_only_depends_on_structural_parameters(self):
        base = {nindividual_key: 500, store_per_house_key: 20, nb_1d_block_key: 20,
                store_nb_choice_key: 3, transport_contact_cap_key: 10}
        other = dict(base, PROB_HOUSE_INFECTION=0.9)
        self.assertEqual(get_clean_env_params(base)[1], get_clean_env_params(other)[1])

    def test_get_environment_simulation_is_complete_and_consistent(self):
        params = {nindividual_key: 300, store_per_house_key: 5, nb_1d_block_key: 5,
                  store_nb_choice_key: 3, transport_contact_cap_key: 10}
        env = get_environment_simulation(params)

        for key in (IH_K, HI_K, IAD_K, IAG_K, IDEA_K, IHOS_K, ISYM_K, IW_K, WI_K,
                    HA_K, HS_K, IS_K, SI_K, ITB_K, ITI_K, HB_K, IBE_K):
            self.assertIn(key, env, f"{key} missing from the environment")

        population = list(range(300))
        for key in (IH_K, IAD_K, IAG_K, IDEA_K, IHOS_K, ISYM_K, IS_K, IBE_K):
            self.assertEqual(sorted(env[key]), population, f"{key} does not cover the population")

        # Cross-references must resolve both ways.
        for individual, house in env[IH_K].items():
            self.assertIn(individual, env[HI_K][house])
        for individual, workplace in env[IW_K].items():
            self.assertIn(individual, env[WI_K][workplace])
        for house, adults in env[HA_K].items():
            for adult in adults:
                self.assertEqual(env[IH_K][adult], house)
                self.assertEqual(env[IAD_K][adult], 1)

        self.assertEqual(len(env[HB_K]), len(env[HI_K]))
        self.assertTrue(set(env[IW_K]).issubset(population))
        self.assertTrue(all(len(stores) == 3 for stores in env[IS_K].values()))

    def test_environment_keys_do_not_collide(self):
        # IDEA_K and DEA_K used to be the very same string.
        from simulator.constants import keys
        names = [n for n in dir(keys) if n.endswith("_K") or n.endswith("_key")]
        values = [getattr(keys, n) for n in names]
        self.assertEqual(len(values), len(set(values)), "two key constants share a value")

    def test_get_environment_simulation_p_matches_the_params_wrapper(self):
        params = {nindividual_key: 120, store_per_house_key: 5, nb_1d_block_key: 4,
                  store_nb_choice_key: 2, transport_contact_cap_key: 6}
        random.seed(7)
        np.random.seed(7)
        from_params = get_environment_simulation(params)
        random.seed(7)
        np.random.seed(7)
        from_clean = get_environment_simulation_p(get_clean_env_params(params)[0])
        self.assertEqual(from_params[IH_K], from_clean[IH_K])
        self.assertEqual(from_params[IAG_K], from_clean[IAG_K])


if __name__ == '__main__':
    unittest.main()
