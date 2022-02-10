from mesa import Agent


class Fungus(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.biomass = self.model.initial_fungus_energy * self.model.energy_biomass_cvn
        self.energy = 0.0
        self.dead = False

    def feed(self):
        if not self.dead:
            self.energy += 1

    def check_death(self) -> None:
        """
        Checks if biomass is less than death threshold. Updates
        `self.dead` accordingly. This should be called every time
        `Nest.feed_larvae`.
        """
        # TODO: change this to a predicate function instead of a
        # side-effect function for legibility?
        self.dead = self.biomass < self.model.fungus_biomass_death_threshold

    def step(self):
        if not self.dead:
            # natural decay
            self.biomass -= self.model.fungus_decay_rate * self.biomass

            # check for death
            self.check_death()

            if self.energy > 0:
                # convert energy storage to biomass
                self.biomass += self.model.energy_biomass_cvn * self.energy
                self.energy = 0
