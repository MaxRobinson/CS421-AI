__author__ = 'Max Robinson, Triton Pitassi, Jaimiey Sears, Joel Simard '
import random
import sys
from Ant import *
from Building import *
from Player import *
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
        super(AIPlayer,self).__init__(inputPlayerId, "Gen Algorithm")
        self.MAX_DEPTH = 2
        self.MIN_ALPHA = -1000
        self.MAX_BETA = 1000
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
    # initGenes()
    # Description:
    #   Initializes the genes of a population. Selecting random values to init the genes too.
    #
    # Parameters:
    #   None
    ##
    def initGenes(self):
        self.fitness = []
        for i in range(0, self.POPULATIONSIZE):
            gene = []
            for i in range(0, self.GENELENGTH):

                gene.append(random.randint(0, 10000))

            self.fitness.append(0)
            self.currentPopulation.append(gene)

    # #
    # resetFitness
    # Description: resets the fitness array to be all 0
    #
    # Parameters:
    #   none
    # #
    def resetFitness(self):
        for i in range(0, self.POPULATIONSIZE):
            self.fitness[i] = 0

    # #
    # mate()
    # Description: Given two parent genes, mate them such that they exchange parts of them
    #   across a pivot. Then apply a random chance to change one part of the gene.
    #
    # Parameters:
    #    parent1 - a gene in the current population
    #    parent2 - a gene in the current population different from parent 1
    # #
    def mate(self, parent1, parent2):
        pivot = random.randint(0, self.GENELENGTH)

        # two temps for parts of array after pivot
        temp1 = parent1[pivot:]
        temp2 = parent2[pivot:]
        child1 = parent1[0:pivot] + temp2
        child2 = parent2[0:pivot] + temp1

        # applies a random chance for mutation for each gene.
        # 1 in mutationRate
        randomChance = random.randint(0, self.MutationRate)
        if randomChance == 1:
            randomPosition = random.randint(0, self.GENELENGTH-1)
            child1[randomPosition] = random.randint(0, 1000)

        if randomChance == 2:
            randomPosition = random.randint(0, self.GENELENGTH-1)
            child2[randomPosition] = random.randint(0, 1000)

        return (child1, child2)

    # #
    # generateNextGen
    # Description: Generates a new generation of genes based on the fitness level of the previous genes
    #   the genes have a weighted chance of being picked to be mated based on fitness level
    #
    # Parameters:
    #    None
    # #
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

            # choose a different parent from parent 1
            while(parent2 == parent1):
                index2 = indiciesAsWeighted[random.randint(0, len(indiciesAsWeighted)-1)]
                parent2 = self.currentPopulation[index2]


            # mate the parents
            children = self.mate(parent1, parent2)

            newPopulation.append(children[0])
            newPopulation.append(children[1])

        self.currentPopulation = newPopulation

        return

    ##
    # registerWin(hasWon):
    # Description: Allows for population management after a win has occurred.
    #   After a win check if it's time to move onto the next gene.
    #   If so move on. If finished all of the population mate the
    #   genes to get the next population
    #
    # Parameter: hasWon
    ##
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

            # select the gene with the min values in the gene
            for i in range(0, numToPlace):
                listOfPlacements.append(currentGene.index(min(currentGene)))
                # set the value to max value so that it will not be selected again
                currentGene[currentGene.index(min(currentGene))] = sys.maxint

            # map the x and y coords from the gene based on index
            for place in listOfPlacements:
                x = place % 10
                y = int(place / 10)
                moves.append((x, y))

            self.playerAnthill = moves[0]

        #Phase 2
        else:
            numToPlace = 2
            currentGene = copy.deepcopy(self.currentPopulation[self.populationIndex])

            # select the gene with the max values in the gene
            for i in range(0, numToPlace):
                listOfPlacements.append(currentGene.index(max(currentGene)))
                # set the value to min value so that it will not be selected again
                currentGene[currentGene.index(max(currentGene))] = -sys.maxint

            # change index to x y coords.
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
    # Description: Chooses the next best move to make by first expanding all legal moves and then scoring
    #   each expanded state. It then decides which move to make based on the highest score.
    #   If multiple moves share the same score, a random move is picked from the list of moves that all
    #   received that score.
    #
    # Parameters:
    #    currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return: The Move to be made
    # #
    def getMove(self, currentState):
        if self.turnNumber == 0:
            asciiPrintState(currentState)
            self.turnNumber += 1

        gameState = currentState.fastclone()
        node = Node(None, gameState, None, None, self.MIN_ALPHA, self.MAX_BETA)

        bestNode = self.search(node, self.playerId, 0)
        return bestNode.move


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
    # Description: This method takes a game state, and a move, and applies the move
    #   to the game State to depict what the game state would look like after the move is made
    #
    # Parameters:
    #    currentState - A clone of the current state (GameState)
    #    move - a game move to be executed to expand the state
    # #
    def expandNode(self, currentState, move):
        gameState = currentState.fastclone()
        # ourInventory = gameState.inventories[self.playerId]
        ourId = gameState.whoseTurn
        ourInventory = gameState.inventories[gameState.whoseTurn]
        if(move.moveType == MOVE_ANT):
            antToMove = None
            for ant in ourInventory.ants:
                if ant.coords == move.coordList[0]:
                    antToMove = ant
            if antToMove is not None:
                antToMove.coords = move.coordList[-1]
                antToMove.hasMoved = True

                # check if other ants near by for attack
                opponentId = self.getOpponentId(gameState.whoseTurn)
                enemyInv = gameState.inventories[opponentId]
                ## Checks if can attack.
                self.attackSequence(enemyInv, antToMove)

        elif(move.moveType == BUILD):
            # just worried about building Ants and Tunnel
            if(move.buildType == WORKER):
                # add ant
                ourInventory.ants.append(Ant(move.coordList[-1], WORKER, ourId))
                # subtract food
                ourInventory.foodCount -= 1
            elif(move.buildType == DRONE):
                ourInventory.ants.append(Ant(move.coordList[-1], DRONE, ourId))
                ourInventory.foodCount -= 1
            elif(move.buildType == SOLDIER):
                ourInventory.ants.append(Ant(move.coordList[-1], SOLDIER, ourId))
                ourInventory.foodCount -= 2
            elif(move.buildType == R_SOLDIER):
                ourInventory.ants.append(Ant(move.coordList[-1], R_SOLDIER, ourId))
                ourInventory.foodCount -= 2
            elif(move.buildType == TUNNEL):
                ourInventory.constrs.append(Building(move.coordList[-1], TUNNEL, ourId))
                ourInventory.foodCount -= 3
        else:
            self.pickUpFood(gameState, ourInventory)
            self.dropOffFood(gameState, ourInventory)
            return gameState

        return gameState

    # #
    # getOpponentId
    # Description: Helper method to get the opponent's ID
    #
    # Parameters:
    #    None
    #
    # Return: The opponent's ID
    # #
    def getOpponentId(self, id):
        opponentId = -1
        if id == 0:
            opponentId = 1
        else:
            opponentId = 0
        return opponentId


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
    # evaluateState
    #
    # Description: Evaluates how "good" a state is based on whose turn it is and
    #   what is on the board
    #   Credit: Kai Jorgensen
    #
    # Parameters:
    #   state - The GameState to evaluate
    #
    # Return: A float between 0.0 (loss) and 1.0 (victory)
    ##
    def evaluateState(self, state):
        # local constants for adjusting weights of evaluation
        QUEEN_EDGE_MAP_WEIGHT = 0.01
        BUILD_WORKER_WEIGHT = 0.1
        MOVE_TOWARDS_QUEEN_WEIGHT = 0.005
        QUEEN_HEALTH_WEIGHT = 0.025

        # get some references for use later
        playerInv = state.inventories[state.whoseTurn]
        enemyInv = state.inventories[1 - state.whoseTurn]
        enemyQueen = enemyInv.getQueen()

        # check for defeat (dead queen or enemy food victory)
        if playerInv.getQueen() is None or enemyInv.foodCount >= 11:
            return 0.0
        # check for victory (dead enemy queen or food victory)
        if enemyQueen is None or playerInv.foodCount >= 11:
            return 1.0

        # start the score at a semi-neutral value
        score = 0.4

        # check each of the player's ants
        for ant in playerInv.ants:
            if ant.type == QUEEN:
                # keep the queen off of the anthill
                if ant.coords == self.playerAnthill:
                    return 0.01
                # keep the queen at the edge of the map
                score -= QUEEN_EDGE_MAP_WEIGHT * ant.coords[1]
            elif ant.type == WORKER:
                # encourage building more workers
                score += BUILD_WORKER_WEIGHT
                # move workers towards queen
                score -= MOVE_TOWARDS_QUEEN_WEIGHT * (abs(ant.coords[0] - enemyQueen.coords[0]) +
                                                      abs(ant.coords[1] - enemyQueen.coords[1]))

        # encourage damaging the enemy queen
        score += QUEEN_HEALTH_WEIGHT * (UNIT_STATS[QUEEN][HEALTH] - enemyQueen.health)

        # return the evaluation score of the state
        return score

    # #
    # CheckIfWon
    # Description: Checks if the gamestate is a win condition
    #
    # Parameters:
    #   ourInv - the AI's inventory
    #   enemyInv - the opponent's Inventory
    #
    # Return: Boolean: True if win condition, False if not.
    # #
    def checkIfWon(self, ourInv, enemyInv):
        if enemyInv.getQueen() is None or ourInv.foodCount == 11:
            return True
        return False

    # #
    # CheckIfLose
    # Description: Checks if the game state is a lose condition
    #
    # Parameters:
    #   ourInv - the AI's inventory
    #   enemyInv - the opponent's Inventory
    #
    # Return: Boolean: True if win condition, False if not.
    # #
    def checkIfLose(self, ourInv, enemyInv):
        # bit more complicated....
        if ourInv.getQueen() is None:
            return True
        return False
    # #
    # evalNumAnts
    # Description: Evaluates the number of ants we have based on the number of ants the opponent has
    #
    # Parameters:
    #   ourInv - the AI's inventory
    #   enemyInv - the opponent's Inventory
    #
    # Return: Score - score based on the difference between the number of ants we have and our opponent has
    # #
    def evalNumAnts(self, ourInv, enemyInv):
        ourNum = len(ourInv.ants)
        enNum = len(enemyInv.ants)

        # score= dif/10 + .5 (for abs(dif) < 5 else dif is +-5)
        return self.diff(ourNum, enNum, 5)

    # #
    # evalAntsHealth
    # Description: evals ants Health. checks the collective difference between our ants health verses our opponents
    #
    # Parameters:
    #   ourInv - the AI's inventory
    #   enemyInv - the opponent's Inventory
    #
    # Return: Score - based on difference of overall ant health between AI's ants and Enemies Ant's
    # #
    def evalAntsHealth(self, ourInv, enemyInv):
        ourHealth=-1
        enHealth=-1
        for oAnt in ourInv.ants:
            ourHealth += oAnt.health
        for eAnt in enemyInv.ants:
            enHealth += eAnt.health

        # score= dif/10 + .5 (for abs(dif) < 5 else dif is +-5)
        return self.diff(ourHealth, enHealth, 5)

    # #
    # evalFood
    # Description: Evals the differnece in food based on diff between our Ai's food and Enemies Food
    #
    # Parameters:
    #   ourInv - the AI's inventory
    #   enemyInv - the opponent's Inventory
    #
    # Return: Score - based on difference of food between AI and Enemy's
    # #
    def evalFood(self, ourInv, enemyInv):
        return self.diff(ourInv.foodCount, enemyInv.foodCount, 10)

    # #
    # evalQueenThreat
    # Description: Evals the threat our AI's ants are posing to the enemy queen. Based on distance from queen.
    #   Uses mostly drones and drone distance.
    #
    # Parameters:
    #   gameState - the state of the game.
    #   ourInv - the AI's inventory
    #   enemyInv - the opponent's inventory
    #
    # Return: Score - based on difference of overall drone distance of a drone to the enemy queen.
    # #
    def evalQueenThreat(self, gameState, ourInv, enemyInv):
        droneList = []
        for ant in ourInv.ants:
            if ant.type == DRONE or ant.type == SOLDIER or ant.type == R_SOLDIER:
                droneList.append(ant)

        totalScore = 0
        for drone in droneList:
            dist = self.dist(gameState, drone, enemyInv.getQueen().coords)
            totalScore += self.scoreDist(dist, 14)

        score = 0
        if len(droneList) > 0:
            score = totalScore / float(len(droneList))

        return score

    # #
    # evalWorkerNotCarrying
    # Description: Evals the placement of worker ants not carrying food. Based on distance from food a worker.
    #   The closer to the food the better the score. Does this for all ants, and does a collective score, and then
    #   normalizes the score.
    #
    # Parameters:
    #   gameState - the state of the game.
    #   ourInv - the AI's inventory
    #
    # Return: Score - distance of all available workers from food.
    # #
    def evalWorkerNotCarrying(self, gameState, ourInv):
        # Find worker ants not carrying
        notCarryingWorkers = []
        for ant in ourInv.ants:
            if (not ant.carrying) and ant.type == WORKER:
                notCarryingWorkers.append(ant)

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
            score = antDistScore / float(len(notCarryingWorkers))
        else:
            return 0

        return score

    # #
    # evalWorkerCarrying
    # Description: Evals the placement of worker ants carrying food. Based on distance from anthill or tunnel.
    #   The closer to the building the better the score. Does this for all ants, and does a collective score, and then
    #   normalizes the score.
    #
    # Parameters:
    #   gameState - the state of the game.
    #   ourInv - the AI's inventory
    #
    # Return: Score - based on all carrying ants from a building to drop food at.
    # #
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

    # #
    # evalType
    # Description: Evals the type of ants that we have and awards score based on the ration of worker ants to
    #   drone ants.
    #
    # Parameters:
    #   ourInv - the AI's inventory
    #
    # Return: Score - based on the ration of drone ants to worker ants.
    # #
    def evalType(self, ourInv):
        workerCount = 0
        droneCount = 0
        for ant in ourInv.ants:
            if ant.type == SOLDIER:
                return 0.0
            if ant.type == R_SOLDIER:
                return 0.0
            if ant.type == WORKER:
                workerCount += 1
            if ant.type == DRONE:
                droneCount += 1

        if workerCount <= 1:
            return 0.0
        elif workerCount >= 2:
            return 0.0

        # return droneCount in proportion to workers
        ratio = droneCount / float(workerCount * 2)
        if ratio > 2:
            ratio = 2
        score = (1/2)*ratio

        return score

    # #
    # evalQueenPosition
    # Description: Ensures that the queen does not sit or move onto the food and block our worker ants.
    #
    # Parameters:
    #   ourInv - the AI's inventory
    #
    # Return: Score - based on if the queen is on food or not.
    # #
    def evalQueenPosition(self, ourInv):
        queen = ourInv.getQueen()
        for constr in ourInv.constrs:
            if constr.type in [ANTHILL, TUNNEL, FOOD]:
                if queen.coords == constr.coords:
                    return 0
        return 1

    # #
    # diff
    # Description: Helper method to calculate the difference between two values, given a bound to bound our equation
    #   and return a score, based on difference and bound
    #
    # Parameters:
    #   ours - AI's value
    #   theirs - opponent's value
    #   bound - an upper bound on the equation. Max difference.
    #
    # Return: Score - based on difference and the upper bound to provide a score between 0 and 1.
    # #
    def diff(self, ours, theirs, bound):
        # score= dif/10 + .5 (for abs(dif) < 5 else dif is +-5)
        diff = ours - theirs
        if diff >= bound:
            diff = bound
        elif diff <= bound:
            diff = -bound

        #return score
        return diff/(bound*2) + 0.5

    # #
    # scoreDist
    # Description: Helper method to provide a score for distance based scores. Given a distance and an upper bound,
    #   retur
    #
    # Parameters:
    #   dist - distance between two things
    #   bound - an upper bound on max possible distance.
    #
    # Return: Score - based on the distance and uses the bound to normalize the number to be between 0 and 1.
    # #
    def scoreDist(self, dist, bound):
        # score= dif/10 + .5 (for abs(dif) < 5 else dif is +-5)
        if dist == 0:
            return 1.0
        if dist > bound:
            dist = bound
        return (-dist + bound)/float(bound)

    # #
    # dist
    # Description: calculates the distance between an ant and coordinate
    #
    # Parameters:
    #   gameState - the state of the game.
    #   ant - the source ant
    #   dest - the destination COORDINATE
    #
    # Return: Score - based on difference of overall ant health between AI's ants and Enemies Ant's
    # #
    def dist(self, gameState, ant, dest):
        return sqrt((dest[0] - ant.coords[0])**2 + (dest[1] - ant.coords[1])**2)
        # return stepsToReach(gameState, ant.coords, dest)

