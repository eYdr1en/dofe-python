# Import the pygame module
import pygame, random
import pygame.freetype
import shelve

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

# Define constants for the screen width and height
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 1000

# Initialize font
pygame.freetype.init()

# Set font
font = pygame.freetype.Font(None, 32)

# Get highscore from disk
d = shelve.open("highscore.txt")
try:
    highscore = d["highscore"]  # the score is read from disk
except:
    highscore = 0
    d["highscore"]
d.close()

# Define a player object by extending pygame.sprite.Sprite
# The surface drawn on the screen is now an attribute of 'player'
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.transform.scale(pygame.image.load("raketa.png"), (80, 160))
        self.rect = self.surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT))
        self.score = 0

    # Move the sprite based on user keypresses
    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        # Update score
        self.score += 1


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.transform.scale(pygame.image.load("ufo.png"), (80, 40))
        self.rect = self.surf.get_rect(
            center=(
                random.randint(0, SCREEN_WIDTH),
                -(random.randint(SCREEN_HEIGHT + 20, SCREEN_HEIGHT + 100)),
            )
        )
        self.speed = random.randint(5, 15)

    # Move the sprite based on speed
    # Remove the sprite when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.bottom > SCREEN_HEIGHT:
            self.kill()


# Initialize pygame
pygame.init()

# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

BLUE = (80, 80, 155)

# Function for stats
def stats(score):
    font.render_to(screen, (4, 4), "Score:" + str(score), BLUE, None, size=30)
    font.render_to(screen, (4, 34), "Highscore:" + str(highscore), BLUE, None, size=30)


# Create a custom event for adding a new enemy
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 250)

# Instantiate player. Right now, this is just a rectangle.
player = Player()

# Create groups to hold enemy sprites and all sprites
# - enemies is used for collision detection and position updates
# - all_sprites is used for rendering
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Variable to keep the main loop running
running = True

# Setup the clock for a decent framerate
clock = pygame.time.Clock()

# Main loop
while running:
    # Look at every event in the queue
    for event in pygame.event.get():
        # Did the user hit a key?
        if event.type == KEYDOWN:
            # Was it the Escape key? If so, stop the loop.
            if event.key == K_ESCAPE:
                running = False
        # Did the user click the window close button? If so, stop the loop.
        elif event.type == QUIT:
            running = False

        # Add a new enemy?
        elif event.type == ADDENEMY:
            # Create the new enemy and add it to sprite groups
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)
    # Get the set of keys pressed and check for user input
    pressed_keys = pygame.key.get_pressed()

    # Update the player sprite based on user keypresses
    player.update(pressed_keys)

    # Update enemy position
    enemies.update()

    # Fill the screen with black
    screen.fill((0, 0, 0))

    # Draw all sprites
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    # Check if any enemies have collided with the player
    if pygame.sprite.spritecollideany(player, enemies):
        # If so, then remove the player and stop the loop
        player.kill()
        running = False
        d = shelve.open("highscore.txt")
        if d["highscore"] < player.score:  # here you will save the score variable
            d["highscore"] = player.score  # thats all, now it is saved on disk.
        d.close()

    stats(player.score)
    # Update the display
    pygame.display.flip()
    # Ensure program maintains a rate of 30 frames per second
    clock.tick(30)
