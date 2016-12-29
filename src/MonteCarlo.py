from random import random, randint
from pic_sk import rgb2pic, pic2rgb
from skimage.color import lab2rgb, rgb2lab
import numpy as np
import pyparsing as pp
from cost_function import *

#colors=np.array([[255, 0, 0], [255, 255, 0], [0, 0, 255], [255, 255, 255]],dtype=np.uint8)
 
colors=[[100.0000, -0.0005, -0.0086],
        [53.2390, 80.0905, 67.2014],
        [97.1388, -21.5578, 94.4773],
        [32.2994, 79.1914, -107.8655]]

def M_recursive_fill(matrix, x_range, y_range, tree, line_width):
    if tree[0] == 'L':
        fill_color(matrix, x_range, y_range, choose_color(matrix, x_range, y_range, tree))
    elif tree[0] == 'H':
        try:
            sep = int((x_range[-1]+1 - x_range[0]) * float(tree[1]) + x_range[0])
            M_recursive_fill(matrix, range(x_range[0], sep - line_width), y_range, tree[2], line_width)
            M_recursive_fill(matrix, range(sep + line_width, x_range[-1]+1), y_range, tree[3], line_width)
            fill_color(matrix, range(sep - line_width, sep + line_width), y_range, [0, 0, 0])
        except IndexError:
            print("Resolution not enough, cut cannot be seen.")        
    elif tree[0] == 'V':
        try:
            sep = int((y_range[-1]+1 - y_range[0]) * float(tree[1]) + y_range[0])
            M_recursive_fill(matrix, x_range, range(y_range[0], sep - line_width), tree[2], line_width)
            M_recursive_fill(matrix, x_range, range(sep + line_width, y_range[-1]+1), tree[3], line_width)
            fill_color(matrix, x_range, range(sep - line_width, sep + line_width),  [0, 0, 0])
        except IndexError:
            print("Resolution not enough, cut cannot be seen.")

def choose_color(matrix, x_range, y_range, tree): 
    min_error = -1
    min_error_color = None
    for c in colors:
        sum = 0.0
        for i in x_range:
            for j in y_range:
                dist = deltaE_ciede2000([matrix[i][j]], [c])
                sum += dist
        if min_error == -1 or sum < min_error:
            min_error = sum
            min_error_color = c

    rgb_choice=lab2rgb([[min_error_color]])
    #print(min_error_color)
    for i in range(3):
        tree[i+1]=str(int(rgb_choice[0][0][i]*255))
    return min_error_color
    
# M_to_array: string(sexp) -> np.array(size_x, size_y, 3)
def M_to_array(str_sexp, matrix, size_x=640, size_y=640, line_width=5):

    tree = parse_sexp(str_sexp)    
    M_recursive_fill(matrix, range(0, size_x), range(0, size_y), tree[0], line_width)

    return matrix, tree
  
    
def random_tree(k, matrix, width=100, height = 100, line_width=5):
    k=randint(1,k)
    cut_num = k
    leaf_num = k+1
    
    cuts = [('H' if random()<0.5 else 'V', randint(1,999)/1000) for _ in range(cut_num)]
    leaves = [" (L 0 0 0)"  for _ in range(leaf_num)]
    
    for c in cuts:
        ran=randint(0, len(leaves)-2)
        leaves[ran]=" (%c %.3f"%(c[0],c[1])+leaves[ran]+leaves[ran+1]+')'
        del leaves[ran+1]
    
    s = "".join(leaves)[1:]

    matrix, tree = M_to_array(s, matrix, width, height, 1)
    
    str_tree=("%s"%tree)[1:-1]
    re=[("'",''), (",",''), ('[','('), (']',')')]
    for t in re:
        str_tree=str_tree.replace(t[0],t[1])
    
    #rgb2pic(matrix)
    return str_tree
    
#print(random_tree(5, pic2rgb('1.jpg'), 100, 100, 1)) #return a lisp tree string