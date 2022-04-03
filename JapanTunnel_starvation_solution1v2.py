import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = "north"
NORTH = "south"
MAXQUEUE = 5
NCARS = 100
# =============================================================================
# Contamos los coches que hay en cola e imponemos que no pueda ser más larga que MAXQUEUE
# Puede tener deadlocke si ambas colas superan MAXQUEUE al mismo tiempo
# Puede tener inanición si nunca se ponen la cola más de MAXQUEUE coches
# =============================================================================
class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.turn_North = Value('i',0)
        self.turn_South = Value('i',0)
        self.is_free = Condition(self.mutex)
        self.queue = Condition(self.mutex)
        self.queue_n = Value('i',0)
        self.queue_s = Value('i',0)
        
    def is_north_free(self):
        return (self.turn_South.value == 0)
    
    def is_south_free(self):
        return (self.turn_North.value == 0)
    
    def queueing_north(self):
        return (self.queue_n.value < MAXQUEUE)
    
    def queueing_south(self):
        return (self.queue_s.value < MAXQUEUE)

    def wants_enter(self, direction):
        self.mutex.acquire()
        if direction == NORTH:
            self.queue_n.value += 1
            print(self.queue_n.value, "cars quequeing north gate")
            self.queue.wait_for(self.queueing_south)
            self.is_free.wait_for(self.is_north_free)
            self.turn_North.value += 1
            self.queue_n.value -=1
            
        else:
            self.queue_s.value += 1
            print(self.queue_s.value, "cars quequeing south gate")
            self.queue.wait_for(self.queueing_north)
            self.is_free.wait_for(self.is_south_free)
            self.turn_South.value += 1
            self.queue_s.value -= 1
        self.queue.notify_all()   
        self.mutex.release()

    def leaves_tunnel(self, direction):
        self.mutex.acquire()
        if direction == NORTH:
            self.turn_North.value -= 1
        else:
            self.turn_South.value -= 1
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
