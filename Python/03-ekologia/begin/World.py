from Position import Position
from Organisms.Plant import Plant
from Organisms.Animal import Animal
from Action import Action
from ActionEnum import ActionEnum
from Organisms.Grass import Grass
from Organisms.Sheep import Sheep
from Organisms.Lynx import Lynx
from Organisms.Antelope import Antelope
import random


class World(object):

    def __init__(self, worldX, worldY):
        self.__worldX = worldX
        self.__worldY = worldY
        self.__turn = 0
        self.__organisms = []
        self.__newOrganisms = []
        self.__separator = '.'

    @property
    def worldX(self):
        return self.__worldX

    @property
    def worldY(self):
        return self.__worldY

    @property
    def turn(self):
        return self.__turn

    @turn.setter
    def turn(self, value):
        self.__turn = value

    @property
    def organisms(self):
        return self.__organisms

    @organisms.setter
    def organisms(self, value):
        self.__organisms = value

    @property
    def newOrganisms(self):
        return self.__newOrganisms

    @newOrganisms.setter
    def newOrganisms(self, value):
        self.__newOrganisms = value

    @property
    def separator(self):
        return self.__separator

    def makeTurn(self):
        actions = []
        for org in self.organisms:
            if self.positionOnBoard(org.position):
                actions = org.move()
                for a in actions:
                    self.makeMove(a)
                actions = []
                if self.positionOnBoard(org.position):
                    actions = org.action()
                    for a in actions:
                        self.makeMove(a)
                    actions = []

        self.organisms = [o for o in self.organisms if self.positionOnBoard(o.position)]
        for o in self.organisms:
            o.liveLength -= 1
            o.power += 1
            if o.liveLength < 1:
                print(str(o.__class__.__name__) + ': died of old age at: ' + str(o.position))
        self.organisms = [o for o in self.organisms if o.liveLength > 0]

        self.newOrganisms = [o for o in self.newOrganisms if self.positionOnBoard(o.position)]
        self.organisms.extend(self.newOrganisms)
        self.organisms.sort(key=lambda o: o.initiative, reverse=True)
        self.newOrganisms = []

        self.turn += 1

    def makeMove(self, action):
        print(action)
        if action.action == ActionEnum.A_ADD:
            self.newOrganisms.append(action.organism)
        elif action.action == ActionEnum.A_INCREASEPOWER:
            action.organism.power += action.value
        elif action.action == ActionEnum.A_MOVE:
            action.organism.position = action.position
        elif action.action == ActionEnum.A_REMOVE:
            action.organism.position = Position(xPosition=-1, yPosition=-1)

    def addOrganism(self, newOrganism):
        newOrgPosition = Position(xPosition=newOrganism.position.x, yPosition=newOrganism.position.y)

        if self.positionOnBoard(newOrgPosition):
            self.organisms.append(newOrganism)
            self.organisms.sort(key=lambda org: org.initiative, reverse=True)
            return True
        return False

    def positionOnBoard(self, position):
        return position.x >= 0 and position.y >= 0 and position.x < self.worldX and position.y < self.worldY

    def getOrganismFromPosition(self, position):
        pomOrganism = None

        for org in self.organisms:
            if org.position == position:
                pomOrganism = org
                break
        if pomOrganism is None:
            for org in self.newOrganisms:
                if org.position == position:
                    pomOrganism = org
                    break
        return pomOrganism

    def getNeighboringPositions(self, position):
        result = []
        pomPosition = None

        for y in range(-1, 2):
            for x in range(-1, 2):
                pomPosition = Position(xPosition=position.x + x, yPosition=position.y + y)
                if self.positionOnBoard(pomPosition) and not (y == 0 and x == 0):
                    result.append(pomPosition)
        return result

    def filterFreePositions(self, fields):
        result = []

        for field in fields:
            if self.getOrganismFromPosition(field) is None:
                result.append(field)
        return result

    def filterPositionsWithoutAnimals(self, fields):
        result = []
        pomOrg = None

        for filed in fields:
            pomOrg = self.getOrganismFromPosition(filed)
            if pomOrg is None or isinstance(pomOrg, Plant):
                result.append(filed)
        return result

    def __str__(self):
        result = '\nturn: ' + str(self.__turn) + '\n'
        for wY in range(0, self.worldY):
            for wX in range(0, self.worldX):
                org = self.getOrganismFromPosition(Position(xPosition=wX, yPosition=wY))
                if org:
                    result += str(org.sign)
                else:
                    result += self.separator
            result += '\n'
        return result

    def plague(self):
        for o in self.organisms:
            o.liveLength /= 2

    def getAllPositions(self):
        positions = []
        for x in range(self.worldX):
            for y in range(self.worldY):
                positions.append(Position(xPosition=x, yPosition=y))
        return positions

    def natureProtection(self):
        # dodanie do listy wszystkich gatunków aktualnie występujących na planszy
        speciesPresent = set(o.__class__ for o in self.organisms)
        # wszystkie gatunki ogólnie występujące
        speciesList = [Grass, Sheep, Lynx, Antelope]

        for species in speciesList:
            # policzenie każdego gatunku (ile osobników jest na planszy)
            speciesCount = sum(1 for o in self.organisms if isinstance(o, species))
            # obliczenie ile maksymalnie może być osobników danego gatunku
            maxOccupancy = self.worldX * self.worldY // 2

            # usunięcie losowych osobników z gatunku, który zajmuje więcej niż połowa planszy
            if speciesCount > maxOccupancy:
                print(f"Zbyt wiele {species.__name__}, usuwanie losowych osobników.")
                for _ in range(speciesCount - maxOccupancy):
                    randomOrganism = random.choice([o for o in self.organisms if isinstance(o, species)])
                    print(f"{randomOrganism.__class__.__name__} remove from: {randomOrganism.position}")
                    self.organisms.remove(randomOrganism)

            # dodanie w losowych miejscach osobników z gatunku, który wyginął
            if species not in speciesPresent:
                # lista wszystkich pustych miejsc
                emptyPositions = self.filterFreePositions(self.getAllPositions())
                # dodanie 2 osobników
                if len(emptyPositions) >= 2:
                    print(f"Brak {species.__name__}, dodawanie nowych osobników.")
                    positions = random.sample(emptyPositions, 2)
                    for position in positions:
                        print(f"{species.__name__} add at: {position}")
                        self.addOrganism(species(position=position, world=self))
                # dodanie 1 osobnika ze względu na brak 2 pustych miejsc
                elif emptyPositions:
                    print(f"Brak {species.__name__}, dodawanie nowego osobnika.")
                    position = random.choice(emptyPositions)
                    print(f"{species.__name__} add at: {position}")
                    self.addOrganism(species(position=position, world=self))
                # dodanie 0 osobników ze względu na brak pustych miejsc
                else:
                    print(f"Brak {species.__name__}, brak miejsca na dodanie nowego osobnika.")
