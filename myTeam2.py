# myTeam2.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def __init__ (self, depth='2'):
    self.depth = int(depth)


  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    agentIndex = self.getTeam(gameState)
    #no, it's no longer Pacman moves first
    result = []
    depth = 0
    
    allActions = gameState.getLegalActions(self.index)
    if 'Stop' in allActions:
      allActions.remove('Stop')
    #we need to add actions here, so do the first iteration here.
    for action in allActions:
      for eachAgent in agentIndex:
        successorState = gameState.generateSuccessor(eachAgent, action)
        eachResult = (self.value(successorState, eachAgent, depth), action)
        result.append(eachResult)
    ans = max(result, key = lambda x: x[0])
    return ans[1]

class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """
  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}
  def nextAgent(self, gameState, agentIndex, depth):
    numAgents = gameState.getNumAgents()
    #wraps around when the whole turn is over
    if agentIndex + 1 == numAgents:
      agentIndex = 0
      depth = self.nextDepth(depth)
    else:
      agentIndex = agentIndex + 1 #increment to the next person's turn
    return agentIndex, depth

  def nextDepth(self, depth):
    if depth < self.depth:
      depth = depth+1
    return depth
  def maxValue(self, gameState, agentIndex, depth):
    v = -93372036854775807
    legalActions = gameState.getLegalActions(agentIndex)
    for action in legalActions:
      succState = gameState.generateSuccessor(agentIndex, action)
      v = max(v, self.value(succState, agentIndex, depth))
    return v

  def minValue(self, gameState, agentIndex, depth):
    v = 93372036854775807
    legalActions = gameState.getLegalActions(agentIndex)
    for action in legalActions:
      succState = gameState.generateSuccessor(agentIndex, action)
      v = min(v, self.value(succState, agentIndex, depth))
    return v

  def value(self, gameState, agentIndex, depth):
    if depth == self.depth:
      return self.evaluationFunction(gameState)
    legalActions = gameState.getLegalActions(agentIndex)
    agentIndex, depth = self.nextAgent(gameState, agentIndex, depth)
    ourAgentsIndex = self.getTeam(gameState)
    if agentIndex in ourAgentsIndex: #assuming we move first
      return self.maxValue(gameState, agentIndex, depth)
    else:
      return self.minValue(gameState, agentIndex, depth)

  def evaluationFunction(self, currentGameState, agentIndex, action):
    from searchAgents import mazeDistance
    """
    The evaluation function takes in the current and proposed successor
    GameStates (pacman.py) and returns a number, where higher numbers are better.

    Remaining food (newFood) and Pacman position after moving (newPos).
    """
    successorGameState = currentGameState.generateSuccessor(agentIndex, action)
    newPos = successorGameState.getAgentPosition(agentIndex)
    newFood = self.getFood(successorGameState)
    newGhostStates = successorGameState.getGhostStates()
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
    "make sure it keeps eating all the food... and do not stop if the food is close"
    "get ALL the food"
    "get to the closest food and EAT it"
    """
    TODO:
    Now we have 2 agents! 
    food is the other section of food
    adjust the index to do this
    the minimax agent is complete, 
    """
    allFood = self.getFood(currentGameState).asList()
    #allFood = currentGameState.getFood().asList()
    foodDistance = []
    ans = self.getScore()
    for dot in allFood:
        distance = self.getMazeDistance(newPos, dot)
        item = (dot, distance)
        foodDistance.append(item)
    #check ALL ghosts
    numAgents = successorGameState.getNumAgents()
    allGhostPositions = []

    opponentIndex = self.getOpponents(successorGameState)
    for eachOppo in opponentIndex:
      ghostNewPos = successorGameState.getAgentPosition(eachOppo)
      if ghostNewPos is not None:
        allGhostPositions.append(ghostNewPos)
    for eachGhost in allGhostPositions:
      ghostDistance = self.getMazeDistance(newPos, eachGhost)
      if ghostDistance<4:
        ans = ans - (3-ghostDistance)*100000

    if len(foodDistance)>0:
      closestFood = min(foodDistance, key = lambda x: x[1])
      ans = ans - closestFood[1]
    if newPos in allFood:
      ans = ans + 10000
    return ans
  
  # def getFeatures(self, gameState, action):
  #   features = util.Counter()
  #   successor = self.getSuccessor(gameState, action)
  #   features['successorScore'] = self.getScore(successor)
  #   #agentState1 = gameState.getAgentState(1)
  #   #print agentState1: #Ghost: (x,y)=(28.0, 4.0), North
  #   defendingFood = self.getFoodYouAreDefending(successor)#returns a map of all your own food
  #   getScore = self.getScore(successor)
  #   print "getScore:"
  #   print getScore
  #   prevObs = self.getPreviousObservation()
  #   redIndex = gameState.getRedTeamIndices()
  #   print "redIndex:"
  #   print redIndex

  #   indices = successor.getRedTeamIndices()
  #   features['getRedTeamIndices'] = indices
  #   features['getAgentDistances'] = gameState.getAgentDistances()

  #   testAgentState = gameState.getAgentState(1) #Ghost: (x,y)=(30.0, 9.0), South...etc

  #   for i in gameState.getRedTeamIndices():
  #       if gameState.isOnRedTeam(i):
  #           pos = gameState.getAgentPosition(i)
  #           features["agent ",i," state"] = gameState.getAgentState(i)
  #   print "features"
  #   print features


  #   # Compute distance to the nearest food
  #   foodList = self.getFood(successor).asList()
  #   if len(foodList) > 0: # This should always be True,  but better safe than sorry
  #     myPos = successor.getAgentState(self.index).getPosition()
  #     minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
  #     features['distanceToFood'] = minDistance

  #   return features

  # def getWeights(self, gameState, action):
  #   return {'successorScore': 100, 'distanceToFood': -1}

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}

