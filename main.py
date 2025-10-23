import pygame
import time
import math
import socket
import threading
import random
import string

pygame.init()
win = pygame.display.set_mode((318, 529))
pygame.display.set_caption("clashing royals")

logo = pygame.image.load("supercell.png")
tenpercent = pygame.image.load("logo10percent.png")
fivepercent = pygame.image.load("logo50percent.png")
sevenpercent = pygame.image.load("logo75percent.png")
onepercent = pygame.image.load("logo100percent.png")
cards = pygame.transform.scale(pygame.image.load("cards.png"), (75, 75))
swords = pygame.transform.scale(pygame.image.load("swords.png"), (75, 75))
battle = pygame.transform.scale(pygame.image.load("battle.png"), (180, 80))
mag = pygame.image.load("movingimage.png")
cancel = pygame.image.load("cancel.png")
pygame.font.init()
font = pygame.font.SysFont("arial", 30)

win.fill((255, 255, 255))
win.blit(logo, (0, 0))
pygame.display.update()
time.sleep(2)
for img in [tenpercent, fivepercent, sevenpercent, onepercent]:
    win.fill((255, 255, 255))
    win.blit(img, (0, 0))
    pygame.display.update()
    time.sleep(0.2)

HOST = ""
PORT = 6767
connected = False
is_host = False
conn = None
addr = None
random_text = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def try_connect():
    global conn, connected, is_host
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect(("127.0.0.1", PORT))
        conn = s
        connected = True
        is_host = False
    except:
        s.close()
        start_server()

def start_server():
    global conn, addr, connected, is_host
    is_host = True
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    connected = True

def battle_search():
    clock = pygame.time.Clock()
    angle = 0
    radius = 100
    text = font.render("searching for battle", True, (0, 0, 0))
    text_rect = text.get_rect(center=(318 // 2, 529 // 2))
    running = True
    threading.Thread(target=try_connect, daemon=True).start()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        win.fill((255, 255, 255))
        win.blit(text, text_rect)
        mag_x = text_rect.centerx + math.cos(math.radians(angle)) * radius
        mag_y = text_rect.centery + math.sin(math.radians(angle)) * radius
        win.blit(mag, (mag_x - mag.get_width() // 2, mag_y - mag.get_height() // 2))
        angle += 2
        if angle >= 360:
            angle -= 360
        win.blit(cancel, (10, 10))
        pygame.display.update()
        if connected:
            show_connected_screen()
            return
        clock.tick(60)
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            cancel_rect = pygame.Rect(10, 10, cancel.get_width(), cancel.get_height())
            if cancel_rect.collidepoint(mouse_pos):
                running = False
                pygame.display.update()

def show_connected_screen():
    win.fill((255, 255, 255))
    role = "0" if is_host else "1"
    role_text = font.render(role, True, (0, 0, 0))
    txt = font.render(random_text, True, (0, 0, 0))
    win.blit(role_text, (150, 200))
    win.blit(txt, (100, 250))
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

def main():
    clock = pygame.time.Clock()
    handled = False
    pygame.draw.rect(win, (255, 255, 255), (0, 0, 318, 529))
    pygame.draw.rect(win, (128, 128, 128), (0, 445, 318, 529))
    pygame.draw.rect(win, (0, 0, 0), (0, 445, 318, 529), 4)
    pygame.draw.rect(win, (0, 0, 0), (80, 447, 80, 80), 5)
    pygame.draw.rect(win, (0, 0, 0), (155, 447, 80, 80), 5)
    win.blit(cards, (80, 450))
    win.blit(swords, (155, 450))
    win.blit(battle, (75, 200))
    r = pygame.Rect(75, 200, battle.get_width(), battle.get_height())
    if pygame.mouse.get_pressed()[0] and r.collidepoint(pygame.mouse.get_pos()) and not handled:
        battle_search()
        handled = True
    elif not pygame.mouse.get_pressed()[0]:
        handled = False
    pygame.display.update()
    clock.tick(60)

while True:
    main()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
