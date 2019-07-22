import random
from singleton_decorator import singleton

@singleton
class StaticRandomGenerator(object):
    
    def __init__(self, seed=None):
        self.__seed = seed
        self.__random_gen = random.Random(seed)

    @property
    def random(self):
        return self.__random_gen
    
    @property
    def seed(self):
        return self.__seed

    @seed.setter
    def seed(self, seed):
        self.__seed = seed
        self.__random_gen = random.Random(seed)

