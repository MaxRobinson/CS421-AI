__author__ = 'Max'

from Player import *


import random
import sys
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *
import copy

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
        super(AIPlayer,self).__init__(inputPlayerId, "HeuristicAndGen")
        self.numTurns = 0
        self.currentPopulation = []
        self.populationIndex = 0
        self.fitness = []
        self.POPULATIONSIZE = 10
        self.GENELENGTH = 40
        self.MutationRate = 5

        self.initGenes()

        self.MAXNUMGAMESPERGENE = 10
        self.numGamesForGene = 0

        self.turnNumber = 0

    ##
    #
    ##
    def initGenes(self):
        self.fitness = []
        for i in range(0, self.POPULATIONSIZE):
            gene = []
            for i in range(0, self.GENELENGTH):

                gene.append(random.randint(0, 10000))

            self.fitness.append(0)
            self.currentPopulation.append(gene)

    def resetFitness(self):
        for i in range(0, self.POPULATIONSIZE):
            self.fitness[i] = 0


    def mate(self, parent1, parent2):
        pivot = random.randint(0, self.GENELENGTH)

        temp1 = parent1[pivot:]
        temp2 = parent2[pivot:]
        child1 = parent1[0:pivot] + temp2
        child2 = parent2[0:pivot] + temp1

        randomChance = random.randint(0, self.MutationRate)
        if randomChance == 1:
            randomPosition = random.randint(0, self.GENELENGTH-1)
            child1[randomPosition] = random.randint(0, 1000)

        if randomChance == 2:
            randomPosition = random.randint(0, self.GENELENGTH-1)
            child2[randomPosition] = random.randint(0, 1000)

        return (child1, child2)

    def generateNextGen(self):

        newPopulation = []

        # create weight array
        indiciesAsWeighted = []
        for i in range(0, len(self.fitness)):
            fitness = self.fitness[i]
            for j in range(0, fitness):
                indiciesAsWeighted.append(i)

        # choose which parents will mate
        for i in range(0, self.POPULATIONSIZE/2):

            # pick parent genes randomly based on weight
            index1 = indiciesAsWeighted[random.randint(0, len(indiciesAsWeighted)-1)] #index into population to mate
            parent1 = self.currentPopulation[index1]

            parent2 = parent1
            index2 = index1
            while(parent2 == parent1):
                index2 = indiciesAsWeighted[random.randint(0, len(indiciesAsWeighted)-1)]
                parent2 = self.currentPopulation[index2]


            print "Mating: ", index1, " ", index2
            children = self.mate(parent1, parent2)

            newPopulation.append(children[0])
            newPopulation.append(children[1])

        self.currentPopulation = newPopulation

            # # get the indexes of the parents to mate.
            # firstParentIndex = self.fitness.index(max(self.fitness))
            # self.fitness[firstParentIndex] = -sys.maxint
            # secondParentIndex = self.fitness.index(max(self.fitness))
            # self.fitness[secondParentIndex] = -sys.maxint
            #
            # # get parent genes
            # parent1 = self.currentPopulation[firstParentIndex]
            # parent2 = self.currentPopulation[secondParentIndex]
            #
            # # mate
            # children = self.mate(parent1, parent2)
            #
            # # replace parents
            # self.currentPopulation[firstParentIndex] = children[0]
            # self.currentPopulation[secondParentIndex] = children[1]

        return

    def registerWin(self, hasWon):
        self.numGamesForGene += 1
        self.turnNumber = 0
        if(hasWon):
            self.fitness[self.populationIndex] += 1

        # check if a gene has not been finished evaluating
        if self.numGamesForGene != self.MAXNUMGAMESPERGENE:
            return

        # if number of games for this gene is met for fitness level move to the next one.
        else:
            self.populationIndex += 1
            self.numGamesForGene = 0
            # if index is equal to size of population then time to mate
            if self.populationIndex == self.POPULATIONSIZE:
                self.generateNextGen()
                self.resetFitness()
                self.populationIndex = 0



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
        listOfPlacements = []
        moves = []
        if currentState.phase == SETUP_PHASE_1:    # stuff on my side
            numToPlace = 11
            currentGene = copy.deepcopy(self.currentPopulation[self.populationIndex])

            for i in range(0, numToPlace):
                listOfPlacements.append(currentGene.index(min(currentGene)))
                currentGene[currentGene.index(min(currentGene))] = sys.maxint


            for place in listOfPlacements:
                x = place % 10
                y = int(place / 10)
                moves.append((x, y))

        #Phase 2
        else:
            numToPlace = 2
            currentGene = copy.deepcopy(self.currentPopulation[self.populationIndex])

            for i in range(0, numToPlace):
                listOfPlacements.append(currentGene.index(max(currentGene)))
                currentGene[currentGene.index(max(currentGene))] = -sys.maxint


            for place in listOfPlacements:
                x = place % 10
                y = int(place / 10) + 6 # accounts for offset into enemy territory

                # if collision wrap until no collision
                while currentState.board[x][y].constr is not None or (x, y) in moves:
                    if x < 9:
                        x = x+1
                    else:
                        if y < 9:
                            y = y +1
                        else:
                            y = 6
                        x = 0

                moves.append((x, y))

        return moves

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
        if self.numTurns == 0:
            asciiPrintState(currentState)
            self.numTurns += 1
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
            elif ant.type == QUEEN:
                queenMove = self.moveQueen(currentState, ant, queenMoves, foodCoordList, buildingList)
                if queenMove is not None:
                    return queenMove
            elif ant.type == SOLDIER:
                soldierMove = self.moveSoldier(currentState, ant, soldierMoves, self.getOpponentId())
                return soldierMove

        # going to be an end move and Change turns
        self.numTurns += 1
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



