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
    return ImageTk.PhotoImage(Image.open(BytesIO("".join(self.im_data))))
  def get_mod(self):
    im = list(self.im_data)
    for action in self.genome:
      im = action.mod(im)
    return ImageTk.PhotoImage(Image.open(BytesIO("".join(im))))
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
    self.root = root
    # image
    self.im_label = tk.Label(self.root, text="foo")
    self.im_label.grid(row=0, columnspan=3)
    self.old_im_label = self.im_label
    # buttons
    self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
    self.exit_button.grid(row=1, column=2)
    self.gen_button = tk.Button(self.root, text="gen", command=self.gen)
    self.gen_button.grid(row=1, column=1)
    # slider
    self.length_scale = tk.Scale(self.root, from_=0, to=10, label="genome length", orient=tk.HORIZONTAL, length=200)
    self.length_scale.grid(row=1, column=0)
  def gen(self):
    g = Genome(self.filename, self.length_scale.get())
    tkim = g.get_mod()
    self.im_label = tk.Label(self.root, image=tkim)
    self.im_label.grid(row=0, columnspan=3)
    self.im_label.image = tkim
    self.old_im_label.destroy()
    self.old_im_label = self.im_label

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "USAGE: " + sys.argv[0] + " image"
    sys.exit()
  root = tk.Tk()
  gui = Gui(root, sys.argv[1])
  root.mainloop()
  root.destroy()
