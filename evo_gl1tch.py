import sys
import random
from PIL import Image, ImageTk
from io import BytesIO
import Tkinter as tk

class Action(object):
  def __init__(self, size):
    self.size = size
  def mod(self, image):
    return image
  def mutate(self):
    pass

class ActionDoNothing(Action):
  def __init__(self, size):
    Action.__init__(self, size)
  def mod(self, image):
    return image
  def mutate(self):
    pass

class ActionDelete(Action):
  def __init__(self, size):
    Action.__init__(self, size)
    self.begin = random.randint(0, size-1)
    self.end = random.randint(self.begin, size-1)
  def mod(self, image):
    newimage = list(image)
    del newimage[self.begin:self.end]
    return newimage
  def mutate(self):
    self.begin = random.randint(0, size-1)
    self.end = random.randint(self.begin, size-1)

class ActionAdd(Action):
  def __init__(self, size):
    Action.__init__(self, size)
    self.begin = random.randint(0, size-1)
    self.chunk = [chr(random.randint(0, 255)) for i in range(random.randint(1, 10000))]
  def mod(self, image):
    return image[:self.begin] + self.chunk + image[self.begin:]
  def mutate(self):
    self.begin = random.randint(0, size-1)
    self.chunk = [chr(random.randint(0, 255)) for i in range(random.randint(1, 10000))]

class ActionMove(Action):
  def __init__(self, size):
    Action.__init__(self, size)
    self.begin = random.randint(0, size-1)
    self.end = random.randint(self.begin, size-1)
    self.insert = random.randint(0, size-(self.end-self.begin)-1)
  def mod(self, image):
    newimage = list(image)
    del newimage[self.begin:self.end]
    return newimage[:self.insert] + image[self.begin:self.end] + newimage[self.insert:]
  def mutate(self):
    self.begin = random.randint(0, size-1)
    self.end = random.randint(self.begin, size-1)
    self.insert = random.randint(0, size-(self.end-self.begin)-1)

class Genome(object):
  def __init__(self, filename, length):
    self.im_data = list(open(filename, "rb").read())
    size = len(self.im_data)
    self.genome = [random.choice([ActionDoNothing(size), ActionDelete(size), ActionAdd(size), ActionMove(size)]) for i in range(length)]
    while not self.test():
      self.genome = [random.choice([ActionDoNothing(size), ActionDelete(size), ActionAdd(size), ActionMove(size)]) for i in range(length)]
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
  def test(self):
    im = list(self.im_data)
    for action in self.genome:
      im = action.mod(im)
    try:
      Image.open(BytesIO("".join(im))).load()
    except:
      return False
    return True

class Gui(object):
  def __init__(self, root, filename):
    self.filename = filename
    self.num_genomes = 9
    # generate initial genomes
    self.genomes = [Genome(self.filename, 0) for i in range(self.num_genomes)]
    # GUI
    self.root = root
    # image
    self.im_vars = [tk.IntVar() for i in range(self.num_genomes)]
    self.im_labels = [tk.Checkbutton(self.root, text="genome "+str(i), variable=self.im_vars[i], indicatoron=False) for i in range(self.num_genomes)]
    for i in range(3):
      for j in range(3):
        self.im_labels[i*3+j].grid(row=i, column=j)
    self.old_im_labels = [self.im_labels[i] for i in range(self.num_genomes)]
    # buttons
    self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
    self.exit_button.grid(row=3, column=2)
    self.gen_button = tk.Button(self.root, text="gen", command=self.show_genomes)
    self.gen_button.grid(row=3, column=1)
    # slider
    self.length_scale = tk.Scale(self.root, from_=0, to=10, label="genome length", orient=tk.HORIZONTAL, length=200)
    self.length_scale.grid(row=3, column=0)
  def evolve(self):
    for i in range(self.num_genomes):
      self.genomes[i] = Genome(self.filename, self.length_scale.get())
  def show_genomes(self):
    self.evolve()
    for i in range(3):
      for j in range(3):
        tkim = self.genomes[i*3+j].get_mod_thumb_tk(300)
        self.im_labels[i*3+j] = tk.Checkbutton(self.root, image=tkim, variable=self.im_vars[i*3+j], indicatoron=False, bd=10, selectcolor="green") 
        self.im_labels[i*3+j].grid(row=i, column=j)
        self.im_labels[i*3+j].image = tkim
        self.old_im_labels[i*3+j].destroy()
        self.old_im_labels[i*3+j] = self.im_labels[i*3+j]

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "USAGE: " + sys.argv[0] + " image"
    sys.exit()
  root = tk.Tk()
  gui = Gui(root, sys.argv[1])
  root.mainloop()
  root.destroy()
