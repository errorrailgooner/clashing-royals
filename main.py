import pygame
import time
import math
import socket
import threading
import random
import string
import ipaddress
import concurrent.futures
import os

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
placeholder = pygame.transform.scale(pygame.image.load("main/cards/placeholder.png"), (60, 70))
pygame.font.init()
font = pygame.font.SysFont("arial", 30)
small_font = pygame.font.SysFont("arial", 16)

win.fill((255, 255, 255))
win.blit(logo, (0, 0))
pygame.display.update()
time.sleep(2)
for img in [tenpercent, fivepercent, sevenpercent, onepercent]:
    win.fill((255, 255, 255))
    win.blit(img, (0, 0))
    pygame.display.update()
    time.sleep(0.2)

HOST = "0.0.0.0"
PORT = 6767
connected = False
is_host = False
conn = None
addr = None
game_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def get_local_network():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        network = ipaddress.ip_network(f"{local_ip}/24", strict=False)
        print(f"Scanning network: {network}")
        return network
    except Exception as e:
        print(f"Error determining network: {e}")
        return None

def try_connect_to_ip(ip):
    global game_id
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((str(ip), PORT))
        s.sendall(b"HELLO")
        response = s.recv(1024)
        if response.startswith(b"HELLO:"):
            game_id = response.decode().split(":")[1]
            print(f"Valid connection to {ip}, Game ID: {game_id}")
            return s, ip
        else:
            print(f"Invalid response from {ip}")
            s.close()
            return None, ip
    except Exception as e:
        s.close()
        return None, ip

def scan_network():
    global conn, connected, is_host, addr
    network = get_local_network()
    if not network:
        print("No network found, starting server")
        start_server()
        return
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_ip = {executor.submit(try_connect_to_ip, ip): ip for ip in network.hosts()}
        for future in concurrent.futures.as_completed(future_to_ip):
            result, ip = future.result()
            if result:
                conn = result
                connected = True
                is_host = False
                addr = (str(ip), PORT)
                print(f"Successfully connected to {ip}")
                return
    print("No valid connections found, starting server")
    start_server()

def start_server():
    global conn, addr, connected, is_host
    is_host = True
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("0.0.0.0", PORT))
        s.listen(1)
        print(f"Server listening on port {PORT}")
        conn, addr = s.accept()
        hello_msg = conn.recv(1024)
        if hello_msg == b"HELLO":
            conn.sendall(f"HELLO:{game_id}".encode())
            connected = True
            print(f"Server connected to {addr}, Game ID: {game_id}")
        else:
            print("Invalid handshake")
            conn.close()
    except Exception as e:
        print(f"Server error: {e}")
        s.close()

def battle_search():
    clock = pygame.time.Clock()
    angle = 0
    radius = 100
    text = font.render("searching for battle", True, (0, 0, 0))
    text_rect = text.get_rect(center=(318 // 2, 529 // 2))
    running = True
    threading.Thread(target=scan_network, daemon=True).start()
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
            game_screen()
            return
        clock.tick(60)
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            cancel_rect = pygame.Rect(10, 10, cancel.get_width(), cancel.get_height())
            if cancel_rect.collidepoint(mouse_pos):
                running = False
                pygame.display.update()

def game_screen():
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        win.fill((255, 255, 255))
        
        game_id_text = small_font.render(f"Game ID: {game_id}", True, (0, 0, 0))
        win.blit(game_id_text, (318 - game_id_text.get_width() - 10, 10))
        
        pygame.draw.rect(win, (128, 128, 128), (0, 445, 318, 84))
        pygame.draw.rect(win, (0, 0, 0), (0, 445, 318, 84), 4)
        
        card_positions = [20, 83, 146, 209, 272]
        for i, x_pos in enumerate(card_positions):
            pygame.draw.rect(win, (0, 0, 0), (x_pos, 450, 60, 70), 3)
            win.blit(placeholder, (x_pos, 450))
        
        pygame.display.update()
        clock.tick(60)

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
