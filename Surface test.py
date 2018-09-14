#Pygame Template for new Pygame Project
import pygame
import random
from math import pi

#Screen Constants
WIDTH = 360
HEIGHT = 480
FPS = 60

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
pygame.display.set_caption("Template")
clock = pygame.time.Clock()

#Game Loop
running = True

class Player(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface((10,10))
		self.image.fill(GREEN)
		self.rect = self.image.get_rect()
		self.radius = 5
		self.rect.centerx = 200#WIDTH /2
		self.rect.centery = 310#HEIGHT - 20
		self.circ = pygame.Rect(WIDTH/2-45, HEIGHT-80, 90, 80)

all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)		

coords = []
selectRect = 0
def selRect():
	global coords, selectRect

	keystate = pygame.key.get_pressed()
	mousestate = pygame.mouse.get_pressed()
	
	if keystate[pygame.K_s] and mousestate[0]:
			coords.append(pygame.mouse.get_pos())
			#print coords
			tempRect = pygame.Rect(0, 0, 0, 0)
			tempRect.width = coords[len(coords)-1][0] - coords[0][0]
			tempRect.height = coords[len(coords)-1][1] - coords[0][1]
			tempRect.topleft = coords[0]
			tempRect.bottomright = coords[len(coords)-1]
			selectRect = tempRect
			
	else:
		coords = []
		selectRect = pygame.Rect(0, 0, 0, 0)

count = 0
sec = 0
def func(radius, x1, y1):
	global sec, count
	sec = pygame.time.get_ticks()
	#print count
	if count < radius:
		player.rect.move_ip(1,0)
		quadrant = 0
	elif count >= radius and count < radius*3:
		player.rect.move_ip(-1,0)
		quadrant = 1
	elif count >= radius*3 and count < radius*4:
		player.rect.move_ip(1,0)
		quadrant = 0
	elif count == radius*4:
		count = -1
		quadrant = 0
	x2 = player.rect.centerx
	#print str(x2) + " " + str(x1) + " " + str(count)
	
	if quadrant:
		y2 = (((radius**2) - ((x2 - x1)**2))**0.5)+y1
		y2 = 2*y1 - y2
	else:
		y2 = (((radius**2) - ((x2 - x1)**2))**0.5)+y1
	player.rect.centery = y2
	count += 1

coor = []	
r = pygame.Rect(0,0,0,0)
r.centerx = 100
r.centery = 100
r.size = (50,50)

for i in range(r.topright[0]-r.width, r.topright[0]):
	for j in range(r.bottomright[1]-r.height, r.bottomright[1]):
		coor.append((i,j))

while running:
	#keep loop running at the right speed
	clock.tick(FPS)
	
	#Process input (events)
	for event in pygame.event.get():
	
		#check for click on close window button
		if event.type == pygame.QUIT:
			running = False
		if event.type == pygame.MOUSEBUTTONUP:
			a = pygame.mouse.get_pos()
			if a in coor:
				print "YES"
			
	#Update
	if pygame.time.get_ticks() - sec > 20:
		func(60, 200, 250)
		
	selRect()
	lis = [player.rect]
	hits = selectRect.collidelist(lis)
	if hits != -1:
		print hits
	if pygame.key.get_pressed()[pygame.K_s]:
		print "true"
	
	#Draw / Render
	screen.fill(BLACK)
	all_sprites.draw(screen)
	"""pygame.draw.rect(screen, YELLOW, player.rect, player.radius)
	pygame.draw.rect(screen, RED, player.circ, 2)
	pygame.draw.circle(screen, (200, 200, 200), (50,100), 20, 6)	pygame.draw.circle(screen, YELLOW, (200, 300), 10)
	rect = pygame.Rect(200, 300, 40, 40)
	rect.centerx = 200
	rect.centery = 300
	pygame.draw.rect(screen, RED, rect, 3)
	pygame.draw.ellipse(screen, BLUE, rect, 5)
	pygame.draw.arc(screen, (200, 200, 200), rect, pi/2, pi+pi/2.0, 5)
	x = pygame.draw.circle(screen, YELLOW, (300, 300), 4)"""
	pygame.draw.rect(screen, RED, selectRect, 3)
	pygame.draw.circle(screen, (255, 0, 255), (200, 250), 50)
	pygame.draw.circle(screen, RED, (50, 50), 1)
	rect = pygame.draw.circle(screen, RED, (100, 200), 1)
	pygame.draw.rect(screen, YELLOW, r, 1)
	
	#AFTER drawing everything, display it on the screen
	pygame.display.flip()
	
pygame.quit()