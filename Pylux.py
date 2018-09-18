import pygame
import random
from os import path
from math import pi

#setting path to image directory
img_dir = path.join(path.dirname(__file__), 'img')

#Screen Constants
WIDTH = 1280
HEIGHT = 720
FPS = 30

#define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 200, 255)
YELLOW = (255, 255, 0)
GREY = (200, 200, 200)
PINK = (255, 0, 255)

#Game Constants
SECOND = 1500

#Initializations
pygame.init()
pygame.mixer.init()

#Screen Constant Initializations
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.set_alpha(None)
pygame.display.set_caption("Orpheum")
clock = pygame.time.Clock()

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(BLACK)

#Global Variables
unitRects = {} #for collision checks of units
unitTravel = {}
coords = []
planetList = []
selectRect = pygame.Rect(0,0,0,0)

#Functions
def newUnit(x, y, source, iD, unitCount = 0):
	"""Generates a new unit for specified source"""
	unit = Unit(x, y, source, iD, unitCount)
	all_sprites.add(unit)
	unitRects[unit] = tuple(unit.rect)
	
def newPlanet(x, y, id, rings):
	"""Generates a planet either bound to a player or neutral"""
	planet = Planet(x, y, id, rings)
	all_sprites.add(planet)
	planets.add(planet)
	planetList.append(planet)
	
font_name = pygame.font.match_font('arial')
def draw_text(surface, text, size, x, y):
	"""displays text to the screen"""
	font = pygame.font.Font(font_name, size)
	text_surface = font.render(text, True, WHITE)
	text_rect = text_surface.get_rect(centerx = surface.get_width()/2)
	surface.blit(text_surface, text_rect)

def unitKill(unit):
	"""completely removes unit from lists"""
	unit.kill()
	unit.remove(all_sprites)
	if unit in unitRects:
		del unitRects[unit]
	if unit in unitTravel:
		del unitTravel[unit]

def loadImage(directory, img_name):
	"""loads immage image from current directory"""
	return pygame.image.load(path.join(directory, img_name)).convert()

def unitSelect(): #needs collision check with units
	"""Draws selection rectangle that selects and highlights any units it collides with"""
	global coords, selectRect

	keystate = pygame.key.get_pressed()
	mousestate = pygame.mouse.get_pressed()
	
	if keystate[pygame.K_s] and mousestate[0]:
			coords.append(pygame.mouse.get_pos())
			tempRect = pygame.Rect(0, 0, 0, 0)
			if coords[len(coords)-1][1] > coords[0][1] and coords[len(coords)-1][0] > coords[0][0]:	
				tempRect.width = coords[len(coords)-1][0] - coords[0][0]
				tempRect.height = coords[len(coords)-1][1] - coords[0][1]
				tempRect.topleft = coords[0]
				tempRect.bottomright = coords[len(coords)-1]
			elif coords[len(coords)-1][1] > coords[0][1] and coords[len(coords)-1][0] < coords[0][0]:	
				tempRect.width = coords[0][0] - coords[len(coords)-1][0]
				tempRect.height = coords[len(coords)-1][1] - coords[0][1]
				tempRect.topright = coords[0]
				tempRect.bottomleft = coords[len(coords)-1]
			elif coords[len(coords)-1][1] < coords[0][1] and coords[len(coords)-1][0] > coords[0][0]:	
				tempRect.width = coords[len(coords)-1][0] - coords[0][0]
				tempRect.height = coords[0][1] - coords[len(coords)-1][1]
				tempRect.bottomleft = coords[0]
				tempRect.topright = coords[len(coords)-1]
			elif coords[len(coords)-1][1] < coords[0][1] and coords[len(coords)-1][0] < coords[0][0]:	
				tempRect.width = coords[0][0] - coords[len(coords)-1][0]
				tempRect.height = coords[0][1] - coords[len(coords)-1][1]
				tempRect.bottomright = coords[0]
				tempRect.topleft = coords[len(coords)-1]
			selectRect = tempRect
			
	else:
		coords = []
		selectRect = pygame.Rect(0, 0, 0, 0)

