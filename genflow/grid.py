from mesa.space import MultiGrid
from nlmpy import nlmpy
import numpy as np


class PatchedMultiGrid(MultiGrid):

    def __init__(self, width, height, **kwargs):
        super().__init__(width, height, torus=False)
        self.land_coverage = kwargs.get('land_coverage', 0.5)
        self.land_algorithm = kwargs.get('land_algorithm', 'random')

    def generate_land(self):
        if self.land_coverage < 1:
            first = 1.0 - self.land_coverage
            second = self.land_coverage
            csquare = None
            if self.land_algorithm == 'random':
                csquare = nlmpy.random(self.height, self.width)
            elif self.land_algorithm == 'aggregate':
                csquare = nlmpy.randomClusterNN(self.height, self.width, .5)
            if csquare is None:
                raise Exception(self.land_algorithm)
            dsquare = nlmpy.classifyArray(csquare, [first, second])
        else:
            dsquare = np.ones((self.height, self.width))
        for y in range(self.height):
            for x in range(self.width):
                if dsquare[x][y] >= 1:
                    yield (x, y)
