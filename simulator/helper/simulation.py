from simulator.constants.keys import *
from simulator.constants.keys import nrun_key, scenario_id_key, random_seed_key, draw_graph_key, nindividual_key, \
    nday_key, \
    innoculation_number_key, nb_1d_block_key, quarantine_days_key, remote_work_key, store_per_house_key, \
    store_preference_key, store_nb_choice_key, house_infect_key, work_infection_key, store_infection_key, \
    transport_infection_key, transport_contact_cap_key, contagion_bounds_key, hospitalization_bounds_key, \
    death_bounds_key, immunity_bounds_key, icu_bed_per_thousand_individual_key, additional_scenario_params_key
from simulator.helper.utils import get_r


def get_virus_simulation_t0(params_arg):
    number_of_individuals_arg = params_arg[nindividual_key]
    infection_initialization_number_arg = params_arg[innoculation_number_key]
    contagion_bound_args = params_arg[contagion_bounds_key]
    hospitalization_args = params_arg[hospitalization_bounds_key]
    death_bound_args = params_arg[death_bounds_key]
    immunity_bound_args = params_arg[immunity_bounds_key]

    inn_ind_cov = dict(zip(range(number_of_individuals_arg),
                           [int(get_r() <= infection_initialization_number_arg / number_of_individuals_arg)
                            for i in range(number_of_individuals_arg)]))

    life_state = dict(zip(range(number_of_individuals_arg), [HEALTHY_V] * number_of_individuals_arg))

    def get_infection_params():
        return get_infection_parameters(contagion_bound_args[0], contagion_bound_args[1],
                                        hospitalization_args[0], hospitalization_args[1],
                                        death_bound_args[0], death_bound_args[1],
                                        immunity_bound_args[0], immunity_bound_args[1])

    time_to_contagion = dict(zip(range(number_of_individuals_arg),
                                 [get_infection_params()[0] for _ in range(number_of_individuals_arg)]))
    time_to_hospital = dict(zip(range(number_of_individuals_arg),
                                [get_infection_params()[1] for _ in range(number_of_individuals_arg)]))
    time_to_death = dict(zip(range(number_of_individuals_arg),
                             [get_infection_params()[2] for _ in range(number_of_individuals_arg)]))
    time_to_end_immunity = dict(zip(range(number_of_individuals_arg),
                                    [get_infection_params()[3] for _ in range(number_of_individuals_arg)]))

    infected_individual_init = [k for k, v in inn_ind_cov.items() if v == 1]

    for individual in infected_individual_init:
        life_state[individual] = INFECTED_V

    return {
        CON_K: time_to_contagion,
        HOS_K: time_to_hospital,
        DEA_K: time_to_death,
        IMM_K: time_to_end_immunity,
        STA_K: life_state,
        FN_K: get_infection_params,
        NC_K: 0
    }


def get_default_params():
    return {
        nrun_key: 1,  # Number of runs
        scenario_id_key: -1,  # Scenario id if running the scenario package
        random_seed_key: 42,  # Of course 42
        draw_graph_key: [],  # What to draw

        nindividual_key: 1000,  # Number of people
        nday_key: 180,  # Number of simulated days
        innoculation_number_key: 5,  # Number of people innoculated at day 0

        # structure parameters
        store_per_house_key: 20,  # Let's say we have 20 houses for each grocerie store
        store_preference_key: 0.95,  # Probality of going to the nearest store
        store_nb_choice_key: 3,  # Number of stores that a single house can go to
        nb_1d_block_key: 20,  # number of block on one axe to slice the grid and model public transportation contamination,
        # total number of blocks is nb_1d_block_key^2

        # parameters that can change over time with lockdown loosening/removal
        remote_work_key: 0.98,  # Percentage of people doing remote work
        house_infect_key: 0.5,  # Probabilty of infecting a random family member (same house)
        work_infection_key: 0.01,  # Probabilty of infecting a random co-worker
        store_infection_key: 0.02,  # Probabilty of infecting someone who goes to the same store
        transport_infection_key: 0.01,  # Probabilty of infecting someone who goes to the same geographical block
        transport_contact_cap_key: 10,  # Cap used to limit transportation contact

        # https://annals.org/aim/fullarticle/2762808/incubation-period-coronavirus-disease-2019-covid-19-from-publicly-reported
        # this study show 4.5 to 5.8 days incubation period. Let's assume contagiosity starts when incubation is done
        contagion_bounds_key: (4, 6),  # Bounds defining a draw for contagion period

        # https://annals.org/aim/fullarticle/2762808/incubation-period-coronavirus-disease-2019-covid-19-from-publicly-reported
        # this study show 8.2 to 15.6 days before symptoms start. Hospitalization usually occur at that point
        # or maybe a little bit later
        hospitalization_bounds_key: (8, 16),  # Bounds defining a draw for hospitalization period

        # https://onlinelibrary.wiley.com/doi/full/10.1002/jmv.25689?af=R
        # seems like the 10‐41 day range is suited for < 7yo and 6‐19 day range for >=70yo
        # we can take a middle compromise
        death_bounds_key: (8, 31),  # Bounds defining a draw for time to death/immunity

        # we still don't really know about long-term immunity so let's assume it is a lifetime one
        # https://edition.cnn.com/2020/04/17/health/south-korea-coronavirus-retesting-positive-intl-hnk/index.html
        immunity_bounds_key: (900, 1000),  # Bounds defining a draw for immunity period

        quarantine_days_key: 15,  # the days of isolation if the test is positive

        # Moroccan data : http://northafricapost.com/39786-covid-19-morocco-expands-hospital-capacity.html
        icu_bed_per_thousand_individual_key: 0.085,

        additional_scenario_params_key: []  # Additional scenario parameters

    }


def get_infection_parameters(lower_contagion_bound, upper_contagion_bound,
                             lower_hospitalization_bound, upper_hospitalization_bound,
                             lower_death_bound, upper_death_bound,
                             lower_immunity_bound, upper_immunity_bound):
    # Time to death/immunity , Time to contagiosity
    return int(lower_contagion_bound + (upper_contagion_bound - lower_contagion_bound) * get_r()), \
           int(lower_hospitalization_bound + (upper_hospitalization_bound - lower_hospitalization_bound) * get_r()), \
           int(lower_death_bound + (upper_death_bound - lower_death_bound) * get_r()), \
           int(lower_immunity_bound + (upper_immunity_bound - lower_immunity_bound) * get_r())