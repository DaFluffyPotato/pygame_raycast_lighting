#!/usr/bin/python3.4
# Setup Python ----------------------------------------------- #
import pygame, sys, random, time, os, entities, shaders
from datetime import datetime
# Setup pygame/window ---------------------------------------- #
mainClock = pygame.time.Clock()
from pygame.locals import *
pygame.init()
pygame.display.set_caption('tech demo')
WINDOWWIDTH = 300
WINDOWHEIGHT = 200
screen = pygame.display.set_mode((WINDOWWIDTH*2, WINDOWHEIGHT*2),0,32)
display = pygame.Surface((WINDOWWIDTH,WINDOWHEIGHT))
# Images ----------------------------------------------------- #
tile_database = {}
tile_list = os.listdir('data/images/tiles')
not_valid = ['tilesets','Thumbs.db']
tall_tiles = ['rocks_0011.png','rocks_0110.png','rocks_0111.png']
for tile in tile_list:
    if tile not in not_valid:
        img = pygame.image.load('data/images/tiles/' + tile).convert()
        img.set_colorkey((255,255,255))
        tile_database[tile] = img.copy()
tile_list = os.listdir('data/images/tiles/tilesets')
for tile in tile_list:
    if tile not in not_valid:
        img = pygame.image.load('data/images/tiles/tilesets/' + tile).convert()
        img.set_colorkey((255,255,255))
        tile_database[tile] = img.copy()

camera_img = pygame.image.load('data/images/camera.png').convert()
camera_img.set_colorkey((255,255,255))
light_img = pygame.image.load('data/images/light_2.png').convert()
light_img.set_colorkey((0,0,0))
light_img_2 = shaders.change_light_color(light_img.copy(),(99,90,124))
light_img = shaders.change_light_color(light_img,(169,162,187))
# Functions -------------------------------------------------- #
def flip(img):
    return pygame.transform.flip(img,True,False)

def text2list(Text,Divider,intmode=False,add_end=False):
    List = []
    Current = ''
    for char in Text:
        if char != Divider:
            Current += char
        else:
            if intmode == True:
                try:
                    List.append(int(Current))
                except:
                    List.append(Current)
            else:
                List.append(Current)
            Current = ''
    if add_end == True:
        if intmode == True:
            try:
                List.append(int(Current))
            except:
                List.append(Current)
        else:
            List.append(Current)
    return List

def load_map(name):
    file = open('data/' + name + '.txt','r')
    map_data = file.read()
    file.close()
    tiles = text2list(map_data,'=')
    n = 0
    for tile in tiles:
        tiles[n] = text2list(tile,';',True)
        n += 1
    for tile in tiles:
        tile[0] = text2list(tile[0],'+')
    tile_map = {}
    spawn = [0,0]
    # left, top, right, bottom
    edges = [99999,99999,-99999,-99999]
    for tile in tiles:
        delete = []
        n = 0
        for img in tile[0]:
            if img == 'spawn.png':
                delete.append(n)
                spawn = [tile[1]*16+0,tile[2]*16+0]
            n += 1
        delete.sort(reverse=True)
        for img in delete:
            tile[0].pop(img)
        if tile[0] != []:
            tile_map[str(tile[1]) + ';' + str(tile[2])] = tile
        if tile[2]*32 > edges[3]:
            edges[3] = tile[2]*16
        if tile[2]*32 < edges[1]:
            edges[1] = tile[2]*16
        if tile[1]*32 > edges[2]:
            edges[2] = tile[1]*16
        if tile[1]*32 < edges[0]:
            edges[0] = tile[1]*16
    return tile_map, spawn, edges
# Variables -------------------------------------------------- #
decor_list = ['skull_0.png','skull_1.png']

level, spawn, edges = load_map('level')
scroll_x = spawn[0]-150
scroll_y = spawn[1]-100

player = entities.PhysicsObject(spawn[0],spawn[1],11,11)
player_grav = 0
player_slide = 0
air_time = 0
right = False
left = False
last_dir = 'r'
no_turn = 0

shader_size = 100
shader_dir = 1

