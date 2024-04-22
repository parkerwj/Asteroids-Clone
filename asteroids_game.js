
const SCREEN_WIDTH = 800;
const SCREEN_HEIGHT = 600;
const MOVEMENT_SPEED = 5;
const BULLET_SPEED = 8;
const NUM_ROCKS = 5;
const MIN_ROCK_RADIUS = 10;
const MAX_ROCK_RADIUS = 50;
const STARTING_LIVES = 3;
const STARTING_LEVEL = 1;
const MAX_LEVEL = 5;
const ROCK_VELOCITY_BASE = 1;
const ROCK_VELOCITY_INCREMENT = 0.5;
const ROCK_RADIUS_BASE = 20;
const ROCK_RADIUS_INCREMENT = 5;
const ROCK_NUMBER_BASE = 5;
const ROCK_NUMBER_INCREMENT = 2;

class Ship extends Arcade.Sprite {
  constructor() {
    super({
      x: SCREEN_WIDTH / 2,
      y: SCREEN_HEIGHT / 2,
      texture: "images/ship.png",
      width: 50,
      height: 50,
    });
    this.angle = 0;
    this.lives = STARTING_LIVES;
    this.change_angle = 0;
    this.thrust = 0;
  }

  update() {
    this.angle += this.change_angle;
    this.x += -this.thrust * Math.sin(Math.radians(this.angle));
    this.y += this.thrust * Math.cos(Math.radians(this.angle));
    if (this.x < 0) {
      this.x = SCREEN_WIDTH;
    } else if (this.x > SCREEN_WIDTH) {
      this.x = 0;
    }
    if (this.y < 0) {
      this.y = SCREEN_HEIGHT;
    } else if (this.y > SCREEN_HEIGHT) {
      this.y = 0;
    }
  }
}

class Bullet extends Arcade.Sprite {
  constructor(x, y, angle) {
    super({
      x,
      y,
      texture: "images/bullet.png",
      width: 20,
      height: 20,
    });
    this.velocity_x = -BULLET_SPEED * Math.sin(Math.radians(angle));
    this.velocity_y = BULLET_SPEED * Math.cos(Math.radians(angle));
  }

  update() {
    this.x += this.velocity_x;
    this.y += this.velocity_y;
    if (
      this.x < 0 ||
      this.x > SCREEN_WIDTH ||
      this.y < 0 ||
      this.y > SCREEN_HEIGHT
    ) {
      this.kill();
    }
  }
}

class Rock extends Arcade.Sprite {
  constructor(x, y, radius, velocity_x, velocity_y) {
    super({
      x,
      y,
      texture: "images/rock.png",
      width: radius * 2,
      height: radius * 2,
    });
    this.velocity_x = velocity_x;
    this.velocity_y = velocity_y;
  }

  update() {
    this.x += this.velocity_x;
    this.y += this.velocity_y;
    if (this.x < -MAX_ROCK_RADIUS) {
      this.x = SCREEN_WIDTH + MAX_ROCK_RADIUS;
    } else if (this.x > SCREEN_WIDTH + MAX_ROCK_RADIUS) {
      this.x = -MAX_ROCK_RADIUS;
    } else if (this.y < -MAX_ROCK_RADIUS) {
      this.y = SCREEN_HEIGHT + MAX_ROCK_RADIUS;
    } else if (this.y > SCREEN_HEIGHT + MAX_ROCK_RADIUS) {
      this.y = -MAX_ROCK_RADIUS;
    }
  }
}

class Game extends Arcade.Window {
  constructor(width, height) {
    super(width, height, "Asteroids Game");
    this.background_texture = this.loadTexture("images/background.png");
    this.ship_sprite = new Ship();
    this.bullet_list = new Arcade.SpriteList();
    this.rock_list = new Arcade.SpriteList();
    this.level = STARTING_LEVEL;
    this.background_music = this.loadSound("audio/background_music.mp3");
    this.shoot_sound = this.loadSound("audio/shoot_sound.wav");
    this.rock_crash_sound = this.loadSound("audio/rock_crash_sound.wav");
    this.game_over_sound = this.loadSound("audio/game_over_sound.wav");
    this.score = 0;
    this.game_over_flag = false;
  }

