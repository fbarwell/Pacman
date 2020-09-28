import pygame
import os
import sys
from pygame.locals import *
from pacman.settings import *
#from pacman.maze import MazeActor
from pacman.maze import Pacman
from pacman.maze import Blinky
from pacman.maze import Pinky
from pacman.maze import Inky
from pacman.maze import Clyde
#from pacman.actors import ActorAnimation
#from pacman.spritesheet import Spritesheet
from pacman.maze import Maze
from pacman.timer import TimerManager
from pacman.timer import Timer





class App:
    def __init__(self):
        self.display_screen = pygame.display.set_mode(DISPLAY_RESOLUTION.size, HWSURFACE | DOUBLEBUF | RESIZABLE)
        self.state = ""


    def run(self):
        pygame.init()

        self.state = "start_screen"
        while True:
            if self.state == "start_screen":
                self.__start_screen()
            elif self.state == "playing":
                self.__playing()
            else:
                break

        pygame.quit()


    #  #################################################################################################################
    #  start_screen
    #  #################################################################################################################
    def __start_screen(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = "quit"
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = "quit"
                    running = False
                elif event.type == VIDEORESIZE:
                    DISPLAY_RESOLUTION.height = event.h
                    DISPLAY_RESOLUTION.width = event.w
                    self.display_screen = pygame.display.set_mode(DISPLAY_RESOLUTION.size, HWSURFACE | DOUBLEBUF | RESIZABLE)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.state = "playing"
                    running = False

            self.display_screen.fill((0, 255, 255))
            pygame.display.flip()
            clock.tick()


    #  #################################################################################################################
    #  playing
    #  #################################################################################################################
    def __playing(self):
        self.display_screen.fill((0, 0, 0))

        #  game screen setup of this state
        game_screen = pygame.Surface(GAME_RESOLUTION.size)
        crop_screen = pygame.Surface(CROP_RESOLUTION.size)
        background = pygame.Surface(GAME_RESOLUTION.size)

        #  sounds
        pygame.mixer.init()
        siren_channel = pygame.mixer.Channel(0)
        siren_sound = pygame.mixer.Sound(os.path.join('pacman', 'sounds', 'pacman_siren.wav'))
        waka_channel = pygame.mixer.Channel(1)
        waka_sound = pygame.mixer.Sound(os.path.join('pacman', 'sounds', 'pacman_Waka_Waka.wav'))
        intro_channel = pygame.mixer.Channel(1)
        intro_sound = pygame.mixer.Sound(os.path.join('pacman', 'sounds', 'pacman_Intro.wav'))
        die_channel = pygame.mixer.Channel(1)
        die_sound = pygame.mixer.Sound(os.path.join('pacman', 'sounds', 'pacman_Death.wav'))

        #  set up the maze
        maze = Maze()
        maze.draw(background)  # draw the maze (the walls) onto the background surface
        #game_screen.blit(background, (0, 0))  # draw the background onto the game_screen.

        #  a group for the sprites (pacman, ghosts, pellets, fruit, etc..)
        ghosts_group = pygame.sprite.Group()
        pacman_group = pygame.sprite.GroupSingle()
        pellets = pygame.sprite.Group()

        #  make the actors
        pacman = Pacman(maze, (15 * 8, 22 * 8 + 4), "left", PACMAN_STARTING_SPEED, 30)
        pacman.freeze()
        pacman_group.add(pacman)

        blinky = Blinky(maze, (15 * 8, 10 * 8 + 4), "right", GHOST_STARTING_SPEED, 20)
        blinky.freeze()
        blinky.mode = "scatter"
        ghosts_group.add(blinky)

        pinky = Pinky(maze, (15 * 8, 10 * 8 + 4), "left", GHOST_STARTING_SPEED, 20)
        pinky.freeze()
        pinky.mode = "scatter"
        ghosts_group.add(pinky)

        inky = Inky(maze, (15 * 8, 10 * 8 + 4), "left", GHOST_STARTING_SPEED, 20)
        inky.freeze()
        inky.mode = "scatter"
        ghosts_group.add(inky)

        clyde = Clyde(maze, (15 * 8, 10 * 8 + 4), "left", GHOST_STARTING_SPEED, 20)
        clyde.freeze()
        clyde.mode = "scatter"
        ghosts_group.add(clyde)

        maze.add_actor(pacman.name, pacman)
        maze.add_actor(blinky.name, blinky)
        maze.add_actor(pinky.name, pinky)
        maze.add_actor(inky.name, inky)
        maze.add_actor(clyde.name, clyde)

        #  add the pellets to the all_sprites group
        for p in maze.pellets:
            pellets.add(p)


        #  each keydown event adds to the key_stack and is popped (and processed) on keyup
        key_stack = []

        prev_state = ""
        first_pass = True

        state = "intro"
        state_timer = Timer(0, True, "")

        chase_scatter_timers = TimerManager()



        # let's do it!
        clock = pygame.time.Clock()
        running = True
        while running:
            game_screen.blit(background, (0, 0))  # draw the background onto the game_screen.

            #  --- Event Handling --------------------------------------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = "quit"
                    running = False
                elif event.type == VIDEORESIZE:
                    DISPLAY_RESOLUTION.height = event.h
                    DISPLAY_RESOLUTION.width = event.w
                    self.display_screen = pygame.display.set_mode(DISPLAY_RESOLUTION.size, HWSURFACE | DOUBLEBUF | RESIZABLE)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.state = "start_screen"
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_UP or event.key == K_DOWN or event.key == K_LEFT or event.key == K_RIGHT:
                        key_stack.append(event.key)
                elif event.type == KEYUP:
                    if event.key == K_UP or event.key == K_DOWN or event.key == K_LEFT or event.key == K_RIGHT:
                        key_stack.remove(event.key)



            #  --- State handling of the game screen --------------------------------------------
            if state == "intro":
                draw_text(game_screen, "Ready!", "arcadeclassic", 18, (100, 130), (255, 255, 0))

                if first_pass:
                    # intro_channel.set_volume(0)
                    intro_channel.play(intro_sound, 0)  # we wait for the sound to stop, and transition to state = "play"

                    pacman.reset()
                    blinky.reset()
                    pinky.reset()
                    inky.reset()
                    clyde.reset()

                    pacman.freeze()
                    blinky.freeze()
                    pinky.freeze()
                    inky.freeze()
                    clyde.freeze()
                else:
                    if intro_channel.get_sound() is None:
                        state = "play"




            # --- Pacman dies -------------------------------------------------------------------------------------------------------------------
            elif state == "die":
                if first_pass:
                    die_channel.play(die_sound, 0)
                    pacman.movement_speed = 0
                    pacman.set_animation("die")
                    pacman.animation_speed = 7.75
                else:
                    if state_timer.get_elapsed_time() > 2650:
                        state = "intro"





            # --- Play! -------------------------------------------------------------------------------------------------------------------------
            elif state == "play":
                if first_pass:
                    # start in scatter mode
                    blinky.scatter()
                    pinky.scatter()
                    inky.scatter()
                    clyde.scatter()

                    chase_scatter_timers.add_timer(1, 7000, True, "chase")  # scatter for  7 seconds, then chase
                    chase_scatter_timers.add_timer(2, 27000, True, "scatter")  # chase for 20 seconds, then scatter
                    chase_scatter_timers.add_timer(3, 34000, True, "chase")  # scatter for  7 seconds, then chase
                    chase_scatter_timers.add_timer(4, 54000, True, "scatter")  # chase for 20 seconds, then scatter
                    chase_scatter_timers.add_timer(5, 59000, True, "chase")  # scatter for  5 seconds, then chase
                    chase_scatter_timers.add_timer(6, 79000, True, "scatter")  # chase for 20 seconds, then scatter
                    chase_scatter_timers.add_timer(7, 84000, True, "chase")  # scatter for  5 seconds, then chase

                    pacman.thaw()
                    blinky.thaw()
                    pinky.thaw()
                    inky.thaw()
                    clyde.thaw()

                    if siren_channel.get_sound() is None:
                        siren_channel.play(siren_sound, -1)

                #  --- Any pacman/ghost collision? --------------------------------
                if pacman.current_tile_center() == blinky.current_tile_center() \
                or pacman.current_tile_center() == pinky.current_tile_center() \
                or pacman.current_tile_center() == inky.current_tile_center() \
                or pacman.current_tile_center() == clyde.current_tile_center():
                    siren_channel.stop()
                    chase_scatter_timers.stop_all()
                    state = "die"

                #  --- Any timers? ------------------------------------------------
                elapsed_timers = chase_scatter_timers.get_elapsed_timers()
                for key, elapsed_timer in elapsed_timers.items():
                    if elapsed_timer.tag == "chase":
                        print("chase!")
                        blinky.chase()
                        pinky.chase()
                        inky.chase()
                        clyde.chase()
                    elif elapsed_timer.tag == "scatter":
                        print("scatter!")
                        blinky.scatter()
                        pinky.scatter()
                        inky.scatter()
                        clyde.scatter()

                    chase_scatter_timers.remove_timer(key)

                #  --- Where to next for pacman? ----------------------------------
                if len(key_stack) > 0:
                    if key_stack[-1] == K_UP:
                        pacman.set_desired_heading("up")
                    elif key_stack[-1] == K_DOWN:
                        pacman.set_desired_heading("down")
                    elif key_stack[-1] == K_LEFT:
                        pacman.set_desired_heading("left")
                    elif key_stack[-1] == K_RIGHT:
                        pacman.set_desired_heading("right")
                else:
                    pacman.cancel_desired_heading()



                #  --- Are we far enough into this tile to have eaten a pellet? ------------------
                #  A tile with a pellet is 8x8 like this:
                #  00000000
                #  00000000
                #  00000000
                #  00011000
                #  00011000
                #  00000000
                #  00000000
                #  00000000

                eat = False
                if pacman.heading == "left":
                    t = maze.get_tile_from_screen((pacman.rect.x + 4, pacman.rect.y + 4))
                    if t.tile_type == "pellet" and t.draw_style != "none":
                        if pacman.rect.x + 4 < t.x + 4:
                            eat = True
                elif pacman.heading == "right":
                    t = maze.get_tile_from_screen((pacman.rect.x + 4, pacman.rect.y + 4)).get_neighbour_tile("right")
                    if t.tile_type == "pellet" and t.draw_style != "none":
                        if pacman.rect.x + 4 + 7 >= t.x + 4:
                            eat = True
                elif pacman.heading == "up":
                    t = maze.get_tile_from_screen((pacman.rect.x + 4, pacman.rect.y + 4))
                    if t.tile_type == "pellet" and t.draw_style != "none":
                        if pacman.rect.y + 4 < t.y + 4:
                            eat = True
                elif pacman.heading == "down":
                    t = maze.get_tile_from_screen((pacman.rect.x + 4, pacman.rect.y + 4)).get_neighbour_tile("down")
                    if t.tile_type == "pellet" and t.draw_style != "none":
                        if pacman.rect.y + 4 + 7 >= t.y + 4:
                            eat = True

                if eat:
                    if waka_channel.get_sound() is None:
                        waka_channel.play(waka_sound, 0)

                    # noinspection PyUnboundLocalVariable
                    t.kill()
                    t.draw_style = "none"

                if pacman.rect.x < 0:
                    pacman.x = GAME_RESOLUTION.width - 16
                elif pacman.rect.x > GAME_RESOLUTION.width - 16:
                    pacman.x = 4



            #  clear/erase the sprites, wherever they may be, leaving the background behind.
            #  After this, the game_screen is just the background again, with no sprites on it.
            pellets.clear(game_screen, background)
            pacman_group.clear(game_screen, background)
            ghosts_group.clear(game_screen, background)

            pellets.draw(game_screen)

            if pacman.current_animation_name == "die":
                pass

            pacman_group.update()
            ghosts_group.update()  # have all the sprites configure themselves as they see fit (move, resize, set colors, set image, etc..)  ie, get them ready for the next frame

            pacman_group.draw(game_screen)
            if pacman.current_animation_name != "die":
                ghosts_group.draw(game_screen)  # redraw all the sprites to the game screen.

            crop_screen.blit(game_screen, (-16, 0))
            self.display_screen.blit(pygame.transform.scale(crop_screen, DISPLAY_RESOLUTION.size), (0, 0))  # with game_screen ready to be shown, draw it to the display_screen
            pygame.display.flip()  # and now, finally, do the actual update of the display itself


            clock.tick(FRAME_RATE)
            #print("time {0}, pacman (x,y) = ({1},{2})".format(pygame.time.get_ticks(), pacman.rect.x, pacman.rect.y))
            if prev_state != state:
                first_pass = True
                state_timer.start()
            else:
                first_pass = False

            prev_state = state
        #  --- Done (clean up) ----------------------------------------------------------------
        if not siren_channel.get_sound() is None:
            siren_channel.stop()
        if not waka_channel.get_sound() is None:
            waka_channel.stop()
        pygame.mixer.quit()



def draw_text(screen, text, font_name, size, position, color):
    font = pygame.font.Font(os.path.join("pacman", "fonts", font_name + ".ttf"), size)
    t = font.render(text, False, color)
    screen.blit(t, position)







