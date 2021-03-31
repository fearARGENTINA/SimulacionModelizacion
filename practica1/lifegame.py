import curses
from time import sleep, time
import random
import sys

NEIGHBOURS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
W, H = 25, 25
MIN_SURVIVAL = 2
MAX_SURVIVAL = 3
SURVIVAL_RANGE = list(range(MIN_SURVIVAL, MAX_SURVIVAL+1))
EVERY_SECONDS = 0.3
MAX_PLAYERS = 50
BORDER_CHAR = '@'
ALIVE_CHAR = 'X'
DEAD_CHAR = ' '

class Player:
    def __init__(self, pos, isDead = False):
        self.isDead = isDead
        self.pos = pos
        
    def die(self):
        self.isDead = True
    
    def respawn(self):
        self.isDead = False
    
    def getPos(self):
        return self.pos
        
    def getAdyacentPoses(self):
        return [ tuple(map(sum, zip(nei, self.pos))) for nei in NEIGHBOURS ]
        
class Scenario:
    playersList = []
    
    def __init__(self, w, h, maxPlayers = 5, randomAlivePositions = []):
        self.w = w
        self.h = h
        self.maxPlayers = maxPlayers
        
        if not len(randomAlivePositions):
            randomAlivePositions = [(random.randrange(0, w), random.randrange(0, h)) for i in range(maxPlayers)]
            
        self.playersList = [[ Player((x, y), True) for x in range(w)] for y in range(h)]
        for pos in randomAlivePositions:
            self.playersList[pos[1]][pos[0]] = Player(pos)
        
    def getPlayers(self):
        return self.playersList
    
    def mapPlayersToState(self):
        return [ list(map(lambda x: x.isDead, rowPlayers)) for rowPlayers in self.playersList]
    
    def getNumAdyacentNeighbours(self, x, y):
        pre_neighboursOffsets = [ (x+nei[0], y+nei[1]) for nei in NEIGHBOURS ]
        
        neighboursOffsets = list(filter(lambda pos: pos[0] >= 0 and pos[0] < self.w and pos[1] >= 0 and pos[1] < self.h, pre_neighboursOffsets))
        
        neighboursAlive = [ not self.playersList[nei[0]][nei[1]].isDead for nei in neighboursOffsets ]
        
        return sum(neighboursAlive)
        
    def nextGeneration(self):
        auxPlayersStates = self.mapPlayersToState()
        
        for x in range(self.w):
            for y in range(self.h):
                isDead = self.playersList[x][y].isDead
                
                adjNeighbours = self.getNumAdyacentNeighbours(x, y)
                
                if isDead:
                   if adjNeighbours == 3:
                        auxPlayersStates[x][y] = False
                else:
                    if not adjNeighbours in SURVIVAL_RANGE:
                        auxPlayersStates[x][y] = True
                        
        for x in range(self.w):
            for y in range(self.h):
                if auxPlayersStates[x][y]:
                    self.playersList[x][y].die()
                else:
                    self.playersList[x][y].respawn()
        
    
class Screen:    
    def __init__(self, w, h):
        self.stdscr = curses.initscr()
        self.stdscr.nodelay(True)
        self.w = w
        self.h = h
        self.grid = [[DEAD_CHAR for x in range(w)] for y in range(h)]
    
    def getCh(self):
        return self.stdscr.getch()
    
    def resetGrid(self):
        self.grid = [[DEAD_CHAR for x in range(self.w)] for y in range(self.h)]
        
    def mapPlayersToGrid(self, players):
        self.grid = [[ALIVE_CHAR if not players[x][y].isDead else DEAD_CHAR for x in range(self.w)] for y in range(self.h)]
        
    def drawGrid(self, players = None):
        self.stdscr.clear()
        
        for i in range(-1, self.h+1):
            if i == -1 or i == self.h:
                self.stdscr.addstr(i+1, 0, BORDER_CHAR*(2+self.w))
            else:
                self.stdscr.addstr(i+1, 0, BORDER_CHAR + ''.join(self.grid[i]) + BORDER_CHAR)
        
    def refresh(self):
        self.stdscr.refresh()
    
    def clear(self):
        self.stdscr.clear()
    
    def write(self, text):
        self.stdscr.clear()
        self.stdscr.addstr(int(self.w/2), int(self.h/2), text)
        self.stdscr.refresh()
        
def waitToStart(screen):
    screen.drawGrid()
    screen.refresh()
    
    while True:
        try:
            if screen.getCh() == ord('b'):
                break
        except:
            continue

def readLifeGameConf(filePath):    
    randomAlivePositions = []
    
    with open(filePath, 'r') as f:
        lines = [ line.strip() for line in f.readlines() ]
        
        for line in lines:
            randomAlivePositions.append(tuple([ int(strNum) for strNum in line.split(',')]))
    
    return randomAlivePositions

def main():
    filePath = 'lifegame.conf'
    
    if len(sys.argv) >= 2:
        filePath = sys.argv[1]
    
    firstConf = readLifeGameConf(filePath)
    
    screen = Screen(W, H)
    scenario = Scenario(W, H, MAX_PLAYERS, firstConf)
    players = scenario.getPlayers()
    screen.mapPlayersToGrid(players)
    
    waitToStart(screen)
    
    nextTime = time()
    
    while True:
        curTime = time()
        
        if curTime >= nextTime:
            players = scenario.getPlayers()
            screen.mapPlayersToGrid(players)        
            screen.drawGrid()
            screen.refresh()
            scenario.nextGeneration()
            
            nextTime = time()+EVERY_SECONDS
                
        if screen.getCh() == ord('q'):
            screen.clear()
            screen.write("Juego finalizado")
            break
        
        
main()