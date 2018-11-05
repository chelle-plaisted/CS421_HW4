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

    ## TODO COMPLETE
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
    # a second where the first half comes from otherParent)
    ## TODO remove unecessary code
    def mateGenes(self, otherParent):

        #select crossover point
        crossPoint = random.randint(0, self.numCells)

        #generate first child gene
        cells = []
        cells += self.cells[0:crossPoint]
        cells += otherParent.cells[crossPoint:]
        child1 = Gene(cells)



        # for i in range(0,crossPoint):
        #     child1.cells[i] = self.cells[i]
        # for i in range(crossPoint, self.numCells):
        #     child1.cells[i] = otherParent.cells[i]

        #generate second child gene
        # child2 = Gene()
        # for i in range(0,crossPoint):
        #     child2.cells[i] = otherParent.cells[i]
        # for i in range(crossPoint, self.numCells):
        #     child2.cells[i] = self.cells[i]

        cells = []
        cells += otherParent.cells[0:crossPoint]
        cells += self.cells[crossPoint:]
        child2 = Gene(cells)

        return (self.mutateGene(child1), self.mutateGene(child2))

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
            idxToMutate = random.randint(0, self.numCells)
            val = random.randint(0, 2**31 -1)
            # print('mutating: ', gene.cells[idxToMutate], ' to ', val)
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
        if index < 0 or index > self.numCells -1:
            return -1
        # if in the second half of cells, add an offset to put the cell on the enemy side
        if index >= 40:
            index += 20 # number of neutral cells
        # x location
        x = index % 10
        # y location
        y = int(index / 10)

        return (x,y)

    ## TODO COMPLETE
    # getConstructions
    #
    # Description: get the Constructions needed for a given phase of the game as
    # defined by the structure of the current gene
    #
    # Parameters:
    #   phase: SETUP_PHASE_1 (get objects on this AI's side of board, indices 0-39)
    #          SETUP_PHASE_2 (get objects on enemy's side of board, indices 40-79)
    # Return: a list of coordinates representing either (anthill_location, tunnel_location,
    # 9 grqss locations) or (enemy food 1, enemy food 2)
    def getConstructions(self, phase):
        #variables
        constructions = []
        constructionIndices = []
        count = 0

        #setup phase 1: placing anthill, tunnel, grass
        if phase == SETUP_PHASE_1:
            #find 9 biggest number indices
            while count < 11:
                greatestNum = -1
                greatestNumIdx = 0
                for i in range(0,40): #find 1 of the 9 highest numbers
                    if i not in constructionIndices and self.cells[i] > greatestNum:
                        greatestNum = self.cells[i]
                        greatestNumIdx = i
                constructionIndices.append(greatestNumIdx)
                count = count + 1

        #setup phase 2: placing food on enemy side
        elif phase == SETUP_PHASE_2:
            # print('phase 2')
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
        self.popSize = 2 #TODO: increase to min 1000
        self.gamesPerGene = 2 #TODO increase to min 1000
        # data to reprsent the current population & fitness
        self.currentPop = []
        self.currentFitness = []
        self.defaultFitness = 0
        self.initializePop()
        # the current index of genes to evaluate
        self.indexToEval = 0
        # how many games have been played for the gene currently being evalutated
        self.gamesPlayed = 0

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
        # TODO, remove code below once getConstructions is finished
        return self.currentPop[self.indexToEval].getConstructions(currentState.phase)
        # numToPlace = 0
        # #implemented by students to return their next move
        # if currentState.phase == SETUP_PHASE_1:    #stuff on my side
        #     numToPlace = 11
        #     moves = []
        #     for i in range(0, numToPlace):
        #         move = None
        #         while move == None:
        #             #Choose any x location
        #             x = random.randint(0, 9)
        #             #Choose any y location on your side of the board
        #             y = random.randint(0, 3)
        #             #Set the move if this space is empty
        #             if currentState.board[x][y].constr == None and (x, y) not in moves:
        #                 move = (x, y)
        #                 #Just need to make the space non-empty. So I threw whatever I felt like in there.
        #                 currentState.board[x][y].constr == True
        #         moves.append(move)
        #     return moves
        # elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
        #     numToPlace = 2
        #     moves = []
        #     for i in range(0, numToPlace):
        #         move = None
        #         while move == None:
        #             #Choose any x location
        #             x = random.randint(0, 9)
        #             #Choose any y location on enemy side of the board
        #             y = random.randint(6, 9)
        #             #Set the move if this space is empty
        #             if currentState.board[x][y].constr == None and (x, y) not in moves:
        #                 move = (x, y)
        #                 #Just need to make the space non-empty. So I threw whatever I felt like in there.
        #                 currentState.board[x][y].constr == True
        #         moves.append(move)
        #     return moves
        # else:
        #     return [(0, 0)]

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
        return parents[0].mateGenes(parents[1])

    ##
    # makeNextGen
    # Description: select the most fit groups of parents and fill the next generation
    #
    ##
    def makeNextGen(self):
        nextGen = []
        # until my next generation is full, keep selecting parents, mating them,
        # and adding the children to the next generation
        while len(nextGen) < self.popSize:
            # select parents
            parents = self.selectParents()
            # mate parents
            children = self.generateChildren(parents)
            # add chldren to next generation
            nextGen += children

        # retire current population by resetting it as the new generation
        self.currentPop = nextGen

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
        sum = 0
        for score in self.currentFitness:
            sum += score

        # continue selection until 2 valid parents are generated
        selected = []
        while len(selected) < 2:
            # generate random value
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

        # return the selected parents
        parents = (self.currentPop[selected[0]], self.currentPop[selected[1]])
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
        else:
            self.currentFitness[self.indexToEval] -= 1

        # if done with current gene, advance to next
        if self.gamesPlayed == self.gamesPerGene :
            # if that was the last gene, make a new generation
            if self.indexToEval == self.popSize - 1:
                # generation has ended print to evidence file
                bestIdx = self.getBestGene()
                # state = self.buildState(bestIdx)
                with open("evidence.txt", "a") as textFile:
                    textFile.write("Best Gene Score {0}".format(self.currentFitness[bestIdx]))
                #     textFile.write("{0}".format(asciiPrintState(state)))
                    textFile.write("---------------------------------------------------\n")
                # make new generation
                self.indexToEval = 0
                self.makeNextGen()
            else: # otherwise, move to next
                self.indexToEval += 1
            # reset the number of games played
            self.gamesPlayed = 0

    ##
    # getBestGene
    #
    # Description: get the index of the best gene of the current generation
    #
    # Return: the index of the gene
    ##
    def getBestGene(self):
        best = 0
        for i in range(0, len(self.currentFitness)):
            if self.currentFitness[i] > self.currentFitness[best] :
                best = idea

        return best

    ##
    # buildState
    #
    # Description: build the state corresponding to the gene specified by the given index
    #
    # Parameters:
    #   -index : index of gene to build state for
    #
    # Return : state GameState object
    def buildState(self, index):
        pass


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

