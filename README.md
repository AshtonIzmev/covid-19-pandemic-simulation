# covid-19-pandemic-simulation
"Life simulation" of a SEIR inspired model to better understand pandemic using python.

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
* N : number of person involved in this simulation (default 5000)
* N_days : number of days for the simulation (default 120)
* NB_STO_PER_HOU : number of house for each store (default 20)
* PROBA_SAME_HOUSE_RATE : probability used to define the number of individuals in a house (default 0.1 builds 3.57 average people per house)
* PROB_INFECTION_AT_HOME : probability of getting infected if an infected individual lives in the same house (defaut 0.5)
* PROB_INFECTION_AT_WORK : probability of getting infected if an infected individual works in the same place (default 0.1)
* PROB_INFECTION_AT_STORE : probability of getting infected if an infected individual shops at the same store (default 0.05 since we tend to spend less time in a store)
* TPE_MAX_EMPLOYEES : number of employees in a small size company (default 3)
* PME_MAX_EMPLOYEES : number of employees in a medium size company (default 15)
* GE_MAX_EMPLOYEES : number of employees in a large size company (default 50)

All those parameters can be discussed and will be enriched as I keep enhancing this simulation model.

# Some graphs
With default parameters.

Placement of houses, stores and workplaces in a grid :
![Geographical position](/images/geo_placement.png)

Evolution of the number of healthy, infected, dead and immune people :
![Population infection state](/images/propagation.png)
it is nice to see the famous 70% herd immunity

Evolution of the number of new cases :
![Population infection state](/images/newcases.png)
it definitely does not look like a Gaussian distribution but more like a Poisson distribution. Check the end tail :)

# Backlog
* Work is only on week days, weekend need to be removed
* You may go to the second nearest grocerie store instead of the closest one (as implemented)
* You probably won't go to the grocerie store every day, but probably twice in week day and once on the weekend (that could be a random variable)
* Infection can and often occurs on public transportation. We need to build a basic transport model with infection probabilities
* Inject the famous covid-19 2.3 R0 into the code somewhere to get realistic results
* Extract more parameters from the code
* Make contagion probability slowly raises as I assume people will get tired of the lockdown and start to be lazy at wearing masks and staying home ...

# Links
[1] https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology#The_SEIR_model
