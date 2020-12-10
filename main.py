import pygame
import os
import sys


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Ground:
    def __init__(self):
        self.speed = 10
        self.x = 350
        self.y = 350
        self.mod_y = [0, 0]  # up, down
        self.mod_x = [0, 0]  # left, right
        self.size = 20
        pass

    def render(self, screen):
        screen.fill((0, 0, 0))
        pygame.draw.ellipse(screen, pygame.Color('red'),
                            (self.x, self.y, self.size, self.size), 0)


if __name__ == '__main__':
    pygame.display.set_caption('CovidInRussia')
    size = x, y = 720, 720
    pygame.init()
    ground = Ground()
    screen = pygame.display.set_mode(size)
    running = True
    all_sprites = pygame.sprite.Group()
    road = pygame.sprite.Sprite()
    road.image = load_image("road.jpg")
    road.rect = road.image.get_rect()
    all_sprites.add(road)
    road.rect.x = 0
    road.rect.y = 0
    clock = pygame.time.Clock()
    fps = 60
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.key.key_code('w'):
                    ground.mod_y[0] = 1
                if event.key == pygame.key.key_code('s'):
                    ground.mod_y[1] = 1
                if event.key == pygame.key.key_code('a'):
                    ground.mod_x[0] = 1
                if event.key == pygame.key.key_code('d'):
                    ground.mod_x[1] = 1
            if event.type == pygame.KEYUP:
                if event.key == pygame.key.key_code('w'):
                    ground.mod_y[0] = 0
                    ground.y -= ground.speed
                if event.key == pygame.key.key_code('s'):
                    ground.mod_y[1] = 0
                    ground.y += ground.speed
                if event.key == pygame.key.key_code('a'):
                    ground.mod_x[0] = 0
                    ground.x -= ground.speed
                if event.key == pygame.key.key_code('d'):
                    ground.mod_x[1] = 0
                    ground.x += ground.speed

        ground.x += (ground.speed * -ground.mod_x[0] + ground.speed *
                     ground.mod_x[1])
        ground.y += (ground.speed * -ground.mod_y[0] + ground.speed *
                     ground.mod_y[1])
        ground.render(screen)
        # ground.render(road)
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
