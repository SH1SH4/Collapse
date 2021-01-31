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


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


# options
tmx_data = load_pygame("maps/map.tmx")
map_data = pyscroll.TiledMapData(tmx_data)
screen_size = (1920, 1020)
TICK = 0
map_layer = pyscroll.BufferedRenderer(map_data, screen_size, True)

# groups
group = pyscroll.PyscrollGroup(map_layer=map_layer)
enemys = pygame.sprite.Group()
hearts = pygame.sprite.Group()
stats = pygame.sprite.Group()
bullets = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
hero_group = pygame.sprite.Group()
marker = pygame.sprite.Group()

# sounds
death = pygame.mixer.Sound('sound/death.wav')
run = pygame.mixer.Sound('sound/run.wav')
sound_theme = pygame.mixer.Sound('sound/main_theme.wav')
main_menu_theme = pygame.mixer.Sound('sound/menu_theme.wav')
hit = pygame.mixer.Sound('sound/hit3.wav')
heal = pygame.mixer.Sound('sound/successful_hit.wav')
stamina_png_back = pygame.transform.scale(load_image('задняя шкала.png'),
                                          (335, 25))

# global func
PILL_POSES = ((190, 22), (212, 253), (45, 242), (127, 99), (269, 266))
PILL_COUNTER = 0
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
        # pix_move = 3
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
        # if xs // 32 == xt // 32:
        #     move[0] = 0
        # if ys // 32 == xt // 32:
        #     move[1] = 0
        # return start[0] + pix_move * move[0], start[1] + pix_move * move[1]

        inf = 1000
        xs, ys = start
        tx, ty = target
        zx, zy = xs // 32 - 19, ys // 32 - 19
        obs = [[inf] * 41 for _ in range(41)]
        obs[19][19] = 0
        way = [[None] * 41 for _ in range(41)]
        queue = [(19, 19)]
        if 0 <= tx // 32 - zx < 41 and 0 <= ty // 32 - zy < 41:
            while queue and way[ty // 32 - zy][tx // 32 - zx] is None:
                x, y = queue.pop(0)
                for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                    next_x, next_y = x + dx, y + dy
                    if 0 <= next_x < 41 and 0 <= next_y < 41 and obs[next_y][next_x] == inf \
                            and self.is_free((next_x + zx, next_y + zy)):
                        obs[next_y][next_x] = obs[y][x] + 1
                        way[next_y][next_x] = (x, y)
                        queue.append((next_x, next_y))

            x, y = tx // 32 - zx, ty // 32 - zy
            if way[y][x] is not None:
                while way[y][x] != (19, 19):
                    x, y = way[y][x]
                return (zx + x) * 32, (zy + y) * 32
            else:
                return xs, ys
        else:
            return xs, ys # оно живое

    def render(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] not in self.free_tile:
                    Obstacles(self.map.get_tile_image(x, y, 0), x * self.tile_size, y * self.tile_size)

        for _ in range(30):
            x, y = (randint(15, self.width - 15), randint(15, self.height - 15))
            #if self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] in self.free_tile:
            Enemy((x * 32, y * 32), load_image("zombie.png"), load_image("zombie_left.png"), 2, 2, self.hero)

        for _ in range(20):
            x, y = (randint(15, self.width - 15), randint(15, self.height - 15))
            if self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] in self.free_tile:
                Apple(x * self.tile_size, y * self.tile_size, load_image("apple.png"), self.hero)

        for pos in PILL_POSES:
            x, y = pos
            Pill((y * 32, x * 32), load_image('pill.png'), self.hero)

    def get_tile_id(self, position):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, 0)]

    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tile


