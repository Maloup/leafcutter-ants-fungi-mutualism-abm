"""
Configure visualization elements and instantiate a server
"""

from .model import (
    LeafcutterAntsFungiMutualismModel, AntAgent, Plant, Nest
)
from .pheromone import Pheromone

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule


def circle_portrayal_example(agent):
    if agent is None:
        return

    if isinstance(agent, AntAgent):
        portrayal = {
            "Shape": "circle", #"leafcutter_ants_fungi_mutualism/resources/ant.png"
            "Color": "brown",
            "Layer": 1,
            "Filled": True,
            "r": 0.6
        }

        if agent.has_leaf:
            portrayal["text"] = "leaf"
            portrayal["text_color"] = "green"

        return portrayal
    elif isinstance(agent, Plant):
        return {
            "Shape": "circle", #"leafcutter_ants_fungi_mutualism/resources/plant.png"
            "Color": "green",
            "Layer": 0,
            "r": agent.num_leaves/agent.initial_num_leaves
        }
    elif isinstance(agent, Nest):
        return {
            "Shape": "circle",
            "Color": "black",
            "Layer": 0,
            "r": 1
        }
    elif isinstance(agent, Pheromone):
        return {
            "Shape": "circle",
            "Color": "blue",
            "Layer": 0,
            "r": agent.lifespan/agent.initial_lifespan
        }
    else:
        print(f"Not yet visualized agent {agent.__class__}!")
        return {
            "Shape": "circle",
            "Color": "red",
            "Layer": 0,
            "r": 0.75
        }

canvas_element = CanvasGrid(circle_portrayal_example, 50, 50, 650, 650)
chart_element = ChartModule([{
    "Label": "Fungus Energy",
    "Color": "Black"
}], data_collector_name="datacollector")

model_kwargs = {"num_ants": 50, "num_plants": 20, "width": 50, "height": 50}

server = ModularServer(
    LeafcutterAntsFungiMutualismModel,
    [canvas_element, chart_element],
    "LeafcutterAntsFungiMutualism",
    model_kwargs,
)
