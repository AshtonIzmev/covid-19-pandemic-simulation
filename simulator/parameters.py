# Default parameters
nrun_key = "NRUN"
random_seed_key = "RANDOM_SEED"

nindividual_key = "N_INDIVIDUALS"
nday_key = "N_DAYS"
innoculation_pct_key = "INITIAL_INNOCULATION_PCT"
same_house_p_key = "PROBA_SAME_HOUSE_RATE"
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

params = {
    nrun_key: 1,  # Number of runs
    random_seed_key: 42,  # Of course 42
    nindividual_key: 1000,  # Number of people
    nday_key: 180,  # Number of simulated days
    innoculation_pct_key: 0.005,  # Proportion of people innoculated at day 0

    store_per_house_key: 20,  # Let's say we have 20 houses for each grocerie store
    remote_work_key: 0.5,  # Percentage of people doing remote work
    store_preference_key: 0.7,  # Probality of going to the nearest store
    same_house_p_key: 0.1,  # probability used to set the number of person per house
    nb_block_key: 10,  # number of block to slice the grid and model public transportation contamination

    house_infect_key: 0.5,  # Probabilty of infecting a random family member (same house)
    work_infection_key: 0.1,  # Probabilty of infecting a random co-worker
    store_infection_key: 0.05,  # Probabilty of infecting someone who goes to the same store
    transport_infection_key: 0.05,  # Probabilty of infecting someone who goes to the same geographical block

    contagion_bounds_key: (2, 7),  # Bounds defining a draw for contagion period
    hospitalization_bounds_key: (14, 20),  # Bounds defining a draw for hospitalization period
    death_bounds_key: (21, 39),  # Bounds defining a draw for time to death/immunity
    immunity_bounds_key: (600, 900)  # Bounds defining a draw for immunity period
}
