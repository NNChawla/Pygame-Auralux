import pygame
import random
from os import path

img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

#Screen Constants
WIDTH = 480
HEIGHT = 600
FPS = 60

#Alterable Constants
POWERUP_TIME = 5000 #5 seconds

#define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

#Initializations
pygame.init()
pygame.mixer.init()

#Screen Constant Initializations
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shmup!")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial')
def draw_text(surface, text, size, x, y):
	font = pygame.font.Font(font_name, size)
	text_surface = font.render(text, True, WHITE)
	text_rect = text_surface.get_rect()
	text_rect.midtop = (x, y)
	surface.blit(text_surface, text_rect)
	
def draw_shield_bar(surface, x, y, pct):
	if pct < 0:
		pct = 0
	BAR_LENGTH = 100
	BAR_HEIGHT = 10
	fill = (pct / 100.0) * BAR_LENGTH
	outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
	fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
	pygame.draw.rect(surface, GREEN, fill_rect)
	pygame.draw.rect(surface, WHITE, outline_rect, 2)
	
dic = {}	
def newmob():
	m = Mob();
	all_sprites.add(m);
	mobs.add(m);
	dic[m] = tuple(m.rect);

def loadImage(directory, img_name):
	return pygame.image.load(path.join(directory, img_name)).convert()
	
def draw_lives(surf, x, y, lives, img):
	for i in range(lives):
		img_rect = img.get_rect()
		img_rect.x = x + 30 * i
		img_rect.y = y
		surf.blit(img, img_rect)

def show_go_screen():
	screen.blit(background, background_rect)
	draw_text(screen, "SHMUP!", 64, WIDTH / 2, HEIGHT / 4)
	draw_text(screen, "Arrow keys move, Space to fire", 22, WIDTH / 2.0, HEIGHT / 2.0)
	draw_text(screen, "Press a key to begin", 18, WIDTH/2.0, HEIGHT * 3 / 4.0)
	pygame.display.flip()
	waiting = True
	while waiting:
		clock.tick(FPS)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			if event.type == pygame.KEYUP:
				waiting = False
		