children = testGene.mateGenes(testGene2)

# check number of children
if not len(children) == 2:
    print('- Function mateGenes() failed test 1. Incorrect number of children: ', children)

# check length of children cells
if not len(children[0].cells) == testGene.numCells:
    print('- Function mateGenes() failed test 2. Child 1 wrong length: ', len(children[0].cells))
if not len(children[1].cells) == testGene.numCells:
    print('- Function mateGenes() failed test 3. Child 2 wrong length: ', len(children[1].cells))

# check format of child 1
inParent1 = True
error = -1
for i in range(0, len(children[0].cells)):
    if children[0].cells[i] == testGene.cells[i] and inParent1:
        continue
    elif  children[0].cells[i] == testGene2.cells[i]:
        inParent1 = False
    else:
        if error == -1:
            error = 0
        if error == 0:
            error = 1
            break
if error == 1:
    print('- Function mateGenes() failed test 4. Mating error with child 1.')

# check format of child 2
inParent1 = True
error = -1
for i in range(0, len(children[1].cells)):
    if children[1].cells[i] == testGene2.cells[i] and inParent1:
        continue
    elif  children[1].cells[i] == testGene.cells[i]:
        inParent1 = False
    else:
        if error == -1:
            error = 0
        if error == 0:
            error = 1
            break

if error == 1:
    print('- Function mateGenes() failed test 4. Mating error with child 2.')


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
