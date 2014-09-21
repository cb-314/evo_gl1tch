import sys
import random
from PIL import Image
from io import BytesIO

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

class Genome(object):
  def __init__(self, filename, length):
    self.im_data = list(open(filename, "rb").read())
    self.genome = [ActionDoNothing(len(self.im_data)) for i in range(length)]
  def show_orig(self):
    Image.open(BytesIO("".join(self.im_data))).show()

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "USAGE: " + sys.argv[0] + " image"
    sys.exit()
  gen = Genome(sys.argv[1], 5)
