import argparse

from simulator.constants.keys import nrun_key, scenario_id_key, random_seed_key, draw_graph_key, nindividual_key, \
    nday_key, \
    innoculation_number_key, nb_1d_block_key, remote_work_key, store_per_house_key, store_preference_key, \
    store_nb_choice_key, house_infect_key, work_infection_key, store_infection_key, transport_infection_key, \
    transport_contact_cap_key, contagion_bounds_key, hospitalization_bounds_key, death_bounds_key, immunity_bounds_key, \
    icu_bed_per_thousand_individual_key, additional_scenario_params_key


def get_parser():
    parser = argparse.ArgumentParser(description='Please feed model parameters')

    parser.add_argument('--nrun', type=int, help='Number of simulations', dest=nrun_key)
    parser.add_argument('--random-seed', type=int, help='Random seed', dest=random_seed_key)

    parser.add_argument('--nind', type=int, help='Number of individuals', dest=nindividual_key)
    parser.add_argument('--nday', type=int, help='Number of days', dest=nday_key)

    parser.add_argument('--sto-house', type=int, help='Number of store per house', dest=store_per_house_key)
    parser.add_argument('--nblock', type=int, help='Number of blocks in the grid', dest=nb_1d_block_key)

    parser.add_argument('--remote-work', type=float, help='Percentage of people remote working', dest=remote_work_key)

    parser.add_argument('--sto-pref', type=float, help='Probability going to nearest store', dest=store_preference_key)
    parser.add_argument('--sto-nb', type=int, help='Number of nearest stores to consider', dest=store_nb_choice_key)

    parser.add_argument('--inn-infec', type=float, help='Initial innoculation percentage', dest=innoculation_number_key)

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

    parser.add_argument('--nbeds-icu', type=int, help='Number of ICU beds per thousand population',
                        dest=icu_bed_per_thousand_individual_key)

    parser.add_argument('--scenario-id', "--sce", type=int, help='Immunity bounds', dest=scenario_id_key)
    parser.add_argument('--draw', type=str, nargs="*",
                        help='Draw a kind of graph by specifying at least the first 3 letters of its keys. '
                             'Choose from "example", "hospital", "new", "summary", "population", "lockdown" and more',
                        dest=draw_graph_key)

    # Scenarios related
    parser.add_argument('--extra-scenario-params', type=float, nargs="*", help='Additional scenario parameters',
                        dest=additional_scenario_params_key)

    return parser
