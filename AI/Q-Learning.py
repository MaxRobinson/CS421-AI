__author__ = 'MaxRobinson'
import random
import pickle
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *


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
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "Random")

    ##
    #getPlacement
    #
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
        return moves[random.randint(0,len(moves) - 1)]

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
    # consolidateState
    #   Given a state, consolidates the state to only needed information.
    # the information needed in the consolidated state is as follows:
    #   - a generalized location for each ant (including queen), ( puts the ants on a 5x5 board instead of a 10 by 10 )
    #   - a generalized location for each ant hill and tunnel
    #   - a boolean of if my queen is on the ant hill or not.
    #       - The queen could be on the " same " generalized location as the ant hill but not ACTUALLY be on the
    #             ant hill, thus needing the boolean to say if this is true or not.
    #
    # Parameters:
    #     currentState: the state to compress.
    #
    ##
    def consolidateState(self, currentState):
        myInventory = currentState.inventories[self.playerId]
        enemyInventory = currentState.inventories[(self.playerId + 1)%2]

        # create compressed state
        compressedState = state()

        # add attributes to compressed state
        # add my ant hill generalized location
        compressedState.myHillLocation = self.generalizeCoords(myInventory.getAnthill().coords)

        # list comprehension over the list of possible FRIENDLY tunnel locations and generalizing their coordinates
        compressedState.myTunnelLocations = [self.generalizeCoords(x.coords) for x in myInventory.getTunnels()]

        # add enemy ant hill generalized location
        compressedState.enemyHillLocation = self.generalizeCoords(enemyInventory.getAnthill().coords)

        # list comprehension over the list of possible ENEMY tunnel locations and generalizing their coordinates
        compressedState.enemyTunnelLocations = [self.generalizeCoords(x.coords) for x in enemyInventory.getTunnels()]

        # list comprehension over the list of ants and getting their generalized location
        myAntCoords = [self.generalizeCoords(ant.coords) for ant in myInventory.ants]

        for coords in myAntCoords:
            compressedState.antPositionList.append(coords)

        # EnemyAntCoords
        enemyAntCoords = [self.generalizeCoords(ant.coords) for ant in enemyInventory.ants]

        # add coords to ant positions
        for coords in enemyAntCoords:
            compressedState.antPositionList.append(coords)

        # food
        compressedState.myFoodCount = myInventory.foodCount
        compressedState.enemyFoodCount = enemyInventory.foodCount

        # check if anything is on my HILL location
        compressedState.anythingOnHill = self.anythingOnHill(myInventory, enemyInventory)


        # return the fully compressed state.
        return compressedState



    ## TODO
    def anythingOnHill(self, myInventory, enemyInventory):
        hillLocation = myInventory.getAnthill().coords
        onHillValue = False
        for coord in [ant.coords for ant in myInventory.ants]:
            if coord == hillLocation:
                onHillValue = True

        # if something already on it we know.
        if not onHillValue:
            # otherwise check if enemy ants are on it.
            for coords in [ant.coords for ant in enemyInventory.ants]:
                if coords == hillLocation:
                    onHillValue = True

        return onHillValue


    ##
    # generalizeCoords
    #   Given coordinates, turn those coordinates (on a 10x10) into coords on a (5x5)
    # Parameters:
    #   coords: tuple containing x,y coords (x,y)
    #
    # Return:
    #   generalized coords (x/2, y/2)
    ##
    def generalizeCoords(self, coords):
        return (coords[0]/2, coords[1]/2)


##
# class State:
#  A state has the following attributes.
#   - a generalized location for each ant (including queens), ( puts the ants on a 5x5 board instead of a 10 by 10 )
#   - a generalized location for each ant hill and tunnel
#   - a boolean of if any ant is on the ant hill or not.
#       * Any ant could be on the "same" generalized location as the ant hill but not ACTUALLY be on the
#             ant hill, thus needing the boolean to say if this is true or not.
#   - FOOD COUNT for both players
#
##
class state:


    ## TODO ##
    def __init__(self):
        self.antPositionList = []

        self.myHillLocation = None
        self.myTunnelLocations = []

        self.enemyHillLocation = None
        self.enemyTunnelLocations = []

        self.anythingOnHill = False

        self.myFoodCount = 0
        self.enemyFoodCount = 0


    def __eq__(self, other):
        if set(self.antPositionList) == set(other.antPositionList) and \
            self.myHillLocation == other.myHillLocation and \
            set(self.myTunnelLocations) == set(other.myTunnelLocations) and \
            self.enemyHillLocation == other.enemyHillLocation and \
            set(self.enemyTunnelLocations) == set(other.enemyTunnelLocations) and \
            self.anythingOnHill == other.anythingOnHill and \
            self.myFoodCount == other.myFoodCount and \
            self.enemyFoodCount == other.enemyFoodCount:

            return True

    def __hash__(self):
        return hash((tuple(self.antPositionList), self.myHillLocation,
                     tuple(self.myTunnelLocations), self.enemyHillLocation,
                     tuple(self.enemyTunnelLocations), self.anythingOnHill,
                     self.myFoodCount, self.enemyFoodCount))


from GameState import *
from Location import *
from Inventory import *
from Construction import *
from Ant import *

