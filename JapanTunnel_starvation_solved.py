"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = "north" #0
NORTH = "south" #1

NCARS = 100

class Monitor():
    def __init__(self):
	
        self.mutex = Lock()
        self.turn_North = Value('i', 0)
        self.turn_South = Value('i', 0)
        self.is_free = Condition(self.mutex)
        self.current_direction = Value('i',0)
    
    def are_north_free(self):
    	return self.turn_South.value == 0 
    
    def are_south_free(self):
    	return self.turn_North.value == 0

    def wants_enter(self, direction):
        self.mutex.acquire()
        if direction == NORTH:
        	self.current_direction.value = 1
        	
        	self.is_free.wait_for(self.are_north_free, timeout=2)
        	self.turn_North.value += 1
        else:
        	self.current_direction.value = 0
        	
        	self.is_free.wait_for(self.are_south_free, timeout=2)
        	self.turn_South.value += 1
        
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
    print(f"car {cid} direction {direction} created", flush=True)
    delay(6)
    print(f"car {cid} heading {direction} wants to enter", flush=True)
    monitor.wants_enter(direction)
    print(f"car {cid} heading {direction} enters the tunnel", flush=True)
    delay(3)
    print(f"car {cid} heading {direction} leaving the tunnel", flush=True)
    monitor.leaves_tunnel(direction)
    print(f"car {cid} heading {direction} out of the tunnel", flush=True)



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
