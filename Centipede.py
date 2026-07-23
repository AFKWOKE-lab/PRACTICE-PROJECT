import pygame
import math
import sys

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
BG_COLOR = (15, 15, 40)             # Dark blue/purple background
BONE_COLOR = (205, 214, 255)        # Light glowing blue/white
LEG_COLOR = (205, 214, 255, 153)    # Slightly transparent (RGBA)
WHITE = (255, 255, 255)

# Pygame Setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Procedural Reptile Animation")
clock = pygame.time.Clock()

# --- CREATURE SETUP ---
num_segments = 35
segment_length = 12

# Spine is a list of dictionaries holding x, y, and angle
spine = [{'x': WIDTH // 2, 'y': HEIGHT // 2, 'angle': 0.0} for _ in range(num_segments)]

# Target follows the mouse
target = {'x': WIDTH // 2, 'y': HEIGHT // 2}

# Legs Configuration
legs = []
leg_spacing = 4  # Add legs every N segments

for i in range(3, num_segments - 3, leg_spacing):
    # Right leg (side = 1) and Left leg (side = -1)
    for side in [1, -1]:
        legs.append({
            'seg_idx': i,
            'side': side,
            'foot_x': WIDTH // 2,
            'foot_y': HEIGHT // 2,
            'is_stepping': False,
            'step_progress': 0.0,
            'start_x': 0, 'start_y': 0,
            'target_x': 0, 'target_y': 0
        })

# --- MAIN ANIMATION LOOP ---
running = True
while running:
    # 1. Handle Events (Mouse clicks/movement and closing the window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            # If the mouse moves or is clicked, update the target position
            target['x'], target['y'] = event.pos

    # 2. Move Head smoothly towards target
    head = spine[0]
    dx = target['x'] - head['x']
    dy = target['y'] - head['y']
    dist = math.hypot(dx, dy)

    if dist > 2:
        head['x'] += dx * 0.08
        head['y'] += dy * 0.08

    # 3. Resolve Spine (Inverse Kinematics)
    for i in range(1, num_segments):
        prev = spine[i - 1]
        curr = spine[i]
        
        # Calculate angle between current segment and previous segment
        angle = math.atan2(prev['y'] - curr['y'], prev['x'] - curr['x'])
        curr['angle'] = angle
        
        # Keep segments at exactly `segment_length` distance apart
        curr['x'] = prev['x'] - math.cos(angle) * segment_length
        curr['y'] = prev['y'] - math.sin(angle) * segment_length

    # Update head angle to match the neck
    if len(spine) > 1:
        head['angle'] = math.atan2(head['y'] - spine[1]['y'], head['x'] - spine[1]['x'])

    # 4. Clear Screen
    screen.fill(BG_COLOR)

    # Surface for drawing transparent lines (legs)
    transparent_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # 5. Update and Draw Legs
    for leg in legs:
        seg = spine[leg['seg_idx']]
        
        # Calculate ideal foot placement
        offset_angle = seg['angle'] + (math.pi / 2) * leg['side']
        leg_reach = 35
        ideal_x = seg['x'] + math.cos(offset_angle) * leg_reach
        ideal_y = seg['y'] + math.sin(offset_angle) * leg_reach

        # Distance between actual foot and ideal foot position
        foot_dist = math.hypot(ideal_x - leg['foot_x'], ideal_y - leg['foot_y'])

        # Trigger a step if the foot is left too far behind
        if foot_dist > 45 and not leg['is_stepping']:
            leg['is_stepping'] = True
            leg['start_x'] = leg['foot_x']
            leg['start_y'] = leg['foot_y']
            leg['step_progress'] = 0.0
            
            # Predict step forward based on body direction
            leg['target_x'] = ideal_x + math.cos(seg['angle']) * 20
            leg['target_y'] = ideal_y + math.sin(seg['angle']) * 20

        # Handle stepping animation
        if leg['is_stepping']:
            leg['step_progress'] += 0.12
            if leg['step_progress'] >= 1.0:
                leg['is_stepping'] = False
                leg['step_progress'] = 1.0
            
            # Linear Interpolation (Lerp)
            leg['foot_x'] = leg['start_x'] + (leg['target_x'] - leg['start_x']) * leg['step_progress']
            leg['foot_y'] = leg['start_y'] + (leg['target_y'] - leg['start_y']) * leg['step_progress']

        # Calculate "knee" joint for a bent look
        joint_x = (seg['x'] + leg['foot_x']) / 2 + math.cos(offset_angle) * 15
        joint_y = (seg['y'] + leg['foot_y']) / 2 + math.sin(offset_angle) * 15

        # Draw the leg lines
        pygame.draw.lines(transparent_surface, LEG_COLOR, False, [(seg['x'], seg['y']), (joint_x, joint_y), (leg['foot_x'], leg['foot_y'])], 2)
        
        # Draw feet/claws
        pygame.draw.circle(transparent_surface, WHITE, (int(leg['foot_x']), int(leg['foot_y'])), 3)

    # Blit (draw) the transparent surface onto the main screen
    screen.blit(transparent_surface, (0, 0))

    # 6. Draw Spine
    points = [(s['x'], s['y']) for s in spine]
    if len(points) > 1:
        pygame.draw.lines(screen, BONE_COLOR, False, points, 4)

    # 7. Draw Head
    pygame.draw.circle(screen, WHITE, (int(head['x']), int(head['y'])), 7)

    # 8. Update Display and Tick Clock
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

