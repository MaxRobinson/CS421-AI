__author__ = 'Max'

from Player import *


import random
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
        super(AIPlayer,self).__init__(inputPlayerId, "HeuristicAI")

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
            locations = []
            
            #  place ant hills
            antHillMove = (2,1)
            antTunelMove = (7,1)
            locations.append(antHillMove)
            locations.append(antTunelMove)
            
            numToPlace = 9
            for i in range(0, numToPlace):
                move = (i,3)
                currentState.board[i][3].constr == True
                locations.append(move)
            return locations

        elif currentState.phase == SETUP_PHASE_2:   # stuff on foe's side
            # set opponent id
            opponentId = PLAYER_ONE
            if self.playerId is PLAYER_ONE:
                opponentId = PLAYER_TWO

            locations = self.findFurthestSpacesForFood(currentState, opponentId)
            return locations

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
        # moves = listAllLegalMoves(currentState)
        # get food coords
        # foodList = self.findFood(currentState)
        foodConstrList = getConstrList(currentState, None, [FOOD])
        foodCoordList = []
        for food in foodConstrList:
            foodCoordList.append(food.coords)
        buildingList = getConstrList(currentState, self.playerId, [ANTHILL])
        listOfWorkers = getAntList(currentState, self.playerId, [WORKER])
        listOfSoldiers = getAntList(currentState, self.playerId, [SOLDIER])

        buildWorker = self.checkWorkers(currentState, listOfWorkers)
        if buildWorker is not None:
            return buildWorker
        buildSoldier = self.checkSoldier(currentState, listOfSoldiers)
        if buildSoldier is not None:
           return buildSoldier

        # get List of  worker ants
        moveList = listAllMovementMoves(currentState)

        antMoves = []
        soldierMoves = []
        workerMoves = []
        queenMoves = []
        for move in moveList:
            if move.moveType == MOVE_ANT:
                ant = getAntAt(currentState, move.coordList[0])
                if ant.type == WORKER:
                    workerMoves.append(move)
                elif ant.type == QUEEN:
                    queenMoves.append(move)
                elif ant.type == SOLDIER:
                    soldierMoves.append(move)
                antMoves.append(move)

        for antMove in antMoves:
            ant = getAntAt(currentState, antMove.coordList[0])
            if ant.type == WORKER:
                return self.moveWorker(currentState, ant, workerMoves, foodCoordList)
            if ant.type == QUEEN:
                queenMove = self.moveQueen(currentState, ant, queenMoves, foodCoordList, buildingList)
                if queenMove is not None:
                    return queenMove
            if ant.type == SOLDIER:
                soldierMove = self.moveSoldier(currentState, ant, soldierMoves, self.getOpponentId())
                return soldierMove

        return Move(END, None, None)

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
    # findFurthestSpacesForFood
    #
    # Description: called during step two of the setup phase
    #   to find the furthest places from the opponents Anthill
    #   and tunnel that we can place food.
    #
    # Parameters:
    #    currentState - the state of the game at this point in time.
    #    opponentId - the id of the opponent.
    #
    # Return: The locations for the food to be placed.
    # #
    def findFurthestSpacesForFood(self, currentState, opponentId):
        location = []
        distanceToConstruct = []

        # identify the location of the anthill
        anthillLocation = getConstrList(currentState, opponentId, [ANTHILL])[0].coords
        tunnelLocation = getConstrList(currentState, opponentId, [TUNNEL])[0].coords

        # identify the location farthest from an anthill or tunnel
        # loop over all squares on opponents side of board
        for i in range(0, 10):
            for j in range(6, 10):
                coordinate = (i, j)
                if getConstrAt(currentState, coordinate) is not None:
                    continue
                distance1 = stepsToReach(currentState, anthillLocation, coordinate)
                distance2 = stepsToReach(currentState, tunnelLocation, coordinate)
                distance = min(distance1, distance2)

                distanceToConstruct.append((coordinate, distance))

        # identify the 2 coordinates with the most distance
        greatestDistance = distanceToConstruct[0]
        secondGreatestDistance = distanceToConstruct[1]
        for square in distanceToConstruct:
            if square == greatestDistance or square == secondGreatestDistance:
                continue
            if square[1] > greatestDistance[1]:
                temp = greatestDistance
                greatestDistance = square
                if temp[1] > secondGreatestDistance[1]:
                    secondGreatestDistance = temp
            elif square[1] > secondGreatestDistance[1]:
                temp = secondGreatestDistance
                secondGreatestDistance = square
                if temp[1] > greatestDistance[1]:
                    greatestDistance = temp

        location.append(greatestDistance[0])
        location.append(secondGreatestDistance[0])
        return location

    # #
    # getBestMove
    #
    # Description: Given a list of moves, a destination and an ant,
    #   find the shortest path from the ant's current location to
    #   the destination, given the list of available moves
    #
    # Parameters:
    #   currentState - the state of the game at this point in time.
    #   movesList - a list of legal moves.
    #   destCoord - the destination coordinate.
    #   ant - the current ant that is being moved.
    #
    # Return: The move from the movesList, that provides the greatest
    #   movement towards the destCoord
    # #
    def getBestMove(self, currentState, movesList, destCoord, ant):

        minDist = 30 # arbitrarily large number
        finalMove = []  # declare object

        for move in movesList:
            if move.coordList[0] == ant.coords:
                length = len(move.coordList)
                endCoord = move.coordList[length-1]
                dist = stepsToReach(currentState, endCoord, destCoord)

                if dist < minDist:
                    minDist = dist
                    finalMove = move

        return finalMove

    # #
    # bestFood
    #
    # Description: this method determines which food is the closest food
    # for the worker to go to get food.
    #
    # Parameters:
    #   currentState - the state of the game at this point in time.
    #   ant - the current ant that is being moved
    #   foodList - A COORDINATE list of the location of the food
    #
    # Return: the coordinate of the closest food.
    # #
    def bestFood(self, currentState, ant, foodList):
        dist1 = stepsToReach(currentState, ant, foodList[0])
        dist2 = stepsToReach(currentState, ant, foodList[1])
        if dist1 < dist2:
            return foodList[0]
        else:
            return foodList[1]

    # #
    # moveWorker
    #
    # Description: Given a list of moves, a destination and an ant,
    #   find the shortest path from the ant's current location to
    #   the destination, given the list of available moves
    #
    # Parameters:
    #   currentState - the state of the game at this point in time.
    #   movesList - a list of legal moves.
    #   destCoord - the destination coordinate.
    #   ant - the current ant that is being moved.
    #
    # Return: The move from the movesList, that provides the greatest
    #   movement towards the destCoord
    # #
    def moveWorker(self, currentState, ant, legalMoves, foodList):
        if not ant.hasMoved:
            if not ant.carrying:
                # FInd FOod Phase
                # find Closest Food to our ant
                food = self.bestFood(currentState, ant.coords, foodList)
                moves = self.getBestMove(currentState, legalMoves, food, ant)
                return moves
            elif ant.carrying:
                # Get Home Phase
                tunnel = getConstrList(currentState, self.playerId, [TUNNEL])[0]
                moves = self.getBestMove(currentState, legalMoves, tunnel.coords, ant)
                return moves

    # #
    # moveQueen
    #
    # Description: Moves the queen off of the anthill.
    #
    # Parameters:
    #   currentState - the state of the game at this point in time.
    #   queen - the queen ant
    #   legalMoves - a list of legal moves for the queen.
    #   foodList - a list of coordinates of food locations
    #   buildingList - a list of friendly buildings * assumed its the anthill
    #
    # Return: If the queen is on the ant hill move off of the anthill.
    # #
    def moveQueen(self, currentState, queen, legalMoves, foodList, buildingList):
        if queen.coords == buildingList[0].coords:
            coords = queen.coords
            for move in legalMoves:
                lastCoord = move.coordList[len(move.coordList)-1]
                if lastCoord != buildingList[0].coords and lastCoord != foodList[0] and lastCoord != foodList[1]:
                    return move
        # check if there are any adjacent ants  that are enemies
        adjacentList = listAdjacent(queen.coords)
        enemyAnts = getAntList(currentState, self.getOpponentId(), (QUEEN, WORKER, DRONE, SOLDIER, R_SOLDIER))
        for enemy in enemyAnts:
            for adjacent in adjacentList:
                if enemy.coords == adjacent:
                    # MOVE QUEEN
                    return self.queenRunAway(currentState, legalMoves, queen, enemy, foodList, buildingList)

    # #
    # moveSoldier
    #
    # Description: Given a soldier ant, find the shortest path needed
    #   to attack the opposing queen, and do so.
    #
    # Parameters:
    #   currentState - the state of the game at this point in time.
    #   soldier - the soldier ant that is being moved
    #   legalMoves - a list of legal moves for Soldier Ants.
    #   opponentId - Id of the opponent player.
    #
    # Return: return the move that gets us the closest to the opposing
    #   queen so that we may attack it.
    # #
    def moveSoldier(self, currentState, soldier, legalMoves, opponentId):
        # get opposite queen location
        opQueen = getAntList(currentState, opponentId, [QUEEN])
        moves = self.getBestMove(currentState, legalMoves, opQueen[0].coords, soldier)
        return moves

    # #
    # checkWorkers
    #
    # Description:  Checks to ensure that there are enough workers.
    #   If there are enough workers, return nothing.
    #   if there are not enough, return a build move to build one,
    #       if that is possible.
    #
    # Parameters:
    #   currentState - the state of the game at this point in time.
    #   workerList- a list of all of the worker ants owned by AI.
    #
    # Return: A build worker move, or None
    # #
    def checkWorkers(self, currentState, workerList):
        if len(workerList) < 2:
            # create new worker
            legalBuilds = listAllBuildMoves(currentState)
            if len(legalBuilds) != 0:
                for build in legalBuilds:
                    if build.buildType == WORKER:
                        return build

    # #
    # checkSoldier
    #
    # Description: Checks to ensure that there are enough soldiers.
    #   If there are enough soldiers, return nothing.
    #   if there are not enough, return a build move to build one,
    #       if that is possible.
    #
    # Parameters:
    #   currentState - the state of the game at this point in time.
    #   listOfSoldiers - a list of all of the soldier ants owned by AI.
    #
    # Return: A build Soldier move, or None
    # #
    def checkSoldier(self, currentState, listOfSoldiers):
        if len(listOfSoldiers) < 1:
            # create new Soldier
            legalBuilds = listAllBuildMoves(currentState)
            if len(legalBuilds) != 0:
                for build in legalBuilds:
                    if build.buildType == SOLDIER:
                        return build

    # #
    # getOpponentId
    #
    # Description: Helper method to get the opponent's Id
    #
    # Parameters:
    #   None
    #
    # Return: Which player the opponent is.
    # #
    def getOpponentId(self):
        opponentId = PLAYER_ONE
        if self.playerId is PLAYER_ONE:
            opponentId = PLAYER_TWO
        return opponentId

    # #
    # queenRunAway
    #
    # Description: This is a helper method to help keep the queen
    #   away from other attacking ants if the queen comes under attack
    #
    # Parameters:
    #   currentState - the state of the game at this point in time.
    #   legalMoves - a list of legal moves for the queen Ant.
    #   queen - the queen ant that is being moved
    #   enemy - the enemy ant that is attacking the queen.
    #   foodList - a list of food COORDINATES that indicate where the food is.
    #   buildingList - a list of buildings, ** Assumed that it is the anthill.
    #
    # Return: A move for the queen to take to hopefully get away from the enemy.
    # #
    def queenRunAway(self, currentState, legalMoves, queen, enemy, foodList, buildingList):
        maxDistAway = 0 # arbitrary low number.
        bestMove = None
        for move in legalMoves:
            lastCoord = move.coordList[len(move.coordList)-1]
            if lastCoord != queen.coords and lastCoord != buildingList[0].coords:
                onFood = False
                for food in foodList:
                    if lastCoord == food:
                        onFood = True
                        break
                if onFood:
                    continue
                # not on anything we don't valid move.
                if isPathOkForQueen(move.coordList):
                    return move


