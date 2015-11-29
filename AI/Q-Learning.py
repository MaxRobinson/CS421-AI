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
    #   - a generalized location for each ant (none queen), ( puts the ants on a 5x5 board instead of a 10 by 10 )
    #   - a generalized location for each queen
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
        myInventory = currentState.inventory[self.playerId]
        enemyInventory = currentState.inventory[(self.playerId + 1)%2]

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

        #EnemyAntCoords
        enemyAntCoords = [self.generalizeCoords(ant.coords) for ant in enemyInventory.ants]

        # add coords to ant positions
        for coords in enemyAntCoords:
            compressedState.antPositionList.append(coords)


        ## food
        compressedState.myFoodCount = myInventory.foodCount
        compressedState.enemyFoodCount = enemyInventory.foodCount


        hillLocation = myInventory.getAnthill.coords()
        ## check if anything is on my HILL location
        for coord in [x.coords for ant in myInventory.ants]:
            if coord == hillLocation:
                compressedState.anythingOnHill = True

        # if something already on it we know.
        if not compressedState.anythingOnHill:
            # otherwise check if enemy ants are on it.
            for coords in [x.coords for ant in enemyInventory.ants]:
                if coords == hillLocation:
                    compressedState.anythingOnHill = True


        print("hello world")


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
#   - a generalized location for each ant (none queen), ( puts the ants on a 5x5 board instead of a 10 by 10 )
#   - a generalized location for each queen (in ant position list)
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
        self.myTunnelLocations = None

        self.enemyHillLocation = None
        self.enemyTunnelLocations = None

        self.anythingOnHill = False

        self.myFoodCount = 0
        self.enemyFoodCount = 0


class UnitTests:
    def __init__(self):
        self.player = AIPlayer(1)

        print("Start Unit Tests: ")

    def testGeneralizeCoords(self):
        genCord = self.player.generalizeCoords((2,3))
        if genCord == (1,1):
            print("GenCoords: Good!")
        else:
            print("GenCoords: BAD!")




unitTest = UnitTests()
unitTest.testGeneralizeCoords()