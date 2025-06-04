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
        games = 0
        begin = datetime.datetime.utcnow()
        while datetime.datetime.utcnow() - begin < self.calculation_time:
            self.run_simulation(gameState)
            games += 1
        
        v_i_values = []
        
        actions = gameState.getLegalPacmanActions()

        #SA: note that if there's only one lecal action you should just return it.
        
        # finds best action according to highest v_i value
        for action in actions:
            successor = gameState.generatePacmanSuccessor(action)
            if successor in self.wins and successor in self.plays and self.plays[successor] != 0:
                v_i = self.wins[successor]/self.plays[successor]
                v_i_values.append(v_i)
            else:
                v_i_values.append(float("inf"))

        return actions[v_i_values.index(max(v_i_values))]

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

        #Determine the num of moves that corresponds to the depth for simulations i.e. max_moves = depth*(state.getNumAgents());
        #set player to 0 + visited states to []

        #then iterate from 1 to max moves:

        #1. if all the possible actions for player have already been played, this means you have some stats for all the states,
        #and from the perspective of the player
        #if this is the case, you can pick the value that has the max UCB FROM THE PERSPECTIVE OF THAT PLAYER
        #note that a WIN for player 0 is a LOSS for player 1,2,3,etc.
        #which means your dictionaries DO INDEED have to be indexed by player and state
        #you will be updating wins[(player, state)] if state,isWin and player is pacman
        #you will ALSO be updating wins[(player, state)] if state,isLose and player is NOT pacman
        
        #2.if you don't have stats you can't make a good decision ... just pick a move at random

        #3. With a new state in hand, see if you have any statistics for it.
        #if no, set wins[(player, state)] and plays[(player, state)] to -

        #4. Add the state to your visited state list

        #5. if the state is either a win or loss or you're over max moves you can break from the iteration

        #6. If not, increment the player (i.e. run the same simulation loop for each ghost) and keep going (i.e. pick a move to play for the next player)

        #ONCE YOU have broken from the loop you need to do the backpropagation, i.e. update ALL the stats
        #that relate to the states that were visited during the simulations


        if(len(self.plays) == 0):
            self.plays[state] = 1
            self.wins[state] = self.simulation(state, self.depth, self.index)
        else:
            visitedStates = [state]
            movesStates = []
            agent = 0
            
            if state not in self.plays:
                self.plays[state] = 0
                self.wins[state] = 0
            
            while (True): 

                if self.plays[state] == 0: #case state has not been visited, simulate
                    value = self.simulation(state, self.depth, agent)
                    for visitedState in visitedStates: #where did visitedStates get updated?
                        self.plays[visitedState] += 1
                        self.wins[visitedState] += value
                    break
                
                actions = state.getLegalActions(agent)
                movesStates = [state.generateSuccessor(agent, action) for action in actions]
                
                if len(movesStates) == 0:
                    break
                
                exploredStates = []
                for movesState in movesStates:
                    if movesState not in self.plays.keys():
                        self.plays[movesState] = 0
                        self.wins[movesState] = 0
                    else:
                        exploredStates.append(movesState)
                
                if len(exploredStates) == 0:
                    state = movesStates[0]
                    visitedStates.append(state)
                    for movesState in movesStates:
                        # Expansion
                        for action in movesState.getLegalActions(agent):
                            currentState = movesState.generateSuccessor(agent, action)
                            self.plays[currentState] = 0
                            self.wins[currentState] = 0
                    value = self.simulation(state, self.depth, agent)
                    for visitedState in visitedStates: #again i think this should happen inside the simulation
                        self.plays[visitedState] += 1
                        self.wins[visitedState] += value
                    break
                else: #Here, I think you want to use UCB only if all states in moveStates have been explored, i.e. if len(exploredStates) = len(movesStates)
                      #in which case you can compare the UCB values of all the nodes and just pick the biggest.
                    UCB = []
                    for movesState in movesStates:
                        if self.plays[movesState] != 0:
                            v_i = self.wins[movesState]/self.plays[movesState]
                            res = v_i + self.C * math.sqrt(math.log(self.plays[state]) / self.plays[movesState])
                            UCB.append(res)                            
                        else:
                            UCB.append(float("inf")) 
                    state = movesStates[UCB.index(max(UCB))] #this will always pick the states that have not been explored.  Is that really what you want?
                    visitedStates.append(state)              
                if (agent < (state.getNumAgents() - 1)):
                    agent += 1
                else:
                    agent = 0
    
    def simulation(self, state, depth, agent): 
        if self.depth >= 0:
            depth = self.depth - depth + 1
        
        while not (state.isWin() or state.isLose()):
            if depth == 0:
                break
            #SA in here, once you hit a terminal node you need to 
            #update stats for all the nodes you visited en route.
            #where are you keeping track of the visited nodes?
            action = random.choice(state.getLegalActions(agent))
            successor = state.generateSuccessor(agent, action)
            state = successor
            if (agent < (state.getNumAgents() - 1)):
                agent += 1
            else:
                agent = 0
            if self.depth >= 0:
                depth -= 1

        value = self.evaluationFunction(state) #I did scate this so values lie between 0 and 1 just FYI
        return value

    def final(self, state):
        """
        Called by Pacman game at the terminal state.
        Updates search tree values of states that were visited during an actual game of pacman.
        """
        "*** YOUR CODE HERE ***"
        #util.raiseNotDefined()
        pass

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

