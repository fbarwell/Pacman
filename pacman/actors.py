import pygame
# from pygame.locals import *
from pacman.settings import *




class ActorAnimation:
    def __init__(self, frame_list, animation_speed=0, max_plays=0):
        self._frame_index = float(0)
        self._frames = frame_list
        self._animation_speed = float(animation_speed)
        self._animation_reference_counter = 0
        self.play_count = 0
        self.max_plays = max_plays


    def add_frame(self, new_image):
        self._frames.append(new_image)

    def reset(self):
        self._animation_reference_counter = 0
        self._frame_index = 0
        self.play_count = 0

    def animate(self):
        if self._animation_speed == 0:
            image = self._frames[int(self._frame_index)]
        else:
            self._frame_index += (self._animation_speed / float(FRAME_RATE))
            if int(self._frame_index) >= len(self._frames):
                self._frame_index = float(0)
                self.play_count += 1

            if self.play_count == self.max_plays and self.max_plays != 0:
                image = self._frames[len(self._frames) - 1]
            else:
                image = self._frames[int(self._frame_index)]

        return image

    def current_frame(self):
        return self._frames[int(self._frame_index)]

    @property
    def animation_speed(self):
        return self._animation_speed

    @animation_speed.setter
    def animation_speed(self, rhs):
        self._animation_speed = rhs



class Actor(pygame.sprite.Sprite):

    def __init__(self, name, starting_position, starting_heading="right", starting_movement_speed=0, starting_animation_speed=0):
        pygame.sprite.Sprite.__init__(self)

        self.name = name
        self._movement_speed = float(0)  # in pixels per frame
        self._speed_x = float(0)
        self._speed_y = float(0)
        self._current_x = float(starting_position[0])
        self._current_y = float(starting_position[1])
        self._heading = ""
        self._animation_speed = ""
        self._animations = dict()   # a dictionary of key/value pairs, where the key is a heading and the value is an Animation() object

        self.rect = Rect(starting_position[0], starting_position[1], 16, 16)
        self.image = pygame.Surface(self.rect.size)
        self.movement_speed = float(starting_movement_speed)
        self.animation_speed = float(starting_animation_speed)
        self.set_heading(starting_heading)
        self._current_animation_name = ""
        self.frozen = False

    def print_state(self):
        print("Actor state:")
        print("    self._current x,y   = {0},{1}".format(self._current_x, self._current_y))
        print("    self.rect x,y       = {0},{1}".format(self.rect.x, self.rect.y))
        print("    self.heading        = " + self._heading)
        print("    self.frozen         = " + str(self.frozen))

    def freeze(self):
        self.frozen = True

    def thaw(self):
        self.frozen = False



    def update(self):
        if not self.frozen:
            self._current_x += self._speed_x
            self._current_y += self._speed_y
            self.image = self._animations[self._current_animation_name].animate()
            self.rect.x = int(self._current_x)
            self.rect.y = int(self._current_y)
        else:
            self.rect.x = int(self._current_x)
            self.rect.y = int(self._current_y)
            self.image = self._animations[self._current_animation_name].current_frame()

    def add_animation(self, animation_name, actor_animation):
        self._animations[animation_name] = actor_animation
        actor_animation.animation_speed = self._animation_speed

    @property
    def current_animation_name(self):
        return self._current_animation_name


    def set_animation(self, new_animation_name):
        self._current_animation_name = new_animation_name
        self._animations[self._current_animation_name].reset()

    @property
    def heading(self):
        return self._heading


    def set_heading(self, new_heading):
        if self._heading != new_heading:
            self._heading = new_heading
            if self._heading == "up":
                self._speed_x = 0
                self._speed_y = -self.movement_speed / float(FRAME_RATE)

            elif self._heading == "down":
                self._speed_x = 0
                self._speed_y = self.movement_speed / float(FRAME_RATE)

            elif self._heading == "left":
                self._speed_x = -self.movement_speed / float(FRAME_RATE)
                self._speed_y = 0

            elif self._heading == "right":
                self._speed_x = self.movement_speed / float(FRAME_RATE)
                self._speed_y = 0


    @property
    def movement_speed(self):
        return self._movement_speed

    @movement_speed.setter
    def movement_speed(self, rhs):
        self._movement_speed = rhs
        if self._heading == "up":
            self._speed_x = 0
            self._speed_y = -float(rhs) / float(FRAME_RATE)
        elif self._heading == "down":
            self._speed_x = 0
            self._speed_y = float(rhs) / float(FRAME_RATE)
        elif self._heading == "left":
            self._speed_x = -float(rhs) / float(FRAME_RATE)
            self._speed_y = 0
        elif self._heading == "right":
            self._speed_x = float(rhs) / float(FRAME_RATE)
            self._speed_y = 0


    @property
    def animation_speed(self):
        return self._animation_speed

    @animation_speed.setter
    def animation_speed(self, rhs):
        self._animation_speed = rhs
        for a in self._animations.values():
            a.animation_speed = rhs

