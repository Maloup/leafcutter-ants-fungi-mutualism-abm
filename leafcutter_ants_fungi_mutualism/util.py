from numpy import tanh, arctan, pi
from enum import Enum, auto

class DeathReason(enum.Enum):
    FUNGUS = auto()
    ANTS = auto()


def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# activations for positive real line


def tanh_activation_pstv(x, a):
    return tanh(a*x)


def arctan_activation_pstv(x, a):
    return (2.0/pi)*arctan(a*x)

# activations for the entire real line


def arctan_activation_real(x, a):
    return (1/pi) * (arctan(a * x)) + 0.5


def tanh_activation_real(x, a):
    return 0.5 * tanh(a*x) + 0.5

def track_death_reason(model):
    if model.death_reason:
        return model.death_reason
    fungus_dead_p = model.model.fungus.dead
    if fungus_dead_p:
        return DeathReason.FUNGUS

    agents_list = model.schedule.agents
    for agent in agents_list:
        if isinstance(agent, AntAgent):
            return None
    return DeathReason.ANTS
