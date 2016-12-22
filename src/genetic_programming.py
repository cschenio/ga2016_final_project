'''
Created on 2009-10-30

@author: Administrator
'''
from random import random, randint, choice
from copy import deepcopy
from PIL import Image, ImageDraw
import sys

class cut:
  def __init__(self, name, childcount):
    self.name = name
    self.childcount = 2

class variable:
  def __init__(self, var, value=0):
    self.var = var
    self.value = value
    self.name = str(var)
    self.type = "variable"  

  def evaluate(self):
    return self.value

  def setvar(self, value):
    self.value = value

  def display(self, indent=0):
    print self.var

class const:
  def __init__(self, value):
    self.value = value
    self.name = str(value)
    self.type = "constant"   

  def evaluate(self):
    return self.value

  def display(self, indent=0):
    print self.value

class node:
  def __init__(self, type, children, funwrap, var=None, const=None):
    self.type = type
    self.children = children
    self.funwrap = funwrap
    self.variable = var
    self.const = const
    self.depth = self.refreshdepth()
    self.value = 0
    self.fitness = 0
    self.portion = 0
    if (type == "function"):
      self.portion = random()
      self.portion = round(self.portion, 3)
    self.lisporder = ""

  def eval(self):
    if self.type == "variable":
      return self.variable.value
    elif self.type == "constant":
      return self.const.value
    else:
      for c in self.children:
        result = [c.eval() for c in self.children]
      return self.funwrap.function(result)  

  def getfitness(self):
    self.fitness=random()

  def setvariablevalue(self, value):
    if self.type == "variable":
      if value.has_key(self.variable.var):
        self.variable.setvar(value[self.variable.var])
      else:
        print "There is no value for variable:", self.variable.var
        return
    if self.type == "constant":
      pass
    if self.children:#function node
      for child in self.children:
        child.setvariablevalue(value)            

  def refreshdepth(self):
    self.lisporder = ""
    if self.type == "constant" or self.type == "variable":
      return 0
    else:
      depth = []
      for c in self.children:
        depth.append(c.refreshdepth())
      return max(depth) + 1

  def __cmp__(self, other):
        return cmp(self.fitness, other.fitness)  

  def display(self, indent=0):
    self.lisporder += "("
    if self.type == "function":
      self.lisporder += (self.funwrap.name + " " + str(self.portion))
    elif self.type == "variable":
      self.lisporder += self.variable.name
    if self.children:
      for c in self.children:
        self.lisporder += c.display(indent + 1)
    self.lisporder += ")"
    return self.lisporder
  ##for draw node
  def getwidth(self):
    if self.type == "variable" or self.type == "constant":
      return 1
    else:
      result = 0
      for i in range(0, len(self.children)):
        result += self.children[i].getwidth()
      return result
    

