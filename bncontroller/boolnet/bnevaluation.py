from bnstructure import BooleanNetwork
from boolean import Boolean, r_bool, truth_values
from booleanfunction import BooleanFunction
from ntree import NTree
from ntreeutils import tree_edit_distance, tree_histogram_distance
from tes import bn_to_tes
from pathlib import Path
from utils import read_json, write_json
from bnevaluation_config import EvaluationConfig
import random, math, queue, copy, subprocess, datetime

def tes_distance(C, T) -> float:
    """
    Objective Function for the Search Processes

        f = E + (E * H) 
    
    where:

        * E is the trees edit distance
        * H is the trees histogram distance

    """
    E = tree_edit_distance(C, T)
    H = tree_histogram_distance(C, T)
    
    return E + (E * H)

def generate_flip(bn: BooleanNetwork, last_flips = []):
    """
    Given the BN and a list of node_id to be excluded from the flipping,
    returns a tuple representing the change (flip) to apply to the BN.
    
    The tuple structure is defined as follow
    
        (node_id, truth_table_entry, new_bias)
    
    where:
        * node_id is the "name" of the node in the BN.
        * bf_args is a tuple of bool representing the entry of the (node) truth table
        which output value has to be flipped.
        * new_bias is the flipped output of the (node) truth table.
    """

    nid = random.choice([n for n in bn.keys() if n not in last_flips])

    k = bn[nid].boolfun.get_k()

    ttidx = random.choice(list(range(2**k))) 

    args, res = bn[nid].boolfun.by_index(ttidx)

    return (nid, args, 1.0 - res.bias())

def generate_flips(bn: BooleanNetwork, last_flips = []):
    """
    Given the BN and a list of node_id to be excluded from the flipping,
    returns a list of tuples representing the changes (flips) to apply to the BN.
    
    The tuple structure is defined as follow
    
        (node_id, truth_table_entry, new_bias)
    
    where:
        * node_id is the "name" of the node in the BN.
        * bf_args is a tuple of bool representing the entry of the (node) truth table
        which output value has to be flipped.
        * new_bias is the flipped output of the (node) truth table.
    """
    return list(generate_flip(bn, last_flips) for _ in last_flips)

def edit_boolean_network(bn: BooleanNetwork, flips: list):
    """
    Given the BN and a list of flips to apply to the BN,
    returns the modified BN (ndr: it doesn't create a new one)
    paired with the node_id(s) of the flipped nodes.
    
    A flip is a tuple and its structure is defined as follow
    
        (node_id, truth_table_entry, new_bias)
    
    where:
        * node_id is the "name" of the node in the BN.
        * bf_args is a tuple of bool representing the entry of the (node) truth table
        which output value has to be flipped.
        * new_bias is the flipped output of the (node) truth table.
    """

    for last_flip, args, new_bias in flips:
        bn[last_flip].boolfun[args] = new_bias

    if len(flips) == 1:
        return (bn, flips[0][0])
    else:
        return (bn, list(map(lambda f: f[0], flips)))

def adaptive_walk(n, k, p, target_tes, thresholds:list, maxIter = 10000):
    """ 
    A simple technique of local search that performs a stochastic descent.
    Starts from a randomly generated boolean network and after the execution 
    of each move then the resulting solution is accepted if it is not worse than
    the current solution. 
    
    A move consists in a flip, from 0 to 1 or vice versa, of a random entry 
    in the truth table of a randomly chosen node.
    
    This algorithm allows moves that produce solutions with values of the 
    objective function equal to the current one, sideways moves; this way we prevent that
    the algorithm gets trapped in local minima. In order not to evaluate twice
    the same network has been introduced an optimization: we don’t allow to repeat 
    the flip of the previous step. 
    The objective function to minimize, is defined as a combination of two measures
    both related to the differences between the differentiation tree produced 
    by the current network and the target differentiation tree. 
    
    The search process terminates when the objective function reaches zero 
    (the found differentiation tree corresponds to the desired one) 
    or when the number of maximum iterations are reached. 
    
    In particular the two used measures are the tree edit distance and
    the histogram distance. 

    """

    bn = BooleanNetwork(n, k, bfInit= lambda *args: Boolean(r_bool(p)))
    tes = bn_to_tes(bn, thresholds)
    dist = tes_distance(tes, target_tes)
    sol = bn

    it, last_flip = 0, -1

    while it < maxIter and dist > 0:

        flips = generate_flip(sol, [last_flip])
        bn, last_flip = edit_boolean_network(bn, flips = [flips])
        tes = bn_to_tes(bn, thresholds)
        _dist = tes_distance(tes, target_tes)

        if _dist > dist:
            bn = sol
        else:
            dist = _dist
            sol = bn
        
        it += 1

    return sol

