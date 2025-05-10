import pygame
import sys
import os
import random
from PIL import Image
import math
import heapq

# Inisialisasi pygame
pygame.init()
font = pygame.font.SysFont("Arial", 22, bold=True)

# Global variabel
map_img = None
road_mask = None
kurir_img = None
bendera_img = None
kurir_pos = None
bendera_pos = None
path = []
running = False

# Konstanta warna jalan abu-abu
GRAY_RANGE = [(90, 150)] * 3

# Ukuran window default, nanti akan disesuaikan dengan ukuran map
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 800
win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Smart Kurir")

# Deteksi jalan abu-abu
def is_gray(rgb):
    return all(GRAY_RANGE[i][0] <= rgb[i] <= GRAY_RANGE[i][1] for i in range(3))

# Load semua gambar
def load_images():
    global map_img, road_mask, kurir_img, bendera_img, WINDOW_WIDTH, WINDOW_HEIGHT, win
    try:
        peta_path = os.path.expanduser("~/Downloads/peta1.png")
        kurir_path = os.path.expanduser("~/Downloads/kurir.png")
        bendera_path = os.path.expanduser("~/Downloads/bendera_merah.png")

        img = Image.open(peta_path).convert("RGB")
        road_mask = [[is_gray(img.getpixel((x, y))) for x in range(img.width)] for y in range(img.height)]
        map_img = pygame.image.load(peta_path).convert()

        # Atur ukuran jendela sesuai peta
        WINDOW_WIDTH, WINDOW_HEIGHT = img.width, img.height
        win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)

        kurir_img = pygame.image.load(kurir_path).convert_alpha()
        bendera_img = pygame.image.load(bendera_path).convert_alpha()
        print("Gambar berhasil dimuat.")
    except Exception as e:
        print("Gagal memuat gambar:", e)
        sys.exit()

# Acak posisi di jalan
def random_road_position():
    h, w = len(road_mask), len(road_mask[0])
    while True:
        x, y = random.randint(0, w - 1), random.randint(0, h - 1)
        if road_mask[y][x]:
            return x, y

# Heuristik A*
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Algoritma A*
def astar(start, goal):
    neighbors = [(0,1), (1,0), (0,-1), (-1,0)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    open_heap = []
    heapq.heappush(open_heap, (fscore[start], start))
    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
        close_set.add(current)
        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if not (0 <= neighbor[0] < len(road_mask[0]) and 0 <= neighbor[1] < len(road_mask)):
                continue
            if not road_mask[neighbor[1]][neighbor[0]]:
                continue
            tentative_gscore = gscore[current] + 1
            if neighbor in close_set and tentative_gscore >= gscore.get(neighbor, float('inf')):
                continue
            if tentative_gscore < gscore.get(neighbor, float('inf')) or neighbor not in [i[1] for i in open_heap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_gscore
                fscore[neighbor] = tentative_gscore + heuristic(neighbor, goal)
                heapq.heappush(open_heap, (fscore[neighbor], neighbor))
    return []

# Gambar tombol mewah
def draw_button(text, x, y, w, h, color, hover_color, action, icon_path=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    is_hovered = rect.collidepoint(mouse)

    scale = 1.05 if is_hovered else 1.0
    scaled_w, scaled_h = int(w * scale), int(h * scale)
    offset_x, offset_y = int((scaled_w - w) / 2), int((scaled_h - h) / 2)
    scaled_rect = pygame.Rect(x - offset_x, y - offset_y, scaled_w, scaled_h)

    shadow = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 60), shadow.get_rect(), border_radius=15)
    win.blit(shadow, (scaled_rect.x + 4, scaled_rect.y + 4))

    bg_color = hover_color if is_hovered else color
    pygame.draw.rect(win, bg_color, scaled_rect, border_radius=15)

    text_offset = 16
    label = font.render(text, True, (255, 255, 255))
    label_rect = label.get_rect(midleft=(scaled_rect.x + text_offset, scaled_rect.centery))
    win.blit(label, label_rect)

    if is_hovered and click[0] and action:
        pygame.time.delay(150)
        action()

# Tombol aksi
def btn_load_map():
    load_images()

def btn_random_kurir():
    global kurir_pos
    if road_mask:
        kurir_pos = random_road_position()

def btn_random_goal():
    global bendera_pos
    if road_mask:
        bendera_pos = random_road_position()

def btn_start():
    global path, running
    if kurir_pos and bendera_pos:
        path = astar(kurir_pos, bendera_pos)
        running = True

def btn_stop():
    global running
    running = False

# Hitung arah kurir
def get_kurir_angle():
    if not path or len(path) < 2:
        return 0
    x1, y1 = path[0]
    x2, y2 = path[1]
    angle = math.degrees(math.atan2(y1 - y2, x2 - x1))
    return angle

# Gambar semua ke layar
def draw():
    win.fill((30, 30, 30))
    if map_img:
        win.blit(map_img, (0, 0))
    if bendera_pos:
        win.blit(bendera_img, bendera_pos)
    if kurir_pos:
        rotated = pygame.transform.rotate(kurir_img, get_kurir_angle())
        rect = rotated.get_rect(center=kurir_pos)
        win.blit(rotated, rect.topleft)

    # Tombol sisi kiri
    draw_button("Load Map", 20, 20, 160, 45, (50, 90, 200), (80, 120, 240), btn_load_map)
    draw_button("Acak Kurir", 20, 80, 160, 45, (40, 150, 90), (70, 200, 120), btn_random_kurir)
    draw_button("Acak Tujuan", 20, 140, 160, 45, (200, 150, 40), (240, 180, 80), btn_random_goal)
    draw_button("Start", 20, 200, 160, 45, (200, 50, 50), (240, 80, 80), btn_start)
    draw_button("Stop", 20, 260, 160, 45, (70, 70, 70), (120, 120, 120), btn_stop)

# Loop utama
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    draw()

    if running and path:
        kurir_pos = path.pop(0)
        if not path:
            running = False

    pygame.display.update()
    clock.tick(60)
