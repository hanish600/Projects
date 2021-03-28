# Sprite classes for platform game
import pygame as pg
import random
import time

# game options/settings
TITLE = "StarBird"
WIDTH = 640
HEIGHT = 800
FPS = 60
FONT_NAME = 'arial'
pic=pg.display.set_icon(pg.image.load("bird.png"))


# Player properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.8
PLAYER_JUMP = 10

# Starting platforms
PLATFORM_LIST = [(0, HEIGHT - 40, WIDTH, 40),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4, 100, 20),
                 (125, HEIGHT - 350, 100, 20),
                 (350, 200, 100, 20),
                 (175, 100, 50, 20)]

# define colors
WHITE = (255, 255, 255)
LIGHTBLUE = (0, 155, 155)
PURPLE=(102,0,204)

vec = pg.math.Vector2

class Player(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        picture=pg.image.load('bird.png')
        angle=0
        scale=.2
        self.image = pg.transform.rotozoom(picture,angle,scale)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def jump(self):
        self.vel.y = -PLAYER_JUMP

    def update(self):
        self.acc = vec(0, PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC
        if keys[pg.K_SPACE]:
            self.jump()

        # apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        # wrap around the sides of the screen
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

class Platform(pg.sprite.Sprite): #stars
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        picture = pg.image.load('star.png')
        angle=0
        scale=.04
        self.image = pg.transform.rotozoom(picture,angle,scale)
        #self.image.fill(LIGHTBLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Game:
    def __init__(self):
        # initialize game window, etc
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        pg.mixer.music.load('music1.ogg')
        pg.mixer.music.play()
        pg.mixer.music.set_volume(.05)
        self.start_time = time.time()
        self.best_score = 0

    def new(self):
        # start a new game
        self.start_time = time.time()
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        for plat in PLATFORM_LIST:
            p = Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
            

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()
        # check if player hits a platform - only if falling
        if self.player.vel.y < 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, True)
            if hits:
                self.score += 1
            if self.best_score < self.score:
                self.best_score = self.score

        # if player reaches top 1/4 of screen
        if self.player.rect.top <= HEIGHT / 4:
            self.player.pos.y += abs(self.player.vel.y)
            for plat in self.platforms:
                plat.rect.y += abs(self.player.vel.y)
                if plat.rect.top >= HEIGHT:
                    plat.kill()

        # Die!
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0 or (60 - (time.time() - self.start_time)) <= 0:
            self.playing = False

        # spawn new platforms to keep same average number
        while len(self.platforms) < 8:
            width = random.randrange(10, 40)
            p = Platform(random.randrange(0, WIDTH - width),
                         random.randrange(-75, -30),
                         width, 20)
            self.platforms.add(p)
            self.all_sprites.add(p)

    def events(self):
        # Game Loop - events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def draw(self):
        # Game Loop - draw
        self.screen.fill((10, 120, 150))
        self.all_sprites.draw(self.screen)
        self.draw_text("Score:" + str(self.score), 22, WHITE, WIDTH / 2, 15)
        self.draw_text("Timer:" + str(60 - int(time.time() - self.start_time)), 22, WHITE, 50, 15)
        self.draw_text("Best:" + str(self.best_score), 22, WHITE, 580, 15)
        # *after* drawing everything, flip the display
        pg.display.flip()

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

pg.mouse.set_cursor(*pg.cursors.diamond)
g = Game()
while g.running:
    g.new()

pg.quit()
