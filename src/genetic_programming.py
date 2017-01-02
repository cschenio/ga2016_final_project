'''
Created on 2009-10-30
@author: Administrator
'''
from random import random, randint, choice
from copy import deepcopy
from PIL import Image, ImageDraw
from operator import itemgetter, attrgetter
import sys
import cost_function as cf

class cut:
  def __init__(self, name, childcount):
    self.name = name
    self.childcount = 2

  def evaluate(self):
    return self.value

  def display(self, indent=0):
    print (self.value)

class node:
  def __init__(self, type, children, funwrap, var="", const=None):
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
    self.matrix = None


  def getfitness(self, image):
    x, y, _  = image.shape
    self.matrix = cf.to_array(self.display(), x, y, 1)
    self.fitness = cf.cost(self.matrix, image)

  def refreshdepth(self):
    self.lisporder = ""
    self.cut = 0
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
    self.lisporder = ""
    self.lisporder += "("
    if self.type == "function":
      self.lisporder += (self.funwrap.name + " " + str(self.portion) + " ")
    elif self.type == "variable":
      self.lisporder += self.variable
    if self.children:
      for c in self.children:
        self.lisporder += c.display(indent + 1)
    self.lisporder += ")"
    return self.lisporder
  
  def getcut(self, indent=0):
    if self.type == "function":
      self.cut += 1
    if self.children:
      for c in self.children:
        self.cut += c.getcut(indent + 1)
    return self.cut

class enviroment:
  def __init__(self, funwraplist, variablelist, target_image,\
               minimaxtype="min", population=None, size=10, maxdepth=50, maxcut = 6,\
               maxgen=100, crossrate=0.9, mutationrate=0.1, newbirthrate=0.6):
    self.funwraplist = funwraplist
    self.variablelist = variablelist
    self.maxcut = maxcut
    self.cut = 0
    self.target_image = target_image
    self.minimaxtype = minimaxtype
    self.maxdepth = maxdepth
    self.population = population or self._makepopulation(size)
    self.size = size
    self.maxgen = maxgen
    self.crossrate = crossrate
    self.mutationrate = mutationrate
    self.newbirthrate = newbirthrate
    self.nextgeneration = []
    
    self.nfe = 0
    self.besttree = self.population[0]
    for i in range(0, self.size):
      self.population[i].depth=self.population[i].refreshdepth()
      self.population[i].display()
    for i in range(0, self.size):
      self.population[i].getfitness(self.target_image)
      self.nfe += 1
      if self.minimaxtype == "min":
        if self.population[i].fitness < self.besttree.fitness:
          self.besttree = self.population[i]
      elif self.minimaxtype == "max":
        if self.population[i].fitness > self.besttree.fitness:
          self.besttree = self.population[i]    

  def _makepopulation(self, popsize):
    temp = []
    for i in range(0,popsize):
      while True:
        Tree = self._maketree(0)
        if Tree.getcut() <= self.maxcut:
          temp.append(Tree)
          break
    return temp
  def _maketree(self, startdepth, threshold=0.8):
    #if startdepth < 2:
      #nodepattern = 0
    if startdepth == self.maxdepth:
      nodepattern = 1#variable or constant
    else:
      nodepattern = random()
    if nodepattern <= threshold:
      childlist = []
      selectedfun = randint(0, len(self.funwraplist) - 1)
      for i in range(0, self.funwraplist[selectedfun].childcount):
        child = self._maketree(startdepth + 1, threshold)
        childlist.append(child)
      return node("function", childlist, self.funwraplist[selectedfun])
    else:
      selectedvariable = randint(0, len(self.variablelist) - 1)
      return node("variable", None, None, \
            self.variablelist[selectedvariable], None)

  def mutate(self, tree, probchange=0.3, startdepth=0):
    if random() < probchange:
      result = self._maketree(0)
      return result
    elif tree.type == "function":
      result = deepcopy(tree)
      selectedchild = randint(0, len(tree.children) - 1)
      result.children[selectedchild] = self.mutate(tree.children[selectedchild], probchange, startdepth + 1)
      return result
    else:
      return tree


  def crossover(self, tree1, tree2, probnext=0.8, top=1):
    if random() > probnext or tree1.type == "variable" or tree2.type == "variable":
      return deepcopy(tree2), deepcopy(tree1)
    else :
      result1 = deepcopy(tree1)
      result2 = deepcopy(tree2)
      selectedchild = randint(0, len(tree1.children) - 1)
      result1.children[selectedchild], result2.children[selectedchild] = self.crossover(tree1.children[selectedchild],tree2.children[selectedchild])
      return result1, result2

  def getsubtree(self, tree, probnext = 0.8):
    if random() > probnext or tree.type == "variable":
      return tree
    else :
      return self.getsubtree(choice(tree.children))

  def envolve(self, maxgen=100, crossrate=0.9, mutationrate=0.1):
    f = open("record.txt",'w')
    for i in range(0, maxgen):
      print ("generation no.", i)
      self.listpopulation()
      #for j in range(0, self.size):
        #print (self.population[j].lisporder)
      self.nextgeneration = []
      for j in range(0, self.size):
        self.nextgeneration.append(self.population[j])
      for j in range(0, self.size):
        self.nextgeneration[j].refreshdepth()
      for j in range(0, self.size):
        if random() < crossrate:
          while True:
            parent1 = self.population[int(random() * (self.size))]
            parent2 = self.population[int(random() * (self.size))]
            while parent1 == parent2:
              parent2 = self.population[int(random() * (self.size))]
            child1, child2 = self.crossover(parent1, parent2)
            child1.refreshdepth()
            child2.refreshdepth()
            #if child.getcut() <= self.maxcut:
            self.nextgeneration.append(child1)
            self.nextgeneration.append(child2)
            break
        else:
          while True:
            parent3 = self.population[int(random() * (self.size))]
            child = self.mutate(parent3)
            child.refreshdepth()
            #if child.getcut() <= self.maxcut:
            self.nextgeneration.append(child)
            break
      #refresh depth    
      for k in range(0, len(self.nextgeneration)):
        self.nextgeneration[k].depth=self.nextgeneration[k].refreshdepth()
      #get lisporder for all trees
      for i in range(0, len(self.nextgeneration)):
        self.nextgeneration[i].lisporder = ""
        self.nextgeneration[i].display()
      #refresh all tree's fitness
      for k in range(self.size, len(self.nextgeneration)):
        #if k % 100 == 0:
        #  print (k)
        self.nextgeneration[k].getfitness(self.target_image)
        self.nfe += 1
        if self.minimaxtype == "min":
          if self.nextgeneration[k].fitness < self.besttree.fitness:
            self.besttree = self.nextgeneration[k]
        elif self.minimaxtype == "max":
          if self.nextgeneration[k].fitness > self.besttree.fitness:
            self.besttree = self.nextgeneration[k]
      print ("best tree's fitness..",self.besttree.fitness)
      #f.write("best tree's fitness.."+ str(self.besttree.fitness))
      #selection
      self.population = []
      self.nextgeneration.sort(key=attrgetter('fitness'))
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
      #print (self.besttree.lisporder)
      #f.write(self.besttree.lisporder)
      if self.besttree.fitness == 0:
        break;
    return self.besttree.lisporder, self.besttree.fitness
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
  
  def get_nfe(self):
    return self.nfe
