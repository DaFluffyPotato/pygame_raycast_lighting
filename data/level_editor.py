#!/usr/bin/python3.4
tile_size = [16,16]
tall_tiles = [('rocks','0011.png'),('rocks','0110.png'),('rocks','0111.png')]
# Setup Python ----------------------------------------------- #
import pygame, sys, random, time, os
# Setup pygame/window ---------------------------------------- #
mainClock = pygame.time.Clock()
from pygame.locals import *
pygame.init()
pygame.mixer.quit()
pygame.display.set_caption('level editor')
WINDOWWIDTH = 300*2
WINDOWHEIGHT = 200*2
screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT),0,32)
Display = pygame.Surface((300,200))
# Font ------------------------------------------------------- #
basicFont = pygame.font.SysFont(None, 20)
# Images ----------------------------------------------------- #
tile_list = os.listdir('images/tiles')
tile_database = {}
not_valid = ['Thumbs.db','tilesets']
for tile in tile_list:
    if tile not in not_valid:
        img = pygame.image.load('Images/tiles/' + tile).convert()
        img.set_colorkey((255,255,255))
        tile_database[tile] = img.copy()
tileset_database = {}
tileset_list = os.listdir('images/tiles/tilesets')
tileset_types = []
for tile in tileset_list:
    if tile != 'Thumbs.db':
        img = pygame.image.load('Images/tiles/tilesets/' + tile).convert()
        img.set_colorkey((255,255,255))
        tile_type = tile[:tile.find('_')]
        tile_subtype = tile[tile.find('_')+1:]
        if tile_type not in tileset_database:
            tileset_database[tile_type] = {}
            tileset_types.append(tile_type)
        tileset_database[tile_type][tile_subtype] = img.copy()
tile_map = {}
# Audio ------------------------------------------------------ #
# Colors ----------------------------------------------------- #
SKY = (31,24,48)
# Variables -------------------------------------------------- #
Clicking = False
Removing = False
current_tile = None
Click = False
scroll_x = 0
scroll_y = 0
up = False
down = False
right = False
left = False
export = False
tile_scroll = 0
tileset_mode = False
current_tileset = None
update_tiles = 0
# Functions -------------------------------------------------- #
def Text2List(Text,Divider,intmode=False):
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
    return List

def load_map():
    file = open('in.txt','r')
    map_data = file.read()
    file.close()
    tiles = Text2List(map_data,'=')
    n = 0
    for tile in tiles:
        tiles[n] = Text2List(tile,';',True)
        n += 1
    for tile in tiles:
        tile[0] = Text2List(tile[0],'+')
    tile_map = {}
    for tile in tiles:
        tile_map[str(tile[1]) + ';' + str(tile[2])] = tile
    return tile_map
