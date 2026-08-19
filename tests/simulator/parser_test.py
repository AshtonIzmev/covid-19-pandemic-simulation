import random
import unittest

from simulator.constants.keys import (
    additional_scenario_params_key,
    contagion_bounds_key,
    draw_graph_key,
    house_infect_key,
    immunity_bounds_key,
    ncpu_key,
    nday_key,
    nindividual_key,
    nrun_key,
    nvariant_key,
    random_seed_key,
    scenario_id_key,
    show_plot_key,
    store_preference_key,
)
from simulator.helper.parser import get_parser, parse_params
from simulator.helper.simulation import get_default_params


class TestParser(unittest.TestCase):

    def test_no_argument_leaves_every_default_in_place(self):
        self.assertEqual(parse_params([]), get_default_params())

    def test_arguments_override_the_defaults(self):
        params = parse_params(["--nind", "250", "--nday", "42", "--nrun", "7"])
        self.assertEqual(params[nindividual_key], 250)
        self.assertEqual(params[nday_key], 42)
        self.assertEqual(params[nrun_key], 7)

    def test_typed_arguments_keep_their_type(self):
        params = parse_params(["--nind", "250", "--p-house", "0.25", "--sto-pref", "0.5"])
        self.assertIsInstance(params[nindividual_key], int)
        self.assertEqual(params[house_infect_key], 0.25)
        self.assertEqual(params[store_preference_key], 0.5)

    def test_bounds_arguments_take_two_values(self):
        params = parse_params(["--contagion-bounds", "3", "9", "--immunity-bounds", "120", "150"])
        self.assertEqual(params[contagion_bounds_key], [3, 9])
        self.assertEqual(params[immunity_bounds_key], [120, 150])

    def test_draw_accepts_several_graph_names(self):
        params = parse_params(["--draw", "exa", "pop", "summ", "R0"])
        self.assertEqual(params[draw_graph_key], ["exa", "pop", "summ", "R0"])

    def test_show_plot_is_a_flag(self):
        self.assertFalse(parse_params([])[show_plot_key])
        self.assertTrue(parse_params(["--show-plot"])[show_plot_key])

    def test_extra_scenario_params_are_kept_as_strings(self):
        params = parse_params(["--extra-scenario-params", "14", "MH", "True"])
        self.assertEqual(params[additional_scenario_params_key], ["14", "MH", "True"])

    def test_scenario_id_has_a_short_alias(self):
        self.assertEqual(parse_params(["--scenario-id", "3"])[scenario_id_key], 3)
        self.assertEqual(parse_params(["--sce", "3"])[scenario_id_key], 3)

    def test_scenario_id_accepts_the_negative_baseline(self):
        self.assertEqual(parse_params(["--sce", "-1"])[scenario_id_key], -1)

    def test_ncpu_accepts_a_negative_value(self):
        self.assertEqual(parse_params(["--ncpu", "-2"])[ncpu_key], -2)

    def test_nvariant(self):
        self.assertEqual(parse_params(["--nvariant", "8"])[nvariant_key], 8)

    def test_parse_params_seeds_the_random_generators(self):
        parse_params(["--random-seed", "123"])
        first = [random.random() for _ in range(5)]
        parse_params(["--random-seed", "123"])
        self.assertEqual(first, [random.random() for _ in range(5)])

    def test_parse_params_reports_the_seed_it_used(self):
        self.assertEqual(parse_params(["--random-seed", "123"])[random_seed_key], 123)

    def test_unknown_argument_is_rejected(self):
        with self.assertRaises(SystemExit):
            get_parser().parse_args(["--not-a-real-option", "1"])

    def test_every_parser_destination_is_a_known_parameter(self):
        # A typo in a `dest=` would silently make the option a no-op.
        defaults = get_default_params()
        destinations = {action.dest for action in get_parser()._actions if action.dest != "help"}
        self.assertEqual(destinations - set(defaults), set())


if __name__ == '__main__':
    unittest.main()
