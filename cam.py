import pygame
import os
import sys
from random import randint
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
TICK = 0
map_layer = pyscroll.BufferedRenderer(map_data, screen_size, True)
group = pyscroll.PyscrollGroup(map_layer=map_layer)
obstacles = pygame.sprite.Group()
enemyx = pygame.sprite.Group()
herox = pygame.sprite.Group()


class Map:
    def __init__(self, filename, free_tile, hero):
        self.map = pytmx.load_pygame(f"maps/{filename}")
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.free_tile = free_tile
        self.hero = hero

    def find_path(self, start, target):
        # pix_move = 5
        # move = [0, 0]
        # xs, ys = start
        # xt, yt = target
        # if xs < xt and self.is_free(((xs + pix_move) // 32, ys // 32)):
        #     move[0] += 1
        # elif xs > xt and self.is_free(((xs - pix_move) // 32, ys // 32)):
        #     move[0] -= 1
        # if ys < yt and self.is_free((xs // 32, (ys + pix_move) // 32)):
        #     move[1] += 1
        # elif ys > yt and self.is_free((xs // 32, (ys - pix_move) // 32)):
        #     move[1] -= 1
        # # if xs // 32 == xt // 32:
        # #     move[0] = 0
        # # if ys // 32 == xt // 32:
        # #     move[1] = 0
        # return start[0] + pix_move * move[0], start[1] + pix_move * move[1]
        INF = 1000
        fix_start = start[0] // self.tile_size, start[1] // self.tile_size
        fix_target = target[0] // self.tile_size, target[1] // self.tile_size
        if fix_start == fix_target:
            return fix_start
        # 0ая координата карты противника по отношению к основной карте
        zero_coord = (fix_start[0] - 20) * 2, (fix_start[1] - 20) * 2
        # Рандомное движение если герой далеко, нужно проверить свободен ли блок
        # if fix_target[0] - zero_coord[0] < 0 and fix_target[1] - zero_coord[1] < 0:
        #     return (fix_start[0] + randint(-1, 1)) * 32, (fix_start[1] + randint(-1, 1)) * 32
        x = 19
        y = 19
        distance = [[INF] * 39 for _ in range(39)]
        distance[19][19] = 0
        prev = [[None] * 39 for _ in range(39)]
        queue = [(x, y)]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
                next_x, next_y = x + dx, y + dy
                if 0 <= next_x < 39 and 0 <= next_y < 39 and \
                        self.is_free((next_y + zero_coord[1], next_x + zero_coord[0])) and distance[next_y][next_x] == INF:
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))

        x, y = fix_target[0] - zero_coord[0], fix_target[1] - zero_coord[1]
        # print(fix_target)
        # print(fix_start)
        # print(x - zero_coord[0], y - zero_coord[1])
        print('сдвиг', zero_coord)
        print('старт', fix_start)
        print('старт с сдвигом', fix_start[0] + zero_coord[0])
        print('target без сдвига', x + zero_coord[0], y + zero_coord[1])
        print('target с свдигом', x, y)
        # for i, ev in enumerate(distance):
        #     print(i, ev)
        # for i, ev in enumerate(prev):
        #     print(i, ev)
        if not 38 >= y - zero_coord[1] >= 0 or not 38 >= x - zero_coord[0] >= 0:
            return start
        if distance[y - zero_coord[1]][x - zero_coord[0]] == INF:
            return start
        while prev[y][x] != (19, 19):
            if prev[y][x] == None:
                return start
            x, y = prev[y][x]

        print('куда идём', x, y)
        print('сдвиг', zero_coord)
        return (x + zero_coord[0]) * self.tile_size, (y + zero_coord[1]) * self.tile_size

    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] not in self.free_tile:
                    Obstacles(self.map.get_tile_image(x, y, 0), x * self.tile_size,
                              y * self.tile_size)
        for i in range(100):
            x, y = (randint(0, self.width - 1), randint(0, self.height - 1))
            if self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] in self.free_tile:
                Enemy((x * self.tile_size, y * self.tile_size), load_image("llama (1).png"), 3, 2,
                      self.hero)

    def get_tile_id(self, position):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, 0)]

    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tile


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
    def __init__(self, position, sheet, columns, rows):
        pygame.sprite.Sprite.__init__(self, group)

        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect.x, self.rect.y = position
        self.delay = 0
        self.speed = 16
        self.add(herox)

    def get_position(self):
        return self.rect.x, self.rect.y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(
                    pygame.Rect(frame_location, self.rect.size)))

    def animation(self):
        if self.delay % 5 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        self.delay += 1

    def update(self, world, delta_time):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.animation()
            if pygame.sprite.spritecollideany(self, obstacles):
                self.rect.x += self.speed
        if key[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.animation()
            if pygame.sprite.spritecollideany(self, obstacles):
                self.rect.x -= self.speed
        if key[pygame.K_UP]:
            self.rect.y -= self.speed
            self.animation()
            if pygame.sprite.spritecollideany(self, obstacles):
                self.rect.y += self.speed
        if key[pygame.K_DOWN]:
            self.rect.y += self.speed
            self.animation()
            if pygame.sprite.spritecollideany(self, obstacles):
                self.rect.y -= self.speed


class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, sheet, columns, rows, hero):
        pygame.sprite.Sprite.__init__(self, group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect.x, self.rect.y = position
        self.delay = 0
        self.add(enemyx)
        self.hero = hero

    def update(self, world, delta_time):
        # global TICK
        # if not TICK % 2:
        next_position = world.find_path((self.rect.x, self.rect.y), self.hero.get_position())
        old = (self.rect.x, self.rect.y)
        self.rect.x, self.rect.y = next_position
        if pygame.sprite.spritecollideany(self, obstacles):
            self.rect.x, self.rect.y = old

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(
                    pygame.Rect(frame_location, self.rect.size)))


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
    new_game = Button(400, 100, "data/test_inacrive.png",
                      "data/test_acrive_black.png")
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
    global TICK
    running = True
    screen.fill((0, 0, 0))
    hero = Hero((32, 32), load_image("llama (1).png"), 3, 2)
    world = Map("poligon2.0.tmx", [30, 15], hero)
    world.render()
    fps = 60
    clock = pygame.time.Clock()
    while running:
        TICK += clock.tick()
        delta_time = clock.tick(fps) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        obstacles.update()
        enemyx.update(world, delta_time)
        group.update(world, delta_time)
        group.center(hero.rect.center)
        group.draw(screen)
        pygame.display.flip()
    pygame.quit()


start_screen()
