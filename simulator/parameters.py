# Default parameters
nrun_key = "NRUN"

nindividual_key = "N_INDIVIDUALS"
nday_key = "N_DAYS"
store_per_house_key = "NB_STORE_PER_HOUSE"
remote_work_key = "REMOTE_WORK_PERCENT"
same_house_p_key = "PROBA_SAME_HOUSE_RATE"
innoculation_pct_key = "INITIAL_INNOCULATION_PCT"
house_infect_key = "PROB_HOUSE_INFECTION"
work_infection_key = "PROB_WORK_INFECTION"
store_infection_key = "PROB_STORE_INFECTION"
store_preference_key = "PROB_PREFERENCE_STORE"
contagion_bounds_key = "CONTAGION_BOUNDS"
hospitalization_bounds_key = "HOSPITALIZATION_BOUNDS"
death_bounds_key = "DEATH_BOUNDS"
immunity_bounds_key = "IMMUNITY_BOUNDS"

params = {
    nrun_key: 1,  # Number of runs
    nindividual_key: 1000,  # Number of people
    nday_key: 180,  # Number of simulated days
    store_per_house_key: 20,  # Let's say we have 20 houses for each grocerie store
    remote_work_key: 0.5,  # Percentage of people doing remote work
    store_preference_key: 0.7,  # Probality of going to the nearest store
    same_house_p_key: 0.1,  # probability used to set the number of person per house
    innoculation_pct_key: 0.005,  # Proportion of people innoculated at day 0
    house_infect_key: 0.5,  # Probabilty of infecting a random family member (same house)
    work_infection_key: 0.1,  # Probabilty of infecting a random co-worker
    store_infection_key: 0.05,  # Probabilty of infecting someone who goes to the same store
    contagion_bounds_key: (2, 7),  # Bounds defining a draw for contagion period
    hospitalization_bounds_key: (14, 20),  # Bounds defining a draw for hospitalization period
    death_bounds_key: (21, 39),  # Bounds defining a draw for time to death/immunity
    immunity_bounds_key: (600, 900)  # Bounds defining a draw for immunity period
}
