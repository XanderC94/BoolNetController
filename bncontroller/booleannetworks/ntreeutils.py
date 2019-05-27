import random, math, queue, apted
from itertools import chain
from collections import defaultdict
from ntree import NTree

bracket_notation_template = "{{{label}{children}}}"

def to_apted_notation(t:NTree) -> str:
    """ 
    Convert a Ntree to a string in bracket-notation

        {A{B{C}{D}{E}}{F}}

    corresponds to

                  A
                /   \
               B     F
             / | \
            C  D  E 

    """

    if t is None or t.is_empty(): 
        return ''
    else: 
        return bracket_notation_template.format(
            label = t.label(), 
            children = ''.join(to_apted_notation(c) for c in t.children)
        )

def tree_edit_distance(C:NTree, T:NTree) -> float:
    """ 
    The tree edit distance between C and T is the minimum cost sequence 
    of node edit operations (node deletion, node insertion, node rename) 
    that transforms one tree into the other.

    See: <http://tree-edit-distance.dbresearch.uni-salzburg.at/>
    """
    
    return apted.APTED(C, T).compute_edit_distance()

def tree_level_arities(nodes: list) -> dict:
    """
    Returns an Histogram (dict) where each key is a cardinality (the number of children)
    while the values are the number of nodes with such cardinality
    """
    arities = defaultdict(int)

    for node in nodes:arities[len(node.children)] += 1
        
    return dict(arities) 

def tree_histogram_distance(C : NTree, T: NTree) -> float:
    """ 
    The histogram distance is a similarity measure between the current tree (C) and the target tree (T), and is defined as:

    d = sum[l=0 -> l*](sum[k=0 -> k*](abs(n_C(k, l) − n_D(k, l)))

    where l* stands for the maximum depth and k∗ stands for the maximum number of children nodes in both trees. 
    The function n_C(k, l) computes the number of nodes at the level l with k children in the current tree, 
    and n_D(k, l) respectively for the desired tree.

    This way the histogram distance gives a measure of the structural similarity, level by level, between the two trees;
    obviously, the lesser the histogram distance is the more similar are the two trees.
    However the histogram distance can result zero even if the two trees in exam are different: 
    this may occur because this measure takes into consideration one level at a time.
    """

    levelc, levelt = [C], [T]
    hdist = 0
   
    while len(levelc) > 0 or len(levelt) > 0:
        
        ac, at = tree_level_arities(levelc), tree_level_arities(levelt)

        arities = defaultdict(int)

        for k, v in chain(ac.items(), at.items()):
            arities[k] = abs(arities[k] - v)

        hdist += sum(list(arities.values()))
        
        levelc = list(chain.from_iterable(n.children for n in levelc))
        levelt = list(chain.from_iterable(n.children for n in levelt))
       
    return hdist

if __name__ == "__main__":
    
    t1 = NTree(1, [ 
            NTree(2, [], 2), 
            NTree(3, [
                NTree(4, [], 4)
            ], 3) 
        ], 1)

    t2 = NTree(1, [ 
            NTree(2, [], 2), 
            NTree(3, [
                # NTree(4, [], 4)
            ], 3) 
        ], 1)


    print(tree_histogram_distance(t1, t2))

    print(to_apted_notation(t1))
    print(to_apted_notation(t2))
    print(apted.APTED(t1, t2).compute_edit_distance())
