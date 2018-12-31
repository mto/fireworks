from graphics import *
from random import uniform, randint
from concurrent.futures import ThreadPoolExecutor

CONST_GRAV = 0.1
colors = ['blue', 'green', 'red']


class Particle:
    def __init__(self, x, y, color, max_size, window, executor):
        self.x = x
        self.y = y
        self.sX = uniform(-5, 5)
        self.sY = uniform(-4, 0)
        self.c = color
        self.l = 0
        self.ls = randint(max_size - 20, max_size + 20)
        self.prev = None
        self.stop = False
        self.deleted = False
        self.window = window
        self.executor = executor

    def sim(self):
        self.sY = self.sY + CONST_GRAV
        self.x = self.x + self.sX
        self.y = self.y + self.sY
        self.l = self.l + 1

    def draw(self):
        if self.prev is not None:
            self.prev.undraw()
        c = Circle(Point(self.x, self.y), 3)
        c.setFill(self.c)
        if self.l < self.ls:
            c.draw(self.window)
            self.prev = c

    def curve(self):
        for idx in range(0, 70):
            if self.l > 50:
                self.stop = True
                break
            else:
                self.sim()
                time.sleep(0.04)

    @staticmethod
    def curve_task(p):
        p.curve()


class Rocket:
    def __init__(self, x, init_y, y, color, window, executor, game):
        self.x = x
        self.t = y
        self.sX = 0
        self.y = init_y
        self.c = color
        self.f = False
        self.prev = None
        self.exploded = False
        self.deleted = False
        self.fired = False
        self.d = uniform(-0.00001, 0.00001)
        self.window = window
        self.executor = executor
        self.game = game

    def sim(self):
        self.y = self.y - 6
        self.sX = self.sX + self.d
        self.x = self.x + self.sX

    def draw(self):
        if self.prev is not None:
            self.prev.undraw()
        c = Circle(Point(self.x, self.y), 5)
        c.setFill(self.c)
        c.setOutline(self.c)
        c.draw(self.window)
        self.prev = c

    def explode(self):
        print('Exploding...')
        self.exploded = True
        for i in range(40):
            p = Particle(self.x, self.y, self.c, randint(60, 100), self.window, self.executor)
            self.game.particles.append(p)
            self.executor.submit(Particle.curve_task, p)

    def fire(self):
        print('Firing rocket')
        self.fired = True
        while self.y > self.t:
            self.sim()
            time.sleep(0.1)

        self.explode()

    @staticmethod
    def fire_task(rocket):
        rocket.fire()


class FireWorks(object):
    def __init__(self):
        self.fw_executor = ThreadPoolExecutor(max_workers=10)
        self.zelle_executor = ThreadPoolExecutor(max_workers=1)

        self.rockets = list()
        self.particles = list()

        self.win = GraphWin("Fireworks", 800, 800)
        self.win.setBackground('black')

    def draw(self):
        for rocket in self.rockets:
            if rocket.exploded:
                if not rocket.deleted and rocket.prev is not None:
                    rocket.deleted = True
                    rocket.prev.undraw()
            elif rocket.fired:
                rocket.draw()

        for p in self.particles:
            if p.stop:
                if not p.deleted and p.prev is not None:
                    p.deleted = True
                    p.prev.undraw()
            else:
                p.draw()

    def start(self):
        for idx in range(0, 1000):
            if idx % 10 == 0:
                color = colors[randint(0, len(colors) - 1)]
                r = Rocket(300 + randint(50, 100), 500 + randint(0, 100), 200 + randint(0, 20), color, window=self.win,
                           executor=self.fw_executor, game=self)
                self.rockets.append(r)
                self.zelle_executor.submit(Rocket.fire_task, r)

            self.draw()
            time.sleep(0.02)


if __name__ == '__main__':
    FireWorks().start()
