from bncontroller.boolnet.structures import BooleanNetwork
from bncontroller.ntree.structures import NTree

def bn_to_tes(bn:BooleanNetwork, thresholds: list) -> NTree:
    """
        Return the tree representing the Threshold Ergodic Set -- TES
        associated with the BN 
    """
    return NTree.empty()