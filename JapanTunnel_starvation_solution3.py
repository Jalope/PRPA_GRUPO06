import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = "north"
NORTH = "south"
MAXFLUX = 10
NCARS = 500
# =============================================================================
# Usamos una constante MAXFLUX y dos variables booleanas que favorecen el paso en cada dirección.
# Cuando algún coche se pone en cola, contamos los coches que pasan en dirección contraria y
# cuando el numero de coches que han pasado superen MAXFLUX, cedemos el turno al otro lado
# Podemos imponer en la precondición del programa que MAXFLUX sea positiva y menor que 
# el número total de coches. La variable turno también se torna disponible cunado el túnel se queda vacío
# Sin deadlocke, sin inanición (en principio)
# =============================================================================
class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.turn_North = Value('b',True)
        self.turn_South = Value('b',True)
        self.is_free = Condition(self.mutex)
        self.queue = Condition(self.mutex)
        self.queue_n = Value('i',0)
        self.queue_s = Value('i',0)
        self.cars_n = Value('i',0)
        self.cars_s = Value('i',0)
        self.count_cars_n = Value('i',0)
        self.count_cars_s = Value('i',0)
    def is_north_free(self):
        return ((self.turn_North.value) and (self.cars_s.value == 0))
    
    def is_south_free(self):
        return ((self.turn_South.value) and (self.cars_n.value == 0))
   
    def wants_enter(self, direction):
        self.mutex.acquire()
        if direction == NORTH:
            if self.count_cars_n.value >= MAXFLUX:
                self.turn_North.value = False
                self.turn_South.value = True
                self.count_cars_n.value = 0
                self.is_free.notify_all() 
            self.queue_n.value += 1
            #print(self.queue_n.value, "cars quequeing north gate")
            self.is_free.wait_for(self.is_north_free)
            if self.queue_s.value > 0:
                self.count_cars_n.value += 1
            self.cars_n.value += 1
            self.queue_n.value -= 1
        else:
            if self.count_cars_s.value >= MAXFLUX:
                self.turn_North.value = True
                self.turn_South.value = False
                self.count_cars_s.value = 0
                self.is_free.notify_all()
            self.queue_s.value += 1
            #print(self.queue_n.value, "cars quequeing south gate")
            self.is_free.wait_for(self.is_south_free)
            if self.queue_n.value > 0:
                self.count_cars_s.value += 1
            self.cars_s.value += 1
            self.queue_s.value -= 1
           
        self.mutex.release()

    def leaves_tunnel(self, direction):
        self.mutex.acquire()
        if direction == NORTH:
            self.cars_n.value -=1
            if self.cars_n.value == 0:
                self.turn_South.value = True
                
        else:
            self.cars_s.value -= 1
            if self.cars_s.value == 0:
                self.turn_North.value = True
                
        self.is_free.notify_all()
        self.mutex.release()

def delay(n=3):
    time.sleep(random.random()*n)

def car(cid, direction, monitor):
    print(f"car {cid} direction {direction} created")
    delay(6)
    print(f"car {cid} heading {direction} wants to enter")
    monitor.wants_enter(direction)
    print(f"car {cid} heading {direction} enters the tunnel")
    delay(3)
    print(f"car {cid} heading {direction} leaving the tunnel")
    monitor.leaves_tunnel(direction)
    print(f"car {cid} heading {direction} out of the tunnel")


def main():
    monitor = Monitor()
    cid = 0
    for _ in range(NCARS):
        direction = NORTH if random.randint(0,1)==1  else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1/0.5)) # a new car enters each 0.5s
if __name__ == '__main__':
    main()