  onDraw() {
    this.startRender();
    this.drawTextureRectangle(
      SCREEN_WIDTH / 2,
      SCREEN_HEIGHT / 2,
      SCREEN_WIDTH,
      SCREEN_HEIGHT,
      this.background_texture,
    );
    this.ship_sprite.draw();
    this.bullet_list.draw();
    this.rock_list.draw();
    this.drawText(
      `Score: ${this.score}`,
      10,
      SCREEN_HEIGHT - 40,
      Arcade.color.WHITE,
      20,
    );
    this.drawText(
      `Level ${this.level}`,
      SCREEN_WIDTH - 70,
      SCREEN_HEIGHT - 30,
      Arcade.color.WHITE,
      16,
    );
    this.drawText(
      `Lives: ${this.ship_sprite.lives}`,
      10,
      SCREEN_HEIGHT - 60,
      Arcade.color.RED,
      16,
    );
  }

  onUpdate(deltaTime) {
    if (this.game_over_flag) {
      this.gameOver();
      return;
    }
    this.ship_sprite.update();
    this.bullet_list.update();
    this.rock_list.update();

    for (let bullet of this.bullet_list) {
      let rock_list = this.checkForCollisionWithList(bullet, this.rock_list);
      if (rock_list.length > 0) {
        bullet.kill();
        for (let rock of rock_list) {
          rock.kill();
          this.score += 1;
          this.rock_crash_sound.play();
        }
      }
    }

    for (let rock of this.rock_list) {
      if (this.checkForCollision(this.ship_sprite, rock)) {
        rock.kill();
        this.rock_crash_sound.play();
        this.ship_sprite.lives -= 1;
        if (this.ship_sprite.lives <= 0) {
          this.game_over_flag = true;
          this.game_over_sound.play();
          return;
        }
      } else if (rock.x < -MAX_ROCK_RADIUS) {
        rock.x = SCREEN_WIDTH + MAX_ROCK_RADIUS;
      } else if (rock.x > SCREEN_WIDTH + MAX_ROCK_RADIUS) {
        rock.x = -MAX_ROCK_RADIUS;
      } else if (rock.y < -MAX_ROCK_RADIUS) {
        rock.y = SCREEN_HEIGHT + MAX_ROCK_RADIUS;
      } else if (rock.y > SCREEN_HEIGHT + MAX_ROCK_RADIUS) {
        rock.y = -MAX_ROCK_RADIUS;
      }
    }

    if (this.rock_list.length === 0) {
      this.level += 1;
      for (let i = 0; i < ROCK_NUMBER_BASE + (this.level - 1) * ROCK_NUMBER_INCREMENT; ++i) {
        let x = Math.random() * SCREEN_WIDTH;
        let y = Math.random() * SCREEN_HEIGHT;
        let velocity_x = Math.random() *
          (-ROCK_VELOCITY_BASE - this.level * ROCK_VELOCITY_INCREMENT,
          ROCK_VELOCITY_BASE + this.level * ROCK_VELOCITY_INCREMENT);
        let velocity_y = Math.random() *
          (-ROCK_VELOCITY_BASE - this.level * ROCK_VELOCITY_INCREMENT,
          ROCK_VELOCITY_BASE + this.level * ROCK_VELOCITY_INCREMENT);
        let radius = Math.random() *
          (ROCK_RADIUS_BASE + this.level * ROCK_RADIUS_INCREMENT - 5,
          ROCK_RADIUS_BASE + this.level * ROCK_RADIUS_INCREMENT + 5);
        let rock = new Rock(x, y, radius, velocity_x, velocity_y);
        this.rock_list.append(rock);
      }
    }
  }

  onKeyPress(key, modifiers) {
    if (this.game_over_flag && key == Arcade.key.ENTER) {
      this.game_over_flag = false;
      this.newGame();
    } else if (this.game_over_flag && key == Arcade.key.ESCAPE) {
      this.closeWindow();
    } else if (key == Arcade.key.LEFT) {
      this.ship_sprite.change_angle = 5;
    } else if (key == Arcade.key.RIGHT) {
      this.ship_sprite.change_angle = -5;
    } else if (key == Arcade.key.UP) {
      this.ship_sprite.thrust = MOVEMENT_SPEED;
    } else if (key == Arcade.key.DOWN) {
      this.ship_sprite.thrust = -MOVEMENT_SPEED;
    } else if (key == Arcade.key.SPACE) {
      let bullet = new Bullet(
        this.ship_sprite.x,
        this.ship_sprite.y,
        this.ship_sprite.angle,
      );
      this.shoot_sound.play();
      bullet.velocity_x += -BULLET_SPEED *
        Math.sin(Math.radians(this.ship_sprite.angle));
      bullet.velocity_y += BULLET_SPEED *
        Math.cos(Math.radians(this.ship_sprite.angle));
      this.bullet_list.append(bullet);
    }
  }

