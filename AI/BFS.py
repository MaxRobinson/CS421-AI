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
from math import *

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
            # we win
            if tempScore == 1:
                return move
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
            #self.pickUpFood(gameState, ourInventory)
            #self.dropOffFood(gameState, ourInventory)
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
        # we know we have an enemy ant
        range = UNIT_STATS[attackingAnt.type][RANGE]
        diffX = abs(attackingAnt.coords[0] - attackCoord[0])
        diffY = abs(attackingAnt.coords[1] - attackCoord[1])

        # pythagoras would be proud
        if range ** 2 >= diffX ** 2 + diffY ** 2:
            #return True if within range
            return True
        else:
            return False

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

    def pickUpFood(self, gameState, ourInventory):
        # check if food there
        for ant in ourInventory.ants:
            if getConstrAt(gameState, ant.coords) is not None:
                if getConstrAt(gameState, ant.coords).type == FOOD and (not ant.carrying):
                    ant.carrying = True

    def dropOffFood(self, gameState, ourInventory):
        # check if landded on tunnel or anthill
        for ant in ourInventory.ants:
            if getConstrAt(gameState, ant.coords) is not None:
                if getConstrAt(gameState, ant.coords).type == TUNNEL or \
                        getConstrAt(gameState, ant.coords).type == ANTHILL\
                        and ant.carrying:
                    ant.carrying = False
                    ourInventory.foodCount += 1

    def evaluateState(self, gameState):
        opponentId = self.getOpponentId()
        enemyInv = gameState.inventories[opponentId]
        ourInv = gameState.inventories[self.playerId]
        if self.checkIfWon(ourInv, enemyInv):
            return 1.0
        elif self.checkIfLose(ourInv, enemyInv):
            return 0.0

        sumScore = 0
        sumScore += self.evalNumAnts(ourInv, enemyInv)
        sumScore += self.evalType(ourInv)
        sumScore += self.evalAntsHealth(ourInv, enemyInv)
        sumScore += self.evalFood(ourInv, enemyInv)
        sumScore += self.evalQueenThreat(gameState, ourInv, enemyInv)
        sumScore += self.evalWorkerCarrying(gameState, ourInv)
        sumScore += self.evalWorkerNotCarrying(gameState, ourInv)
        sumScore += self.evalQueenPosition(ourInv)

        score = sumScore/8  # divide by number of catagories to
        # score = sumScore
        # print "eval Worker Not Carying Score ", self.evalWorkerNotCarrying(gameState, ourInv)
        # print "eval Worker Carrying Score ", self.evalWorkerCarrying(gameState, ourInv)
        return score

    def checkIfWon(self, ourInv, enemyInv):
        if enemyInv.getQueen() is None or ourInv.foodCount == 11:
            return True
        return False

    #if queen near other ant attack
    def checkIfLose(self, ourInv, enemyInv):
        # bit more complicated....
        if ourInv.getQueen() is None:
            return True
        return False

    def evalNumAnts(self, ourInv, enemyInv):
        ourNum = len(ourInv.ants)
        enNum = len(enemyInv.ants)

        # score= dif/10 + .5 (for abs(dif) < 5 else dif is +-5)
        return self.diff(ourNum, enNum, 5)

    def evalAntsHealth(self, ourInv, enemyInv):
        ourHealth=-1
        enHealth=-1
        for oAnt in ourInv.ants:
            ourHealth += oAnt.health
        for eAnt in enemyInv.ants:
            enHealth += eAnt.health

        # score= dif/10 + .5 (for abs(dif) < 5 else dif is +-5)
        return self.diff(ourHealth, enHealth, 5)

    def evalFood(self, ourInv, enemyInv):
        return self.diff(ourInv.foodCount, enemyInv.foodCount, 10)

    def evalWorkerNotCarrying(self, gameState, ourInv):
        # Find worker ants not carrying
        notCarryingWorkers = []
        for ant in ourInv.ants:
            if (not ant.carrying) and ant.type == WORKER:
                notCarryingWorkers.append(ant)
        print "not Carrying Worker length: ", len(notCarryingWorkers)

        antDistScore = 0
        for ant in notCarryingWorkers:
            minDist = 1000
            foodList = []
            for constr in gameState.inventories[2].constrs:
                if constr.type == FOOD:
                    foodList.append(constr)

            for food in foodList:
                dist = self.dist(gameState, ant, food.coords)
                if dist < minDist:
                    minDist = dist

            antDistScore += self.scoreDist(minDist, 14)

        if len(notCarryingWorkers) > 0:
            print "antDistScore: ", antDistScore
            score = antDistScore / float(len(notCarryingWorkers))
        else:
            return 0

        return score

    def evalQueenThreat(self, gameState, ourInv, enemyInv):
        droneList = []
        for ant in ourInv.ants:
            if ant.type == DRONE:
                droneList.append(ant)

        totalScore = 0
        for drone in droneList:
            dist = self.dist(gameState, drone, enemyInv.getQueen().coords)
            totalScore += self.scoreDist(dist, 14)

        score = 0
        if len(droneList) > 0:
            score = totalScore / float(len(droneList))

        return score

    def evalWorkerCarrying(self, gameState, ourInv):
        # Find worker ants not carrying
        CarryingWorkers = []
        for ant in ourInv.ants:
            if ant.carrying and ant.type == WORKER:
                CarryingWorkers.append(ant)

        antDistScore = 0
        for ant in CarryingWorkers:
            minDist = None
            tunnelDist = 10000
            for tunnel in ourInv.getTunnels():
                dist = self.dist(gameState, ant, tunnel.coords)
                if dist < tunnelDist:
                    tunnelDist = dist
            antHillDist = self.dist(gameState, ant, ourInv.getAnthill().coords)
            if tunnelDist < antHillDist:
                minDist = tunnelDist
            else:
                minDist = antHillDist
            antDistScore += self.scoreDist(minDist, 14)
        if len(CarryingWorkers) > 0:
            score = antDistScore / float(len(CarryingWorkers))
        else:
            return 0

        return score

    def evalType(self, ourInv):
        workerCount = 0
        droneCount = 0
        for ant in ourInv.ants:
            if ant.type == WORKER:
                workerCount += 1
            if ant.type == DRONE:
                droneCount += 1

        if workerCount <= 1:
            return 0

        if droneCount < workerCount * 2:
            return .2
        else:
            return .7

    def evalQueenPosition(self, ourInv):
        queen = ourInv.getQueen()
        for food in ourInv.constrs:
            if food.type == FOOD:
                if queen.coords == food.coords:
                    return 0
        return 1

    def diff(self, ours, theirs, bound):
        # score= dif/10 + .5 (for abs(dif) < 5 else dif is +-5)
        diff = ours - theirs
        if diff >= bound:
            diff = bound
        elif diff <= bound:
            diff = -bound

        #return score
        return diff/(bound*2) + 0.5

    def scoreDist(self, dist, bound):
        # score= dif/10 + .5 (for abs(dif) < 5 else dif is +-5)
        if dist == 0:
            return 1.0
        if dist == 1:
            return .8
        if dist > bound:
            dist = bound
        #return score
        print "antDistScore: ", (-dist + bound)/float(bound)
        return (-dist + bound)/float(bound)

    def dist(self, gameState, ant, dest):
        # return sqrt((dest[0] - ant.coords[0])**2 + (dest[1] - ant.coords[1])**2)
        return stepsToReach(gameState, ant.coords, dest)
