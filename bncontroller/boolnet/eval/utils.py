from bncontroller.boolnet.bnstructures import BooleanNetwork
from bncontroller.ntree.ntstructures import NTree
from bncontroller.ntree.ntutils import tree_edit_distance, tree_histogram_distance
import random


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

    node_label = random.choice([n for n in bn.keys if n not in last_flips])

    k = bn[node_label].bf.arity

    truthtable_index = random.choice(list(range(2**k))) 

    args, res = bn[node_label].bf.by_index(truthtable_index)

    return (node_label, args, 1.0 - res.bias)

def generate_flips(bn: BooleanNetwork, n_flips, last_flips = []):
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
    flips = []

    for _ in range(n_flips):
        flip = generate_flip(bn, last_flips + flips)
        flips.append(flip)
    
    return flips

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
        bn[last_flip].bf[args] = new_bias

    return (bn, list(map(lambda f: f[0], flips)))