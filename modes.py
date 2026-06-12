# ==========================================
# MODES SYSTEM FOR TWO-FACED
# ==========================================
# Handles:
# - Intro menu screen
# - Study Mode button
# - Challenge Mode button
# - Button hover effects
# - Mouse click detection
# - Returning selected mode
# ==========================================

import pygame
import os
import random
from challenge_images import challenge_images

# ====================== COLORS ======================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (220, 220, 220)

BLUE = (70, 130, 255)
GREEN = (60, 180, 75)

HOVER_BLUE = (100, 160, 255)
HOVER_GREEN = (90, 210, 105)

# ====================== BUTTON SIZE ======================
BUTTON_WIDTH = 260
BUTTON_HEIGHT = 70

# ====================== DRAW MENU ======================
def draw_menu(screen, font, small_font):
    """
    Draw the intro menu screen.
    """

    width = screen.get_width()
    height = screen.get_height()

    # Background split screen
    pygame.draw.rect(screen, DARK_GRAY, (0, 0, width // 2, height))
    pygame.draw.rect(screen, LIGHT_GRAY, (width // 2, 0, width // 2, height))

    # Title text
    title = font.render("What's your motive?", True, BLACK)
    title_rect = title.get_rect(center=(width // 2, 120))
    screen.blit(title, title_rect)

    # Create buttons
    study_button = pygame.Rect(
        (width - BUTTON_WIDTH) // 2,
        240,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )

    challenge_button = pygame.Rect(
        (width - BUTTON_WIDTH) // 2,
        350,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )

    # Get mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Hover effect for Study button
    if study_button.collidepoint(mouse_x, mouse_y):
        study_color = HOVER_BLUE
    else:
        study_color = BLUE

    # Hover effect for Challenge button
    if challenge_button.collidepoint(mouse_x, mouse_y):
        challenge_color = HOVER_GREEN
    else:
        challenge_color = GREEN

    # Draw buttons
    pygame.draw.rect(screen, study_color, study_button, border_radius=12)
    pygame.draw.rect(screen, challenge_color, challenge_button, border_radius=12)

    # Button text
    study_text = small_font.render("Study Mode", True, WHITE)
    challenge_text = small_font.render("Challenge Mode", True, WHITE)

    screen.blit(
        study_text,
        study_text.get_rect(center=study_button.center)
    )

    screen.blit(
        challenge_text,
        challenge_text.get_rect(center=challenge_button.center)
    )

    # Return button rectangles so main.py can detect clicks
    return study_button, challenge_button


# ====================== CHECK MENU CLICK ======================
def check_menu_click(event, study_button, challenge_button):
    """
    Detect if player clicked one of the buttons.
    Returns:
        "study"
        "challenge"
        None
    """

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:  # Left click

            mouse_pos = event.pos

            if study_button.collidepoint(mouse_pos):
                return "study"

            if challenge_button.collidepoint(mouse_pos):
                return "challenge"

    return None


# ====================== DRAW MODE LABEL ======================
def draw_mode_label(screen, small_font, mode_name):
    """
    Small helper label for top-left corner.
    """

    text = small_font.render(f"Mode: {mode_name}", True, BLACK)
    screen.blit(text, (15, 15))

# ====================== GET RANDOM CHALLENGE IMAGE ======================
def load_challenge_entry():

    # Pick random challenge from database
    entry = random.choice(challenge_images)

    # Build safe image path
    image_path = os.path.join(
        "Assets",
        entry["file"]
    )

    # Return BOTH:
    # - challenge data
    # - image location
    return entry, image_path