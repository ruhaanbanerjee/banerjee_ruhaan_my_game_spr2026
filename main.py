# game engine using template from Chris Bradfield's "Making Games with Python & Pygame"
# 
'''
Main file responsible for game loop including input, update, and draw methods.


'''

import pygame as pg
import sys
from os import path #acceses file an operating system
from settings import *
from sprites import *
from utils import *
vec = pg.math.Vector2
# import settings


# the game class that will be instantiated in order to run the game...
class Game:
    def __init__(self):
        pg.init()
        # setting up pygame screen using tuple value for width height
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.playing = True
        self.game_cooldown = Cooldown(5000)
        
        
        # self.load_data()
    
    # a method is a function tied to a Class

    def load_data(self):
        self.game_dir = path.dirname(__file__) #accesses the file space that we are currently in
        self.map = Map(path.join(self.game_dir, 'level1.txt'))
        print('data is loaded')

    def new(self):
        self.load_data()
        self.all_sprites = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()
        # self.player = Player(self, 15, 15) # initiating the classes of player, mob, and wall
        # self.mob = Mob(self, 4, 4) 
        # self.wall = Wall(self, WIDTH/2/TILESIZE, HEIGHT/2/TILESIZE)
        for row, tiles in enumerate(self.map.data):
            for col, tile, in enumerate(tiles):
                if tile  == '1':
                    # call class constructor without assigning variable...when
                    Wall(self, col, row)
                if tile == "P":
                    self.player = Player(self, col, row)
        
        self.run()

    def run(self):
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000 # the running function that keeps going while the game is running
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: # making sure that we can quit the game when it is not running
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.MOUSEBUTTONUP: #getting input based on mouse up, key down, or key up
                print("i can get mouse input")
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_k:
                    print("i can determine when keys are pressed")

            if event.type == pg.KEYUP:
                if event.key == pg.K_k:
                    print("i can determine when keys are released")
    


    def quit(self):
        pass

    def update(self):
        self.all_sprites.update() # updating all the sprites to their new position

    
    def draw(self):
        self.screen.fill(BLUE)
        self.draw_text("Hello World", 24, WHITE, WIDTH/2, TILESIZE) #drawing the important objects and text on the screen
        self.draw_text(str(self.dt), 24, WHITE, WIDTH/2, HEIGHT/4)
        # self.draw_text(str(self.game_cooldown.time), 24, WHITE, WIDTH/2, HEIGHT/.5)
        self.draw_text(str(self.game_cooldown.ready()), 24, WHITE, WIDTH/2, HEIGHT/3)
        self.draw_text(str(self.player.pos), 24, WHITE, WIDTH/2, HEIGHT-TILESIZE*3)
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    def draw_text(self, text, size, color, x, y):
        font_name = pg.font.match_font('arial') # setting text and, font size and position
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x,y)
        self.screen.blit(text_surface, text_rect)

if __name__ == "__main__":
    g = Game()

while g.running:
    g.new() #making sure that when the game is running it runs the new function


pg.quit()


    

    
