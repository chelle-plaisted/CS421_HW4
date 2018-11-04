import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *

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
        self.numCells = 80 # 40 for each owned half of the gameboard
        # Gene contents
        if cells == None:
            self.cells = self.initializeGene()
        else:
            self.cells = cells

    ##
    # initializeGene
    # Description: Generate a new gene reprsentation in array as follows:
    #   -populate all indicies with random number
    #   -indices 0-39 = AI player's side of board. On this half:
    #       -Top value: anthill location
    #       =Next value: tunnel location
    #       -Next 9 values: grass Locations
    #   -indices 40-79 = enemy player's side of board. On this half:
    #       -Top 2 values: enemy food Locations
    #   - array values stored in self.cells
    ##
    def initializeGene(self):
        self.cells = [random.randint(0, 2**31 -1)] * self.numCells

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
    ##
    def mateGenes(self, otherParent):
        pass

    ##
    # mutateGene
    #
    # Description: given an index to mutate, reset this specific cell to a new
    # random value.
    ##
    def mutateGene(self, index):
        if index < 0 or index > self.numCells - 1:
            pass # do nothing, this is an invalid index to mutate
        else:
            self.cells[index] = random.randint(0, 2**31 -1)

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
        if index >= self.numCells / 2:
            index += 20 # number of neutral cells
        # x location
        x = index % 10
        # y location
        y = index / 10

        return (x,y)

    ##
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
        constructions = []
        if phase == SETUP_PHASE_1:
            pass
        elif phase == SETUP_PHASE_2:
            pass

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
        super(AIPlayer,self).__init__(inputPlayerId, "Random")
        # general values to determine scope of algorithm
        self.popSize = 10 #TODO: increase to min 1000
        self.gamesPerGene = 10 #TODO increase to min 1000
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
        # return self.currentPop[self.indexToEval].getConstructions(currentState.phase)
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

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

    ## TODO COMPLETE
    # selectParents
    #
    # Description: select the parents to mate for the next child
    #
    # Return: a tuple of parent genes
    ##
    def selectParents(self):
        return(None, None)

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
            # otherwise, move to next
            if self.indexToEval == self.popSize - 1:
                self.indexToEval = 0
                self.makeNextGen()
            else:
                self.indexToEval += 1
            # reset the number of games played
            self.gamesPlayed = 0

################################################################################
#TODO COMPLETE
#UNIT TESTS
################################################################################

################################################################################
#def initializeGene(self):
################################################################################

################################################################################
#def mateGenes(self, otherParent):
################################################################################

################################################################################
#def mutateGene(self, index):
################################################################################

################################################################################
#def getCoords(index):
################################################################################

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