class enviroment:
  def __init__(self, funwraplist, variablelist, constantlist, checkdata, \
               minimaxtype="min", population=None, size=10, maxdepth=3, \
               maxgen=100, crossrate=0.9, mutationrate=0.1, newbirthrate=0.6):
    self.funwraplist = funwraplist
    self.variablelist = variablelist
    self.constantlist = constantlist
    self.checkdata = checkdata
    self.minimaxtype = minimaxtype
    self.maxdepth = maxdepth
    self.population = population or self._makepopulation(size)
    self.size = size
    self.maxgen = maxgen
    self.crossrate = crossrate
    self.mutationrate = mutationrate
    self.newbirthrate = newbirthrate
    self.nextgeneration = []

    self.besttree = self.population[0]
    for i in range(0, self.size):
      self.population[i].lisporder = ""
      self.population[i].display
    for i in range(0, self.size):
      self.population[i].depth=self.population[i].refreshdepth()
      self.population[i].getfitness()
      if self.minimaxtype == "min":
        if self.population[i].fitness < self.besttree.fitness:
          self.besttree = self.population[i]
      elif self.minimaxtype == "max":
        if self.population[i].fitness > self.besttree.fitness:
          self.besttree = self.population[i]    

  def _makepopulation(self, popsize):
    return [self._maketree(0) for i in range(0, popsize)]     

  def _maketree(self, startdepth):
    if startdepth == 0:
      #make a new tree
      nodepattern = 0#function
    elif startdepth == self.maxdepth:
      nodepattern = 1#variable or constant
    else:
      nodepattern = randint(0, 1)
    if nodepattern == 0:
      childlist = []
      selectedfun = randint(0, len(self.funwraplist) - 1)
      for i in range(0, self.funwraplist[selectedfun].childcount):
        child = self._maketree(startdepth + 1)
        childlist.append(child)
      return node("function", childlist, self.funwraplist[selectedfun])
    else:
      selectedvariable = randint(0, len(self.variablelist) - 1)
      return node("variable", None, None, \
             variable(self.variablelist[selectedvariable]), None)

  def mutate(self, tree, probchange=0.1, startdepth=0):
    if random() < probchange:
      return self._maketree(startdepth)
    else:
      result = deepcopy(tree)
      if result.type == "function":
        result.children = [self.mutate(c, probchange, startdepth + 1) \
                           for c in tree.children]
    return result

  def crossover(self, tree1, tree2, probswap=0.8, top=1):
    if not top:
      return deepcopy(tree2)
    else:
      result = deepcopy(tree1)
      if tree1.type == "function" and tree2.type == "function":
        result.children = [self.crossover(c, choice(tree2.children), \
                           probswap, 0) for c in tree1.children]
    return result

  def envolve(self, maxgen=100, crossrate=0.9, mutationrate=0.1):
    for i in range(0, maxgen):
      print "generation no.", i
      self.nextgeneration = []
      for j in range(0, self.size):
        self.nextgeneration.append(self.population[j])
      for j in range(0, 2*self.size):
        if random() < self.crossrate:
          parent1 = self.population[int(random() * (self.size))]
          parent2 = self.population[int(random() * (self.size))]
          child = self.crossover(parent1, parent2)
          self.nextgeneration.append(child)
        else:
          parent3 = self.population[int(random() * (self.size))]
          child = self.mutate(parent3, mutationrate)
          self.nextgeneration.append(child)
      #refresh depth    
      for k in range(0, len(self.nextgeneration)):
        self.nextgeneration[k].depth=self.nextgeneration[k].refreshdepth()
      #get lisporder for all trees
      for i in range(0, len(self.nextgeneration)):
        self.nextgeneration[i].lisporder = ""
        self.nextgeneration[i].display()
      #refresh all tree's fitness
      for k in range(0, len(self.nextgeneration)):
        self.nextgeneration[k].getfitness()
        if self.minimaxtype == "min":
          if self.nextgeneration[k].fitness < self.besttree.fitness:
            self.besttree = self.nextgeneration[k]
        elif self.minimaxtype == "max":
          if self.nextgeneration[k].fitness > self.besttree.fitness:
            self.besttree = self.nextgeneration[k]
      print "best tree's fitness..",self.besttree.fitness
      #selection
      self.population = []
      self.nextgeneration.sort()
      allfitness = 0
      randomnum = random()*(len(self.nextgeneration) - 1)
      dis = float(len(self.nextgeneration) - 1) / float(self.size)
      for i in range(0, len(self.nextgeneration)):
        allfitness += self.nextgeneration[i].fitness
      for j in range (0, self.size):
        selectedTree, t1 = self.roulettewheelsel(randomnum, allfitness)
        self.population.append(selectedTree)
        randomnum += dis
        if randomnum >= float(len(self.nextgeneration) - 1):
          randomnum -= float(len(self.nextgeneration) - 1)
      if self.besttree.fitness == 0:
        break;
    print self.besttree.lisporder
    #for tree in self.nextgeneration:
     # print tree.fitness

  def gettoptree(self, choosebest=0.9, reverse=False):
    if self.minimaxtype == "min":
      self.population.sort()
    elif self.minimaxtype == "max":
      self.population.sort(reverse=True)  

    if reverse == False:
      if random() < choosebest:
        i = randint(0, self.size * self.newbirthrate)
        return self.population[i], i
      else:
        i = randint(self.size * self.newbirthrate, self.size - 1)
        return self.population[i], i
    else:
      if random() < choosebest:
        i = self.size - randint(0, self.size * self.newbirthrate) - 1
        return self.population[i], i
      else:
        i = self.size - randint(self.size * self.newbirthrate,\
            self.size - 1)
        return self.population[i], i

  def roulettewheelsel(self, randomnum, allfitness):
    check = 0
    for i in range(0, len(self.nextgeneration)):
      check += (1.0 - self.nextgeneration[i].fitness / allfitness)
      if check >= randomnum:
        return self.nextgeneration[i], i
    

  def listpopulation(self):
    for i in range(0, self.size):
      self.population[i].display()   

#############################################################


horizontal = cut('H',2)
vertical = cut('V',2)

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

if __name__ == "__main__":
  checkdata = constructcheckdata(count = 10)
  #print checkdata
  env = enviroment([horizontal, vertical], ["L 0 0 255", "L 255 0 0", "L 255 255 0", "L 255 255 255"],
                  [-3, -2, -1, 1, 2, 3], checkdata, size = 10)
  env.envolve(maxgen = 10)