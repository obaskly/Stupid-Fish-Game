import pygame
from pygame.locals import *
import random

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption('Sea World')

background_image = pygame.image.load('bg.jpg').convert()

def show_start_menu(screen, font):
    text = font.render("Press ENTER to start", True, (255, 255, 255))
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2))

def show_game_over(screen, font, score):
    text = font.render(f"Game Over - Score: {score}", True, (255, 255, 255))
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2))
    text2 = font.render("Press ENTER to restart", True, (255, 255, 255))
    screen.blit(text2, (screen_width // 2 - text2.get_width() // 2, screen_height // 2 + 40))

class Level:
    def __init__(self):
        self.level = 1
        self.font = pygame.font.Font(None, 36)

    def update(self, player_fish):
        if player_fish.growth >= 10:
            self.level += 1
            player_fish.growth = 0 

    def draw(self, screen):
        text = self.font.render(f'Level: {self.level}', True, (255, 255, 255))
        screen.blit(text, (700, 10))
        
class Score:
    def __init__(self):
        self.score = 0
        self.font = pygame.font.Font(None, 36)

    def update(self, player_fish):
        self.score = player_fish.growth

    def draw(self, screen):
        text = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
        screen.blit(text, (10, 10))

score_display = Score()

class Fish(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path, size, speed, level):
        super().__init__()
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = scale_image(self.original_image, size)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = speed
        self.speed_y = speed
        self.level = level
        self.base_speed = speed
        
    def distance_to_player(self, player):
        dx = self.rect.x - player.rect.x
        dy = self.rect.y - player.rect.y
        return (dx ** 2 + dy ** 2) ** 0.5
        
    def can_be_eaten_by(self, player_fish):
        return (
            isinstance(self, SmallFish) and player_fish.growth >= 0
            or isinstance(self, MediumFish) and player_fish.growth >= 5
            or isinstance(self, LargeFish) and player_fish.growth >= 10
        )

    def update(self, player_fish):
        self.speed = self.base_speed * self.level.level
        if self.can_be_eaten_by(player_fish) and self.distance_to_player(player_fish) < 150:
            dx = self.rect.x - player_fish.rect.x
            dy = self.rect.y - player_fish.rect.y
            escape_speed_x = (dx / (abs(dx) + abs(dy))) * self.speed * 2.0  
            escape_speed_y = (dy / (abs(dx) + abs(dy))) * self.speed * 2.0

            self.rect.x += escape_speed_x
            self.rect.y += escape_speed_y

            if self.rect.left < 0 or self.rect.right > screen_width:
                self.rect.x = screen_width // 2
            if self.rect.top < 0 or self.rect.bottom > screen_height:
                self.rect.y = screen_height // 2
        else:
            self.rect.x += self.speed

            if self.rect.x > screen_width:
                self.rect.x = -self.rect.width

class SmallFish(Fish):
    def __init__(self, x, y, level):
        super().__init__(x, y, 'small_fish.png', 30, random.randint(1, 3), level)

class MediumFish(Fish):
    def __init__(self, x, y, level):
        super().__init__(x, y, 'medium_fish.png', 60, random.randint(1, 2), level)

class LargeFish(Fish):
    def __init__(self, x, y, level):
        super().__init__(x, y, 'large_fish.png', 90, random.randint(1, 1), level)

class PlayerFish(Fish):
    def __init__(self, x, y, level):
        super().__init__(x, y, 'player_fish.png', 30, 5, level)
        self.growth = 0
        self.lost = False
        self.acceleration_x = 0
        self.acceleration_y = 0
        self.velocity_x = 0
        self.velocity_y = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.acceleration_y = -0.1
        elif keys[pygame.K_DOWN]:
            self.acceleration_y = 0.1
        else:
            self.acceleration_y = 0

        if keys[pygame.K_LEFT]:
            self.acceleration_x = -0.1
        elif keys[pygame.K_RIGHT]:
            self.acceleration_x = 0.1
        else:
            self.acceleration_x = 0

    def can_eat(self, fish):
        return (
            isinstance(fish, SmallFish) and self.growth >= 0
            or isinstance(fish, MediumFish) and self.growth >= 5
            or isinstance(fish, LargeFish) and self.growth >= 10
        )

    def grow(self):
        self.growth += 1
        new_width = self.rect.width + 5
        self.image = scale_image(self.original_image, new_width)
        self.rect = self.image.get_rect(center=self.rect.center)

    def move_up(self):
        self.rect.y -= 3

    def move_down(self):
        self.rect.y += 3

    def move_left(self):
        self.rect.x -= 3

    def move_right(self):
        self.rect.x += 3
        
    def update(self, _=None):
        self.velocity_x += self.acceleration_x
        self.velocity_y += self.acceleration_y

        self.velocity_x = max(min(self.velocity_x, self.speed_x), -self.speed_x)
        self.velocity_y = max(min(self.velocity_y, self.speed_y), -self.speed_y)

        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity_x = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
            self.velocity_x = 0
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.velocity_y = 0

def scale_image(image, new_width):
    width, height = image.get_size()
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width)
    return pygame.transform.scale(image, (new_width, new_height))
    
def check_collision(player_fish, fishes):
    collisions = pygame.sprite.spritecollide(player_fish, fishes, False)

    for fish in collisions:
        if player_fish.can_eat(fish):
            player_fish.grow()
            fish.kill()

            fish_type = type(fish)
            x = random.randrange(screen_width)
            y = random.randrange(screen_height)

            if fish_type == SmallFish:
                new_fish = SmallFish(x, y, level)
            elif fish_type == MediumFish:
                new_fish = MediumFish(x, y, level)
            else:
                new_fish = LargeFish(x, y, level)

            fishes.add(new_fish)
        elif not fish.can_be_eaten_by(player_fish):
            player_fish.lost = True

fishes = pygame.sprite.Group()

level = Level()  

for _ in range(20):
    fish_type = random.choice(['small', 'medium', 'large'])
    x = random.randrange(screen_width)
    y = random.randrange(screen_height)

    if fish_type == 'small':
        fish = SmallFish(x, y, level)
    elif fish_type == 'medium':
        fish = MediumFish(x, y, level)
    else:
        fish = LargeFish(x, y, level)

    fishes.add(fish)

player_fish = PlayerFish(screen_width // 2, screen_height // 2, level)
score_display = Score()

def main():
    global player_fish, fishes, level
    player_fish = PlayerFish(screen_width // 2, screen_height // 2, level)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player_fish.handle_input()

        check_collision(player_fish, fishes)

        fishes.update(player_fish)

        screen.blit(background_image, (0, 0))
        fishes.draw(screen)

        level.update(player_fish)
        level.draw(screen)

        score_display.update(player_fish)
        score_display.draw(screen)

        player_fish.update(player_fish)
        screen.blit(player_fish.image, player_fish.rect)

        pygame.display.flip()
        pygame.time.Clock().tick(60)

        if player_fish.lost:
            break

    if player_fish.lost:
        return "game_over"
    else:
        return "exit"

main_font = pygame.font.Font(None, 36)
game_state = "start_menu"
while game_state != "exit":
    if game_state == "start_menu":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state = "exit"
            if event.type == KEYDOWN and event.key == K_RETURN:
                player_fish = PlayerFish(screen_width // 2, screen_height // 2, level)
                score_display = Score()
                game_state = main()

        screen.blit(background_image, (0, 0))
        show_start_menu(screen, main_font)
        pygame.display.flip()
        pygame.time.Clock().tick(60)

    if game_state == "game_over":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state = "exit"
            if event.type == KEYDOWN and event.key == K_RETURN:
                player_fish = PlayerFish(screen_width // 2, screen_height // 2, level)
                game_state = main()

        screen.blit(background_image, (0, 0))
        show_game_over(screen, main_font, score_display.score)
        pygame.display.flip()
        pygame.time.Clock().tick(60)

pygame.quit()