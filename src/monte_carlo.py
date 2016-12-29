from random import random, randint
import numpy as np
import cost_function as cf
  
def random_tree(k):
    k=randint(1,k)
    cut_num = k
    leaf_num = k+1
    
    cuts = [('H' if random()<0.5 else 'V', randint(1,999)/1000) for _ in range(cut_num)]
    leaves = [" (L color)"  for _ in range(leaf_num)]
    
    for c in cuts:
        ran = randint(0, len(leaves)-2)
        leaves[ran] = " (%c %.3f"%(c[0],c[1])+leaves[ran]+leaves[ran+1]+')'
        del leaves[ran+1]
    
    s = "".join(leaves)[1:]

    return s

def monte_carlo(repeat_times, maxcut, target_image):
    min_cost = -1
    min_cost_solution = None
    for i in range(repeat_times):
        s = random_tree(maxcut)
        x, y, _ = target_image.shape
        matrix = cf.to_array(s, x, y, 1)
        c = cf.cost(matrix, target_image)
        if min_cost == -1 or c < min_cost:
            min_cost = c
            min_cost_solution = s

    return s, c
