# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util
import datetime
from math import log, sqrt
import copy

from game import Agent

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


# add this class to multiAgents.py
# the following class corrects and replaces the previous MonteCarloAgent class released on March 19
# the only differences between this version, and the one released on March 19 are:
#       * line 37 of this file, "if self.Q" has been replaced by "if Q"
#       * line 45 of this file, where "assert( Q == 'contestClassic' )" has been added
class MonteCarloAgent(MultiAgentSearchAgent):
    """
        Your monte-carlo agent (question 5)
        ***UCT = MCTS + UBC1***
        TODO:
        1) Complete getAction to return the best action based on UCT.
        2) Complete runSimulation to simulate moves using UCT.
        3) Complete final, which updates the value of each of the states visited during a play of the game.

        * If you want to add more functions to further modularize your implementation, feel free to.
        * Make sure that your dictionaries are implemented in the following way:
            -> Keys are game states.
            -> Value are integers. When performing division (i.e. wins/plays) don't forget to convert to float.
      """

    def __init__(self, evalFn='mctsEvalFunction', depth='-1', timeout='400', numTraining=100, C='2', Q=None):
        # This is where you set C, the depth, and the evaluation function for the section "Enhancements for MCTS agent".
        if Q:
            if Q == 'minimaxClassic':
                pass
            elif Q == 'testClassic':
                pass
            elif Q == 'smallClassic':
                pass
            else: # Q == 'contestClassic'
                assert( Q == 'contestClassic' )
                pass
        # Otherwise, your agent will default to these values.
        else:
            self.C = int(C)
            # If using depth-limited UCT, need to set a heuristic evaluation function.
            if int(depth) > 0:
                evalFn = 'scoreEvaluationFunction'
        self.states = []
        self.plays = dict()
        self.wins = dict()
        self.calculation_time = datetime.timedelta(milliseconds=int(timeout))
        #self.C = kwargs.get('C', 1.4)

        #initialize with opening gameState?

        self.numTraining = numTraining

        MultiAgentSearchAgent.__init__(self, evalFn, depth)

    def update(self, state):
        """
        You do not need to modify this function. This function is called every time an agent makes a move.
        """
        self.states.append(state)

    def getAction(self, gameState):

        max_depth = 0

        actions = gameState.getLegalActions(0)
        if (len(actions) == 0):
          return
        if (len(actions) == 1):
          return actions[0]

        legal_moves = [(action, gameState.generateSuccessor(0, action)) for action in actions]

        games = 0
        begin = datetime.datetime.utcnow()
        while (datetime.datetime.utcnow() - begin < self.calculation_time):
            self.run_simulation(gameState)
            games += 1
        

        # Pick the move with the highest percentage of wins.
        percent_wins, move = max(
            (100*self.wins.get((S,0), 0) /
             self.plays.get((S,0), 1),
             p)
            for p, S in legal_moves
        )

        #Display the stats for each possible play.
        for x in sorted(
           ((100 * self.wins.get((S,0), 0) /
             self.plays.get((S, 0), 1),
             self.wins.get((S, 0), 0),
             self.plays.get((S, 0), 0), p)
            for p, S in legal_moves),
           reverse=True
        ):
           print "{3}: {0:.2f}% ({1} / {2})".format(*x)

        #print "Move selected is {}".format(move)

        #a = raw_input('!')

        #print "Maximum depth searched:", max_depth

    
        return move

    def run_simulation2(self, state):
        """
        Simulates moves based on MCTS.
        1) (Selection) While not at a leaf node, traverse tree using UCB1.
        2) (Expansion) When reach a leaf node, expand.
        4) (Simulation) Select random moves until terminal state is reached.
        3) (Backpropapgation) Update all nodes visited in search tree with appropriate values.
        * Remember to limit the depth of the search only in the expansion phase!
        Updates values of appropriate states in search with with evaluation function.
        """
        plays, wins = self.plays, self.wins
        
        player = 0        
        
        visitedStates = []
        
        expand = True
        
        visitedStates.append((state, player))
        
        maxMoves = self.depth * state.getNumAgents()

        winflag = False;
        loseflag = False;
        
        for t in xrange(1, maxMoves + 1):
            actions = state.getLegalActions(player)
            movesStates = [(action, state.generateSuccessor(player, action)) for action in actions]
            
            if all(plays.get((gameState, player)) for action, gameState in movesStates):
                log_total = log(sum(plays[(gameState, player)] for action, gameState in movesStates))
                value, move, state = max(
                    ((float(wins[(gameState, player)]) / float(plays[(gameState, player)])) +
                     self.C * sqrt(float(log_total) / float(plays[(gameState, player)])), player, gameState)
                     for action, gameState in movesStates
                )
            else:
                move, state = random.choice(movesStates)
            
            if expand and (state, player) not in plays:
                expand = False
                plays[(state, player)] = 0
                wins[(state, player)] = 0
            
            visitedStates.append((state, player))
            
            if state.isWin() and player == 0:
                winflag = True
                break
            if state.isLose() and player > 0:
                loseflag = True
                break
        
            if player < (state.getNumAgents() - 1):
                player += 1
            else:
                player = 0            
            
        for state, player in visitedStates:
            if (state, player) not in plays:
                continue
            self.plays[(state, player)] += 1
            
            if winflag:
                print("win for pacman {}".format(self.evaluationFunction(state)))
                self.wins[(state, player)] += self.evaluationFunction(state)
            if loseflag:
                print("win for ghost")
                self.wins[(state, player)] += (1 - self.evaluationFunction(state))
            #else:
                #wins[(state, player)] += self.evaluationFunction(state)
            
        

    def run_simulation(self, state):

        """
        Simulates moves based on MCTS.
        1) (Selection) While not at a leaf node, traverse tree using UCB1.
        2) (Expansion) When reach a leaf node, expand.
        4) (Simulation) Select random moves until terminal state is reached.
        3) (Backpropapgation) Update all nodes visited in search tree with appropriate values.
        * Remember to limit the depth of the search only in the expansion phase!
        Updates values of appropriate states in search with with evaluation function.
        """
        # Plays out a "random" game from the current position,
        # then updates the statistics tables with the result.

        # A bit of an optimization here, so we have a local
        # variable lookup instead of an attribute access each loop.
        #self.states.append(state)
        #states_copy = self.states[:]
        visited_states = set()
        
        #state = states_copy[-1]
        player = 0
        expand = True
        max_moves = 4*(state.getNumAgents());
        winflag = False
        loseflag = False
        plays, wins = self.plays, self.wins
        #visited_states.add((state, player))
 
        for t in xrange(1,max_moves + 1):

          actions = state.getLegalActions(player)
          legal_moves = [(action, state.generateSuccessor(player, action)) for action in actions]

          if all(plays.get((S, player)) for p, S in legal_moves):
            # If we have stats on all of the legal moves here, use them.
            log_total = log(
                sum(plays[(S, player)] for p, S in legal_moves))
            
            value, move, state = max(
                ((wins[(S, player)] / plays[(S, player)]) +
                 self.C * sqrt(log_total / plays[(S, player)]), p, S)
                for p, S in legal_moves
            )
          else: 
            #generate random action, if possible
            action = random.choice(state.getLegalActions(player))      
            state = state.generateSuccessor(player, action)

          #states_copy.append(state)

          if expand and (state, player) not in self.plays:
            expand = False
            self.plays[(state, player)] = 0
            self.wins[(state, player)] = 0

          visited_states.add((state, player))

          if state.isWin() or state.isLose(): 
            if (state.isWin()): 
              winflag = True
              #print("Win")
            else:
              loseflag = True 
              #print("Loss")
            break

          #update player
          if (player < (state.getNumAgents() - 1)): player += 1
          else: player = 0
                  
        #print("LEN {} {}".format(len(visited_states), max_moves))    
        for state, player in visited_states:
          if (state, player) not in self.plays: 
            continue
          self.plays[(state, player)] += 1
          if (winflag):
            if (player == 0):
              self.wins[(state, player)] += (scoreEvaluationFunction(state) + 500)/1000
          elif (loseflag):
            if (player > 0):
              self.wins[(state, player)] += 1-((scoreEvaluationFunction(state) + 500)/1000)
          #else:
          #  if (player == 0):
          #    self.wins[(state, player)] += (betterEvaluationFunction(state) + 500)/(1000)
          #  if (player > 0):
          #    self.wins[(state, player)] += 1-(betterEvaluationFunction(state) + 500)/(1000)

        #print(self.wins[(state, player)])

        return    

    def final(self, state):
        """
        Called by Pacman game at the terminal state.
        Updates search tree values of states that were visited during an actual game of pacman.
        """
        for s in set(self.states):
            if (s ,0) in self.plays:
                self.plays[(s ,0)] += 1
                self.wins[(s ,0)] += mctsEvalFunction(state)   

