from bnstructure import BooleanNetwork, BooleanNode
from ntree import NTree

def bn_to_tes(bn:BooleanNetwork, thresholds: list) -> NTree:
    """
        Return the tree representing the Threshold Ergodic Set -- TES
        associated with the BN 
    """
    return NTree.empty()