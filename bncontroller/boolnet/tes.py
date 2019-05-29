from bncontroller.boolnet.bnstructures import BooleanNetwork
from bncontroller.ntree.ntstructures import NTree

def bn_to_tes(bn:BooleanNetwork, thresholds: list) -> NTree:
    """
        Return the tree representing the Threshold Ergodic Set -- TES
        associated with the BN 
    """
    return NTree.empty()