class UnitTests:


    def __init__(self):
        self.player = AIPlayer(PLAYER_ONE)
        self.state = state()

        print("Start Unit Tests: ")

    def testGeneralizeCoords(self):
        genCord = self.player.generalizeCoords((2,3))
        if genCord == (1,1):
            print("GenCoords: Good!")
        else:
            print("GenCoords: BAD!")

    def testStateEquality(self):
        if(self.state.__eq__(self.state)):
            print("State Equality: Equal")
        else:
            print("State Equality: Equal")

    def testStateHash(self):
        print("Init Hash Value: ", self.state.__hash__())

        self.state.enemyFoodCount = 1
        print("Next Hash Value: ", self.state.__hash__())
        temp = set()
        temp.add(self.state)
        print("Added a state to a set")


    def testCompressState(self):
        print("compressing State")
        tempState = self.setupState()


        compressedState = self.player.consolidateState(tempState)

        expectedCompressedState = state()
        expectedCompressedState.myHillLocation = (0,1)
        expectedCompressedState.myTunnelLocations = [(0,1)]

        expectedCompressedState.enemyHillLocation = (0,3)
        expectedCompressedState.enemyTunnelLocations = [(0,3)]

        expectedCompressedState.antPositionList = [(0,1), (0,3), (0,3)]
        expectedCompressedState.anythingOnHill = True

        if(compressedState.__eq__(expectedCompressedState)):
            print("Compression worked!!!!!!")
        else:
            print("Compression failed!!!!!!")
            attrs = vars(expectedCompressedState)
            print("Expected State: ")
            print(','.join("%s: %s" % item for item in attrs.items()))

            attrs2 = vars(compressedState)
            print("Actual State: ")
            print(','.join("%s: %s" % item for item in attrs2.items()))

    def testDictionaryAndState(self):
        dictThing = {}
        dictThing[self.state] = 15
        print(dictThing[self.state])



    def setupState(self):
        board = [[Location((col, row)) for row in xrange(0, BOARD_LENGTH)] for col in xrange(0, BOARD_LENGTH)]
        p1Inventory = Inventory(PLAYER_ONE, [], [], 0)
        p2Inventory = Inventory(PLAYER_TWO, [], [], 0)
        neutralInventory = Inventory(NEUTRAL, [], [], 0)

        self.putFood(neutralInventory)
        self.putOurInventory(p1Inventory)
        self.putTheirInventory(p2Inventory)

        state = GameState(board, [p1Inventory, p2Inventory, neutralInventory], PLAY_PHASE, PLAYER_ONE)

        return state

    # #
    # putFood
    # Description: places the Food for our set up for our gameState for the Unit Test
    #
    # Parameters:
    #   neutralInventory - the inventory where grass and food is placed
    #
    # Return: Nothing
    # #
    def putFood(self, neutralInventory):
        for i in range(0,9):
            ourGrass = Construction((i, 0), GRASS)
            otherGrass = Construction((i,9), GRASS)
            neutralInventory.constrs.append(ourGrass)
            neutralInventory.constrs.append(otherGrass)
        for i in range(0,2):
            ourFood = Construction((i,1), FOOD)
            otherFood = Construction((i,8), FOOD)
            neutralInventory.constrs.append(ourFood)
            neutralInventory.constrs.append(otherFood)


    # #
    # putOurInventory
    # Description: places the ants and anthill for our set up for our AI's inventory for the gameState for the Unit Test
    #
    # Parameters:
    #   inventory - the inventory for our AI.
    #
    # Return: Nothing
    # #
    def putOurInventory(self, inventory):
        inventory.constrs.append(Construction((0,3), ANTHILL))
        inventory.constrs.append(Construction((1,3), TUNNEL))
        inventory.ants.append(Ant((0,3), QUEEN, PLAYER_ONE)) # Queen
        inventory.ants.append(Ant((0,6), DRONE, PLAYER_ONE)) # Queen


    # #
    # putTheirInventory
    # Description: places the ants and anthill for our set up for our opponent's inventory
    # for the gameState for the Unit Test
    #
    # Parameters:
    #   inventory - the inventory for our opponent.
    #
    # Return: Nothing
    # #
    def putTheirInventory(self, inventory):
        inventory.constrs.append(Construction((0, 7), ANTHILL))
        inventory.constrs.append(Construction((1, 7), TUNNEL))
        queen = Ant((0, 7), QUEEN, PLAYER_TWO)
        queen.health = 1
        inventory.ants.append(queen) # Queen

    # #
    # equalStates
    # Description: Checks if two game states are equal
    #
    # Parameters:
    #   state1 - a game state
    #   state2 - a game state to check against.
    #
    # Return: Boolean: True if equal, False if Not
    # #
    def equalStates(self, state1, state2):
        if state1.phase != state2.phase or state1.whoseTurn != state2.whoseTurn:
            return False
        for i in range(0,3):
            state1Inv = state1.inventories[i]
            state2Inv = state1.inventories[i]
            if len(state1Inv.constrs) != len(state2Inv.constrs):
                return False
            for j in range(0, len(state1Inv.constrs)):
                if state1Inv.constrs[i] != state1Inv.constrs[i]:
                    return False
            if i < 2:
                if len(state1Inv.ants) != len(state2Inv.ants):
                    return False
                for k in range(0, len(state1Inv.ants)):
                    if state1Inv.ants[i] != state1Inv.ants[i]:
                        return False
                if state1Inv.foodCount != state2Inv.foodCount:
                    return False
        return True


unitTest = UnitTests()
unitTest.testGeneralizeCoords()
unitTest.testStateHash()
unitTest.testStateEquality()
unitTest.testCompressState()
unitTest.testDictionaryAndState()