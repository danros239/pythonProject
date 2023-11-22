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

left, right = (0, 0)

mouse_pos = pygame.Vector2(0, 0)


def rnd(minn, maxn):
    return minn + (maxn - minn) * rn.random()

def keyPressed(inputKey):
    keysPressed = pygame.key.get_pressed()
    if keysPressed[inputKey]:
        return True
    else:
        return False

def clamp(color):
    new_col = color
    for i in color:
        if i > 255:
            i = 255
        if i < 0:
            i = 0


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
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.a = pygame.Vector2(0, G)
        self.type = 0

        self.r = 10
        self.color = rn.choice(GAME_COLORS)
        self.live = 30
        self.friction = 0.25

    def __del__(self):
        print("Ball destroyed")


    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        self.vel += self.a / FPS

        self.pos += self.vel / FPS

        #self.vel += self.a / FPS

        if self.pos.x > WIDTH:
            self.pos.x -= 2 * (self.pos.x - WIDTH)
            self.vel.x *= -(1 - self.friction)
        if self.pos.x < 0:
            self.pos.x *= -1
            self.vel.x *= -(1 - self.friction)

        if self.pos.y > HEIGHT:
            dy = self.pos.y - HEIGHT
            # print("before: " + str(self.vy**2/2 - G*(self.y - HEIGHT)) + "after: ", end=' ')
            self.vel.y = math.sqrt(max(self.vel.y ** 2 - 4 * G * dy, 0)) * -(1 - self.friction)

            self.vel.x *= (1 - 0.8 * self.friction)
            # print((self.vy**2)/2 - G*(self.y - HEIGHT))
            self.pos.y -= 2 * dy

    def get_vel2(self):
        return self.vel.magnitude_squared()

    def draw(self):
        #self.pos = pygame.Vector2(self.x, self.y)
        if self.type == 0:
            pygame.draw.circle(
            self.screen,
            self.color,
            self.pos,
            self.r
            )
        elif self.type == 1:
            pygame.draw.line(screen, self.color, self.pos, self.pos + self.vel * 1.5/30)

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        if self.type >= 0:
            return (self.pos - pygame.Vector2(obj.pos.x, obj.pos.y)).magnitude_squared() < (self.r + obj.r)**2
        elif self.type == 1:
            flag = False
            point = pygame.Vector2(self.vel*1.5/30 / 5)
            for i in range(5):
                newpos = self.pos + i*point
                if (newpos - pygame.Vector2(obj.pos.x, obj.pos.y)).magnitude_squared() < (self.r + obj.r)**2:
                    flag = True
            return flag





class Gun:
    def __init__(self, screen):
        self.screen = screen
        self.f2_power = 100
        self.f2_maxpower = 1500
        self.f2_on = 0
        self.an = 1
        self.color = GREY
        self.x = Ball(self.screen).pos.x
        self.y = Ball(self.screen).pos.y

        self.ammo = [10, 10, 10]
        self.ammotype = 0

        self.pos = pygame.Vector2(self.x, self.y)
        self.vel = pygame.Vector2(0, 0)

        self.vmax = 100
        self.xs = 70
        self.ys = 30

        self.barrel = pygame.Vector2(self.xs, self.ys)
        self.sprite = pygame.Surface(self.barrel)
        self.sprite.set_colorkey(RED)

    def change_ammo(self, event):
        if keyPressed(pygame.K_1):
            self.ammotype = 0
        elif keyPressed(pygame.K_2):
            self.ammotype = 1
        elif keyPressed(pygame.K_3):
            self.ammotype = 2


    def fire2_start(self, event):
        if self.ammo[self.ammotype] > 0:
            self.f2_on = 1
            self.ammo[self.ammotype] -= 1
        else:
            self.color = BLUE

    def fire2_end(self, event):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        if self.f2_on == 1:
            self.an = math.atan2((mouse_pos.y - self.y), (mouse_pos.x - self.x))
            bullet += 1
            new_ball = Ball(self.screen, self.x, self.y)
            new_ball.type = self.ammotype

            if self.ammotype == 0:
                new_ball.r = 15
                new_ball.vel = pygame.Vector2(self.f2_power, 0).rotate(self.an * 180/3.1416)
                new_ball.color = RED

                balls.append(new_ball)
                self.f2_on = 0
                self.f2_power = 100

            if self.ammotype == 1:
                new_ball.r = 5
                new_ball.friction = 0.85
                new_ball.color = YELLOW
                new_ball.vel = pygame.Vector2(self.f2_power*3, 0).rotate(self.an * 180 / 3.1416)
                balls.append(new_ball)
                self.f2_on = 0
                self.f2_power = 100

    def targetting(self):
        """Прицеливание. Зависит от положения мыши."""
        self.an = math.atan2((mouse_pos.y - self.y), (mouse_pos.x - self.x))

    def update(self):
        if left:
            self.x -= self.vmax / FPS
        if right:
            self.x += self.vmax / FPS

        self.pos.x = self.x

    def draw(self):
        self.sprite.fill(self.color)
        sprite_new = pygame.transform.rotate(self.sprite, -self.an * 180 / math.pi)

        rect = sprite_new.get_rect()
        rect.center = (self.x - self.xs / 2 + self.ys / 2, self.y)

        sprite_new, rect = rotate(self.sprite, self.an * 180 / math.pi, (self.x, self.y), pygame.Vector2(self.xs/2 - self.ys/2, 0))
        screen.blit(sprite_new, rect)
        # pygame.draw.rect(self.screen, self.color, self.sprite)
        # pygame.draw.rect(self.screen, self.color, ((self.x, self.y), (self.f2_power/self.f2_maxpower*100 + 10, 10)), 2, 5)
        # FIXIT don't know how to do it

    def power_up(self):
        if self.f2_on:
            if self.f2_power < self.f2_maxpower:
                if self.ammotype == 0:
                    self.f2_power += 60*(30/FPS)
                if self.ammotype == 1:
                    self.f2_power += 20*(30/FPS)
                if(self.ammotype) == 2:
                    self.f2_power += 150*(30/FPS)
            self.color = (250*min(self.f2_power / self.f2_maxpower, 1), 55, 55)
            if self.color[0] > 255:
                self.color = clamp(self.color)
        else:
            self.color = GREY


