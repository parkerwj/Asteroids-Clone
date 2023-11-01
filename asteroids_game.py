
import random
import arcade
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MOVEMENT_SPEED = 5
BULLET_SPEED = 8
NUM_ROCKS = 5
MIN_ROCK_RADIUS = 10
MAX_ROCK_RADIUS = 50
STARTING_LIVES = 3
STARTING_LEVEL = 1
MAX_LEVEL = 5
ROCK_VELOCITY_BASE = 1
ROCK_VELOCITY_INCREMENT = 0.5
ROCK_RADIUS_BASE = 20
ROCK_RADIUS_INCREMENT = 5
ROCK_NUMBER_BASE = 5
ROCK_NUMBER_INCREMENT = 2

class Ship(arcade.Sprite):
    def __init__(self):
        super().__init__("images/baby.png", center_x=SCREEN_WIDTH/2, center_y=SCREEN_HEIGHT/2)
        self.angle = 0
        self.lives = STARTING_LIVES
        self.change_angle = 0
        self.thrust = 0
        self.width = 50
        self.height = 50

    def update(self):
        self.angle += self.change_angle
        self.center_x += -self.thrust * math.sin(math.radians(self.angle))
        self.center_y += self.thrust * math.cos(math.radians(self.angle))
        if self.center_x < 0:
            self.center_x = SCREEN_WIDTH
        elif self.center_x > SCREEN_WIDTH:
            self.center_x = 0
        if self.center_y < 0:
            self.center_y = SCREEN_HEIGHT
        elif self.center_y > SCREEN_HEIGHT:
            self.center_y = 0

class Bullet(arcade.Sprite):
    def __init__(self, x, y, angle):
        super().__init__("images/laser.png")
        self.center_x = x
        self.center_y = y
        self.velocity_x = -BULLET_SPEED * math.sin(math.radians(angle))
        self.velocity_y = BULLET_SPEED * math.cos(math.radians(angle))
        self.width = 20
        self.height = 20

    def update(self):
        self.center_x += self.velocity_x
        self.center_y += self.velocity_y
        if self.center_x < 0 or self.center_x > SCREEN_WIDTH or self.center_y < 0 or self.center_y > SCREEN_HEIGHT:
            self.kill()

class Rock(arcade.Sprite):
    def __init__(self, x, y, radius, velocity_x, velocity_y):
        super().__init__("images/asteroid.png")
        self.center_x = x
        self.center_y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.width = radius * 2
        self.height = radius * 2

    def update(self):
        self.center_x += self.velocity_x
        self.center_y += self.velocity_y
        if self.center_x < -MAX_ROCK_RADIUS:
            self.center_x = SCREEN_WIDTH + MAX_ROCK_RADIUS
        elif self.center_x > SCREEN_WIDTH + MAX_ROCK_RADIUS:
            self.center_x = -MAX_ROCK_RADIUS
        elif self.center_y < -MAX_ROCK_RADIUS:
            self.center_y = SCREEN_HEIGHT + MAX_ROCK_RADIUS
        elif self.center_y > SCREEN_HEIGHT + MAX_ROCK_RADIUS:
            self.center_y = -MAX_ROCK_RADIUS