#Classes
class Planet(pygame.sprite.Sprite):
	"""
	
	This class generates a planet object with methods to upgrade itself and generate units
	
	"""
	def __init__(self, spawnX, spawnY, piD = 0, rings = 0):
		pygame.sprite.Sprite.__init__(self)

		if piD == 0:
			self.color = WHITE
		elif piD == 1:
			self.color = BLUE
		elif piD == 2:
			self.color = RED
		elif piD == 3:
			self.color = GREEN
		else:
			self.color = PINK

		self.image = pygame.Surface((40,40)).convert()
		self.radius = 20
		self.image.fill(self.color)
		self.rect = pygame.Rect(0,0,0,0)
		self.rect.centerx = spawnX
		self.rect.centery = spawnY
		self.rect.width = self.radius*2
		self.rect.height = self.radius*2

		self.planetiD = piD
		self.modifier = 0
		self.unitsInOrbit = 0
		self.orbitList = []
		self.upgradeStatus = 0
		self.ringNumber = rings
		self.ringState = 0
		self.rings = []
		self.claimStatus = 0
		self.state = 0 #0 for inactive, 1 for active
		self.unitProdDelay = pygame.time.get_ticks()
		self.selected = False #whether it's been clicked or not
		#self.unitLimit = 200

		if self.claimStatus == 0 and self.planetiD != 0:
				self.claimStatus = 100

	def update(self):
		"""Every cycle of the game loop, executes these commands"""
		
		#planet claimStatus depleted, planetiD becomes 0
		if self.claimStatus == 0:
			self.planetiD = 0
			self.image.fill(WHITE)

		#State
		if self.planetiD > 0:
			self.state = 1
			self.image.fill(self.color)
		else:
			self.state = 0 #COLLISION CHECK change playeriD to unitiD when claimStatus > 0

		#While planet is active
		if self.state == 1:

			if pygame.time.get_ticks() - self.unitProdDelay > SECOND:
				self.unitProduction(self.ringState, self.modifier)

			if self.selected:
				self.image.fill(YELLOW)
				keystate = pygame.key.get_pressed()
				if keystate[pygame.K_q]:
					self.selected = False
					self.image.fill(self.color)

			keystate = pygame.key.get_pressed()
			if keystate[pygame.K_u] and self.selected:
				self.upgrade()
				self.selected = False
				self.image.fill(self.color)

	def unitProduction(self, rings, modifier):
		"""Based on the rings of a planet, produces a set number of units"""
		self.unitProdDelay = pygame.time.get_ticks()
		unitRate = rings+1 * 2 + modifier
		count = 1
		##if self.unitsInOrbit < self.unitLimit:
		for unit in range(unitRate):
			if count%2 == 0:
				position = -(self.radius+10)
				initialCount = 68
			else:
				position = self.radius+10
				initialCount = 0
			newUnit(self.rect.centerx, self.rect.centery + position, self, self.planetiD, initialCount)
			count += 1

	def upgrade(self): #needs to fix claim status first
		"""removes units from orbit of planet and upgrades rings based on amount of units stored"""
		tbkill = self.unitsInOrbit

		if self.claimStatus < 100:
			self.unitsInOrbit -= (100-self.claimStatus)
			if self.unitsInOrbit < 0:
				self.unitsInOrbit = 0
			self.claimStatus += tbkill
			if self.claimStatus > 100:
				self.claimStatus = 100
				
			unwanted = set()
			for i in range(tbkill - self.unitsInOrbit):
				unitKill(self.orbitList[i])
				unwanted.add(self.orbitList[i])
			self.orbitList = [i for i in self.orbitList if i not in unwanted]
			
		overflow = False
		if self.ringNumber == 0:
			return
			
		elif self.upgradeStatus < 100:
			self.unitsInOrbit -= (100-self.upgradeStatus)
			if self.unitsInOrbit < 0:
				self.unitsInOrbit = 0
			self.upgradeStatus += tbkill
			if self.upgradeStatus > 100 and self.upgradeStatus < 200:
				self.upgradeStatus = 100
			elif self.upgradeStatus >= 200:
				overflow = True
		
		if self.upgradeStatus == 100 and not(overflow):
			if self.ringNumber - self.ringState < 0:
				return
			self.ringState += 1
			if self.ringNumber - self.ringState > 0:
				self.modifier += 2
				self.upgradeStatus = self.unitsInOrbit
			elif self.ringNumber - self.ringState == 0:
				self.modifier += 2
		elif overflow:
			if self.ringNumber - self.ringState < 0:
				return
			self.ringState += tbkill/100
			if self.ringNumber - self.ringState > 0:
				for i in range(tbkill/100):
					self.modifier += 2
				self.upgradeStatus = self.unitsInOrbit
			elif self.ringNumber - self.ringState == 0:
				self.modifier += 2

		unwanted = set()
		for i in range(tbkill-self.unitsInOrbit):
			unitKill(self.orbitList[i])
			unwanted.add(self.orbitList[i])
		self.orbitList = [i for i in self.orbitList if i not in unwanted]

	def drawRings(self, rings, status):
		"""Displays rings around planet"""
		for i in range(self.ringNumber):
			self.rings.append(self.rect.inflate(self.radius*2+i*10, self.radius*2+i*10))
		for i in range(rings):
			rect = self.rings[i]
			pygame.draw.ellipse(screen, GREY, rect, 2)
			if i > self.ringState:
				endPoint = pi/2.0
			else:
				endPoint = (status/100.0)*2*pi + pi/2.0
			pygame.draw.arc(screen, self.color, rect, pi/2.0, endPoint , 2)
			"""if i == self.ringState:
				break""" #TBA for hidden rings

	def drawClaimStatus(self, status):
		"""Draws fill percentage of rings around planet"""
		rect = self.rect.inflate(self.radius, self.radius)
		pygame.draw.ellipse(screen, GREY, rect, 2)
		pygame.draw.arc(screen, self.color, rect, pi/2.0, (status/100.0)*2*pi + pi/2.0, 2)

