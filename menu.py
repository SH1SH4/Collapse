import pygame
import os
import sys
import pytmx

pygame.init()

pygame.display.set_caption("Start")
size = width, height = 1920, 1020
screen = pygame.display.set_mode(size)

color = "white"


class Map:
    def __init__(self, filename, free_tile):
        self.map = pytmx.load_pygame(f"maps/{filename}")
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.free_tile = free_tile

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                image = self.map.get_tile_image(x, y, 0)
                screen.blit(image, (x * self.tile_size, y * self.tile_size))

    def get_tile_id(self, position):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, 0)]

    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tile


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


class Hero:
    def __init__(self, position):
        self.x, self.y = position

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        center = self.x * 32 + 16, self.y * 32 + 16
        pygame.draw.circle(screen, (255, 0, 0), center, 32 // 2)


class Game:
    def __init__(self, map, hero):
        self.map = map
        self.hero = hero

    def render(self, screen):
        self.map.render(screen)
        self.hero.render(screen)

    def update_hero(self):
        next_x, next_y = self.hero.get_position()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
        if pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
        if self.map.is_free((next_x, next_y)):
            self.hero.set_position((next_x, next_y))


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


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

map = Map("poligon2.0.tmx", [30])
map.get_tile_id((2, 2))


def start_game():
    camera = Camera()
    running = True
    screen.fill((0, 0, 0))
    world = Map("poligon2.0.tmx", [30])
    hero = Hero((5, 5))
    game = Game(world, hero)

    clock = pygame.time.Clock()
    fps = 60
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
        clock.tick(fps)
        game.render(screen)
        game.update_hero()

    pygame.quit()

start_screen()
