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
        self.levels = ["level1.txt", "level2.txt", "level3.txt", "level4.txt", "level5.txt"] # list of level files
        self.current_level = 0  # start on level 1
        self.finished_game = False  # tracks if all levels are done

    def load_data(self): 
        self.game_dir = path.dirname(__file__) #loading in the text for the level from the file where the game is
        # load the current level file
        self.map = Map(path.join(self.game_dir, self.levels[self.current_level]))

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
            # if there is another level, start it
            self.current_level += 1
            if self.current_level < len(self.levels):
                self.playing = False
            else:
                self.won = True
                self.finished_game = True
                self.playing = False


        # if the player collides with the sprite enemy it will respawn at the start
        if self.player and pg.sprite.spritecollide(self.player, self.all_enemies, False, collide_hit_rect):
            if self.player.lives > 0:
                self.player.lives -= 1
                self.player.respawn() #calling respawn function from sprites

            # checking if the game is over by checking the amount of lives remaining
            if self.player.lives <= 0:
                self.player.lives = 0
                self.playing = False
                self.running = False
                if self.running == False:
                    g.show_lose_screen()

    def draw(self):
        self.screen.fill(BG_COLOR) #setting the code for the text and writing the game text to tell the player what to do
        self.all_sprites.draw(self.screen)
        self.draw_text("ESCAPE THE ABYSS", 40, GOAL_COLOR, 20, 10, center=False)
        self.draw_text("A/D or Arrow Keys = Move", 22, TEXT_COLOR, WIDTH // 2, HEIGHT - 70)
        self.draw_text("SPACE or W = Jump / Double Jump", 22, TEXT_COLOR, WIDTH // 2, HEIGHT - 40)
        self.draw_text(f"Lives: {self.player.lives}", 24, TEXT_COLOR, WIDTH - 140, 10, center=False) #wrtiing the lives on screen for the player to see
        pg.display.flip()

   # display a victory screen and keep it open until the player closes the window
    def show_win_screen(self):
        waiting = True
        while waiting and self.running:  # keep the win screen active while the game is running
            self.screen.fill(WIN_COLOR)   # fill the screen with the background color
            # draw the main victory message in the center of the screen
            self.draw_text("YOU ESCAPED THE ABYSS", 48, GOAL_COLOR, WIDTH // 2, HEIGHT // 2 - 40)

            # draw the instruction text below the main message
            self.draw_text("Press close to exit", 24, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 20)

            pg.display.flip()  # update the screen to show the text

            for event in pg.event.get():  # check for player input/events
                if event.type == pg.QUIT:  # checking if the player has closed the window
                    waiting = False        # stop waiting for the player to quit the screen
                    self.running = False   # stop running the game

    def show_lose_screen(self):
        waiting = True
        while waiting:  # keep the loss screen active while the game is running
            self.screen.fill(BG_COLOR)   # fill the screen with the background color
            # draw the main victory message in the center of the screen
            self.draw_text("YOU LOSE", 48, ENEMY_COLOR, WIDTH // 2, HEIGHT // 2 - 40)

            # draw the instruction text below the main message
            self.draw_text("Press close to exit", 24, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 20)

            pg.display.flip()  # update the screen to show the text

            for event in pg.event.get():  # check for player input/events
                if event.type == pg.QUIT:  # checking if the player has closed the window
                    waiting = False        # stop waiting for the player to quit the screen
                    self.running = False   # stop running the game


    def draw_text(self, text, size, color, x, y, center=True):
        font = pg.font.Font(None, size) #setting font for text and putting the stuff on the screen
        surf = font.render(text, True, color)
        shadow = font.render(text, True, (0, 0, 0))
        if center:
            rect = surf.get_rect(center=(x, y))
            shadow_rect = shadow.get_rect(center=(x + 2, y + 2))
        else:
            rect = surf.get_rect(topleft=(x, y))
            shadow_rect = shadow.get_rect(topleft=(x + 2, y + 2))
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(surf, rect)


if __name__ == "__main__": #run the game
    g = Game()
    while g.running:
        g.new()
        #checks if all the levels are finished before showing that you won the game
        if g.finished_game:
            g.show_win_screen()
        elif not g.running:
            break

    pg.quit()