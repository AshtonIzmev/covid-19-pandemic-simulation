[![Build Status](https://travis-ci.org/AshtonIzmev/covid-19-pandemic-simulation.svg?branch=master)](https://travis-ci.org/AshtonIzmev/covid-19-pandemic-simulation)
[![codecov](https://codecov.io/gh/AshtonIzmev/covid-19-pandemic-simulation/branch/master/graph/badge.svg)](https://codecov.io/gh/AshtonIzmev/covid-19-pandemic-simulation)
[![pypi](https://badge.fury.io/py/pandemic-simulation.svg)](https://badge.fury.io/py/pandemic-simulation)
[![license](https://img.shields.io/pypi/l/pandemic-simulation.svg)](https://github.com/AshtonIzmev/covid-19-pandemic-simulation/blob/master/LICENSE)

# covid-19-pandemic-simulation
"Life simulation" of a SEIR inspired model to better understand pandemic using python.


# Getting started
```bash
pip install pandemic-simulation  # Last stable version
# or
apt-get install python3-venv gcc python3-dev
python3 -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt


### To plot new daily cases
python -m simulator.run --draw new --show-plot

### To plot daily state with 150 days and other parameters kept default
python -m simulator.run --nday 150  --draw pop --show-plot

### To plot hospitalization state with 5000 individuals
python -m simulator.run --nday 200 --nind 5000 --draw hos --show-plot

### To plot a summary of the pandemic (with short immunity time)
python -m simulator.run  --nday 500 --nind 5000 --immunity-bounds 120 150 --draw sum new --show-plot
```

# Run a scenario
35k individuals (--nind), 20 simulations (--nrun). Add --show-plot if you want plots to be displayed in a pop-up instead of written to images/output folder

Scenario -1 : It is just a flu (using 3 cpu in parallel)
```bash
python -m scenario.run --nrun 20  --nday 180 --nind 35000 --scenario -1  --draw exa pop summ R0 --ncpu 3
```
Scenario 0 : Eradicate
```bash
python -m scenario.run --nrun 40  --nday 90 --nind 35000 --scenario 0 --p-house 0.5 --p-work 0.01 --p-transport 0.01 --p-store 0.001  --draw exa pop summ R0
```
Scenario 1 : One shot lockdown removal
```bash
python -m scenario.run --nrun 20  --nday 360 --nind 35000 --scenario 1 --extra 14 --draw exa pop summ lock hos new R0
```
Scenario 2 : Yo-yo lockdown removal
```bash
python -m scenario.run --nrun 20  --nday 360 --nind 35000 --scenario 2 --extra 7 1 2  --draw exa pop summ lock hos new R0
```
Scenario 3 : Herd immunity
```bash
python -m scenario.run --nrun 20  --nday 360 --nind 35000 --scenario 3 --extra 0  --draw exa pop summ lock hos new R0
```
Scenario 4 : Rogue citizen
```bash
python -m scenario.run --nrun 20  --nday 180 --nind 35000 --scenario 4 --extra 1 10  --draw exa pop summ lock hos new R0
```
Scenario 5 : Rogue neighborhood
```bash
python -m scenario.run --nrun 20  --nday 180 --nind 35000 --scenario 5 --extra 4 10  --draw exa pop summ lock hos new R0
```
Scenario 6 : Infected travelers
```bash
python -m scenario.run --nrun 20  --nday 180 --nind 35000 --scenario 6 --p-store 0.001 --extra 5  --draw exa pop summ lock hos new R0
```
Scenario 7 : Temporal immunity
```bash
python -m scenario.run --nrun 20  --nday 720 --nind 35000 --scenario -1 --imm 30 60  --draw exa pop summ R0
```

More scenarios are available in the scenario package.

# Usage
```bash
usage: run_benchmark.py [-h] [--nrun NRUN] [--random-seed RANDOM_SEED]
                        [--ncpu NUM_CPU] [--nind N_INDIVIDUALS]
                        [--nday N_DAYS] [--sto-house NB_STORE_PER_HOUSE]
                        [--nblock NB_1D_GRID_BLOCK]
                        [--remote-work REMOTE_WORK_PERCENT]
                        [--sto-pref PROB_PREFERENCE_STORE]
                        [--sto-nb STORE_NB_CHOICE_KEY]
                        [--inn-infec INITIAL_INNOCULATION_NB]
                        [--p-house PROB_HOUSE_INFECTION]
                        [--p-store PROB_STORE_INFECTION]
                        [--p-work PROB_WORK_INFECTION]
                        [--p-transport PROB_TRANSPORT_INFECTION]
                        [--transport-contact-cap TRANSPORT_CONTACT_CAP]
                        [--contagion-bounds CONTAGION_BOUNDS CONTAGION_BOUNDS]
                        [--hospitalization-bounds HOSPITALIZATION_BOUNDS HOSPITALIZATION_BOUNDS]
                        [--death-bounds DEATH_BOUNDS DEATH_BOUNDS]
                        [--immunity-bounds IMMUNITY_BOUNDS IMMUNITY_BOUNDS]
                        [--nbeds-icu ICU_BED_PER_1K_INDIV]
                        [--scenario-id SCENARIO_ID]
                        [--draw [DRAW_GRAPH [DRAW_GRAPH ...]]]
                        [--extra-scenario-params [ADDITIONAL_SCENARIO_PARAMETERS [ADDITIONAL_SCENARIO_PARAMETERS ...]]]

Please feed model parameters

optional arguments:
  -h, --help            show this help message and exit
  --nrun NRUN           Number of simulations
  --random-seed RANDOM_SEED
                        Random seed
  --ncpu NUM_CPU        Number of cpus to use (-1 is all but one)
  --nind N_INDIVIDUALS  Number of individuals
  --nday N_DAYS         Number of days
  --nvariant N_VARIANT  Number of variants
  --sto-house NB_STORE_PER_HOUSE
                        Number of store per house
  --nblock NB_1D_GRID_BLOCK
                        Number of blocks in the grid
  --remote-work REMOTE_WORK_PERCENT
                        Percentage of people remote working
  --sto-pref PROB_PREFERENCE_STORE
                        Probability going to nearest store
  --sto-nb STORE_NB_CHOICE_KEY
                        Number of nearest stores to consider
  --inn-infec INITIAL_INNOCULATION_NB
                        Initial innoculation percentage
  --p-house PROB_HOUSE_INFECTION
                        Probability of house infection
  --p-store PROB_STORE_INFECTION
                        Probability of store infection
  --p-work PROB_WORK_INFECTION
                        Probability of workplace infection
  --p-transport PROB_TRANSPORT_INFECTION
                        Probability of public transportation infection
  --transport-contact-cap TRANSPORT_CONTACT_CAP
                        Number of people an individual is close when commuting
  --contagion-bounds CONTAGION_BOUNDS CONTAGION_BOUNDS
                        Contagion bounds
  --hospitalization-bounds HOSPITALIZATION_BOUNDS HOSPITALIZATION_BOUNDS
                        Hospitalization bounds
  --death-bounds DEATH_BOUNDS DEATH_BOUNDS
                        Death bounds
  --immunity-bounds IMMUNITY_BOUNDS IMMUNITY_BOUNDS
                        Immunity bounds
  --nbeds-icu ICU_BED_PER_1K_INDIV
                        Number of ICU beds per thousand population
  --scenario-id SCENARIO_ID, --sce SCENARIO_ID
                        Immunity bounds
  --draw [DRAW_GRAPH [DRAW_GRAPH ...]]
                        Draw a kind of graph by specifying at least the first
                        3 letters of its keys. Choose from "example",
                        "hospital", "new", "summary", "population", "lockdown"
                        and more
  --show-plot           Show the plots instead of persistings them to files
  --extra-scenario-params [ADDITIONAL_SCENARIO_PARAMETERS [ADDITIONAL_SCENARIO_PARAMETERS ...]]
                        Additional scenario parameters
```

# Main idea
I wanted to recreate the SEIR model results without having to use the differentials equations like in [1]. This means going down the individual level and simulating each person life.

So what is "life" in a pandemic lockdown situation (where almost all nations are now) ?

1. You are an individual with an age (important factor here)
2. You have a house where you live along family members, probably with children
3. If you haven't been authorized to do remote work, you will have to go to your workplace every day
4. You or one of the adults living in your house has to go to the grocerie store every day
5. In every place (house, store, work or transport), you get to interact with other individuals who can be infected. So there is a probability you will get infected too
6. If you are infected, you become contagious after few days and start to spread the disease
7. If you are infected, you will die or recover from the disease after a period of time, based on your age (and health issues but let's forget about those for now)
8. If hospitals are full, mortality rates raises
9. Death or immunity will not make you anymore contagious for other individual, obviously
10. You are isolated if one of your family members has been hospitalized

# Public transportation model
Each house and workplace is being assigned a geolocation in a grid. This grid can be cut into blocks (defined by a parameter).
When a worker goes from his house to his workplace, he goes through blocks that are shared by other workers.
We maintain a dictionnary of this transportation relationship between workers to propagate the pandemic.

# Some graphs
With default parameters.

Placement of houses, stores and workplaces in a grid :
![Geographical position](/images/geo_placement.png)

Evolution of the number of healthy, infected, dead and immune people :
![Population infection state](/images/propagation.png)
It is nice to see the famous 70% herd immunity

Evolution of the number of new cases :
![New cases](/images/newcases.png)
Check the long tail, new cases can emerge days after been to 0

With a temporary immunity, we see waves slowly eaten by dead people :
![Temporary immunity waves](/images/vague.png)
Temporary immunity of 60 to 90 days can prevent the pandemic from dying

With a summary of a strange non-wave pandemic evolution using :
```bash
python -m simulator.run  --nday 500 --nind 5000 --immunity-bounds 120 150  --draw summary
```
![Temporary immunity waves](/images/summary.png)
The lockdown beats the immunity decreasing. I had to launch the simulation with those models many times to get it.

Here are multiple runs plot against each other :
```bash
python -m simulator.run --nrun 20  --nday 180 --nind 1000 --immunity-bounds 60 90  --draw exa
```
![Examples](/images/examples.png)
Using a quick and dirty kmeans, we only display the most "different" run distributions to illustrate the butterfly effect of a pandemic

# Backlog
- [ ]  Simulate a population density and allow people to go to other houses in very dense place (in poor neighborhood)
- [ ]  Build a new kind of individuals who do not work in workplaces but can go in every house or store (policemen for example)
- [ ]  Add a delay between test and isolation (PCR tests can take one day)
- [x]  Self-isolation of individuals based on symptoms probability of appearance
- [x]  Add a tqdm progress bar to ray parallelized code execution
- [x]  parallelize the runs (using for example N_proc-1 processors multithreading)
- [x]  Build a moving average R0 instead of the daily R0 currently used
- [x]  Add a moroccan age pyramid
- [x]  Get rid of FN_K: get_infection_params and use a python class
- [x]  FAILED : Switch from dictionaries and list to numpy array (may be way more efficient, probably enabling some nice vectorization but huge refactors to come. Turns out it was a bad idea for performance -> lonely branch)
- [x]  More tests, there are never enough tests
- [x]  Get rid of params as a global variable and use a function (probably a bad pattern)
- [x]  Plot the R0 of the pandemic ? (with linear and logarithmic scale)
- [x]  Fix transport propagation performance issue
- [x]  Add a test-isolation stratey. Since at the end of the confinement, we assume that a part of the people will be tested and positive persons will be isolated.
- [x]  When hospitals are full, mortality rates raises
- [x]  Make contagion probability slowly raises as I assume people will get tired of the lockdown and start to be lazy at wearing masks and staying home ... (Handled in a scenario)
- [x]  Contagion parameters depend on geographic blocks (using individual model, we achieve this)
- [x]  Use a contagion probability model for each individual (e.g. probability of contagion is obtained with a model)
- [x]  Reviewing the distribution model of individuals over households, probably it can be modeled with a truncated normal distribution, we can set parameters using information from this website https://www.hcp.ma/Les-projections-de-la-population-et-des-menages-entre-2014-et-2050_a1920.html.
- [x]  Infection can and often occurs on public transportation. We need to build a basic transport model with infection probabilities
- [x]  You probably won't go to the grocerie store every day, but probably twice in week day and once on the weekend (that could be a random variable)
- [x]  Extract more parameters from the code
- [x]  Model temporary immunity
- [x]  Handle multiple runs and add error bars to result plots
- [x]  Work is only on week days, weekend need to be removed
- [x]  You may go to the second nearest grocerie store instead of the closest one (as implemented)
- [x]  You probably won't go to the grocerie store every day, but probably twice in week day and once on the weekend (that could be a random variable)
- [x]  Add a model for hospitalized people (since hospitals can be saturated)
- [x]  Handle multiple runs and add error bars to result plots

## Articles explaining the approach
https://issam.ma/jekyll/update/2020/04/11/covid-pandemic-simulation.html (French)
https://issam.ma/jekyll/update/2020/05/01/pandemic-lockdown-scenarios.html (French)
https://issam.ma/jekyll/update/2020/07/04/macro-economic-immunity.html (French)

# Links
[1] https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology#The_SEIR_model