class Game(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, "Asteroids Game")
        self.background_texture = arcade.load_texture("images/background.png")
        self.ship_sprite = Ship()
        self.bullet_list = arcade.SpriteList()
        self.rock_list = arcade.SpriteList()
        self.level = STARTING_LEVEL
        self.background_music = arcade.Sound("audio/background_music.mp3")
        self.shoot_sound = arcade.Sound("audio/shoot.wav")
        self.rock_crash_sound = arcade.Sound("audio/explosion.wav")
        self.game_over_sound = arcade.Sound("audio/gameover.wav")
        self.score = 0
        self.game_over_flag = False

    def on_draw(self):
        arcade.start_render()
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT, self.background_texture)
        self.ship_sprite.draw()
        self.bullet_list.draw()
        self.rock_list.draw()
        arcade.draw_text(f"Score: {self.score}", 10, SCREEN_HEIGHT - 40, arcade.color.WHITE, 20)
        arcade.draw_text(f"Level {self.level}", SCREEN_WIDTH - 70, SCREEN_HEIGHT - 30, arcade.color.WHITE, 16)
        arcade.draw_text(f"Lives: {self.ship_sprite.lives}", 10, SCREEN_HEIGHT - 60, arcade.color.RED, 16)

    def on_update(self, delta_time):
        if self.game_over_flag:
            self.game_over()
            return
        self.ship_sprite.update()
        self.bullet_list.update()
        self.rock_list.update()

        for bullet in self.bullet_list:
            rock_list = arcade.check_for_collision_with_list(bullet, self.rock_list)
            if len(rock_list) > 0:
                bullet.kill()
                for rock in rock_list:
                    rock.kill()
                    self.score += 1
                    self.rock_crash_sound.play()

        for rock in self.rock_list:
            if arcade.check_for_collision(self.ship_sprite, rock):
                rock.kill()
                self.rock_crash_sound.play()
                self.ship_sprite.lives -= 1
                if self.ship_sprite.lives <= 0:
                    self.game_over_flag = True
                    self.game_over_sound.play()
                    return
            elif rock.center_x < -MAX_ROCK_RADIUS:
                rock.center_x = SCREEN_WIDTH + MAX_ROCK_RADIUS
            elif rock.center_x > SCREEN_WIDTH + MAX_ROCK_RADIUS:
                rock.center_x = -MAX_ROCK_RADIUS
            elif rock.center_y < -MAX_ROCK_RADIUS:
                rock.center_y = SCREEN_HEIGHT + MAX_ROCK_RADIUS
            elif rock.center_y > SCREEN_HEIGHT + MAX_ROCK_RADIUS:
                rock.center_y = -MAX_ROCK_RADIUS

        if len(self.rock_list) == 0:
            self.level += 1
            for i in range(ROCK_NUMBER_BASE + (self.level-1)*ROCK_NUMBER_INCREMENT):
                x = random.uniform(0, SCREEN_WIDTH)
                y = random.uniform(0, SCREEN_HEIGHT)
                velocity_x = random.uniform(-ROCK_VELOCITY_BASE-self.level*ROCK_VELOCITY_INCREMENT, ROCK_VELOCITY_BASE+self.level*ROCK_VELOCITY_INCREMENT)
                velocity_y = random.uniform(-ROCK_VELOCITY_BASE-self.level*ROCK_VELOCITY_INCREMENT, ROCK_VELOCITY_BASE+self.level*ROCK_VELOCITY_INCREMENT)
                radius = random.uniform(ROCK_RADIUS_BASE+self.level*ROCK_RADIUS_INCREMENT-5, ROCK_RADIUS_BASE+self.level*ROCK_RADIUS_INCREMENT+5)
                rock = Rock(x, y, radius, velocity_x, velocity_y)
                self.rock_list.append(rock)

    def on_key_press(self, key, modifiers):
        if self.game_over_flag and key == arcade.key.ENTER:
            self.game_over_flag = False
            self.new_game()
        elif self.game_over_flag and key == arcade.key.ESCAPE:
            arcade.close_window()
        elif key == arcade.key.LEFT:
            self.ship_sprite.change_angle = 5
        elif key == arcade.key.RIGHT:
            self.ship_sprite.change_angle = -5
        elif key == arcade.key.UP:
            self.ship_sprite.thrust = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.ship_sprite.thrust = -MOVEMENT_SPEED
        elif key == arcade.key.SPACE:
            bullet = Bullet(self.ship_sprite.center_x, self.ship_sprite.center_y, self.ship_sprite.angle)
            self.shoot_sound.play()
            bullet.velocity_x += -BULLET_SPEED * math.sin(math.radians(self.ship_sprite.angle))
            bullet.velocity_y += BULLET_SPEED * math.cos(math.radians(self.ship_sprite.angle))
            self.bullet_list.append(bullet)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.ship_sprite.change_angle = 0
        elif key == arcade.key.UP or key == arcade.key.DOWN:
            self.ship_sprite.thrust = 0

    def on_close(self):
        self.game_over_sound.play()
        arcade.pause(2)
        super().on_close()

    def game_over(self):
        arcade.draw_text("Game Over", SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 20, arcade.color.RED, 36)
        arcade.draw_text("Press ENTER to play again or ESC to quit", SCREEN_WIDTH/2 - 220, SCREEN_HEIGHT/2 - 20, arcade.color.WHITE, 20)

    def new_game(self):
        self.ship_sprite.lives = STARTING_LIVES
        self.level = STARTING_LEVEL
        self.score = 0
        self.rock_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        for i in range(NUM_ROCKS):
            x = random.uniform(0, SCREEN_WIDTH)
            y = random.uniform(0, SCREEN_HEIGHT)
            velocity_x = random.uniform(-ROCK_VELOCITY_BASE-self.level*ROCK_VELOCITY_INCREMENT, ROCK_VELOCITY_BASE+self.level*ROCK_VELOCITY_INCREMENT)
            velocity_y = random.uniform(-ROCK_VELOCITY_BASE-self.level*ROCK_VELOCITY_INCREMENT, ROCK_VELOCITY_BASE+self.level*ROCK_VELOCITY_INCREMENT)
            radius = random.uniform(ROCK_RADIUS_BASE+self.level*ROCK_RADIUS_INCREMENT-5, ROCK_RADIUS_BASE+self.level*ROCK_RADIUS_INCREMENT+5)
            rock = Rock(x, y, radius, velocity_x, velocity_y)
            self.rock_list.append(rock)

    def restart_game(self):
        self.ship_sprite.lives = STARTING_LIVES
        self.level = STARTING_LEVEL
        self.score = 0
        self.rock_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        for i in range(NUM_ROCKS):
            x = random.uniform(0, SCREEN_WIDTH)
            y = random.uniform(0, SCREEN_HEIGHT)
            velocity_x = random.uniform(-ROCK_VELOCITY_BASE-self.level*ROCK_VELOCITY_INCREMENT, ROCK_VELOCITY_BASE+self.level*ROCK_VELOCITY_INCREMENT)
            velocity_y = random.uniform(-ROCK_VELOCITY_BASE-self.level*ROCK_VELOCITY_INCREMENT, ROCK_VELOCITY_BASE+self.level*ROCK_VELOCITY_INCREMENT)
            radius = random.uniform(ROCK_RADIUS_BASE+self.level*ROCK_RADIUS_INCREMENT-5, ROCK_RADIUS_BASE+self.level*ROCK_RADIUS_INCREMENT+5)
            rock = Rock(x, y, radius, velocity_x, velocity_y)
            self.rock_list.append(rock)

def main():
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.background_music.play()
    arcade.run()

if __name__ == "__main__":
    main()