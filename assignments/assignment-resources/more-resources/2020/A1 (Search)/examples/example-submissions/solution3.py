#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports---i.e., ones that are automatically
#   available on TEACH.CS
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os #for time functions
from search import * #for search engines
from rushhour import * #for Rush Hour specific classes and problems

#RUSH HOUR GOAL TEST
def rushhour_goal_fn(state): 
#IMPLEMENT
  '''Have we reached a goal state?'''
  return False #replace this

#RUSH HOUR HEURISTICS
def heur_zero(state):
#IMPLEMENT  
  '''Zero Heuristic can be used to make A* search perform uniform cost search'''
  return 0 #replace this

def heur_min_moves(state):
#IMPLEMENT
  '''basic rushhour heuristic'''
  #An admissible heuristic is nice to have. Getting to the goal may require
  #many moves and each moves the goal vehicle one tile of distance.
  #Since the board wraps around, there are two different
  #directions that lead to the goal.
  #NOTE that we want an estimate of the number of ADDITIONAL
  #     moves required from our current state
  #1. Proceeding in the first direction, let MOVES1 =
  #   number of moves required to get to the goal if it were unobstructed
  #2. Proceeding in the second direction, let MOVES2 =
  #   number of moves required to get to the goal if it were unobstructed
  #
  #Our heuristic value is the minimum of MOVES1 and MOVES2 over all goal vehicles.
  #You should implement this heuristic function exactly, even if it is
  #tempting to improve it.
  return 0 #replace this

def heur_alternate(state):
#IMPLEMENT
  '''a better heuristic'''
  '''INPUT: a rush hour state'''
  '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
  #heur_min_moves has an obvious flaw.
  #Write a heuristic function that improves a little upon heur_min_moves to estimate distance between the current state and the goal.
  #Your function should return a numeric value for the estimate of the distance to the goal.
  return 0 #replace this


def fval_function(sN, weight):
#IMPLEMENT  
  """
  Provide a custom formula for f-value computation for Anytime Weighted A star.
  Returns the fval of the state contained in the sNode.

  @param sNode sN: A search node (containing a rush hour state)
  @param float weight: Weight given by Anytime Weighted A star
  @rtype: float
  """
  
  #Many searches will explore nodes (or states) that are ordered by their f-value.
  #For UCS, the fvalue is the same as the gval of the state. For best-first search, the fvalue is the hval of the state.
  #You can use this function to create an alternate f-value for states; this must be a function of the state and the weight.
  #The function must return a numeric f-value.
  #The value will determine your state's position on the Frontier list during a 'custom' search.
  #You must initialize your search engine object as a 'custom' search engine if you supply a custom fval function.
  return 0 #replace this

def anytime_weighted_astar(initial_state, heur_fn, weight=1., timebound = 10):
#IMPLEMENT  
  '''Provides an implementation of anytime weighted a-star, as described in the HW1 handout'''
  '''INPUT: a rush hour state that represents the start state and a timebound (number of seconds)'''
  '''OUTPUT: A goal state (if a goal is found), else False'''
  '''implementation of weighted astar algorithm'''
  return 0 #replace this

def anytime_gbfs(initial_state, heur_fn, timebound = 10):
#IMPLEMENT  
  '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
  '''INPUT: a rush hour state that represents the start state and a timebound (number of seconds)'''
  '''OUTPUT: A goal state (if a goal is found), else False'''
  '''implementation of anytime greedybfs algorithm'''
  return 0 #replace this

