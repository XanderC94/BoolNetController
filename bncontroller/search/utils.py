from bncontroller.boolnet.structures import BooleanNetwork
from bncontroller.ntree.utils import tree_edit_distance, tree_histogram_distance
import random, collections, math

Flip = collections.namedtuple('Flip', ['label', 'entry'])

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

###########################################################################################

def sampling(flips, n_flips):

    return set(random.sample(flips, n_flips) if len(flips) >= n_flips else flips)

def ncombinations(n, k):
    return math.factorial(n) / (math.factorial(k) * math.factorial(n-k))

def identity(x): 
    return x

#############################################################################

ScrambleOutput = collections.namedtuple('ScrambleOutput', ['new_sol', 'edits'])

def bn_scramble_strategy(bn: BooleanNetwork, n_flips: int, excluded: set={}):
    '''
    Default scrambling strategy for vns algorithm.
    Scrambling = flips generation + boolean network edit

    returns the modified bn, the applied flips
    '''
    
    flips = generate_flips(bn, n_flips, excluded=set(map(hash, excluded)), flip_map=hash)
    bn = edit_boolean_network(bn, flips)

    return ScrambleOutput(new_sol=bn, edits=flips)

############################################################################################

def generate_available_flips(bn: BooleanNetwork, excluded=set(), flip_map=identity):

    free_flips = set()

    for node in bn.nodes:
        if flip_map(node.label) not in excluded:
            for i in range(2**node.arity):
                
                pFlip = Flip(node.label, i)

                if flip_map(pFlip) not in excluded:
                    free_flips.add(pFlip)

    return free_flips

#############################################################################################

def generate_flip(bn, excluded=set()):
    return generate_flips(bn, 1, excluded=excluded)

def generate_flips(bn: BooleanNetwork, n_flips, excluded=set(), flip_map=identity) -> set:
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

    free_flips = generate_available_flips(bn, excluded, flip_map)

    return sampling(free_flips, n_flips)

###################################################################################

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

    for label, i in flips:
        e, r = bn[label].bf.by_index(i)
        bn[label].bf[e] = 1.0 - r.bias

    return bn