  onKeyRelease(key, modifiers) {
    if (key == Arcade.key.LEFT || key == Arcade.key.RIGHT) {
      this.ship_sprite.change_angle = 0;
    } else if (key == Arcade.key.UP || key == Arcade.key.DOWN) {
      this.ship_sprite.thrust = 0;
    }
  }

  onClose() {
    this.game_over_sound.play();
    Arcade.pause(2);
    super.onClose();
  }

  gameOver() {
    this.drawText(
      "Game Over",
      SCREEN_WIDTH / 2 - 100,
      SCREEN_HEIGHT / 2 + 20,
      Arcade.color.RED,
      36,
    );
    this.drawText(
      "Press ENTER to play again or ESC to quit",
      SCREEN_WIDTH / 2 - 220,
      SCREEN_HEIGHT / 2 - 20,
      Arcade.color.WHITE,
      20,
    );
  }

  newGame() {
    this.ship_sprite.lives = STARTING_LIVES;
    this.level = STARTING_LEVEL;
    this.score = 0;
    this.rock_list = new Arcade.SpriteList();
    this.bullet_list = new Arcade.SpriteList();
    for (let i = 0; i < NUM_ROCKS; ++i) {
      let x = Math.random() * SCREEN_WIDTH;
      let y = Math.random() * SCREEN_HEIGHT;
      let velocity_x = Math.random() *
        (-ROCK_VELOCITY_BASE - this.level * ROCK_VELOCITY_INCREMENT,
        ROCK_VELOCITY_BASE + this.level * ROCK_VELOCITY_INCREMENT);
      let velocity_y = Math.random() *
        (-ROCK_VELOCITY_BASE - this.level * ROCK_VELOCITY_INCREMENT,
        ROCK_VELOCITY_BASE + this.level * ROCK_VELOCITY_INCREMENT);
      let radius = Math.random() *
        (ROCK_RADIUS_BASE + this.level * ROCK_RADIUS_INCREMENT - 5,
        ROCK_RADIUS_BASE + this.level * ROCK_RADIUS_INCREMENT + 5);
      let rock = new Rock(x, y, radius, velocity_x, velocity_y);
      this.rock_list.append(rock);
    }
  }

  restartGame() {
    this.ship_sprite.lives = STARTING_LIVES;
    this.level = STARTING_LEVEL;
    this.score = 0;
    this.rock_list = new Arcade.SpriteList();
    this.bullet_list = new Arcade.SpriteList();
    for (let i = 0; i < NUM_ROCKS; ++i) {
      let x = Math.random() * SCREEN_WIDTH;
      let y = Math.random() * SCREEN_HEIGHT;
      let velocity_x = Math.random() *
        (-ROCK_VELOCITY_BASE - this.level * ROCK_VELOCITY_INCREMENT,
        ROCK_VELOCITY_BASE + this.level * ROCK_VELOCITY_INCREMENT);
      let velocity_y = Math.random() *
        (-ROCK_VELOCITY_BASE - this.level * ROCK_VELOCITY_INCREMENT,
        ROCK_VELOCITY_BASE + this.level * ROCK_VELOCITY_INCREMENT);
      let radius = Math.random() *
        (ROCK_RADIUS_BASE + this.level * ROCK_RADIUS_INCREMENT - 5,
        ROCK_RADIUS_BASE + this.level * ROCK_RADIUS_INCREMENT + 5);
      let rock = new Rock(x, y, radius, velocity_x, velocity_y);
      this.rock_list.append(rock);
    }
  }
}

function main() {
  const game = new Game(SCREEN_WIDTH, SCREEN_HEIGHT);
  game.background_music.play();
  Arcade.run();
}

if (typeof require != "undefined" && require.main == module) {
  main();
}
