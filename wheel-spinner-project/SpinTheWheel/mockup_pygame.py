import pygame
import math
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
#pygame.display.setCaption("Spin the Wheel Game")
ft_obj = pygame.font.Font(None, 52)

# Colors
BLACK = "#2d3047"
WHITE = (255, 255, 255)
RED = "#c8553d"
GREEN = "#588b8b"
BLUE = "#93b7be"
ORANGE = "#f28f3b"
PEACH = "#ffd5c2"

col_names = {
    WHITE: "white",
    RED: "red",
    GREEN: "green",
    BLUE: "blue",
    ORANGE: "orange",
    PEACH: "peach",
}

BG_COL = BLACK
CURSOR_COL = WHITE


# Define the wheel's wedges
NUM_WEDGES = 6

# ATTENTION: grosse astuce!
# comme on recherche l'alignement entre le cuseurs qui se trouve en haut de l'écran (et pas l'angle 0)
# et puis comme on dessine les wedges dans un ordre qui est inversé par rapport à la rotation appliquée
# sur la roue, nous devons à la fois selectionner le 1er element différemment 
# ET utiliser l'ordre inverser pour que le calcul de wedge actuel + l'image affichée soit en cohérence
disp_order_WEDGE_COLORS = [RED, GREEN, BLUE, ORANGE, PEACH, WHITE]

WEDGE_COLORS = [WHITE, RED, GREEN, BLUE, ORANGE, PEACH]
WEDGE_COLORS.reverse()


ANGLE_PER_WEDGE = 360 / NUM_WEDGES
WHEEL_RADIUS = 200

angles_thresholds = [ (i*ANGLE_PER_WEDGE-30,i*ANGLE_PER_WEDGE+30) for i in range(6) ]
print(angles_thresholds)

# Wheel rotation
# 0 --> milieu du peach, -30..30 est donc l'intervalle où on est ds peach 
# 
current_angle = 0  # degrés & clockwise
spinning = False
speed = 0
deceleration = 0.08  # Constant deceleration
final_target_angle = 0
tmp_disp = None  # label to disp final wedge color
LABEL_POS = (320,540)


def gen_initial_speed():
    return random.uniform(6.0, 21.667)  # the random spin speed, initially applied


def draw_wheel(center_x, center_y, angle):
    for i in range(NUM_WEDGES):
        start_angle = math.radians(angle + i * ANGLE_PER_WEDGE)
        end_angle = math.radians(angle + (i + 1) * ANGLE_PER_WEDGE)

        # Calculate the points for the wedge polygon
        start_x = center_x + WHEEL_RADIUS * math.cos(start_angle)
        start_y = center_y + WHEEL_RADIUS * math.sin(start_angle)
        end_x = center_x + WHEEL_RADIUS * math.cos(end_angle)
        end_y = center_y + WHEEL_RADIUS * math.sin(end_angle)

        # Draw the wedge
        points = [(center_x, center_y), (start_x, start_y), (end_x, end_y)]
        pygame.draw.polygon(screen, disp_order_WEDGE_COLORS[i], points)


def get_wcolor_under_cursor(curr_angle):

    global WEDGE_COLORS
    # Center of the wheel
    # center_x, center_y = WIDTH // 2, HEIGHT // 2
    
    # The angle where the cursor is pointing (upwards is 90 degrees)
    # cursor_angle = 90  # 90 degrees is the upward direction
    
    # Adjust the angle to see which wedge the cursor points to
    print(curr_angle)
    adjusted_angle = curr_angle % 360
    print('adjusted->',adjusted_angle)
    
    # Determine the wedge under the cursor
    for rank in range(0, 6):
        intv = angles_thresholds[rank]
        if intv[0] < adjusted_angle <= intv[1]:
            return WEDGE_COLORS[rank]
    return WEDGE_COLORS[0]  # because numbers below 0.0 arent supported by the for loop above


# Main loop

# - debug
# print("Initial angle:", current_angle)
#y = get_wcolor_under_cursor(current_angle)
# print("Initial color under cursor:", y, col_names[y])

running = True
while running:
    screen.fill(BG_COL)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not spinning:
                # Start the spinning
                spinning = True
                tmp_disp = None
                # initial_angle = current_angle % (90*6)  # Save the starting angle
                speed = gen_initial_speed()
                # Random target angle (1-3 full spins)
                # final_target_angle = initial_angle + random.uniform(360, 1080)

    # Draw the wheel
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    draw_wheel(center_x, center_y, current_angle)

    # Spin the wheel
    if spinning:
        current_angle -= speed
        speed -= deceleration
        if speed < 0.0001:
            spinning = False
            speed = 0
            wedge_color = get_wcolor_under_cursor(current_angle)
            wedge_name = col_names[wedge_color]
            # print(f"The wheel stopped at {wedge_name.capitalize()}!")
            tmp_disp = ft_obj.render(wedge_name.capitalize(), True, wedge_color, "#ffffff" if wedge_color!=WHITE else "#000000")
 
    # Draw the cursor
    pygame.draw.polygon(screen, CURSOR_COL, [(center_x - 10, 50), (center_x + 10, 50), (center_x, 90)])
    if tmp_disp:
       screen.blit(tmp_disp, LABEL_POS)
  
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
