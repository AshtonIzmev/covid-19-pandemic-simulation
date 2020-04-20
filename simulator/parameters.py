# Default parameters
nrun_key = "NRUN"
scenario_id_key = "SCENARIO_ID"
random_seed_key = "RANDOM_SEED"
draw_graph_key = "DRAW_GRAPH"

nindividual_key = "N_INDIVIDUALS"
nday_key = "N_DAYS"
innoculation_number_key = "INITIAL_INNOCULATION_NB"
nb_block_key = "NB_GRID_BLOCK"
# Work relative
remote_work_key = "REMOTE_WORK_PERCENT"
# Store relative
store_per_house_key = "NB_STORE_PER_HOUSE"
store_preference_key = "PROB_PREFERENCE_STORE"
# Dynamic
house_infect_key = "PROB_HOUSE_INFECTION"
work_infection_key = "PROB_WORK_INFECTION"
store_infection_key = "PROB_STORE_INFECTION"
transport_infection_key = "PROB_TRANSPORT_INFECTION"
# Bounds
contagion_bounds_key = "CONTAGION_BOUNDS"
hospitalization_bounds_key = "HOSPITALIZATION_BOUNDS"
death_bounds_key = "DEATH_BOUNDS"
immunity_bounds_key = "IMMUNITY_BOUNDS"

# Scenario parameters
days_wait_lockdown_removal = "DAYS_WAIT_FOR_LOCKDOWN_REMOVAL"

params = {
    nrun_key: 1,  # Number of runs
    scenario_id_key: -1,  # Scenario id if running the scenario package
    random_seed_key: 42,  # Of course 42
    draw_graph_key: ["summary", "hospital"],  # By default, draw summary

    nindividual_key: 1000,  # Number of people
    nday_key: 180,  # Number of simulated days
    innoculation_number_key: 5,  # Number of people innoculated at day 0

    # structure parameters
    store_per_house_key: 20,  # Let's say we have 20 houses for each grocerie store
    store_preference_key: 0.95,  # Probality of going to the nearest store
    nb_block_key: 10,  # number of block to slice the grid and model public transportation contamination

    # parameters that can change over time with lockdown loosening/removal
    remote_work_key: 0.98,  # Percentage of people doing remote work
    house_infect_key: 0.5,  # Probabilty of infecting a random family member (same house)
    work_infection_key: 0.01,  # Probabilty of infecting a random co-worker
    store_infection_key: 0.02,  # Probabilty of infecting someone who goes to the same store
    transport_infection_key: 0.01,  # Probabilty of infecting someone who goes to the same geographical block

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

    days_wait_lockdown_removal: 7  # How to long to wait before lockdown removal

}
