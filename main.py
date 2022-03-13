#!/bin/python3

import pygame
import time
import math
import threading
import numpy


W = 1000
H = 1000

def is_inside_set(c):
    z = 0
    for x in range(50):
        try:
            z = z**2 + c
        except Exception:
            return False

    return numpy.abs(z) < 2

def main():
    pygame.init()
    loop = True
    screen = pygame.display.set_mode((W, H))

    current_view = [2, 2]
    center = complex(0, 0)
    x = [(current_view[0]*2 * x / W - current_view[0]) for x in range(W+1)]
    y = [(current_view[1]*2 * y / W - current_view[1]) for y in range(H+1)]
    plane = [ [0] * W ] * H
    
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    loop = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    current_view = [current_view[0]*0.9, current_view[1]*0.9]
                    x = [(current_view[0]*2 * x / W - current_view[0]) for x in range(W+1)]
                    y = [(current_view[1]*2 * y / W - current_view[1]) for y in range(H+1)]

        if loop == False:
            break

        for i in range(H):
            for j in range(W):
                plane[i][j] = is_inside_set(complex(x[i], y[j]) - center)
                screen.set_at( (i, j), 0x000000 if plane[i][j] == True else 0xFFFFFF)

        pygame.display.flip()
        time.sleep(0.5)

    pygame.quit()

# for multi-threading
def mtmain():
    pygame.init()

    screen = pygame.display.set_mode((W, H))
    threads = []

    zoom = 5.0
    while True:
        for i in range(H):
            t = threading.Thread(target=draw, args=(i, screen, zoom))
            t.daemon = True
            t.start()
            threads.append(t)

        zoom *= 1.75
        for i in range(H):
            threads[i].join()

    pygame.quit()


if __name__=='__main__':
    main()
