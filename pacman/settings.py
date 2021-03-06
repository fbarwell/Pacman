from pygame.locals import *


FRAME_RATE = 60 # frames per second

PACMAN_STARTING_SPEED = 50 # pixels per second
GHOST_STARTING_SPEED = 46.875

GAME_RESOLUTION = Rect(0, 0, 32 * 8, 35 * 8)
CROP_RESOLUTION = Rect(0, 0, 28 * 8, 35 * 8)
DISPLAY_FLAGS = HWSURFACE | DOUBLEBUF | RESIZABLE

DISPLAY_RESOLUTION = Rect(0, 0, CROP_RESOLUTION.width * 3, CROP_RESOLUTION.height * 3)