class Unit(pygame.sprite.Sprite):
	
	"""
	
	This class generates a single unit bound to a specific player with methods to travel and enter orbit
	
	"""
	
	def __init__(self, spawnX, spawnY, source, uiD = 0, count = 0):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface((2,2)).convert()
		self.image.fill(source.color)
		self.radius = 1
		self.rect = pygame.draw.circle(screen, source.color, (spawnX, spawnY), 1)
		self.speedx = 2
		self.speedy = 2
		
		self.unitiD = uiD
		self.selected = False
		self.traveling = False
		self.orbiting = True #only true when collide with own planet or spawning
		self.state = 0 #TBA features
		self.source = source #planet object //when 0, unit is not bound to orbit
		self.color = source.color
		self.coords = []
		self.count = count
		self.orbitDelay = 0
		
		self.source.unitsInOrbit += 1
		self.source.orbitList.append(self)
	
	def update(self):
		"""Every cycle of the game loop, executes these commands"""
		global unitTravel
		if self.selected:			
			self.image.fill(YELLOW)
			mousestate = pygame.mouse.get_pressed()
			keystate = pygame.key.get_pressed()
			if mousestate[0] and selectRect == (0,0,0,0): #click where you want units to go
				self.coords = pygame.mouse.get_pos()
				self.travel(self.coords[0], self.coords[1])
				self.traveling = True
				self.selected = False
				self.image.fill(self.color)
				unitTravel[self] = tuple(self.rect)
				if self.source != 0:
					self.source.orbitList.remove(self)
					self.source.unitsInOrbit -= 1
					self.source = 0
					self.orbiting = False
			elif keystate[pygame.K_q] and selectRect == (0,0,0,0): #press q to cancel a selection
				self.selected = False
				self.image.fill(self.color)
		if self.traveling:
			self.travel(self.coords[0], self.coords[1])
		if self.orbiting:
			if pygame.time.get_ticks() - self.orbitDelay > 50:
				self.enterOrbit(self.source)
		
	#called when selected and moved
	def travel(self, x, y):
		"""Moves the unit towards the point specified by the player when the unit is selected"""
		global unitTravel
		if self.rect.centerx < x:
			if x - self.rect.centerx > 10:
				self.rect.move_ip(self.speedx,0)
			else:
				self.rect.move_ip(1,0)
		elif self.rect.centerx > x:
			if self.rect.centerx - x > 10:
				self.rect.move_ip(-self.speedx,0)
			else:
				self.rect.move_ip(-1,0)
			
		if self.rect.centery < y:
			if y - self.rect.centery > 10:
				self.rect.move_ip(0,self.speedy)
			else:
				self.rect.move_ip(0,1)
		elif self.rect.centery > y:
			if self.rect.centery - y > 10:
				self.rect.move_ip(0,-self.speedy)
			else:
				self.rect.move_ip(0,-1)
		if self.rect.centerx == x and self.rect.centery == y:
			self.traveling = False
			del unitTravel[self]
			
		
	#NEEDS to have function for when collides with claimed planet
	def enterOrbit(self, source):
		"""In place of an animation, moves unit around the planet in an apparent orbit"""
		radius = source.radius+14
		
		self.orbitDelay = pygame.time.get_ticks()
		if self.count < radius:
			self.rect.move_ip(1,0)
			quadrant = 0
		elif self.count >= radius and self.count < radius*3:
			self.rect.move_ip(-1,0)
			quadrant = 1
		elif self.count >= radius*3 and self.count < radius*4:
			self.rect.move_ip(1,0)
			quadrant = 0
		elif self.count == radius*4:
			self.count = -1
			quadrant = 0
		x2 = self.rect.centerx
		if radius**2 - (x2-source.rect.centerx)**2 < 0:
			print str(x2) + " " + str(self.count)
		
		if quadrant:
			y2 = (((radius**2) - ((x2 - source.rect.centerx)**2))**0.5)+source.rect.centery
			y2 = 2*source.rect.centery - y2
		else:
			y2 = (((radius**2) - ((x2 - source.rect.centerx)**2))**0.5)+source.rect.centery
		self.rect.centery = y2
		self.count += 1
		
