#----------------------------------------imports---------------------------------------------------#
from asyncio import shield
from multiprocessing.connection import wait
from select import select
from time import sleep
from tkinter import CENTER
import pygame
import os
import random
from pygame.locals import (
    RLEACCEL
)

pygame.font.init()
pygame.mixer.init()

#------------------------------------------Constants------------------------------------------------------#
#various constants
WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Coffee & Coding Space Arcade Game")
FPS = 60
WHITE = (255, 255, 255)
GREY = (211,211,211)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0,255,0)
BLUE = (0,0,255)
WINNER_FONT = pygame.font.SysFont('8-Bit-Madness', 100)

#the keys allowed for inventory (1-5)
INVENTORY_KEYS = [pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_5]

#events that occur in the game
ENEMY_SPAWNS = pygame.USEREVENT + 1
ENEMY_HIT = pygame.USEREVENT + 2
ENEMY_ENTRY = pygame.USEREVENT + 3
ENEMY_DEFEAT = pygame.USEREVENT + 4
SHIELD_SPAWNS = pygame.USEREVENT + 5
STAR_SPAWNS = pygame.USEREVENT + 6
BATTRY_SPAWNS = pygame.USEREVENT + 7


#using random and pygame timer to make the entities spawn at random
pygame.time.set_timer(ENEMY_SPAWNS, (random.randint(1,5)*1000))
pygame.time.set_timer(SHIELD_SPAWNS, (random.randint(1,10)*4000))
pygame.time.set_timer(STAR_SPAWNS, (random.randint(1,15)*3000))
pygame.time.set_timer(BATTRY_SPAWNS, (random.randint(1,20)*3000))

#various constants for the sprite images
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40



PLAYER_SPACESHIP_IMAGE = pygame.image.load(
    os.path.join('Assets', 'spaceship_green.png'))
PLAYER_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(
    PLAYER_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)

ENEMY_SPACESHIP_IMAGE = pygame.image.load(
    os.path.join('Assets', 'spaceship_red.png'))
ENEMY_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(
    ENEMY_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)

BATTERY_IMAGE = pygame.image.load(
    os.path.join('Assets', 'battery.png'))
BATTERY = pygame.transform.scale(
    BATTERY_IMAGE, (SPACESHIP_WIDTH//2, SPACESHIP_HEIGHT))

SHIELD_IMAGE = pygame.image.load(
    os.path.join('Assets', 'shield.png'))
SHIELD = pygame.transform.scale(
    SHIELD_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))

STAR_IMAGE = pygame.image.load(
    os.path.join('Assets','star.png'))
STAR = pygame.transform.scale(
    STAR_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT))



SPACE = pygame.transform.scale(pygame.image.load(
    os.path.join('Assets', 'space.png')), (WIDTH, HEIGHT))

#sounds
pygame.mixer.music.load(
    os.path.join('Assets', 'bgm.wav'))

GAME_OVER_SOUND = pygame.mixer.Sound(
    os.path.join('Assets', 'GameOver.wav'))

WINNER_SOUND = pygame.mixer.Sound(
    os.path.join('Assets', 'winner.wav'))

LAZER_SOUND = pygame.mixer.Sound(
    os.path.join('Assets', 'lazer.mp3'))

EXPLOSION_SOUND = pygame.mixer.Sound(
    os.path.join('Assets', 'explosion.mp3'))

ENTRY_SOUND = pygame.mixer.Sound(
    os.path.join('Assets', 'entry.wav'))

ITEM_PICK_UP_SOUND = pygame.mixer.Sound(
    os.path.join('Assets', 'pickUpItem.wav'))

HEAL_SOUND = pygame.mixer.Sound(
    os.path.join('Assets', 'Heal.wav'))

SHIELD_SOUND = pygame.mixer.Sound(
    os.path.join('Assets', 'shieldOn.wav'))

LAZER_POWER_UP_SOUND = pygame.mixer.Sound(
    os.path.join('Assets', 'lazerPowerUp.wav'))


#making the various power up objects
class ShieldPowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super(ShieldPowerUp, self).__init__()
        #adds shield sprite
        self.sprite = SHIELD
        self.surface = SHIELD.convert()
        #take away background
        self.surface.set_colorkey(BLACK,RLEACCEL)
        #randomly generates where the power up spawns within the range of the window
        self.rect = self.surface.get_rect(
            center = (
                ( random.randint(0, WIDTH), random.randint(100,HEIGHT - SPACESHIP_HEIGHT - 30))
            )
        )
    #use fills up player's shield health when used
    def use(self, player):
        playSound(SHIELD_SOUND)
        player.shieldHealth = player.maxShieldHealth


class BatteryPowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super(BatteryPowerUp, self).__init__()
        #adds battery sprite
        self.sprite = BATTERY
        self.surface = BATTERY.convert()
        #take away background
        self.surface.set_colorkey(BLACK,RLEACCEL)
        #randomly generates where the power up spawns within the range of the window
        self.rect = self.surface.get_rect(
            center = (
                ( random.randint(0, WIDTH), random.randint(100,HEIGHT - SPACESHIP_HEIGHT - 30))
            )
        )
    #use function fills up player's health when used
    def use(self, player):
        playSound(HEAL_SOUND)
        player.health = player.maxHealth

class StarPowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super(StarPowerUp, self).__init__()
        #adds star sprite
        self.sprite = STAR
        self.surface = STAR.convert()
        #take away background
        self.surface.set_colorkey(BLACK,RLEACCEL)
        #randomly generates where the power up spwans within the range of the window
        self.rect = self.surface.get_rect(
            center = (
                ( random.randint(0, WIDTH), random.randint(100,HEIGHT - SPACESHIP_HEIGHT - 30))
            )
        )

    #use function fills uup player's special ammo
    def use(self,player):
        playSound(LAZER_POWER_UP_SOUND)
        player.specialAmmo = player.maxSpecialAmmo

#these functions shorten other functions so they're more readable and are easier to use
#----------------------------------------------various make functions---------------------------------------
#makes event
def postEvent(event):
    pygame.event.post(pygame.event.Event(event))

#collects collided sprites to a group
def collect_gotten_items(player, items):
    return pygame.sprite.spritecollide(player,items,True)

#makes a lazer
def make_lazer(entity):
    return pygame.Rect(entity.rect.x + entity.rect.width, entity.rect.y + entity.rect.height//2 - 2, 10, 5)

#makes a special lazer
def make_special_lazer(entity):
    return pygame.Rect(entity.rect.x + entity.rect.width, entity.rect.y + entity.rect.height//2 - 2, 20, 5)

#----------------------------------------------------Various Display functions--------------------------------------------#
#draws the lazer
def draw_player_lazer(lazer):
    pygame.draw.rect(WIN, GREEN, lazer)

#draws the special lazer
def draw_special_lazer(lazer):
    pygame.draw.rect(WIN, BLUE, lazer)

#draws an enemy lazer
def draw_enemy_lazer(lazer):
    pygame.draw.rect(WIN, RED, lazer)


def draw_background():
    WIN.blit(SPACE, (0, 0))

def draw_healthBar(player):
    smallText = pygame.font.SysFont('8-Bit-Madness',35)
    subSurf = text_objects("Health", smallText, WHITE)
    WIN.blit(subSurf,(10,10))
    pygame.draw.rect(WIN,RED,(100,17,150,10))
    pygame.draw.rect(WIN,GREEN,(100,17,150-(6*(25-player.health)),10))

def draw_shieldBar(player):
    smallText = pygame.font.SysFont('8-Bit-Madness',35)
    subSurf = text_objects("Shield", smallText, WHITE)
    WIN.blit(subSurf,(10,35))
    pygame.draw.rect(WIN,RED,(100,40,100,10))
    pygame.draw.rect(WIN,GREY,(100,40,100-(10*(10-player.shieldHealth)),10))

def draw_special_ammo(player):
    smallText = pygame.font.SysFont('8-Bit-Madness',35)
    subSurf = text_objects("Special Ammo:", smallText, WHITE)
    WIN.blit(subSurf,(10,60))
    timer = text_objects( str(player.specialAmmo),smallText,WHITE)
    WIN.blit(timer, (200,60))

def draw_entered(entered, max):
    smallText = pygame.font.SysFont('8-Bit-Madness',35)
    subSurf = text_objects("Enemies Entered: " + str(entered) +"/" + str(max), smallText, (255,255,255))
    WIN.blit(subSurf,(625,10))

def draw_number_of_defeated(defeated):
    smallText = pygame.font.SysFont('8-Bit-Madness',35)
    subSurf = text_objects("Enemies Defeated: " + str(defeated), smallText, (255,255,255))
    WIN.blit(subSurf,(625,40))


def draw_score(score):
    smallText = pygame.font.SysFont('8-Bit-Madness',50)
    subSurf = text_objects("Score: " + str(score), smallText, (255,255,255))
    WIN.blit(subSurf,(350,10))


def text_objects(text, font, color):
    textSurface = font.render(text,True, color)
    return textSurface

def draw_message(text):
    draw_text = WINNER_FONT.render(text, 1, WHITE)
    WIN.blit(draw_text, (WIDTH/2 - draw_text.get_width() /
                         2, HEIGHT/2 - draw_text.get_height()/2))
    pygame.display.update()
    pygame.time.delay(1000)

def draw_entity(entity):
    WIN.blit(entity.surface, entity.rect)

def draw_inventory():
    for i in range(5):
        pygame.draw.rect(WIN, GREY, pygame.Rect(270 + (SPACESHIP_WIDTH+10) *i, HEIGHT - SPACESHIP_HEIGHT - 10, SPACESHIP_WIDTH + 10 , SPACESHIP_HEIGHT + 10), 3)
            
def draw_inventory_item(index, item):
    WIN.blit(item,(275 + (SPACESHIP_WIDTH+10) *index, HEIGHT - SPACESHIP_HEIGHT - 5))    

def playSound(sound):
    pygame.mixer.Sound.play(sound)



all_sprites = pygame.sprite.Group()