class Player(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(player_img, (50, 38))
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()		
		self.radius = 20
		#pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
		self.rect.centerx = WIDTH/2
		self.rect.bottom = HEIGHT - 10
		self.speedx = 0
		self.shield = 100
		self.shoot_delay = 250
		self.last_shot = pygame.time.get_ticks()
		self.lives = 3
		self.hidden = False
		self.hide_timer = pygame.time.get_ticks()
		self.power = 1
		self.power_time = pygame.time.get_ticks()

	def update(self):
		#timeout for powerups
		if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
			self.power -= 1
			self.power_time = pygame.time.get_ticks()
		
		#unhide if hidden
		if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
			self.hidden = False
			self.rect.centerx = WIDTH/2
			self.rect.bottom = HEIGHT - 10
			
		self.speedx = 0
		keystate = pygame.key.get_pressed()
		if keystate[pygame.K_LEFT]:
			self.speedx = -5
		if keystate[pygame.K_RIGHT]:
			self.speedx = 5
		if keystate[pygame.K_SPACE]:
			self.shoot()
		self.rect.x += self.speedx
		
		if self.rect.right > WIDTH:
			self.rect.right = WIDTH
		if self.rect.left < 0:
			self.rect.left = 0
			
	def shoot(self):
		now = pygame.time.get_ticks()
		if now - self.last_shot > self.shoot_delay:
			self.last_shot = now
			if self.power == 1:		
				bullet = Bullet(self.rect.centerx, self.rect.top)
				all_sprites.add(bullet)
				bullets.add(bullet)
				shoot_sound.play()
			elif self.power >= 2:
				bullet1 = Bullet(self.rect.left, self.rect.centery)
				bullet2 = Bullet(self.rect.right, self.rect.centery)
				all_sprites.add(bullet1)
				all_sprites.add(bullet2)
				bullets.add(bullet1)
				bullets.add(bullet2)
				shoot_sound.play()
	
	def powerup(self):
		self.power += 1
		self.power_time = pygame.time.get_ticks();
	
	def hide(self):
		# hide the player temporarily
		self.hidden = True
		self.hide_timer = pygame.time.get_ticks()
		self.rect.center = (WIDTH/2, HEIGHT + 200)

class Mob(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image_orig = random.choice(meteor_images)
		self.image_orig.set_colorkey(BLACK)
		self.image = self.image_orig.copy()
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.radius = int(self.rect.width * .85 /2)
		
		#pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
		self.rect.x = random.randrange(WIDTH - self.rect.width)
		self.rect.y = random.randrange(-100, -40)
		self.speedy = random.randrange(1, 8)
		self.speedx = random.randrange(-2, 2)
		
		self.rot = 0
		self.rot_speed = random.randrange(-8, 8)
		self.last_update = pygame.time.get_ticks()
	
	def rotate(self):
		now = pygame.time.get_ticks()
		if now - self.last_update > 50:
			self.last_update = now
			self.rot = (self.rot + self.rot_speed) % 360
			new_image = pygame.transform.rotate(self.image_orig, self.rot)
			old_center = self.rect.center
			self.image = new_image
			self.rect = self.image.get_rect()
			self.rect.center = old_center
	
	def update(self):
		self.rotate()
		self.rect.x += self.speedx
		self.rect.y += self.speedy
		if self.rect.top > HEIGHT + 10 or self.rect.left < -40 or self.rect.right > WIDTH + 40:
			self.rect.x = random.randrange(WIDTH - self.rect.width)
			self.rect.y = random.randrange(-150, -100)
			self.speedy = random.randrange(1, 8)
			self.speedx = random.randrange(-2, 2)

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(bullet_img, (10, 15))
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.bottom = y
		self.rect.centerx = x
		self.speedy = -10
		
	def update(self):
		self.rect.y += self.speedy
		#kill if moves off top of screen
		if self.rect.bottom < 0:
			self.kill()
			
class Pow(pygame.sprite.Sprite):
	def __init__(self, center):
		pygame.sprite.Sprite.__init__(self)
		self.type = random.choice(['shield', 'gun'])
		self.image = powerup_images[self.type]
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.speedy = 4
		
	def update(self):
		self.rect.y += self.speedy
		#kill if moves off top of screen
		if self.rect.top < 0:
			self.kill()

class Explosion(pygame.sprite.Sprite):
	def __init__(self, center, size):
		pygame.sprite.Sprite.__init__(self)
		self.size = size
		self.image = explosion_anim[self.size][0]
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.frame = 0
		self.last_update = pygame.time.get_ticks()
		self.frame_rate = 60
	
	def update(self):
		now = pygame.time.get_ticks()
		if now - self.last_update > self.frame_rate:
			self.last_update = now
			self.frame += 1
			if self.frame == len(explosion_anim[self.size]):
				self.kill()
			else:
				center = self.rect.center
				self.image = explosion_anim[self.size][self.frame]
				self.rect.center = center

class RectEnhance(pygame.Rect):
	def __init__(self, i):
		super(RectEnhance, self).__init__(i)
		#self.image = pygame.Surface(
		self.orbit = 0
				
#load all game graphics
background = loadImage(img_dir, 'starfield.png');
background_rect = background.get_rect()
player_img = loadImage(img_dir, 'playerShip1_red.png');
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = loadImage(img_dir, 'laserRed16.png');
meteor_images = []
meteor_list = ["meteorBrown_big1.png", "meteorBrown_big2.png",
"meteorBrown_med1.png", "meteorBrown_med2.png",
"meteorBrown_small1.png", "meteorBrown_small2.png",
"meteorBrown_tiny1.png"]
for img in meteor_list:
	meteor_images.append(loadImage(img_dir, img));
	
powerup_images = {}
powerup_images['shield'] = loadImage(img_dir, 'shield_gold.png');
powerup_images['shield'].set_colorkey(BLACK)
powerup_images['gun'] = loadImage(img_dir, 'bolt_gold.png');
powerup_images['gun'].set_colorkey(BLACK)
	
#explosion animation
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
	filename = 'regularExplosion0{}.png'.format(i)
	img = pygame.image.load(path.join(img_dir, filename)).convert()
	img.set_colorkey(BLACK)
	img_lg = pygame.transform.scale(img, (75, 75))
	explosion_anim['lg'].append(img_lg)
	img_sm = pygame.transform.scale(img, (32, 32))
	explosion_anim['sm'].append(img_sm)
	filename = 'sonicExplosion0{}.png'.format(i)
	img = pygame.image.load(path.join(img_dir, filename)).convert()
	img.set_colorkey(BLACK)
	explosion_anim['player'].append(img)
	

#load all game sounds
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'laserSound.wav'))
expl_sounds = []
for snd in ['meteorXplosion.wav', 'meteorXplosion2.wav']:
	expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))

