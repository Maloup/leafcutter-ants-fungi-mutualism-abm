from mesa import Agent


class Pheromone(Agent):
    def __init__(self, unique_id, model, lifespan=50):
        super().__init__(unique_id, model)
        self.initial_lifespan = lifespan
        self.lifespan = lifespan

    def step(self):
        self.lifespan = max(0, self.lifespan - 1)

        if self.lifespan == 0:
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)
