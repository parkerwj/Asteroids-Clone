const SCREEN_WIDTH = 800;
const SCREEN_HEIGHT = 600;
const MOVEMENT_SPEED = 80;
const BULLET_SPEED = 300; // Increased laser speed

const gameConfig = {
  type: Phaser.AUTO,
  width: SCREEN_WIDTH,
  height: SCREEN_HEIGHT,
  physics: {
    default: 'arcade',
    arcade: {
      debug: false,
    },
  },
  scene: {
    preload: preload,
    create: create,
    update: update,
  },
};

const game = new Phaser.Game(gameConfig);

function preload() {
  this.load.image('background', 'images/background.png');
  this.load.image('ship', 'images/player.png');
  this.load.image('laser', 'images/laser.png');
  this.load.image('asteroid', 'images/asteroid.png');
  this.load.audio('background_music', 'audio/background_music.mp3');
  this.load.audio('shoot_sound', 'audio/shoot.wav');
  this.load.audio('rock_crash_sound', 'audio/explosion.wav');
  this.load.audio('game_over_sound', 'audio/gameover.wav');
}

let ship;
let bullets;
let rocks;
let cursors;
let score = 0;
let level = 1;
let lives = 3;
let gameover = false;
let backgroundMusic;
let shootSound;
let rockCrashSound;
let gameOverSound;
let livesText;
let levelText;
let scoreText;
let gameoverScreen;
let gameoverText;
let restartText;
let quitText;


function create() {
  backgroundMusic = this.sound.add('background_music');
  backgroundMusic.play({ loop: true });

  shootSound = this.sound.add('shoot_sound');
  rockCrashSound = this.sound.add('rock_crash_sound');
  gameOverSound = this.sound.add('game_over_sound');

    // Create a game over screen
    gameoverScreen = this.add.rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0x000000, 0.8);
    gameoverScreen.setOrigin(0, 0);
    gameoverScreen.setInteractive(); // Enable interaction
  
    gameoverText = this.add.text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 'Game Over', {
      fontSize: '36px',
      fill: '#ff0000',
    });
    gameoverText.setOrigin(0.5, 0.5);
    gameoverText.visible = false;
  
    restartText = this.add.text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40, 'Press ENTER to play again', {
      fontSize: '20px',
      fill: '#ffffff',
    });
    restartText.setOrigin(0.5, 0.5);
    restartText.visible = false;
  
    quitText = this.add.text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 80, 'Press Q to quit', {
      fontSize: '20px',
      fill: '#ffffff',
    });
    quitText.setOrigin(0.5, 0.5);
    quitText.visible = false;
  

  restartText = this.add.text(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40, 'Press ENTER to play again or ESC to quit', {
    fontSize: '20px',
    fill: '#ffffff',
  });
  restartText.setOrigin(0.5, 0.5);
  restartText.visible = false; // Initially hidden

  this.add.image(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 'background');

  ship = this.physics.add.sprite(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 'ship');
  ship.setCollideWorldBounds(true);
  ship.setScale(0.1);

  bullets = this.physics.add.group();
  rocks = this.physics.add.group();

  this.physics.add.collider(bullets, rocks, bulletHitRock, null, this);

  // Add a collision event between the ship and rocks
  this.physics.add.collider(ship, rocks, shipHitRock, null, this);

  cursors = this.input.keyboard.createCursorKeys();

  this.input.keyboard.on('keydown-SPACE', shootBullet);
  livesText = this.add.text(10, 10, `Lives: ${lives}`, {
    fontSize: '20px',
    fill: '#ffffff',
  });
  levelText = this.add.text(10, 40, `Level: ${level}`, {
    fontSize: '20px',
    fill: '#ffffff',
  });
  scoreText = this.add.text(10, 70, `Score: ${score}`, {
    fontSize: '20px',
    fill: '#ffffff',
  });

  newGame();
}

