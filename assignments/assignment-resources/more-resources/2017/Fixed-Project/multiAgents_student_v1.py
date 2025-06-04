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
import random, util, math
import datetime

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
        return self.DFMiniMax(gameState, 0, 0)
    
    def DFMiniMax(self, gameState, depth, agent):
        # checks if depth reached or game is finished
        if depth >= self.depth or gameState.isLose() or gameState.isWin():
            return self.evaluationFunction(gameState)
        
        if (agent < (gameState.getNumAgents() - 1)):
            nextAgent = agent + 1
            nextDepth = depth
        else:
            nextAgent = 0
            nextDepth = depth + 1
        
        scores = []
        actions = gameState.getLegalActions(agent)
        
        for action in actions:
            successor = gameState.generateSuccessor(agent, action)
            scores.append(self.DFMiniMax(successor, nextDepth, nextAgent))
        
        # if agent is pacman
        if agent == 0:
            # returns the best action at the root node
            if depth == 0:
                return actions[scores.index(max(scores))]
            return max(scores)
        # if agent is ghost
        else:
            return min(scores)

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        return self.AlphaBeta(gameState, 0, 0, float("-inf"), float("inf"))
    
    def AlphaBeta(self, gameState, agent, depth, alpha, beta):
        # checks if depth reached or game is finished
        if depth >= self.depth or gameState.isLose() or gameState.isWin():
            return self.evaluationFunction(gameState)
        
        if (agent < (gameState.getNumAgents() - 1)):
            nextAgent = agent + 1
            nextDepth = depth
        else:
            nextAgent = 0
            nextDepth = depth + 1
            
        actions = gameState.getLegalActions(agent)
        
        # pacman plays, max player
        if agent == 0:
            bestAction = None
            for action in actions:
                successor = gameState.generateSuccessor(agent, action)
                alphaValue = self.AlphaBeta(successor, nextAgent, nextDepth, alpha, beta)
                if alphaValue > alpha:
                    bestAction = action
                    alpha = alphaValue
                if beta <= alpha:
                    break
            if depth == 0:
                return bestAction
            return alpha
        
        # ghost plays, min player
        else:
            for action in actions:
                successor = gameState.generateSuccessor(agent, action)
                beta = min(beta, self.AlphaBeta(successor, nextAgent, nextDepth, alpha, beta))
                if beta <= alpha:
                    break
            return beta

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

    def __init__(self, evalFn='mctsEvalFunction', depth='-1', timeout='40', numTraining=100, C='2', Q=None):
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

        self.numTraining = numTraining

        "*** YOUR CODE HERE ***"

        MultiAgentSearchAgent.__init__(self, evalFn, depth)

    def update(self, state):
        """
        You do not need to modify this function. This function is called every time an agent makes a move.
        """
        self.states.append(state)

    def getAction(self, gameState):
        """
        Returns the best action using UCT. Calls runSimulation to update nodes
        in its wins and plays dictionary, and returns best successor of gameState.
        """
        "*** YOUR CODE HERE ***"
        player = 0
        actions = gameState.getLegalPacmanActions()
        
        if not actions:
            return
        if len(actions) == 1:
            return actions[0]
        
        games = 0
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            self.run_simulation(gameState)
            games += 1

        movesStates = [(action, gameState.generatePacmanSuccessor(action)) for action in actions]
        # Display the number of calls of `run_simulation` and the
        # time elapsed.
        #print games, datetime.datetime.utcnow - begin
        
        percent_wins, move = max(
            (self.wins.get(gameState, 0) / self.plays.get(gameState, 1), action)
            for action, gameState in movesStates
        )
        
        #for x in sorted(
            #((100 * self.wins.get(gameState, 0) /
              #self.plays.get(gameState, 1),
              #self.wins.get(gameState, 0),
              #self.plays.get(gameState, 0), action)
             #for action, gameState in movesStates),
                #reverse=True            
        #):
            #print "{3}: {0:.2f}% ({1} / {2})".format(*x)
            
        return move

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
        plays, wins = self.plays, self.wins
        
        player = 0
        
        visitedStates = set()
        
        expand = True
        
        # in here the tutorial uses self.max_moves
        # I don't know what it does, therefore I've used self.C
        # the only reasonable thing I find to iterate over
        for t in xrange(1, self.C + 1):
            actions = state.getLegalPacmanActions()
            
            movesStates = [(action, state.generatePacmanSuccessor(action)) for action in actions]
            
            if all(plays.get(gameState) for action, gameState in movesStates):
                total_sum = sum(plays[gameState] for action, gameState in movesStates)
                if total_sum != 0:
                    log_total = math.log(total_sum)
                    value, move, state = max(
                        ((wins[gameState] / plays[gameState]) +
                         self.C * math.sqrt(log_total / plays[gameState]), player, gameState)
                         for action, gameState in movesStates
                    )
            else:
                move, state = random.choice(movesStates)
            
            if expand and state not in plays:
                expand = False
                plays[state] = 0
                wins[state] = 0
                if t > self.depth:
                    self.depth = t
            
            visitedStates.add(state)
            
            if state.isWin():
                break
            
        for state in visitedStates:
            if state not in plays:
                continue
            plays[state] += 1
            if state.isWin():
                wins[state] += 1
        

    def final(self, state):
        """
        Called by Pacman game at the terminal state.
        Updates search tree values of states that were visited during an actual game of pacman.
        """
        "*** YOUR CODE HERE ***"
        #util.raiseNotDefined()
        for s in set(self.states):
            if s in self.plays:
                self.plays[s] += 1
                self.wins[s] += self.evaluationFunction(state)        

def mctsEvalFunction(state):
    """
    Evaluates state reached at the end of the expansion phase.
    """
    return 1 if state.isWin() else 0

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (to help improve your UCT MCTS).
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()
    
def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
    """
    return currentGameState.getScore()

# Abbreviation
better = betterEvaluationFunction

