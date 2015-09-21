__author__ = 'Max Robinson, Triton Pitassi'
import random
from Ant import *
from Building import *
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *

# # 
# AIPlayer
# Description: The responsbility of this class is to interact with the game by
# deciding a valid move based on a given game state. This class has methods that
# will be implemented by students in Dr. Nuxoll's AI course.
# 
# Variables:
#    playerId - The id of the player.
# # 
class AIPlayer(Player):

    # __init__
    # Description: Creates a new Player
    # 
    # Parameters:
    #    inputPlayerId - The id to give the new player (int)
    # # 
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "BFS")

    # # 
    # getPlacement
    # 
    # Description: called during setup phase for each Construction that
    #    must be placed by the player.  These items are: 1 Anthill on
    #    the player's side; 1 tunnel on player's side; 9 grass on the
    #    player's side; and 2 food on the enemy's side.
    # 
    # Parameters:
    #    construction - the Construction to be placed.
    #    currentState - the state of the game at this point in time.
    # 
    # Return: The coordinates of where the construction is to be placed
    # # 
    def getPlacement(self, currentState):
        numToPlace = 0
        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    # stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   # stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    # # 
    # getMove
    # Description: Gets the next move from the Player.
    # 
    # Parameters:
    #    currentState - The state of the current game waiting for the player's move (GameState)
    # 
    # Return: The Move to be made
    # # 
    def getMove(self, currentState):
        currentState.fastclone()
        moves = listAllLegalMoves(currentState)
        score = -1
        moveToMake = None
        for move in moves:
            newGameState = self.expandNode(currentState, move)
            tempScore = self.evaluateState(newGameState)
            if tempScore > score:
                score = tempScore
                moveToMake = move

        if moveToMake is None:
            return Move(END, None, None)

        return moveToMake

    # # 
    # getAttack
    # Description: Gets the attack to be made from the Player
    # 
    # Parameters:
    #    currentState - A clone of the current state (GameState)
    #    attackingAnt - The ant currently making the attack (Ant)
    #    enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    # # 
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        # Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]



    # #
    # expandNode
    #   NOTE: Assuming valid move
    #
    #  *** NOTE: Building a tunnel costs 3 food, and ends that workers turn. Builds tunnel at that location. ****
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
                self.pickUpFood(gameState, ourInventory, antToMove)
                self.dropOffFood(gameState, ourInventory, antToMove)

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
                ourInventory.constr.append(Building(move.coordList[-1], TUNNEL, self.playerId))
                ourInventory.foodCount -= 3
        else:
            print("IS ENDING TURN")
            return gameState

        return gameState

    def getOpponentId(self):
        opponentId = -1
        if self.playerId == 0:
            opponentId = 1
        else:
            opponentId = 0
        return opponentId

    ##
    # Ripped from Game file
    def isValidAttack(self, attackingAnt, attackCoord):
        if attackCoord == None:
            return None
        #we know we have an enemy ant
        range = UNIT_STATS[attackingAnt.type][RANGE]
        diffX = abs(attackingAnt.coords[0] - attackCoord[0])
        diffY = abs(attackingAnt.coords[1] - attackCoord[1])

        #pythagoras would be proud
        if range ** 2 >= diffX ** 2 + diffY ** 2:
            #return True if within range
            return True
        else:
            return False


    def attackSequence(self, enemyInv, antToMove ):
        attackedAntList = []
        for ant in enemyInv.ants:
            if self.isValidAttack(antToMove, ant.coords):
                #keep track of valid attack coords (flipped for player two)
                attackedAntList.append(self.state.coordLookup(ant.coords, self.playerId))

        if attackedAntList != []:
            antToAttack = attackedAntList[random.randint(0, len(attackedAntList))]
            # subtract health
            if antToMove == SOLDIER or antToMove == QUEEN:
                antToAttack.health -= 2
            else:
                antToAttack.health -= 1
            #if ant dies, remove it from list
            if antToAttack.health <= 0:
                enemyInv.ants.remove(antToAttack)


    def pickUpFood(self, gameState, ourInventory, antToMove):
        # check if food there
        if getConstrAt(gameState, antToMove.coords) is not None:
            if getConstrAt(gameState, antToMove.coords).type == FOOD and (not antToMove.carrying):
                antToMove.carrying = True

    def dropOffFood(self, gameState, ourInventory, antToMove):
        # check if landded on tunnel or anthill
        if getConstrAt(gameState, antToMove.coords) is not None:
            if getConstrAt(gameState, antToMove.coords).type == TUNNEL or \
                    getConstrAt(gameState, antToMove.coords).type == ANTHILL\
                    and antToMove.carrying:
                antToMove.carrying = False
                ourInventory.foodCount += 1


    def evaluateState(self, gameState):
        return random.random()
