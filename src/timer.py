import time

timestamp = 0

#we have a changable timer so we can also run simulations
def update():
    global timestamp
    timestamp = time.ticks_ms()

add = time.ticks_add

diff = time.ticks_diff

update()