##################### HW #3 ##########################

    # #
    # setStateToMoveDeeper
    # Description: sets the state to allow for more traversal.
    #
    # Parameters:
    #   gameState - the state of the game.
    #   playerId - player ID
    #
    #
    # Return: MaxEval - the best evaluation rating for a node in the list.
    # #
    def setStateToMoveDeeper(self, gameState, playerId):
        # antList = gameState.inventories[playerId].ants
        # for ant in antList:
        #     ant.hasMoved = False
        gameState.whoseTurn = playerId

    # #
    # search
    # Description: searches to a depth of MAX_DEPTH to determine the best branch to go down.
    #   Uses Alpha Beta Pruning to help speed up the game.
    #
    # Parameters:
    #   CurrentNode - current NOde
    #   playerId - players ID
    #   currentDepth - current Depth
    #
    # Return: A node
    #       - breaks if Max_depth is 0
    # #
    def search(self, currentNode, playerId, currentDepth):
        moveList = listAllLegalMoves(currentNode.state)
        nodeList = []

        nodeDict = {}
        for move in moveList:
            # expand node
            gameState = self.expandNode(currentNode.state, move)
            eval = self.evaluateState(gameState)
            node = Node(move, gameState, currentNode.state, eval, currentNode.alpha, currentNode.beta)

            if move.moveType == END:
                self.setStateToMoveDeeper(gameState, self.getOpponentId(playerId))
            nodeList.append(node)

            # #if we can win, don't look further
            # if node.eval == 1.0:
            #     return node

            if eval not in nodeDict:
                nodeDict[eval] = list()
            nodeDict[eval].append(node)

        # BASE CASE: if MAX_DEPTH - Skip recursion, and find best node of those evaluated
        # if not max dept recurs
        if currentDepth != self.MAX_DEPTH:
            # recurse here
            maxKey = max(nodeDict.keys())
            shortenedList = []
            if len(nodeDict[maxKey]) > 5:
                shortenedList = nodeDict[maxKey][:6]
            else:
                shortenedList = nodeDict[maxKey]

            for node in shortenedList:

                whoseTurn = None

                if node.move == END:
                    whoseTurn = self.getOpponentId(node.state.whoseTurn)
                else:
                    whoseTurn = node.state.whoseTurn

                # Our turn
                if whoseTurn == self.playerId:
                    # do max
                    eval = self.search(node, node.state.whoseTurn, currentDepth+1).eval
                    if eval is None:
                        continue

                    if eval > node.beta:
                        # prune
                        node.eval = None
                        return currentNode
                    if eval > node.alpha:
                        node.alpha = eval

                # not our turn do min
                else:
                    eval = self.search(node, node.state.whoseTurn, currentDepth+1).eval
                    if eval is None:
                        continue

                    if eval < node.alpha:
                        # prune
                        node.eval = None
                        return currentNode
                    if eval < node.beta:
                        node.beta = eval
            return self.findBestNode(shortenedList)

        # BASE CASE
        # return best node of nodes that haven't been recursively expanded
        return self.findBestNode(nodeList)

    # #
    # findBestNode
    # Description: returns the best node, in a list of nodes.
    #   Determines the best node to pick based on whose turn it is. (max or min)
    #
    # Parameters:
    #   listOfNodes - a list of Node objects.
    #
    # Return: A NODE!!!!!!
    # #
    def findBestNode(self, nodeList):
        if len(nodeList) < 1:
            return None

        bestNode = nodeList[0]

        # If it's an end turn move, do the opposite of the player who it says turn it is.
        whoseTurn = -1
        if nodeList[0].move.moveType == END:
            whoseTurn = self.getOpponentId(nodeList[0].state.whoseTurn)
        else:
            whoseTurn = nodeList[0].state.whoseTurn


        # rather than just check first node find player id for nodes in node list
        if(whoseTurn == self.playerId):
            #find max's
            for node in nodeList:
                if node.eval is None:
                    continue
                if node.eval > bestNode.eval:
                    bestNode = node
        else:
            #find min's
            for node in nodeList:
                if node.eval is None:
                    continue
                if node.eval < bestNode.eval:
                    bestNode = node

        return bestNode


