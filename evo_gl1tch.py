import sys
import random
import copy
import time
from PIL import Image, ImageTk
from io import BytesIO
import Tkinter as tk

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
  def get_mod_thumb(self, width):
    im = self.get_mod()
    height = int(float(im.size[1])/float(im.size[0]) * width)
    im = im.resize((width, height))
    return im
  def get_mod_thumb_tk(self, width):
    return ImageTk.PhotoImage(self.get_mod_thumb(width))

class Gui(object):
  def __init__(self, root, filename):
    self.filename = filename
    self.num_genomes = 24
    # generate initial genomes
    self.genomes = [Genome(self.filename, 0, 0, 0) for i in range(self.num_genomes)]
    # GUI
    self.root = root
    # image
    self.im_vars = [tk.IntVar() for i in range(self.num_genomes)]
    self.im_labels = []
    for i in range(4):
      for j in range(6):
        tkim = self.genomes[i*6+j].get_mod_thumb_tk(200)
        self.im_labels.append(tk.Checkbutton(self.root, 
          image=tkim, variable=self.im_vars[i*6+j], indicatoron=False, bd=10, selectcolor="green"))
        self.im_labels[i*6+j].grid(row=i, column=j)
        self.im_labels[i*6+j].image = tkim
    self.old_im_labels = [self.im_labels[i] for i in range(self.num_genomes)]
    # slider
    self.length_scale = tk.Scale(self.root, 
      from_=0, to=10, label="genome length", orient=tk.HORIZONTAL, length=200)
    self.length_scale.grid(row=4, column=0)
    self.length_scale.set(4)
    self.param_scale = tk.Scale(self.root, 
      from_=1, to=1000, label="param", orient=tk.HORIZONTAL, length=200)
    self.param_scale.grid(row=4, column=1)
    self.param_scale.set(70)
    self.mutation_scale = tk.Scale(self.root, 
      from_=0, to=100, label="mutation probability", orient=tk.HORIZONTAL, length=200)
    self.mutation_scale.grid(row=4, column=2)
    self.mutation_scale.set(15)
    # buttons
    self.reset_button = tk.Button(self.root, text="reset", command=self.reset)
    self.reset_button.grid(row=5, column=0)
    self.save_button = tk.Button(self.root, text="save", command=self.save)
    self.save_button.grid(row=5, column=1)
    self.evo_button = tk.Button(self.root, text="evolve", command=self.show_genomes)
    self.evo_button.grid(row=5, column=2)
    self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
    self.exit_button.grid(row=5, column=3)
  def save(self):
    for i in range(self.num_genomes):
      if self.im_vars[i].get():
        self.genomes[i].save("img" + str(i).zfill(3))
  def reset(self):
    self.genomes = [Genome(self.filename, 0, 0, 0) for i in range(self.num_genomes)]
    for var in self.im_vars:
      var.set(0)
    for i in range(4):
      for j in range(6):
        tkim = self.genomes[i*6+j].get_mod_thumb_tk(300)
        self.im_labels[i*6+j] = tk.Checkbutton(self.root, 
          image=tkim, variable=self.im_vars[i*6+j], indicatoron=False, bd=10, selectcolor="green")
        self.im_labels[i*6+j].grid(row=i, column=j)
        self.im_labels[i*6+j].image = tkim
        self.old_im_labels[i*6+j].destroy()
        self.old_im_labels[i*6+j] = self.im_labels[i*6+j]
  def evolve(self):
    good_genomes = [self.genomes[i] for i in range(self.num_genomes) if self.im_vars[i].get()]
    if len(good_genomes) == 0:
      for i in range(self.num_genomes):
        self.genomes[i] = Genome(self.filename, self.length_scale.get(), self.param_scale.get(), float(self.mutation_scale.get())/100.0)
    else:
      for i in range(self.num_genomes):
        self.genomes[i] = random.choice(good_genomes).cross(random.choice(good_genomes))
        self.genomes[i].mutate()
  def show_genomes(self):
    for genome in self.genomes:
      genome.update(self.param_scale.get(), float(self.mutation_scale.get())/100.0)
    if len(self.genomes[0].genome) != self.length_scale.get():
      for genome in self.genomes:
        genome.resize(self.length_scale.get())
    self.evolve()
    for var in self.im_vars:
      var.set(0)
    for i in range(4):
      for j in range(6):
        tkim = self.genomes[i*6+j].get_mod_thumb_tk(200)
        self.im_labels[i*6+j] = tk.Checkbutton(self.root, 
          image=tkim, variable=self.im_vars[i*6+j], indicatoron=False, bd=10, selectcolor="green")
        self.im_labels[i*6+j].grid(row=i, column=j)
        self.im_labels[i*6+j].image = tkim
        self.old_im_labels[i*6+j].destroy()
        self.old_im_labels[i*6+j] = self.im_labels[i*6+j]

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "USAGE: " + sys.argv[0] + " image"
    sys.exit()
  root = tk.Tk()
  gui = Gui(root, sys.argv[1])
  root.mainloop()
  root.destroy()
