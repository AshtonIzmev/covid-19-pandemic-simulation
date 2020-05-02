import random
import unittest

import numpy as np

from scenario.example import scx_base_just_a_flu, sc0_base_lockdown, sc1_simple_lockdown_removal, \
    sc2_yoyo_lockdown_removal, sc3_loose_lockdown, sc4_rogue_citizen, sc5_rogue_neighborhood, sc6_travelers
from simulator.constants.keys import nindividual_key, nday_key, additional_scenario_params_key
from simulator.helper.environment import get_environment_simulation
from simulator.helper.simulation import get_default_params


class TestScenarios(unittest.TestCase):

    @classmethod
    def setUp(cls):
        random.seed(12)
        np.random.seed(seed=12)

    def test_scx_base_just_a_flu(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        env_dic = get_environment_simulation(params)
        stats_result = scx_base_just_a_flu.launch_run(params, env_dic, display_progress=False)
        self.assertTrue(len(stats_result) > 0)

    def test_sc0_base_lockdown(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        env_dic = get_environment_simulation(params)
        stats_result = sc0_base_lockdown.launch_run(params, env_dic, display_progress=False)
        self.assertTrue(len(stats_result) > 0)

    def test_sc1_simple_lockdown_removal(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        params[additional_scenario_params_key] = [14]
        env_dic = get_environment_simulation(params)
        stats_result = sc1_simple_lockdown_removal.launch_run(params, env_dic, display_progress=False)
        self.assertTrue(len(stats_result) > 0)

    def test_sc2_yoyo_lockdown_removal(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        params[additional_scenario_params_key] = [14, 2, 7]
        env_dic = get_environment_simulation(params)
        stats_result = sc2_yoyo_lockdown_removal.launch_run(params, env_dic, display_progress=False)
        self.assertTrue(len(stats_result) > 0)

    def test_sc3_loose_lockdown(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        params[additional_scenario_params_key] = [14]
        env_dic = get_environment_simulation(params)
        stats_result = sc3_loose_lockdown.launch_run(params, env_dic, display_progress=False)
        self.assertTrue(len(stats_result) > 0)

    def test_sc4_rogue_citizen(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        params[additional_scenario_params_key] = [5, 10]
        env_dic = get_environment_simulation(params)
        stats_result = sc4_rogue_citizen.launch_run(params, env_dic, display_progress=False)
        self.assertTrue(len(stats_result) > 0)

    def test_sc5_rogue_neighborhood(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        params[additional_scenario_params_key] = [4, 2]
        env_dic = get_environment_simulation(params)
        stats_result = sc5_rogue_neighborhood.launch_run(params, env_dic, display_progress=False)
        self.assertTrue(len(stats_result) > 0)

    def test_sc6_travelers(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        params[additional_scenario_params_key] = [5]
        env_dic = get_environment_simulation(params)
        stats_result = sc6_travelers.launch_run(params, env_dic, display_progress=False)
        self.assertTrue(len(stats_result) > 0)


if __name__ == '__main__':
    unittest.main()
