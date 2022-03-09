# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3
# Art from Kenney.nl
import pygame
import random
import os
import sys

def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store        your data files:
        datadir = os.path.dirname(__file__)

    return datadir

gamedir = find_data_file('GameCode.pyw')

img_dir = os.path.join(gamedir, 'img')
snd_dir = os.path.join(gamedir, 'snd')


WIDTH = 500 # ширина игрового окна
HEIGHT = 540 # высота игрового окна
FPS = 60 # частота кадров в секунду
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

highscore_dir = open('Highscore.txt','r+')
highscore = highscore_dir.read()

difficulty = 1


# создаем игру и окно
pygame.init()
pygame.mixer.init()  # для звука
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroid Destroyer")


# настройка папки ассетов
#game_folder = gamedir


#Загрузка игровой графики
background = pygame.image.load(os.path.join(img_dir, 'starfield2.png')).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(os.path.join(img_dir, "player.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(os.path.join(img_dir, "laserGreen.png")).convert()

meteor_images = []
meteor_list =['meteorSmall.png','meteorSmall1.png','meteorBig.png','meteorBig1.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(os.path.join(img_dir, img)).convert())
meteor_images[2] = pygame.transform.scale(meteor_images[2], (80,80))
meteor_images[1] = pygame.transform.scale(meteor_images[1], (60,60))

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)
powerup_images = {}
powerup_images['shield'] = pygame.image.load(os.path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(os.path.join(img_dir, 'bolt_gold.png')).convert()

# Загрузка звука игры
shoot_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'Laser_Shoot31.wav'))
expl_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(os.path.join(snd_dir, snd)))

#music_dir = find_data_file('music.mp3')
pygame.mixer.music.load(os.path.join(snd_dir, 'music.wav '))
pygame.mixer.music.set_volume(0.4)
shield_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'Powerup15.wav'))
power_sound = pygame.mixer.Sound(os.path.join(snd_dir, 'Powerup12.wav'))

# Создаем игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 40))
        self.image = player_img
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 150
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        # показать, если скрыто
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        # тайм-аут для бонусов
        POWERUP_TIME = 5000
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()


    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if not self.hidden:
                if self.power == 1:
                    bullet = Bullet(self.rect.centerx, self.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                    shoot_sound.play()
                if self.power == 2:
                    bullet1 = Bullet(self.rect.left, self.rect.centery)
                    bullet2 = Bullet(self.rect.right, self.rect.centery)
                    all_sprites.add(bullet1)
                    all_sprites.add(bullet2)
                    bullets.add(bullet1)
                    bullets.add(bullet2)
                    shoot_sound.play()
                if self.power == 3:
                    bullet1 = Bullet(self.rect.left, self.rect.centery)
                    bullet2 = Bullet(self.rect.right, self.rect.centery)
                    bullet3 = Bullet(self.rect.centerx, self.rect.top)
                    all_sprites.add(bullet1)
                    all_sprites.add(bullet2)
                    all_sprites.add(bullet3)
                    bullets.add(bullet1)
                    bullets.add(bullet2)
                    bullets.add(bullet3)
                    shoot_sound.play()
                if self.power >= 4:
                    self.power = 3



    def hide(self):
        # временно скрыть игрока
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        mob_scale = random.randrange(10, 100)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width* .85 / 2)
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -140)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
        self.shield = self.radius

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def newmob():
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -150 or self.rect.right > WIDTH + 150:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-150, -140)
            self.speedy = random.randrange(1, 8)
            self.shield = self.radius





class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 20))
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10
        self.damage = 10

    def update(self):
        self.rect.y += self.speedy
        # убить, если он заходит за верхнюю часть экрана
        if self.rect.bottom < 0:
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
        self.frame_rate = 50

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

class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        # убить, если он сдвинется с нижней части экрана
        if self.rect.top > HEIGHT:
            self.kill()

font_name = pygame.font.match_font('arial')

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, GREEN)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, (0, 255, 255), fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_pow(surf, x, y, pow, img):
    for i in range(pow):
        img_rect = img.get_rect()
        img.set_colorkey(BLACK)
        img_rect.y = y + 30 * i
        img_rect.x = x
        surf.blit(img, img_rect)

