from numpy import tanh, arctan, pi


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
