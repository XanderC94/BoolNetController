import itertools, random, string, math, time

truthValues = [False, True]

# Return a Random bool between [False, True] with p=0.5 for both
rBool = lambda : random.choice(truthValues)

class Boolean(object):
    """

    A Probabilistic (and Deterministic) Boolean variable implementation.

    * A Probabilistic Boolean variable holds both True and False 
    with different bias/probability.
    Only evaluation may tell which value holds at one time.
    Peeking a probabilistic Boolean before any evaluation always holds False.

    * A Deterministic Boolean variable holds always True or False at any time.
    A Deterministic Boolean is a Probabilistic Boolean 
    with Truth bias equal to 1.0 (holds True) or 0.0 (holds False)

    """
    def __init__(self, truth):
        self.setTruth(truth)      
    
    
    def truth(self):
        """ 
        Return the truth value (float) of the Boolean Variable.

        Truth values equals to 1.0 or 0.0 are proper of a Deterministic Boolean variables.
        Truth values in (0.0, 1.0) are proper of Probabilistic Boolean variables
        """
        return self.__truth

    def setTruth(self, newTruthValue):
        
        self.__truth = self.__check_truth_compliance(newTruthValue)
        self.__strategy = BooleanStrategy.factory(newTruthValue)

    def __check_truth_compliance(self, truth) -> float:
        if isinstance(truth, bool):
            return float(truth)
        elif isinstance(truth, (float, int)):
            return min(1.0, truth) if truth > 0 else 0.0
        else:
            raise Exception(f'Boolean Variable does not accept {type(truth)} as truth values.')
    
    def __bool__(self):
        return self.__strategy()
    
    def __call__(self):
        return self.__strategy()

    def __str__(self):
        return str({'0':1 - self.__truth, '1':self.__truth})
        
    def toJson(self) -> dict:
        """
        Return a (valid) json representation (dict) of this object
        """
        return {'0':1 - self.__truth, '1':self.__truth}
    
    @staticmethod
    def fromJson(json:dict):
        return Boolean(json['1'])

###########################################################################################

class BooleanStrategy(object):

    def __bool__(self):
        pass
    
    def __call__(self):
        pass

    @staticmethod
    def factory(truth):
        if truth == 1.0 or truth == 0.0:
            return DeterministicStrategy(truth)
        else:
            return ProbabilisticStrategy(truth)

class DeterministicStrategy(BooleanStrategy):
    
    def __init__(self, truth):
        self.__truth = truth
    
    def __bool__(self):
        return bool(self.__truth)
    
    def __call__(self):
        return bool(self.__truth)

class ProbabilisticStrategy(BooleanStrategy):

    def __init__(self, truth):
        self.__truth = truth
    
    def __call__(self):
        return random.choices(truthValues, weights=[1 - self.__truth, self.__truth])[0]
         
    def __bool__(self):
        return self()
    
##########################################################################################

if __name__ == "__main__":
    
    nIter = 1000000
    
    pbv = Boolean(0.85)
    
    dbv = Boolean(False)
    
    for i  in range(10):
        print(dbv(), pbv())

    print(f"Performances on {nIter} iterations:")
    ######################################
    b = False
    boolean = lambda: b

    t = time.perf_counter()

    for i  in range(nIter):
        # print(dbv, pbv)
        boolean()
    
    print("Simple bool function call:", time.perf_counter() - t)
    #####################################
   
    t = time.perf_counter()

    for i  in range(nIter):
        dbv()

    print("Deterministic:", time.perf_counter() - t)
    #######################################
    t = time.perf_counter()

    for i  in range(nIter):
        pbv()

    print("Probabilistic:", time.perf_counter() - t)