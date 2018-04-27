import pygame, math
from pygame.locals import *

def polygon_points(center,radius,sides):
    points = []
    rot = 0
    increment = 360/sides
    for i in range(sides):
        dx = math.cos(math.radians(rot))
        dy = math.sin(math.radians(rot))
        points.append([center[0]+dx*radius,center[1]+dy*radius])
        rot += increment
    return points

global raycast_sensitivity
raycast_sensitivity = 6 # higher is less sensitive

def change_light_color(image,color):
    color_surf = pygame.Surface((image.get_width(),image.get_height()))
    color_surf.fill(color)
    image.blit(color_surf,(0,0),special_flags=BLEND_MULT)
    return image

def raycast(start,end,surf):
    dif_x = end[0]-start[0]
    dif_y = end[1]-start[1]
    t = abs(dif_x)+abs(dif_y)
    inc_x = dif_x/t
    inc_y = dif_y/t
    main_inc = [inc_x*raycast_sensitivity,inc_y*raycast_sensitivity]
    current = [start[0],start[1]]
    i = 0
    broken = False
    while i < t/raycast_sensitivity:
        try:
            if surf.get_at((int(current[0]),int(current[1]))) != (0,0,0):
                broken = True
                break
        except IndexError:
            pass
        current[0] += main_inc[0]
        current[1] += main_inc[1]
        i += 1
    if broken == False:
        current = end
    for i in range(raycast_sensitivity*4):
        try:
            if surf.get_at((int(current[0]),int(current[1]))) == (0,0,0):
                break
        except IndexError:
            pass
        current[0] -= inc_x*0.25
        current[1] -= inc_y*0.25
    if broken == True:
        current[0] += inc_x*2
        current[1] += inc_y*2
    return current

def light_outline(loc,radius,density,collision_surf,reset_pos=True):
    top_left = [loc[0]-radius,loc[1]-radius]
    points = polygon_points(loc,radius,density)
    n = 0
    for point in points:
        points[n] = raycast((loc[0],loc[1]),point,collision_surf)
        n += 1
    if reset_pos == True:
        for point in points:
            point[0] -= top_left[0]
            point[1] -= top_left[1]
    return points

def light_image(light,collision_surf,light_img):
    surf = pygame.Surface((light[1]*2,light[1]*2))
    points = light_outline((light[0][0],light[0][1]),light[1],light[2],collision_surf)
    pygame.draw.polygon(surf,(255,255,255),points)
    surf.set_colorkey((255,255,255))
    light_surf = pygame.transform.scale(light_img,(light[1]*2,light[1]*2))
    light_surf.blit(surf,(0,0))
    light_surf.set_colorkey((0,0,0))
    return light_surf

def raw_light_image(light,light_img):
    light_surf = pygame.transform.scale(light_img,(light[1]*2,light[1]*2))
    light_surf.set_colorkey((0,0,0))
    return light_surf

def draw_lights(surf,lights,collision_surf,light_img):
    for light in lights:
        surf.blit(light_image(light,collision_surf,light_img),(light[0][0]-light[1],light[0][1]-light[1]),special_flags=BLEND_ADD)

def draw_raw_lights(surf,lights,light_img):
    for light in lights:
        surf.blit(raw_light_image(light,light_img),(light[0][0]-light[1],light[0][1]-light[1]),special_flags=BLEND_ADD)

def generate_light_map(surf,lights,collision_surf):
    s = surf.copy()
    for light in lights:
        points = light_outline((light[0][0],light[0][1]),light[1],light[2],collision_surf,False)
        pygame.draw.polygon(s,(255,255,255),points)
    return s
    
