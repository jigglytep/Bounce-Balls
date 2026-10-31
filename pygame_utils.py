import os
import time
import math
import random
import pygame
import pymunk
import numpy as np
import cv2_utils
import pyo_utils

#############################################
#   Andrew Chao - andrewchao7000@gmail.com  #
#   6/1/2026                                #
#############################################

HALLOWEEN_TYPES = [
    ("pumpkin", (255, 130, 25)),
    ("witch_hat", (155, 75, 235)),
    ("ghost", (170, 225, 255)),
    ("spider", (140, 80, 210)),
    ("candy_corn", (255, 195, 40)),
    ("black_cat", (80, 220, 130)),
    ("cauldron", (110, 245, 90)),
    ("candy", (255, 85, 180)),
]

_SPRITE_CACHE = {}


def _create_halloween_sprite(kind, radius):
    key = (kind, radius)
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]

    # Surface slightly larger than diameter to fit hat brims, spider legs, cat ears, candy wrappers
    pad = int(radius * 0.55)
    size = (radius + pad) * 2
    cx, cy = size // 2, size // 2
    r = radius
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    if kind == "pumpkin":
        # Stem
        stem_pts = [
            (cx - int(r * 0.15), cy - int(r * 0.78)),
            (cx + int(r * 0.15), cy - int(r * 0.78)),
            (cx + int(r * 0.28), cy - int(r * 1.18)),
            (cx + int(r * 0.05), cy - int(r * 1.22)),
        ]
        pygame.draw.polygon(surf, (55, 155, 55), stem_pts)
        # Pumpkin body lobes
        body_rect = pygame.Rect(cx - int(r * 1.05), cy - int(r * 0.82), int(r * 2.1), int(r * 1.7))
        pygame.draw.ellipse(surf, (235, 105, 15), body_rect)
        pygame.draw.ellipse(surf, (180, 65, 5), body_rect, 2)
        mid_rect = pygame.Rect(cx - int(r * 0.7), cy - int(r * 0.84), int(r * 1.4), int(r * 1.72))
        pygame.draw.ellipse(surf, (250, 125, 20), mid_rect)
        pygame.draw.ellipse(surf, (195, 75, 10), mid_rect, 2)
        center_rect = pygame.Rect(cx - int(r * 0.35), cy - int(r * 0.85), int(r * 0.7), int(r * 1.74))
        pygame.draw.ellipse(surf, (255, 145, 30), center_rect)
        pygame.draw.ellipse(surf, (205, 85, 10), center_rect, 2)
        # Happy triangle eyes (warm yellow glow)
        left_eye = [(cx - int(r * 0.5), cy - int(r * 0.1)), (cx - int(r * 0.2), cy - int(r * 0.1)), (cx - int(r * 0.35), cy - int(r * 0.42))]
        right_eye = [(cx + int(r * 0.2), cy - int(r * 0.1)), (cx + int(r * 0.5), cy - int(r * 0.1)), (cx + int(r * 0.35), cy - int(r * 0.42))]
        pygame.draw.polygon(surf, (255, 240, 90), left_eye)
        pygame.draw.polygon(surf, (255, 240, 90), right_eye)
        pygame.draw.polygon(surf, (70, 30, 10), left_eye, 1)
        pygame.draw.polygon(surf, (70, 30, 10), right_eye, 1)
        # Cute smile
        smile_rect = pygame.Rect(cx - int(r * 0.55), cy - int(r * 0.15), int(r * 1.1), int(r * 0.7))
        pygame.draw.arc(surf, (255, 240, 90), smile_rect, math.pi * 1.15, math.pi * 1.85, max(3, int(r * 0.16)))

    elif kind == "witch_hat":
        # Cone of hat
        cone_pts = [
            (cx - int(r * 0.8), cy + int(r * 0.45)),
            (cx + int(r * 0.8), cy + int(r * 0.45)),
            (cx + int(r * 0.25), cy - int(r * 0.7)),
            (cx + int(r * 0.55), cy - int(r * 1.1)),
            (cx - int(r * 0.15), cy - int(r * 0.95)),
        ]
        pygame.draw.polygon(surf, (65, 35, 95), cone_pts)
        pygame.draw.polygon(surf, (35, 15, 55), cone_pts, 2)
        # Hat band (orange ribbon)
        band_pts = [
            (cx - int(r * 0.75), cy + int(r * 0.22)),
            (cx + int(r * 0.75), cy + int(r * 0.22)),
            (cx + int(r * 0.82), cy + int(r * 0.45)),
            (cx - int(r * 0.82), cy + int(r * 0.45)),
        ]
        pygame.draw.polygon(surf, (255, 130, 25), band_pts)
        # Gold buckle
        buckle_rect = pygame.Rect(cx - int(r * 0.22), cy + int(r * 0.18), int(r * 0.44), int(r * 0.3))
        pygame.draw.rect(surf, (255, 215, 50), buckle_rect, max(2, int(r * 0.1)))
        # Wide hat brim
        brim_rect = pygame.Rect(cx - int(r * 1.25), cy + int(r * 0.3), int(r * 2.5), int(r * 0.55))
        pygame.draw.ellipse(surf, (75, 40, 110), brim_rect)
        pygame.draw.ellipse(surf, (35, 15, 55), brim_rect, 2)
        # Little star on tip
        pygame.draw.circle(surf, (255, 225, 70), (cx + int(r * 0.55), cy - int(r * 1.1)), max(3, int(r * 0.14)))

    elif kind == "ghost":
        # Dome top + wavy skirt
        head_center = (cx, cy - int(r * 0.18))
        head_r = int(r * 0.82)
        pygame.draw.circle(surf, (245, 250, 255), head_center, head_r)
        body_pts = [
            (cx - head_r, cy - int(r * 0.18)),
            (cx - head_r, cy + int(r * 0.75)),
            (cx - int(r * 0.52), cy + int(r * 0.5)),
            (cx - int(r * 0.25), cy + int(r * 0.8)),
            (cx, cy + int(r * 0.52)),
            (cx + int(r * 0.25), cy + int(r * 0.8)),
            (cx + int(r * 0.52), cy + int(r * 0.5)),
            (cx + head_r, cy + int(r * 0.75)),
            (cx + head_r, cy - int(r * 0.18)),
        ]
        pygame.draw.polygon(surf, (245, 250, 255), body_pts)
        pygame.draw.circle(surf, (130, 185, 230), head_center, head_r, 2)
        pygame.draw.lines(surf, (130, 185, 230), False, body_pts[1:-1], 2)
        # Cute eyes & rosy cheeks
        pygame.draw.circle(surf, (40, 45, 65), (cx - int(r * 0.3), cy - int(r * 0.22)), max(3, int(r * 0.14)))
        pygame.draw.circle(surf, (40, 45, 65), (cx + int(r * 0.3), cy - int(r * 0.22)), max(3, int(r * 0.14)))
        pygame.draw.circle(surf, (255, 255, 255), (cx - int(r * 0.34), cy - int(r * 0.26)), max(1, int(r * 0.05)))
        pygame.draw.circle(surf, (255, 255, 255), (cx + int(r * 0.26), cy - int(r * 0.26)), max(1, int(r * 0.05)))
        # Rosy cheeks
        pygame.draw.circle(surf, (255, 175, 195), (cx - int(r * 0.46), cy - int(r * 0.04)), max(3, int(r * 0.13)))
        pygame.draw.circle(surf, (255, 175, 195), (cx + int(r * 0.46), cy - int(r * 0.04)), max(3, int(r * 0.13)))
        # Happy little 'o' mouth / smile
        smile_rect = pygame.Rect(cx - int(r * 0.22), cy - int(r * 0.15), int(r * 0.44), int(r * 0.3))
        pygame.draw.arc(surf, (40, 45, 65), smile_rect, math.pi * 1.1, math.pi * 1.9, 2)

    elif kind == "spider":
        # 8 cute bent legs (4 per side)
        leg_color = (50, 35, 70)
        for i, y_off in enumerate([-0.35, -0.12, 0.12, 0.35]):
            y_start = cy + int(r * y_off)
            y_knee = cy + int(r * (y_off - 0.28))
            y_foot = cy + int(r * (y_off + 0.18))
            # Left leg
            pygame.draw.lines(surf, leg_color, False, [
                (cx - int(r * 0.55), y_start),
                (cx - int(r * 1.05), y_knee),
                (cx - int(r * 1.28), y_foot),
            ], 3)
            # Right leg
            pygame.draw.lines(surf, leg_color, False, [
                (cx + int(r * 0.55), y_start),
                (cx + int(r * 1.05), y_knee),
                (cx + int(r * 1.28), y_foot),
            ], 3)
        # Round fuzzy body
        pygame.draw.circle(surf, (65, 45, 90), (cx, cy), int(r * 0.78))
        pygame.draw.circle(surf, (130, 85, 185), (cx, cy), int(r * 0.78), 2)
        # Big friendly googly eyes
        eye_r = max(4, int(r * 0.24))
        pupil_r = max(2, int(r * 0.12))
        for ex in (cx - int(r * 0.28), cx + int(r * 0.28)):
            ey = cy - int(r * 0.12)
            pygame.draw.circle(surf, (255, 255, 255), (ex, ey), eye_r)
            pygame.draw.circle(surf, (30, 20, 45), (ex, ey), pupil_r)
            pygame.draw.circle(surf, (255, 255, 255), (ex - 2, ey - 2), max(1, pupil_r // 2))
        # Cute smile
        smile_rect = pygame.Rect(cx - int(r * 0.26), cy + int(r * 0.05), int(r * 0.52), int(r * 0.32))
        pygame.draw.arc(surf, (255, 180, 220), smile_rect, math.pi * 1.15, math.pi * 1.85, 2)

    elif kind == "candy_corn":
        # Rounded triangle layered in Yellow (bottom), Orange (middle), White (tip)
        top_y = cy - int(r * 0.95)
        bot_y = cy + int(r * 0.85)
        mid1_y = cy - int(r * 0.32)
        mid2_y = cy + int(r * 0.28)
        # Full triangle base (yellow)
        full_pts = [(cx, top_y), (cx + int(r * 0.88), bot_y), (cx - int(r * 0.88), bot_y)]
        pygame.draw.polygon(surf, (255, 220, 45), full_pts)
        # Middle + top (orange)
        w2 = int(r * 0.62)
        orange_pts = [(cx, top_y), (cx + w2, mid2_y), (cx - w2, mid2_y)]
        pygame.draw.polygon(surf, (255, 130, 20), orange_pts)
        # Top tip (white)
        w1 = int(r * 0.32)
        white_pts = [(cx, top_y), (cx + w1, mid1_y), (cx - w1, mid1_y)]
        pygame.draw.polygon(surf, (255, 252, 245), white_pts)
        # Outline
        pygame.draw.polygon(surf, (195, 85, 10), full_pts, 2)
        # Cute face in middle section
        pygame.draw.circle(surf, (55, 30, 15), (cx - int(r * 0.22), cy + int(r * 0.05)), max(2, int(r * 0.1)))
        pygame.draw.circle(surf, (55, 30, 15), (cx + int(r * 0.22), cy + int(r * 0.05)), max(2, int(r * 0.1)))
        smile_rect = pygame.Rect(cx - int(r * 0.2), cy + int(r * 0.08), int(r * 0.4), int(r * 0.25))
        pygame.draw.arc(surf, (55, 30, 15), smile_rect, math.pi * 1.15, math.pi * 1.85, 2)

    elif kind == "black_cat":
        # Pointy cat ears
        left_ear = [(cx - int(r * 0.75), cy - int(r * 0.25)), (cx - int(r * 0.78), cy - int(r * 1.05)), (cx - int(r * 0.2), cy - int(r * 0.68))]
        right_ear = [(cx + int(r * 0.75), cy - int(r * 0.25)), (cx + int(r * 0.78), cy - int(r * 1.05)), (cx + int(r * 0.2), cy - int(r * 0.68))]
        pygame.draw.polygon(surf, (40, 40, 52), left_ear)
        pygame.draw.polygon(surf, (40, 40, 52), right_ear)
        # Pink inner ears
        left_inner = [(cx - int(r * 0.65), cy - int(r * 0.35)), (cx - int(r * 0.68), cy - int(r * 0.88)), (cx - int(r * 0.3), cy - int(r * 0.62))]
        right_inner = [(cx + int(r * 0.65), cy - int(r * 0.35)), (cx + int(r * 0.68), cy - int(r * 0.88)), (cx + int(r * 0.3), cy - int(r * 0.62))]
        pygame.draw.polygon(surf, (255, 165, 190), left_inner)
        pygame.draw.polygon(surf, (255, 165, 190), right_inner)
        # Cat head
        pygame.draw.circle(surf, (40, 40, 52), (cx, cy), int(r * 0.82))
        pygame.draw.circle(surf, (95, 95, 120), (cx, cy), int(r * 0.82), 2)
        # Bright emerald eyes
        for ex in (cx - int(r * 0.32), cx + int(r * 0.32)):
            ey = cy - int(r * 0.12)
            pygame.draw.circle(surf, (110, 240, 110), (ex, ey), max(4, int(r * 0.2)))
            pygame.draw.ellipse(surf, (20, 25, 20), pygame.Rect(ex - max(1, int(r * 0.06)), ey - int(r * 0.14), max(3, int(r * 0.12)), int(r * 0.28)))
        # Cute pink triangle nose & whiskers
        nose_pts = [(cx - int(r * 0.12), cy + int(r * 0.08)), (cx + int(r * 0.12), cy + int(r * 0.08)), (cx, cy + int(r * 0.22))]
        pygame.draw.polygon(surf, (255, 165, 190), nose_pts)
        for wy in (-0.05, 0.12):
            pygame.draw.line(surf, (210, 210, 225), (cx - int(r * 0.45), cy + int(r * 0.12)), (cx - int(r * 0.95), cy + int(r * wy)), 2)
            pygame.draw.line(surf, (210, 210, 225), (cx + int(r * 0.45), cy + int(r * 0.12)), (cx + int(r * 0.95), cy + int(r * wy)), 2)

    elif kind == "cauldron":
        # Cauldron pot body
        pot_rect = pygame.Rect(cx - int(r * 0.88), cy - int(r * 0.45), int(r * 1.76), int(r * 1.35))
        pygame.draw.ellipse(surf, (50, 50, 65), pot_rect)
        pygame.draw.ellipse(surf, (25, 25, 35), pot_rect, 2)
        # Rim
        rim_rect = pygame.Rect(cx - int(r * 0.92), cy - int(r * 0.52), int(r * 1.84), int(r * 0.36))
        pygame.draw.ellipse(surf, (70, 70, 90), rim_rect)
        # Glowing green potion & bubbles
        potion_rect = pygame.Rect(cx - int(r * 0.78), cy - int(r * 0.46), int(r * 1.56), int(r * 0.26))
        pygame.draw.ellipse(surf, (115, 245, 85), potion_rect)
        for bx, by, br in [(-0.35, -0.52, 0.2), (0.0, -0.62, 0.25), (0.35, -0.5, 0.18), (-0.15, -0.82, 0.14), (0.22, -0.85, 0.12)]:
            b_pos = (cx + int(r * bx), cy + int(r * by))
            b_rad = max(3, int(r * br))
            pygame.draw.circle(surf, (135, 255, 110), b_pos, b_rad)
            pygame.draw.circle(surf, (220, 255, 210), (b_pos[0] - 1, b_pos[1] - 1), max(1, b_rad // 3))

    else:  # "candy" (wrapped Halloween candy)
        # Left and right wrapper twists
        left_wrap = [(cx - int(r * 0.65), cy), (cx - int(r * 1.2), cy - int(r * 0.45)), (cx - int(r * 1.2), cy + int(r * 0.45))]
        right_wrap = [(cx + int(r * 0.65), cy), (cx + int(r * 1.2), cy - int(r * 0.45)), (cx + int(r * 1.2), cy + int(r * 0.45))]
        pygame.draw.polygon(surf, (255, 140, 30), left_wrap)
        pygame.draw.polygon(surf, (255, 140, 30), right_wrap)
        pygame.draw.polygon(surf, (170, 70, 10), left_wrap, 2)
        pygame.draw.polygon(surf, (170, 70, 10), right_wrap, 2)
        # Round candy center (purple & orange stripes)
        pygame.draw.circle(surf, (165, 65, 225), (cx, cy), int(r * 0.72))
        stripe_rect = pygame.Rect(cx - int(r * 0.25), cy - int(r * 0.68), int(r * 0.5), int(r * 1.36))
        pygame.draw.ellipse(surf, (255, 155, 35), stripe_rect)
        pygame.draw.circle(surf, (95, 30, 140), (cx, cy), int(r * 0.72), 2)

    _SPRITE_CACHE[key] = surf
    return surf


#classes
class Ball:
    def __init__(self, color, radius, inital_position, space, kind=None):
        if kind is None:
            kind, default_color = random.choice(HALLOWEEN_TYPES)
            self.color = default_color
        else:
            self.color = color
        self.kind = kind
        self.radius = radius

        #body
        density = 0.01
        mass = (np.pi * radius**2) * density
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = inital_position

        #poly
        self.poly = pymunk.Circle(self.body, radius)
        self.poly.elasticity = 0.72
        self.poly.friction = 0.45

        #collision
        self.poly.collision_type = 1 #COLLISION NUM 1

        #add to space
        space.add(self.body, self.poly)

        # Pre-rendered Halloween sprite
        self.sprite = _create_halloween_sprite(self.kind, self.radius)

    def draw(self, screen):
        # Gently tilt/rotate sprite based on physics body angle
        angle_deg = -math.degrees(self.body.angle) * 0.35
        rotated = pygame.transform.rotate(self.sprite, angle_deg)
        rect = rotated.get_rect(center=(int(self.body.position.x), int(self.body.position.y)))
        screen.blit(rotated, rect)

    def draw_glow(self, screen, size, intensity):
        for i in range(1, intensity):
            self.__draw_circle_alpha(screen, self.color, self.body.position, self.radius + (i * size), 18)

    def remove_from_space(self, space):
        _last_plink_time.pop(self.poly, None)
        space.remove(self.body, self.poly)

    def __draw_circle_alpha(self, surface, color, center, radius, alpha=255, width=0):
        r, g, b = color[:3]

        diameter = radius * 2
        temp_surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

        pygame.draw.circle(temp_surface, (r, g, b, alpha), (radius, radius), radius, width)

        target_x = center[0] - radius
        target_y = center[1] - radius
        surface.blit(temp_surface, (target_x, target_y))
class Platform:
    def __init__(self, color, poly_points, space):
        self.color = color

        #body
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = (0,0)

        #poly
        poly_points = poly_points.reshape(-1, 2).tolist() #reshape to right format
        self.poly = pymunk.Poly(self.body, poly_points)

        self.poly.elasticity = 1.0  # 1.0 means it absorbs no energy (hard surface)
        self.poly.friction = 0.5  # Gives the surface some grip

        # collision
        self.poly.collision_type = 2  # COLLISION NUM 2

        #add to space
        space.add(self.body, self.poly)

    def draw(self, screen):
        vertices = self.poly.get_vertices()

        point_list = []
        for v in vertices:
            point = self.body.local_to_world(v)
            point_list.append((int(point.x), int(point.y)))

        pygame.draw.polygon(screen, self.color, point_list)
        pygame.draw.polygon(screen, (255, 145, 30), point_list, 3)

    def remove_from_space(self, space):
        _last_plink_time.pop(self.poly, None)
        space.remove(self.body, self.poly)

#audio
_last_plink_time = {}


def play_ball_on_platform_hit_sound(object_data, space, data):
    hit_force = object_data.total_impulse.length

    if hit_force > 150:
        ball_shape, _ = object_data.shapes
        now = time.monotonic()
        # Short per-ball cooldown (65ms) so sliding along a barrier doesn't buzz continuously
        if now - _last_plink_time.get(ball_shape, 0.0) < 0.065:
            return True
        _last_plink_time[ball_shape] = now

        volume = min(max(hit_force / 12000.0, 0.25), 0.95)
        pyo_utils.play_bounce_sound(volume)

    return True
def play_ball_on_ball_hit_sound(object_data, space, data):
    hit_force = object_data.total_impulse.length

    if hit_force > 500:
        volume = min(hit_force / 1000.0, 1.0)
        if volume < 0.05:
            return
        ball_shape, platform_shape = object_data.shapes
        # TODO MAKE NEW SOUND if u want:)



    return True

def _draw_halloween_decor(screen, width):
    # Festive Halloween pennant bunting across the top edge
    bunting_colors = [(255, 135, 25), (120, 55, 185), (255, 205, 45), (85, 215, 110)]
    flag_w = 60
    flag_h = 26
    for i, x in enumerate(range(0, width, flag_w)):
        col = bunting_colors[i % len(bunting_colors)]
        pts = [(x, 0), (x + flag_w, 0), (x + flag_w // 2, flag_h)]
        pygame.draw.polygon(screen, col, pts)
        pygame.draw.polygon(screen, (60, 30, 85), pts, 2)
def main_game_window(pygame_width, pygame_height, platform_update_frequency):
    video_capture_device_number = cv2_utils.get_video_capture_number()

    # pygame init (open on secondary display HDMI-1 at +1920+0 if connected)
    os.environ["SDL_VIDEO_WINDOW_POS"] = "1920,0"
    Running = True
    pygame.init()
    target_display = 1 if pygame.display.get_num_displays() > 1 else 0
    screen = pygame.display.set_mode((pygame_width, pygame_height), pygame.NOFRAME, display=target_display)
    clock = pygame.time.Clock()

    # pymunk init
    space = pymunk.Space()
    space.gravity = 0, 1962

    # pymunk collision checker
    COLLISION_TYPE_BALL = 1
    COLLISION_TYPE_PLATFORM = 2


    space.on_collision(COLLISION_TYPE_BALL, COLLISION_TYPE_PLATFORM, post_solve=play_ball_on_platform_hit_sound)

    # general lists
    ball_list = []
    platform_list = []

    ball_kill_list = []

    # button options
    draw_platform = True
    dark_bg = False

    #color options (Halloween purple platforms with orange trim)
    platform_color = (70, 35, 105)
    previosu_colors = [
        (239, 71, 111),
        (247, 140, 107),
        (255, 209, 102),
        (6, 214, 160),
        (17, 138, 178),
        (7, 59, 76)]

    neon_ball_colors = [
        (255, 42, 109),
        (255, 126, 39),
        (254, 213, 51),
        (5, 213, 175),
        (1, 190, 254),
        (143, 0, 255)
    ]

    #trackers
    tracker = 0

    #update speed
    update_every_x_frame = platform_update_frequency
    frame_count = 0

    #inital user calibration
    screen.fill("white")
    pygame.display.flip()

    lower_bound = np.array([35, 40, 40])
    upper_bound = np.array([135, 255, 255])

    cv2_utils.calibrate_color(video_capture_device_number, lower_bound, upper_bound)
    calibration_points = cv2_utils.find_calibration_points(video_capture_device_number)
    homography_matrix = cv2_utils.calculate_homography_matrix(calibration_points, pygame_width, pygame_height)

    #create capture
    capture = cv2_utils.get_capture(video_capture_device_number)


    # loop
    while Running:

        #user event checker
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Running = False

            if event.type == pygame.KEYDOWN:

                # 'q' to quit
                if event.key == pygame.K_q:
                    Running = False


                # 'c' to open color calibration
                if event.key == pygame.K_c:

                    capture.release()
                    cv2_utils.calibrate_color(video_capture_device_number, lower_bound, upper_bound)
                    capture = cv2_utils.get_capture(video_capture_device_number)

                # 'n' to start/stop drawing platforms
                if event.key == pygame.K_n:
                    draw_platform = not draw_platform

                # 'b' to toggle warm cream vs cozy twilight background
                if event.key == pygame.K_b:
                    dark_bg = not dark_bg

        # take a physics step
        space.step(1.0 / 60)

        # fill screen (bright cream keeps tape well-lit for webcam; 'b' toggles dark twilight)
        bg_color = (35, 22, 56) if dark_bg else (253, 247, 237)
        screen.fill(bg_color)
        _draw_halloween_decor(screen, pygame_width)

        if frame_count > update_every_x_frame:
            # get platforms corners from webcam
            platform_polygon_list = cv2_utils.capture_webcam_frame_and_get_platform_polygons(capture, homography_matrix, lower_bound, upper_bound, pygame_width, pygame_height)

            #delete platforms
            for platform in platform_list:
                platform.remove_from_space(space)

            platform_list.clear()

        #check for dead balls
        for ball in ball_list:
            if ball.body.position.y > pygame_height + ball.radius + 100:
                ball_kill_list.append(ball)

        #delete balls
        for ball in ball_kill_list:
            ball.remove_from_space(space)
            ball_list.remove(ball)

        ball_kill_list.clear()

        # add platforms to empty platform list
        if frame_count > update_every_x_frame:
            for platform_polygon in platform_polygon_list:
                platform_list.append(Platform(platform_color, platform_polygon, space))

        # add balls to balls list
        if tracker > 2:
            tracker = 0

            #stream
            #ball_list.append(Ball(neon_ball_colors[random.randint(0,5)], 15, (pygame_width/2, 30), space))
            #rain
            spawn_x = random.randint(25, pygame_width - 25)
            spawn_y = random.randint(-20, 30)
            radius = random.choice([20, 22, 24])
            ball_list.append(Ball(None, radius, (spawn_x, spawn_y), space))


        #draw platforms
        if draw_platform:
            for platform in platform_list:
                platform.draw(screen)

        #draw balls (glow underneath so cute character faces stay crisp)
        for ball in ball_list:
            ball.draw_glow(screen, 8, 3)
            ball.draw(screen)

        # display work onto screen
        pygame.display.flip()

        # fps cap
        clock.tick(30)

        #update tracker
        tracker+=1
        if frame_count > update_every_x_frame:
            frame_count = 0

        frame_count += 1

    capture.release()
    pygame.quit()
    if pyo_utils.server is not None and pyo_utils.server.getIsStarted():
        pyo_utils.server.stop()


#test stuff ignrore
def test():
    #pygame init
    Running = True
    pygame.init()
    screen = pygame.display.set_mode((800,800))
    clock = pygame.time.Clock()

    #pymunk init
    space = pymunk.Space()
    space.gravity = 0,5000

    #general init
    balls = []

    #loop
    while Running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Running = False

        #take a physics step
        space.step(1.0/60)

        #fill screen
        screen.fill("black")

        #get mouse position
        mouse_pos = pygame.mouse.get_pos()
        balls.append(Ball((0,255,0),15,mouse_pos,space))
        for ball in balls:
            ball.draw(screen)


        #misc


        #display work onto screen
        pygame.display.flip()

        #fps cap
        clock.tick(60)
