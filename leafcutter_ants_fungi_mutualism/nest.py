from mesa import Agent
import queue
from .ant_agent import AntAgent, AntWorkerState


class Nest(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.energy_buffer = 0.0
        # both queues have the same size at the moment
        self.forager_fitness_queue = queue.Queue(self.model.max_fitness_queue_size)
        self.fungus_fitness_queue = queue.Queue(self.model.max_fitness_queue_size)

    def get_fitness_q_lists(self):
        return list(self.forager_fitness_queue.queue), list(self.fungus_fitness_queue.queue)


    def ant_birth(self, n):
        forager_fitness_queue_list, fungus_fitness_queue_list = self.get_fitness_q_lists()
        if len(forager_fitness_queue_list) != 0:
            average_forager_fitness = sum(forager_fitness_queue_list)/len(forager_fitness_queue_list)
        else:
            average_forager_fitness = 0.5

        if len(fungus_fitness_queue_list) != 0:
            average_fungus_fitness = sum(fungus_fitness_queue_list)/len(fungus_fitness_queue_list)
        else:
            average_fungus_fitness = 0.5

        forager_fitness_weight = 0.5
        average_fitness = \
            forager_fitness_weight * average_forager_fitness + \
            (1 - forager_fitness_weight) * average_fungus_fitness

        for _ in range(n):
            state = AntWorkerState.EXPLORE

            if self.random.random() > average_fitness:
                state = AntWorkerState.CARETAKING

            agent = AntAgent(self.model.next_id(), self.model, state=state)

            self.model.schedule.add(agent)
            self.model.grid.place_agent(agent, self.pos)

    def feed_larvae(self):
        if self.model.fungus.biomass > self.model.fungus_biomass_death_threshold + 2 * self.model.energy_per_offspring:
            self.model.fungus.biomass -= self.model.caretaker_carrying_amount
            # `fungus_larvae_cvn` defaults to 1.0
            self.energy_buffer += self.model.fungus_larvae_cvn*self.model.caretaker_carrying_amount

    def step(self):
        offspring_count = int(self.energy_buffer /
                              self.model.energy_per_offspring)
        self.energy_buffer -= offspring_count * self.model.energy_per_offspring
        self.ant_birth(offspring_count)
