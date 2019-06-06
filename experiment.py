#!/usr/bin/env python
from genflow.model import GeneFlow


def run_model(population=200, generations=1000, **kwargs):
    height = 60
    width = 60
    params = {
        "dispersion": kwargs.get('dispersion', 5),
        "land_coverage": kwargs.get('coverage', 50),
        "land_algorithm": kwargs.get('land', 'random'),
    }
    prefix = kwargs.get('prefix', 'gf')
    suffix = kwargs.get('suffix', '01')
    model = GeneFlow(
        height=height,
        width=width,
        population=population,
        **params
        )

    for i in range(generations+1):
        if i % 50 == 0:
            print('step %d' % i)
        model.step()

    # results = model.datacollector.get_model_vars_dataframe()
    aresults = model.datacollector.get_agent_vars_dataframe()
    # results.to_csv('model_%d.csv' % population)
    agent_filename = "../data/%s_%sx%s_%s_%s_%s_%s_%s_%s.csv" % (
        prefix, height, width, generations, population,
        params['dispersion'], params['land_coverage'],
        params['land_algorithm'][0:3], suffix
    )
    aresults.to_csv(agent_filename)


def experiment01(landscape="aggregate", n=5,
                 coverage=[i * 10 for i in range(1, 10)],
                 prefix='ex01'):
    # run simulation for random-agregate landscape
    # at several levels of coverage
    for percent in coverage:
        print("coverage %s" % percent)
        for rep in range(n):
            print("repetion %s" % rep)
            params = {
                'prefix': prefix,
                'land': landscape,
                'coverage': percent,
                'suffix': "%02d" % (rep + 1)
            }
            run_model(**params)


def experiment02():
    # run simulation for random landscape
    experiment01('random', prefix='ex02')


def experiment03():
    #
    # run simulation for random landscape
    # near of percolation treshold
    #
    params = {
        "generations": 500,
        "dispertion": 1,
        "land": 'random',
        "prefix": 'pe01',
    }
    for percent in range(20, 40, 5):
        print("coverage %s" % percent)
        params['coverage'] = percent
        for rep in range(1, 6):
            print("repetion %s" % rep)
            params['suffix'] = '%02d' % rep
            run_model(**params)


if __name__ == '__main__':

    experiment01()
    experiment02()
