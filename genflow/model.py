from mesa import Model
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from genflow.agent import Tree, LandPatch
from numpy import random
from genflow.grid import PatchedMultiGrid
from sklearn.neighbors import BallTree
import numpy as np

GENOME_LENGTH = 6
MUTATION_RATE = 100
DNA_ALPHABET = list('agc')


def count_parents(model):
    return len(model.schedule.parents)


class TreeScheduler(RandomActivation):

    @property
    def parents(self):
        return [a for a in self.agents if type(a) is Tree and  a.is_parent]


class GeneFlow(Model):
    '''
    2d geografic area for gene flow modeling
    '''
    def __init__(self, height=50, width=50, population=50, **kwargs):
        '''
        Create the space
        '''
        self.height = height
        self.width = width
        self.dispersion = kwargs.get('dispersion', 3)
        self.land_coverage = kwargs.get('land_coverage', 50) / 100
        self.land_algorithm = kwargs.get('land_algorithm', 'random')
        self.genome_length = GENOME_LENGTH
        self.chromosome = DNA_ALPHABET[0] * self.genome_length
        self.original_genome = (self.chromosome, self.chromosome)
        self.gamete_step = 0
        self.schedule = TreeScheduler(self)
        self.grid = PatchedMultiGrid(
            height, width,
            land_coverage=self.land_coverage,
            land_algorithm=self.land_algorithm)
        patches = []
        self.nstep = 0
        self.last_step = -1
        self.population = population
        self.individuals = 0
        for position in self.grid.generate_land():
            land = LandPatch(position, position, self)
            self.grid.place_agent(land, position)
            patches.append(position)
        total_patches = len(patches)
        self.patches = np.array(patches)
        self.patches_index = BallTree(self.patches)
        for i in range(population):
            index = np.random.randint(0, total_patches)
            position = tuple(self.patches[index])
            tree_id = self.get_tree_id()
            tree = Tree(tree_id, position, self)
            tree.set_genome(*self.original_genome)
            self.add_agent(tree, position)
        self.datacollector = DataCollector(
            model_reporters={'adults': count_parents},
            agent_reporters={
                'x': lambda a: a.x,
                'y': lambda a: a.y,
                'generation': lambda a: a.born,
                'age': lambda a: a.age,
                'gamete1': lambda a: a.genome[0],
                'gamete2': lambda a: a.genome[1]
            }
        )
        self.running = True


    def add_agent(self, agent, position):
        self.grid.place_agent(agent, position)
        self.schedule.add(agent)

    def remove_agent(self, agent):
        self.grid._remove_agent((agent.x, agent.y), agent)
        self.schedule.remove(agent)

    def mutate(self, gamete):
        position = random.randint(0, self.genome_length)
        change = random.choice(DNA_ALPHABET)
        gamete = list(gamete)
        gamete[position] = change
        gamete = "".join(gamete)
        return gamete

    def can_mutate(self):
        response = False
        step = self.gamete_step % MUTATION_RATE
        if step == 0:
            self.mutate_step = random.randint(0, MUTATION_RATE)
        if step == self.mutate_step:
            response = True
        self.gamete_step += 1
        return response

    def get_random_position(self):
        x = self.random.randrange(self.width)
        y = self.random.randrange(self.height)
        return (x, y)

    def get_tree_id(self):
        tree_id = "%s_%s" % (self.nstep, self.individuals % self.population)
        self.individuals += 1
        return tree_id

    def find_partner(self, position):
        search = self.parents_index.query_radius(
            [position],
            r=self.dispersion
        )
        positions = [self.parents[i] for i in search[0]]
        agents = self.grid.get_cell_list_contents(positions)
        return np.random.choice([a for a in agents if self.is_parent(a)])

    def is_parent(self, agent):
        return type(agent) == Tree and agent.born == self.last_step

    def step(self):
        # index parents positions
        self.parents = [t.pos for t in self.schedule.agents if t.born ==
                self.nstep]
        self.parents_index = BallTree(np.array(self.parents))
        self.last_step = self.nstep
        collect_data = self.nstep % 50 == 0
        self.nstep += 1

        if collect_data:
            self.datacollector.collect(self)
        self.schedule.step()
        for agent in self.schedule.agents:
            if agent.age == 1:
                self.remove_agent(agent)
