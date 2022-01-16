from mesa import Agent


class Pheromone(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.initial_lifespan = self.model.pheromone_lifespan
        self.lifespan = self.model.pheromone_lifespan

    def step(self):
        self.lifespan -= 1

        if self.lifespan == 0:
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)
