import pygame
import random
import math
import heapq

def bezier_curve(t, p0, p1, p2, p3):
    return (
        (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0],
        (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1]
    )

def draw_road(grid, p0, p1, p2, p3, road_color, road_width, line_color, road_points):
    for t in range(200):
        t /= 200.0
        x, y = bezier_curve(t, p0, p1, p2, p3)
        road_points.append((int(x), int(y)))
        pygame.draw.circle(grid, road_color, (int(x), int(y)), road_width // 2)
    
    for j in range(0, len(road_points) - 10, 20):
        x1, y1 = road_points[j]
        x2, y2 = road_points[j + 10]
        pygame.draw.line(grid, line_color, (x1, y1), (x2, y2), 2)

def generate_map(width, height):
    grid = pygame.Surface((width, height))
    grid.fill((128, 128, 128))  
    
    road_color = (50, 50, 50)
    road_width = 30
    line_color = (255, 255, 255)
    
    road_points = []
    p0 = (0, random.randint(100, height - 100))
    p3 = (width, random.randint(100, height - 100))
    p1 = (width // 3, random.randint(100, height - 100))
    p2 = (2 * width // 3, random.randint(100, height - 100))
    draw_road(grid, p0, p1, p2, p3, road_color, road_width, line_color, road_points)
    
    vertical_road_points = []
    p0 = (random.randint(100, width - 100), 0)
    p3 = (random.randint(100, width - 100), height)
    p1 = (random.randint(100, width - 100), height // 3)
    p2 = (random.randint(100, width - 100), 2 * height // 3)
    draw_road(grid, p0, p1, p2, p3, road_color, road_width, line_color, vertical_road_points)
    
    return grid, road_points + vertical_road_points

def find_nearest_point(road_points, pos):
    return min(road_points, key=lambda p: math.dist(p, pos))

def main():
    pygame.init()
    width, height = 600, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Dynamic Road Generator")
    
    grid, road_points = generate_map(width, height)
    button_font = pygame.font.Font(None, 36)
    
    buttons = {
        "ubah_map": pygame.Rect(220, 550, 160, 40),
        "start": pygame.Rect(50, 550, 100, 40),
        "stop": pygame.Rect(400, 550, 100, 40),
        "acak_titik": pygame.Rect(510, 550, 100, 40)
    }
    
    player_pos = find_nearest_point(road_points, (50, 50))
    goal_pos = find_nearest_point(road_points, (random.randint(100, width - 100), random.randint(100, height - 100)))
    path = []
    moving = False
    move_delay = 100
    frame_counter = 10
    
    running = True
    while running:
        screen.fill((255, 255, 255))
        screen.blit(grid, (0, 0))
        
        for name, rect in buttons.items():
            pygame.draw.rect(screen, (0, 0, 0), rect)
            screen.blit(button_font.render(name.replace('_', ' ').title(), True, (255, 255, 255)), (rect.x + 10, rect.y + 5))
        
        pygame.draw.circle(screen, (255, 0, 0), player_pos, 10)
        pygame.draw.circle(screen, (0, 0, 255), goal_pos, 10)
        
        if moving and path:
            frame_counter += 1
            if frame_counter >= move_delay:
                frame_counter = 0
                player_pos = path.pop(0)
                if not path:
                    moving = False
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttons["ubah_map"].collidepoint(event.pos):
                    grid, road_points = generate_map(width, height)
                    goal_pos = find_nearest_point(road_points, (random.randint(100, width - 100), random.randint(100, height - 100)))
                    player_pos = find_nearest_point(road_points, (50, 50))
                elif buttons["start"].collidepoint(event.pos):
                    path = a_star_pathfinding(road_points, player_pos, goal_pos)
                    moving = True
                elif buttons["stop"].collidepoint(event.pos):
                    moving = False
                elif buttons["acak_titik"].collidepoint(event.pos):
                    player_pos = find_nearest_point(road_points, (random.randint(50, width - 50), random.randint(50, height - 50)))
                    goal_pos = find_nearest_point(road_points, (random.randint(50, width - 50), random.randint(50, height - 50)))
    
    pygame.quit()

def a_star_pathfinding(road_points, start, goal):
    open_set = [(0, start)]
    heapq.heapify(open_set)
    came_from = {}
    g_score = {point: float('inf') for point in road_points}
    g_score[start] = 0
    f_score = {point: float('inf') for point in road_points}
    f_score[start] = math.dist(start, goal)
    
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
        
        for neighbor in road_points:
            if math.dist(current, neighbor) < 20:
                tentative_g_score = g_score[current] + math.dist(current, neighbor)
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + math.dist(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []

if __name__ == "__main__":
    main()