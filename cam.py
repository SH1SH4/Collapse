import pygame
import os
import sys
import pytmx
import pyscroll
from pytmx.util_pygame import load_pygame

pygame.init()

pygame.display.set_caption("Start")
size = width, height = 1920, 1020
screen = pygame.display.set_mode(size)

color = "white"

tmx_data = load_pygame("maps/poligon2.0.tmx")
map_data = pyscroll.TiledMapData(tmx_data)
screen_size = (1920, 1020)
map_layer = pyscroll.BufferedRenderer(map_data, screen_size, True)
group = pyscroll.PyscrollGroup(map_layer=map_layer)
obstacles = pygame.sprite.Group()
hero = pygame.sprite.Group()
heart = pygame.sprite.Group()
run = pygame.mixer.Sound('sound/шаги.wav')
sound_theme = pygame.mixer.Sound('sound/Alan Walker - Spectre.wav')
main_menu_theme = pygame.mixer.Sound('sound/Игорь Корнелюк - Воланд.wav')

class Map:
    def __init__(self, filename, free_tile):
        self.map = pytmx.load_pygame(f"maps/{filename}")
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.free_tile = free_tile

    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] not in self.free_tile:
                    Obstacles(self.map.get_tile_image(x, y, 0), x * self.tile_size, y * self.tile_size)

    def get_tile_id(self, position):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, 0)]

    def is_free(self, position):
        return self.get_tile_id(position) not in self.free_tile


class Obstacles(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__(obstacles)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        # self.add(obstacles)
        self.mask = pygame.mask.from_surface(self.image)


class Button:
    def __init__(self, width, height, inactive=None, active=None):
        self.width = width
        self.height = height
        self.inactive = pygame.image.load(inactive)
        self.active = pygame.image.load(active)

    def draw(self, x, y, name, action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            screen.blit(self.active, (x, y))
            if click[0] == 1:
                screen.blit(self.active, (x, y))
                if name == "play":
                    start_game()
                    print("Ok")
                if name == "new_game":
                    print("New game")
                if name == "exit":
                    pygame.quit()
                    quit()
        else:
            screen.blit(self.inactive, (x, y))


class Hero(pygame.sprite.Sprite):
    def __init__(self, position, sheet, columns, rows, x, y):
        pygame.sprite.Sprite.__init__(self, group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect.x, self.rect.y = position
        self.delay = 0
        self.hp_health = 10
        self.add(hero)
        self.hp_hero(self.hp_health)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def animation(self):
        if self.delay % 5 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        self.delay += 1

    def update(self, world, delta_time):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] or key[pygame.K_RIGHT] or key[pygame.K_UP] or key[pygame.K_DOWN]:
            run.play()
            if key[pygame.K_LEFT]:
                self.hp_health -= 1
                self.hp_hero(self.hp_health)
                self.rect.x -= 5
                self.animation()
                if pygame.sprite.spritecollideany(self, obstacles):
                    self.rect.x += 5
            if key[pygame.K_RIGHT]:
                self.rect.x += 5
                self.animation()
                if pygame.sprite.spritecollideany(self, obstacles):
                    self.rect.x -= 5
            if key[pygame.K_UP]:
                self.rect.y -= 5
                self.animation()
                if pygame.sprite.spritecollideany(self, obstacles):
                    self.rect.y += 5
            if key[pygame.K_DOWN]:
                self.rect.y += 5
                self.animation()
                if pygame.sprite.spritecollideany(self, obstacles):
                    self.rect.y -= 5
        else:
            run.stop()

    def hp_hero(self, health):
        self.remove(heart)
        for i in range(1, health + 1):
            hp = HP((pygame.transform.scale(load_image('heart.png'), (30, 30))), i)


class HP(pygame.sprite.Sprite):
    def __init__(self, sheet, health):
        print(health)
        super().__init__(heart)
        self.image = sheet
        self.rect = self.image.get_rect()
        self.rect.x = 10 * (health * 3.5)
        self.rect.y = 30


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def play_but():
    play = Button(400, 100, "data/play_inactive.png", "data/play_active.png")
    play.draw(760, 400, "play")


def newgame_but():
    new_game = Button(400, 100, "data/test_inacrive.png", "data/test_acrive_black.png")
    new_game.draw(760, 550, "new_game")


def exit_but():
    exit_b = Button(400, 100, "data/exit_inacrive.png", "data/exit_acrive.png")
    exit_b.draw(760, 700, "exit")


def start_screen():
    menu_background = pygame.image.load("data/background.png")
    screen.blit(menu_background, (0, 0))
    clock = pygame.time.Clock()
    run = True
    while run:
        for event in pygame.event.get():
            play_but()
            newgame_but()
            exit_but()
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        pygame.display.update()


def start_game():
    running = True
    screen.fill((0, 0, 0))
    world = Map("poligon2.0.tmx", [30, 15])
    hero = Hero((50, 50), load_image("llama (1).png"), 3, 2, 50, 50)
    main_menu_theme.stop()
    sound_theme.set_volume(0.3)
    sound_theme.play(-1)
    # game = Game(world, hero)
    world.render()
    clock = pygame.time.Clock()
    fps = 60
    clock = pygame.time.Clock()
    while running:
        delta_time = clock.tick(fps) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        obstacles.update()
        group.update(world, delta_time)
        group.center(hero.rect.center)
        group.draw(screen)
        heart.draw(screen)
        pygame.display.flip()

    pygame.quit()

main_menu_theme.play()
start_screen()