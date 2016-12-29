from skimage.color import deltaE_ciede2000, lab2rgb, rgb2lab
import numpy as np
import pyparsing as pp

WHITE = [100.0000, -0.0005, -0.0086]
RED = [53.2390, 80.0905, 67.2014]
YELLOW = [97.1388, -21.5578, 94.4773]
BLUE = [32.2994, 79.1914, -107.8655]
TARGET_IMAGE = None

def set_target_image(t):
    global TARGET_IMAGE
    TARGET_IMAGE = t

# cost: np.array(size_x, size_y, 3) , np.array(size_x, size_y, 3) -> float
def cost(array_a, array_b):
    a = array_a.reshape(-1)
    b = array_b.reshape(-1)
    sum = 0
    
    sum += deltaE_ciede2000(a, b)
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

def check_color(x_range, y_range, color_list):
    min_error = -1
    min_error_color = None
    for c in color_list:
        sum = 0.0
        for i in x_range:
            for j in y_range:
                dist = deltaE_ciede2000(TARGET_IMAGE[i][j], c)
                sum += dist
        if min_error == -1 or sum < min_error:
            min_error = sum
            min_error_color = c
    print(x_range, y_range, min_error_color)
    return min_error_color

def recursive_fill(matrix, x_range, y_range, tree, line_width):
    if tree[0] == 'L':
        best_color = check_color(
            x_range, 
            y_range, 
            [WHITE, RED, YELLOW, BLUE])
        print("best_color = ", best_color) 
        fill_color(matrix, x_range, y_range, best_color)
    
    elif tree[0] == 'H':
        try:
            sep = int((x_range[-1]+1 - x_range[0]) * float(tree[1]) + x_range[0])
            recursive_fill(matrix, range(x_range[0], sep - line_width), y_range, tree[2], line_width)
            recursive_fill(matrix, range(sep + line_width, x_range[-1]+1), y_range, tree[3], line_width)
            fill_color(matrix, range(sep - line_width, sep + line_width), y_range, [0, 0, 0])
        except IndexError:
            print("Resolution not enough, cut cannot be seen.")        
    
    elif tree[0] == 'V':
        try:
            sep = int((y_range[-1]+1 - y_range[0]) * float(tree[1]) + y_range[0])
            recursive_fill(matrix, x_range, range(y_range[0], sep - line_width), tree[2], line_width)
            recursive_fill(matrix, x_range, range(sep + line_width, y_range[-1]+1), tree[3], line_width)
            fill_color(matrix, x_range, range(sep - line_width, sep + line_width),  [0, 0, 0])
        except IndexError:
            print("Resolution not enough, cut cannot be seen.")

# to_array: string(sexp) -> np.array(size_x, size_y, 3)
def to_array(str_sexp, size_x=640, size_y=640, line_width=5):
    tree = parse_sexp(str_sexp)    
    matrix = np.zeros((size_x, size_y), dtype=np.uint8)
    recursive_fill(matrix, range(0, size_x), range(0, size_y), tree[0], line_width)
    return matrix