jumps = 3
# Loop ------------------------------------------------------- #
while True:
    # Background --------------------------------------------- #
    display.fill((31,24,48))
    scroll_x += (player.x-150-scroll_x)/12
    scroll_y += (player.y-100-scroll_y)/12
    mx,my = pygame.mouse.get_pos()
    mx = int(mx/2)
    my = int(my/2)
    # Tiles -------------------------------------------------- #
    tile_surf = pygame.Surface((WINDOWWIDTH,WINDOWHEIGHT))
    tile_surf.set_colorkey((0,0,0))
    visible_tiles = []
    collision_tiles = []
    for y in range(15):
        for x in range(21):
            target_x = x-1 + int(scroll_x/16)
            target_y = y-1 + int(scroll_y/16)
            target = str(target_x) + ';' + str(target_y)
            if target in level:
                visible_tiles.append(level[target])
    for tile in visible_tiles:
        solid = False
        for img in tile[0]:
            if img not in decor_list:
                solid = True
            if img not in tall_tiles:
                tile_surf.blit(tile_database[img],(tile[1]*16-scroll_x,tile[2]*16-scroll_y))
            else:
                tile_surf.blit(tile_database[img],(tile[1]*16-scroll_x,tile[2]*16-1-scroll_y))
        if solid == True:
            collision_tiles.append([tile[1]*16,tile[2]*16,16,16])
    # Shaders ------------------------------------------------ #
    shader_size += shader_dir*0.4
    if shader_size > 125:
        shader_dir = -1
    if shader_size < 110:
        shader_dir = 1
    
    lights = [[[player.rect.x-int(scroll_x)+5,player.rect.y-int(scroll_y)],int(shader_size),128]]
    shader_surf = pygame.Surface((300,200))
    shaders.draw_lights(shader_surf,lights,tile_surf,light_img_2)
    shader_surf.set_colorkey((0,0,0))
    shader_surf.set_alpha(100)
    display.blit(shader_surf,(0,0))
    overlay_surf = pygame.Surface((300,200))
    shaders.draw_raw_lights(overlay_surf,lights,light_img)
    # Show Tiles --------------------------------------------- #
    display.blit(tile_surf,(0,0))
    display.blit(overlay_surf,(0,0),special_flags=BLEND_MULT)
    # Player ------------------------------------------------- #
    p_momentum = [player_slide,player_grav]
    air_time += 1
    if no_turn > 0:
        no_turn -= 1
    player_grav += 0.2
    if player_grav > 4:
        player_grav = 4
    if player_slide > 0:
        player_slide -= 0.5
        if player_slide > 2:
            player_slide = 2
    if player_slide < 0:
        player_slide += 0.5
        if player_slide < -2:
            player_slide = -2
    if no_turn == 0:
        if right == True:
            player_slide += 1
        if left == True:
            player_slide -= 1
    p_collisions = player.Move(p_momentum,collision_tiles)
    if p_collisions['bottom'] == True:
        air_time = 0
        jumps = 1
    if p_momentum[0] > 0:
        last_dir = 'r'
    elif p_momentum[0] < 0:
        last_dir = 'l'
    if last_dir == 'r':
        display.blit(camera_img,(player.rect.x-scroll_x,player.rect.y-scroll_y))
    else:
        display.blit(flip(camera_img),(player.rect.x-scroll_x,player.rect.y-scroll_y))
    # Buttons ------------------------------------------------ #
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == K_RIGHT:
                right = True
            if event.key == K_LEFT:
                left = True
            if event.key == K_UP:
                if jumps > 0:
                    jumps -= 1
                    player_grav = -4
                else:
                    if p_collisions['right'] == True:
                        player_slide = -3
                        player_grav = -4
                        no_turn = 10
                    if p_collisions['left'] == True:
                        player_slide = 3
                        player_grav = -4
                        no_turn = 10
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                right = False
            if event.key == K_LEFT:
                left = False
    # Update ------------------------------------------------- #
    screen.blit(pygame.transform.scale(display,(WINDOWWIDTH*2,WINDOWHEIGHT*2)),(0,0))
    pygame.display.update()
    mainClock.tick(40)
    
