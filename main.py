# ==========================================
# TWO-FACED GAME
# FULL VERSION (WITH HEAVY COMMENTS FOR LEARNING)
# ==========================================

import pygame
import random
import os
import challenge_images as cd

from two_faced_timer import parse_time, format_time, get_time_left

from image_reveal import (
    load_images,
    choose_random_image,
    slide_reveal,
    puzzle_reveal,
    scratch_reveal,
    two_faced_reveal
)

import modes

pygame.init()

# ==========================================
# SCREEN SETUP
# ==========================================

WIDTH, HEIGHT = 800, 600  # # defines game window size
Screen = pygame.display.set_mode((WIDTH, HEIGHT))  # # creates game window
pygame.display.set_caption("🎭 TWO-FACED 🎭")  # # sets window title

# ==========================================
# FONTS
# ==========================================

font = pygame.font.Font(None, 56)  # # big text (titles, input)
small_font = pygame.font.Font(None, 36)  # # smaller UI text

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def normalize(text):
    # # makes text lowercase + clean so comparisons are fair
    return text.lower().strip()

def is_close(a, b):
    # # allows flexible matching instead of strict equality
    a = normalize(a)
    b = normalize(b)
    return a == b or a in b or b in a

def draw_wrapped_text(surface, text, font, color, x, y, max_width):

    words = text.split()
    line = ""

    for word in words:

        test_line = line + word + " "

        if font.size(test_line)[0] <= max_width:
            line = test_line

        else:
            rendered = font.render(line, True, color)
            surface.blit(rendered, (x, y))

            y += font.get_height() + 5

            line = word + " "
    if line:
        rendered = font.render(line, True, color)
        surface.blit(rendered, (x, y))

# ==========================================
# STUDY MODE ENGINE
# ==========================================

class StudyEngine:

    def __init__(self):

        # # load all images used in study mode
        self.images = load_images(WIDTH, HEIGHT)

        # # what the user types for timer input
        self.user_input = ""

        # # how long the countdown runs (in seconds)
        self.countdown = None

        # # when the timer started (pygame time)
        self.start_time = None

        # # marks if a round ended
        self.round_finished = False

        # # counts how many rounds played
        self.study_rounds = 0

        # # pause screen toggle
        self.pause = False

        # # current image being shown
        self.current_image = None

        # # animation style for reveal
        self.current_style = None

        # # available animation types
        self.reveal_styles = ["slide", "puzzle", "scratch", "two_faced"]

    # ======================================
    # RESET STUDY ROUND
    # ======================================
    def reset_round(self):

        # # clears everything so next round starts clean
        self.user_input = ""
        self.countdown = None
        self.start_time = None
        self.round_finished = False
        self.current_image = None
        self.pause = False # Important fix

    # ======================================
    # HANDLE INPUT (STUDY MODE)
    # ======================================
    def handle_event(self, event):

        # # if pause screen is active, only allow menu actions
        if self.pause:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_q:
                    self.pause = False  # resume study
                    self.round_finished = False
                    self.start_time = None
                    self.countdown = None
                    self.current_image = None
                
                elif event.key == pygame.K_p:
                    self.reset_round()
                    return "challenge"   # switch to challenge
                
                elif event.key == pygame.K_b:
                    self.reset_round()
                    return "menu"        # go back to menu

            return None

        # # only handle keyboard input
        if event.type == pygame.KEYDOWN:

            # # if round ended, wait for user to press N
            if self.round_finished and not self.pause:
                if event.key == pygame.K_n:
                    self.reset_round()
                    self.study_rounds += 1

                    # # every 5 rounds, show pause screen
                    if self.study_rounds % 5 == 0:
                        self.pause = True
                return None

            # # if countdown hasn't started yet, user is typing time
            if self.countdown is None:

                if event.key == pygame.K_RETURN:

                    # # convert text input into seconds
                    seconds = parse_time(self.user_input)

                    if seconds:
                        self.countdown = seconds
                        self.start_time = pygame.time.get_ticks()

                        # # pick random image for study round
                        self.current_image = choose_random_image(self.images)

                        # # pick animation style
                        self.current_style = random.choice(self.reveal_styles)

                elif event.key == pygame.K_BACKSPACE:
                    self.user_input = self.user_input[:-1]

                else:
                    # # add typed character to input
                    self.user_input += event.unicode

        return None

    # ======================================
    # UPDATE (STUDY MODE)
    # ======================================
    def update(self):

        # # only update timer if active
        if self.countdown and self.start_time:

            time_left = get_time_left(self.start_time, self.countdown)

            # # if time runs out → round ends
            if time_left <= 0:
                self.countdown = None
                self.start_time = None
                self.round_finished = True

    # ======================================
    # DRAW (STUDY MODE)
    # ======================================
    def draw(self):
        
        if self.pause:

            title = font.render("Study Break!", True, (0,0,0))
            Screen.blit(title, (250, 180))

            Screen.blit(
                small_font.render(
                    "Q = Continue Studying!",
                    True,
                    (0,0,0)
                ),
                (220, 260)
            )

            Screen.blit(
                small_font.render(
                    "P = Go to Challenge Mode!",
                    True,
                    (0,0,0)
                ),
                (220, 310)
            )

            Screen.blit(
                small_font.render(
                    "B = Go to Main Menu!",
                    True,
                    (0,0,0)
                ),
                (220, 360)
            )

            return

        # # show label on screen
        modes.draw_mode_label(Screen, small_font, "Study")

        # # show input or countdown text
        if self.countdown is None:
            text = font.render(f"Enter time: {self.user_input}", True, (0,0,0))
        else:
            time_left = get_time_left(self.start_time, self.countdown)
            text = font.render(f"Countdown: {format_time(time_left)}", True, (0,0,0))

        Screen.blit(
            text, 
            text.get_rect(center=(WIDTH/2, 48))
        )

        # # show image if available
        if self.current_image:

            # # full reveal if no timer running
            if self.countdown is None:
                progress = 1
            else:
                time_left = get_time_left(self.start_time, self.countdown)

                # # calculate reveal progress (0 → 1)
                elapsed = self.countdown - time_left
                progress = elapsed / self.countdown
                progress = max(0.0, min(1.0, progress))

                # # clamp so it NEVER goes below 0 or above 1
                progress = max(0, min(1, progress))

            # # choose correct animation
            if self.current_style == "slide":
                slide_reveal(Screen, self.current_image, progress)

            elif self.current_style == "puzzle":
                puzzle_reveal(Screen, self.current_image, progress)

            elif self.current_style == "scratch":
                scratch_reveal(Screen, self.current_image, progress)

            else:
                two_faced_reveal(Screen, self.current_image, progress)