all_sprites = pygame.sprite.Group()
planets = pygame.sprite.Group()

for i in range(6):
	newPlanet(i*100+150, i*100+150, 0, random.randrange(0, 3))
for i in range(3):
	newPlanet(i*200+250, i*200+150, i+1, random.randrange(0,2))

planetCoords = []
for p in planetList:
	coor = []
	for i in range(p.rect.topright[0]-p.rect.width, p.rect.topright[0]):
		for j in range(p.rect.bottomright[1]-p.rect.height, p.rect.bottomright[1]):
			coor.append((i,j))
	planetCoords.append(coor)
"""
correction = []
for planet in planets:
	for i in correction:
		distance = (((planet.rect.centerx-i[0])**2)+((planet.rect.centery-i[1])**2)**0.5)
		if distance < planet.radius*2:
			planet.rect.centerx = ((((planet.radius*3)**2) - ((planet.rect.centery - i[1])**2))**0.5)+i[0]
			planet.rect.centery = ((((planet.radius*3)**2) - ((planet.rect.centerx - i[0])**2))**0.5)+i[1]
			
	correction.append((planet.rect.centerx, planet.rect.centery))
	if HEIGHT-planet.rect.centerx < planet.radius:
		planet.rect.centerx -= planet.radius
"""

all_sprites.clear(screen, background)

#Game Loop

running = True

while running:
	#keep loop running at the right speed
	clock.tick(FPS)
	
	#Process input (events)
	for event in pygame.event.get():
	
		#check for click on close window button
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.MOUSEBUTTONUP and not(pygame.key.get_pressed()[pygame.K_s]):
			mousepos = pygame.mouse.get_pos()
			planet = 0
			clicked = 0
			for list in planetCoords:
				if mousepos in list:
					planet = planetCoords.index(list)
					clicked = 1
					break
			if clicked:
				planetList[planet].selected = True
			
	
	#Update
	all_sprites.update()
	tbkill = []
	#units with diff iD collide with each other
	for unit in unitTravel.keys():
		for unit1 in unitTravel.keys():
			if unit.unitiD == unit1.unitiD:
				break
			if unitTravel[unit] == unitTravel[unit1]:
				tbkill.append(unit)
				tbkill.append(unit1)
				
	for i in tbkill:
		unitKill(i)
				
	#units with diff iD collide with foreign planet
	for planet in planets:
		collisions = planet.rect.collidedictall(unitTravel)
		for unit in collisions:
			if planet.planetiD != unit[0].unitiD and planet.planetiD != 0:
				if planet.claimStatus > 0:
					planet.claimStatus -= 1
			elif planet.planetiD == unit[0].unitiD:
				newUnit(planet.rect.centerx, planet.rect.centery+planet.radius+10, planet, planet.planetiD)
			elif planet.planetiD == 0:
				if planet.claimStatus == 0:
					planet.claimStatus += 1
					planet.color = unit[0].color
				elif planet.claimStatus > 0 and planet.claimStatus < 100 and planet.color == unit[0].color:
					planet.claimStatus += 1
				elif planet.claimStatus > 0 and planet.claimStatus < 100 and planet.color != unit[0].color:
					planet.claimStatus -= 1
				elif planet.claimStatus == 100:
					planet.planetiD = unit[0].unitiD
					planet.color = unit[0].color
				else:
					print "error"
			unitKill(unit[0])

	#collisions between selectRect and units turn units selected
	unitSelect()
	selectedUnits = selectRect.collidedictall(unitRects)
	if len(selectedUnits) > 0:
		for i in selectedUnits:
			i[0].selected = True

	#Draw / Render
	screen.fill(BLACK)
	all_sprites.draw(screen)

	pygame.draw.rect(screen, WHITE, selectRect, 2) #needs to determine color by who is inputting
	for i in planets:
		i.drawRings(i.ringNumber, i.upgradeStatus)
		i.drawClaimStatus(i.claimStatus)
		#pygame.draw.rect(screen, YELLOW, i.rect, 2)
	#draw_text(screen, str(clock.get_fps()), 18, WIDTH - 10, 10)
	#AFTER drawing everything, display it on the screen
	pygame.display.flip()
	if clock.get_fps() < 21.0 and clock.get_fps() > 20.0:
		break

pygame.quit()