def draw_shield(surf, mob):
    if mob.shield < 5:
        mob.shield = 0
    BAR_LENGTH = 50
    BAR_HEIGHT = 5
    fill = (mob.shield / mob.radius) * BAR_LENGTH
    outline_rect = pygame.Rect(mob.rect.x, mob.rect.y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(mob.rect.x, mob.rect.y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, RED, fill_rect)
    pygame.draw.rect(surf, BLACK, outline_rect, 2)

def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "Asteroid Destroyer", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Arrow keys move, Space to fire", 22,
              WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Esc to main menu", 22,
              WIDTH / 2, HEIGHT / 2+25)
    draw_text(screen, "Press a key to begin", 18, WIDTH / 2, HEIGHT * 3 / 4)
    draw_text(screen, "Highscore: %s" %(highscore), 18, WIDTH / 5, HEIGHT / 5)
    draw_text(screen, 'press h to help ', 15, 400,5)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_h:
                    screen.blit(background, background_rect)
                    draw_text(screen, str(score), 25, WIDTH / 2, 10)
                    draw_text(screen, 'your score', 15, WIDTH / 2,30)
                    draw_shield_bar(screen, 5, 5, player.shield)
                    draw_text(screen, 'shield', 15, 50,20)
                    draw_text(screen, 'pickup shields to recover', 15, 77,40)
                    draw_text(screen, 'your shield bar', 15, 50,60)
                    draw_lives(screen, WIDTH - 100, 5, player.lives,player_mini_img)
                    draw_text(screen, 'lives: ', 15, 370,5)
                    draw_pow(screen, WIDTH - 30, 30,player.power ,powerup_images['gun'])
                    draw_text(screen, 'powerups (1 up to 3): ', 15, 400,50)
                    pygame.display.flip()
                else: waiting = False


clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
for i in range(8):
    Mob.newmob()
score = 0
powerups = pygame.sprite.Group()
dscore = 0

#Запуск музыки
pygame.mixer.music.play(loops=-1)


# Цикл игры
game_over = True
running = True
while running:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            Mob.newmob()
        score = 0
    # Ввод процесса (события)
    clock.tick(FPS)
    for event in pygame.event.get():
        # проверить закрытие окна
        if event.type == pygame.QUIT:
            if score > int(highscore): highscore = str(score)
            highscore_dir.seek(0)
            highscore_dir.write(highscore)
            running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                game_over = True
                waiting = True
                if score > int(highscore): highscore = str(score)
                highscore_dir.seek(0)
                highscore_dir.write(highscore)

    # Обновление(
    all_sprites.update()


    # Проверка, не ударил ли моб игрока
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        Mob.newmob()
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100
    # Если игрок умер, игра окончена
    if player.lives == 0 and not death_explosion.alive():
        game_over = True
        if score > int(highscore): highscore = str(score)
        highscore_dir.seek(0)
        highscore_dir.write(highscore)

# Проверка, не столкнулись ли моб и пуля
    for mob in mobs:
        hits = pygame.sprite.spritecollide(mob, bullets, True, pygame.sprite.collide_circle)
        for hit in hits:
            mob.shield -= 18
        if mob.shield <=0:
            score += 60 - mob.radius
            dscore += 60 - mob.radius
            mob.kill()
            random.choice(expl_sounds).play()
            expl = Explosion(hit.rect.center, 'lg')
            all_sprites.add(expl)
            if random.random() > 0.92:
                pow = Pow(mob.rect.center)
                all_sprites.add(pow)
                powerups.add(pow)
            Mob.newmob()


    # Проверка столкновений игрока и улучшения
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            shield_sound.play()
            player.shield += random.randrange(10, 30)
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'gun':
            power_sound.play()
            player.powerup()
    if dscore >= 1000:
        dscore = 0
        Mob.newmob()
    # Рендеринг
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 25, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives,player_mini_img)
    draw_pow(screen, WIDTH - 30, 30,player.power ,powerup_images['gun'])
    for mob in mobs:
        if mob.shield < mob.radius:
            draw_shield(screen,mob)
    # после отрисовки всего, переворачиваем экран
    pygame.display.flip()


highscore_dir.close()
pygame.quit()