# Loop ------------------------------------------------------- #
while True:
    # Background --------------------------------------------- #
    Display.fill(SKY)
    if right == True:
        scroll_x += 4
    if left == True:
        scroll_x -= 4
    if up == True:
        scroll_y -= 4
    if down == True:
        scroll_y += 4
    # Tiles -------------------------------------------------- #
    for tile in tile_map:
        for img in tile_map[tile][0]:
            if img in tile_database:
                display_img = tile_database[img]
            else:
                display_img = tileset_database[img[0]][img[1]]
            if img not in tall_tiles:
                Display.blit(display_img,(tile_map[tile][1]*tile_size[0]-scroll_x,tile_map[tile][2]*tile_size[1]-scroll_y))
            else:
                Display.blit(display_img,(tile_map[tile][1]*tile_size[0]-scroll_x,tile_map[tile][2]*tile_size[1]-1-scroll_y))
    # GUI ---------------------------------------------------- #
    x = 0
    y = 0
    if tileset_mode == False:
        for img in tile_list:
            if img not in not_valid:
                Display.blit(pygame.transform.scale(tile_database[img],(16,16)),(x*17,y*17-tile_scroll*17))
                TileR = pygame.Rect(x*17,y*17-tile_scroll*17,16,16)
                if Click == True:
                    if MouseR.colliderect(TileR):
                        current_tile = img
                        Clicking = False
                x += 1
                if x > 2:
                    x = 0
                    y += 1
    else:
        for tile_type in tileset_types:
            Display.blit(pygame.transform.scale(tileset_database[tile_type]['0111.png'],(16,16)),(x*17,y*17-tile_scroll*17))
            TileR = pygame.Rect(x*17,y*17-tile_scroll*17,16,16)
            if Click == True:
                if MouseR.colliderect(TileR):
                    current_tileset = tile_type
                    Clicking = False
            x += 1
            if x > 2:
                x = 0
                y += 1
    # Mouse -------------------------------------------------- #
    MX,MY = pygame.mouse.get_pos()
    MX = int(MX/2)
    MY = int(MY/2)
    MouseR = pygame.Rect(MX,MY,2,2)
    MX = int(round((scroll_x+MX-10)/tile_size[0],0))
    MY = int(round((scroll_y+MY-10)/tile_size[1],0))
    if tileset_mode == False:
        if current_tile != None:
            if current_tile[:5] not in tall_tiles:
                Display.blit(tile_database[current_tile],(MX*tile_size[0]-scroll_x,MY*tile_size[1]-scroll_y))
            else:
                Display.blit(tile_database[current_tile],(MX*tile_size[0]-scroll_x,MY*tile_size[1]-1-scroll_y))
            if Clicking == True:
                loc = str(MX) + ';' + str(MY)
                if loc not in tile_map:
                    tile_map[loc] = [[current_tile],MX,MY]
                elif current_tile not in tile_map[loc][0]:
                    tile_map[loc][0].append(current_tile)
    else:
        if current_tileset != None:
            Display.blit(tileset_database[current_tileset]['1111.png'],(MX*tile_size[0]-scroll_x,MY*tile_size[1]-scroll_y))
            if Clicking == True:
                loc = str(MX) + ';' + str(MY)
                if loc not in tile_map:
                    tile_map[loc] = [[(current_tileset,'1111.png')],MX,MY]
                else:
                    found = False
                    for img in tile_map[loc][0]:
                        if img not in tile_database:
                            if img[0] == current_tileset:
                                found = True
                    if found == False:
                        tile_map[loc][0].append((current_tileset,'1111.png'))
    if Removing == True:
        loc = str(MX) + ';' + str(MY)
        if loc in tile_map:
            del tile_map[loc]
    # Buttons ------------------------------------------------ #
    Click = False
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == ord('u'):
                update_tiles = 2
            if event.key == ord('t'):
                if tileset_mode == True:
                    tileset_mode = False
                else:
                    tileset_mode = True
            if event.key == ord('a'):
                left = True
            if event.key == ord('d'):
                right = True
            if event.key == ord('w'):
                up = True
            if event.key == ord('s'):
                down = True
            if event.key == ord('e'):
                export = True
            if event.key == ord('i'):
                tile_map = load_map()
        if event.type == KEYUP:
            if event.key == ord('a'):
                left = False
            if event.key == ord('d'):
                right = False
            if event.key == ord('w'):
                up = False
            if event.key == ord('s'):
                down = False
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                Clicking = True
                Click = True
            if event.button == 3:
                Removing = True
            if event.button == 4:
                tile_scroll -= 1
            if event.button == 5:
                tile_scroll += 1
        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                Clicking = False
            if event.button == 3:
                Removing = False
    # Update Tiles ------------------------------------------- #
    for i in range(update_tiles):
        directions = [(0,-1),(1,0),(0,1),(-1,0)]
        for tile in tile_map:
            i_num = 0
            for img in tile_map[tile][0]:
                if img not in tile_database:
                    found = ['0','0','0','0']
                    tile_types_found = []
                    n = 0
                    for direction in directions:
                        test_str = str(tile_map[tile][1]+direction[0]) + ';' + str(tile_map[tile][2]+direction[1])
                        if test_str in tile_map:
                            for img2 in tile_map[test_str][0]:
                                if img2 not in tile_database:
                                    if img2[0] == img[0]:
                                        found[n] = '1'
                                        tile_types_found.append(img2[1])
                        if len(tile_types_found) <= n:
                            tile_types_found.append(None)
                        n += 1
                    f_copy = found.copy()
                    found = ''
                    switch = None
                    if (tile_types_found[0] in ['1110.png','0110.png']) and (tile_types_found[3] in ['0111.png','0110.png']):
                        switch = 'corner_0.png'
                    if (tile_types_found[0] in ['1011.png','0011.png']) and (tile_types_found[1] in ['0111.png','0011.png']):
                        switch = 'corner_1.png'
                    if (tile_types_found[2] in ['1110.png','1100.png']) and (tile_types_found[3] in ['1101.png','1100.png']):
                        switch = 'corner_2.png'
                    if (tile_types_found[1] in ['1101.png','1001.png']) and (tile_types_found[2] in ['1011.png','1001.png']):
                        switch = 'corner_3.png'
                    for char in f_copy:
                        found += char
                    if switch == None:
                        if found + '.png' in tileset_database[img[0]]:
                            tile_map[tile][0][i_num] = (img[0],found + '.png')
                    else:
                        if switch in tileset_database[img[0]]:
                            tile_map[tile][0][i_num] = (img[0],switch)
                i_num += 1
    update_tiles = 0
    # Export ------------------------------------------------- #
    if export == True:
        export = False
        export_str = ''
        for tile in tile_map:
            for img in tile_map[tile][0]:
                if img in tile_database:
                    export_str += img + '+'
                else:
                    export_str += img[0] + '_' + img[1] + '+'
            export_str += ';' + str(tile_map[tile][1]) + ';' + str(tile_map[tile][2]) + ';='
        file = open('export.txt','w')
        file.write(export_str)
        file.close()
    # Update ------------------------------------------------- #
    screen.blit(pygame.transform.scale(Display,(300*2,200*2)),(0,0))
    pygame.display.update()
    mainClock.tick(40)
    
