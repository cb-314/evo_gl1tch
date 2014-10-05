import sys
import random
import copy
import time
from PIL import Image, ImageTk
from io import BytesIO
import Tkinter as tk
import numpy as np
import cv2
import multiprocessing

class Action(object):
  def __init__(self, size, param):
    self.size = size
    self.param = param
  def mod(self, image):
    return image
  def mutate(self):
    pass
  def update(self, param):
    self.param = param

class ActionDoNothing(Action):
  def __init__(self, size, param):
    Action.__init__(self, size, param)

class ActionDelete(Action):
  def __init__(self, size, param):
    Action.__init__(self, size, param)
    self.begin = random.randint(0, self.size-1)
    self.end = random.randint(self.begin, min(self.begin+self.param, self.size-1))
  def mod(self, image):
    newimage = list(image)
    del newimage[self.begin:self.end]
    return newimage
  def mutate(self):
    self.begin = random.randint(0, self.size-1)
    self.end = random.randint(self.begin, min(self.begin+self.param, self.size-1))

class ActionAdd(Action):
  def __init__(self, size, param):
    Action.__init__(self, size, param)
    self.begin = random.randint(0, self.size-1)
    self.chunk = [chr(random.randint(0, 255)) for i in range(random.randint(1, self.param))]
  def mod(self, image):
    return image[:self.begin] + self.chunk + image[self.begin:]
  def mutate(self):
    self.begin = random.randint(0, self.size-1)
    self.chunk = [chr(random.randint(0, 255)) for i in range(random.randint(1, self.param))]

class ActionMove(Action):
  def __init__(self, size, param):
    Action.__init__(self, size, param)
    self.begin = random.randint(0, self.size-1)
    self.end = random.randint(self.begin, min(self.begin+self.param, self.size-1))
    self.insert = random.randint(0, self.size-(self.end-self.begin)-1)
  def mod(self, image):
    newimage = list(image)
    del newimage[self.begin:self.end]
    return newimage[:self.insert] + image[self.begin:self.end] + newimage[self.insert:]
  def mutate(self):
    self.begin = random.randint(0, self.size-1)
    self.end = random.randint(self.begin, min(self.begin+self.param, self.size-1))
    self.insert = random.randint(0, self.size-(self.end-self.begin)-1)

class Genome(object):
  def __init__(self, filename, length, param, mutation_prob):
    self.im_data = list(open(filename, "rb").read())
    self.size = len(self.im_data)
    self.param = param
    self.mutation_prob = mutation_prob
    self.genome = [random.choice(
      [ActionDoNothing(self.size, self.param), 
      ActionDelete(self.size, self.param), 
      ActionAdd(self.size, self.param), 
      ActionMove(self.size, self.param)]) 
    for i in range(length)]
    while not self.test():
      self.genome = [random.choice(
        [ActionDoNothing(self.size, self.param), 
        ActionDelete(self.size, self.param), 
        ActionAdd(self.size, self.param), 
        ActionMove(self.size, self.param)]) 
      for i in range(length)]
  def test(self):
    im = list(self.im_data)
    for action in self.genome:
      im = action.mod(im)
    try:
      Image.open(BytesIO("".join(im))).load()
    except:
      return False
    return True
  def save(self, prefix):
    im = self.get_mod()
    im.save(prefix + "_" + time.strftime("%Y%m%d_%H%M%S") + ".jpg")
  def update(self, param, mutation_prob):
    self.param = param
    self.mutation_prob = mutation_prob
    for action in self.genome:
      action.update(param)
    while not self.test():
      self.genome = [random.choice(
        [ActionDoNothing(self.size, self.param), 
        ActionDelete(self.size, self.param), 
        ActionAdd(self.size, self.param),
        ActionMove(self.size, self.param)]) 
      for i in range(length)]
  def resize(self, length):
    if length < len(self.genome):
      while length != len(self.genome):
        pos = random.randint(0, len(self.genome)-1)
        del self.genome[pos]
    elif length > len(self.genome):
      splice = random.randint(0, len(self.genome))
      self.genome.insert(splice, random.choice(
        [ActionDoNothing(self.size, self.param), 
        ActionDelete(self.size, self.param), 
        ActionAdd(self.size, self.param), 
        ActionMove(self.size, self.param)]))
      while not self.test():
        self.genome[splice] = random.choice(
          [ActionDoNothing(self.size, self.param), 
          ActionDelete(self.size, self.param), 
          ActionAdd(self.size, self.param), 
          ActionMove(self.size, self.param)])
  def mutate(self):
    old_genome = copy.deepcopy(self.genome)
    for action in self.genome:
      if random.random() < self.mutation_prob:
        action.mutate()
    while not self.test():
      self.genome = copy.deepcopy(old_genome)
      for action in self.genome:
        if random.random() < self.mutation_prob:
          action.mutate()
  def cross(self, other):
    new_genome = copy.deepcopy(other)
    splice = random.randint(0, len(self.genome))
    for i in range(len(self.genome)):
      if i <= splice:
        new_genome.genome[i] = copy.deepcopy(self.genome[i])
      else:
        new_genome.genome[i] = copy.deepcopy(other.genome[i])
    return new_genome
  def fitness(self):
    # get the two images
    orig = self.get_orig()
    mod = self.get_mod()
    # find features in orig and match with mod
    cv_orig = np.array(orig)
    cv_mod = np.array(mod)
    orb = cv2.ORB(nfeatures=256)
    kp_orig = orb.detect(cv_orig)
    kp_mod = orb.detect(cv_mod)
    kp_orig, des_orig = orb.compute(cv_orig, kp_orig)
    kp_mod, des_mod = orb.compute(cv_mod, kp_mod)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des_orig, des_mod)
    num_matches = len(matches)
    # split and get pixel values
    orig = [np.array(o.getdata()) for o in orig.split()]
    mod = [np.array(m.getdata()) for m in mod.split()]
    # calculate some pixel-level metrics
    diff = sum([np.mean(abs(m-o)) for m, o in zip(orig, mod)])
    vari = sum([np.std(m) for m in mod])
    exposure = abs(np.mean(mod[0]*0.299 + mod[1]*0.587 + mod[2]*0.114) - 128)
    # calculate fitness uniform weights up to now
    fitness = num_matches + diff + vari - exposure
    return fitness
  def get_orig(self):
    return Image.open(BytesIO("".join(self.im_data)))
  def get_orig_tk(self):
    return ImageTk.PhotoImage(self.get_orig())
  def get_mod(self):
    im = list(self.im_data)
    for action in self.genome:
      im = action.mod(im)
    return Image.open(BytesIO("".join(im)))
  def get_mod_tk(self):
    return ImageTk.PhotoImage(self.get_mod())
  def get_mod_thumb(self, width=-1, height=-1):
    im = self.get_mod()
    if height == -1 and width != -1:
      height = int(float(im.size[1])/float(im.size[0]) * width)
    elif width == -1 and height != -1:
      width = int(float(im.size[0])/float(im.size[1]) * height)
    else:
      return im
    im = im.resize((width, height))
    return im
  def get_mod_thumb_tk(self, width=-1, height=-1):
    return ImageTk.PhotoImage(self.get_mod_thumb(width, height))

