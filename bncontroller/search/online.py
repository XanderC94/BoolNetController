from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.search.parametric import default_scramble_strategy, comparators
from bncontroller.search.utils import edit_boolean_network

def online_evaluation(bn: OpenBooleanNetwork, sensors_values: dict):
    pass

class OnlineVNSData(object):

    def __init__(self, 
            bn: OpenBooleanNetwork, 
            score: object,
            excluded: set,
            n_it: int, max_it: int,
            n_stalls: int, max_stalls: int,
            n_flips: int, max_flips: int,
            n_stagnation: int, max_stagnation:int
        ):

        self.bn = bn
        self.score = score
        self.n_it = n_it
        self.max_it = max_it
        self.n_stalls = n_stalls
        self.max_stalls = max_stalls
        self.n_flips = n_flips
        self.max_flips = max_flips
        self.n_stagnation = n_stagnation
        self.max_stagnation = max_stagnation
        self.excluded = excluded

#########################################################################

def onlineVNS(
        monad:OnlineVNSData,
        evaluate=lambda bn:online_evaluation(bn, {}), 
        scramble=default_scramble_strategy, 
        compare=comparators.lesser):

    if monad.score is None:
        monad.score = evaluate(monad.bn)
    else:
        # monad.max_flips = sum(2**n.arity for n in monad.bn.nodes if n not in monad.bn.input_nodes)
    
        monad.bn, flips, monad.excluded = scramble(monad.bn, monad.n_flips, monad.excluded)

        new_score = evaluate(monad.bn)
        
        if compare(new_score, monad.score):

            monad.score = new_score

        else:

            monad.bn = edit_boolean_network(monad.bn, flips)

            monad.n_stagnation += 1
            monad.n_stalls += 1
            
            if monad.max_stalls > 0 and monad.n_stalls >= monad.max_stalls:
                monad.n_stalls = 0
                monad.n_flips += 1
                    
            monad.it += 1

    return monad