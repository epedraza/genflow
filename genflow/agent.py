from mesa import Agent
from numpy import random
from uuid import uuid4
from math import sin, cos
import numpy as np

class LandPatch(Agent):
    """
    And patch of land situable for place a tree
    """
    def __init__(self, unique_id, position, model):
        super().__init__(unique_id, model)
        self.pos = position
        self.gen = 0

    def step(self):
        """
           do nothing
        """
        self.gen += 1

class Tree(Agent):
    """
        Tree agent
    """
    dispersion = 0

    def __init__(self, tree_id,  pos, model, is_parent=True):
        super().__init__(tree_id, model)
        self.x, self.y = pos
        self.model = model
        self.is_parent = is_parent
        self.genome = (None, None)
        self._nextState = None
        self.age = 0
        self.born = self.model.nstep

    @property
    def position(self):
        return (self.x, self.y)

    def set_genome(self, gamete_one, gamete_two):
        self.genome = (gamete_one, gamete_two)

    def get_gamete(self):
        gamete = random.choice(self.genome)
        if self.model.can_mutate():
            gamete = self.model.mutate(gamete)
        return gamete

    def in_range(self, position, max_position, min_position=0):
        if position > max_position:
            return max_position
        if position < min_position:
            return min_position
        return position

    def child_position(self):
        inds = self.model.patches_index.query_radius(
            [self.pos],
            r=self.model.dispersion)
        index = np.random.choice(inds[0])
        position = tuple(self.model.patches[index])
        return position

    def reproduce(self):
        partner = self.model.find_partner(self.position)
        gamete_one = self.get_gamete()
        gamete_two = partner.get_gamete()
        position = self.child_position()
        tree_id = self.model.get_tree_id()
        child = Tree(tree_id, position, self.model, is_parent=False)
        child.set_genome(gamete_one, gamete_two)
        self.model.add_agent(child, position)
        return child

    def find_partner(self):
        neighbors = self.model.grid.get_neighbors(
            self.position, True, True, self.model.dispersion
        )
        trees = [n for n in neighbors if type(n) is Tree and n.age == 0]
        trees.append(self)
        mate = random.choice(trees)
        return mate

    def step(self):
        self.age += 1
        if self.age == 1:
            self.reproduce()
        elif self.age == 2:
            self.model.remove_agent(self)

