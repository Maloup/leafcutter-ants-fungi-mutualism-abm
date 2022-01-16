from mesa import Agent


class RandomWalkerAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def random_move(self):
        """
        Randomly move to a Moore neighborhood.
        """
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=True)
        self.model.grid.move_agent(self, self.random.choice(neighbors))
