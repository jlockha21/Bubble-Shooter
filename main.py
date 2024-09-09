import pygame
import sys
import random
import math

pygame.init()

# Game Variables
WIDTH = 800
HEIGHT = 600
BALL_RADIUS = 20
BALL_SPEED = 8
SHOOT_DELAY = 500
GRID_SIZE = BALL_RADIUS * 2  # Grid size based on bubble diameter
TOLERANCE = 2  # Tolerance to avoid overlap issues

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Bubble Colors
BUBBLE_COLORS = [RED, GREEN, BLUE]

# Game Screen
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PUZZLE BUBBLE")

CLOCK = pygame.time.Clock()

# Game State Constants
START_MENU = 0
PLAYING = 1
GAME_OVER = 2

# Initial Game State
game_state = START_MENU

class Bubble:
    def __init__(self, color, x, y, angle=0):
        self.color = color
        self.x = x
        self.y = y
        self.radius = BALL_RADIUS
        self.angle = angle

    def draw(self):
        pygame.draw.circle(SCREEN, self.color, (int(self.x), int(self.y)), self.radius)

    def move(self):
        self.x += BALL_SPEED * math.cos(self.angle)
        self.y -= BALL_SPEED * math.sin(self.angle)

        # Bounce off walls
        if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
            self.angle = math.pi - self.angle

    def collides_with(self, other):
        distance = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        return distance <= self.radius * 2

    def is_close_to(self, other):
        distance = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        return distance < GRID_SIZE - TOLERANCE

class Shooter:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 50
        self.color = YELLOW
        self.shooting = False
        self.current_bubble = None
        self.next_bubble_color = self.get_random_color()
        self.angle = math.pi / 2  # Straight up

    def get_remaining_colors(self):
        colors = set(bubble.color for bubble in bubbles)
        return list(colors) if colors else BUBBLE_COLORS

    def get_random_color(self):
        remaining_colors = self.get_remaining_colors()
        return random.choice(remaining_colors) if remaining_colors else random.choice(BUBBLE_COLORS)

    def aim(self, mouse_pos):
        dx = mouse_pos[0] - self.x
        dy = self.y - mouse_pos[1]
        self.angle = math.atan2(dy, dx)

    def shoot(self):
        self.current_bubble = Bubble(self.next_bubble_color, self.x, self.y, self.angle)
        self.next_bubble_color = self.get_random_color()
        self.shooting = True

    def stop_shooting(self):
        self.shooting = False

    def move_left(self):
        self.x -= BALL_SPEED
        if self.x - BALL_RADIUS < 0:
            self.x = BALL_RADIUS

    def move_right(self):
        self.x += BALL_SPEED
        if self.x + BALL_RADIUS > WIDTH:
            self.x = WIDTH - BALL_RADIUS

    def draw(self):
        if self.current_bubble:
            self.current_bubble.draw()
        pygame.draw.circle(SCREEN, self.color, (self.x, self.y), BALL_RADIUS)
        pygame.draw.circle(SCREEN, self.next_bubble_color, (self.x, self.y + BALL_RADIUS * 2), BALL_RADIUS)
        
        line_length = 50
        end_x = self.x + line_length * math.cos(self.angle)
        end_y = self.y - line_length * math.sin(self.angle)
        pygame.draw.line(SCREEN, WHITE, (self.x, self.y), (end_x, end_y), 2)

# Initialize bubbles
bubbles = []
shooter = Shooter()
shoot_timer = 0

