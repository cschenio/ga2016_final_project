from random import random, randint
from pic import rgb2pic, pic2rgb
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color
import numpy as np
import pyparsing as pp
from cost_function import *

#colors=np.array([[255, 0, 0], [255, 255, 0], [0, 0, 255], [255, 255, 255]],dtype=np.uint8)
 
colors=[LabColor (lab_l=100.0000, lab_a=-0.0005, lab_b=-0.0086),
        LabColor (lab_l=53.2390, lab_a=80.0905, lab_b=67.2014),
        LabColor (lab_l=97.1388, lab_a=-21.5578, lab_b=94.4773),
        LabColor (lab_l=32.2994, lab_a=79.1914, lab_b=-107.8655)]

def M_recursive_fill(matrix, x_range, y_range, tree, line_width):
    if tree[0] == 'L':
        fill_color(matrix, x_range, y_range, choose_color(matrix, x_range, y_range, tree))
    elif tree[0] == 'H':
        try:
            sep = int((x_range[-1]+1 - x_range[0]) * float(tree[1]) + x_range[0])
            M_recursive_fill(matrix, range(x_range[0], sep - line_width), y_range, tree[2], line_width)
            M_recursive_fill(matrix, range(sep + line_width, x_range[-1]+1), y_range, tree[3], line_width)
            fill_color(matrix, range(sep - line_width, sep + line_width), y_range, LabColor(0, 0, 0))
        except IndexError:
            print("Resolution not enough, cut cannot be seen.")        
    elif tree[0] == 'V':
        try:
            sep = int((y_range[-1]+1 - y_range[0]) * float(tree[1]) + y_range[0])
            M_recursive_fill(matrix, x_range, range(y_range[0], sep - line_width), tree[2], line_width)
            M_recursive_fill(matrix, x_range, range(sep + line_width, y_range[-1]+1), tree[3], line_width)
            fill_color(matrix, x_range, range(sep - line_width, sep + line_width),  LabColor(0, 0, 0))
        except IndexError:
            print("Resolution not enough, cut cannot be seen.")

def choose_color(matrix, x_range, y_range, tree):

    error, choice= np.inf, []
    seg=matrix[x_range[0]:x_range[-1]+1][y_range[0]:y_range[-1]+1]

    for color in colors:
        color_matrix=[[] for _ in range(len(seg))]
        for i in range(len(seg)):
            for j in range(len(seg[i])):
                color_matrix[i].append(color)
        
        #print(color_matrix[0][0], seg[0][0])
        color_cost = cost(seg, np.array(color_matrix))
        if  color_cost < error: 
            error=color_cost
            choice=color
        
    a=convert_color(choice,sRGBColor)
    rgb_choice=[a.rgb_r*255, a.rgb_g*255, a.rgb_b*255]
    for i in range(3):
        tree[i+1]=str(rgb_choice[i])
    return choice
    
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