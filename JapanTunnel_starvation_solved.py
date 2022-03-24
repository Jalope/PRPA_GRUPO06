"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = "north" 
NORTH = "south" 
MAXQUEUE = 2 #Para evitar inanición ponemos un numero maximo de coches que están a la espera de acceder al túnel
NCARS = 50
#Esta solución tiene deadlocke cuando la cola de ambos sentidos llega a valer simultaneamente MAXQUEUE
class Monitor():
    def __init__(self):
	
        self.mutex = Lock()
        self.turn_North = Value('i', 0)
        self.turn_South = Value('i', 0)
        self.is_free = Condition(self.mutex)
        self.queue_n = Value('i',0)
        self.queue_s = Value('i',0)
        self.nn = Value('i',0)
        self.ns = Value('i',0)
    
    def are_north_free(self):
    	return ((self.turn_South.value == 0) and (self.queue_s.value < MAXQUEUE))
    
    def are_south_free(self):
    	return ((self.turn_North.value == 0) and (self.queue_n.value < MAXQUEUE))

    def wants_enter(self, direction):
        self.mutex.acquire()
        if direction == NORTH:
        	self.queue_n.value += 1
        	print(self.queue_n.value,"cars heading south waiting")
        	self.is_free.wait_for(self.are_north_free)
        	self.turn_North.value += 1
        	
        	#self.nn.value +=1
        else:
        	self.queue_s.value += 1
        	print(self.queue_s.value,"cars heading north waiting")
        	self.is_free.wait_for(self.are_south_free)
        	self.turn_South.value += 1
        	
        	#self.ns.value += 1
        self.mutex.release()
	
    def leaves_tunnel(self, direction):
        self.mutex.acquire()
        if direction == NORTH:
        	self.turn_North.value -= 1
        	self.queue_n.value -= 1
        else:
        	self.turn_South.value -= 1
        	self.queue_s.value -= 1
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

def traffic(m):
    print("------------------")
    print("Traffic count:", m.nn.value, "north direction and", m.ns.value, "south direction")
	

def main():
    monitor = Monitor()
    cid = 0
    for _ in range(NCARS):
        #direction = NORTH if random.randint(0,1)==1  else SOUTH
        if random.randint(0,1)==1:
            direction = NORTH
            monitor.nn.value +=1
        else:
            direction = SOUTH
            monitor.ns.value +=1
            
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1/0.5)) # a new car enters each 0.5s

    print("----------------------------------")
    print("Traffic count:", monitor.ns.value, "north direction and", monitor.nn.value, "south direction")
    print("----------------------------------")    
if __name__ == '__main__':
    main()
