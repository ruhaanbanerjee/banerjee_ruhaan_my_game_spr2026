import pygame as pg
from settings import *


class Map:
    def __init__(self, filename):
        # creating the data for builing the map using a list
        self.data = []

        # open a specific file and close it with 'with'
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        # setting the tile width and the size based on the value defined in settings "TILESIZE"
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE


class Spritesheet:
    def __init__(self, filename): #initializing the class spritesheet to convert the image onto th character
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height): #scaling the image to fit on the surface of the player which is the size of a pixel
        image = pg.Surface((width, height)) # it scales the image on one frame or one image
        image.blit(self.spritesheet, (0,0), (x,y, width, height))
        new_image = pg.transform.scale(image, (width, height))
        image = new_image
        return image


# this class creates a countdown timer for a cooldown
class Cooldown:
    def __init__(self, time):
        self.start_time = 0
        # allows us to set property for time until cooldown
        self.time = time
        # self.current_time = self.time
    def start(self):
        self.start_time = pg.time.get_ticks()

    def ready(self):
        # sets current time to 
        current_time = pg.time.get_ticks()
        # if the difference between current and start time are greater than self.time
        # return True
        if current_time - self.start_time >= self.time:
            return True
        return False