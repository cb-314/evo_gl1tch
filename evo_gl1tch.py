import sys
import random
from PIL import Image, ImageTk
from io import BytesIO
import Tkinter

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
    # main frame
    self.main_frame = Tkinter.Frame(root)
    self.main_frame.pack()
    self.im_label = Tkinter.Label(self.main_frame)
    self.im_label.pack(side=Tkinter.TOP)
    self.old_im_label = self.im_label
    # buttons
    self.button_frame = Tkinter.Frame(self.main_frame)
    self.button_frame.pack(side=Tkinter.BOTTOM)
    self.exit_button = Tkinter.Button(self.button_frame, text="Exit", command=self.main_frame.quit)
    self.exit_button.pack(side=Tkinter.RIGHT)
    self.gen_button = Tkinter.Button(self.button_frame, text="gen", command=self.gen)
    self.gen_button.pack(side=Tkinter.RIGHT)
    self.length_scale = Tkinter.Scale(self.button_frame, from_=0, to=10, label="number of actions", orient=Tkinter.HORIZONTAL, length=200)
    self.length_scale.pack(side=Tkinter.LEFT)
  def gen(self):
    g = Genome(self.filename, self.length_scale.get())
    tkim = g.get_mod()
    self.im_label = Tkinter.Label(self.main_frame, image=tkim)
    self.im_label.image = tkim
    self.im_label.pack(side=Tkinter.TOP)
    self.old_im_label.destroy()
    self.old_im_label = self.im_label

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "USAGE: " + sys.argv[0] + " image"
    sys.exit()
  root = Tkinter.Tk()
  gui = Gui(root, sys.argv[1])
  root.mainloop()
  root.destroy()