# #
# Node
# Description: Class that contains a state move, parent, eval, and alpha and beta values.
#   Used for searching possible paths for the AI to go down.
#
# #
class Node:
    def __init__(self, move, state, parent,  eval, alpha, beta):
        self.alpha = alpha
        self.beta = beta
        self.move = move
        self.state = state
        self.parent = parent
        self.eval = eval



## Unit Tests
from GameState import *
from Location import *
from Inventory import *
from Construction import *

# #
# putFood
# Description: places the Food for our set up for our gameState for the Unit Test
#
# Parameters:
#   neutralInventory - the inventory where grass and food is placed
#
# Return: Nothing
# #
def putFood(neutralInventory):
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
def putOurInventory(inventory):
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
def putTheirInventory(inventory):
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
def equalStates(state1, state2):
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






# #
# Unit Test
# Description: Test's that given a game state, that it expands accordingly, and evaluates that state correctly.
# #
board = [[Location((col, row)) for row in xrange(0, BOARD_LENGTH)] for col in xrange(0, BOARD_LENGTH)]
p1Inventory = Inventory(PLAYER_ONE, [], [], 0)
p2Inventory = Inventory(PLAYER_TWO, [], [], 0)
neutralInventory = Inventory(NEUTRAL, [], [], 0)

putFood(neutralInventory)
putOurInventory(p1Inventory)
putTheirInventory(p2Inventory)

