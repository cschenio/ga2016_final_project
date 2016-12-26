from colormath.color_objects import sRGBColor, LabColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color
import numpy as np
import pyparsing as pp


# cost: np.array(size_x, size_y, 3) , np.array(size_x, size_y, 3) -> float
def cost(array_a, array_b):
    a = array_a.reshape(-1)
    b = array_b.reshape(-1)
    sum = 0
    for i in range(len(a)):
        sum += delta_e_cie2000(a[i], b[i])
    return sum

def parse_sexp(str_sexp):
    w = pp.Word(pp.alphanums + '.' + '-')
    lp = pp.Suppress("(")
    rp = pp.Suppress(")")
    sexp = pp.Forward()
    sexp_list = pp.Forward()
    sexp_list = pp.Group(lp + pp.ZeroOrMore(sexp) + rp)
    sexp << (w | sexp_list)
    return sexp.parseString(str_sexp)

def fill_color(matrix, x_range, y_range, color):
    for i in x_range:
        for j in y_range:
            matrix[i][j] = color


def recursive_fill(matrix, x_range, y_range, tree, line_width):
    if tree[0] == 'L':
        fill_color(matrix, 
                   x_range, 
                   y_range, 
                   LabColor(tree[1], tree[2], tree[3]))
    elif tree[0] == 'H':
        try:
            sep = int((x_range[-1]+1 - x_range[0]) * float(tree[1]) + x_range[0])
            recursive_fill(matrix, range(x_range[0], sep - line_width), y_range, tree[2], line_width)
            recursive_fill(matrix, range(sep + line_width, x_range[-1]+1), y_range, tree[3], line_width)
            fill_color(matrix, range(sep - line_width, sep + line_width), y_range, LabColor(0, 0, 0))
        except IndexError:
            print("Resolution not enough, cut cannot be seen.")        
    elif tree[0] == 'V':
        try:
            sep = int((y_range[-1]+1 - y_range[0]) * float(tree[1]) + y_range[0])
            recursive_fill(matrix, x_range, range(y_range[0], sep - line_width), tree[2], line_width)
            recursive_fill(matrix, x_range, range(sep + line_width, y_range[-1]+1), tree[3], line_width)
            fill_color(matrix, x_range, range(sep - line_width, sep + line_width),  LabColor(0, 0, 0))
        except IndexError:
            print("Resolution not enough, cut cannot be seen.")
# to_array: string(sexp) -> np.array(size_x, size_y, 3)
def to_array(str_sexp, size_x=640, size_y=640, line_width=5):
    tree = parse_sexp(str_sexp)    
    matrix = np.zeros((size_x, size_y), dtype=LabColor)
    recursive_fill(matrix, range(0, size_x), range(0, size_y), tree[0], line_width)
    return matrix


# random testing
    
# a = np.array([[[255, 255, 255], [255, 255, 255]],
#               [[255, 255, 255], [255, 255, 255]]])
# b = np.array([[[1, 2, 3], [3, 4, 5]],
#               [[5, 6, 7], [7, 8, 9]]])

# print(cost(a, b))


# s = "(V 0.5 (H 0.5 (L 255 0 0) (L 0 0 255)) (L 255 255 255))"
# x = to_array(s, 10, 10, 1)
# print(x)

# random testing end

# print(convert_color(sRGBColor(0, 0, 0, True), LabColor))
# print(convert_color(sRGBColor(255, 255, 255, True), LabColor))
# print(convert_color(sRGBColor(255, 0, 0, True), LabColor))
# print(convert_color(sRGBColor(255, 255, 0, True), LabColor))
# print(convert_color(sRGBColor(0, 0, 255, True), LabColor))

