
import random
import arcade
import math
from flask import Flask, render_template, request

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
        super().__init__("static/images/ship.png", center_x=SCREEN_WIDTH/2, center_y=SCREEN_HEIGHT/2)
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
        super().__init__("static/images/bullet.png")
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
        super().__init__("static/images/rock.png")
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

class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ship_sprite = Ship()
        self.bullet_list = arcade.SpriteList()
        self.rock_list = arcade.SpriteList()
        self.level = STARTING_LEVEL
        self.score = 0
        self.game_over_flag = False
        self.background_music = arcade.Sound("audio/background_music.mp3")
        self.shoot_sound = arcade.Sound("audio/shoot_sound.wav")
        self.rock_crash_sound = arcade.Sound("audio/rock_crash_sound.wav")
        self.game_over_sound = arcade.Sound("audio/game_over_sound.wav")
        self.new_game()

    def new_game(self):
        # Reset game state for a new game
        self.ship_sprite.lives = STARTING_LIVES
        self.level = STARTING_LEVEL
        self.score = 0
        self.rock_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        for i in range(NUM_ROCKS):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            velocity_x = random.uniform(-ROCK_VELOCITY_BASE-self.level*ROCK_VELOCITY_INCREMENT, ROCK_VELOCITY_BASE+self.level*ROCK_VELOCITY_INCREMENT)
            velocity_y = random.uniform(-ROCK_VELOCITY_BASE-self.level*ROCK_VELOCITY_INCREMENT, ROCK_VELOCITY_BASE+self.level*ROCK_VELOCITY_INCREMENT)
            radius = random.uniform(ROCK_RADIUS_BASE+self.level*ROCK_RADIUS_INCREMENT-5, ROCK_RADIUS_BASE+self.level*ROCK_RADIUS_INCREMENT+5)
            rock = Rock(x, y, radius, velocity_x, velocity_y)
            self.rock_list.append(rock)

    def update(self, dt):
        # Update game state for a given time interval (dt)
        if self.game_over_flag:
            return
        self.ship_sprite.update()
        self.bullet_list.update()
        self.rock_list.update()
        # Check for collisions and update score
        for bullet in self.bullet_list:
            rock_list = arcade.check_for_collision_with_list(bullet, self.rock_list)
            if len(rock_list) > 0:
                bullet.kill()
                for rock in rock_list:
                    rock.kill()
                    self.score += 1
                    self.rock_crash_sound.play()
        # Check for collisions with ship and update lives
        for rock in self.rock_list:
            if arcade.check_for_collision(self.ship_sprite, rock):
                rock.kill()
                self.rock_crash_sound.play()
                self.ship_sprite.lives -= 1
                if self.ship_sprite.lives <= 0:
                    self.game_over_flag = True
                    self.game_over_sound.play()
                    return
        # Advance to next level if all rocks are destroyed
        if len(self.rock_list) == 0:
            self.level += 1
            for i in range(ROCK_NUMBER_BASE + (self.level-1)*ROCK_NUMBER_INCREMENT):
                x = random.uniform(0, self.width)
                y = random.uniform(0, self.height)
                velocity_x = random.uniform(-ROCK_VELOCITY_BASE-self.level*ROCK_VELOCITY_INCREMENT, ROCK_VELOCITY_BASE+self.level*ROCK_VELOCITY_INCREMENT)
                velocity_y = random.uniform(-ROCK_VELOCITY_BASE-self.level*ROCK_VELOCITY_INCREMENT, ROCK_VELOCITY_BASE+self.level*ROCK_VELOCITY_INCREMENT)
                radius = random.uniform(ROCK_RADIUS_BASE+self.level*ROCK_RADIUS_INCREMENT-5, ROCK_RADIUS_BASE+self.level*ROCK_RADIUS_INCREMENT+5)
                rock = Rock(x, y, radius, velocity_x, velocity_y)
                self.rock_list.append(rock)

    def render(self):
        # Render the game in an HTML canvas
        canvas = f"""
        <canvas id="gameCanvas" width="{self.width}" height="{self.height}"></canvas>
        <script>
        // Define assets
        var shipImage = new Image();
        shipImage.src = "static/images/ship.png";
        var bulletImage = new Image();
        bulletImage.src = "static/images/bullet.png";
        var rockImage = new Image();
        rockImage.src = "static/images/rock.png";
        var backgroundImage = new Image();
        backgroundImage.src = "static/images/background.png";
        // Define game variables
        var canvas = document.getElementById("gameCanvas");
        var ctx = canvas.getContext("2d");
        var score = {self.score};
        var level = {self.level};
        var lives = {self.ship_sprite.lives};
        // Load background image
        backgroundImage.onload = function() {{
            ctx.drawImage(backgroundImage, 0, 0);
        }};
        // Render ship sprite
        ctx.save();
        ctx.translate({self.ship_sprite.center_x}, {self.height - self.ship_sprite.center_y});
        ctx.rotate(-{math.radians(self.ship_sprite.angle)});
        ctx.drawImage(shipImage, -{self.ship_sprite.width/2}, -{self.ship_sprite.height/2}, {self.ship_sprite.width}, {self.ship_sprite.height});
        ctx.restore();
        // Render bullets
        for(var i=0; i<{len(self.bullet_list)}; i++) {{
            var bullet = {self.bullet_list[i]};
            ctx.drawImage(bulletImage, bullet.center_x-bullet.width/2, {self.height}-bullet.center_y-bullet.height/2, bullet.width, bullet.height);
        }}
        // Render rocks
        for(var i=0; i<{len(self.rock_list)}; i++) {{
            var rock = {self.rock_list[i]};
            ctx.drawImage(rockImage, rock.center_x-rock.width/2, {self.height}-rock.center_y-rock.height/2, rock.width, rock.height);
        }}
        // Render score, level, and lives
        ctx.font = "20px Arial";
        ctx.fillStyle = "white";
        ctx.fillText("Score: "+score, 10, 30);
        ctx.fillText("Level: "+level, {self.width}-100, 30);
        ctx.fillStyle = "red";
        ctx.fillText("Lives: "+lives, 10, 60);
        </script>
        """
        return canvas

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("game.html")

@app.route("/update", methods=["POST"])
def update():
    game.update(1/60)
    return game.render()

if __name__ == "__main__":
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.background_music.play()
    app.run(debug=True, threaded=True)
