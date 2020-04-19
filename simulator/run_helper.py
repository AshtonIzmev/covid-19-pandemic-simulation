import argparse

from simulator.parameters import *


def get_parser():
    parser = argparse.ArgumentParser(description='Please feed model parameters')

    parser.add_argument('--nrun', type=int, help='Number of simulations', dest=nrun_key)
    parser.add_argument('--random-seed', type=int, help='Random seed', dest=random_seed_key)

    parser.add_argument('--nind', type=int, help='Number of individuals', dest=nindividual_key)
    parser.add_argument('--nday', type=int, help='Number of days', dest=nday_key)

    parser.add_argument('--sto-house', type=int, help='Number of store per house', dest=store_per_house_key)
    parser.add_argument('--nblock', type=int, help='Number of blocks in the grid', dest=nb_block_key)

    parser.add_argument('--remote-work', type=float, help='Percentage of people remote working', dest=remote_work_key)

    parser.add_argument('--sto-pref', type=float, help='Probability going to nearest store', dest=store_preference_key)
    parser.add_argument('--p-same-house', type=float, help='"Probability" for individuals for living in the same house'
                        , dest=same_house_p_key)
    parser.add_argument('--inn-infec', type=float, help='Initial innoculation percentage',
                        dest=innoculation_number_key)

    parser.add_argument('--p-house', type=float, help='Probability of house infection', dest=house_infect_key)
    parser.add_argument('--p-store', type=float, help='Probability of store infection', dest=store_infection_key)
    parser.add_argument('--p-work', type=float, help='Probability of workplace infection', dest=work_infection_key)

    parser.add_argument('--contagion-bounds', type=int, nargs=2, help='Contagion bounds', dest=contagion_bounds_key)
    parser.add_argument('--hospitalization-bounds', type=int, nargs=2, help='Hospitalization bounds',
                        dest=hospitalization_bounds_key)
    parser.add_argument('--death-bounds', type=int, nargs=2, help='Death bounds', dest=death_bounds_key)
    parser.add_argument('--immunity-bounds', type=int, nargs=2, help='Immunity bounds', dest=immunity_bounds_key)

    parser.add_argument('--scenario-id', "--sce", type=int, help='Immunity bounds', dest=scenario_id_key)

    parser.add_argument('--population-state', '--pop', help='Draw population state graph', action='store_true')
    parser.add_argument('--hospitalized-cases', '--hos', help='Draw hospitalized cases graph', action='store_true')
    parser.add_argument('--new-cases', '--new', help='Draw new cases graph', action='store_true')
    parser.add_argument('--summary', '--sum', help='Draw a pandemic summary', action='store_true')
    parser.add_argument('--examples', '--exa', help='Draw the most different pandemic evolution examples',
                        action='store_true')
    parser.add_argument('--all-plots', '--all', help='Draw all plots in a single pass', action='store_true')

    parser.add_argument('--days-lockdown-removal', type=int, help='Number of days to lockdown removal',
                        dest=days_wait_lockdown_removal)

    return parser
