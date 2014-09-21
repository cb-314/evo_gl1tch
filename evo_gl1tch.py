import sys
from PIL import Image
from io import BytesIO

class Action(object):
  def __init__(self):
    pass
  def mod(self, image):
    print "basemod"
    return image
  def mutate(self):
    pass

class ActionDoNothing(Action):
  def __init__(self):
    Action.__init__(self)
  def mod(self, image):
    return image
  def mutate(self):
    pass

class Genome(object):
  def __init__(self, filename, length):
    self.im_data = list(open(filename, "rb").read())
    self.genome = [ActionDoNothing() for i in range(length)]
  def show_orig(self):
    Image.open(BytesIO("".join(self.im_data))).show()

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "USAGE: " + sys.argv[0] + " image"
    sys.exit()
  gen = Genome(sys.argv[1], 5)
  gen.show_orig()
