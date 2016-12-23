from random import random, randint
from pic import rgb2pic, pic2rgb
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color
import numpy as np
import pyparsing as pp
from cost_function import *

colors=np.array([[255, 0, 0], [255, 255, 0], [0, 0, 255], [255, 255, 255]],dtype=np.uint8)
#colors=[LabColor(lab_l=0.0000 lab_a=0.0000 lab_b=0.0000),LabColor(lab_l:100.0000 lab_a:-0.0005 lab_b:-0.0086),LabColor(lab_l:53.2390 lab_a:80.0905 lab_b:67.2014),LabColor(lab_l:97.1388 lab_a:-21.5578 lab_b:94.4773),LabColor(lab_l:32.2994 lab_a:79.1914 lab_b:-107.8655)]
# cost: np.array(size_x, size_y, 3) , np.array(size_x, size_y, 3) -> float


def M_recursive_fill(matrix, x_range, y_range, tree, line_width):
    if not x_range or not y_range: return
    if tree[0] == 'L':
        fill_color(matrix, x_range, y_range, choose_color(matrix, x_range, y_range))
    elif tree[0] == 'H':
        sep = int((x_range[-1]+1 - x_range[0]) * float(tree[1]) + x_range[0])
        M_recursive_fill(matrix, range(x_range[0], sep - line_width), y_range, tree[2], line_width)
        M_recursive_fill(matrix, range(sep + line_width, x_range[-1]+1), y_range, tree[3], line_width)
        fill_color(matrix, range(sep - line_width, sep + line_width), y_range, np.array([0, 0, 0]))
    elif tree[0] == 'V':
        sep = int((y_range[-1]+1 - y_range[0]) * float(tree[1]) + y_range[0])
        M_recursive_fill(matrix, x_range, range(y_range[0], sep - line_width), tree[2], line_width)
        M_recursive_fill(matrix, x_range, range(sep + line_width, y_range[-1]+1), tree[3], line_width)
        fill_color(matrix, x_range, range(sep - line_width, sep + line_width), np.array([0, 0, 0]))
                       

def choose_color(matrix, x_range, y_range):
    if not x_range or not y_range: return np.array([255, 0, 0],dtype=np.uint8)
    error, choice= np.inf, []
    seg=matrix[x_range[0]:x_range[-1]+1][y_range[0]:y_range[-1]+1]
    print(seg.shape)
    print("color, color_cost, min_error ")
    for color in colors:
        color_matrix=np.zeros(seg.shape, dtype=np.uint8)
        for i in range(len(seg)):
            for j in range(len(seg[i])):
                color_matrix[i][j]=color
        
        color_cost = cost(seg, color_matrix)
        if  color_cost < error: 
            error=color_cost
            choice=color
            
        print(color,color_cost,error)
        
    print("\nchoice",choice,'\n')
    return choice
    
# M_to_array: string(sexp) -> np.array(size_x, size_y, 3)
def M_to_array(str_sexp, matrix, size_x=640, size_y=640, line_width=5):
    tree = parse_sexp(str_sexp)    
    # print(tree)
    #matrix = np.zeros((size_x, size_y, 3), dtype=np.uint8)
    M_recursive_fill(matrix, range(0, size_x), range(0, size_y), tree[0], line_width)
    return matrix

def random_tree(k, matrix):
    
    cut_num = k
    leaf_num = k+1
    
    cuts = [('H' if random()<0.5 else 'V', randint(1,999)/1000) for _ in range(cut_num)]
    leaves = [" (L 0 0 0)"  for _ in range(leaf_num)]
    
    for c in cuts:
        ran=randint(0, len(leaves)-2)
        leaves[ran]=" (%c %.3f"%(c[0],c[1])+leaves[ran]+leaves[ran+1]+')'
        del leaves[ran+1]
    
    s = "".join(leaves)[1:]
    
    return M_to_array(s, np.array(matrix, dtype=np.uint8), 100, 100, 1)
    
#rgb2pic(random_tree(10, pic2rgb('blue.jpg')))