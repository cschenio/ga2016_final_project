from random import random, randint
from pic import rgb2pic, pic2rgb
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color
import numpy as np
import pyparsing as pp

colors=np.array([[255, 0, 0], [0, 255, 255], [0, 0, 255], [255, 255, 255]])
#colors=[LabColor(lab_l=0.0000 lab_a=0.0000 lab_b=0.0000),LabColor(lab_l:100.0000 lab_a:-0.0005 lab_b:-0.0086),LabColor(lab_l:53.2390 lab_a:80.0905 lab_b:67.2014),LabColor(lab_l:97.1388 lab_a:-21.5578 lab_b:94.4773),LabColor(lab_l:32.2994 lab_a:79.1914 lab_b:-107.8655)]
# M_cost: np.array(size_x, size_y, 3) , np.array(size_x, size_y, 3) -> float

def M_cost(array_a, array_b):
    a = array_a.reshape(-1, 3)
    b = array_b.reshape(-1, 3)
    sum = 0
    for i in range(len(a)):
        color_a = convert_color(sRGBColor(a[i][0], a[i][1], a[i][2], True), LabColor)
        color_b = convert_color(sRGBColor(b[i][0], b[i][1], b[i][2], True), LabColor)
        sum += delta_e_cie2000(color_a, color_b)
    return sum

def M_parse_sexp(str_sexp):
    w = pp.Word(pp.alphanums + '.')
    lp = pp.Suppress("(")
    rp = pp.Suppress(")")
    sexp = pp.Forward()
    sexp_list = pp.Forward()
    sexp_list = pp.Group(lp + pp.ZeroOrMore(sexp) + rp)
    sexp << (w | sexp_list)
    return sexp.parseString(str_sexp)

def M_fill_color(matrix, x_range, y_range, color):
    for i in x_range:
        for j in y_range:
            matrix[i][j] = color


def M_recursive_fill(matrix, x_range, y_range, tree, line_width):
    if tree[0] == 'L':
        M_fill_color(matrix, x_range, y_range, choose_color(matrix, x_range, y_range))
    elif tree[0] == 'H':
        sep = int((x_range[-1]+1 - x_range[0]) * float(tree[1]) + x_range[0])
        M_recursive_fill(matrix, range(x_range[0], sep - line_width), y_range, tree[2], line_width)
        M_recursive_fill(matrix, range(sep + line_width, x_range[-1]+1), y_range, tree[3], line_width)
        M_fill_color(matrix, range(sep - line_width, sep + line_width), y_range, np.array([0, 0, 0]))
    elif tree[0] == 'V':
        sep = int((y_range[-1]+1 - y_range[0]) * float(tree[1]) + y_range[0])
        M_recursive_fill(matrix, x_range, range(y_range[0], sep - line_width), tree[2], line_width)
        M_recursive_fill(matrix, x_range, range(sep + line_width, y_range[-1]+1), tree[3], line_width)
        M_fill_color(matrix, x_range, range(sep - line_width, sep + line_width), np.array([0, 0, 0]))
                       

def choose_color(matrix, x_range, y_range):

    error, choice= np.inf, []
    seg=matrix[x_range[0]:x_range[-1]+1][y_range[0]:y_range[-1]+1]
    print(seg.shape)
    for color in colors:
        #color_matrix=np.array([color for _ in range((x_range[-1]+1)*(y_range[-1]+1))])
        #color_matrix=color_matrix.reshape(x_range[-1]+1, y_range[-1]+1, 3)
        color_matrix=np.zeros(seg.shape, dtype=np.uint8)
        for i in range(len(seg)):
            for j in range(len(seg[i])):
                color_matrix[i][j]=color
                
        if M_cost(seg, color_matrix) < error: 
            error=M_cost(seg, color_matrix)
            choice=color
            
        print(color,error)
        
    print(choice)
    return choice
    
# M_to_array: string(sexp) -> np.array(size_x, size_y, 3)
def M_to_array(str_sexp, size_x=640, size_y=640, line_width=5):
    tree = M_parse_sexp(str_sexp)    
    # print(tree)
    matrix = np.zeros((size_x, size_y, 3), dtype=np.uint8)
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
    
    return M_to_array(s, 100, 100, 1)
    
#rgb2pic(random_tree(5, pic2rgb('20160319100104840.jpg')))