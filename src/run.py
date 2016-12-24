import cost_function as cf
import pic
import genetic_programming as gp
from random import random, randint, choice
import MonteCarlo as mc

horizontal = gp.cut('H',2)
vertical = gp.cut('V',2)

def examplefun(x, y):
    return x+2*y

def constructcheckdata(count=10):
  checkdata = []
  for i in range(0, count):
    dic = {}
    x = randint(0, 10)
    y = randint(0, 10)
    dic['x'] = x
    dic['y'] = y
    dic['result'] = examplefun(x, y)
    checkdata.append(dic)
  return checkdata


checkdata = constructcheckdata(count = 10)

x = 50
y = 50

# gp
target_image = pic.pic2rgb("../data/img03.jpg", x, y)
env = gp.enviroment([horizontal, vertical], ["L 0 0 255", "L 255 0 0", "L 255 255 0", "L 255 255 255"],
                   [-3, -2, -1, 1, 2, 3], checkdata, target_image, size = 50, maxcut = 5, maxdepth = 20)
s = env.envolve(maxgen = 10)
rgbmatrix = cf.to_array(s, x, y, 1)
pic.rgb2pic(rgbmatrix, "../data/output03_gp.jpg")

# monte carlo
min_cost = -1
answer = None
for i in range(10):
    candidate = mc.random_tree(5, pic.pic2rgb('../data/img03.jpg'), x, y, 1))
    candidate_cost = cf.cost(candidate, target_image)
    if min_cost == -1 || candidate_cost < min_cost:
        answer = candidate
        min_cost = candidate_cost

pic.rgb2pic(answer, "../data/output03_mc.jpg")
    
