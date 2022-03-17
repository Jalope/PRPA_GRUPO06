"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value
from xml.etree.ElementTree import C14NWriterTarget

SOUTH = "north"
NORTH = "south"

NCARS = 10

# Esta solución es la más restrictiva. Sólo un coche puede usar el tunel por vez.


class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.turn = Value('b', True)
        self.is_free = Condition(self.mutex)
        # si es NORT (S -> N) es True si es SOUTH (N -> S) es False
        self.dirrTunelNorte = Value('b', False)
        self.dirr = "north"
        self.n = 0
        self.s = 0
        self.dentro = 0

    def empty(self):
        if self.dirr != NORTH:
            return ((self.s.value+self.dentro.value) == 0) or (self.s.value == 0 and self.dirrTunelNorte.value)
        else:
            return ((self.n.value+self.dentro.value) == 0) or (self.n.value == 0 and not self.dirrTunelNorte.value)

    def wants_enter(self, direction, cN, cS, cDentro):
        self.mutex.acquire()
        cN.value = (cN.value+1) if direction != NORTH else cN.value
        cS.value = (cS.value+1) if direction == NORTH else cS.value

        self.dirr = direction
        self.n = cN
        self.s = cS
        self.dentro = cDentro
        print("dirr: ", self.dirr, " cN:", self.n.value, " cS:", self.s.value, " D:", self.dentro.value)
        self.is_free.wait_for(self.empty)

        cN.value = (cN.value-1) if direction != NORTH else cN.value
        cS.value = (cS.value-1) if direction == NORTH else cS.value
        self.n = cN
        self.s = cS
        self.dirrTunelNorte.value = True if direction == NORTH else False
        cDentro.value = cDentro.value + 1
        self.dentro = cDentro
        self.mutex.release()

    def leaves_tunnel(self, direction, cN, cS, cDentro):
        self.mutex.acquire()
        cDentro.value = cDentro.value - 1
        self.dentro = cDentro
        self.is_free.notify_all()
        self.mutex.release()


def delay(n=3):
    time.sleep(random.random()*n)


def car(cid, direction, monitor, cN, cS, cDentro):
    print(f"car {cid} direction {direction} created", flush=True)
    delay(6)
    print(f"car {cid} heading {direction} wants to enter", flush=True)
    monitor.wants_enter(direction, cN, cS, cDentro)
    print(f"car {cid} heading {direction} enters the tunnel", flush=True)
    delay(3)
    print(f"car {cid} heading {direction} leaving the tunnel", flush=True)
    monitor.leaves_tunnel(direction, cN, cS, cDentro)
    print(f"car {cid} heading {direction} out of the tunnel", flush=True)


def main():
    monitor = Monitor()
    cid = 0
    cN = Value('i', 0)
    cS = Value('i', 0)
    cDentro = Value('i', 0)

    for _ in range(NCARS):
        if random.randint(0, 1) == 1:
            direction = NORTH
        else:
            direction = SOUTH
        cid += 1
        p = Process(target=car, args=(
            cid, direction, monitor, cN, cS, cDentro))
        p.start()
        time.sleep(random.expovariate(1/0.5))  # a new car enters each 0.5s


if __name__ == '__main__':
    main()
