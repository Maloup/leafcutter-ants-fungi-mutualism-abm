from mesa import Agent
import queue
from .ant_agent import AntAgent, AntWorkerState


class Nest(Agent):
    """
    Agent object used for modeling the ant colony. It occupies a single grid cell
    and ants in the `CARETAKING` must also occupy the same cell.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        # energy buffer - models nutrition provided to larvae
        self.energy_buffer = 0.0
        # forager fitness queue for Moran process
        self.fitness_queue = queue.Queue(self.model.max_fitness_queue_size)

    def ant_birth(self, n) -> None:
        """
        Creates `n` new adult ants (i.e. constructs `AntAgent` objects). One of
        two possible states are probabalistically assigned to the new adults
        based on the average fitness value of the Moran process queue.
        """
        fitness_queue_list = list(self.fitness_queue.queue)
        if len(fitness_queue_list) != 0:
            average_fitness = sum(fitness_queue_list)/len(fitness_queue_list)
        else:
            # Assuming uniform apriori role distribution
            average_fitness = 0.5
        for _ in range(n):
            agent = AntAgent(self.model.next_id(), self.model)

            if self.random.random() > average_fitness:
                agent.state = AntWorkerState.CARETAKING

            self.model.schedule.add(agent)
            self.model.grid.place_agent(agent, self.pos)

    def feed_larvae(self) -> None:
        """
        Called by `AntAgent` objects in the `CARETAKING` state. A fixed amount of fungus biomass is removed and converted to energy (nutrition for larvae) in the nest's energy buffer.
        """
        if not self.model.fungus.dead:
            self.model.fungus.biomass -= self.model.caretaker_carrying_amount
            self.model.fungus.check_death()
            self.energy_buffer += self.model.fungus_larvae_cvn * \
                self.model.caretaker_carrying_amount

    def step(self) -> None:
        """
        Consume energy from the energy buffer and create new adult ants.
        The amount of energy required per new ant is a fixed constant.
        """
        offspring_count = int(self.energy_buffer /
                              self.model.energy_per_offspring)
        self.energy_buffer -= offspring_count * self.model.energy_per_offspring
        self.ant_birth(offspring_count)
