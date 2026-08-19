import argparse
import random

from simulator.constants.keys import (
    additional_scenario_params_key,
    contagion_bounds_key,
    death_bounds_key,
    draw_graph_key,
    hospitalization_bounds_key,
    house_infect_key,
    icu_bed_per_thousand_individual_key,
    immunity_bounds_key,
    innoculation_number_key,
    nb_1d_block_key,
    ncpu_key,
    nday_key,
    nindividual_key,
    nrun_key,
    nvariant_key,
    random_seed_key,
    remote_work_key,
    scenario_id_key,
    show_plot_key,
    store_infection_key,
    store_nb_choice_key,
    store_per_house_key,
    store_preference_key,
    transport_contact_cap_key,
    transport_infection_key,
    work_infection_key,
)


def get_parser():
    parser = argparse.ArgumentParser(description='Please feed model parameters')

    parser.add_argument('--nrun', type=int, help='Number of simulations', dest=nrun_key)
    parser.add_argument('--random-seed', type=int, help='Random seed', dest=random_seed_key)

    parser.add_argument('--ncpu', type=int, help='Number of cpus to use (-1 is all but one)', dest=ncpu_key)

    parser.add_argument('--nind', type=int, help='Number of individuals', dest=nindividual_key)
    parser.add_argument('--nday', type=int, help='Number of days', dest=nday_key)
    parser.add_argument('--nvariant', type=int, help='Number of variants', dest=nvariant_key)

    parser.add_argument('--sto-house', type=int, help='Number of store per house', dest=store_per_house_key)
    parser.add_argument('--nblock', type=int, help='Number of blocks in the grid', dest=nb_1d_block_key)

    parser.add_argument('--remote-work', type=float, help='Percentage of people remote working', dest=remote_work_key)

    parser.add_argument('--sto-pref', type=float, help='Probability going to nearest store', dest=store_preference_key)
    parser.add_argument('--sto-nb', type=int, help='Number of nearest stores to consider', dest=store_nb_choice_key)

    parser.add_argument('--inn-infec', type=float, dest=innoculation_number_key,
                        help='Number of individuals infected at day 0')

    parser.add_argument('--p-house', type=float, help='Probability of house infection', dest=house_infect_key)
    parser.add_argument('--p-store', type=float, help='Probability of store infection', dest=store_infection_key)
    parser.add_argument('--p-work', type=float, help='Probability of workplace infection', dest=work_infection_key)
    parser.add_argument('--p-transport', type=float, help='Probability of public transportation infection',
                        dest=transport_infection_key)
    parser.add_argument('--transport-contact-cap', type=int,
                        help='Number of people an individual is close when commuting', dest=transport_contact_cap_key)

    parser.add_argument('--contagion-bounds', type=int, nargs=2, help='Contagion bounds', dest=contagion_bounds_key)
    parser.add_argument('--hospitalization-bounds', type=int, nargs=2, help='Hospitalization bounds',
                        dest=hospitalization_bounds_key)
    parser.add_argument('--death-bounds', type=int, nargs=2, help='Death bounds', dest=death_bounds_key)
    parser.add_argument('--immunity-bounds', type=int, nargs=2, help='Immunity bounds', dest=immunity_bounds_key)

    parser.add_argument('--nbeds-icu', type=float, help='Number of ICU beds per thousand population',
                        dest=icu_bed_per_thousand_individual_key)

    parser.add_argument('--scenario-id', "--sce", type=int, dest=scenario_id_key,
                        help='Scenario to run, see the scenario.example package')
    parser.add_argument('--draw', type=str, nargs="*",
                        help='Draw one or more graphs, named by a prefix of their key. Choose from '
                             '"population", "new", "hospital", "summary", "example", "lockdown", '
                             '"R0", "R0d" and "metasimu"',
                        dest=draw_graph_key)
    parser.add_argument('--show-plot', dest=show_plot_key, action='store_true',
                        help='Show the plots in a window instead of writing them to images/output')

    # Scenarios related
    parser.add_argument('--extra-scenario-params', type=str, nargs="*", help='Additional scenario parameters',
                        dest=additional_scenario_params_key)

    return parser


def parse_params(argv=None):
    """Overlay the command line onto the default parameters and seed the RNGs."""
    import numpy

    from simulator.helper.simulation import get_default_params

    params = get_default_params()
    args = get_parser().parse_args(argv)
    for arg in vars(args):
        value = getattr(args, arg)
        if arg in params and value is not None:
            params[arg] = value
    random.seed(params[random_seed_key])
    numpy.random.seed(params[random_seed_key])
    return params