state = GameState(board, [p1Inventory, p2Inventory, neutralInventory], PLAY_PHASE, PLAYER_ONE)
expectedState = state.fastclone()
expectedState.inventories[PLAYER_TWO].ants = []


ourAI = AIPlayer(PLAYER_ONE)

move = Move(MOVE_ANT,[(0,6)], None)
retrievedState = ourAI.expandNode(state, move)

if equalStates(retrievedState, expectedState):
    score = ourAI.evaluateState(retrievedState)
    if score == 1.0:
        print "Unit Test #1 Passed"
    else:
        print "UNIT TEST #1 FAILED"
else:
    print "UNIT TEST #1 FAILED: STATES NOT THE SAME."



######################## Unit tests for Genes #############

def testGeneCreation():
    AI = AIPlayer(PLAYER_ONE)
    # AI.initGenes()
    THINGYTHING = AI.currentPopulation
    if len(THINGYTHING) != AI.POPULATIONSIZE:
        print "POPULATION FAILED", len(THINGYTHING)
        return
    if len(THINGYTHING[0]) != AI.GENELENGTH:
        print "GENE LENGTH NOT RIGHT"
        return

    if len(AI.fitness) != AI.POPULATIONSIZE:
        print "FITNESS NOT RIGHT"
        return

    for item in AI.fitness:
        if item != 0:
            print "FITNESS NOT SET TO 0"
            return

    else:
        print "Population: ", THINGYTHING



