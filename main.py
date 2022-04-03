#!/bin/python3

import pygame
import time
import math
import numpy
from multiprocessing import Process, Pipe, Lock


W = 1000
H = 1000
iterations = 20

def cal_color(velocity, n):
    return ( numpy.floor(0xFF*(n/iterations)), numpy.floor(0xFF*(0.3*(1-velocity/32)+0.7*n/iterations)), 0xFF - numpy.floor(velocity*0xFF/32))

def is_inside_set(c):
    z = 0
    x = 0
    velocity = 0
    for x in range(iterations):
        velocity = numpy.abs(z)
        if velocity > 4:
            return cal_color(velocity, x)
        z = z**2 + c

    if velocity > 2:
        return cal_color(velocity, x)
    return (0, 0, 0)

def mandelbrot(conn, x, y, matrix, center):
    # starting delay
    time.sleep(0.5)

    for h in range(len(y)):
        for w in range(len(x)):
            matrix[h][w] = is_inside_set(complex(x[w], y[h]) + center)

    conn.send(matrix)

def mouse_pos_in_coord(pos, current_view):
    return complex(current_view[0]*2 * pos[0] / W - current_view[0], current_view[1] - current_view[1]*2 * pos[1] / W)

def main():
    pygame.init()
    loop = True
    free_to_render = True
    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()

    zoom_in = 0.9
    zoom_out = 1.1
    

    current_view = [2, 2]
    center = complex(-1.5, 0)
    center_shift = complex(0, 0)
    x = [(current_view[0]*2 * x / W - current_view[0]) for x in range(W)]
    y = [(current_view[1] - current_view[1]*2 * y / W) for y in range(H)]
    plane_matrix = []
    for height in range(len(y)):
        plane_matrix.append([])
        for width in range(len(x)):
            plane_matrix[height].append((0, 0, 0))

    plane = pygame.Surface((W, H))
    
    screen.fill((0xFF, 0xFF, 0xFF))
    pygame.display.flip()
    
    parent_conn, child_conn = Pipe()
    p_mandelbrot = Process(target=mandelbrot, args=(child_conn, x, y, plane_matrix, center,))
    p_mandelbrot.start()

    input_changed = False
    screen_changed = False
    screen_updated = False

    while loop:
        clock.tick(10)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                p_mandelbrot.kill()
                loop = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    p_mandelbrot.kill()
                    loop = False
                    break

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    if p_mandelbrot.is_alive():
                        p_mandelbrot.kill()
                    # If you zoom in the center to be rendered shifts
                    current_view = [current_view[0]*zoom_in, current_view[1]*zoom_in]
                    mouse_to_center_vec = mouse_pos_in_coord(pygame.mouse.get_pos(), current_view)
                    center += mouse_to_center_vec/abs(mouse_to_center_vec) * (1-zoom_in)
                    center_shift += mouse_to_center_vec/abs(mouse_to_center_vec) * (1-zoom_in)

                    x = [(current_view[0]*2 * x / W - current_view[0]) for x in range(W)]
                    y = [(current_view[1] - current_view[1]*2 * y / W) for y in range(H)]

                    input_changed = True
                    screen_changed = True

                if event.button == 5:
                    if p_mandelbrot.is_alive():
                        p_mandelbrot.kill()
                    current_view = [current_view[0]*zoom_out, current_view[1]*zoom_out]
                    x = [(current_view[0]*2 * x / W - current_view[0]) for x in range(W)]
                    y = [(current_view[1] - current_view[1]*2 * y / W) for y in range(H)]

                    input_changed = True
                    screen_changed = True

        if loop == False:
            break

        # Create a new mandelbrot set if it wasnt running
        if not p_mandelbrot.is_alive() and input_changed:
            input_changed = False
            p_mandelbrot = Process(target=mandelbrot, args=(child_conn, x, y, plane_matrix, center,))
            p_mandelbrot.start()

        if parent_conn.poll():
            for i, row in enumerate(parent_conn.recv()):
                for j, val in enumerate(row):
                    plane.set_at((j, i), val)
                    screen_updated = True
                    screen_changed = True


        if screen_updated:
            screen_updated = False
            center += center_shift
            center_shift = 0

        if screen_changed:
            screen_changed = False
            screen.blit(plane, (numpy.floor(current_view[0]*numpy.real(center_shift)/2 * W),
                numpy.floor(current_view[1]*numpy.imag(center_shift)/2 * H)))
            pygame.display.flip()

    p_mandelbrot.join()
    parent_conn.close()
    child_conn.close()
    pygame.quit()


if __name__=='__main__':
    main()