class Gui(object):
  def __init__(self, root, filename):
    self.filename = filename
    self.num_genomes = 1
    self.img_width = 640
    self.img_height = 480
    self.old_ctrl_height = None
    # generate initial genomes
    self.genomes = [Genome(self.filename, 0, 0, 0) for i in range(self.num_genomes)]
    # GUI
    self.root = root
    self.root.pack(fill=tk.BOTH, expand=1)
    self.root.bind("<Configure>", self.window_resize_callback)
    # frame to get all the controls
    self.control_frame = tk.Frame(self.root, width=self.img_width)
    # sliders
    self.population_scale = tk.Scale(self.control_frame, 
      from_=1, to=100, label="population size", orient=tk.HORIZONTAL, length=200, command=self.population_size_callback)
    self.population_scale.grid(row=1, column=0)
    self.population_scale.set(self.num_genomes)
    self.length_scale = tk.Scale(self.control_frame, 
      from_=0, to=10, label="genome length", orient=tk.HORIZONTAL, length=200)
    self.length_scale.grid(row=1, column=1)
    self.length_scale.set(4)
    self.param_scale = tk.Scale(self.control_frame, 
      from_=1, to=1000, label="param", orient=tk.HORIZONTAL, length=200)
    self.param_scale.grid(row=1, column=2)
    self.param_scale.set(70)
    self.mutation_scale = tk.Scale(self.control_frame, 
      from_=0, to=100, label="mutation probability", orient=tk.HORIZONTAL, length=200)
    self.mutation_scale.grid(row=1, column=3)
    self.mutation_scale.set(15)
    # buttons
    self.reset_button = tk.Button(self.control_frame, text="reset", command=self.reset)
    self.reset_button.grid(row=2, column=0)
    self.save_button = tk.Button(self.control_frame, text="save", command=self.save)
    self.save_button.grid(row=2, column=1)
    self.evo_button = tk.Button(self.control_frame, text="evolve", command=self.evolve)
    self.evo_button.grid(row=2, column=2)
    self.exit_button = tk.Button(self.control_frame, text="Exit", command=self.control_frame.quit)
    self.exit_button.grid(row=2, column=3)
    # setup canvas and scrollbar
    self.canvas_scrollbar = tk.Scrollbar(self.control_frame, orient=tk.HORIZONTAL)
    self.canvas = tk.Canvas(self.root, width=self.img_width, height=self.img_height, xscrollcommand=self.canvas_scrollbar.set)
    # config scrollbar
    self.canvas_scrollbar.config(command=self.canvas.xview)
    self.canvas_scrollbar.grid(row=0, columnspan=4, sticky=tk.E+tk.W)
    # add stuff to window
    self.root.add(self.canvas)
    self.root.add(self.control_frame)
    # plot images
    self.im_vars = [False for i in range(self.num_genomes)]
    self.show_phenotypes()
  def population_size_callback(self, size):
    self.num_genomes = int(size)
  def img_click_callback(self, event):
    canvas = event.widget
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    closest = canvas.find_closest(x, y)
    if closest[0] in self.im_idx.keys():
      if self.im_vars[self.im_idx[canvas.find_closest(x, y)[0]]]:
        self.im_vars[self.im_idx[canvas.find_closest(x, y)[0]]] = False
      else:
        self.im_vars[self.im_idx[canvas.find_closest(x, y)[0]]] = True
    self.show_phenotypes()
  def window_resize_callback(self, event):
    if self.old_ctrl_height == None :
      self.old_ctrl_height = self.root.winfo_height() - self.root.sash_coord(0)[1]
    self.root.sash_place(0, self.root.sash_coord(0)[0], self.root.winfo_height() - self.old_ctrl_height)
  def show_phenotypes(self):
    self.img_height = self.root.sash_coord(0)[1]
    self.canvas.config(height=self.img_height)
    self.im_refs = []
    self.im_idx = {}
    self.canvas.delete(tk.ALL)
    for i in range(self.num_genomes):
      tkim = self.genomes[i].get_mod_thumb_tk(height=self.img_height)
      self.img_width = tkim.width()
      self.canvas.config(scrollregion=(0, 0, self.num_genomes*(self.img_width+60), 0))
      self.im_refs.append(tkim)
      if self.im_vars[i]:
        self.canvas.create_rectangle(i*(self.img_width+60)+15, 0, (i+1)*(self.img_width+60)-15, self.img_height, fill="red")
      idx = self.canvas.create_image((i*(self.img_width+60)+self.img_width/2+30, self.img_height/2), image=tkim, tags="img")
      self.im_idx[idx] = i
    self.canvas.tag_bind("img", "<ButtonPress-1>", self.img_click_callback)
  def save(self):
    for i in range(self.num_genomes):
      if self.im_vars[i]:
        self.genomes[i].save("img" + str(i).zfill(3))
  def reset(self):
    self.genomes = [Genome(self.filename, 0, 0, 0) for i in range(self.num_genomes)]
    for var in self.im_vars:
      var = False
    self.show_phenotypes()
  def evolve(self):
    # first look for genome parameter changes
    for genome in self.genomes:
      genome.update(self.param_scale.get(), float(self.mutation_scale.get())/100.0)
    if len(self.genomes[0].genome) != self.length_scale.get():
      for genome in self.genomes:
        genome.resize(self.length_scale.get())
    # then find selected genomes
    good_genomes = [self.genomes[i] for i in range(self.num_genomes) if self.im_vars[i]]
    # and evolve
    if len(good_genomes) == 0:
      for i in range(self.num_genomes):
        self.genomes[i] = Genome(self.filename, self.length_scale.get(), self.param_scale.get(), float(self.mutation_scale.get())/100.0)
    else:
      for i in range(len(good_genomes)):
        self.genomes[i] = good_genomes[i]
      for i in range(len(good_genomes), self.num_genomes):
        self.genomes[i] = random.choice(good_genomes).cross(random.choice(good_genomes))
        self.genomes[i].mutate()
    # then reset the gui
    for var in self.im_vars:
      var = False
    self.show_phenotypes()
    for genome in self.genomes:
      genome.fitness()