def testMate(parent1, parent2):
    AI = AIPlayer(PLAYER_ONE)
    children = AI.mate(parent1, parent2)

    if len(children[0]) != AI.GENELENGTH:
        print "CHILD 1 IS NOT LONG ENOUGH"
        return

    if len(children[1]) != AI.GENELENGTH:
        print "CHILD 2 IS NOT LONG ENOUGH"
        return

    print "parent 1: ", parent1
    print "Parent 2: ", parent2
    print "Child 1: ", children[0]
    print "Child 2: ", children[1]


def testBoardPlacement():
    AI = AIPlayer(PLAYER_ONE)

    AI.initGenes()

    board = [[Location((col, row)) for row in xrange(0, BOARD_LENGTH)] for col in xrange(0, BOARD_LENGTH)]
    p1Inventory = Inventory(PLAYER_ONE, [], [], 0)
    p2Inventory = Inventory(PLAYER_TWO, [], [], 0)
    neutralInventory = Inventory(NEUTRAL, [], [], 0)

    state = GameState(board, [p1Inventory, p2Inventory, neutralInventory], SETUP_PHASE_1, PLAYER_ONE)

    moves = AI.getPlacement(state)

    print moves

    if len(moves) != 11:
        print "LIST OF POSITIONS NOT RIGHT PHASE 1"
        return

    state = GameState(board, [p1Inventory, p2Inventory, neutralInventory], SETUP_PHASE_2, PLAYER_ONE)

    moves = AI.getPlacement(state)
    print "Food Placement ", moves
    if len(moves) != 2:
        print "List of moves NOT RIGHT PHASE 2"
        return

def testGenerateNextGen():
    AI = AIPlayer(PLAYER_ONE)

    AI.initGenes()
    AI.fitness = [20,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,19]

    print "CURR POP: ", AI.currentPopulation

    AI.generateNextGen()

    print "Next Gen: ", AI.currentPopulation

    if len(AI.currentPopulation) != AI.POPULATIONSIZE:
        print "NEXT POPULATION LENGTH NOT RIGHT"
        return



testGeneCreation()
testBoardPlacement()
testGenerateNextGen()

parent1 = []
for i in range(0, 40):
    parent1.append(random.randint(0, 10000))

parent2 = []
for i in range(0, 40):
    parent2.append(random.randint(0, 10000))

testMate(parent1, parent2)













