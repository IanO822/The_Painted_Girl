# -*- coding: utf-8 -*-
import os
import sys
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import random
import math
import datetime
import time
import numpy as np
import copy

#基本定義
FPS = 60
WIDTH = 960
HEIGHT = 540
GRAVITY = 10
GROUND = 450
LORE_WIDTH = 500
LORE_HEIGHT = 500
#顏色
BLACK = 0, 0, 0
WHITE = 255, 255, 255
YELLOW = 255, 255, 0
GREEN = 0, 255, 0
DGREEN = 0, 120, 0
RED = 255, 0, 0
LBLUE = 152, 245, 255
BLUE = 30, 144, 255
CYAN = 32, 178, 170
TEAL = 0, 160, 160
GOLD = 255, 215, 0
DGRAY = 105, 105, 105
GRAY = 192, 192, 192
LGRAY = 119, 136, 153
AGRAY = 64, 64, 64
BGRAY = 100, 100, 100
IGRAY = 80, 84, 92
PURPLE = 148, 0, 211
DCGRAY = 49, 51, 56
BACKGROUND_COLOR = 0, 255, 0
#稀有度顏色
COMMON = (195, 195, 195)
UNCOMMON = (181, 230, 29)
RARE = (0, 162, 232)
EPIC = (152, 70, 151)
LEGENDARY = (255, 127, 39)
#天空顏色
SKY_BACKBROUND = (0, 0, 255)
DAY_COLOR = (167, 236, 255)   # 白天（淺藍）
AFTERNOON_COLOR = (70, 130, 180) # 下午（藍）
DUSK_COLOR = (255, 140, 30)   # 黃昏/晨曦（橘紅）
NIGHT_COLOR = (25, 25, 112)   # 夜晚（深藍）
MIDNIGHT_COLOR = (0, 0, 0)
SKY_BACKGROUND = (0, 0, 255)
SUN_COLOR = (255, 204, 0)     # 太陽（黃色）
MOON_COLOR = (255, 255, 255)  # 月亮（白色
#時間
DAWN = [5, 7]
DAY = [7, 11]
NOON = [11, 16]
AFTERNOON = [16, 17]
DUSK = [17, 19]
NIGHT = [19, 24]
MIDNIGHT = [0, 5]

#建立視窗
pygame.init()
try:
    pygame.mixer.init()
except:
    None
#全螢幕
FULLSCREEN = True

if FULLSCREEN:
    info = pygame.display.Info()
    SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
    display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME) #pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    scale = min(SCREEN_WIDTH / WIDTH, SCREEN_HEIGHT / HEIGHT)
    screen = pygame.Surface((WIDTH, HEIGHT))
else:
    SCREEN_WIDTH, SCREEN_HEIGHT = WIDTH, HEIGHT
    scale = 1
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
new_width = int(WIDTH * scale)
new_height = int(HEIGHT * scale)
x_offset = (SCREEN_WIDTH - new_width) // 2
y_offset = (SCREEN_HEIGHT - new_height) // 2
#標題
pygame.display.set_caption("The Painted Girl")
#pygame.display.set_icon(pygame.image.load(os.path.join("resource", "Finding The Light Logo.png")).convert_alpha())
clock = pygame.time.Clock()
now = datetime.datetime.now()

#圖片
def import_img(img_name, removeBG=True, scale=1):
    img = pygame.image.load(os.path.join("resource", img_name + ".png")).convert()
    if removeBG:
        img.set_colorkey(BACKGROUND_COLOR)
    # 等比縮放
    if scale != 1:
        w, h = img.get_size()
        img = pygame.transform.scale(img, (int(w * scale), int(h * scale)))

    return img

#角色
player_imgs = {}
agent_imgs = {}

for i in range(3):
    player_imgs.update({i+1:import_img("player_"+ str(i+1), True, 0.2)})
    agent_imgs.update({i+1:import_img("agent_"+ str(i+1))})

