import pandas as pd

TPE_MAX_EMPLOYEES = 3
PME_MAX_EMPLOYEES = 15
GE_MAX_EMPLOYEES = 50


# Source : https://www.worldometers.info/coronavirus/coronavirus-age-sex-demographics/
covid_mortality_rate = {
    8: 0.148,
    7: 0.08,
    6: 0.036,
    5: 0.013,  # 50-59 yo => 0.013 probability of dying
    4: 0.04,
    3: 0.02,
    2: 0.02,
    1: 0.02,
    0: 0
}
# Source : https://gis.cdc.gov/grasp/COVIDNet/COVID19_5.html
covid_hospitalization_rate = {
    8: 0.172,
    7: 0.158,
    6: 0.122,
    5: 0.074,
    4: 0.025,
    3: 0.025,
    2: 0.025,
    1: 0.01,
    0: 0.03
}

# Source https://www.populationpyramid.net/world/2019/
world_age_distribution = [
    ["0-4", 349247348, 328119059],
    ["5-9", 341670620, 320090537],
    ["10-14", 328942130, 307203261],
    ["15-19", 314806147, 293931999],
    ["20-24", 307809031, 288834393],
    ["25-29", 307548367, 290783757],
    ["30-34", 305762271, 293702434],
    ["35-39", 270507560, 262936512],
    ["40-44", 247594384, 242696599],
    ["45-49", 239897308, 237022350],
    ["50-54", 218833001, 219504648],
    ["55-59", 187135108, 190624979],
    ["60-64", 153758680, 161570707],
    ["65-69", 124471230, 136004171],
    ["70-74", 82793263, 96515002],
    ["75-79", 53073892, 66973202],
    ["80-84", 33071682, 47305811],
    ["85-89", 15423679, 25733670],
    ["90-94", 5370654, 11222622],
    ["95-99", 1203726, 3239297],
    ["100-125", 114528, 418582]
]


def get_age_distribution():
    # Source https://www.populationpyramid.net/world/2019/
    age_distribution = pd.DataFrame(world_age_distribution, columns=['age', 'nb_men', 'nb_women'])
    age_distribution['nb'] = age_distribution['nb_men'] + age_distribution['nb_women']
    age_distribution['pct'] = age_distribution['nb'] / age_distribution['nb'].sum()
    age_distribution['min_age'] = age_distribution['age'].map(lambda s: int(s.split('-')[0]))
    age_distribution['max_age'] = age_distribution['age'].map(lambda s: int(s.split('-')[1]))
    # We did a cut to 25 years old for adult
    age_distribution_children = age_distribution.iloc[:7]
    age_distribution_adults = age_distribution.iloc[4:]
    age_distribution_children_cumsum = \
        age_distribution_children['pct'].cumsum() / age_distribution_children['pct'].cumsum().max()
    age_distribution_adults_cumsum = \
        age_distribution_adults['pct'].cumsum() / age_distribution_adults['pct'].cumsum().max()
    return age_distribution_children, age_distribution_children_cumsum, age_distribution_adults, \
           age_distribution_adults_cumsum


age_dist_children, age_dist_children_cs, age_dist_adults, age_dist_adults_cs = get_age_distribution()
