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

    def feed_larvae(self):
        if (self.model.fungus.biomass > self.model.fungus_biomass_death_threshold + 2 * self.model.energy_per_offspring):
            self.model.fungus.biomass -= 1.0
            # `fungus_larvae_cvn` defaults to 1.0
            self.energy_buffer += self.model.fungus_larvae_cvn  # * 1.0

    def step(self):
        offspring_count = int(self.energy_buffer /
                              self.model.energy_per_offspring)
        self.energy_buffer -= offspring_count * self.model.energy_per_offspring
        self.ant_birth(offspring_count)