def calc_fitness(genome):
  return genome.fitness()

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "USAGE: " + sys.argv[0] + " image"
    sys.exit()
#  root = tk.PanedWindow(orient=tk.VERTICAL)
#  gui = Gui(root, sys.argv[1])
#  root.mainloop()
#  root.destroy()
  num_genomes = 50
  num_elite = 5
  genomes = [Genome(sys.argv[1], 4, 70, 0.30) for i in range(num_genomes)]
  for i in range(50):
    print "generation", i
    pool = multiprocessing.Pool(processes=4)
    fitness = pool.map(calc_fitness, genomes)
#    fitness = [genome.fitness() for genome in genomes]
    genomes = [g[0] for g in sorted(zip(genomes, fitness), key=lambda x:x[1])]
    genomes = genomes[-num_elite:]
    print "best fitness", max(fitness)
    for j in range(num_elite):
      genomes[-(j+1)].get_mod().save("img"+str(i).zfill(3)+"_"+str(j).zfill(3)+".jpg")
    print "evolving"
    while len(genomes) < num_genomes:
      parent1 = random.choice(genomes[:num_elite])
      parent2 = random.choice(genomes[:num_elite])
      if parent1 != parent2 or num_elite == 1:
        genome = parent1.cross(parent2)
        genome.mutate()
        if genome.test():
          genomes.append(genome)
    print "finished"
