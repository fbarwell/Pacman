import pygame
import os
import math
from random import *
from pacman.spritesheet import Spritesheet
from pygame.locals import *
from pacman.actors import Actor
from pacman.actors import ActorAnimation
from pacman.settings import *






class MazeTile(pygame.sprite.Sprite):
    def __init__(self, maze, spritesheet, tile_type_number, r=0, c=0, draw_style="normal"):
        pygame.sprite.Sprite.__init__(self)

        self.__maze = maze
        self.__draw_style = ""
        self.__tile_type_number = -1

        self.tile_type = "" # set next
        self.set_tile_type_number(spritesheet, tile_type_number)
        self.draw_style = draw_style

        self.r = r
        self.c = c
        self.x = c * 8
        self.y = r * 8

        self.rect = Rect(self.x, self.y, 8, 8)

        self.address = str(r) + "," + str(c)

    def center_offset(self, heading, tile_count):
        d = tile_count * 8
        if heading == "up":
            return self.rect.centerx, self.rect.centery - d
        elif heading == "down":
            return self.rect.centerx, self.rect.centery + d
        if heading == "left":
            return self.rect.centerx - d, self.rect.centery
        elif heading == "right":
            return self.rect.centerx + d, self.rect.centery


    @property
    def tile_type_number(self):
        return self.__tile_type_number

    def set_tile_type_number(self, spritesheet, tile_type_number):
        self.__tile_type_number = tile_type_number

        if tile_type_number == 45:
            self.tile_type = "pellet"
        elif tile_type_number == 47:
            self.tile_type = "powerpellet"
        elif tile_type_number == 44:
            self.tile_type = "none"
        else:
            self.tile_type = "wall"



        # --------------------------------------------------------------------
        # spritesheet lays out tiles in a grid with 3 rows, and 16 columns
        #
        # The tile_type_number parameter is an integer from 0..47
        # we'll convert it, and load in the correct tile from the spritesheet
        #
        #                    Sheet Tile (Row,Col)   spritesheet coord
        #                    Row=ttn // 16          x = Col * 9
        # tile_type_number   Col=ttn % 16           y = Row * 9
        # ----------------   --------------------   ------------------
        # 0                  0, 0                   0, 0
        # 1                  0, 1                   0, 9
        # 2                  0, 2                   0, 18
        # 15                 0, 15                  0, 135
        # 16                 1, 0                   9, 0
        # 17                 1, 1                   9, 9
        # 18                 1, 2                   9, 18
        # ...
        #
        # The spritesheet also repeats the 16x3 grid, 3 times.
        # The same tiles repeat with different color sets.
        # We'll load each tile 3x and refer to the 'style'
        # as "Normal", "Vivid", "Black and White"
        # --------------------------------------------------------------------
        self.__images = dict()
        self.__images["vivid"]  = spritesheet.image_at((tile_type_number % 16 * 9, 200 + tile_type_number // 16 * 9     , 8, 8))
        self.__images["normal"] = spritesheet.image_at((tile_type_number % 16 * 9, 200 + tile_type_number // 16 * 9 + 27, 8, 8))
        self.__images["bw"]     = spritesheet.image_at((tile_type_number % 16 * 9, 200 + tile_type_number // 16 * 9 + 54, 8, 8))
        self.__images["none"]   = spritesheet.image_at((44               % 16 * 9, 200 + 44               // 16 * 9 + 54, 8, 8))
        if self.__draw_style != "":
            self.image = self.__images[self.__draw_style]

    @property
    def draw_style(self):
        return self.__draw_style


    @draw_style.setter
    def draw_style(self, draw_style):
        self.__draw_style = draw_style
        if self.__images:
            self.image = self.__images[draw_style]


    def get_neighbour_tile(self, direction, distance=1):
        new_r = 0
        new_c = 0
        if direction == "left":
            new_r = self.r
            new_c = self.c - distance
        elif direction == "right":
            new_r = self.r
            new_c = self.c + distance
        elif direction == "up":
            new_r = self.r - distance
            new_c = self.c
        elif direction == "down":
            new_r = self.r + distance
            new_c = self.c

        return self.__maze.get_tile(new_r, new_c)


    def distance_to_tile(self, other_tile):
        dx = other_tile.rect.x - self.rect.x
        dy = other_tile.rect.y - self.rect.y
        h = math.sqrt(dx **  2 + dy ** 2)
        return h

    def distance_to_coordinate(self, xy):
        dx = xy[0] - self.rect.centerx
        dy = xy[1] - self.rect.centery
        h = math.sqrt(dx ** 2 + dy ** 2)
        return h




class Maze(pygame.sprite.Group):
    def __init__(self):
        pygame.sprite.Group.__init__(self)
        self.pellets = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.powerpellets = pygame.sprite.Group()

        self.num_rows = 0
        self.num_columns = 0

        map = [ [  3,  3,  1, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 43,   42, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,  0,  3,  3],
                [  3,  3,  3, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 25,   24, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45,  2,  3,  3],
                [  3,  3,  3, 45, 23, 14, 14, 22, 45, 23, 14, 14, 14, 22, 45, 25,   24, 45, 23, 14, 14, 14, 22, 45, 23, 14, 14, 22, 45,  2,  3,  3],
                [  3,  3,  3, 47, 25, 44, 44, 24, 45, 25, 44, 44, 44, 24, 45, 25,   24, 45, 25, 44, 44, 44, 24, 45, 25, 44, 44, 24, 47,  2,  3,  3],
                [  3,  3,  3, 45, 27, 20, 20, 26, 45, 27, 20, 20, 20, 26, 45, 27,   26, 45, 27, 20, 20, 20, 26, 45, 27, 20, 20, 26, 45,  2,  3,  3],
                [  3,  3,  3, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45,   45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45,  2,  3,  3],
                [  3,  3,  3, 45, 23, 14, 14, 22, 45, 23, 22, 45, 23, 14, 14, 14,   14, 14, 14, 22, 45, 23, 22, 45, 23, 14, 14, 22, 45,  2,  3,  3],
                [  3,  3,  3, 45, 27, 20, 20, 26, 45, 25, 24, 45, 27, 20, 20, 35,   34, 20, 20, 26, 45, 25, 24, 45, 27, 20, 20, 26, 45,  2,  3,  3],
                [  3,  3,  3, 45, 45, 45, 45, 45, 45, 25, 24, 45, 45, 45, 45, 25,   24, 45, 45, 45, 45, 25, 24, 45, 45, 45, 45, 45, 45,  2,  3,  3],
                [  3,  3,  5, 12, 12, 12, 12, 22, 45, 25, 27, 14, 14, 22, 44, 25,   24, 44, 23, 14, 14, 26, 24, 45, 23, 12, 12, 12, 12,  4,  3,  3],
                [  3,  3, 44, 44, 44, 44, 44,  3, 45, 25, 34, 20, 20, 26, 44, 27,   26, 44, 27, 20, 20, 35, 24, 45,  2, 44, 44, 44, 44, 44,  3,  3],
                [  3,  3, 44, 44, 44, 44, 44,  3, 45, 25, 24, 44, 44, 44, 44, 44,   44, 44, 44, 44, 44, 25, 24, 45,  2, 44, 44, 44, 44, 44,  3,  3],
                [  3,  3, 44, 44, 44, 44, 44,  3, 45, 25, 24, 44, 29, 12, 33, 44,   44, 32, 12, 28, 44, 25, 24, 45,  2, 44, 44, 44, 44, 44,  3,  3],
                [  3,  3, 10, 10, 10, 10, 10, 26, 45, 27, 26, 44,  2, 44, 44, 44,   44, 44, 44,  3, 44, 27, 26, 45, 27, 10, 10, 10, 10, 10,  3,  3],
                [ 44, 44, 44, 44, 44, 44, 44, 44, 45, 44, 44, 44,  2, 44, 44, 44,   44, 44, 44,  3, 44, 44, 44, 45, 44, 44, 44, 44, 44, 44, 44, 44],
                [  3,  3, 12, 12, 12, 12, 12, 22, 45, 23, 22, 44,  2, 44, 44, 44,   44, 44, 44,  3, 44, 23, 22, 45, 23, 12, 12, 12, 12, 12,  3,  3],
                [  3,  3, 44, 44, 44, 44, 44,  3, 45, 25, 24, 44, 31, 10, 10, 10,   10, 10, 10, 30, 44, 25, 24, 45,  2, 44, 44, 44, 44, 44,  3,  3],
                [  3,  3, 44, 44, 44, 44, 44,  3, 45, 25, 24, 44, 44, 44, 44, 44,   44, 44, 44, 44, 44, 25, 24, 45,  2, 44, 44, 44, 44, 44,  3,  3],
                [  3,  3, 44, 44, 44, 44, 44,  3, 45, 25, 24, 44, 23, 14, 14, 14,   14, 14, 14, 22, 44, 25, 24, 45,  2, 44, 44, 44, 44, 44,  3,  3],
                [  3,  3,  1, 10, 10, 10, 10, 26, 45, 27, 26, 44, 27, 20, 20, 35,   34, 20, 20, 26, 44, 27, 26, 45, 27, 10, 10, 10, 10,  0,  3,  3],
                [  3,  3,  3, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 25,   24, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45,  2,  3,  3],
                [  3,  3,  3, 45, 23, 14, 14, 22, 45, 23, 14, 14, 14, 22, 45, 25,   24, 45, 23, 14, 14, 14, 22, 45, 23, 14, 14, 22, 45,  2,  3,  3],
                [  3,  3,  3, 45, 27, 21, 35, 24, 45, 27, 20, 20, 20, 26, 45, 27,   26, 45, 27, 20, 20, 20, 26, 45, 25, 34, 20, 26, 45,  2,  3,  3],
                [  3,  3,  3, 47, 45, 45, 25, 24, 45, 45, 45, 45, 45, 45, 45, 44,   44, 45, 45, 45, 45, 45, 45, 45, 25, 24, 45, 45, 47,  2,  3,  3],
                [  3,  3,  7, 14, 22, 45, 25, 24, 45, 23, 22, 45, 23, 14, 14, 14,   14, 14, 14, 22, 45, 23, 22, 45, 25, 24, 45, 23, 14,  6,  3,  3],
                [  3,  3,  9, 20, 26, 45, 27, 26, 45, 25, 24, 45, 27, 20, 20, 35,   34, 20, 20, 40, 45, 25, 24, 45, 27, 26, 45, 27, 20,  8,  3,  3],
                [  3,  3,  3, 45, 45, 45, 45, 45, 45, 25, 24, 45, 45, 45, 45, 25,   24, 45, 45, 45, 45, 25, 24, 45, 45, 45, 45, 45, 45,  2,  3,  3],
                [  3,  3,  3, 45, 23, 14, 14, 14, 14, 37, 36, 14, 14, 22, 45, 25,   24, 45, 23, 14, 14, 37, 36, 14, 14, 14, 14, 38, 45,  2,  3,  3],
                [  3,  3,  3, 45, 27, 20, 20, 20, 20, 20, 20, 20, 20, 26, 45, 27,   26, 45, 27, 20, 20, 20, 20, 20, 20, 20, 20, 26, 45,  2,  3,  3],
                [  3,  3,  3, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45,   45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45, 45,  2,  3,  3],
                [  3,  3,  5, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12,   12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12,  4,  3,  3]
               ]

        self.__tiles = []

        #ss = Spritesheet(os.path.join("pacman", "img", "tile_sheet.png"))
        ss = Spritesheet(os.path.join("pacman", "img", "sprites.png"))

        for r, row_item in enumerate(map):
            tilerow = []
            for c, map_value in enumerate(map[r]):
                t = MazeTile(self, ss, map_value, r, c)

                # self.add(t)

                if t.tile_type == "pellet":
                    self.pellets.add(t)
                elif t.tile_type == "wall":
                    self.walls.add(t)
                elif t.tile_type == "powerpellet":
                    self.powerpellets.add(t)

                tilerow.append(t)
            self.__tiles.append(tilerow)

        self.num_rows = len(self.__tiles)
        self.num_columns = len(self.__tiles[0])
        self.actors = {}

    def add_actor(self, name, maze_actor):
        self.actors[name] = maze_actor

    def get_tile(self, r, c):
        return self.__tiles[r][c]

    def get_tile_from_screen(self, position):
        r = int(position[1] / 8)
        c = int(position[0] / 8)
        return self.__tiles[r][c]

    def draw(self, surface):
        self.walls.draw(surface)

    def is_path_clear(self, rect):
        path_is_clear = True
        path_is_clear = path_is_clear and self.get_tile_from_screen((rect.x,                  rect.y                  )).tile_type != "wall"
        path_is_clear = path_is_clear and self.get_tile_from_screen((rect.x + rect.width - 1, rect.y                  )).tile_type != "wall"
        path_is_clear = path_is_clear and self.get_tile_from_screen((rect.x,                  rect.y + rect.height - 1)).tile_type != "wall"
        path_is_clear = path_is_clear and self.get_tile_from_screen((rect.x + rect.width - 1, rect.y + rect.height - 1)).tile_type != "wall"
        return path_is_clear






class MazeActor(Actor):
    def __init__(self, name, maze, starting_position, starting_heading="right", starting_movement_speed=0, starting_animation_speed=0):
        super().__init__(name, starting_position, starting_heading, starting_movement_speed, starting_animation_speed)

        # used by the reset() method
        self._starting_position = starting_position
        self._starting_heading = starting_heading
        self._starting_movement_speed = starting_movement_speed
        self._starting_animation_speed = starting_animation_speed

        self._maze = maze
        self._queued_heading = ""
        self.mode = ""

    def reset(self):
        self._queued_heading = ""
        self._current_x = float(self._starting_position[0])
        self._current_y = float(self._starting_position[1])
        self.rect = Rect(self._starting_position[0], self._starting_position[1], 16, 16)
        self.image = pygame.Surface(self.rect.size)
        self.movement_speed = float(self._starting_movement_speed)
        self.animation_speed = float(self._starting_animation_speed)
        self.set_heading(self._starting_heading)
        self.frozen = False


    def scatter(self):
        self.mode = "scatter"
        if self.heading == "up":
            self.set_desired_heading("down")
        elif self.heading == "left":
            self.set_desired_heading("right")
        elif self.heading == "right":
            self.set_desired_heading("left")
        elif self.heading == "down":
            self.set_desired_heading("up")

    def chase(self):
        self.mode = "chase"
        if self.heading == "up":
            self.set_desired_heading("down")
        elif self.heading == "left":
            self.set_desired_heading("right")
        elif self.heading == "right":
            self.set_desired_heading("left")
        elif self.heading == "down":
            self.set_desired_heading("up")

    def set_animation(self, new_animation_name):
        if self.current_animation_name != new_animation_name:
            if self.mode == "":
                super().set_animation(new_animation_name)
            else:
                super().set_animation(self.mode + "_" + new_animation_name)



    def get_target_tile(self):
        pass

    def set_desired_heading(self, new_desired_heading):
        self._queued_heading = new_desired_heading

    def cancel_desired_heading(self):
        if self._queued_heading != "":
            self._queued_heading = ""

    def current_tile_topleft(self):
        return self._maze.get_tile_from_screen((self._current_x + 4, self._current_y + 4))

    def current_tile_bottomright(self):
        return self._maze.get_tile_from_screen((self._current_x + 11, self._current_y + 11))

    def current_tile_center(self):
        return self._maze.get_tile_from_screen((self._current_x + 7, self._current_y + 7))

    def get_target_coordinate(self):
        pass

    def get_next_heading(self, target_coordinate):
        current_tile = self.current_tile_center()

        min_distance_to_target = 999999
        d = 999999
        next_heading = ""

        # up?
        tile = current_tile.get_neighbour_tile("up")
        if tile.tile_type != "wall" and self.heading != "down":
            if current_tile.address == "11,14" or current_tile.address == "11,17" or current_tile.address == "23,14" or current_tile.address == "23,17":
                pass # no go!  special case
            else:
                d = tile.distance_to_coordinate(target_coordinate)
                if d < min_distance_to_target:
                    min_distance_to_target = d
                    next_heading = "up"

        # left?
        tile = current_tile.get_neighbour_tile("left")
        if tile.tile_type != "wall" and self.heading != "right":
            d = tile.distance_to_coordinate(target_coordinate)
            if d < min_distance_to_target:
                min_distance_to_target = d
                next_heading = "left"

        # down?
        tile = current_tile.get_neighbour_tile("down")
        if tile.tile_type != "wall" and self.heading != "up":
            if current_tile.address == "11,15" or current_tile.address == "11,16":
                pass # no go!  special case
            else:
                d = tile.distance_to_coordinate(target_coordinate)
                if d < min_distance_to_target:
                    min_distance_to_target = d
                    next_heading = "down"

        # right?
        tile = current_tile.get_neighbour_tile("right")
        if tile.tile_type != "wall" and self.heading != "left":
            d = tile.distance_to_coordinate(target_coordinate)
            if d < min_distance_to_target:
                min_distance_to_target = d
                next_heading = "right"

        if next_heading == "":
            next_heading = self.heading

        return next_heading


    def update(self):
        if self._queued_heading == "" and self.frozen:
            super().update()
        else:
            queued_heading = self._queued_heading
            if queued_heading == "":
                queued_heading = self.heading


            # Solve the move in 2 parts.  Part 1 is the distance towards the next tile.
            # Part 2 handles the distance if the actor moves into another tile
            # It's possible that the actor starts off exactly at a tile edge.  If so, the part 1 distance is zero
            # Part 2 has to handle walls.
            # If we enter part 2 with a turn requested, and the turn would hit a wall, then we ignore the request as if it's not made
            # as if no turn request was made.  Going straight forward might run into a wall.  If so, then set part 2 distance to zero (and stop)
            # Remember, that in 99.99% of cases part 1 is just a straight move forward, and part 2 is zero.

            cx = self._current_x + 4
            cy = self._current_y + 4

            dx1 = 0  # delta-x, part 1
            dy1 = 0  # delta-y, part 1

            dx2 = 0  # delta-x, part 2
            dy2 = 0  # delta-y, part 2

            # p is the total distance (in pixels) to move during this frame
            p = self.movement_speed / float(FRAME_RATE)  # pixels per frame
            p = round(p, 10)


            # -------------------------------------------------------------------------------
            # part 1:  Get to next tile, or an instant 180 degree turnaround
            # -------------------------------------------------------------------------------
            distance_to_next_tile = 0
            if self.heading == "up" or (self.heading == "down" and queued_heading == "up"):
                distance_to_next_tile = round(cy % 8, 10)
                if p > distance_to_next_tile:
                    dy1 = -distance_to_next_tile
                else:
                    dy1 = -p
            elif self.heading == "down" or (self.heading == "up" and queued_heading == "down"):
                distance_to_next_tile = round((8 - cy % 8) % 8, 10)
                if p > distance_to_next_tile:
                    dy1 = distance_to_next_tile
                else:
                    dy1 = p
            if self.heading == "left" or (self.heading == "right" and queued_heading == "left"):
                distance_to_next_tile = round(cx % 8, 10)
                if p > distance_to_next_tile:
                    dx1 = -distance_to_next_tile
                else:
                    dx1 = -p
            elif self.heading == "right" or (self.heading == "left" and queued_heading == "right"):
                distance_to_next_tile = round((8 - cx % 8) % 8, 10)
                if p > distance_to_next_tile:
                    dx1 = distance_to_next_tile
                else:
                    dx1 = p
            dx1 = round(dx1, 10)
            dy1 = round(dy1, 10)

            # -------------------------------------------------------------------------------
            # part 2:  Past the tile break (maybe a turn?)
            # -------------------------------------------------------------------------------
            if abs(dx1 + dy1) < p:
                target_coordinate = self.get_target_coordinate()
                queued_heading = self.get_next_heading(target_coordinate)
                if queued_heading == "":
                    queued_heading = self.heading

                # where are we after part 1?
                pos = (round(cx + dx1, 10), round(cy + dy1, 10))

                # if we have a 90 degree turn requested, and that turn puts us into a wall, then behave as if the request wasn't made
                if ((self.heading == "left" or self.heading == "right") and (queued_heading == "up" or queued_heading == "down")) \
                or ((self.heading == "up" or self.heading == "down") and (queued_heading == "left" or queued_heading == "right")):
                    t = self._maze.get_tile_from_screen(pos)
                    nt = t.get_neighbour_tile(queued_heading)
                    if nt.tile_type == "wall":
                        queued_heading = self.heading  # ** we check to see that we did this later.  see note

                # is the neighbour tile we're heading towards a wall?
                t = self._maze.get_tile_from_screen(pos)
                t = t.get_neighbour_tile(queued_heading)
                if t.tile_type == "wall":
                    dx2 = 0
                    dy2 = 0
                else:
                    if queued_heading == "up":
                        dx2 = 0
                        dy2 = -p - dy1
                    elif queued_heading == "down":
                        dx2 = 0
                        dy2 = p - dy1
                    elif queued_heading == "left":
                        dx2 = -p - dx1
                        dy2 = 0
                    elif queued_heading == "right":
                        dx2 = p - dx1
                        dy2 = 0

                    #if self._queued_heading != "" and self._queued_heading == queued_heading: # ** see note above
                    if queued_heading != self.heading:
                        self.set_heading(queued_heading)
                        self.set_animation(queued_heading)
                        self.cancel_desired_heading()  # cancel the request - we handled it.

            # Was this a 180 turnaround?
            if (self.heading == "down" and queued_heading == "up") \
            or (self.heading == "up" and queued_heading == "down") \
            or (self.heading == "left" and queued_heading == "right") \
            or (self.heading == "right" and queued_heading == "left"):
                self.set_heading(queued_heading)
                self.set_animation(queued_heading)
                self.cancel_desired_heading()  # cancel the request - we handled it.



            x = round(self._current_x + dx1 + dx2, 10)
            y = round(self._current_y + dy1 + dy2, 10)
            int_x = int(x)
            int_y = int(y)

            super().update()
            self._current_x = x
            self._current_y = y
            self.rect.x = int_x
            self.rect.y = int_y

            self.rect.x = int(self._current_x)
            self.rect.y = int(self._current_y)
            # self.image = self._animations[self._current_animation_name].current_frame()

            if not self.frozen and round(dx1 + dx2, 10) == 0 and round(dy1 + dy2, 10) == 0:
                self.freeze()
            elif self.frozen:
                self.thaw()

            # corridor
            if self.current_tile_topleft().c == 0 and self.heading == "left":
                self._current_x += (GAME_RESOLUTION.width - 16)
            elif self.current_tile_topleft().c == 30 and self.heading == "right":
                self._current_x -= (GAME_RESOLUTION.width - 16)











class Pacman(MazeActor):
    def __init__(self, maze, starting_position, starting_heading="right", starting_movement_speed=0, starting_animation_speed=0):
        super().__init__("Pacman", maze, starting_position, starting_heading, starting_movement_speed, starting_animation_speed)

        spritesheet = Spritesheet(os.path.join('pacman', 'img', 'sprites.png'))
        self.add_animation("up", ActorAnimation([spritesheet.image_at((34, 0, 16, 16)), spritesheet.image_at((18, 32, 16, 16)), spritesheet.image_at((2, 32, 16, 16)), spritesheet.image_at((2, 32, 16, 16)), spritesheet.image_at((18, 32, 16, 16))]))
        self.add_animation("down", ActorAnimation([spritesheet.image_at((34, 0, 16, 16)), spritesheet.image_at((18, 48, 16, 16)), spritesheet.image_at((2, 48, 16, 16)), spritesheet.image_at((2, 48, 16, 16)), spritesheet.image_at((18, 48, 16, 16))]))
        self.add_animation("left", ActorAnimation([spritesheet.image_at((34, 0, 16, 16)), spritesheet.image_at((18, 16, 16, 16)), spritesheet.image_at((2, 16, 16, 16)), spritesheet.image_at((2, 16, 16, 16)), spritesheet.image_at((18, 16, 16, 16))]))
        self.add_animation("right", ActorAnimation([spritesheet.image_at((34, 0, 16, 16)), spritesheet.image_at((18, 0, 16, 16)), spritesheet.image_at((2, 0, 16, 16)), spritesheet.image_at((2, 0, 16, 16)), spritesheet.image_at((18, 0, 16, 16))]))

        self.add_animation("die", ActorAnimation([spritesheet.image_at(( 34, 0, 16, 16)),
                                                  spritesheet.image_at(( 50, 0, 16, 16)),
                                                  spritesheet.image_at(( 66, 0, 16, 16)),
                                                  spritesheet.image_at(( 82, 0, 16, 16)),
                                                  spritesheet.image_at(( 98, 0, 16, 16)),
                                                  spritesheet.image_at((114, 0, 16, 16)),
                                                  spritesheet.image_at((130, 0, 16, 16)),
                                                  spritesheet.image_at((146, 0, 16, 16)),
                                                  spritesheet.image_at((162, 0, 16, 16)),
                                                  spritesheet.image_at((178, 0, 16, 16)),
                                                  spritesheet.image_at((194, 0, 16, 16)),
                                                  spritesheet.image_at((210, 0, 16, 16))
                                                  ], 0, 1))

        self.set_animation(starting_heading)

    def reset(self):
        super().reset()
        self.set_animation(self._starting_heading)

    def get_next_heading(self, target_coordinate):
        return self._queued_heading

    def update(self):
        super().update()
        if self.current_animation_name == "die":
            self.thaw()





class Blinky(MazeActor):
    def __init__(self, maze, starting_position, starting_heading="right", starting_movement_speed=0, starting_animation_speed=0):
        super().__init__("Blinky", maze, starting_position, starting_heading, starting_movement_speed, starting_animation_speed)

        spritesheet = Spritesheet(os.path.join('pacman', 'img', 'sprites.png'))

        self.add_animation("chase_up",      ActorAnimation([spritesheet.image_at((67, 64, 16, 16)), spritesheet.image_at((67 + 16, 64, 16, 16))]))
        self.add_animation("chase_down",    ActorAnimation([spritesheet.image_at((99, 64, 16, 16)), spritesheet.image_at((99 + 16, 64, 16, 16))]))
        self.add_animation("chase_left",    ActorAnimation([spritesheet.image_at((35, 64, 16, 16)), spritesheet.image_at((35 + 16, 64, 16, 16))]))
        self.add_animation("chase_right",   ActorAnimation([spritesheet.image_at(( 3, 64, 16, 16)), spritesheet.image_at(( 3 + 16, 64, 16, 16))]))

        self.add_animation("scatter_up",    ActorAnimation([spritesheet.image_at((67, 64, 16, 16)), spritesheet.image_at((67 + 16, 64, 16, 16))]))
        self.add_animation("scatter_down",  ActorAnimation([spritesheet.image_at((99, 64, 16, 16)), spritesheet.image_at((99 + 16, 64, 16, 16))]))
        self.add_animation("scatter_left",  ActorAnimation([spritesheet.image_at((35, 64, 16, 16)), spritesheet.image_at((35 + 16, 64, 16, 16))]))
        self.add_animation("scatter_right", ActorAnimation([spritesheet.image_at(( 3, 64, 16, 16)), spritesheet.image_at(( 3 + 16, 64, 16, 16))]))

        # these 4 are all the same, but set up to give us the name of "mode_heading"
        self.add_animation("frightened_up",    ActorAnimation([spritesheet.image_at((131, 64, 16, 16)), spritesheet.image_at((131 + 16, 64, 16, 16))]))
        self.add_animation("frightened_down",  ActorAnimation([spritesheet.image_at((131, 64, 16, 16)), spritesheet.image_at((131 + 16, 64, 16, 16))]))
        self.add_animation("frightened_left",  ActorAnimation([spritesheet.image_at((131, 64, 16, 16)), spritesheet.image_at((131 + 16, 64, 16, 16))]))
        self.add_animation("frightened_right", ActorAnimation([spritesheet.image_at((131, 64, 16, 16)), spritesheet.image_at((131 + 16, 64, 16, 16))]))

        self.mode = "chase"
        self.set_animation(self.heading)

    def reset(self):
        self.mode = "chase"
        super().reset()

    def get_target_coordinate(self):
        if self.mode == "chase":
            pacman = self._maze.actors["Pacman"]
            target_tile = pacman.current_tile_center()
            return target_tile.rect.center
        elif self.mode == "scatter":
            return 220, -12




class Pinky(MazeActor):
    def __init__(self, maze, starting_position, starting_heading="right", starting_movement_speed=0, starting_animation_speed=0):
        super().__init__("Pinky", maze, starting_position, starting_heading, starting_movement_speed, starting_animation_speed)

        spritesheet = Spritesheet(os.path.join('pacman', 'img', 'sprites.png'))

        self.add_animation("scatter_up",    ActorAnimation([spritesheet.image_at((67, 80, 16, 16)), spritesheet.image_at((67 + 16, 80, 16, 16))]))
        self.add_animation("scatter_down",  ActorAnimation([spritesheet.image_at((99, 80, 16, 16)), spritesheet.image_at((99 + 16, 80, 16, 16))]))
        self.add_animation("scatter_left",  ActorAnimation([spritesheet.image_at((35, 80, 16, 16)), spritesheet.image_at((35 + 16, 80, 16, 16))]))
        self.add_animation("scatter_right", ActorAnimation([spritesheet.image_at(( 3, 80, 16, 16)), spritesheet.image_at(( 3 + 16, 80, 16, 16))]))

        self.add_animation("chase_up",    ActorAnimation([spritesheet.image_at((67, 80, 16, 16)), spritesheet.image_at((67 + 16, 80, 16, 16))]))
        self.add_animation("chase_down",  ActorAnimation([spritesheet.image_at((99, 80, 16, 16)), spritesheet.image_at((99 + 16, 80, 16, 16))]))
        self.add_animation("chase_left",  ActorAnimation([spritesheet.image_at((35, 80, 16, 16)), spritesheet.image_at((35 + 16, 80, 16, 16))]))
        self.add_animation("chase_right", ActorAnimation([spritesheet.image_at(( 3, 80, 16, 16)), spritesheet.image_at(( 3 + 16, 80, 16, 16))]))

        # these 4 are all the same, but set up to give us the name of "mode_heading"
        self.add_animation("frightened_up",    ActorAnimation([spritesheet.image_at((131, 64, 16, 16)), spritesheet.image_at((131 + 16, 64, 16, 16))]))
        self.add_animation("frightened_down",  ActorAnimation([spritesheet.image_at((131, 64, 16, 16)), spritesheet.image_at((131 + 16, 64, 16, 16))]))
        self.add_animation("frightened_left",  ActorAnimation([spritesheet.image_at((131, 64, 16, 16)), spritesheet.image_at((131 + 16, 64, 16, 16))]))
        self.add_animation("frightened_right", ActorAnimation([spritesheet.image_at((131, 64, 16, 16)), spritesheet.image_at((131 + 16, 64, 16, 16))]))

        self.mode = "chase"
        self.set_animation(starting_heading)

    def reset(self):
        self.mode = "chase"
        super().reset()

    def get_target_coordinate(self):
        if self.mode == "chase":
            pacman = self._maze.actors["Pacman"]
            pacman_tile = pacman.current_tile_center()

            p1 = pacman_tile.center_offset(pacman.heading, 4)
            p1_x = p1[0]
            p1_y = p1[1]

            if pacman.heading == "up":
                p1_x = p1_x - 32

            return p1_x, p1_y

        elif self.mode == "scatter":
            return 36, -12








class Inky(MazeActor):
    def __init__(self, maze, starting_position, starting_heading="right", starting_movement_speed=0, starting_animation_speed=0):
        super().__init__("Inky", maze, starting_position, starting_heading, starting_movement_speed, starting_animation_speed)

        spritesheet = Spritesheet(os.path.join('pacman', 'img', 'sprites.png'))

        self.add_animation("scatter_up",    ActorAnimation([spritesheet.image_at((67, 96, 16, 16)), spritesheet.image_at((67 + 16, 96, 16, 16))]))
        self.add_animation("scatter_down",  ActorAnimation([spritesheet.image_at((99, 96, 16, 16)), spritesheet.image_at((99 + 16, 96, 16, 16))]))
        self.add_animation("scatter_left",  ActorAnimation([spritesheet.image_at((35, 96, 16, 16)), spritesheet.image_at((35 + 16, 96, 16, 16))]))
        self.add_animation("scatter_right", ActorAnimation([spritesheet.image_at(( 3, 96, 16, 16)), spritesheet.image_at(( 3 + 16, 96, 16, 16))]))

        self.add_animation("chase_up",    ActorAnimation([spritesheet.image_at((67, 96, 16, 16)), spritesheet.image_at((67 + 16, 96, 16, 16))]))
        self.add_animation("chase_down",  ActorAnimation([spritesheet.image_at((99, 96, 16, 16)), spritesheet.image_at((99 + 16, 96, 16, 16))]))
        self.add_animation("chase_left",  ActorAnimation([spritesheet.image_at((35, 96, 16, 16)), spritesheet.image_at((35 + 16, 96, 16, 16))]))
        self.add_animation("chase_right", ActorAnimation([spritesheet.image_at(( 3, 96, 16, 16)), spritesheet.image_at(( 3 + 16, 96, 16, 16))]))

        # these 4 are all the same, but set up to give us the name of "mode_heading"
        self.add_animation("frightened_up",    ActorAnimation([spritesheet.image_at((131, 64, 16, 16)), spritesheet.image_at((131 + 16, 64, 16, 16))]))
        self.add_animation("frightened_down",  ActorAnimation([spritesheet.image_at((131, 64, 16, 16)), spritesheet.image_at((131 + 16, 64, 16, 16))]))
        self.add_animation("frightened_left",  ActorAnimation([spritesheet.image_at((131, 64, 16, 16)), spritesheet.image_at((131 + 16, 64, 16, 16))]))
        self.add_animation("frightened_right", ActorAnimation([spritesheet.image_at((131, 64, 16, 16)), spritesheet.image_at((131 + 16, 64, 16, 16))]))

        self.mode = "chase"
        self.set_animation(starting_heading)

    def reset(self):
        self.mode = "chase"
        super().reset()

    def get_target_coordinate(self):
        if self.mode == "chase":
            pacman = self._maze.actors["Pacman"]
            blinky = self._maze.actors["Blinky"]
            pacman_tile = pacman.current_tile_center()
            blinky_tile = blinky.current_tile_center()

            p1 = pacman_tile.center_offset(pacman.heading, 2)
            p1_x = p1[0]
            p1_y = p1[1]
            if pacman.heading == "up":
                p1_x = p1_x - 16

            p2 = blinky_tile.rect.center
            p2_x = p2[0]
            p2_y = p2[1]

            # target point:
            # start at p2, head to p1, and double the distance
            xy = (p1_x + (p1_x - p2_x), p1_y + (p1_y - p2_y))
            return xy

        elif self.mode == "scatter":
            return 236, 260





class Clyde(MazeActor):
    def __init__(self, maze, starting_position, starting_heading="right", starting_movement_speed=0, starting_animation_speed=0):
        super().__init__("Clyde", maze, starting_position, starting_heading, starting_movement_speed, starting_animation_speed)

        spritesheet = Spritesheet(os.path.join('pacman', 'img', 'sprites.png'))

        self.add_animation("scatter_up",    ActorAnimation([spritesheet.image_at((67, 112, 16, 16)), spritesheet.image_at((67 + 16, 112, 16, 16))]))
        self.add_animation("scatter_down",  ActorAnimation([spritesheet.image_at((99, 112, 16, 16)), spritesheet.image_at((99 + 16, 112, 16, 16))]))
        self.add_animation("scatter_left",  ActorAnimation([spritesheet.image_at((35, 112, 16, 16)), spritesheet.image_at((35 + 16, 112, 16, 16))]))
        self.add_animation("scatter_right", ActorAnimation([spritesheet.image_at(( 3, 112, 16, 16)), spritesheet.image_at(( 3 + 16, 112, 16, 16))]))

        self.add_animation("chase_up",    ActorAnimation([spritesheet.image_at((67, 112, 16, 16)), spritesheet.image_at((67 + 16, 112, 16, 16))]))
        self.add_animation("chase_down",  ActorAnimation([spritesheet.image_at((99, 112, 16, 16)), spritesheet.image_at((99 + 16, 112, 16, 16))]))
        self.add_animation("chase_left",  ActorAnimation([spritesheet.image_at((35, 112, 16, 16)), spritesheet.image_at((35 + 16, 112, 16, 16))]))
        self.add_animation("chase_right", ActorAnimation([spritesheet.image_at(( 3, 112, 16, 16)), spritesheet.image_at(( 3 + 16, 112, 16, 16))]))

        # these 4 are all the same, but set up to give us the name of "mode_heading"
        self.add_animation("frightened_up",    ActorAnimation([spritesheet.image_at((131, 64, 16, 16)), spritesheet.image_at((131 + 16, 64, 16, 16))]))
        self.add_animation("frightened_down",  ActorAnimation([spritesheet.image_at((131, 64, 16, 16)), spritesheet.image_at((131 + 16, 64, 16, 16))]))
        self.add_animation("frightened_left",  ActorAnimation([spritesheet.image_at((131, 64, 16, 16)), spritesheet.image_at((131 + 16, 64, 16, 16))]))
        self.add_animation("frightened_right", ActorAnimation([spritesheet.image_at((131, 64, 16, 16)), spritesheet.image_at((131 + 16, 64, 16, 16))]))

        self.mode = "chase"
        self.set_animation(starting_heading)

    def reset(self):
        self.mode = "chase"
        super().reset()

    def get_target_coordinate(self):
        if self.mode == "chase":
            pacman = self._maze.actors["Pacman"]

            distance_to_pacman = self.current_tile_center().distance_to_tile(pacman.current_tile_center())
            if distance_to_pacman < 8 * 8:
                xy = 4, 260
            else:
                xy = pacman.current_tile_center().rect.center

            return xy

        elif self.mode == "scatter":
            return 20, 260
