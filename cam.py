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


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image

# options
tmx_data = load_pygame("maps/араб.tmx")
map_data = pyscroll.TiledMapData(tmx_data)
screen_size = (1920, 1020)
TICK = 0
map_layer = pyscroll.BufferedRenderer(map_data, screen_size, True)

# groups
group = pyscroll.PyscrollGroup(map_layer=map_layer)
apple = pygame.sprite.Group()
enemy = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
hero_group = pygame.sprite.Group()
heart = pygame.sprite.Group()
staminaa = pygame.sprite.Group()

# sounds
run = pygame.mixer.Sound('sound/run.wav')
sound_theme = pygame.mixer.Sound('sound/Alan Walker - Spectre.wav')
main_menu_theme = pygame.mixer.Sound('sound/Игорь Корнелюк - Воланд.wav')
hit = pygame.mixer.Sound('sound/hit3.wav')
regen = pygame.mixer.Sound('sound/successful_hit.wav')
stamina_png_back = pygame.transform.scale(load_image('задняя шкала.png'), (335, 25))

#global func
SPEED_HERO = 5
enemy = pygame.sprite.Group()
pole = pygame.sprite.Group()
DAMAGE_TICK = 0
LOSE = False


class Map:
    def __init__(self, filename, free_tile, hero):
        self.map = pytmx.load_pygame(f"maps/{filename}")
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.free_tile = free_tile
        self.hero = hero

    def find_path(self, start, target):
        pix_move = 2
        move = [0, 0]
        xs, ys = start
        xt, yt = target
        # Рандомное движение если герой далеко, нужно проверить свободен ли блок
        # if abs(fix_target[0] - fix_start[0]) > 19 or abs(fix_target[1] - fix_start[1]) > 19:
        #     # print('random')
        #     return start
        if xs < xt and self.is_free(((xs + pix_move) // 32, ys // 32)):
            move[0] += 1
        elif xs > xt and self.is_free(((xs - pix_move) // 32, ys // 32)):
            move[0] -= 1
        if ys < yt and self.is_free((xs // 32, (ys + pix_move) // 32)):
            move[1] += 1
        elif ys > yt and self.is_free((xs // 32, (ys - pix_move) // 32)):
            move[1] -= 1
        if xs // 32 == xt // 32:
            move[0] = 0
        if ys // 32 == xt // 32:
            move[1] = 0
        return start[0] + pix_move * move[0], start[1] + pix_move * move[1]
        # INF = 1000
        # fix_start = start[0] // self.tile_size, start[1] // self.tile_size
        # fix_target = target[0] // self.tile_size, target[1] // self.tile_size
        # if fix_start == fix_target:
        #     return fix_start
        # # 0ая координата карты противника по отношению к основной карте
        # zero_coord = fix_start[0] - 19, fix_start[1] - 19
        # zero_coord_abs = list(map(abs, zero_coord))
        # # print(zero_coord, zero_coord_abs)
        # # Рандомное движение если герой далеко, нужно проверить свободен ли блок
        # if abs(fix_target[0] - fix_start[0]) > 19 or abs(fix_target[1] - fix_start[1]) > 19:
        #     # print('random')
        #     return start
        #     # return (fix_start[0] + randint(-1, 1)) * 32, (fix_start[1] + randint(-1, 1)) * 32
        # x = 19
        # y = 19
        # distance = [[INF] * 39 for _ in range(39)]
        # distance[19][19] = 0
        # prev = [[None] * 39 for _ in range(39)]
        # queue = [(x, y)]
        # while queue:
        #     x, y = queue.pop(0)
        #     for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
        #         next_x, next_y = x + dx, y + dy
        #         if 0 <= next_x < 39 and 0 <= next_y < 39 and \
        #                 self.is_free((next_y + zero_coord[1], next_x + zero_coord[0])) and distance[next_y][next_x] == INF:
        #             distance[next_y][next_x] = distance[y][x] + 1
        #             prev[next_y][next_x] = (x, y)
        #             queue.append((next_x, next_y))
        #
        # x, y = fix_target[0] - zero_coord_abs[0], fix_target[1] - zero_coord_abs[1]
        # # print(fix_target)
        # # print(fix_start)
        # # print(x - zero_coord[0], y - zero_coord[1])
        # # print('------')
        # # print('сдвиг', zero_coord)
        # # print('старт', fix_start)
        # # print('старт с сдвигом', fix_start[0] + zero_coord[0], fix_start[1] + zero_coord[1])
        # # print('target без сдвига', x + zero_coord[0], y + zero_coord[1])
        # # print('target с свдигом', x, y)
        # # for i, ev in enumerate(distance):
        # #     print(i, ev)
        # # for i, ev in enumerate(prev):
        # #     print(i, ev)
        # if distance[y][x] == INF:
        #     # print('return start')
        #     return start
        # while prev[y][x] != (19, 19):
        #     if prev[y][x] == None:
        #         # print('ноне')
        #         return start
        #     x, y = prev[y][x]
        #     # print(x, y)
        # # print('откуда идём', start[0], start[1])
        # # print('куда идём', (fix_start[0] + (x - 19)) * self.tile_size, (fix_start[1] + (y - 19)) * self.tile_size)
        # return (fix_start[0] + (x - 19)) * self.tile_size, (fix_start[1] + (y - 19)) * self.tile_size

    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] not in self.free_tile:
                    Obstacles(self.map.get_tile_image(x, y, 0), x * self.tile_size,
                              y * self.tile_size)
        for _ in range(100):
            x, y = (randint(0, self.width - 1), randint(0, self.height - 1))
            if self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] in self.free_tile:
                Enemy((x * self.tile_size, y * self.tile_size), load_image("zombie.png"), load_image("zombie_left.png"),
                      2, 2, self.hero)

        for _ in range(20):
            x, y = (randint(0, self.width - 1), randint(0, self.height - 1))
            if self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] in self.free_tile:
                Apple(x * self.tile_size, y * self.tile_size, load_image("apple.png"), self.hero)

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
        self.add(obstacles)


class Apple(pygame.sprite.Sprite):
    def __init__(self, x, y, image, hero):
        super().__init__(apple)
        pygame.sprite.Sprite.__init__(self, group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hero = hero
        self.add(apple)

    def update(self, world, delta_time):
        if pygame.sprite.spritecollideany(self, hero_group):
            self.hero.hp_health += 1
            self.hero.hp_hero(self.hero.hp_health)
            self.kill()


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
                    view_management()
                    print("Ok")
                elif name == "exit":
                    pygame.quit()
                    quit()
                elif name == "autors":
                    about_autors()
                elif name == "game":
                    about_game()
        else:
            screen.blit(self.inactive, (x, y))


class Hero(pygame.sprite.Sprite):
    def __init__(self, position, sheet, sheet_left, columns, rows):
        pygame.sprite.Sprite.__init__(self, group)

        self.frames = []
        self.frames_left = []
        self.cut_sheet(sheet, columns, rows)
        self.cut_sheet_left(sheet_left, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect.x, self.rect.y = position
        self.delay = 0
        self.hp_health = 10
        self.stamina = 50
        self.add(hero_group)
        self.hp_hero(self.hp_health)

        self.run_channel = None
        self.hit_channel = None

    def get_position(self):
        return self.rect.x, self.rect.y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def cut_sheet_left(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames_left.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def animation(self):
        if self.delay % 10 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        self.delay += 1

    def animation_left(self):
        if self.delay % 10 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames_left)
            self.image = self.frames_left[self.cur_frame]
        self.delay += 1

    def update(self, world, delta_time):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] or key[pygame.K_RIGHT] or key[pygame.K_UP] or key[pygame.K_DOWN]:
            if self.run_channel is None or not self.run_channel.get_busy():
                self.run_channel = run.play()
        if key[pygame.K_LEFT] or key[pygame.K_RIGHT] or key[pygame.K_UP] or key[pygame.K_DOWN] or key[pygame.K_w] or \
                key[pygame.K_a] or key[pygame.K_s] or key[pygame.K_d]:

            if key[pygame.K_LEFT]:
                if key[pygame.K_LSHIFT]:
                    if self.stamina > 0:
                        self.rect.x -= SPEED_HERO + (self.razgon * 2)
                        self.animation_left()
                        self.stamina -= 1
                        self.stamina_hero(self.stamina)
                        if pygame.sprite.spritecollideany(self, obstacles):
                            self.rect.x += SPEED_HERO + (self.razgon * 2)
                            self.razgon = 0
                    else:
                        self.rect.x -= SPEED_HERO + self.razgon
                        self.animation_left()
                        if pygame.sprite.spritecollideany(self, obstacles):
                            self.rect.x += SPEED_HERO + self.razgon
                            self.razgon = 0

                else:
                    self.rect.x -= SPEED_HERO + self.razgon
                    self.animation_left()
                    if pygame.sprite.spritecollideany(self, obstacles):
                        self.rect.x += SPEED_HERO + self.razgon
                        self.razgon = 0
            elif key[pygame.K_a]:
                if key[pygame.K_LSHIFT]:
                    if self.stamina > 0:
                        self.rect.x -= SPEED_HERO + (self.razgon * 2)
                        self.animation_left()
                        self.stamina -= 1
                        self.stamina_hero(self.stamina)
                        if pygame.sprite.spritecollideany(self, obstacles):
                            self.rect.x += SPEED_HERO + (self.razgon * 2)
                            self.razgon = 0
                    else:
                        self.rect.x -= SPEED_HERO + self.razgon
                        self.animation_left()
                        if pygame.sprite.spritecollideany(self, obstacles):
                            self.rect.x += SPEED_HERO + self.razgon
                            self.razgon = 0

                else:
                    self.rect.x -= SPEED_HERO + self.razgon
                    self.animation_left()
                    if pygame.sprite.spritecollideany(self, obstacles):
                        self.rect.x += SPEED_HERO + self.razgon
                        self.razgon = 0
            if key[pygame.K_RIGHT]:
                if key[pygame.K_LSHIFT]:
                    if self.stamina > 0:
                        self.rect.x += SPEED_HERO + (self.razgon * 2)
                        self.animation()
                        self.stamina -= 1
                        self.stamina_hero(self.stamina)
                        if pygame.sprite.spritecollideany(self, obstacles):
                            self.rect.x -= SPEED_HERO + (self.razgon * 2)
                            self.razgon = 0
                    else:
                        self.rect.x += SPEED_HERO + self.razgon
                        self.animation()
                        if pygame.sprite.spritecollideany(self, obstacles):
                            self.rect.x -= SPEED_HERO + self.razgon
                            self.razgon = 0
                else:
                    self.rect.x += SPEED_HERO + self.razgon
                    self.animation()
                    if pygame.sprite.spritecollideany(self, obstacles):
                        self.rect.x -= SPEED_HERO + self.razgon
                        self.razgon = 0
            elif key[pygame.K_d]:
                if key[pygame.K_LSHIFT]:
                    if self.stamina > 0:
                        self.rect.x += SPEED_HERO + (self.razgon * 2)
                        self.animation()
                        self.stamina -= 1
                        self.stamina_hero(self.stamina)
                        if pygame.sprite.spritecollideany(self, obstacles):
                            self.rect.x -= SPEED_HERO + (self.razgon * 2)
                            self.razgon = 0
                    else:
                        self.rect.x += SPEED_HERO + self.razgon
                        self.animation()
                        if pygame.sprite.spritecollideany(self, obstacles):
                            self.rect.x -= SPEED_HERO + self.razgon
                            self.razgon = 0
                else:
                    self.rect.x += SPEED_HERO + self.razgon
                    self.animation()
                    if pygame.sprite.spritecollideany(self, obstacles):
                        self.rect.x -= SPEED_HERO + self.razgon
                        self.razgon = 0
            if key[pygame.K_UP]:
                if key[pygame.K_LSHIFT]:
                    if self.stamina > 0:
                        self.rect.y -= SPEED_HERO + (self.razgon * 2)
                        self.animation()
                        self.stamina -= 1
                        self.stamina_hero(self.stamina)
                        if pygame.sprite.spritecollideany(self, obstacles):
                            self.rect.y += SPEED_HERO + (self.razgon * 2)
                            self.razgon = 0
                    else:
                        self.rect.y -= SPEED_HERO + self.razgon
                        self.animation()
                        if pygame.sprite.spritecollideany(self, obstacles):
                            self.rect.y += SPEED_HERO + self.razgon
                            self.razgon = 0
                else:
                    self.rect.y -= SPEED_HERO + self.razgon
                    self.animation()
                    if pygame.sprite.spritecollideany(self, obstacles):
                        self.rect.y += SPEED_HERO + self.razgon
                        self.razgon = 0
            elif key[pygame.K_w]:
                if key[pygame.K_LSHIFT]:
                    if self.stamina > 0:
                        self.rect.y -= SPEED_HERO + (self.razgon * 2)
                        self.animation()
                        self.stamina -= 1
                        self.stamina_hero(self.stamina)
                        if pygame.sprite.spritecollideany(self, obstacles):
                            self.rect.y += SPEED_HERO + (self.razgon * 2)
                            self.razgon = 0
                    else:
                        self.rect.y -= SPEED_HERO + self.razgon
                        self.animation()
                        if pygame.sprite.spritecollideany(self, obstacles):
                            self.rect.y += SPEED_HERO + self.razgon
                            self.razgon = 0
                else:
                    self.rect.y -= SPEED_HERO + self.razgon
                    self.animation()
                    if pygame.sprite.spritecollideany(self, obstacles):
                        self.rect.y += SPEED_HERO + self.razgon
                        self.razgon = 0
            if key[pygame.K_DOWN]:
                if key[pygame.K_LSHIFT]:
                    if self.stamina > 0:

                        self.rect.y += SPEED_HERO + (self.razgon * 2)
                        self.animation()
                        self.stamina -= 1
                        self.stamina_hero(self.stamina)
                        if pygame.sprite.spritecollideany(self, obstacles):
                            self.rect.y -= SPEED_HERO + (self.razgon * 2)
                            self.razgon = 0
                    else:
                        self.rect.y += SPEED_HERO + self.razgon
                        self.animation()
                        if pygame.sprite.spritecollideany(self, obstacles):
                            self.rect.y -= SPEED_HERO + self.razgon
                            self.razgon = 0
                else:
                    self.rect.y += SPEED_HERO + self.razgon
                    self.animation()
                    if pygame.sprite.spritecollideany(self, obstacles):
                        self.rect.y -= SPEED_HERO + self.razgon
                        self.razgon = 0

            elif key[pygame.K_s]:
                if key[pygame.K_LSHIFT]:
                    if self.stamina > 0:

                        self.rect.y += SPEED_HERO + (self.razgon * 2)
                        self.animation()
                        self.stamina -= 1
                        self.stamina_hero(self.stamina)
                        if pygame.sprite.spritecollideany(self, obstacles):
                            self.rect.y -= SPEED_HERO + (self.razgon * 2)
                            self.razgon = 0
                    else:
                        self.rect.y += SPEED_HERO + self.razgon
                        self.animation()
                        if pygame.sprite.spritecollideany(self, obstacles):
                            self.rect.y -= SPEED_HERO + self.razgon
                            self.razgon = 0
                else:
                    self.rect.y += SPEED_HERO + self.razgon
                    self.animation()
                    if pygame.sprite.spritecollideany(self, obstacles):
                        self.rect.y -= SPEED_HERO + self.razgon
                        self.razgon = 0

            if not TICK % 21:
                if self.razgon == 6:
                    pass
                else:
                    self.razgon += 1
        else:
            self.razgon = 0
            if self.stamina != 100:
                if not TICK % 2:
                    if self.stamina <= 100:
                        self.stamina += 1
                        self.stamina_hero(self.stamina)

        if key[pygame.K_MINUS]:
            if self.hit_channel is None or not self.hit_channel.get_busy():
                self.hit_channel = hit.play()
            self.hp_health -= 1
            print(self.hp_health)
            self.hp_hero(self.hp_health)
            hit.play()

    def hp_hero(self, health):
        self.remove(heart)
        if health > 0:
            for i in range(1, 11):
                if i <= health:
                    hp = HP((pygame.transform.scale(load_image('heart.png'), (30, 30))), i)
                else:
                    hp = HP((pygame.transform.scale(load_image(
                        'kisspng-broken-heart-computer-icons-clip-art-broken-or-splitted-heart-vector-5ae64d56110867.0049922915250425180698.png'),
                        (30, 30))), i)
                    hit.play()

    def stamina_hero(self, stamina):
        stamina_hero = StaminaBack(stamina_png_back)
        stamina_hero = StaminaBlue(stamina)


def print_text(text, x, y, font_size, font_color=(0, 0, 0), font_type="data/text.ttf"):
    font_type = pygame.font.Font(font_type, font_size)
    message = font_type.render(text, True, font_color)
    screen.blit(message, (x, y))


class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, sheet, sheet_left, columns, rows, hero):
        pygame.sprite.Sprite.__init__(self, group)
        self.frames = []
        self.frames_left = []
        self.cut_sheet(sheet, columns, rows)
        self.cut_sheet_left(sheet_left, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect.x, self.rect.y = position
        self.delay = 0
        self.add(enemy)
        self.hero = hero

    def update(self, world, delta_time):
        # if not TICK % 32:
        next_step = world.find_path((self.rect.x, self.rect.y), self.hero.get_position())
        x, y = next_step
        print(f'''---{next_step}---''')
        if self.rect.x < x:
            self.animation()
        if self.rect.x > x:
            self.animation_left()
        if self.rect.y > y or self.rect.y < y:
            self.animation()
        self.rect.x, self.rect.y = next_step
        global DAMAGE_TICK
        if pygame.sprite.spritecollideany(self, hero_group) and pygame.time.get_ticks() - DAMAGE_TICK > 800:
            print(pygame.time.get_ticks(), DAMAGE_TICK, pygame.time.get_ticks() - DAMAGE_TICK)
            DAMAGE_TICK = pygame.time.get_ticks()
            self.hero.hp_health -= 1
            self.hero.hp_hero(self.hero.hp_health)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def cut_sheet_left(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames_left.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def animation(self):
        if self.delay % 10 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        self.delay += 1

    def animation_left(self):
        if self.delay % 10 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames_left)
            self.image = self.frames_left[self.cur_frame]
        self.delay += 1


class StaminaBlue(pygame.sprite.Sprite):
    def __init__(self, stamina):
        super().__init__(staminaa)
        stamina_screen = pygame.transform.scale(load_image('передняя шкала.png'), (int(3.25 * stamina), 15))
        self.image = stamina_screen
        self.rect = self.image.get_rect()
        self.rect.x = 45
        self.rect.y = 70


class StaminaBack(pygame.sprite.Sprite):
    def __init__(self, stamina_screen):
        super().__init__(staminaa)
        self.image = stamina_screen
        self.rect = self.image.get_rect()
        self.rect.x = 40
        self.rect.y = 65


class HP(pygame.sprite.Sprite):
    def __init__(self, sheet, health):
        super().__init__(heart)
        self.image = sheet
        self.rect = self.image.get_rect()
        self.rect.x = 10 * (health * 3.5)
        self.rect.y = 30


def restart():
    global group, apple, enemy, obstacles, hero_group, heart, staminaa, pole
    del group, apple, enemy, obstacles, hero_group, heart, staminaa, pole
    group = pyscroll.PyscrollGroup(map_layer=map_layer)
    pole = pygame.sprite.Group()
    apple = pygame.sprite.Group()
    enemy = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    hero_group = pygame.sprite.Group()
    heart = pygame.sprite.Group()
    staminaa = pygame.sprite.Group()
    start_screen()


class Pole_zreniya(pygame.sprite.Sprite):
    def __init__(self, position,  image):
        super().__init__(pole)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
        self.add(pole)


def play_but():
    play = Button(600, 150, "data/play_inactive.png", "data/play_active.png")
    play.draw(660, 460, "play")


def exit_but():
    exit_b = Button(600, 150, "data/exit_inacrive.png", "data/exit_acrive.png")
    exit_b.draw(660, 660, "exit")


def autors_but():
    exit_b = Button(600, 150, "data/ab_autors_inact.png", "data/ab_autors_act.png")
    exit_b.draw(1590, 970, "autors")


def game_but():
    exit_b = Button(600, 150, "data/ab_game_inact.png", "data/ab_game_act.png")
    exit_b.draw(10, 970, "game")


def view_management():
    managment = True
    while managment:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                managment = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                managment = False
        screen.fill((0, 0, 0))
        button_go = pygame.image.load("data/button_go.png")
        screen.blit(button_go, (1450, 25))
        esc = pygame.image.load("data/esc.png")
        screen.blit(esc, (770, 300))
        enter = pygame.image.load("data/enter-key.png")
        screen.blit(enter, (980, 400))
        shift = pygame.image.load("data/shift.png")
        screen.blit(shift, (900, 500))
        e = pygame.image.load("data/e.png")
        screen.blit(e, (860, 200))
        screen.blit(enter, (1170, 800))
        screen.blit(shift, (1200, 700))
        print_text("УПРАВЛЕНИЕ", 780, 10, 50, (255, 255, 255))
        print_text("Кнопки W, A, S, D или СТРЕЛОЧКИ - управление игроком", 100, 100, 40, (255, 255, 255))
        print_text("Кнопка E - подобрать предмет", 100, 200, 40, (255, 255, 255))
        print_text("Кнопка Esc - ПАУЗА в игре", 100, 300, 40, (255, 255, 255))
        print_text("Кнопка Enter - отмена паузы в игре", 100, 400, 40, (255, 255, 255))
        print_text("Кнопка Shift - ускорение игрока", 100, 500, 40, (255, 255, 255))
        print_text("P.S. чтобы игрок двигался быстрее, сначала подождите", 100, 600, 40, (255, 255, 255))
        print_text("разгон персонажа и примините кнопку Shift", 100, 700, 40, (255, 255, 255))
        print_text("Чтобы начать игру - нажмите кнопку Enter", 100, 800, 40, (255, 255, 255))
        pygame.display.update()
    start_game()


def about_autors():
    autors = True
    while autors:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                autors = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                autors = False
        screen.fill((0, 0, 0))
        pygame.display.update()
    start_screen()


def about_game():
    game = True
    while game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                game = False
        screen.fill((0, 0, 0))
        pygame.display.update()
    start_screen()


def start_screen():
    main_menu_theme.play(-1)
    main_menu_theme.set_volume(0.1)
    menu_background = pygame.image.load("data/background.png")
    screen.blit(menu_background, (0, 0))
    clock = pygame.time.Clock()
    run = True
    while run:
        for event in pygame.event.get():
            play_but()
            exit_but()
            autors_but()
            game_but()
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        pygame.display.update()


def pause():
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                paused = False
        print_text("Игра находится на паузе, чтобы продолжить нажмите кнопку ENTER", 145, 450, 40, (255, 255, 255))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            paused = False
        pygame.display.update()


def game_over():
    running = False
    sound_theme.stop()
    over = True
    while over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                over = False
        screen.fill((0, 0, 0))
        print_text("GAME OVER", 780, 450, 50, (255, 255, 255))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            over = False
            restart()
            pass
        pygame.display.update()


def start_game():
    global TICK, DAMAGE_TICK
    running = True
    screen.fill((0, 0, 0))
    hero = Hero((500, 500), load_image("hero.png"), load_image("hero_left.png"), 2, 2)
    world = Map("араб.tmx", [30, 15, 10, 5, 34], hero)
    pole_zr = Pole_zreniya((0, 0), load_image("pole_zrenia.png"))
    main_menu_theme.stop()
    sound_theme.set_volume(0.1)
    sound_theme.play(-1)
    world.render()
    clock = pygame.time.Clock()
    fps = 60
    clock = pygame.time.Clock()
    print(hero.hp_health)
    while running:
        delta_time = clock.tick(fps) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pause()
        TICK = pygame.time.get_ticks()
        print(TICK)
        obstacles.update()
        enemy.update(world, delta_time)
        group.update(world, delta_time)
        apple.update(world, delta_time)
        group.center(hero.rect.center)
        group.draw(screen)
        pole.draw(screen)
        heart.draw(screen)
        staminaa.draw(screen)
        if not hero.hp_health:
            break
        pygame.display.flip()
    else:
        pygame.quit()
    game_over()


start_screen()
