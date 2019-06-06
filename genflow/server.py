from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from genflow.model import GeneFlow, GENOME_LENGTH
from genflow.agent import Tree, LandPatch

GENOME_SIZE = GENOME_LENGTH * 2

land_coverage = UserSettableParameter(
    'slider', 'Área habitable (%)',
    50, 5, 100, 5
)

land_algorithm = UserSettableParameter(
    'choice', 'Arquitectura',
    'random', choices=('random', 'aggregate')
)

population = UserSettableParameter(
        'slider', 'Tamaño de la población',
        30, 10, 200, 10
        )

dispersion = UserSettableParameter(
    'slider',
    'Distancia de dispersión',
    3, 1, 15, 1
)



def hex_color(count):
    hex_count = hex(round((count * 255) / GENOME_SIZE)).split('x')[1]
    if len(hex_count) == 1:
        hex_count = '0' + hex_count
    return hex_count


def get_color(agent):
    # convert the genotype to a color
    genome = agent.genome
    bases = list(genome[0]) + list(genome[1])
    count = {'red': 0, 'green': 0, 'blue': 0}
    for b in bases:
        if b == 'a':
            count['red'] += 1
        elif b == 'g':
            count['blue'] += 1
        else:
            count['green'] += 1
    green = hex_color(count['green'])
    blue = hex_color(count['blue'])
    red = hex_color(count['red'])
    return '#' + red + green + blue

TREE_AGES = {0: 0, 1: 0.25, 2: 0.75}


def agent_portrayal(agent):
    if agent is None:
        return

    portrayal = {}
    if type(agent) is LandPatch:
        portrayal = {
            'Color': "#f1f1f1",
            'Shape': "rect",
            'Filled': "true",
            'Layer': 0,
            'w': 1,
            'h': 1
        }
    elif type(agent) is Tree:

        color = get_color(agent)
        radio = 0.5 + TREE_AGES[agent.age]
        portrayal = {
            "Shape": "circle",
            "Color": color,
            "Filled": "true",
            "Layer": 1,
            "r": radio,
            "Label": "%s-%s-%s" % (agent.unique_id, agent.pos, agent.born)
        }
    return portrayal


WIDTH = 30
HEIGHT = 30
RATIO = 10

grid = CanvasGrid(agent_portrayal, WIDTH, HEIGHT,
                  WIDTH * RATIO, HEIGHT * RATIO)

server = ModularServer(
    GeneFlow,
    [grid],
    "Gene Flow",
    {
        "land_coverage": land_coverage,
        "land_algorithm": land_algorithm,
        "population": population,
        "dispersion": dispersion,
        "width": WIDTH,
        "height": HEIGHT
    }
)