class Hero(pygame.sprite.Sprite):
    def __init__(self, position, sheet, sheet_left, columns, rows):
        super().__init__(group)
        self.frames = []
        self.frames_left = []
        self.cut_sheet(sheet, columns, rows)
        self.cut_sheet_left(sheet_left, columns, rows)
        self.cur_frame = 0
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        self.image = self.frames[self.cur_frame]
        self.rect.x, self.rect.y = position
        self.delay = 0
        self.hp = 1
        self.stamina = 50
        self.max_speed = 6
        self.speed = 0
        self.add(hero_group)
        self.update_hp(0)
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
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames_left.append(sheet.subsurface(
                    pygame.Rect(frame_location, self.rect.size)))

    def animation(self):
        if self.delay % 4 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        self.delay += 1

    def animation_left(self):
        if self.delay % 4 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames_left)
            self.image = self.frames_left[self.cur_frame]
        self.delay += 1

    def update(self, world):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] or key[pygame.K_RIGHT] or key[pygame.K_UP] or key[
            pygame.K_DOWN] or key[pygame.K_w] or \
                key[pygame.K_a] or key[pygame.K_s] or key[pygame.K_d]:
            for i in marker:
                i.kill()
            if not TICK % 10:
                self.run_channel = run.play()
            if key[pygame.K_LSHIFT] and self.stamina > 0 and self.speed > 0:
                self.update_stamina()
                self.max_speed = 10
                self.stamina -= 1
            else:
                if not TICK % 4 and not key[pygame.K_LSHIFT] and self.stamina <= 100:
                    self.stamina += 1
                    self.update_stamina()
                if self.max_speed > 6:
                    self.max_speed -= 1
                if self.speed > self.max_speed and not TICK % 5:
                    self.speed -= 1
            if key[pygame.K_LEFT] or key[pygame.K_a]:
                if self.speed < self.max_speed:
                    self.speed += 1
                self.animation_left()
                self.rect.x -= self.speed
                if pygame.sprite.spritecollideany(self, obstacles):
                    self.rect.x += self.speed
                    self.speed = 0
            if key[pygame.K_RIGHT] or key[pygame.K_d]:
                if self.speed < self.max_speed:
                    self.speed += 1
                self.animation()
                self.rect.x += self.speed
                if pygame.sprite.spritecollideany(self, obstacles):
                    self.rect.x -= self.speed
                    self.speed = 0
            if key[pygame.K_UP] or key[pygame.K_w]:
                if self.speed < self.max_speed:
                    self.speed += 1
                self.animation()
                self.rect.y -= self.speed
                if pygame.sprite.spritecollideany(self, obstacles):
                    self.rect.y += self.speed
                    self.speed = 0
            if key[pygame.K_DOWN] or key[pygame.K_s]:
                if self.speed < self.max_speed:
                    self.speed += 1
                self.animation()
                self.rect.y += self.speed
                if pygame.sprite.spritecollideany(self, obstacles):
                    self.rect.y -= self.speed
                    self.speed = 0
        else:
            if not len(marker):
                Marker(self.nearest(), self)
            if self.speed > 0:
                self.speed -= 1
            if self.stamina < 99:
                self.stamina += 2
                self.update_stamina()

    def nearest(self):
        near = float("inf")
        for enemy in enemys:
            if abs(self.rect.x - enemy.rect.x) + abs(self.rect.y - enemy.rect.y) < near:
                near = abs(self.rect.x - enemy.rect.x) + abs(self.rect.y - enemy.rect.y)
                choose = enemy
        return choose.rect.x, choose.rect.y

    def update_hp(self, change):
        hearts.remove(hearts.sprites())
        self.hp += change
        if change > 0:
            heal.play()
        elif change < 0:
            hit.play()
        for i in range(1, 6):
            if i <= self.hp:
                HP((pygame.transform.scale(load_image('heart.png'), (30, 30))), i)
            else:
                HP((pygame.transform.scale(load_image('broke.png'), (30, 30))), i)

    def update_stamina(self):
        StaminaBack(stamina_png_back)
        StaminaBlue(self.stamina)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, sheet, sheet_left, columns, rows, hero):
        pygame.sprite.Sprite.__init__(self, group)
        self.frames = []
        self.frames_left = []
        self.cut_sheet(sheet, columns, rows)
        self.cut_sheet_left(sheet_left, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        self.rect.x, self.rect.y = position
        self.delay = 0
        self.add(enemys)
        self.hero = hero

    def update(self, world):
        if not TICK % 9:
            next_step = world.find_path((self.rect.x, self.rect.y), self.hero.get_position())
            x, y = next_step
            if self.rect.x < x:
                self.animation()
            if self.rect.x > x:
                self.animation_left()
            if self.rect.y > y or self.rect.y < y:
                self.animation()
            self.rect.x, self.rect.y = next_step
        global DAMAGE_TICK
        if pygame.sprite.spritecollideany(self, hero_group) and pygame.time.get_ticks() - DAMAGE_TICK > 800:
            DAMAGE_TICK = pygame.time.get_ticks()
            self.hero.update_hp(-1)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(
                    pygame.Rect(frame_location, self.rect.size)))

    def cut_sheet_left(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames_left.append(sheet.subsurface(
                    pygame.Rect(frame_location, self.rect.size)))

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


class Marker(pygame.sprite.Sprite):
    def __init__(self, near, hero):
        super().__init__(group)
        self.image = pygame.Surface((50, 50))
        pygame.draw.circle(self.image, pygame.Color(9, 152, 184), (23, 25), 25, 3)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.hero = hero
        self.rect.x = near[0]
        self.rect.y = near[1]
        self.add(marker)

    def update(self, world):
        self.rect.x = self.hero.nearest()[0]
        self.rect.y = self.hero.nearest()[1]


class Bullet(pygame.sprite.Sprite):
    def __init__(self, start, target):
        super().__init__(bullets)
        self.start = start
        self.target = target
        self.f_tick = TICK    # Тик когда произошёл выстрел

    def update(self, screen):
        if TICK - self.f_tick < 60:
            pygame.draw.line(screen, (255, 0, 0, [(1 - (TICK - self.f_tick % 60) // 6 / 10)]), self.start, self.target, 8)
        else:
            self.kill()


class Obstacles(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__(obstacles)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.add(obstacles)


class Pill(pygame.sprite.Sprite):
    def __init__(self, pos, image, hero):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.hero = hero

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, hero_group):
            global PILL_COUNTER
            PILL_COUNTER += 1
            self.kill()


class Apple(pygame.sprite.Sprite):
    def __init__(self, x, y, image, hero):
        super().__init__(group)
        # pygame.sprite.Sprite.__init__(self, group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hero = hero

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, hero_group) and self.hero.hp < 5:
            self.hero.update_hp(1)
            self.kill()
            

class StaminaBlue(pygame.sprite.Sprite):
    def __init__(self, stamina):
        super().__init__(stats)
        stamina_screen = pygame.transform.scale(load_image('передняя шкала.png'), (int(3.25 * stamina), 15))
        self.image = stamina_screen
        self.rect = self.image.get_rect()
        self.rect.x = 45
        self.rect.y = 70


class StaminaBack(pygame.sprite.Sprite):
    def __init__(self, stamina_screen):
        super().__init__(stats)
        self.image = stamina_screen
        self.rect = self.image.get_rect()
        self.rect.x = 40
        self.rect.y = 65


class HP(pygame.sprite.Sprite):
    def __init__(self, sheet, health):
        super().__init__(hearts)
        self.image = sheet
        self.rect = self.image.get_rect()
        self.rect.x = 10 * (health * 3.5)
        self.rect.y = 30


class Exit(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(group)
        self.image = load_image("exit.png")
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 67 * 32, 0

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, hero_group):
            if PILL_COUNTER < 3:
                pass
            else:
                game_win()


class Button:
    def __init__(self, width, height, inactive=None, active=None):
        self.width = width
        self.height = height
        self.inactive = pygame.image.load(inactive)
        self.active = pygame.image.load(active)

    def draw(self, x, y, name):
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


def restart():
    global group, hearts, stats, obstacles, hero_group
    del group, hearts, stats, obstacles, hero_group
    group = pyscroll.PyscrollGroup(map_layer=map_layer)
    hearts = pygame.sprite.Group()
    stats = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    hero_group = pygame.sprite.Group()
    start_screen()


def print_text(text, x, y, font_size, font_color=(0, 0, 0),
               font_type="data/text.ttf"):
    font_type = pygame.font.Font(font_type, font_size)
    message = font_type.render(text, True, font_color)
    screen.blit(message, (x, y))


def play_but():
    play = Button(600, 150, "data/play_inactive.png", "data/play_active.png")
    play.draw(660, 460, "play")


def exit_but():
    exit_b = Button(600, 150, "data/exit_inacrive.png", "data/exit_acrive.png")
    exit_b.draw(660, 660, "exit")


def autors_but():
    exit_b = Button(600, 150, "data/ab_autors_inact.png",
                    "data/ab_autors_act.png")
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
        screen.fill((16, 19, 45))
        button_go = pygame.image.load("data/button_go.png")
        screen.blit(button_go, (1450, 170))
        esc = pygame.image.load("data/esc.png")
        screen.blit(esc, (770, 450))
        enter = pygame.image.load("data/enter-key.png")
        screen.blit(enter, (980, 540))
        shift = pygame.image.load("data/shift.png")
        screen.blit(shift, (900, 650))
        tab = pygame.image.load("data/tab.png")
        screen.blit(tab, (800, 350))
        screen.blit(enter, (1170, 790))
        print_text("УПРАВЛЕНИЕ", 780, 10, 50, (255, 255, 255))
        print_text("Кнопки W, A, S, D или СТРЕЛОЧКИ - управление игроком", 100,
                   250, 40, (255, 255, 255))
        print_text("Кнопка TAB - показать HUD", 100, 350, 40,
                   (255, 255, 255))
        print_text("Кнопка Esc - ПАУЗА в игре", 100, 450, 40, (255, 255, 255))
        print_text("Кнопка Enter - отмена паузы в игре", 100, 550, 40,
                   (255, 255, 255))
        print_text("Кнопка Shift - ускорение игрока", 100, 650, 40,
                   (255, 255, 255))
        print_text("Чтобы начать игру - нажмите кнопку Enter", 100, 800, 40,
                   (255, 255, 255))
        pygame.display.update()
    start_game()


def about_autors():
    main_menu_theme.stop()
    autors = True
    menu_background = pygame.image.load("data/background_2.png")
    screen.blit(menu_background, (0, 0))
    while autors:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                autors = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                autors = False
        print_text("Об авторах", 780, 10, 50, (255, 255, 255))
        print_text("Матвеев", 100, 100, 40, (255, 255, 255))
        print_text("Александр", 100, 200, 40, (255, 255, 255))
        print_text("Шишкин", 850, 100, 40, (255, 255, 255))
        print_text("Алексей", 850, 200, 40, (255, 255, 255))
        print_text("Арнаут", 1550, 100, 40, (255, 255, 255))
        print_text("Антон", 1550, 200, 40, (255, 255, 255))
        pygame.display.update()
    start_screen()


def about_game():
    main_menu_theme.stop()
    game = True
    menu_background = pygame.image.load("data/background_2.png")
    screen.blit(menu_background, (0, 0))
    while game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                game = False
        print_text("Сюжет игры", 780, 10, 50, (255, 255, 255))
        print_text("Весь мир охватила пандемия!", 100, 100, 40, (255, 255, 255))
        print_text("Все силовые структуры, включая ОМОН теперь не занимаются",
                   100, 200, 40, (255, 255, 255))
        print_text("защитой людей, а лишь пытаются их съесть!", 100, 300, 40,
                   (255, 255, 255))
        print_text("Вы оказались на бывшей территории летнего лагеря,", 100,
                   400, 40, (255, 255, 255))
        print_text("В этой локации очень много зараженных ОМОНовцов, все они",
                   100, 500, 40, (255, 255, 255))
        print_text("были посланы сюда для подавления очага.", 100, 600, 40,
                   (255, 255, 255))
        print_text(
            "Но они не смогли препядствовать вирусу, поэтому сами стали жертвами",
            100, 700, 40, (255, 255, 255))
        print_text(
            "Ваша задача - найти выход, либо найти 3 квестовых предмета.", 100,
            800, 40, (255, 255, 255))
        print_text("УДАЧИ!", 100, 900, 40, (255, 255, 255))
        pygame.display.update()
    start_screen()


def start_screen():
    main_menu_theme.play(-1)
    main_menu_theme.set_volume(0.1)
    menu_background = pygame.image.load("data/background.png")
    screen.blit(menu_background, (0, 0))
    work = True
    while work:
        for event in pygame.event.get():
            play_but()
            exit_but()
            autors_but()
            game_but()
            if event.type == pygame.QUIT:
                work = False
                pygame.quit()
                quit()
        pygame.display.update()


def pause():
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                paused = False
        print_text(
            "Игра находится на паузе, чтобы продолжить нажмите кнопку ENTER",
            145, 450, 40, (255, 255, 255))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            paused = False
        pygame.display.update()


def game_over():
    sound_theme.stop()
    death.play()
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
            death.stop()
            restart()
            pass
        pygame.display.update()


def game_win():
    sound_theme.stop()
    over = True
    while over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                over = False
        screen.fill((0, 0, 0))
        print_text("YOU WON!", 780, 450, 50, (255, 255, 255))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            over = False
            restart()
            pass
        pygame.display.update()


def start_game():
    global TICK, DAMAGE_TICK, PILL_COUNTER
    running = True
    screen.fill((0, 0, 0))
    hero = Hero((7 * 32, 12 * 32), load_image("hero.png"), load_image("hero_left.png"), 2, 2)
    world = Map("map.tmx", [30, 15, 10, 5, 34, 73, 313, 597, 577, 818, 442, 412, 567, 308, 580], hero)
    Exit()
    main_menu_theme.stop()
    sound_theme.set_volume(0.1)
    sound_theme.play(-1)
    world.render()
    fps = 60
    clock = pygame.time.Clock()
    # pole.draw(screen)
    stats.draw(screen)
    hud = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pause()
        if keys[pygame.K_MINUS]:
            PILL_COUNTER += 1
        if keys[pygame.K_TAB]:
            hud = True
        else:
            hud = False
        TICK += 1
        # obstacles.update() # лол эта функция ни на что не влияет, но фпс жрёт??
        group.center(hero.rect.center)
        group.update(world)
        bullets.update(screen)
        group.draw(screen)
        framerate = clock.get_fps()
        if hud:
            hearts.draw(screen)
            stats.draw(screen)
            print_text(f"Пилюль Собрано: {PILL_COUNTER}/3 Фпс:{str(framerate)[:2]}", 1550, 30, 20, (255, 255, 255))
        if not hero.hp:
            break
        pygame.display.flip()
        clock.tick(fps)
    else:
        pygame.quit()
    game_over()


start_screen()