# add the function scoreEvaluationFunction to multiAgents.py
def scoreEvaluationFunction(currentGameState):
   """
     This default evaluation function just returns the score of the state.
     The score is the same one displayed in the Pacman GUI.

     This evaluation function is meant for use with adversarial search agents
   """
   return currentGameState.getScore()

def mctsEvalFunction(state):
    """
    Evaluates state reached at the end of the expansion phase.
    """
    return 1 if state.isWin() else 0

def betterEvaluationFunction(currentGameState):

    if currentGameState.isWin() :  return 3000
    if currentGameState.isLose() :  return -3000
    
    currentPos = currentGameState.getPacmanPosition()
    currentFood = currentGameState.getFood()
    GhostStates = currentGameState.getGhostStates()
    capsulePos = currentGameState.getCapsules()
    
    weightFood, weightGhost, weightCapsule, weightHunter = 5.0, 5.0, 5.0, 0.0
    ghostScore, capsuleScore, hunterScore = 0.0, 0.0, 0.0

    
    #"obtain food score" # may closestFood be zero?
    currentFoodList = currentFood.asList()
    closestFood = min([util.manhattanDistance(currentPos, foodPos) for foodPos in currentFoodList])
    foodScore = 1.0 / closestFood
    
    #"obtain ghost, capsule, hunting score"
    if GhostStates:
        ghostPositions = [ghostState.getPosition() for ghostState in GhostStates]
        ScaredTimes = [ghostState.scaredTimer for ghostState in GhostStates]
        ghostDistances = [util.manhattanDistance(currentPos, ghostPos) for ghostPos in ghostPositions]
        
        if sum(ScaredTimes) == 0 : # escape and eat mode
            closestGhost = min(ghostDistances)
            ghostCenterPos = ( sum([ghostPos[0] for ghostPos in ghostPositions])/len(GhostStates),\
                               sum([ghostPos[1] for ghostPos in ghostPositions])/len(GhostStates))
            ghostCenterDist = util.manhattanDistance(currentPos, ghostCenterPos)
            #print 'center ' + str(ghostCenterPos)
            if ghostCenterDist <= closestGhost and closestGhost >= 1 and closestGhost <= 5:
                if len(capsulePos) != 0:
                    closestCapsule = min([util.manhattanDistance(capsule,currentPos) for capsule in capsulePos])
                    if closestCapsule <= 3:
                        weightCapsule, capsuleScore = 20.0, (1.0 / closestCapsule)
                        weightGhost, ghostScore = 3.0, (-1.0 / (ghostCenterDist+1))
                    else:
                        weightGhost, ghostScore = 10.0, (-1.0 / (ghostCenterDist+1))
                else:
                    weightGhost, ghostScore = 10.0, (-1.0 / (ghostCenterDist+1))
            elif ghostCenterDist >= closestGhost and closestGhost >= 1 :
                weightFood *= 2
                if len(capsulePos) != 0:
                    closestCapsule = min([util.manhattanDistance(capsule,currentPos) for capsule in capsulePos])
                    if closestCapsule <= 3:
                        weightCapsule, capsuleScore = 15.0, (1.0 / closestCapsule)
                        weightGhost, ghostScore = 3.0, (-1.0 / closestGhost)
                    else:
                        ghostScore = -1.0 / closestGhost
                else:
                    ghostScore = -1.0 / closestGhost
            elif closestGhost == 0:
                return -3000
            elif closestGhost == 1:
                weightGhost, ghostScore = 15.0, (-1.0 / closestGhost)
            else:
                ghostScore = -1.0 / closestGhost
        else: # hunter mode
            normalGhostDist = []
            closestPrey = 1000000000
            ghostCenterX, ghostCenterY = 0.0, 0.0
            for (index, ghostDist) in enumerate(ghostDistances):
                if ScaredTimes[index] == 0 :
                    normalGhostDist.append(ghostDist)
                    ghostCenterX += ghostPositions[index][0]
                    ghostCenterY += ghostPositions[index][1]
                else:
                    if ghostDist <= ScaredTimes[index] :
                        if ghostDist < closestPrey:
                            closestPrey = ghostDistances[index]
            if normalGhostDist:
                closestGhost = min(normalGhostDist)
                ghostCenterPos = ( ghostCenterX/len(normalGhostDist), ghostCenterY/len(normalGhostDist))
                ghostCenterDist = util.manhattanDistance(currentPos, ghostCenterPos)
                if ghostCenterDist <= closestGhost and closestGhost >= 1 and closestGhost <= 5:
                    weightGhost, ghostScore = 10.0, (- 1.0 / (ghostCenterDist+1))
                elif ghostCenterDist >= closestGhost and closestGhost >= 1 :
                    ghostScore = -1.0 / closestGhost
                elif closestGhost == 0:
                    return -1000000000
                elif closestGhost == 1:
                    weightGhost, ghostScore = 15.0, (-1.0 / closestGhost)
                else:
                    ghostScore = - 1.0 / closestGhost
            weightHunter, hunterScore = 35.0, (1.0 / closestPrey)
    
    #"a new evaluation function."
    heuristic = currentGameState.getScore() + \
                weightFood*foodScore + weightGhost*ghostScore + \
                weightCapsule*capsuleScore + weightHunter*hunterScore
    #print(heuristic)
    return heuristic

# Abbreviation
better = betterEvaluationFunction

