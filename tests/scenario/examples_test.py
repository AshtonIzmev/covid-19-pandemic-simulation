import random
import unittest
import ray
import numpy as np
import logging
from scenario.example import scx_base_just_a_flu, sc0_base_lockdown, sc1_simple_lockdown_removal, \
    sc2_yoyo_lockdown_removal, sc3_loose_lockdown, sc4_rogue_citizen, sc5_rogue_neighborhood, sc6_travelers, sc9_vaccination
from simulator.constants.keys import nindividual_key, nday_key, additional_scenario_params_key
from simulator.helper.environment import get_environment_simulation
from simulator.helper.simulation import get_default_params
from scenario.helper.progressbar import ProgressBar


class TestScenarios(unittest.TestCase):

    @classmethod
    def setUp(cls):
        random.seed(12)
        np.random.seed(seed=12)

    @classmethod
    def setUpClass(cls):
        ray.init(include_dashboard=False, logging_level=logging.ERROR)

    def test_scx_base_just_a_flu(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        env_dic = get_environment_simulation(params)
        ray_params = ray.put(params)
        ray_env_dic = ray.put(env_dic)
        pb = ProgressBar(params[nday_key])
        actor = pb.actor
        stats_l = [scx_base_just_a_flu.do_parallel_run.remote(ray_env_dic, ray_params, 0, 0, actor)]
        self.assertTrue(len(stats_l) > 0)

    def test_sc0_base_lockdown(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        env_dic = get_environment_simulation(params)
        ray_params = ray.put(params)
        ray_env_dic = ray.put(env_dic)
        pb = ProgressBar(params[nday_key])
        actor = pb.actor
        stats_l = [sc0_base_lockdown.do_parallel_run.remote(ray_env_dic, ray_params, 0, 0, actor)]
        self.assertTrue(len(stats_l) > 0)

    def test_sc1_simple_lockdown_removal(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        params[additional_scenario_params_key] = [14]
        env_dic = get_environment_simulation(params)
        ray_params = ray.put(params)
        ray_env_dic = ray.put(env_dic)
        pb = ProgressBar(params[nday_key])
        actor = pb.actor
        stats_l = [sc1_simple_lockdown_removal.do_parallel_run.remote(ray_env_dic, ray_params, 0, 0, actor)]
        self.assertTrue(len(stats_l) > 0)

    def test_sc2_yoyo_lockdown_removal(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        params[additional_scenario_params_key] = [14, 2, 7]
        env_dic = get_environment_simulation(params)
        ray_params = ray.put(params)
        ray_env_dic = ray.put(env_dic)
        pb = ProgressBar(params[nday_key])
        actor = pb.actor
        stats_l = [sc2_yoyo_lockdown_removal.do_parallel_run.remote(ray_env_dic, ray_params, 0, 0, actor)]
        self.assertTrue(len(stats_l) > 0)

    def test_sc3_loose_lockdown(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        params[additional_scenario_params_key] = [14]
        env_dic = get_environment_simulation(params)
        ray_params = ray.put(params)
        ray_env_dic = ray.put(env_dic)
        pb = ProgressBar(params[nday_key])
        actor = pb.actor
        stats_l = [sc3_loose_lockdown.do_parallel_run.remote(ray_env_dic, ray_params, 0, 0, actor)]
        self.assertTrue(len(stats_l) > 0)

    def test_sc4_rogue_citizen(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        params[additional_scenario_params_key] = [5, 10]
        env_dic = get_environment_simulation(params)
        ray_params = ray.put(params)
        ray_env_dic = ray.put(env_dic)
        pb = ProgressBar(params[nday_key])
        actor = pb.actor
        stats_l = [sc4_rogue_citizen.do_parallel_run.remote(ray_env_dic, ray_params, 0, 0, actor)]
        self.assertTrue(len(stats_l) > 0)

    def test_sc5_rogue_neighborhood(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        params[additional_scenario_params_key] = [4, 2]
        env_dic = get_environment_simulation(params)
        ray_params = ray.put(params)
        ray_env_dic = ray.put(env_dic)
        pb = ProgressBar(params[nday_key])
        actor = pb.actor
        stats_l = [sc5_rogue_neighborhood.do_parallel_run.remote(ray_env_dic, ray_params, 0, 0, actor)]
        self.assertTrue(len(stats_l) > 0)

    def test_sc6_travelers(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        params[additional_scenario_params_key] = [5]
        env_dic = get_environment_simulation(params)
        ray_params = ray.put(params)
        ray_env_dic = ray.put(env_dic)
        pb = ProgressBar(params[nday_key])
        actor = pb.actor
        stats_l = [sc6_travelers.do_parallel_run.remote(ray_env_dic, ray_params, 0, 0, actor)]
        self.assertTrue(len(stats_l) > 0)

    def test_sc9_variant(self):
        params = get_default_params()
        params[nindividual_key] = 100
        params[nday_key] = 30
        params[additional_scenario_params_key] = [-1]
        env_dic = get_environment_simulation(params)
        ray_params = ray.put(params)
        ray_env_dic = ray.put(env_dic)
        pb = ProgressBar(params[nday_key])
        actor = pb.actor
        stats_l = [sc9_vaccination.do_parallel_run.remote(ray_env_dic, ray_params, 0, 0, actor)]
        self.assertTrue(len(stats_l) > 0)


if __name__ == '__main__':
    unittest.main()
