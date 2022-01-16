from mesa import Agent


class Fungus(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.energy = 0
        self.biomass = 1

    def feed(self):
        self.energy += 1

    def step(self):
        # TODO: mechanism for converting energy into biomass
        pass
