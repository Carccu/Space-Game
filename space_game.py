# Tech With Tim --> https://www.youtube.com/watch?v=jO6qQDNa2UY
# KidsCanCode --> https://www.youtube.com/watch?v=nGufy7weyGY
import pygame
import os, sys
pygame.init()
pygame.mixer.init()
pygame.font.init()

img_dir = os.path.join(os.path.dirname(__file__), 'Img')
sound_dir = os.path.join(os.path.dirname(__file__), 'Sound')
# Game window settings
WIN_WIDTH, WIN_HEIGHT = 1366, 768
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption('SPACE')
BORDER = pygame.Rect(WIN_WIDTH / 2 - 5, 0, 10, WIN_HEIGHT) # Draw the border in the middle of game screen
HEALTH_FONT = pygame.font.match_font('comicsans')

# Game settings
clock = pygame.time.Clock()
FPS = 60 # Setting the frame rate

# Colors
RED = (255, 0, 0)
BLACK = (0, 0, 0)
PURPLE = (90, 2, 90)
LIGHT_PURPLE = (196, 170, 214)
WHITE = (255, 255, 255)
GREEN = (101, 128, 79)
ORANGE = (187, 108, 46)

# Load game graphics
BG = pygame.image.load(os.path.join(img_dir, 'SpaceBackGround.jpg')).convert()
BG_RECT = BG.get_rect()
PL1 = pygame.image.load(os.path.join(img_dir, 'enemyGreen1.png')).convert() # Image for Player 1
PL1_LIFE_IMG = pygame.transform.rotate(pygame.transform.scale(PL1, (33, 22)), 180)
PL1_LIFE_IMG.set_colorkey(BLACK)
PL2 = pygame.image.load(os.path.join(img_dir, 'enemyRed1.png')).convert() # Image for Player 2
PL2_LIFE_IMG = pygame.transform.rotate(pygame.transform.scale(PL2, (33, 22)), 180)
PL2_LIFE_IMG.set_colorkey(BLACK)
PL1_BULLET = pygame.image.load(os.path.join(img_dir, 'laserBlue07.png')).convert() # Player 1 bullet image
PL2_BULLET = pygame.image.load(os.path.join(img_dir, 'laserRed07.png')).convert() # Player 2 bullet image
explosion_anim = {}
explosion_anim['small'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_small = pygame.transform.scale(img, (40, 40))
    explosion_anim['small'].append(img_small)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

# Load game sound effects
SHOOT = pygame.mixer.Sound(os.path.join(sound_dir, 'Laser_shoot6.wav'))
SHIP_EXPLODED = pygame.mixer.Sound(os.path.join(sound_dir, 'Expl9.wav'))
HIT_SOUND = pygame.mixer.Sound(os.path.join(sound_dir, 'Hit_hurt10.wav'))
WINNER_SOUND = pygame.mixer.Sound(os.path.join(sound_dir, 'winning-chimes.wav'))

all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()

class Player(pygame.sprite.Sprite):
    def __init__(self, image, rotation, player_pos, x):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.rotate(image, rotation)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 40
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = x # WIN_WIDTH / 2 / 2 - 5
        self.rect.centery = WIN_HEIGHT / 2
        self.vel = 7
        self.health = 100
        self.lives = 3
        self.max_bullets = 5
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.player_pos = player_pos
        

    def update(self):
        # Unhide if hidden
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 2000:
            self.hidden = False
            if self.player_pos == 'left':
                self.rect.right = WIN_WIDTH / 2 / 2 - 5
            if self.player_pos == 'right':
                self.rect.left = WIN_WIDTH / 4 * 3
            self.rect.centery = WIN_HEIGHT / 2

        keys_pressed = pygame.key.get_pressed()
        if self.player_pos == 'left':
            if keys_pressed[pygame.K_w] and self.rect.top - self.vel > 0: # Move up
                self.rect.top -= self.vel
            if keys_pressed[pygame.K_s] and self.rect.bottom + self.vel < WIN_HEIGHT - 5: # Move down
                self.rect.bottom += self.vel 
            if keys_pressed[pygame.K_a] and self.rect.left - self.vel > 0: # Move left
                self.rect.left -= self.vel
            if keys_pressed[pygame.K_d] and self.rect.right + self.vel < WIN_WIDTH / 2 - 5: # Move right
                self.rect.right += self.vel
            if keys_pressed[pygame.K_RALT]:
                self.shoot()

        if self.player_pos == 'right':
            if keys_pressed[pygame.K_UP] and self.rect.top - self.vel > 0: # Move up
                self.rect.top -= self.vel
            if keys_pressed[pygame.K_DOWN] and self.rect.bottom + self.vel < WIN_HEIGHT - 5: # Move down
                self.rect.bottom += self.vel 
            if keys_pressed[pygame.K_LEFT] and self.rect.left - self.vel > WIN_WIDTH / 2 + 5: # Move left
                self.rect.left -= self.vel
            if keys_pressed[pygame.K_RIGHT] and self.rect.right + self.vel < WIN_WIDTH: # Move right
                self.rect.right += self.vel
            if keys_pressed[pygame.K_RCTRL]:
                self.shoot()
    
    def hide(self):
        # Hide the player temporarily
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIN_WIDTH / 2, WIN_HEIGHT + 200)

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if len(bullets) < self.max_bullets:
                if self.player_pos == 'left':
                    bullet = Bullet(PL1_BULLET, 90, 'left', self.rect.centerx + 70, self.rect.centery)
                if self.player_pos == 'right':
                    bullet = Bullet(PL2_BULLET, 270, 'right', self.rect.centerx - 70, self.rect.centery)
                all_sprites.add(bullet)
                bullets.add(bullet)
                SHOOT.play()