def create_initial_bubbles():
    rows = (HEIGHT // 3) // GRID_SIZE
    cols = WIDTH // GRID_SIZE
    for row in range(rows):
        for col in range(cols):
            x = col * GRID_SIZE + BALL_RADIUS
            y = row * GRID_SIZE + BALL_RADIUS
            color = random.choice(BUBBLE_COLORS)
            bubbles.append(Bubble(color, x, y))

def check_collision(bubble1, bubble2):
    distance = ((bubble1.x - bubble2.x) ** 2 + (bubble1.y - bubble2.y) ** 2) ** 0.5
    return distance <= bubble1.radius * 2

def find_connected_bubbles(start_bubble):
    to_check = [start_bubble]
    connected = []

    while to_check:
        bubble = to_check.pop()
        if bubble not in connected:
            connected.append(bubble)
            for other in bubbles:
                if check_collision(bubble, other) and other.color == bubble.color:
                    to_check.append(other)
    
    return connected

def remove_connected_bubbles(start_bubble):
    connected = find_connected_bubbles(start_bubble)
    if len(connected) >= 3:
        for bubble in connected:
            if bubble in bubbles:
                bubbles.remove(bubble)
        return True
    return False

def snap_to_grid(x, y):
    x = round(x / GRID_SIZE) * GRID_SIZE
    y = round(y / GRID_SIZE) * GRID_SIZE
    return x, y

def adjust_bubble_placement(new_bubble):
    closest_bubble = None
    min_distance = float('inf')

    for bubble in bubbles:
        distance = ((new_bubble.x - bubble.x) ** 2 + (new_bubble.y - bubble.y) ** 2) ** 0.5
        if distance < min_distance and bubble.is_close_to(new_bubble):
            min_distance = distance
            closest_bubble = bubble

    if closest_bubble:
        angle_to_bubble = math.atan2(new_bubble.y - closest_bubble.y, new_bubble.x - closest_bubble.x)
        new_bubble.x = closest_bubble.x + (GRID_SIZE) * math.cos(angle_to_bubble)
        new_bubble.y = closest_bubble.y + (GRID_SIZE) * math.sin(angle_to_bubble)

def keep_bubble_in_bounds(bubble):
    if bubble.x - bubble.radius < 0:
        bubble.x = bubble.radius
    if bubble.x + bubble.radius > WIDTH:
        bubble.x = WIDTH - bubble.radius
    if bubble.y - bubble.radius < 0:
        bubble.y = bubble.radius
    if bubble.y + bubble.radius > HEIGHT:
        bubble.y = HEIGHT - bubble.radius

def draw_start_menu():
    SCREEN.fill(BLACK)
    font = pygame.font.Font(None, 74)
    text = font.render('PUZZLE BUBBLE', True, WHITE)
    SCREEN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2 - 50))

    font = pygame.font.Font(None, 36)
    start_text = font.render('Press ENTER to Start', True, WHITE)
    SCREEN.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 20))

    pygame.display.flip()

create_initial_bubbles()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state == START_MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = PLAYING

        elif game_state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not shooter.shooting and pygame.time.get_ticks() - shoot_timer >= SHOOT_DELAY:
                        shooter.shoot()
                        shoot_timer = pygame.time.get_ticks()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if not shooter.shooting and pygame.time.get_ticks() - shoot_timer >= SHOOT_DELAY:
                        shooter.shoot()
                        shoot_timer = pygame.time.get_ticks()

    if game_state == START_MENU:
        draw_start_menu()

    elif game_state == PLAYING:
        mouse_pos = pygame.mouse.get_pos()
        shooter.aim(mouse_pos)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            shooter.move_left()
        if keys[pygame.K_RIGHT]:
            shooter.move_right()

        if shooter.shooting:
            shooter.current_bubble.move()
            collision_detected = False

            for bubble in bubbles:
                if check_collision(shooter.current_bubble, bubble):
                    collision_detected = True
                    shooter.current_bubble.x, shooter.current_bubble.y = snap_to_grid(shooter.current_bubble.x, shooter.current_bubble.y)
                    adjust_bubble_placement(shooter.current_bubble)
                    keep_bubble_in_bounds(shooter.current_bubble)
                    bubbles.append(shooter.current_bubble)
                    break

            if collision_detected or shooter.current_bubble.y <= BALL_RADIUS:
                if not collision_detected:
                    shooter.current_bubble.x, shooter.current_bubble.y = snap_to_grid(shooter.current_bubble.x, shooter.current_bubble.y)
                    adjust_bubble_placement(shooter.current_bubble)
                    keep_bubble_in_bounds(shooter.current_bubble)
                    bubbles.append(shooter.current_bubble)

                if remove_connected_bubbles(shooter.current_bubble):
                    shooter.current_bubble = None
                shooter.stop_shooting()

        SCREEN.fill(BLACK)

        for bubble in bubbles:
            bubble.draw()

        shooter.draw()

        pygame.display.flip()
        CLOCK.tick(30)
