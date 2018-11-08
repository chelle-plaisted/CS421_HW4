import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *
import random
from time import time
##
##
# Gene class
#
# Description: A gene reprsents the essential information of the game layout
# through an array and provides functionality to manipulate the gene as necessary
#
##

class Gene():
    #__init__
    # Description: Creates a new Gene
    ##
    def __init__(self, cells = None):

        # 40 for our side, 40 on enemy side
        self.numCells = 80

        self.chanceOfMutate = 0.05

        #state represented by gene
        self.geneState = None

        # Gene contents
        if cells == None:
            self.initializeGene()
        else:
            self.cells = cells

    ##
    # initializeGene
    # Description: Generate a new gene reprsentation in array as follows:
    #   -populate all indicies with random number
    #   -indices 0-39 = AI player's side of board. On this half:
    #       -Top value: anthill location
    #       -Next value: tunnel location
    #       -Next 9 values: grass Locations
    #   -indices 40-79 = enemy player's side of board. On this half:
    #       -Top 2 values: enemy food Locations
    #   - array values stored in self.cells
    ##
    def initializeGene(self):
        self.cells = []
        for i in range (0, self.numCells):
            self.cells += [random.randint(0, 2**31 -1)]

    ##
    # mateGenes
    #
    # Description: make the current gene with another parent gene by selecting
    # a random crossover point and making a new gene that splices the cell contents
    # of its parents at the given crossover.
    #
    # Parameters:
    #   otherParent: other parent Gene to mate with
    #
    # Return: 2 child Genes (1 where the first half comes from current gene, and
    # a second where the first half comes from otherParent) and the crossover point (for testing)
    ## TODO remove unecessary code
    def mateGenes(self, otherParent):

        #select crossover point
        crossPoint = random.randint(0, self.numCells) # includes self.numCells

        #generate first child gene
        cells = []
        cells += self.cells[0:crossPoint] # does not include crossPoint
        cells += otherParent.cells[crossPoint:]
        child1 = Gene(cells)

        #generate second child gene
        cells = []
        cells += otherParent.cells[0:crossPoint]
        cells += self.cells[crossPoint:]
        child2 = Gene(cells)

        return (self.mutateGene(child1), self.mutateGene(child2), crossPoint)

    ##
    # mutate
    #
    # Description: apply a chance of mutation to a Gene and mutate if necessary
    #
    # Parameters:
    #   gene : a gene that could be mutated
    #
    # Return: a gene, either mutated or left alone
    ##
    def mutateGene(self, gene):
        # mutate if needed
        mutation = random.random()
        if mutation <= self.chanceOfMutate:
            # mutate the gene
            idxToMutate = random.randint(0, self.numCells-1)
            val = random.randint(0, 2**31 -1)
            gene.cells[idxToMutate] = val

        return gene

    ##
    # getCoords
    #
    # Description: get the corresponding map locations for a given indexToEval
    #
    # Return: a tuple representing a location on the gameboard or -1 for error
    def getCoords(self, index):
        # error check
        if index < 0 or index > self.numCells - 1:
            return -1
        # if in the second half of cells, add an offset to put the cell on the enemy side
        if index >= 40:
            index += 20 # number of neutral cells
        # x location
        x = index % 10
        # y location
        y = int(index / 10)

        return (x,y)

    ##
    # getConstructions
    #
    # Description: get the Constructions needed for a given phase of the game as
    # defined by the structure of the current gene.  Also sets up geneState, a
    # game state representing this gene.
    # Array order SETUP_PHASE_1: [AntHill, Tunnel, Grasses 1-9] length 11
    # Array order SETUP_PHASE_2: [Enemy food 1, Enemy food 2] length 2
    #
    # Parameters:
    #   phase: SETUP_PHASE_1 (get objects on this AI's side of board, indices 0-39)
    #          SETUP_PHASE_2 (get objects on enemy's side of board, indices 40-79)
    # Return: a list of coordinates representing either (anthill_location, tunnel_location,
    # 9 grqss locations) or (enemy food 1, enemy food 2)
    ##
    def getConstructions(self, phase):
        #variables
        constructions = []
        constructionIndices = []
        count = 0

        #setup phase 1: placing anthill, tunnel, grass
        if phase == SETUP_PHASE_1:
            #find 11 biggest number indices
            while count < 11:
                greatestNum = -1
                greatestNumIdx = 0
                for i in range(0,40): # find 1 of the 11 highest numbers
                    if i not in constructionIndices and self.cells[i] > greatestNum:
                        greatestNum = self.cells[i]
                        greatestNumIdx = i
                constructionIndices.append(greatestNumIdx)
                count = count + 1

        #setup phase 2: placing food on enemy side
        elif phase == SETUP_PHASE_2:
            #indices of locations we cannot place food in
            #because Booger always places its constructs there
            occupiedLocations = [49,58,59,64,67,68,69,76,77,78,79]

            #find 2 biggest number indices
            while count < 2:
                greatestNum = -1
                greatestNumIdx = 0
                for i in range(40,80): #find 1 of the 2 highest numbers
                    if i not in constructionIndices and i not in occupiedLocations and self.cells[i] > greatestNum:
                        greatestNum = self.cells[i]
                        greatestNumIdx = i
                constructionIndices.append(greatestNumIdx)
                count = count + 1

        #convert indices to coords
        for i in constructionIndices:
            coords = self.getCoords(i)
            constructions.append(coords)

        #done
        return constructions

    ##
    # buildGeneState
    #
    # Description: build a state corresponding to current gene based on the cell
    # values of the gene and the oritentation of the enemy (Booger's) constructions
    # Note: state does NOT include placement of ImaAgent food or ant placement, because
    # these do not impact the placement decision.
    #
    ##
    def buildGeneState(self):
        self.geneState = GameState.getBlankState()
        # build phase 1
        constructions = self.getConstructions(SETUP_PHASE_1)
        hill = Building(constructions[0], ANTHILL, 0)
        self.geneState.inventories[0].constrs.append(hill)

        tunnel = Building(constructions[1], TUNNEL, 0)
        self.geneState.inventories[0].constrs.append(tunnel)
        grass = []
        for i in range(0,9):
            grass.append(Building(constructions[i+2], GRASS, 0))
            self.geneState.inventories[2].constrs.append(grass[i])

        # build phase 2
        constructions = self.getConstructions(SETUP_PHASE_2)
        food1 = Building(constructions[0], FOOD, 0)
        food2 = Building(constructions[1], FOOD, 0)
        self.geneState.inventories[2].constrs.append(food1)
        self.geneState.inventories[2].constrs.append(food2)

        #add Booger's set locations
        constructions = [(9,9), (4, 8),
                (9,6), (8,7), (7,8), (6,9), \
                (9,7), (8,8), (7,9), \
                (9,8), (8,9) ]
        hill = Building(constructions[0], ANTHILL, 0)
        self.geneState.inventories[1].constrs.append(hill)
        tunnel = Building(constructions[1], TUNNEL, 0)
        self.geneState.inventories[1].constrs.append(tunnel)
        grass = []
        for i in range(0,9):
            grass.append(Building(constructions[i+2], GRASS, 1))
            self.geneState.inventories[2].constrs.append(grass[i])