# class Player2(pygame.sprite.Sprite):
#     def __init__(self):
#         pygame.sprite.Sprite.__init__(self)
#         self.image = pygame.transform.rotate(PL2, 270)
#         self.image.set_colorkey(BLACK)
#         self.rect = self.image.get_rect()
#         self.radius = 40
#         # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
#         self.rect.centerx = WIN_WIDTH / 4 * 3
#         self.rect.centery = WIN_HEIGHT / 2
#         self.vel = 7
#         self.health = 100
#         self.lives = 3
#         self.max_bullets = 5
#         self.shoot_delay = 250
#         self.last_shot = pygame.time.get_ticks()
#         self.hidden = False
#         self.hide_timer = pygame.time.get_ticks()

#     def update(self):
#         # Unhide if hidden
#         if self.hidden and pygame.time.get_ticks() - self.hide_timer > 2000:
#             self.hidden = False
#             self.rect.left = WIN_WIDTH / 4 * 3
#             self.rect.centery = WIN_HEIGHT / 2

#         keys_pressed = pygame.key.get_pressed()
#         if keys_pressed[pygame.K_UP] and self.rect.top - self.vel > 0: # Move up
#             self.rect.top -= self.vel
#         if keys_pressed[pygame.K_DOWN] and self.rect.bottom + self.vel < WIN_HEIGHT - 5: # Move down
#             self.rect.bottom += self.vel 
#         if keys_pressed[pygame.K_LEFT] and self.rect.left - self.vel > WIN_WIDTH / 2 + 5: # Move left
#             self.rect.left -= self.vel
#         if keys_pressed[pygame.K_RIGHT] and self.rect.right + self.vel < WIN_WIDTH: # Move right
#             self.rect.right += self.vel
#         if keys_pressed[pygame.K_RCTRL]:
#             self.shoot()

#     def shoot(self):
#         now = pygame.time.get_ticks()
#         if now - self.last_shot > self.shoot_delay:
#             self.last_shot = now
#             if len(bullets) < self.max_bullets:
#                 bullet = Bullet(PL2_BULLET, 270, 'right', self.rect.centerx - 70, self.rect.centery)
#                 all_sprites.add(bullet)
#                 bullets.add(bullet)
#                 SHOOT.play()

#     def hide(self):
#         # Hide the player temporarily
#         self.hidden = True
#         self.hide_timer = pygame.time.get_ticks()
#         self.rect.center = (WIN_WIDTH + 200, WIN_HEIGHT / 2)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, rotation, player_pos, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.rotate(image, rotation)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.centerx = x
        self.rect.centery = y
        self.vel = 9
        self.player_pos = player_pos

    def update(self):
        if self.player_pos == 'left':
            self.rect.x += self.vel
            if self.rect.centerx > WIN_WIDTH:
                self.kill()
        if self.player_pos == 'right':
            self.rect.x -= self.vel
            if self.rect.centerx < 0:
                self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center
        

