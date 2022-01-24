from mesa import Agent
import numpy as np

from .util import manhattan_distance


class RandomWalkerAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def random_move(self):
        """
        Randomly move to a Moore neighborhood.
        """
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=True)
        self.model.grid.move_agent(self, self.random.choice(neighbors))


class BiasedRandomWalkerAgent(RandomWalkerAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.prev_pos = None

    def random_move(self):
        """
        Biased random move to a Moore neighborhood.
        """
        if self.prev_pos is None:
            # random walk for first step
            super().random_move()
            self.prev_pos = self.pos
        else:
            # biased random move
            neighbors = self.model.grid.get_neighborhood(self.pos, moore=True)
            dists = np.array([manhattan_distance(self.prev_pos, n)
                              for n in neighbors])
            prob_dist = dists/np.sum(dists)
            next_idx = np.random.choice(len(neighbors), p=prob_dist)
            next_pos = neighbors[next_idx]

            self.prev_pos = self.pos
            self.model.grid.move_agent(self, next_pos)
