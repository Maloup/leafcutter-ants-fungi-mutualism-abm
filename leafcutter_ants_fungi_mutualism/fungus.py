from mesa import Agent


class Fungus(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.energy = self.model.initial_fungus_energy
        self.biomass = self.energy
        self.dead = False

    def feed(self):
        if not self.dead:
            self.energy += 1

    def step(self):
        if not self.dead:
            self.biomass -= self.model.fungus_decay_rate*self.biomass

            if self.biomass <= self.model.fungus_biomass_death_threshold:
                self.dead = True
            elif self.energy > 0:
                self.biomass += self.energy
                self.energy = 0
