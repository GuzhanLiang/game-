
from CoffeeAndCodingHelper import *

'''
Lesson 1: Constants
I'll use these constants to teach the students about the basics of constants
may rename them to be more clear
'''


#The speed of the character
VEL = 5

#The speed of the character's lazer
LAZER_VEL = 7

#Damage of the lazer
LAZER_DAMAGE =  1

#Damage of special lazer
SPECIAL_LAZER_DAMAGE =  3

#The max amount of lazers a character can shoot
MAX_SPECIAL_AMMO =  10

#The max amount of lazers an enemy can shoot
MAX_ENEMY_LAZER =  2

#The max health of the player
MAX_HEALTH =  25

#The maximum health of the shield (damage done)
MAX_SHIELD_HEALTH =  10

#The maximum items in the players inventory
MAX_INVENTORY =  5

#The maximum number 
MAX_ONSCREEN_POWERUPS =  3

#the amount of points gotten for defeating an enemy
POINTS_FOR_DEFEAT =  10

#The top score the player needs to get to win 
MAX_SCORE =  1000

#The maximum number of enemies 
MAX_ENEMIES =  5

#The enemy's speed
ENEMY_SPEED =  1

#The enemy's max health
ENEMY_MAX_HEALTH =  3

#The number of enemies allowed to pass player
MAX_ENEMY_ENTRY =  5

class Player(pygame.sprite.Sprite):
    #This function moves the health bar. more about pygame than basic coding will stay collapsed

    #This function has to do with the initialization of a player object too advanced will stay collapsed
    def __init__(self):
        super(Player, self).__init__()
        self.surface = PLAYER_SPACESHIP.convert()
        self.surface.set_colorkey(BLACK,RLEACCEL)
        self.rect = self.surface.get_rect(
            center = (
                100,300
            )
        )
        self.health = MAX_HEALTH
        self.maxHealth = MAX_HEALTH
        self.shieldHealth = MAX_SHIELD_HEALTH
        self.maxShieldHealth = MAX_SHIELD_HEALTH
        self.lazers = []
        self.inventory = []
        self.specialAmmo = 0
        self.maxSpecialAmmo = MAX_SPECIAL_AMMO
    
    '''
    Lesson 2: conditionals
    will use movement to eplain if/else
    '''
    def move(self, keys_pressed):
        if keys_pressed[pygame.K_a] and self.rect.x - VEL > 0:  # LEFT
            self.rect.x -= VEL
        if keys_pressed[pygame.K_d] and self.rect.x + VEL + self.rect.width < WIDTH + self.rect.width/2:  # RIGHT
            self.rect.x += VEL
        if keys_pressed[pygame.K_w] and self.rect.y - VEL > 0:  # UP
            self.rect.y -= VEL
        if keys_pressed[pygame.K_s] and self.rect.y + VEL + self.rect.height < HEIGHT - 15:  # DOWN
            self.rect.y += VEL


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surface = ENEMY_SPACESHIP.convert()
        self.surface.set_colorkey(BLACK,RLEACCEL)
        self.rect = self.surface.get_rect(
            center = (
                (WIDTH - SPACESHIP_WIDTH, HEIGHT - (SPACESHIP_HEIGHT*(random.randint(1,10))))
            )
        )
        self.speed = ENEMY_SPEED
        self.health = ENEMY_MAX_HEALTH
        self.lazers = []
    
    def update(self):
        self.rect.move_ip(-self.speed,0)
        if self.rect.right < 0:
            self.kill()
            postEvent(ENEMY_ENTRY)

def use_item(key,player):
    inv_key = int(pygame.key.name(key)) -1
    if inv_key < len(player.inventory) and len(player.inventory) > 0:
        (player.inventory[inv_key]).use(player)
        del player.inventory[inv_key]

'''
lesson 4
'''

def move_enemy_lazers(ammo, player):
    for lazer in ammo:
        lazer.x -= LAZER_VEL
        if player.rect.colliderect(lazer):
            if player.shieldHealth > 0:
                player.shieldHealth -= LAZER_DAMAGE
            else:
                player.health -= LAZER_DAMAGE
            ammo.remove(lazer)
        elif lazer.x < 0:
            ammo.remove(lazer)
            
