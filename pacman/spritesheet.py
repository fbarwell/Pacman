import pygame

class Spritesheet(object):
    def __init__(self, filename):
        self.sheet_image = pygame.image.load(filename).convert_alpha()

    # Load a specific image from a specific rectangle
    def image_at(self, rectangle):
        ## "Loads image from x,y,x+offset,y+offset"
        #rect = pygame.Rect(rectangle)
        #image = pygame.Surface(rect.size, pygame.SRCALPHA)
        #image.blit(self.sheet_image, (0, 0), rect)
        #return image

        rect = pygame.Rect(rectangle)
        i = self.sheet_image.subsurface(rect)
        return i