def variable_neighborhood_search(n, k, p, target_tes, thresholds:list, maxIter = 10000, maxStall = 10):
    """
    Metaheuristic technique highly inspired by the Variable Neighbourhood Search (VNS) and 
    proposed in

        Nenad Mladenovic and Pierre Hansen. Variable neighborhood search.
        Computers & Operations Research, 24(11):1097–1100, 1997

    The algorithm that we propose is an evolution of the previously presented
    algorithm, Adaptive Walk. The Adaptive Walk algorithm starts with a randomly 
    chosen network and applies an intensification strategy by making a flip 
    to an output entry at a time. However in this way the search process,
    depending on the starting solution, might get stuck into local minima with
    no possibilities to escape from them or into areas of the search landscape that
    does not present “good” quality solutions. For this reason we have added a
    diversification strategy to our VNS-like algorithm. 
    The process of diversification is implemented by increasing the number of 
    flips if the search process does not find a better solution than 
    the current one for a given number of steps. 
    A better solution corresponds to a Boolean network able to express a
    differentiation dynamics more similar to the desired one: with a lower value
    of objective function than to the one obtained by the current network

    The increasing of the number of random flips aids the search process to 
    escape from local minima and it is similar to the change of neighborhood 
    in case of no improvements that is present in the classical VNS. 
    As soon as a better solution is found, the number of flip is brought back to one 
    and so the intensification process restarts until the objective function reaches 
    zero or the number of maximum iterations is reached. 
    When the number of flip is equal to one this algorithm behaves like
    the Adaptive Walk.

    """
    bn = BooleanNetwork(n, k, bfInit= lambda *args: Boolean(r_bool(p)))
    tes = bn_to_tes(bn, thresholds)
    dist = tes_distance(tes, target_tes)
    sol = bn

    it, last_flips, nStall, nFlips = 0, -1, 0, 1

    while it < maxIter and dist > 0:

        if nStall == maxStall:
            nStall = 0
            nFlips += 1

            if nFlips > len(bn): 
                return sol

        flips = generate_flips(sol, last_flips)
        bn, last_flips = edit_boolean_network(bn, flips)

        tes = bn_to_tes(bn, thresholds)
        _dist = tes_distance(tes, target_tes)

        if _dist > dist:
            bn = sol
        else:

            if dist == _dist:
                nStall += 1
            else:
                nStall = 0
                nFlips = 1

            dist = _dist
            sol = bn

        it += 1

    return sol

#########################################################################################################

def run_simulation(config : EvaluationConfig, model) -> dict:
    date = f'{datetime.datetime.now():%Y-%m-%dT%H-%M-%S}'
    write_json(model, config.bn_model_dir / f'bn_model_{date}.json')
    subprocess.run([str(config.webots_path), *config.webots_launch_args, str(config.webots_world_path)])


def aggregate_sym_data(path:Path) -> dict:
    return {}

def custom_vns(n, k, p, simulation = lambda *args: str(*args), maxIter = 10000, maxStall = 1):
    """
    """
    bn = BooleanNetwork(n, k, bfInit= lambda *args: Boolean(r_bool(p)))
    sol = bn
    # run agent with flipped network simulation
    data_path = simulation(bn)
    dist = float('inf')
    it, last_flips, nStall, nFlips = 0, -1, 0, 1

    while it < maxIter and dist > 0:

        if nStall == maxStall:
            nStall = 0
            nFlips += 1

            if nFlips > len(bn): 
                return sol

        flips = generate_flips(sol, last_flips)
        bn, last_flips = edit_boolean_network(bn, flips)

        # run agent with flipped network simulation
        data_path = simulation(bn)

        _dist = random.random() # Read Symulation values

        if _dist > dist:
            bn = sol
        else:

            if dist == _dist:
                nStall += 1
            else:
                nStall = 0
                nFlips = 1

            dist = _dist
            sol = bn

        it += 1

    return sol


if __name__ == "__main__":
    
    bn = adaptive_walk(5, 1, 0.666, NTree.empty(), [], maxIter=100000)

    print(bn)
