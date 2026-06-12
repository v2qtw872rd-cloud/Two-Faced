# ==========================================
# IMAGE REVEAL SYSTEM FOR TWO-FACED
# ==========================================
# Now supports TWO animation modes:
#
# 1. External control (old system):
#    progress (0 → 1 from main.py)
#
# 2. Internal timing (NEW optional system):
#    start_time + duration
#
# IMPORTANT:
# - Backward compatible
# - No changes required in main.py
# ==========================================

import pygame
import os
import random

# ==========================================
# SAFETY HELPER (FOOLPROOF)
# ==========================================
def safe_subsurface(image, rect):

    img_width, img_height = image.get_size()

    x = max(0, rect.x)
    y = max(0, rect.y)

    w = max(1, min(rect.width, img_width - x))
    h = max(1, min(rect.height, img_height - y))

    return image.subsurface((x, y, w, h))


# ==========================================
# EASING FUNCTION (SMOOTH ANIMATION)
# ==========================================
def ease_in_out(p):

    p = max(0.0, min(1.0, p))
    return p * p * (3 - 2 * p)


# ==========================================
# INTERNAL PROGRESS CALCULATOR (NEW)
# ==========================================
# If start_time + duration are provided,
# this calculates smooth progress automatically.
# ==========================================
def calc_progress(progress=None, start_time=None, duration=None):

    # MODE 1: external control (your current system)
    if progress is not None:
        return ease_in_out(progress)

    # MODE 2: internal timing system
    if start_time is not None and duration is not None:

        now = pygame.time.get_ticks()
        elapsed = (now - start_time) / 1000

        p = elapsed / duration
        return ease_in_out(p)

    # fallback safety
    return 0.0


# ====================== LOAD IMAGES ======================
def load_images(screen_width=800, screen_height=600):

    images = []
    supported = (".png", ".jpg", ".webp", ".jpeg")

    current_folder = os.path.dirname(os.path.abspath(__file__))
    assets_folder = os.path.join(current_folder, "Assets")

    if not os.path.exists(assets_folder):
        raise FileNotFoundError(f"Assets folder not found at {assets_folder}")

    print("Files in assets folder:")

    for file in os.listdir(assets_folder):
        print("  ", file)

    for file in os.listdir(assets_folder):

        if file.lower().endswith(supported):

            path = os.path.join(assets_folder, file)

            try:
                image = pygame.image.load(path).convert()

                target_width = 500
                target_height = 300

                iw, ih = image.get_size()

                scale_factor = min(
                    target_width / iw,
                    target_height / ih
                )

                image = pygame.transform.smoothscale(
                    image,
                    (int(iw * scale_factor),
                     int(ih * scale_factor))
                )

                print(f"Loaded image: {file}, size: {image.get_size()}")

                print("Width:", image.get_width())
                print("Height:", image.get_height())

                images.append(image)

            except pygame.error as e:
                print(f"Failed to load {file}: {e}")

    if len(images) == 0:

        fallback = pygame.Surface((520, 360))
        fallback.fill((255, 0, 0))

        print("No images found! Using fallback.")

        images.append(fallback)

    return images


# ====================== RANDOM IMAGE ======================
def choose_random_image(images):

    if len(images) == 0:
        return None

    return random.choice(images)

# ===================== GET IMAGE POSITION ==================
def get_image_position(screen, image):
    
    width, height = image.get_size()

    top_ui_height = 100
    bottom_ui_height = 150

    available_space = (
        screen.get_height()
        - top_ui_height
        - bottom_ui_height
    )

    x = (screen.get_width() - width) // 2
    y = top_ui_height + (available_space - height) // 2

    return x, y


# ====================== SLIDE REVEAL ======================
# Reveals from left ----> right
def slide_reveal(screen, image, progress=None, start_time=None, duration=None):

    progress = calc_progress(progress, start_time, duration)

    width, height = image.get_size()

    reveal_width = max(1, int(width * progress))
    reveal_width = min(reveal_width, width)

    rect = pygame.Rect(0, 0, reveal_width, height)

    piece = safe_subsurface(image, rect)

    x, y = get_image_position(screen, image)

    screen.blit(piece, (x, y))


# ====================== PUZZLE REVEAL ======================
# Reveals image tile-by-tile in a grid pattern
def puzzle_reveal(screen, image, progress=None, start_time=None, duration=None):

    progress = calc_progress(progress, start_time, duration)

    width, height = image.get_size()

    cols, rows = 8, 6

    tile_w = max(1, width // cols)
    tile_h = max(1, height // rows)

    total_tiles = cols * rows
    tiles_to_show = max(1, int(total_tiles * progress))

    x, y = get_image_position(screen, image)

    tile_count = 0

    for row in range(rows):
        for col in range(cols):

            if tile_count >= tiles_to_show:
                return

            rect = pygame.Rect(
                col * tile_w,
                row * tile_h,
                tile_w,
                tile_h
            )

            piece = safe_subsurface(image, rect)

            screen.blit(
                piece,
                (x + col * tile_w,
                 y + row * tile_h)
            )

            tile_count += 1


# ====================== SCRATCH REVEAL ======================
# Reveals by gray overlay that "scratches off" to show the image underneath, gray overlay fades away gradually
def scratch_reveal(screen, image, progress=None, start_time=None, duration=None):

    progress = calc_progress(progress, start_time, duration)

    width, height = image.get_size()

    x, y = get_image_position(screen, image)

    screen.blit(image, (x, y))

    overlay = pygame.Surface((width, height))
    overlay.fill((180, 180, 180))

    alpha = int(255 * (1 - progress))
    overlay.set_alpha(alpha)

    screen.blit(overlay, (x, y))


# ====================== TWO-FACED REVEAL ======================
# Reveals from center outwards, like two curtains opening from the middle
def two_faced_reveal(screen, image, progress=None, start_time=None, duration=None):

    progress = calc_progress(progress, start_time, duration)

    width, height = image.get_size()

    # Center of the image
    image_center = width // 2

    # Width of revealed section
    reveal_width = max(1, int(width * progress))

    # Calculation for left edge of revealed area
    left_edge = image_center - (reveal_width // 2)

    # Keep inside image bounds
    left_edge = max(0, left_edge)

    reveal_width = min(reveal_width, width)

    rect = pygame.Rect(
        left_edge,
        0,
        reveal_width,
        height
    )

    visible_piece = safe_subsurface(image, rect)

    x, y = get_image_position(screen, image)

    # Shift piece so it appears in correct location
    screen.blit(
        visible_piece,
        (x + left_edge, y)
    )