from mesa import Agent
import numpy as np

from .util import manhattan_distance


class RandomWalkerAgent(Agent):
    """
    An agent class capable of executing an unbiased random
    walk step on a grid.
    """

    def __init__(self, unique_id, model):
        """
        Parameters
        ----------
        model: Model object
            Expected to be an instance of the `Model` class
            that has a `grid` attribute that is an instance of `mesa.Space.Grid`
        """
        super().__init__(unique_id, model)

    def random_move(self):
        """
        Randomly move to a cell in the neighborhood of its current
        position.
        """
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=True)
        self.model.grid.move_agent(self, self.random.choice(neighbors))


class BiasedRandomWalkerAgent(RandomWalkerAgent):
    """
    An agent class capable of performing a biased random
    walk step on a model's grid.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.prev_pos = None

    def random_move(self):
        """
        Perform a biased random walk step by randomly selecting
        one of the cells Moore neighborhood. The probability of selecting
        a cell is proportional to the manhattan distance between that cell
        and this agent's previous position. If previous position is `None`, then
        an unbiased random walk step is performed instead.
        """
        if self.prev_pos is None:
            # unbiased random walk for first step
            super().random_move()
            # update previous position
            self.prev_pos = self.pos
        else:
            # biased random walk step
            # get Moore neighborhood
            neighbors = self.model.grid.get_neighborhood(self.pos, moore=True)
            dists = np.array([manhattan_distance(self.prev_pos, n)
                              for n in neighbors])
            # create probability mass function
            prob_dist = dists / np.sum(dists)
            next_idx = np.random.choice(len(neighbors), p=prob_dist)
            next_pos = neighbors[next_idx]

            self.prev_pos = self.pos
            self.model.grid.move_agent(self, next_pos)