class Target:
    def __init__(self, screen):
        """ Инициализация новой цели. """
        self.screen = screen
        self.points = 0
        self.live = 1
        self.type = 0

        self.pos_0 = pygame.Vector2(rnd(600, 780), rnd(300, 500))
        self.pos = pygame.Vector2(self.pos_0.x, self.pos_0.y)

        self.r_trajectory = rnd(100, 150)
        self.r_vel = rnd(50, 200)

        self.vel = pygame.Vector2(0, 0)
        self.accel = pygame.Vector2(0, 0)
        
        self.an = 0
        self.r_vect = pygame.Vector2(self.r_trajectory, 0)

        r = self.r = rnd(2, 50)
        color = self.color = RED

    # self.new_target()

    def new_target(self):
        """ Инициализация новой цели. """

        global score
        self.pos_0 = pygame.Vector2(rnd(600, 780), rnd(300, 500))
        x = self.x = rnd(600, 780)
        y = self.y = rnd(300, 550)
        self.pos = pygame.Vector2(self.x, self.y)
        r = self.r = rnd(2, 50)
        self.r_trajectory = rnd(100, 150)
        self.r_vel = rnd(50, 200)
        self.r_vect = pygame.Vector2(self.r_trajectory, 0)
        color = self.color = RED
        self.live = 1
        score += 1

    def hit(self, points=1):
        """Попадание шарика в цель."""
        self.points += points

    def update(self):
        if self.type == 0:
            self.r_vect = self.r_vect.rotate(self.r_vel/self.r_trajectory * 180/3.1416 / FPS)
            self.pos = self.pos_0 + self.r_vect
            print(self.pos)

        else:
            self.vel += self.accel / FPS
            self.pos += self.vel / FPS

    def draw(self):
        pygame.draw.circle(self.screen, RED, self.pos, self.r)

class Dropper:
    def __init__(self, screen, pos):
        self.screen = screen
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)
        self.vmax = 100
        self.size = pygame.Vector2(100, 50)

        self.cooldown = 1
        self.timer = 0
        self.bombs = 1

    def draw(self):
        pygame.draw.rect(self.screen, BLACK, (self.pos - self.size/2, self.size))

    def update(self, gun, targets):
        self.vel.x += 60/FPS * math.copysign(1, gun.pos.x - self.pos.x)

        if self.vel.magnitude() > self.vmax:
            self.vel.x = self.vmax * math.copysign(1, self.vel.x)

        self.pos += self.vel / FPS
        if math.fabs(self.pos.x - gun.pos.x) < 5 and self.timer > self.cooldown:
            self.drop(targets)
            self.timer = 0
        self.timer += 1/FPS


    def drop(self, targets):
        new_target = Target(self.screen)
        new_target.type = 1
        new_target.accel = pygame.Vector2(0, G/5)
        new_target.color = BLACK
        new_target.r = 10
        new_target.vel.x = self.vel.x
        new_target.pos = pygame.Vector2(self.pos)
        targets.append(new_target)
        return 1




pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
balls = []
targ_num = 2
score = 0
active = 0

text = "Score: {score:n}"
font = pygame.font.SysFont("Segoe UI Bold", 24)


clock = pygame.time.Clock()
guns = []
guns.append(Gun(screen))
guns.append(Gun(screen))
guns[1].x += 400

dropper = Dropper(screen, pygame.Vector2(100, 100))
targets = []

for i in range(targ_num):
    targets.append(Target(screen))
finished = False

while not finished:
    screen.fill(WHITE)
    scoreboard = font.render(text.format(score=score), True, BLACK)
    screen.blit(scoreboard, (20, 20))
    dropper.draw()
    for gun in guns:
        gun.draw()
    for i in targets:
        i.draw()
    for b in balls:
        b.draw()
    pygame.display.update()

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            guns[active].fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            guns[active].fire2_end(event)
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.Vector2(event.pos[0], event.pos[1])
        elif event.type == pygame.KEYDOWN:
            guns[active].change_ammo(event)
            if keyPressed(pygame.K_SPACE):
                active = (active + 1)%2

        right = keyPressed(pygame.K_d) or keyPressed(pygame.K_RIGHT)

        left = keyPressed(pygame.K_a) or keyPressed(pygame.K_LEFT)

    guns[active].targetting()

    for b in balls:
        b.move()
        if b.get_vel2() < 1:
            balls.remove(b)

        for i in targets:
            if b.hittest(i) and i.live:
                i.live = 0
                i.hit()
                i.new_target()
    guns[active].power_up()
    guns[active].update()
    dropper.update(guns[active], targets)

    for i in targets:
        i.update()


pygame.quit()
