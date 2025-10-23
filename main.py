import pygame
import time
import math
import socket
import threading
import random
import string

HOST = "0.0.0.0"
PORT = 6767

def random_string(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

connection_result = {
    'connected': False,
    'role': None,
    'id': None,
    'peer_addr': None,
}

def get_local_ipv4():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = None
    finally:
        s.close()
    return ip

def scan_and_connect_full_subnet(port=PORT, timeout_per_try=0.25):
    local_ip = get_local_ipv4()
    if not local_ip:
        local_ip = "127.0.0.1"
    parts = local_ip.split('.')
    if len(parts) != 4:
        base = "192.168.1"
        own_last = 1
    else:
        base = '.'.join(parts[:3])
        own_last = int(parts[3])
    for i in range(1, 255):
        if i == own_last:
            continue
        ip = f"{base}.{i}"
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout_per_try)
            err = s.connect_ex((ip, port))
            if err == 0:
                try:
                    s.settimeout(3.0)
                    data = s.recv(1024)
                    if data:
                        shared_id = data.decode(errors='ignore').strip()
                    else:
                        shared_id = None
                    connection_result['connected'] = True
                    connection_result['role'] = 1
                    connection_result['id'] = shared_id or random_string()
                    connection_result['peer_addr'] = (ip, port)
                    s.close()
                    return
                except Exception:
                    try:
                        s.close()
                    except Exception:
                        pass
            else:
                s.close()
        except Exception:
            try:
                s.close()
            except Exception:
                pass
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        listener.bind((HOST, port))
        listener.listen(1)
        shared_id = random_string()
        try:
            conn, addr = listener.accept()
            try:
                conn.sendall(shared_id.encode())
            except Exception:
                pass
            finally:
                try:
                    conn.close()
                except Exception:
                    pass
            connection_result['connected'] = True
            connection_result['role'] = 0
            connection_result['id'] = shared_id
            connection_result['peer_addr'] = addr
        except Exception:
            connection_result['connected'] = False
    except Exception:
        connection_result['connected'] = False
    finally:
        try:
            listener.close()
        except Exception:
            pass

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
win.fill((255, 255, 255))
win.blit(tenpercent, (0, 0))
pygame.display.update()
time.sleep(0.1)
win.fill((255, 255, 255))
win.blit(fivepercent, (0, 0))
pygame.display.update()
time.sleep(0.3)
win.fill((255, 255, 255))
win.blit(sevenpercent, (0, 0))
pygame.display.update()
time.sleep(0.5)
win.fill((255, 255, 255))
win.blit(onepercent, (0, 0))
pygame.display.update()

def show_connected_screen(role, shared_id):
    win.fill((255, 255, 255))
    role_text = font.render(str(role), True, (0, 0, 0))
    id_text = font.render(str(shared_id), True, (0, 0, 0))
    role_rect = role_text.get_rect(center=(159, 200))
    id_rect = id_text.get_rect(center=(159, 250))
    win.blit(role_text, role_rect)
    win.blit(id_text, id_rect)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        pygame.time.delay(50)

def battle_search():
    scanner_thread = threading.Thread(target=scan_and_connect_full_subnet, daemon=True)
    scanner_thread.start()
    clock = pygame.time.Clock()
    angle = 0
    radius = 100
    text = font.render("searching for battle", True, (0, 0, 0))
    text_rect = text.get_rect(center=(318 // 2, 529 // 2))
    running = True
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
        clock.tick(60)
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            cancel_rect = pygame.Rect(10, 10, cancel.get_width(), cancel.get_height())
            if cancel_rect.collidepoint(mouse_pos):
                running = False
                pygame.display.update()
                return
        if connection_result.get('connected'):
            sid = connection_result.get('id') or random_string()
            role = connection_result.get('role', 1)
            show_connected_screen(role, sid)
            running = False
            return

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
        print("battle started")
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
