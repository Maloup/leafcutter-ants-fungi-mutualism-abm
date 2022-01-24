from mesa import Agent

from .ant_agent import AntAgent


class Nest(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.energy_buffer = 0.0

    def ant_birth(self, n):
        for _ in range(n):
            agent = AntAgent(self.model.next_id(), self.model)
            self.model.schedule.add(agent)

            self.model.grid.place_agent(agent, self.pos)

    def step(self):
        offspring_count = int(self.energy_buffer / self.model.energy_per_offspring)
        self.energy_buffer -= offspring_count * self.model.energy_per_offspring
        self.ant_birth(offspring_count)