##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "Ima Agent")

         # general values to determine scope of algorithm
        self.popSize = 10
        self.gamesPerGene = 10
        # data to reprsent the current population & fitness
        self.currentPop = []
        self.currentFitness = []
        self.defaultFitness = 2 * self.gamesPerGene # to avoid negative fitness values that will
        # mess up parent selection
        self.initializePop()
        # the current index of genes to evaluate
        self.indexToEval = 0
        # how many games have been played for the gene currently being evalutated
        self.gamesPlayed = 0
        self.file = None

    ##
    #getPlacement
    #
    # TODO: adjust to use genetic algorithm
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        #redirect prints to file
        self.file = open("evidence1.txt","a")
        #sys.stdout = self.file
        return self.currentPop[self.indexToEval].getConstructions(currentState.phase)

    ##
    # initializePop
    # Description: initializes the genes of the population to randomized values
    # and sets the default value of the fitness to 0.
    ##
    def initializePop(self):
        for i in range(0, self.popSize):
            # make a new gene
            gene = Gene()
            # add it to the current Population
            self.currentPop.append(gene)
            # set the default fitness to 0
            self.currentFitness.append(self.defaultFitness)

    ##
    # generateChildren
    # Description: generate 2 children for parents with a set chance of mutation
    # using a random crossover point.
    #
    # Parameters:
    #   parents: tuple of 2 parents
    #
    # Return: list of 2 children
    ##
    def generateChildren(self, parents):
        rtnVal = parents[0].mateGenes(parents[1])
        return [rtnVal[0], rtnVal[1]] # crossPoint only needed for testing

    ##
    # makeNextGen
    # Description: select the most fit groups of parents and fill the next generation
    #
    ##
    def makeNextGen(self):
        print('started make next gen')
        t0 = time()
        nextGen = []
        # until my next generation is full, keep selecting parents, mating them,
        # and adding the children to the next generation
        while len(nextGen) < self.popSize:
            # select parents
            t0 = time()
            parents = self.selectParents()
            t1 = time()
            print('parent selection: ', t1 - t0)
            # mate parents
            children = self.generateChildren(parents)
            t2 = time()
            # add chldren to next generation
            nextGen += children

            print('child generation: ', t2-t1)


        # retire current population by resetting it as the new generation
        self.currentPop = nextGen

        # reset all fitness values
        self.currentFitness = [self.defaultFitness] * self.popSize
        t4 = time()
        print('total makeNextGen: ', t4 - t0)

    ## TODO EDIT: do we want any tweaks, prune bottom 10% of population,
    # allow parent to 'self mate' and continue on a supposedly goot gene set....
    # selectParents
    #
    # Description: select the parents to mate for the next child according to
    # the Fitness Proportionate Selection Method
    #
    # Return: a tuple of parent genes
    ##
    def selectParents(self):
        # get sum of fitnesses
        print('started parent selection')
        sum = 0
        t0 = time()
        for score in self.currentFitness:
            sum += score
        t1 = time()
        # print('parent sum: ', t1-t0)
        # continue selection until 2 valid parents are generated
        selected = []
        count = 0
        while len(selected) < 2:
            # print('looping for parent')
            count = count + 1
            # generate random value * sum
            val = random.random() * sum
            # select using random value
            chosen = -1
            for idx in range(0, len(self.currentPop)):
                val -= self.currentFitness[idx]
                if val < 0 :
                    chosen = idx
                    break
            # don't choose the same parent twice
            if not chosen in selected:
                selected.append(chosen)
            # print('selected 1 parent')

        # return the selected parents

        parents = (self.currentPop[selected[0]], self.currentPop[selected[1]])
        if(parents[1].cells == parents[0].cells):
            print('same parent')
        print('number of loops: ', count)
        return parents

    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        moves = listAllLegalMoves(currentState)
        selectedMove = moves[random.randint(0,len(moves) - 1)];

        #don't do a build move if there are already 3+ ants
        numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        while (selectedMove.moveType == BUILD and numAnts >= 3):
            selectedMove = moves[random.randint(0,len(moves) - 1)];

        return selectedMove

    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #
    # Updates the fitness for current gene and advances to the next gene if necessary.
    # TODO: add code to write to evidence file
    #
    def registerWin(self, hasWon):
        # update the games played
        self.gamesPlayed += 1
        # update fitness
        if hasWon:
            self.currentFitness[self.indexToEval] += 1
            print('won: ', self.currentFitness[self.indexToEval])
        else:
            self.currentFitness[self.indexToEval] -= 1
            print('lost: ', self.currentFitness[self.indexToEval])

        # if done with current gene, advance to next
        if self.gamesPlayed == self.gamesPerGene:
            # reset the number of games played
            self.gamesPlayed = 0
            # if that was the last gene, make a new generation
            if self.indexToEval == self.popSize - 1:
                # generation has ended print to evidence file
                t0 = time()

                bestIdx = self.getBestGene()
                bestGene = self.currentPop[bestIdx]
                bestGene.buildGeneState()
                state = bestGene.geneState
                print("Best Gene Score = ", self.currentFitness[bestIdx])
                asciiPrintState(state)
                print("=========================================================")

                t1 = time()

                # make new generation
                self.indexToEval = 0
                self.makeNextGen()

                t2 = time()



            else: # otherwise, move to next
                self.indexToEval += 1

        self.file.close()

    ##
    # getBestGene
    #
    # Description: get the index of the best gene of the current generation
    #
    # Return: the index of the gene
    ##
    def getBestGene(self):
        best = 0
        for i in range(1, len(self.currentFitness)):
            if self.currentFitness[i] > self.currentFitness[best] :
                best = i
            elif self.currentFitness[i] == self.currentFitness[best] :
                test = random.random()
                if test >  0.5 :
                    best = i
        return best


