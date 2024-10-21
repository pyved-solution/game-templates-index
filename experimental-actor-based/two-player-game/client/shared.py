import pyved as pyv
import pygame


SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480

BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# netw
# socket
HOST = '127.0.0.1'
PORT = 60111

# - tests avec websocket
# HOST = 'localhost'
# PORT = 2567

# - state:default
bricks = None
left_paddle = right_paddle = None

# - state:menu
local_player = None  # later on, at execution time, this becomes either 'left' or 'right'
connecting_msg = None
connection_required = False
signal_sent = False
button_a, button_b = None, None