function update() {
  if (gameover) {
    return;
  }

  if (cursors.left.isDown) {
    ship.angle -= 5;
  } else if (cursors.right.isDown) {
    ship.angle += 5;
  }

  if (cursors.up.isDown) {
    // Move the ship forward in the direction it's facing
    this.physics.velocityFromRotation(ship.rotation + 80, MOVEMENT_SPEED * 2, ship.body.velocity);
  } else if (cursors.down.isDown) {
    // Move the ship backward in the opposite direction it's facing
    this.physics.velocityFromRotation(ship.rotation + Math.PI + 80, MOVEMENT_SPEED * 2, ship.body.velocity);
  } else {
    ship.setAcceleration(0);
    ship.setVelocity(0);
  }
  // Update lives, level, and score text
  livesText.setText(`Lives: ${lives}`);
  levelText.setText(`Level: ${level}`);
  scoreText.setText(`Score: ${score}`);


  rocks.children.iterate((rock) => {
    if (rock.x < -rock.width / 2) {
      rock.x = SCREEN_WIDTH + rock.width / 2;
    } else if (rock.x > SCREEN_WIDTH + rock.width / 2) {
      rock.x = -rock.width / 2;
    }

    if (rock.y < -rock.height / 2) {
      rock.y = SCREEN_HEIGHT + rock.height / 2;
    } else if (rock.y > SCREEN_HEIGHT + rock.height / 2) {
      rock.y = -rock.height / 2;
    }
  });
}

function shootBullet() {
  if (gameover) return;

  const bullet = bullets.create(ship.x, ship.y, 'laser');
  const angle = Phaser.Math.DegToRad(ship.angle - 90);
  const velocityX = Math.cos(angle) * BULLET_SPEED;
  const velocityY = Math.sin(angle) * BULLET_SPEED;

  bullet.body.setVelocity(velocityX, velocityY);
  bullet.angle = ship.angle;
  bullet.setScale(0.05); // Adjust the scale to make the laser smaller
  shootSound.play();
}

function shipHitRock(ship, rock) {
  rockCrashSound.play();
  rock.destroy();
  loseLife();
}
function loseLife() {
  lives--;
  if (lives <= 0) {
    gameOver();
  }
}


function bulletHitRock(bullet, rock) {
  rockCrashSound.play();
  bullet.destroy();
  rock.destroy();
  score++;
  if (rocks.countActive() === 0) {
    level++;
    spawnRocks();
  }
}

function spawnRocks() {
  for (let i = 0; i < level * 5; i++) {
    let x = Phaser.Math.Between(0, SCREEN_WIDTH);
    let y = Phaser.Math.Between(0, SCREEN_HEIGHT);
    let velocityX = Phaser.Math.Between(-level - 1, level + 1) * MOVEMENT_SPEED;
    let velocityY = Phaser.Math.Between(-level - 1, level + 1) * MOVEMENT_SPEED;
    let radius = Phaser.Math.Between(
      10 + (level - 1) * 5,
      50 + (level - 1) * 5
    );
    let rock = rocks.create(x, y, 'asteroid');
    rock.setScale(radius / 100);
    rock.setVelocity(velocityX, velocityY);
  }
}

function gameOver() {
  gameover = true;
  backgroundMusic.stop();
  gameOverSound.play();

  gameoverText.visible = true;
  restartText.visible = true;
  quitText.visible = true;
  gameoverScreen.visible = true;

  game.input.keyboard.on('keydown-ENTER', () => {
    restartGame();
  });

  game.input.keyboard.on('keydown-Q', () => {
    // Handle quitting the game here, e.g., redirect to the main menu.
  });
}

function newGame() {
  lives = 3;
  level = 1;
  score = 0;
  gameover = false;
  rocks.clear(true, true);
  bullets.clear(true, true);
  spawnRocks();
}

function restartGame() {
  lives = 3;
  level = 1;
  score = 0;
  gameover = false;
  rocks.clear(true, true);
  bullets.clear(true, true);
  spawnRocks();

  // Hide the game over screen and options
  gameoverText.visible = false;
  restartText.visible = false;
  quitText.visible = false;
  gameoverScreen.visible = false;

  // Restart the background music
  backgroundMusic.play({ loop: true });
}