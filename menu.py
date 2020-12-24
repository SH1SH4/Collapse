import pygame

pygame.init()

pygame.display.set_caption("Start")
size = width, height = 800, 500
screen = pygame.display.set_mode(size)

color = "white"


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
                    print("Ok")
                if name == "new_game":
                    print("New game")
                if name == "exit":
                    pygame.quit()
                    quit()
        else:
            screen.blit(self.inactive, (x, y))


def play_but():
    play = Button(200, 50, "data/play_inactive.png", "data/play_active.png")
    play.draw(300, 200, "play")


def newgame_but():
    new_game = Button(200, 50, "data/test_inacrive.png", "data/test_acrive_black.png")
    new_game.draw(300, 270, "new_game")


def exit_but():
    exit_b = Button(200, 50, "data/exit_inacrive.png", "data/exit_acrive.png")
    exit_b.draw(300, 340, "exit")


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


start_screen()
