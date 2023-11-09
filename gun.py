import math
import random as rn

import pygame

FPS = 60
G = 9.8 * 10 ** 2

RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
GAME_COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]

WIDTH = 800
HEIGHT = 600


def rnd(minn, maxn):
    return minn + (maxn - minn) * rn.random()


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def dot(self, vec):
        return self.x * vec.x + self.y + vec.y

    def rotate(self, an):
        return Vec2(self.x*math.cos(an) + self.y*math.sin(an), self.x*-math.sin(an) + self.y*math.cos(an))

    def v(self):
        return pygame.Vector2(self.x, self.y)


def rotate(surface, angle, pivot, offset):
    """Rotate the surface around the pivot point.

        Args:
            surface (pygame.Surface): The surface that is to be rotated.
            angle (float): Rotate by this angle.
            pivot (tuple, list, pygame.math.Vector2): The pivot point.
            offset (pygame.math.Vector2): This vector is added to the pivot.
        """
    rot_img = pygame.transform.rotate(surface, -angle)
    rot_offset = offset.rotate(angle)
    rect = rot_img.get_rect(center=pivot + rot_offset)
    return rot_img, rect


class Ball:
    def __init__(self, screen: pygame.Surface, x=40, y=450):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 10
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = -G
        self.color = rn.choice(GAME_COLORS)
        self.live = 30
        self.friction = 0.25

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        self.vx += self.ax / FPS / 2
        self.vy += self.ay / FPS / 2
        self.x += self.vx / FPS
        self.y -= self.vy / FPS
        self.vx += self.ax / FPS / 2
        self.vy += self.ay / FPS / 2

        if self.x > WIDTH:
            self.x -= 2 * (self.x - WIDTH)
            self.vx *= -1
        if self.x < 0:
            self.x *= -1
            self.vx *= -1

        if self.y > HEIGHT:
            dy = self.y - HEIGHT
            # print("before: " + str(self.vy**2/2 - G*(self.y - HEIGHT)) + "after: ", end=' ')
            self.vy = math.sqrt(max(self.vy ** 2 - 4 * G * dy, 0)) * (1 - self.friction)
            self.vx *= (1 - 0.8 * self.friction)
            # print((self.vy**2)/2 - G*(self.y - HEIGHT))
            self.y -= 2 * dy

    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        # print((self.x - obj.x)**2 + (self.y - obj.y)**2 - (self.r + obj.r)**2)

        return ((self.x - obj.x) ** 2 + (self.y - obj.y) ** 2) < (self.r + obj.r) ** 2


class Gun:
    def __init__(self, screen):
        self.screen = screen
        self.f2_power = 100
        self.f2_maxpower = 1500
        self.f2_on = 0
        self.an = 1
        self.color = GREY
        self.x = Ball(self.screen).x
        self.y = Ball(self.screen).y
        self.xs = 70
        self.ys = 30

        self.barrel = pygame.Vector2(self.xs, self.ys)
        self.sprite = pygame.Surface(self.barrel)
        self.sprite.set_colorkey(RED)

    def fire2_start(self, event):
        self.f2_on = 1

    def fire2_end(self, event):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        new_ball = Ball(self.screen)
        new_ball.r += 5
        self.an = math.atan2((event.pos[1] - new_ball.y), (event.pos[0] - new_ball.x))

        new_ball.vx = self.f2_power * math.cos(self.an)
        new_ball.vy = - self.f2_power * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = 0
        self.f2_power = 100

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            self.an = math.atan2((event.pos[1] - 450), (event.pos[0] - 20))
        if self.f2_on:
            self.color = RED
        else:
            self.color = GREY

    def draw(self):
        self.sprite.fill(self.color)
        sprite_new = pygame.transform.rotate(self.sprite, -self.an * 180 / math.pi)

        rect = sprite_new.get_rect()
        rect.center = (self.x - self.xs / 2 + self.ys / 2, self.y)

        sprite_new, rect = rotate(self.sprite, self.an * 180 / math.pi, (self.x - self.xs/2 + self.ys/2, self.y), pygame.Vector2(self.xs/2 - self.ys/2, 0))
        screen.blit(sprite_new, rect)
        # pygame.draw.rect(self.screen, self.color, self.sprite)
        # pygame.draw.rect(self.screen, self.color, ((self.x, self.y), (self.f2_power/self.f2_maxpower*100 + 10, 10)), 2, 5)
        # FIXIT don't know how to do it

    def power_up(self):
        if self.f2_on:
            if self.f2_power < self.f2_maxpower:
                self.f2_power += 30
            self.color = (245 * self.f2_power / self.f2_maxpower, 55, 55)
        else:
            self.color = GREY


class Target:
    def __init__(self, screen):
        """ Инициализация новой цели. """
        self.screen = screen
        self.points = 0
        self.live = 1
        x = self.x = rnd(600, 780)
        y = self.y = rnd(300, 550)
        r = self.r = rnd(2, 50)
        color = self.color = RED

    # self.new_target()

    def new_target(self):
        """ Инициализация новой цели. """
        x = self.x = rnd(600, 780)
        y = self.y = rnd(300, 550)
        r = self.r = rnd(2, 50)
        color = self.color = RED
        self.live = 1

    def hit(self, points=1):
        """Попадание шарика в цель."""
        self.points += points

    def draw(self):
        pygame.draw.circle(self.screen, RED, (self.x, self.y), self.r)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
balls = []

clock = pygame.time.Clock()
gun = Gun(screen)
target = Target(screen)
finished = False

while not finished:
    screen.fill(WHITE)
    gun.draw()
    target.draw()
    for b in balls:
        b.draw()
    pygame.display.update()

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            gun.fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            gun.fire2_end(event)
        elif event.type == pygame.MOUSEMOTION:
            gun.targetting(event)

    for b in balls:
        b.move()
        if b.hittest(target) and target.live:
            target.live = 0
            target.hit()
            target.new_target()
    gun.power_up()

pygame.quit()