################################################################################
#TODO COMPLETE
#UNIT TESTS
testAgent = AIPlayer(0)
testGene = Gene()
################################################################################

################################################################################
#def initializeGene(self):
################################################################################
testGene.initializeGene()
takenValues = []
repeats = 0
count = 0
for cell in testGene.cells:
    if not cell in takenValues:
        takenValues.append(cell)
    else:
        repeats += 1
    count += 1

# check not too many repeats
if not (float(repeats) / testGene.numCells < .10):
    print('- Function initializeGene() failed test 1. Too many repeats.')

# check length
if not count == testGene.numCells:
    print('- Function initializeGene() failed test 2. Number of cells expected: ',
        testGene.numCells, ' ; Number of cells found: ', count)

################################################################################
#def mateGenes(self, otherParent):
################################################################################
# make a second gene
testGene2 = Gene()

rtnVal = testGene.mateGenes(testGene2)
children = rtnVal[0:2]
cross = rtnVal[2]

# check number of children
if not len(children) == 2:
    print('- Function mateGenes() failed test 1. Incorrect number of children: ', children)

# check length of children cells
if not len(children[0].cells) == testGene.numCells:
    print('- Function mateGenes() failed test 2. Child 1 wrong length: ', len(children[0].cells))
if not len(children[1].cells) == testGene.numCells:
    print('- Function mateGenes() failed test 3. Child 2 wrong length: ', len(children[1].cells))