#物件
car_img = import_img("car", True, 2.5)
lamp_1_img = import_img("lamp", True, 1)
lamp_2_img = import_img("lamp_", True, 1)
grass_img = import_img("grass", True, 1)

#背景
area_background_imgs = {}
for i in range(4):
    area_background_imgs.update({str(i):import_img("area_" + str(i))})

#按鈕
empty_button_img = import_img("empty_button") 

#字體
text_font = os.path.join("resource", "font.ttf")
text_font_2 = os.path.join("resource", "font2.ttf")

#畫出圖片
def draw_img(surf, img, x, y):
    if type(img) != int:
        img_rect = img.get_rect()
        img_rect.x = x
        img_rect.y = y
        surf.blit(img, img_rect)

#顯示文字
def draw_color_text(surf, text, size, x, y, color):
    font = pygame.font.Font(text_font_2, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

#外框字
def outline_text(text, size, x, y, color):
    font = pygame.font.Font(text_font_2, size)
    base = font.render(str(text), True, BLACK)  # 渲染外框
    outline = pygame.Surface((base.get_width() + 4, base.get_height() + 4), pygame.SRCALPHA)
    text_surface = font.render(str(text), True, color)  # 渲染主文字
    # 繪製外框 (上下左右四個方向)
    for dx in [-2, 2]:
        for dy in [-2, 2]:
            outline.blit(base, (dx + 2, dy + 2))
    # 中心繪製主文字
    outline.blit(text_surface, (2, 2))
    screen.blit(outline, (x, y))

#修正座標
def fixed_coord_x(coord_x):
    return player.rect.x - (Player_location.coord_x - coord_x)

#偵測鼠標懸停(長方形)
def is_hovering(x1, x2, y1, y2, mouse_x = 0, mouse_y = 0, mouse_icon = ""):
    if x1 < Mouse.x < x2 and y1 < Mouse.y < y2 and mouse_icon:
        outline_text(mouse_icon, 30, Mouse.x, Mouse.y - 10, RED)
    return x1 < Mouse.x < x2 and y1 < Mouse.y < y2

#偵測鼠標懸停(圓形)
def is_hovering_circle(x, y, radius, mouse_x = 0, mouse_y = 0):
    return abs(Mouse.x - x) ** 2 + abs(Mouse.y - y) ** 2 <= radius ** 2

#NPC
def summon_npc(coord_x, y, interactions, name, img, name_color = LBLUE):
    coord_x = fixed_coord_x(coord_x)
    if name:
        draw_color_text(screen,f"[{name}]", 20, coord_x, y - 40 , name_color)
    draw_img(screen, img, coord_x - img.get_width() / 2, y)
    if abs(player.rect.x - (coord_x + 80 - img.get_width() / 2)) <= 80:
        y_move = 0
        for option, action in interactions.items():
            y_move += 60
            draw_img(screen, empty_button_img, coord_x + 50, y - 50 + y_move)
            draw_color_text(screen, option, 30, coord_x + 125, y - 45 + y_move, WHITE)
            press_button = pygame.mouse.get_pressed()
            if is_hovering(coord_x + 50, coord_x + 200, y - 50 + y_move, y + y_move, Mouse.x, Mouse.y):
                pygame.draw.rect(screen, WHITE, (coord_x + 50, y - 50 + y_move, 150, 50), 3)
                if press_button[0]:
                    return option, action

#滾動式背景
def scrolling_background(first_load = False):
    global background_backward_img, background_img, background_forward_img, player_move_count_temp
    #初次執行
    if first_load:
        Areas.changed = True
        global background_location_x, background_location_y
        background_location_x = 0
        background_location_y = 0
        player_move_count_temp = 0
    #檢測更換區域
    new_area = (Player_location.coord_x // 900) + 1
    if Areas.area != new_area:
        Areas.area = new_area
        Areas.lock_right = False
        Areas.lock_left = False
        Areas.changed = True
    #特殊區域
    Areas.special_area = ""
    #導入背景圖片 前/中/後
    Areas.area = int(Areas.area)
    if Areas.area < Areas.areas and Areas.changed and not Areas.lock_right:
        background_forward_img = area_background_imgs[str(Areas.area + 1)]
    if Areas.area < Areas.areas and Areas.changed:
        background_img = area_background_imgs[str(Areas.area) + Areas.special_area]
    if Areas.changed and not Areas.lock_left:
        background_backward_img = area_background_imgs[str(Areas.area - 1)]
    Areas.changed = False
    #當前區域座標
    global current_coord_x
    current_coord_x = Player_location.coord_x - (Areas.area - 1) * 900
    player_move_count_temp = Player_location.coord_x
    #計算背景位置
    if (Areas.lock_left and current_coord_x <= 450) or (Areas.lock_right and current_coord_x >= 450) or (Areas.lock_left and Areas.lock_right):
        background_location_x = 0
        Player_location.player_move = True
        player.rect.x = current_coord_x
    elif ((Areas.lock_left and current_coord_x > 450) or (Areas.lock_right and current_coord_x < 450) or (Areas.lock_right == False and Areas.lock_left == False)) and not (Areas.lock_left and Areas.lock_right):
        background_location_x = -(Player_location.coord_x - ((Areas.area - 1) * 900) - 450 - Player_location.background_moving)
        Player_location.player_move = False
        player.rect.x = 450

    #畫出背景
    #下一個區域
    if background_location_x < 0 and Areas.lock_right == False and current_coord_x > 450:
        draw_img(screen, background_forward_img, background_location_x + 900, background_location_y)
    #當前區域
    draw_img(screen, background_img, background_location_x, 0)
    #上一個區域
    if background_location_x > 0 and Areas.lock_left == False and current_coord_x < 500:
        draw_img(screen, background_backward_img, background_location_x - 900, 0)

#傳送
def teleport(coord_x, coord_y = None):
    Player_location.coord_x = coord_x
    if coord_y != None:
        player.rect.y = coord_y
player_name = "Player"

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.name = player_name
        self.image = empty_button_img
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = GROUND - 180
        self.facing = 1
        self.speed = 1
        self.jump_time = 0
        self.jump_height = 0
        self.fall_speed = 1
        self.velocity = 0
        self.image_frame = 1
        self.moving_tick = 0
    
    def update(self):
        if self.moving_tick % 15 == 0:
            self.image_frame += 1
            if self.image_frame > 3:
                self.image_frame = 2
        self.image = pygame.transform.flip(player_imgs[self.image_frame], self.facing == -1, False)
        key_pressed = pygame.key.get_pressed()
        #移動
        self.move_distant = max(self.speed, 0)
        if key_pressed[pygame.K_d] and Player_location.disable_move == False and Player_location.dash_distance == 0:
            self.facing = 1
            if player.rect.right + self.move_distant <= WIDTH: Player_location.x_move += self.move_distant
            self.moving_tick += 1
        elif key_pressed[pygame.K_a] and Player_location.disable_move == False and Player_location.dash_distance == 0:
            self.facing = -1
            if player.rect.left - self.move_distant >= 0: Player_location.x_move -= self.move_distant
            self.moving_tick += 1
        else:
            self.image_frame = 1

#玩家位置
class Player_location:
    def __init__(self):
        self.x_move = 0
        self.disable_move = False
        self.disable_jump = False
        self.disable_ground = False
        self.x = 0
        self.y = 0
        self.coord_x = 0
        self.coord_y = 0
        self.anti_gravity = False
        self.dash_distance = 0
        self.midair_dash = 0
        self.mouse = False
        self.background_moving = 0
        self.player_move = False

#區域
class Areas():
    def __init__(self):
        self.object = {}
        self.area = 0
        self.areas = 0
        self.spawnpoint = 0
        self.switch = False
        self.spawn = False
        self.use = False
        self.cleared = {}
        self.first = {}
        self.lootchest = {}
        self.mob_killed = {}
        self.lock_right = False
        self.lock_left = False
        self.regen_lock = False
        self.safe = False
        self.changed = True
        self.special_area = ""

#滑鼠
class Mouse():
    def __init__(self):
        self.x = 0
        self.y = 0

#除錯資訊
class Info():
    def __init__(self):
        self.open = False

all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

Player_location.x_move = 0
Player_location.disable_move = False
Player_location.disable_jump = False
Player_location.anti_gravity = False
Player_location.disable_ground = False
Player_location.dash_distance = 0
Player_location.midair_dash = 0
Player_location.x = 0
Player_location.y = 0
Player_location.coord_x = 0
Player_location.coord_y = 0
Player_location.background_moving = 0
Player_location.player_move = False

Areas.area = 1
Areas.areas = 3
Areas.spawn = True
Areas.use = False
Areas.lock_right = False
Areas.lock_left = True
Areas.changed = True

Mouse.x = 0
Mouse.y = 0

Info.open = False

first_time_load_scrolling_background = True

running = True

while running:
    clock.tick(FPS)
    # 取得游標位置
    Mouse.x, Mouse.y = pygame.mouse.get_pos()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    Mouse.x = (mouse_x - x_offset) / scale
    Mouse.y = (mouse_y - y_offset) / scale
    
    # **縮放並繪製到全螢幕視窗**
    if FULLSCREEN:
        scaled_surface = pygame.transform.smoothscale(screen, (new_width, new_height))
        display.fill((0, 0, 0))  # 填充黑邊
        display.blit(scaled_surface, (x_offset, y_offset))
    
    # **清空畫布**
    screen.fill(BACKGROUND_COLOR)

    # 滾動式背景
    Player_location.coord_x += Player_location.x_move
    Player_location.x_move = 0
    scrolling_background(first_time_load_scrolling_background)
    first_time_load_scrolling_background = False

    # 取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                Areas.use = True  # 使用
            if event.key == pygame.K_F3:#角色屬性
                if Info.open == False:
                    Info.open = True
                else:
                    Info.open = False

    if Info.open:
        #顯示座標資訊
        draw_color_text(screen, "座標: " + str(Player_location.coord_x // 10), 20, 50, 300, BLACK)
        draw_color_text(screen, "背景: " + str(background_location_x // 10), 20, 50, 330, BLACK)
        draw_color_text(screen, "區域: " + str(Areas.area), 20, 50, 360, BLACK)
        draw_color_text(screen, "區域座標: " + str(current_coord_x), 20, 50, 390, BLACK)
        if Areas.lock_left:draw_color_text(screen, "邊界:左邊", 20, 50, 420, BLACK)
        if Areas.lock_right:draw_color_text(screen, "邊界:右邊", 20, 50, 450, BLACK)

    summon_npc(300, 50, {}, "", lamp_1_img, "WHITE")
    summon_npc(600, 50, {}, "", lamp_1_img, "WHITE")
    summon_npc(900, 50, {}, "", lamp_1_img, "WHITE")
    summon_npc(0, 220, {}, "", grass_img)
    summon_npc(960, 220, {}, "", grass_img)
    summon_npc(500, 250, {}, "", car_img)
    # 在這裡畫角色、NPC 等遊戲內容
    all_sprites.update()
    all_sprites.draw(screen)
    dark_overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)  # 建立具透明通道的Surface
    dark_overlay.fill((0, 0, 0, 128))  # RGB(0,0,0)，透明度128（約為50%不透明）
    screen.blit(dark_overlay, (0, 0))

    if Areas.area == 1:
        Areas.lock_left = True
    if Areas.area == 3:
        Areas.lock_right = True

    pygame.display.flip()

pygame.quit()