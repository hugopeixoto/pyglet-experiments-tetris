import pyglet
import random
import copy

from pyglet.gl import *
from pyglet.window import key
from pyglet.window import mouse

random.seed()
 
def chunks (array, n):
  for i in range(0, len(array), n):
    yield(array[i:i+n])

# VARIABLES
window = pyglet.window.Window(width=640, height=480)
batch = pyglet.graphics.Batch()
clock = pyglet.resource.image('block.png')
frame = pyglet.resource.image('frame.png')
pieces = pyglet.resource.image('pieces.png')
pieces_bitmask = pieces.get_image_data().get_data('I', 4*4).replace("\x00", "1").replace("\xff", "0")
pieces_bitmask_by_piece = chunks(pieces_bitmask, 64)
piece_templates = map(lambda bitmask: list(chunks(zip(*[[int(y) for y in x] for x in chunks(bitmask, 16)]), 4)), pieces_bitmask_by_piece)

frame_grid = pyglet.image.ImageGrid(frame, 3, 3)

# SETUP GL
gl.glEnable(GL_BLEND)
gl.glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

class Block:
  texture = pyglet.resource.image('block.png')
  size = [16, 16]

  def __init__ (self, color):
    self.color = color

  def draw (self, x, y):
    gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glColor3f(self.color[0], self.color[1], self.color[2])
    Block.texture.blit(x, y, 0, self.size[0], self.size[1])

class Piece:
  templates = piece_templates

  colors = [[1.0, 0.0, 1.0], [0.4, 0.5, 1.0]]

  def __init__ (self, template):
    self.color = random.choice(self.colors)
    self.position = [0, 0]
    self.template = template
    self.rotation = 0
    self.block = Block(self.color)

  def draw (self):
    for x, y, block in self.blocks(0, 0, 0):
      block.draw((self.position[0] + x) * 16, (self.position[1] + y) * 16)

  def blocks (self, dx, dy, rotation):
    for y, row in enumerate(self.template[(self.rotation + rotation) % len(self.template)]):
      for x, state in enumerate(row):
        if state == 1:
          yield(x + dx, y + dy, self.block)

class Board:
  def __init__ (self, width, height):
    self.width = width
    self.height = height
    self.piece = None
    self.grid = self.get_empty_rows(self.height)

  def get_empty_rows (self, n):
    return [[None for x in xrange(0, self.width)] for y in xrange(0, n)]

  def draw (self, base_x, base_y):
    global frame
    # draw border

    gl.glPushMatrix()
    gl.glColor3f(1, 1, 1)
    frame.blit(base_x, base_y, 0, self.width*16, self.height*16)

    gl.glTranslatef(base_x, base_y, 0)
    # draw the board content
    for y, row in enumerate(self.grid):
      for x, cell in enumerate(row):
        if cell:
          cell.draw(x * 16, y * 16)

    if self.piece:
        self.piece.draw()

    gl.glPopMatrix()

  def place_random_piece (self):
    self.piece = Piece(random.choice(Piece.templates))
    self.piece.position = [(self.width - 4) / 2, (self.height - 4)]

  def piece_rotate (self):
    if self.piece:
      if not self.will_collide(0, 0, 1):
        self.piece.rotation = (self.piece.rotation + 1) % len(self.piece.template)

  def piece_down (self):
    if self.piece:
      if self.will_collide(0, -1, 0):
        self.flatten()
        self.place_random_piece()
      else:
        self.piece.position[1] -= 1

  def piece_left (self):
    if self.piece:
      if not self.will_collide(-1, 0, 0):
        self.piece.position[0] -= 1

  def piece_right (self):
    if self.piece:
      if not self.will_collide(1, 0, 0):
        self.piece.position[0] += 1

  def will_collide (self, dx, dy, rotation):
    for x, y, block in self.piece.blocks(dx + self.piece.position[0], dy + self.piece.position[1], rotation):
      if (self.width <= x or x < 0) or (self.height <= y or y < 0) or self.grid[y][x]:
        return True
    return False

  def flatten (self):
    # merge DAS PIECE
    for x, y, block in self.piece.blocks(0, 0, 0):
      self.grid[self.piece.position[1] + y][self.piece.position[0] + x] = block

    # check for lines
    self.grid = [row for row in self.grid if not all(row)]
    self.grid += self.get_empty_rows(self.height - len(self.grid))


board = Board(10, 20)
board.place_random_piece()

# APP RUN CODE
@window.event
def on_key_press(symbol, modifiers):
  global board
  if symbol == key.LEFT:
    board.piece_left()
  elif symbol == key.RIGHT:
    board.piece_right()
  elif symbol == key.DOWN:
    board.piece_down()
  elif symbol == key.UP:
    board.piece_rotate()
 
# Y U NO WORK, MOUSE?
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        print 'The left mouse button was pressed.'
               
@window.event
def on_draw():
    global board
    window.clear()
    board.draw(64, 64)

def update(dt):
  global board
  board.piece_down()
  pass 

pyglet.clock.schedule_interval(update, 0.3)
pyglet.app.run()