# check the cross point
if not cross >= 0 and cross <= testGene.numCells:
    print('- Function mateGenes() failed test 6. Invalid crossover point: ', cross)

# check format of child 1
differentIndices = []
for i in range(0, len(children[0].cells)):
    if i < cross and children[0].cells[i] == testGene.cells[i]:
        continue
    elif  i >= cross and children[0].cells[i] == testGene2.cells[i]:
        continue
    else:
        differentIndices.append(i)
if len(differentIndices) > 1: # 1 mutation allowed
    print('- Function mateGenes() failed test 4. Mating error with child 1. Cross: ', cross)
    for index in differentIndices:
        print('Index: ', index, ' child: ', children[0].cells[index], '; Parent 1: ',
        testGene.cells[index], '; Parent 2: ', testGene2.cells[index])

# check format of child 2
differentIndices = []
for i in range(0, len(children[1].cells)):
    if i < cross and children[1].cells[i] == testGene2.cells[i]:
        continue
    elif i >= cross and children[1].cells[i] == testGene.cells[i]:
        continue
    else:
        differentIndices.append(i)

if len(differentIndices) > 1: # 1 mutation allowed
    print('- Function mateGenes() failed test 5. Mating error with child 2. Cross: ', cross)
    for index in differentIndices:
        print('Index: ', index, ' child: ', children[1].cells[index], '; Parent 1: ',
        testGene2.cells[index], '; Parent 2: ', testGene.cells[index])


################################################################################
#def mutateGene(self, index):
################################################################################
numTests = 200
mutated = False
oldCells = testGene.cells.copy()
for i in range(0, numTests + 1):
    outputGene = testGene.mutateGene(testGene)
    if not outputGene.cells == oldCells:
        mutated = True
        break

if not mutated:
    print('- Function mutateGene() failed test 1. No mutation occured in ', numTests,
        ' rounds with ', testGene.chanceOfMutate, '% chance of mutation.')


################################################################################
#def getCoords(index):
################################################################################
testIdx1 = -1
coords = testGene.getCoords(testIdx1)
if not coords == -1:
    print('- Function getCoords() failed test 1. Test index ', testIdx1, ' yielded coords ',
        coords, '. Expected -1 as error.')
testIdx2 = 90
coords = testGene.getCoords(testIdx2)
if not coords == -1:
    print('- Function getCoords() failed test 2. Test index ', testIdx2, ' yielded coords ',
        coords, '. Expected -1 as error.')
testIdx3 = 0
coords = testGene.getCoords(testIdx3)
if not coords == (0,0):
    print('- Function getCoords() failed test 3. Test index ', testIdx3, ' yielded coords ',
        coords, '. Expected coords (0,0)')
testIdx4 = 24
coords = testGene.getCoords(testIdx4)
if not coords == (4,2):
    print('- Function getCoords() failed test 4. Test index ', testIdx4, ' yielded coords ',
        coords, '. Expected coords (4,2)')
testIdx5 = 40
coords = testGene.getCoords(testIdx5)
if not coords == (0,6):
    print('- Function getCoords() failed test 5. Test index ', testIdx5, ' yielded coords ',
        coords, '. Expected coords (0,6)')
testIdx6 = 79
coords = testGene.getCoords(testIdx6)
if not coords == (9,9):
    print('- Function getCoords() failed test 6. Test index ', testIdx6, ' yielded coords ',
        coords, '. Expected coords (9,9)')
testIdx7 = 58
coords = testGene.getCoords(testIdx7)
if not coords == (8,7):
    print('- Function getCoords() failed test 7. Test index ', testIdx7, ' yielded coords ',
        coords, '. Expected coords (8,7)')
testIdx8 = 65
coords = testGene.getCoords(testIdx8)
if not coords == (5,8):
    print('- Function getCoords() failed test 8. Test index ', testIdx8, ' yielded coords ',
        coords, '. Expected coords (5,8)')

################################################################################
#def getConstructions(self, phase):
################################################################################

################################################################################
# def getPlacement(self, currentState):
################################################################################

################################################################################
# def initializePop(self):
################################################################################

################################################################################
# def generateChildren(self, parents):
################################################################################

################################################################################
# def makeNextGen(self):
################################################################################

################################################################################
# def selectParents(self):
################################################################################

################################################################################
# def registerWin(self, hasWon):
################################################################################