def move_lazers(ammo, enemies, player):
    for lazer in ammo:
        lazer.x += LAZER_VEL
        for enemy in enemies:
            if enemy.rect.colliderect(lazer):
                if player.specialAmmo > 0:
                    enemy.health -= SPECIAL_LAZER_DAMAGE
                else:
                    enemy.health -= LAZER_DAMAGE
                ammo.remove(lazer)
                if enemy.health == 0:
                    enemy.kill()
                    postEvent(ENEMY_DEFEAT)
        if lazer.x > WIDTH:
            ammo.remove(lazer)

def draw_inventory_items(inventory):
    for i in range(len(inventory)):
        draw_inventory_item(i, inventory[i].sprite)



def draw_window(keys_pressed, player,enemies,powerUps, entered, defeated, score):
    draw_background()
    draw_healthBar(player)
    draw_shieldBar(player)
    draw_special_ammo(player)
    draw_entered(entered,MAX_ENEMY_ENTRY)
    draw_number_of_defeated(defeated)
    draw_score(score)
    draw_inventory()
    draw_inventory_items(player.inventory)
    draw_entity(player)
    player.move(keys_pressed)
    
    enemies.update()
    move_lazers(player.lazers, enemies, player)
    for power in powerUps:
        if pygame.sprite.collide_rect(player,power):
            playSound(ITEM_PICK_UP_SOUND)

    powerUps_gotten = collect_gotten_items(player,powerUps)
    
    for power in powerUps_gotten:
        if len(player.inventory) < MAX_INVENTORY:
            player.inventory.append(power)
        else:
            power.kill()

    for entity in all_sprites:
        draw_entity(entity)
        if type(entity) == Enemy:
            if len(entity.lazers) <= MAX_ENEMY_LAZER:
                enemy_lazer = make_lazer(entity)
                entity.lazers.append(enemy_lazer)
            move_enemy_lazers(entity.lazers, player)
            for lazer in entity.lazers:
                draw_enemy_lazer(lazer)
    
    

    for lazer in player.lazers:
        if player.specialAmmo > 0:
            draw_special_lazer(lazer)
        else:
            draw_player_lazer(lazer)
    pygame.display.update()

def main():
    pygame.mixer.music.play()
    entered = 0
    score = 0
    defeated = 0
    player = Player()
    enemies = pygame.sprite.Group()
    powerUps = pygame.sprite.Group()
    all_sprites.add(player)
    clock = pygame.time.Clock()

    run = True
    while run:
        
        clock.tick(FPS)

        if player.health <= 0 or entered == MAX_ENEMY_ENTRY:
            playSound(GAME_OVER_SOUND)
            message = "Game Over!"
            draw_message(message)
            all_sprites.empty()
            run = False

        if score >= MAX_SCORE:
            playSound(WINNER_SOUND)
            message = "WINNER!"
            draw_message(message)
            all_sprites.empty()
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: #and len(player.lazers) < MAX_LAZERS:
                    if player.specialAmmo > 0:
                        player.specialAmmo -= 1
                        lazer = make_special_lazer(player)
                        playSound(LAZER_POWER_UP_SOUND)
                    else:
                        lazer = make_lazer(player)
                        playSound(LAZER_SOUND)
                    player.lazers.append(lazer)
                    

                elif event.key in INVENTORY_KEYS :
                    use_item(event.key, player)
    
            if event.type == ENEMY_SPAWNS and len(enemies) < MAX_ENEMIES:
                enemy = Enemy()
                enemies.add(enemy)
                all_sprites.add(enemy)

            if event.type == SHIELD_SPAWNS and len(powerUps) < MAX_ONSCREEN_POWERUPS:
                shield = ShieldPowerUp()
                powerUps.add(shield)
                all_sprites.add(shield)
            
            if event.type == STAR_SPAWNS and len(powerUps)  < MAX_ONSCREEN_POWERUPS:
                star = StarPowerUp()
                powerUps.add(star)
                all_sprites.add(star)

            if event.type == BATTRY_SPAWNS and len(powerUps)  < MAX_ONSCREEN_POWERUPS:
                battery = BatteryPowerUp()
                powerUps.add(battery)
                all_sprites.add(battery)

            if event.type == ENEMY_ENTRY:
                playSound(ENTRY_SOUND)
                entered += 1

            if event.type == ENEMY_DEFEAT:
                playSound(EXPLOSION_SOUND)
                defeated += 1
                score += POINTS_FOR_DEFEAT
                
        

        keys_pressed = pygame.key.get_pressed()
        
        draw_window(keys_pressed, player,enemies,powerUps,entered, defeated, score)
    main()


if __name__ == "__main__":
    main()