# ==========================================
# CHALLENGE MODE ENGINE
# ==========================================

class ChallengeEngine:

    def __init__(self):

        # # current challenge image
        self.challenge_image = None

        # # correct answer data
        self.entry = None

        # # user input text
        self.input = ""

        # # score system
        self.score = 0

        # # lives system
        self.hearts = 3

        # # feedback text
        self.feedback = ""

        # # waiting for new round
        self.waiting = True

        # # combo system
        self.combo = 0

        # # difficulty scaling
        self.difficulty = 1

        # # reveal progress (0 → 1)
        self.reveal_progress = 0

        # # animation styles
        self.reveal_styles = ["slide", "puzzle", "scratch", "two_faced"]

        # current animation
        self.current_style = random.choice(self.reveal_styles)

        # current hint text
        self.current_hint = ""

        # hint button rectangle
        self.hint_button = pygame.Rect(20, 120, 100, 35)

        # hint penalty
        self.hint_penalty = 0

    # ======================================
    # SPAWN NEW IMAGE
    # ======================================
    def spawn(self):

        # # pick random challenge
        self.entry = choose_random_image(cd.challenge_images)

        # # build file path
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        filename = self.entry["file"].strip()
        image_path = os.path.join(BASE_DIR, "Assets", filename)

        # # if image doesn't exist → skip
        if not os.path.exists(image_path):
            self.waiting = True
            return

        # # load image
        loaded = pygame.image.load(image_path).convert()

        # # resize image to fit screen
        img_w, img_h = loaded.get_size()
        
        SAFE_TOP = 120
        SAFE_BOTTOM = 160
        max_h = HEIGHT - SAFE_TOP - SAFE_BOTTOM

        scale = min((WIDTH-100)/img_w, max_h/img_h)

        self.challenge_image = pygame.transform.smoothscale(
            loaded,
            (int(img_w*scale), int(img_h*scale))
        )

        # # reset round state
        self.input = ""
        self.feedback = ""
        self.current_hint = ""  # clear old hint
        self.waiting = False
        self.reveal_progress = 0

        # # choose animation style
        self.current_style = random.choice(self.reveal_styles)

    # ======================================
    # INPUT HANDLING
    # ======================================
    def handle_event(self, event):

        # game over check
        if self.hearts <= 0:
            return "game_over"

        # ignore input while waiting
        if self.waiting:
            return None
        
        # ==============================
        # HINT BUTTON CLICK
        # ==============================

        if event.type == pygame.MOUSEBUTTONDOWN:

            if self.hint_button.collidepoint(event.pos):

                if self.entry and "hints" in self.entry:

                    self.current_hint = random.choice(
                        self.entry["hints"]
                    )

                    # player must answer 3 correctly before earning points again
                    self.hint_penalty = 3

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_BACKSPACE:
                self.input = self.input[:-1]

            elif event.key == pygame.K_RETURN:

                # # compare answer
                answer = normalize(self.input)
                correct = normalize(self.entry["answer"])

                if is_close(answer, correct):

                    self.combo += 1

                    # hint penalty check
                    if self.hint_penalty > 0:
                        self.hint_penalty -= 1

                        self.feedback = (
                            f"Correct! {self.hint_penalty} more before scoring"
                        )
                    
                    else:

                        self.score += int(
                            10 * (1 + self.combo * 0.25)
                        )

                        self.feedback = "Correct"

                else:
                    self.hearts -= 1
                    self.combo = 0
                    self.feedback = "Wrong!"

                # # reset for next round
                self.challenge_image = None
                self.waiting = True

            else:
                self.input += event.unicode

        return None

    # ======================================
    # UPDATE CHALLENGE
    # ======================================
    def update(self):

        # # gradually reveal image over time
        if self.challenge_image:
            self.reveal_progress = min(
                1,
                self.reveal_progress + (0.002 + self.difficulty * 0.0005)
            )

    # ======================================
    # DRAW CHALLENGE
    # ======================================
    def draw(self):

        # # UI label
        modes.draw_mode_label(Screen, small_font, "Challenge")

        # # hearts display
        Screen.blit(
            small_font.render("❤️"*self.hearts, True, (0,0,0)),
            (20, 50)
        )

        # score display
        Screen.blit(
            small_font.render(f"Score: {self.score}", True, (0,0,0)),
            (20, 90)
        )

        if self.hint_penalty > 0:

            Screen.blit(
                small_font.render(
                    f"Penalty: {self.hint_penalty}",
                    True,
                    (200,0,0)
                ),
                (20, 170)
            )

        # Hint button
        hint_button = pygame.Rect(20, 120, 100, 35)

        pygame.draw.rect(
            Screen,
            (255, 255, 255),
            hint_button
        )

        pygame.draw.rect(
            Screen,
            (0,0,0),
            hint_button,
            2
        )

        Screen.blit(
            small_font.render("Hint", True, (0,0,0)),
            (35, 127)
        )

        # DISPLAY HINT
        if self.current_hint:
            
            hint_bg = pygame.Rect(
                20,
                HEIGHT - 170,
                260,
                140
            )

            pygame.draw.rect(
                Screen,
                (240, 240, 150),
                hint_bg
            )

            pygame.draw.rect(
                Screen,
                (0, 0, 0),
                hint_bg,
                2
            )

            draw_wrapped_text(
                Screen,
                self.current_hint,
                small_font,
                (0,0,0),
                30,
                HEIGHT - 155,
                240
            )

        # # dynamic textbox (auto grows with text)
        text_surface = font.render(self.input, True, (0,0,0))
        box_width = max(300, text_surface.get_width() + 20)

        box = pygame.Rect(WIDTH//2 - box_width//2, HEIGHT-130, box_width, 50)

        pygame.draw.rect(Screen, (255,255,255), box)
        pygame.draw.rect(Screen, (0,0,0), box, 2)

        Screen.blit(text_surface, (box.x+10, box.y+5))

        # # feedback text
        if self.feedback:
            Screen.blit(font.render(self.feedback, True, (0,0,0)), (WIDTH//2-150, HEIGHT-200))

        # # image reveal
        if self.challenge_image:

            progress = max(0, min(1, self.reveal_progress))

            if self.current_style == "slide":
                slide_reveal(Screen, self.challenge_image, progress)

            elif self.current_style == "puzzle":
                puzzle_reveal(Screen, self.challenge_image, progress)

            elif self.current_style == "scratch":
                scratch_reveal(Screen, self.challenge_image, progress)

            else:
                two_faced_reveal(Screen, self.challenge_image, progress)


# ==========================================
# MAIN LOOP
# ==========================================

clock = pygame.time.Clock()
running = True
game_state = "menu"

study = StudyEngine()
challenge = ChallengeEngine()

study_button = None
challenge_button = None

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if game_state == "menu":
            clicked = modes.check_menu_click(event, study_button, challenge_button)

            if clicked == "study":
                game_state = "study"

            elif clicked == "challenge":
                game_state = "challenge"

        elif game_state == "study":
            result = study.handle_event(event)
            if result:
                game_state = result

        elif game_state == "challenge":
            if challenge.waiting:
                challenge.spawn()

            result = challenge.handle_event(event)
            if result == "game_over":
                game_state = "game_over"

        elif game_state == "game_over":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    challenge = ChallengeEngine()
                    game_state = "challenge"

                elif event.key == pygame.K_m:
                    game_state = "menu"

    # background
    pygame.draw.rect(Screen, (40,40,40), (0,0,WIDTH//2,HEIGHT))
    pygame.draw.rect(Screen, (220,220,220), (WIDTH//2,0,WIDTH//2,HEIGHT))

    if game_state == "menu":
        study_button, challenge_button = modes.draw_menu(Screen, font, small_font)

    elif game_state == "study":
        study.update()
        study.draw()

    elif game_state == "challenge":
        challenge.update()
        challenge.draw()

    elif game_state == "game_over":

        # # game over title
        Screen.blit(font.render("GAME OVER", True, (200,0,0)),
                    (WIDTH//2-120, HEIGHT//3))

        # # instructions so player is NOT stuck
        Screen.blit(small_font.render("Press R = Retry", True, (0,0,0)), (WIDTH//2-120, HEIGHT//2))
        Screen.blit(small_font.render("Press M = Menu", True, (0,0,0)), (WIDTH//2-120, HEIGHT//2+40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()