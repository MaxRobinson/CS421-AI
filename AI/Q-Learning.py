__author__ = 'MaxRobinson'
import random
import pickle
import os
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *


## Global Constants
INIT_ET = 1.0

STATE_INDEX = 0
UTILITY_INDEX = 1
ET_INDEX = 2


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
        super(AIPlayer,self).__init__(inputPlayerId, "TD-Learning")
        self.memoryFileName = "robinsom16_TD-Learning.txt"
        self.alphaValueFileName = "robinsom16_TD-AlphaValue.txt"
        self.epsilonValueFileName = "robinsom16_TD-EpsilonValue.txt"

        self.alphaExponentNumber = -0.2
        self.gameNumber = 1

        self.gamma = .8
        self.alpha = .999
        self.lambdaValue = .95
        self.epsilon = .99

        # key: HASH VALUE of a given compressed State,
        # Value: list [ compressedState, Utility value, EligibilityTrace value]
        self.stateUtilityMemory = {}

        # If we have an existing memory, Load it!!! If not don't do anything.
        if(os.path.isfile("robinsom16_TD-Learning.txt")):
            self.readMemory()

        # If we have an alpha value, Load it!!! If not don't do anything.
        if(os.path.isfile("robinsom16_TD-AlphaValue.txt")):
            self.readAlphaValue()

        # If we have an alpha value, Load it!!! If not don't do anything.
        if(os.path.isfile("robinsom16_TD-EpsilonValue.txt")):
            self.readEpsilonValue()

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
    # getMove
    # Description:
    #   First, updates the AI's Memory based on the state it is currently in.
    #   Then, it gets the next move from the Player, based on possible moves and an expand node fucntion.
    #
    # Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return:
    #   move - The Move to be made
    ##
    def getMove(self, currentState):

        # compress state
        compressedState = self.consolidateState(currentState)

        # first: update memory
        self.updateMemory(compressedState)

        # Second: find the best possible move or explore
        move = self.getBestMove(currentState)

        return move


    ##
    # getBestMove
    #   Description:
    #   Given a current state, this method looks at all of the possible moves that can be made,
    #   If we role, and we get a number less than epsilon (the explore value) then we choose a random move
    #   Otherwise, we expand the move and get back what the state would look like if we took that move,
    #       we then compress this state, and see if that state is in our Memory.
    #       If it is in our memory, we see if it has the maximum util value of the other reachable states,
    #           if it is, then we update the maxUtil seen and set the move to return to the move associated with
    #           getting to that state.
    #       If it is not in our memory we skip it.
    #   If at the end, we have not found any states that match in our memory, make a random move.
    ##
    def getBestMove(self, currentState):

        # get all possible moves.
        moves = listAllLegalMoves(currentState)
        move = None

        role = random.random()
        # if less than epsilon, explore via random move
        if(role < self.epsilon):
            move = moves[random.randint(0,len(moves) - 1)]
        elif(move == None):
            maxUtil = 0
            for posMove in moves:
                # get the state we'd be in with the move
                expandState = self.expandNode(currentState, posMove)

                # compress the state after that move
                compressPosState = self.consolidateState(expandState)

                # get the key into the dictionary for that state
                key = compressPosState.__hash__()

                #if that state is in the dictionary
                if key in self.stateUtilityMemory:
                    # get that states util
                    keyUtil = self.stateUtilityMemory[key][UTILITY_INDEX]

                    # if it's the best util we've seen set the move equal to that move, and update the maxUtil
                    if keyUtil > maxUtil:
                        maxUtil = keyUtil
                        move = posMove

        # if for some reason the move is still none, get a random move
        # this could occur if we haven't seen any of the states that the moves could give us.
        if(move is None):
            move = moves[random.randint(0, len(moves) - 1)]

        return move


    ## TODO
    def updateMemory(self, compressedState):
        # if the current state is not in memory, add it to memory, and give the utility the reward value of the state
        if compressedState.__hash__() not in self.stateUtilityMemory:
            self.stateUtilityMemory[compressedState.__hash__()] = [compressedState, self.getReward(compressedState), INIT_ET]

        # get the values stored for current state -
        currentStateUtilAndEt = self.stateUtilityMemory[compressedState.__hash__()]

        # update all states Utilities using Eligibility Trace.
        for key in self.stateUtilityMemory:
            utilAndEt = self.stateUtilityMemory[key]
            state = utilAndEt[STATE_INDEX]
            stateUtil = utilAndEt[UTILITY_INDEX]
            stateEt = utilAndEt[ET_INDEX]

            # update the Util Value of all states
            # equation: where s' is my current state
            # U(s) = U(s) + alpha(reward(s) + gama(U(s')) - U(s))
            utilAndEt[UTILITY_INDEX] = stateUtil + stateEt * self.alpha*(self.getReward(state) +
                                           self.gamma*(currentStateUtilAndEt[UTILITY_INDEX]) - stateUtil )

            # update the ET value of all states
            utilAndEt[ET_INDEX] = stateEt * self.lambdaValue * self.gamma

        # if we have seen this state before, Reset the ET value
        if compressedState.__hash__() in self.stateUtilityMemory:
            currentStateUtilAndEt[ET_INDEX] = 1

        return
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
    # registerWin():
    # Description: Upon a game ending, save the AI's memory to file.
    #
    # Parameter: hasWon - a boolean saying if we have won or not.
    ##
    def registerWin(self, hasWon):

        # create a win or lose state ( based on if we won or lost)
        winComppressedState = state()
        winComppressedState.hasWon = hasWon
        winComppressedState.hasLost = not hasWon

        # use the win or lose state to update the memory
        self.updateMemory(winComppressedState)
        self.alpha *= 0.999
        self.epsilon *= 0.99

        # save info
        self.saveMemory()
        self.saveAlphaValue()
        self.saveEpsilonValue()


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
    #   currentState - the state to compress.
    #
    # Return:
    #   compressedState - a fully compressed state that has only the info needed for the AI
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

        # check if we have won.
        compressedState.hasWon = self.hasWon(self.playerId, currentState)

        # check if we have Lost.
        # giving it the opponents ID.
        compressedState.hasLost = self.hasWon((self.playerId + 1) % 2, currentState)


        # return the fully compressed state.
        return compressedState



    ##
    # anythingOnHill
    #   This returns a true/false value that says if there is anything that is on the "True"
    #   location of the AI's antHill.
    #
    #   NOTE: This does not look at the compressed version of the state
    #
    # Return:
    #   onHillValue - true if something is on the hill, false if not.
    ##
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
    # getReward
    #   Gives the reward for the AI based on a given state of winning or loosing or if in game.
    #
    # Parameter:
    #   gameOver: Boolean of if the game is over
    #   hasWon: Boolean of if the player has won or not. (should be false if gameOver is false)
    #
    # Return:
    #   rewardValue - the value of the reward based on the state
    ##
    # def getReward(self, gameOver, hasWon):
    #     # +1 for win
    #     # -1 for loss
    #     # else: -0.01
    #     if(gameOver):
    #         if(hasWon):
    #             return 1.0
    #         else:
    #             return -1.0
    #     else:
    #         return -0.01



    def getReward(self, compressedState):
        # +1 for win
        # -1 for loss
        # else: -0.01
        if(compressedState.hasWon):
            return 1.0
        elif(compressedState.hasLost):
            return -1.0
        else:
            return -0.01


    ##
    # saveMemory
    #   saves the stateUtilityMemory out to a file using pickle serialization
    ##
    def saveMemory(self):
        outputFile = file(self.memoryFileName, "w")
        pickle.dump(self.stateUtilityMemory, outputFile)
        outputFile.close()


    ##
    # saveAlphaValue
    #   Saves alpha value to file to a file so that the AI may continue learning after a given number of games.
    #   (Aka. pick up where it left off).
    ##
    def saveAlphaValue(self):
        outputFile = file(self.alphaValueFileName, "w")
        outputFile.write(str(self.alpha))
        outputFile.close()


    def saveEpsilonValue(self):
        outputFile = file(self.epsilonValueFileName, "w")
        outputFile.write(str(self.epsilon))
        outputFile.close()


    ##
    # readMemory
    #   reads from an input file and sets the value of the AI's "Memory" to what was in the output file
    #
    #   NOTE: !!!!! MODIFIES stateUtilityMemory !!!!!
    ##
    def readMemory(self):
        inputFile = file(self.memoryFileName, "r")
        self.stateUtilityMemory = pickle.load(inputFile)
        inputFile.close()


    ##
    # readAlphaValue
    #   Saves alpha value to file to a file so that the AI may continue learning after a given number of games.
    #   (Aka. pick up where it left off).
    ##
    def readAlphaValue(self):
        inputFile = file(self.alphaValueFileName, "r")
        self.alpha = float(inputFile.read())
        inputFile.close()

    ##
    # readEpsilonValue
    #   Reads alpha value to file to a file so that the AI may continue learning after a given number of games.
    #   (Aka. pick up where it left off).
    ##
    def readEpsilonValue(self):
        inputFile = file(self.epsilonValueFileName, "r")
        self.epsilon = float(inputFile.read())
        inputFile.close()

    # #
    # expandNode
    # Description: This method takes a game state, and a move, and applies the move
    #   to the game State to depict what the game state would look like after the move is made
    #
    # Parameters:
    #    currentState - A clone of the current state (GameState)
    #    move - a game move to be executed to expand the state
    # #
    def expandNode(self, currentState, move):
        gameState = currentState.fastclone()
        ourInventory = gameState.inventories[self.playerId]
        if(move.moveType == MOVE_ANT):
            antToMove = None
            for ant in ourInventory.ants:
                if ant.coords == move.coordList[0]:
                    antToMove = ant
            if antToMove is not None:
                antToMove.coords = move.coordList[-1]
                antToMove.hasMoved = True

                # check if other ants near by for attack
                opponentId = self.getOpponentId()
                enemyInv = gameState.inventories[opponentId]
                ## Checks if can attack.
                self.attackSequence(enemyInv, antToMove)

        elif(move.moveType == BUILD):
            # just worried about building Ants and Tunnel
            if(move.buildType == WORKER):
                # add ant
                ourInventory.ants.append(Ant(move.coordList[-1], WORKER, self.playerId))
                # subtract food
                ourInventory.foodCount -= 1
            elif(move.buildType == DRONE):
                ourInventory.ants.append(Ant(move.coordList[-1], DRONE, self.playerId))
                ourInventory.foodCount -= 1
            elif(move.buildType == SOLDIER):
                ourInventory.ants.append(Ant(move.coordList[-1], SOLDIER, self.playerId))
                ourInventory.foodCount -= 2
            elif(move.buildType == R_SOLDIER):
                ourInventory.ants.append(Ant(move.coordList[-1], R_SOLDIER, self.playerId))
                ourInventory.foodCount -= 2
            elif(move.buildType == TUNNEL):
                ourInventory.constrs.append(Building(move.coordList[-1], TUNNEL, self.playerId))
                ourInventory.foodCount -= 3
        else:
            self.pickUpFood(gameState, ourInventory)
            self.dropOffFood(gameState, ourInventory)
            return gameState

        return gameState

    # #
    # attackSequence
    # Description: This method determines if there are any valid attacks for ourAI, and if so,
    #   to evaluate the attack by picking a random enemy to attack.
    #
    # Parameters:
    #    enemyInv - The opponents Inventory
    #    antToMove - The ant that is moving into attack range.
    #
    # Return: Nothing
    # #
    def attackSequence(self, enemyInv, antToMove ):
        attackedAntList = []
        for ant in enemyInv.ants:
            if self.isValidAttack(antToMove, ant.coords):
                # keep track of valid ants to attack
                attackedAntList.append(ant)

        if len(attackedAntList) > 0:
            antToAttack = attackedAntList[random.randint(0, len(attackedAntList)-1)]
            # subtract health
            if antToMove == SOLDIER or antToMove == QUEEN:
                antToAttack.health -= 2
            else:
                antToAttack.health -= 1
            #if ant dies, remove it from list
            if antToAttack.health <= 0:
                enemyInv.ants.remove(antToAttack)

    # #
    # isValidAttack
    # Description: Determines if an attack is valid.
    #   This method was taken from the Game.py file, and slightly modified by current authors.
    #
    # Parameters:
    #    attackingAnt - The ant that will be attacking
    #    attackCoord - The Coords of where the ant is attacking
    #
    # Return: A boolean: True for Valid attack, False otherwise.
    def isValidAttack(self, attackingAnt, attackCoord):
        if attackCoord == None:
            return None
        # we know we have an enemy ant
        range = UNIT_STATS[attackingAnt.type][RANGE]
        diffX = abs(attackingAnt.coords[0] - attackCoord[0])
        diffY = abs(attackingAnt.coords[1] - attackCoord[1])

        # pythagoras would be proud
        if range ** 2 >= diffX ** 2 + diffY ** 2:
            # return True if within range
            return True
        else:
            return False

    # #
    # getOpponentId
    # Description: Helper method to get the opponent's ID
    #
    # Parameters:
    #    None
    #
    # Return: The opponent's ID
    # #
    def getOpponentId(self):
        opponentId = -1
        if self.playerId == 0:
            opponentId = 1
        else:
            opponentId = 0
        return opponentId

    ##
    # pickUpFood
    # Description: This method edits the game state to pickUP food if a worker ant that can carry is standing
    #   on food.
    #
    # Parameters:
    #    gameState - The state being edited.
    #    ourInventory - our Inventory
    #
    # Return: Nothing
    # #
    def pickUpFood(self, gameState, ourInventory):
        # check if food there
        for ant in ourInventory.ants:
            if getConstrAt(gameState, ant.coords) is not None:
                if getConstrAt(gameState, ant.coords).type == FOOD and (not ant.carrying):
                    ant.carrying = True

    # #
    # dropOffFood
    # Description: This method edits the game state to drop off food if a worker ant with food is standing
    #   on a tunnel or anthill.
    #
    # Parameters:
    #    gameState - The state being edited.
    #    ourInventory - our Inventory
    #
    # Return: Nothing
    # #
    def dropOffFood(self, gameState, ourInventory):
        # check if landded on tunnel or anthill
        for ant in ourInventory.ants:
            if getConstrAt(gameState, ant.coords) is not None:
                if getConstrAt(gameState, ant.coords).type == TUNNEL or \
                        getConstrAt(gameState, ant.coords).type == ANTHILL\
                        and ant.carrying:
                    ant.carrying = False
                    ourInventory.foodCount += 1

    ##
    #hasWon(int)
    #Description: Determines whether the game has ended in victory for the given player.
    #
    #Parameters:
    #   playerId - The ID of the player being checked for winning (int)
    #
    #Returns: True if the player with playerId has won the game.
    ##
    def hasWon(self, playerId, state):
        opponentId = (playerId + 1) % 2

        if ((state.phase == PLAY_PHASE) and
        ((state.inventories[opponentId].getQueen() == None) or
        # (state.inventories[opponentId].getAnthill().captureHealth <= 0) or
        (state.inventories[playerId].foodCount >= FOOD_GOAL) or
        (state.inventories[opponentId].foodCount == 0 and
            len(state.inventories[opponentId].ants) == 1))):
            return True
        else:
            return False

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

        self.hasWon = False
        self.hasLost = False


    def __eq__(self, other):
        if set(self.antPositionList) == set(other.antPositionList) and \
            self.myHillLocation == other.myHillLocation and \
            set(self.myTunnelLocations) == set(other.myTunnelLocations) and \
            self.enemyHillLocation == other.enemyHillLocation and \
            set(self.enemyTunnelLocations) == set(other.enemyTunnelLocations) and \
            self.anythingOnHill == other.anythingOnHill and \
            self.myFoodCount == other.myFoodCount and \
            self.enemyFoodCount == other.enemyFoodCount and \
            self.hasWon == other.hasWon and \
            self.hasLost == other.hasLost:

            return True

    def __hash__(self):
        return hash((tuple(self.antPositionList), self.myHillLocation,
                     tuple(self.myTunnelLocations), self.enemyHillLocation,
                     tuple(self.enemyTunnelLocations), self.anythingOnHill,
                     self.myFoodCount, self.enemyFoodCount,
                     self.hasWon, self.hasLost))


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
        expectedCompressedState.hasWon = True
        expectedCompressedState.hasLost = False

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
        dictThing[self.state.__hash__()] = 15
        self.state.myFoodCount = 1
        dictThing[self.state.__hash__()] = 10
        print("Testing dictionary usage: ", dictThing)

    def testMemoryWrite(self):
        self.player.stateUtilityMemory[self.state.__hash__()] = 10
        self.player.saveMemory()

    def testMemoryRead(self):
        self.player.readMemory()
        print("Testing READ from file: ",  self.player.stateUtilityMemory)

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

##test read and write ##
unitTest.testMemoryWrite()
unitTest.testMemoryRead()
