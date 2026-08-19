"""Short aliases for the life-state values, so the propagation fixtures below
read as a grid of individuals rather than a wall of numbers."""
from simulator.constants.keys import (
    DEAD_V,
    HEALTHY_V,
    HOSPITALIZED_V,
    IMMUNE_V,
    INFECTED_V,
    ISOLATED_V,
)

H = HEALTHY_V
F = INFECTED_V
M = IMMUNE_V
D = DEAD_V
P = HOSPITALIZED_V
S = ISOLATED_V