player_die_sound = pygame.mixer.Sound(path.join(snd_dir, 'rumble1.ogg'))
pygame.mixer.music.load(path.join(snd_dir, 'latency.ogg'))
pygame.mixer.music.set_volume(0.6)

pygame.mixer.music.play(loops=-1)
	
#Game Loop
running = True
game_over = True
		
while running:
	if game_over: 
		show_go_screen()
		game_over = False
		all_sprites = pygame.sprite.Group()
		mobs = pygame.sprite.Group()
		bullets = pygame.sprite.Group() 
		powerups = pygame.sprite.Group()
		player = Player()
		shipRect = RectEnhance(player)
		all_sprites.add(player)
		for i in range(8):
			newmob()
			print dic
		score = 0
		
	#keep loop running at the right speed
	clock.tick(FPS)
	
	#Process input (events)
	for event in pygame.event.get():
		#check for click on close window button
		if event.type == pygame.QUIT:
			running = False
	
	#Update
	all_sprites.update()
	
	#check to see if bullet hit a mob
	hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
	if len(hits) > 0:
		print hits
	for hit in hits:
		score += 60 - hit.radius
		#play explosion sound
		random.choice(expl_sounds).play()
		expl = Explosion(hit.rect.center, 'lg')
		all_sprites.add(expl)
		newmob() 
		if random.random() > 0.9:
			pow = Pow(hit.rect.center)
			all_sprites.add(pow)
			powerups.add(pow)
	
	#check to see if a mob hit the player
	hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
	for hit in hits:
		player.shield -= hit.radius * 2
		expl = Explosion(hit.rect.center, 'sm')
		all_sprites.add(expl)
		newmob()
		if player.shield <= 0:
			player_die_sound.play()
			death_explosion = Explosion(player.rect.center, 'player')
			all_sprites.add(death_explosion)
			player.hide()
			player.lives -= 1
			player.shield = 100
	
	#check to see if player collides with powerup
	hits = pygame.sprite.spritecollide(player, powerups, True)
	for hit in hits:
		if hit.type == 'shield':
			player.shield += random.randrange(10, 30);
			if player.shield >= 100:
					player.shield = 100;
		if hit.type == 'gun':
			player.powerup()
			
	# if player has died and explosion finished
	if player.lives == 0 and not death_explosion.alive():
		game_over = True
	
	hits = shipRect.collidedictall(dic)
	if len(hits) > 0:
		for i in hits:
			i[0].image.fill(GREEN)
		"""hits[0].image = pygame.Surface((50,40))
		hits[0].image.fill(GREEN)
		pygame.draw.rect(hits[0]."""
	
	#Draw / Render
	screen.fill(BLACK)
	screen.blit(background, background_rect)
	all_sprites.draw(screen)
	draw_text(screen, str(score), 18, WIDTH/2, 10)
	draw_shield_bar(screen, 5, 5, player.shield)
	draw_lives(screen, WIDTH-100, 5, player.lives, player_mini_img)
	pygame.draw.rect(screen, RED, shipRect, 2)
	
	#AFTER drawing everything, display it on the screen
	pygame.display.flip()
	
pygame.quit()
