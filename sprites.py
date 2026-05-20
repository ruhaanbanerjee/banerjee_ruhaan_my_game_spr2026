import pygame as pg                          
from pygame.sprite import Sprite             
from settings import *                       

vec = pg.math.Vector2                        # shorter name for pygame's 2D vector class


# Check if one sprite's hit box is touching another sprite
def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)


# Stop a sprite from moving through walls
def collide_with_walls(sprite, group, dir):
    if dir == "x":                           # left/right collision
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)  # find walls being hit
        if hits:                             # if the sprite hit a wall
            if sprite.vel.x > 0:            
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2    # place sprite to left of wall
            elif sprite.vel.x < 0:           
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2   # place sprite to right of wall
            sprite.vel.x = 0                 # stop horizontal movement
            sprite.hit_rect.centerx = sprite.pos.x   # update hit position

    if dir == "y":                           # up/down collision
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)  # find walls being touched
        if hits:                             # if the sprite hit a wall
            if sprite.vel.y > 0:             
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2    # place sprite on top of wall
            elif sprite.vel.y < 0:           
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2 # place sprite below wall
            sprite.vel.y = 0                 
            sprite.hit_rect.centery = sprite.pos.y  # update hit position


# Player class
class Player(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites       # put player in the all_sprites group
        Sprite.__init__(self, self.groups)   # initialize the sprite
        self.game = game                     
        self.image = pg.Surface((TILESIZE - 6, TILESIZE - 4))  # create player image
        self.image.fill(PLAYER_COLOR)        
        self.rect = self.image.get_rect()    

        self.hit_rect = PLAYER_HIT_RECT   # make a hit box for collisions
        self.pos = vec((x + 0.5) * TILESIZE, (y + 0.5) * TILESIZE)  # starting position
        self.spawn = vec((x + 0.5) * TILESIZE, (y + 0.5) * TILESIZE) #setting the position of the player starting as spawn
        self.vel = vec(0, 0)                 
        self.acc = vec(0, 0)                 
        self.on_ground = False               
        self.jump_count = 0                  # no jumps used yet
        self.lives = PLAYER_MAX_LIVES        # set player lives
        self.last_hit = 0

        # 1 means facing right, -1 means facing left
        self.facing = 1

        #keeps track of whether the player is punching
        self.attacking = False
        self.attack_start = 0
        self.last_attack = 0

        # this is the invisible punch hitbox
        self.attack_rect = pg.Rect(0, 0, PUNCH_RANGE, PUNCH_WIDTH)

        self.rect.center = self.pos          # place the image at the start position
        self.hit_rect.center = self.pos      

    # Read keyboard input and set movement
    def get_keys(self):
        self.acc = vec(0, GRAVITY)           # gravity always pulls player downward
        keys = pg.key.get_pressed()          # check which keys are held down

        # move left if A or left arrow is held
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_SPEED
            self.facing = -1

        # move right if D or right arrow is held
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_SPEED
            self.facing = 1

        self.acc.x += self.vel.x * FRICTION  # apply friction to horizontal movement

    # Make the player jump or double jump
    def jump(self):
        if self.on_ground:                   # if player is standing on ground
            self.vel.y = JUMP_VEL            
            self.jump_count = 1              # record one jump used
            self.on_ground = False           
        elif self.jump_count == 1:           # if one jump was already used
            self.vel.y = DOUBLE_JUMP_VEL     
            self.jump_count = 2              # record second jump used

    def punch(self):
        # get the current game time
        now = pg.time.get_ticks()

        # do not let the player punch too fast
        if now - self.last_attack < ATTACK_COOLDOWN:
            return

        # save the time when this punch happened
        self.last_attack = now
        self.attack_start = now

        # turn on attacking mode
        self.attacking = True

        # if player is facing right, make hitbox on right side
        if self.facing == 1:
            self.attack_rect = pg.Rect(self.hit_rect.right, self.hit_rect.centery - PUNCH_WIDTH // 2, PUNCH_RANGE, PUNCH_WIDTH)

        # if player is facing left, make hitbox on left side
        else:
            self.attack_rect = pg.Rect(self.hit_rect.left - PUNCH_RANGE, self.hit_rect.centery - PUNCH_WIDTH // 2, PUNCH_RANGE, PUNCH_WIDTH)

        # find enemies that are touching the punch hitbox
        enemies_hit = pg.sprite.spritecollide(self, self.game.all_enemies, False, lambda player, enemy: self.attack_rect.colliderect(enemy.rect))

        # remove each enemy that was punched
        for enemy in enemies_hit:
            enemy.kill()

        # find breakable walls touching the punch hitbox
        walls_hit = pg.sprite.spritecollide(self, self.game.all_breakables, False, lambda player, wall: self.attack_rect.colliderect(wall.rect))

        # remove each breakable wall that was punched
        for wall in walls_hit:
            wall.kill()

    def respawn(self): #respawning if hit with the enemy
        self.pos = self.spawn #setting position back to the original start point
        self.vel = vec(0, 0) 
        self.acc = vec(0, 0)
        self.hit_rect.center = self.pos
        self.rect.center = self.pos
        self.last_hit = pg.time.get_ticks()
    # Update the player every frame

    def update(self):
        self.get_keys()                      # read movement input

        self.vel += self.acc                 # change velocity using acceleration
        if self.vel.y > MAX_FALL_SPEED:      # prevent falling too fast
            self.vel.y = MAX_FALL_SPEED

        self.pos.x += self.vel.x             # move horizontally
        self.hit_rect.centerx = self.pos.x   
        collide_with_walls(self, self.game.all_walls, "x")  # stop at walls

        self.pos.y += self.vel.y             # move vertically
        self.hit_rect.centery = self.pos.y   
        collide_with_walls(self, self.game.all_walls, "y") 

        self.rect.center = self.hit_rect.center   

        # check if player is standing on the ground
        self.hit_rect.y += 2                 
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False, collide_hit_rect)  # see if touching wall below
        self.hit_rect.y -= 2                 

        if hits:                             # if touching the ground
            self.on_ground = True            # player is on the ground
            self.jump_count = 0              # reset jump count
        else:
            self.on_ground = False           # player is in the air\
        
        # if the player is currently punching
        if self.attacking:
            now = pg.time.get_ticks()

            # stop showing the punch after a short time
            if now - self.attack_start > ATTACK_TIME:
                self.attacking = False

class Enemy(Sprite):
    def __init__(self, game, x, y): #created enemy class
        self.groups = game.all_sprites, game.all_enemies #setting to to two different groups, all sprites and all enemies
        Sprite.__init__(self, self.groups)
        self.game = game

        self.image = pg.Surface((TILESIZE - 6, TILESIZE - 6)) #setting the size of the mob
        self.image.fill(ENEMY_COLOR)
        self.rect = self.image.get_rect()

        self.start_x = (x + 0.5) * TILESIZE #setting the starting position of the enemy
        self.y = (y + 0.5) * TILESIZE
        self.x = self.start_x #current x position of the enemy
        self.direction = 1 
        self.speed = 2 #how fast the enemy moves
        self.range = 80 #how far the enemy moves from its starting point

        self.rect.center = (self.x, self.y) #changing location

    def update(self):
        self.x += self.speed * self.direction #moving the enemy left or right

        if self.x > self.start_x + self.range: #if enemy goes too far right
            self.direction = -1 
        if self.x < self.start_x - self.range: #if enemy goes too far left
            self.direction = 1 

        self.rect.center = (int(self.x), int(self.y)) #updating position on screen

# Wall class for platforms and solid blocks
class Wall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_walls   # add wall to sprite and wall groups
        Sprite.__init__(self, self.groups)               # initialize the sprite
        self.game = game                                 
        self.image = pg.Surface((TILESIZE, TILESIZE))    # create wall image
        self.image.fill(WALL_COLOR)                     
        self.rect = self.image.get_rect(topleft=(x * TILESIZE, y * TILESIZE))  


# Goal class for the finish tile
class Goal(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_goals   # add goal to sprite and goal groups
        Sprite.__init__(self, self.groups)               # initialize the sprite
        self.game = game                                
        self.image = pg.Surface((TILESIZE, TILESIZE))    # create goal image
        self.image.fill(GOAL_COLOR)                      
        self.rect = self.image.get_rect(topleft=(x * TILESIZE, y * TILESIZE)) 



# BreakableWall Class
class BreakableWall(Sprite):
    def __init__(self, game, x, y):
        # add wall to all sprites, walls, and breakables
        self.groups = game.all_sprites, game.all_walls, game.all_breakables

        # initialize the sprite with those groups
        Sprite.__init__(self, self.groups)

        self.game = game

        # create the breakable wall image
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(BREAKABLE_COLOR)

        # place the wall on the map grid
        self.rect = self.image.get_rect(topleft=(x * TILESIZE, y * TILESIZE))

# Coin class
class Coin(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites       # add coin to all_sprites group
        Sprite.__init__(self, self.groups)   # initialize the sprite
        self.game = game                    
        self.image = pg.Surface((TILESIZE // 2, TILESIZE // 2))  # create coin image
        self.image.fill(YELLOW)              
        self.rect = self.image.get_rect(center=((x + 0.5) * TILESIZE, (y + 0.5) * TILESIZE))  

    def update(self):
        pass                                 # coin does nothing right now