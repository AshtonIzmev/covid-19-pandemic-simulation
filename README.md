# covid-19-pandemic-simulation
"Life simulation" of a SEIR inspired model to better understand pandemic using python.

This project is subject to heavy changes until the 2020-04-20.

# Getting started
```bash
pip install -r requirements.txt

### To execute all the unit tests
make test

### To plot new daily cases
python -m simulator.run --new-cases 
 
### To plot daily state with 150 days and other parameters kept default
python -m simulator.run --population-state --nday 150  

### To plot hospitalization state with 5000 individuals
python -m simulator.run --hospitalized-cases --nday 200 --nind 5000

### To plot a summary of the pandemic (with short immunity time)
python -m simulator.run  --nday 500 --nind 5000 --summary --immunity-bounds 120 150
```

# Usage
```bash
usage: run.py [-h] [--nrun NRUN] [--nind N_INDIVIDUALS] [--nday N_DAYS]
              [--sto-house NB_STORE_PER_HOUSE]
              [--p-same-house PROBA_SAME_HOUSE_RATE]
              [--inn-infec INITIAL_INNOCULATION_PCT]
              [--p-house PROB_HOUSE_INFECTION]
              [--p-store PROB_STORE_INFECTION] [--p-work PROB_WORK_INFECTION]
              [--contagion-bounds CONTAGION_BOUNDS CONTAGION_BOUNDS]
              [--hospitalization-bounds HOSPITALIZATION_BOUNDS HOSPITALIZATION_BOUNDS]
              [--death-bounds DEATH_BOUNDS DEATH_BOUNDS]
              [--imunity-bounds IMMUNITY_BOUNDS IMMUNITY_BOUNDS]
              [--population-state] [--hospitalized-cases] [--new-cases]

Please feed model parameters

optional arguments:
  -h, --help            show this help message and exit
  --nrun NRUN           Number of simulations
  --nind N_INDIVIDUALS  Number of individuals
  --nday N_DAYS         Number of days
  --sto-house NB_STORE_PER_HOUSE
                        Number of store per house
  --p-same-house PROBA_SAME_HOUSE_RATE
                        "Probability" for individuals for living in the same
                        house
  --inn-infec INITIAL_INNOCULATION_PCT
                        Initial innoculation percentage
  --p-house PROB_HOUSE_INFECTION
                        Probability of house infection
  --p-store PROB_STORE_INFECTION
                        Probability of store infection
  --p-work PROB_WORK_INFECTION
                        Probability of workplace infection
  --contagion-bounds CONTAGION_BOUNDS CONTAGION_BOUNDS
                        Contagion bounds
  --hospitalization-bounds HOSPITALIZATION_BOUNDS HOSPITALIZATION_BOUNDS
                        Hospitalization bounds
  --death-bounds DEATH_BOUNDS DEATH_BOUNDS
                        Death bounds
  --imunity-bounds IMMUNITY_BOUNDS IMMUNITY_BOUNDS
                        Immunity bounds
  --population-state    Draw population state graph
  --hospitalized-cases  Draw hospitalized cases graph
  --new-cases           Draw new cases graph
```

# Main idea
I wanted to recreate the SEIR model results without having to use the differentials equations like in [1]. This means going down the individual level and simulating each person life.

So what is "life" in a pandemic lockdown situation (where almost all nations are now) ?

1. You are an individual with an age (important factor here)
2. You have a house where you live along family members, probably with children
3. If you haven't been authorized to do remote work, you will have to go to your workplace every day
4. You or one of the adults living in your house has to go to the grocerie store every day
5. In every place (house, store, work), you get to interact with other individuals who can be infected. So there is a probability you will get infected too
6. If you are infected, you become contagious after few days and start to spread the disease
7. If you are infected, you will die or recover from the disease after a period of time, based on your age (and health issues but let's forget about those for now)
8. Death or immunity will not make you anymore contagious for other individual, obviously


# Input parameters
* N_INDIVIDUALS : number of person involved in this simulation (default 5000)
* N_DAYS : number of days for the simulation (default 120)
* NB_STO_PER_HOU : number of house for each store (default 20)
* PROBA_SAME_HOUSE_RATE : probability used to define the number of individuals in a house (default 0.1 builds 3.57 average people per house)
* INITIAL_INNOCULATION_PCT : Percentage of people who get the virus at day 0
* PROB_HOUSE_INFECTION : probability of getting infected if an infected individual lives in the same house (defaut 0.5)
* PROB_WORK_INFECTION : probability of getting infected if an infected individual works in the same place (default 0.1)
* PROB_STORE_INFECTION : probability of getting infected if an infected individual shops at the same store (default 0.05 since we tend to spend less time in a store)
* [ LOWER_INFECTION_BOUND, UPPER_INFECTION_BOUND ] : random number range to generate time to decision (death/immunity)
* [ LOWER_CONTAGION_BOUND, UPPER_CONTAGION_BOUND ] : random number range to generate time to becoming conatigous (death/immunity)


All those parameters can be discussed and will be enriched as I keep enhancing this simulation model.

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
python -m simulator.run  --nday 500 --nind 5000 --summary --immunity-bounds 120 150
```
![Temporary immunity waves](/images/summary.png)
The lockdown beats the immunity decreasing. I had to launch the simulation with those models many times to get it.

# Backlog
- [x]  Work is only on week days, weekend need to be removed
- [x] You may go to the second nearest grocerie store instead of the closest one (as implemented)
- [x]  You probably won't go to the grocerie store every day, but probably twice in week day and once on the weekend (that could be a random variable)
- [x] You may go to the second nearest grocerie store instead of the closest one (as implemented)
- [ ]  You probably won't go to the grocerie store every day, but probably twice in week day and once on the weekend (that could be a random variable)
- [ ]  Infection can and often occurs on public transportation. We need to build a basic transport model with infection probabilities
- [ ]  Inject the famous covid-19 2.3 R0 into the code somewhere to get realistic results
- [x]  Extract more parameters from the code
- [x]  Model temporary immunity
- [ ]  Contagion parameters depend on geographic zones
- [ ]  Make contagion probability slowly raises as I assume people will get tired of the lockdown and start to be lazy at wearing masks and staying home ...
- [ ]  Use a contagion probability model for each individual (e.g. probability of contagion is obtained with a model)
- [x]  Add a model for hospitalized people (since hospitals can be saturated)
- [x]  Handle multiple runs and add error bars to result plots

## Articles explaining the approach
https://issam.ma/jekyll/update/2020/04/11/covid-pandemic-simulation.html

# Links
[1] https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology#The_SEIR_model