def draw_health(surf, x, y, fill_color, outline_color, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, fill_color, fill_rect)
    pygame.draw.rect(surf, outline_color, outline_rect, 2)

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(HEALTH_FONT, size)
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect()
    text_rect.midtop = (x, y)
    # text_rect.y = y
    surf.blit(text_surf, text_rect)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 40 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def game_over_screen():
    WIN.blit(BG, BG_RECT)
    draw_text(WIN, "SPACE WAR!", 80, WIN_WIDTH / 2, WIN_HEIGHT / 4)
    draw_text(WIN, "PLAYER 1: Use A, S, D, W to move, RIGHT ALT to shoot", 40, WIN_WIDTH / 2, WIN_HEIGHT / 2)
    draw_text(WIN, "PLAYER 2: Use ARROW keys to move, RIGHT CTRL to shoot", 40, WIN_WIDTH / 2, WIN_HEIGHT / 2 + 60)
    draw_text(WIN, "              ", 40, WIN_WIDTH / 2, WIN_HEIGHT / 2)
    draw_text(WIN, "Press any key to start!", 35, WIN_WIDTH / 2, WIN_HEIGHT - 40)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                waiting = False

def winner_text(winner):
    WIN.blit(BG, BG_RECT)
    draw_text(WIN, winner, 120, WIN_WIDTH / 2, WIN_HEIGHT / 4)
    pygame.display.update()
    WINNER_SOUND.play()
    pygame.time.delay(3000)

def main():
    game_over = True
    run = True    

    while run:
        if game_over:
            game_over_screen()
            game_over = False
            player1 = Player(PL1, 90, 'left', WIN_WIDTH / 2 / 2 - 5)
            player2 = Player(PL2, 270, 'right', WIN_WIDTH / 4 * 3)
            all_sprites.add(player1)
            all_sprites.add(player2)

        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        all_sprites.update()

        # Check if the player 1 bullets hit the player 2
        hits = pygame.sprite.spritecollide(player2, bullets, True)
        for hit in hits:
            HIT_SOUND.play()
            player2.health -= hit.radius * 1.4
            explosion = Explosion(hit.rect.center, 'small')
            all_sprites.add(explosion)
            if player2.health <= 0:
                SHIP_EXPLODED.play()
                death_expl2 = Explosion(player2.rect.center, 'player')
                all_sprites.add(death_expl2)
                player2.hide()
                player2.lives -= 1
                player2.health = 100
                
        # Check if the player 2 bullets hit the player 1
        hits = pygame.sprite.spritecollide(player1, bullets, True)
        for hit in hits:
            HIT_SOUND.play()
            player1.health -= hit.radius * 1.4
            explosion = Explosion(hit.rect.center, 'small')
            all_sprites.add(explosion)
            if player1.health <= 0:
                SHIP_EXPLODED.play()
                death_expl1 = Explosion(player1.rect.center, 'player')
                all_sprites.add(death_expl1)
                player1.hide()
                player1.lives -= 1
                player1.health = 100

        # If the player died and the explosion has finished playing
        if player1.lives == 0 and not death_expl1.alive():
            winner_text('PLAYER 2 WINS!')
            player1.lives = 3
            game_over_screen()
        if player2.lives == 0 and not death_expl2.alive():
            winner_text('PLAYER 1 WINS!')
            player2.lives = 3
            game_over_screen()
        

        WIN.fill(BLACK)
        WIN.blit(BG, BG_RECT)
        all_sprites.draw(WIN)
        pygame.draw.rect(WIN, WHITE, BORDER)
        draw_text(WIN, 'PLAYER 1', 40, WIN_WIDTH / 4, 20)
        draw_text(WIN, 'PLAYER 2', 40, WIN_WIDTH - (WIN_WIDTH / 4), 20)
        draw_lives(WIN, WIN_WIDTH / 2 - 125, 10, player1.lives, PL1_LIFE_IMG) # Player 1
        draw_health(WIN, WIN_WIDTH / 2 - 120, 40, GREEN, WHITE, player1.health)
        draw_lives(WIN, WIN_WIDTH - 120, 10, player2.lives, PL2_LIFE_IMG) # Player 2
        draw_health(WIN, WIN_WIDTH - 115, 40, ORANGE, WHITE, player2.health)
        
        
        pygame.display.update()

    pygame.quit()

    
if __name__ == '__main__':
    main()
