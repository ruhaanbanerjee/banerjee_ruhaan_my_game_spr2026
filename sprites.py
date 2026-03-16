import pygame as pg                          # import pygame and name it pg
from pygame.sprite import Sprite             # import the Sprite class
from settings import *                       # import all game settings like colors and sizes

vec = pg.math.Vector2                        # shorter name for pygame's 2D vector class


# Check if one sprite's hit box is touching another sprite's rectangle
def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)


# Stop a sprite from moving through walls
def collide_with_walls(sprite, group, dir):
    if dir == "x":                           # handle left/right collision
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)  # find walls being touched
        if hits:                             # if the sprite hit a wall
            if sprite.vel.x > 0:             # if moving right
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2    # place sprite to left of wall
            elif sprite.vel.x < 0:           # if moving left
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2   # place sprite to right of wall
            sprite.vel.x = 0                 # stop horizontal movement
            sprite.hit_rect.centerx = sprite.pos.x   # update hit box position

    if dir == "y":                           # handle up/down collision
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)  # find walls being touched
        if hits:                             # if the sprite hit a wall
            if sprite.vel.y > 0:             # if falling down
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2    # place sprite on top of wall
            elif sprite.vel.y < 0:           # if moving upward
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2 # place sprite below wall
            sprite.vel.y = 0                 # stop vertical movement
            sprite.hit_rect.centery = sprite.pos.y  # update hit box position


# Player class
class Player(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites       # put player in the all_sprites group
        Sprite.__init__(self, self.groups)   # initialize the sprite
        self.game = game                     # save reference to the game

        self.image = pg.Surface((TILESIZE - 6, TILESIZE - 4))  # create player image
        self.image.fill(PLAYER_COLOR)        # color the player
        self.rect = self.image.get_rect()    # get player rectangle

        self.hit_rect = PLAYER_HIT_RECT.copy()   # make a hit box for collisions
        self.pos = vec((x + 0.5) * TILESIZE, (y + 0.5) * TILESIZE)  # starting position
        self.vel = vec(0, 0)                 # starting velocity
        self.acc = vec(0, 0)                 # starting acceleration

        self.on_ground = False               # player starts not on the ground
        self.jump_count = 0                  # no jumps used yet
        self.lives = PLAYER_MAX_LIVES        # set player lives

        self.rect.center = self.pos          # place the image at the start position
        self.hit_rect.center = self.pos      # place the hit box at the start position

    # Read keyboard input and set movement
    def get_keys(self):
        self.acc = vec(0, GRAVITY)           # gravity always pulls player downward
        keys = pg.key.get_pressed()          # check which keys are held down

        if keys[pg.K_a] or keys[pg.K_LEFT]:  # move left if A or left arrow is held
            self.acc.x = -PLAYER_SPEED
        if keys[pg.K_d] or keys[pg.K_RIGHT]: # move right if D or right arrow is held
            self.acc.x = PLAYER_SPEED

        self.acc.x += self.vel.x * FRICTION  # apply friction to horizontal movement

    # Make the player jump or double jump
    def jump(self):
        if self.on_ground:                   # if player is standing on ground
            self.vel.y = JUMP_VEL            # do first jump
            self.jump_count = 1              # record one jump used
            self.on_ground = False           # player is now in the air
        elif self.jump_count == 1:           # if one jump was already used
            self.vel.y = DOUBLE_JUMP_VEL     # do second jump
            self.jump_count = 2              # record second jump used

    # Update the player every frame
    def update(self):
        self.get_keys()                      # read movement input

        self.vel += self.acc                 # change velocity using acceleration
        if self.vel.y > MAX_FALL_SPEED:      # prevent falling too fast
            self.vel.y = MAX_FALL_SPEED

        self.pos.x += self.vel.x             # move horizontally
        self.hit_rect.centerx = self.pos.x   # move hit box horizontally
        collide_with_walls(self, self.game.all_walls, "x")  # stop at walls horizontally

        self.pos.y += self.vel.y             # move vertically
        self.hit_rect.centery = self.pos.y   # move hit box vertically
        collide_with_walls(self, self.game.all_walls, "y")  # stop at walls vertically

        self.rect.center = self.hit_rect.center   # match image position to hit box

        # Check if player is standing on the ground
        self.hit_rect.y += 2                 # move hit box slightly down for checking
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False, collide_hit_rect)  # see if touching wall below
        self.hit_rect.y -= 2                 # move hit box back

        if hits:                             # if touching the ground
            self.on_ground = True            # player is on the ground
            self.jump_count = 0              # reset jump count
        else:
            self.on_ground = False           # player is in the air


# Wall class for platforms and solid blocks
class Wall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_walls   # add wall to sprite and wall groups
        Sprite.__init__(self, self.groups)               # initialize the sprite
        self.game = game                                 # save reference to the game
        self.image = pg.Surface((TILESIZE, TILESIZE))    # create wall image
        self.image.fill(WALL_COLOR)                      # color the wall
        self.rect = self.image.get_rect(topleft=(x * TILESIZE, y * TILESIZE))  # place wall on grid


# Goal class for the finish tile
class Goal(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_goals   # add goal to sprite and goal groups
        Sprite.__init__(self, self.groups)               # initialize the sprite
        self.game = game                                 # save reference to the game
        self.image = pg.Surface((TILESIZE, TILESIZE))    # create goal image
        self.image.fill(GOAL_COLOR)                      # color the goal
        self.rect = self.image.get_rect(topleft=(x * TILESIZE, y * TILESIZE))  # place goal on grid


# Enemy class
class Enemy(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_enemies # add enemy to sprite and enemy groups
        Sprite.__init__(self, self.groups)               # initialize the sprite
        self.game = game                                 # save reference to the game
        self.image = pg.Surface((TILESIZE - 6, TILESIZE - 6))  # create enemy image
        self.image.fill(ENEMY_COLOR)                     # color the enemy
        self.rect = self.image.get_rect(center=((x + 0.5) * TILESIZE, (y + 0.5) * TILESIZE))  # place enemy


# Power-up class
class PowerUp(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_powerups  # add power-up to sprite and power-up groups
        Sprite.__init__(self, self.groups)                 # initialize the sprite
        self.game = game                                   # save reference to the game
        self.image = pg.Surface((TILESIZE - 12, TILESIZE - 12))  # create power-up image
        self.image.fill(POWERUP_COLOR)                     # color the power-up
        self.rect = self.image.get_rect(center=((x + 0.5) * TILESIZE, (y + 0.5) * TILESIZE))  # place power-up


# Breakable wall class
class BreakableWall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_breakables  # add breakable wall to sprite and breakable groups
        Sprite.__init__(self, self.groups)                   # initialize the sprite
        self.game = game                                     # save reference to the game
        self.image = pg.Surface((TILESIZE, TILESIZE))        # create breakable wall image
        self.image.fill(BREAKABLE_COLOR)                     # color the breakable wall
        self.rect = self.image.get_rect(topleft=(x * TILESIZE, y * TILESIZE))  # place breakable wall on grid


# Coin class
class Coin(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites       # add coin to all_sprites group
        Sprite.__init__(self, self.groups)   # initialize the sprite
        self.game = game                     # save reference to the game
        self.image = pg.Surface((TILESIZE // 2, TILESIZE // 2))  # create coin image
        self.image.fill(YELLOW)              # color the coin
        self.rect = self.image.get_rect(center=((x + 0.5) * TILESIZE, (y + 0.5) * TILESIZE))  # place coin

    def update(self):
        pass                                 # coin does nothing each frame right now