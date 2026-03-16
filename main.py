import pygame as pg
from os import path
from settings import *
from sprites import *
from utils import *


class Game:
    def __init__(self): # initializing the game class
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT)) #setting the screen to the width and height defined in settings
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True #checking for running, playing, and winning
        self.playing = True
        self.won = False

    def load_data(self): 
        self.game_dir = path.dirname(__file__) #loading in the text for the level from the file where the game is
        self.map = Map(path.join(self.game_dir, "level1.txt"))

    def new(self):
        self.load_data()

        self.all_sprites = pg.sprite.Group() #initalizing all of the sprites so that it all connects to all sprites
        self.all_walls = pg.sprite.Group()
        self.all_goals = pg.sprite.Group()
        self.all_enemies = pg.sprite.Group()
        self.all_powerups = pg.sprite.Group()
        self.all_breakables = pg.sprite.Group()

        self.player = None #the player will be created later
        self.won = False

        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles): #setting each symbol in the level 1 code to a certain sprite from the sprites module
                if tile == "1":
                    Wall(self, col, row)
                elif tile == "P":
                    self.player = Player(self, col, row)
                elif tile == "G":
                    Goal(self, col, row)
                elif tile == "E":
                    Enemy(self, col, row)
                elif tile == "U":
                    PowerUp(self, col, row)
                elif tile == "B":
                    BreakableWall(self, col, row)

        self.run()

    def run(self):
        self.playing = True #just checking for the function to be playing and initialzing the other functions for playing
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pg.event.get(): #checking if the person has quit the game or not
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False

            if event.type == pg.KEYDOWN: #when the player presses space or W the player jumps
                if event.key in (pg.K_SPACE, pg.K_w) and self.player:
                    self.player.jump()

    def update(self):
        self.all_sprites.update() #updates the sprites based on their new positions

        # if the player touches the goal then the game ends and the level is complete
        if self.player and pg.sprite.spritecollide(self.player, self.all_goals, False, collide_hit_rect):
            self.won = True
            self.playing = False

    def draw(self):
        self.screen.fill(BG_COLOR) #setting the game fill to the background color established in settings
        self.all_sprites.draw(self.screen) #drawing the screen in

        self.draw_text("Escape the Abyss", 30, TEXT_COLOR, WIDTH // 2, 12) #writing text on the screen for the name of the game
        self.draw_text("A/D move   SPACE jump/double jump", 22, TEXT_COLOR, WIDTH // 2, 48) #writing the instructions for the game on the screen

        pg.display.flip() #updates the entire window

    # display a victory screen and keep it open until the player closes the window
    def show_win_screen(self):
        waiting = True
        while waiting and self.running: # keep the win screen active while the game is running
            self.screen.fill(BG_COLOR)  #fill the screen with the background color
            self.draw_text("YOU ESCAPED THE ABYSS", 44, GOAL_COLOR, WIDTH // 2, HEIGHT // 2 - 40)
            self.draw_text("Close window to quit", 24, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 20)
            pg.display.flip() # update the screen to show the text

            for event in pg.event.get():
                if event.type == pg.QUIT: #checking for if the player has quit the window yet
                    waiting = False #stop waiting for the player to quit the screen
                    self.running = False #stop running the game

    def draw_text(self, text, size, color, x, y):
        font = pg.font.SysFont("arial", size)
        surf = font.render(text, True, color) #setting the font, positions and rendering it to an image surface
        rect = surf.get_rect(midtop=(x, y))
        self.screen.blit(surf, rect) #drawing the text onto the screen


if __name__ == "__main__": #run the game
    g = Game()
    while g.running:
        g.new()
        if g.won: #checking if the player has won the game
            g.show_win_screen()
        else: #checks if it needs to break the loop and end the game
            break
    pg.quit()