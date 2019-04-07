import requests
import pygame
import os
import sys

map_params = {'ll': '58.980282,53.407158',
              'z': 10, 'l': 'map'}
z = 10
ll = [58.980282, 53.407158]
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
map_api_server = "http://static-maps.yandex.ru/1.x/"


def change_picture(map_params):
    response = requests.get(map_api_server, params=map_params)
    map_file = "map.png"

    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

    screen.blit(pygame.image.load("map.png"), (0, 0))
    pygame.display.flip()


pygame.init()
number = 0
screen = pygame.display.set_mode((600, 450))
running = True
clock = pygame.time.Clock()
fps = 60
change_picture(map_params)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                z += 1
                if z > 17:
                    z = 17
            if event.key == pygame.K_PAGEDOWN:
                z -= 1
                if z < 0:
                    z = 0
            if event.key == pygame.K_UP:
                ll[1] += 0.03 / (2 ** (z - 10))
                if ll[1] >= 85:
                    ll[1] = 85.0
            if event.key == pygame.K_DOWN:
                ll[1] -= 0.03 / (2 ** (z - 10))
                if ll[1] <= -85:
                    ll[1] = -85.0
            if event.key == pygame.K_RIGHT:
                ll[0] += 0.03 / (2 ** (z - 10))
                if ll[0] >= 175:
                    ll[0] = 175.0
            if event.key == pygame.K_LEFT:
                ll[0] -= 0.03 / (2 ** (z - 10))
                if ll[0] <= -175:
                    ll[0] = -175.0
    if z != map_params['z']:
        map_params['z'] = z
        change_picture(map_params)
    if '{},{}'.format(*ll) != map_params['ll']:
        map_params['ll'] = '{},{}'.format(*ll)
        change_picture(map_params)
    clock.tick(fps)
pygame.quit()

os.remove('map.png')
