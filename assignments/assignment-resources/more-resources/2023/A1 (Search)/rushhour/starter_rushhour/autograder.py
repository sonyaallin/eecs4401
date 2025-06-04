# import student's functions
from solution_complete import *
from rushhour import *
import os
import pickle

# Select what to test
test_time_astar = True
test_time_gbfs = True
test_mindist = True
test_fval_function = True
test_iterative_gbfs = True
test_alternate = True
test_iterative_astar = True
test_weighted_astar = True
test_fvalXUP_function = True
test_fvalXDP_function = True
test_goal = True

timebound = 1 #num seconds (time to solve is constrained by this!)

#load the test problems
filehandler = open(b"rushhour_tests_student.pickle", "rb")
PROBLEMS = pickle.load(filehandler)
filehandler.close()

GOALS = []
with (open("rushhour_goals_student.pickle", "rb")) as openfile:
    while True:
        try:
            GOALS.append(pickle.load(openfile))
        except EOFError:
            break

def test_goal_fn():

    score = 0
    details = set()
    score = 0
    
    for i in range(0,len(GOALS)):
        s0 = GOALS[i]

        if (rushhour_goal_fn(s0)):
            score += 1
    
    print("Goal states correctly detected {} of {} times.".format(score, len(GOALS)))    

def test_time_astar_fun():

    s0 = PROBLEMS[0]  # We start with a relatively hard one
    time = os.times()[0]
    weight = 2
    final = iterative_astar(s0, heur_fn=heur_alternate, weight=weight, timebound=timebound)
    difference = os.times()[0] - time
    print('This amount of time was given: {}'.format(timebound))
    print('Your iterative_astar used this amount of time: {}'.format(difference))

    if heur_alternate(s0) == 0:
        print('Heur alternate returned 0; this should only happen if we are at a goal.')
        return

    if difference - timebound < 0.1:
        print('Time keeping was acceptable on this problem')
    if difference - timebound >= 0.1:
        print('Time keeping was not acceptable on this problem')

def test_time_gbfs_fun():

    s0 = PROBLEMS[0]  # We start with a relatively hard one
    time = os.times()[0]
    final = iterative_gbfs(s0, heur_fn=heur_alternate, timebound=timebound)
    difference = os.times()[0] - time
    print('This amount of time was given: {}'.format(timebound))
    print('Your iterative_gbfs used this amount of time: {}'.format(difference))

    if heur_alternate(s0) == 0:
        print('Heur alternate returned 0; this should only happen if we are at a goal.')
        return
        
    if difference - timebound < 0.1:
        print('Time keeping was acceptable on this problem')
    if difference - timebound >= 0.1:
        print('Time keeping was not acceptable on this problem')

def test_mindist():
    ##############################################################
    # TEST MIN DISTANCE
    print('Testing Min Distance Estimate')

    # Correct Minimum distances for the initial states of the provided problem set
    correct_basic_dist = [7, 0, 1, 2, 2, 0, 0, 7, 1, 7, 7, 7, 7, 7, 2, 2, 2, 6, 14, 27]

    solved = 0;
    unsolved = [];
    for i in range(0, 20):        

        s0 = PROBLEMS[i]

        basic_dist = heur_min_dist(s0)
        print('calculated min_dist:', str(basic_dist))
        # To see state
        # print("PROBLEM {}".format(i))
        # print(s0.state_string())

        if basic_dist == correct_basic_dist[i]:
            solved += 1
        else:
            unsolved.append(i)

    print("*************************************")
    print("In the problem set provided, you calculated the correct min_dist distance for {} states out of 20.".format(
        solved))
    print("States that were incorrect: {}".format(unsolved))
    print("*************************************\n")
    ##############################################################


def test_alternate_fun():

    ##############################################################
    # TEST ALTERNATE HEURISTIC
    print('Testing alternate heuristic with best_first search')

    zerocount, solved = 0, 0;
    unsolved = [];

    #for reference, solution lengths are here
    basic_dist_solns = [-99, 2, 1, 2, 4, 2, 4, 10, 1, 7, 15, 8, -99, -99, 4, 7, 4, -99, -99, 28]
    basicsolved = len([i for i in basic_dist_solns if i != -99])

    other_dist_solns = [10, 1, 1, 2, 3, 1, 1, 7, 1, 7, 37, -99, -99, -99, 2, 5, 2, 7, -99, 28]
    othersolved = len([i for i in other_dist_solns if i != -99])   
    
    for i in range(0, len(PROBLEMS)):

        print("*************************************")
        print("PROBLEM {}".format(i))

        s0 = PROBLEMS[i]  # Problems get harder as i gets bigger
        se = SearchEngine('best_first', 'full')
        if heur_alternate(s0) == 0: 
            print('Heur alternate returned 0; is this what you really want?')
            zerocount += 1

        se.init_search(s0, goal_fn=rushhour_goal_fn, heur_fn=heur_alternate)
        final, stats = se.search(timebound)

        if final:
            # final.print_path() #to see solution
            solved += 1
        else:
            unsolved.append(i)


    if (zerocount == len(PROBLEMS)):
        print("You must implement a heuristic before your performance can be estimated.")
        return

    print("\n*************************************")
    print("Of {} initial problems, {} were solved in less than {} seconds by this solver.".format(len(PROBLEMS), solved, timebound))
    print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))
    print("The basic distance implementation solved {} out of the {} practice problems given {} seconds.".format(basicsolved, len(PROBLEMS), timebound))
    print("A second, improved heuristic solved {} out of the {} practice problems given {} seconds.".format(othersolved, len(PROBLEMS), timebound))
    print("*************************************\n")
    ##############################################################

def test_fval_function_fun():

    test_state = Rushhour("START", 6, None, None, None)

    correct_fvals1 = [16.0, 9.0, 56.0]
    eps = 0.01

    ##############################################################
    # TEST fval_function
    print("*************************************")
    print('Testing fval_function')

    solved1 = 0
    weights = [1, .3, 5.]
    for i in range(len(weights)):

        test_node = sNode(test_state, hval=10, fval_function=fval_function)

        fval = round(fval_function(test_node, weights[i]), 0)

        if fval > correct_fvals1[i] - eps and fval < correct_fvals1[i] + eps:
            solved1 += 1

    print("\n*************************************")
    print("Your fval_function calculated the correct fval for {} out of {} tests.".format(solved1, len(correct_fvals1)))
    print("*************************************\n")

    ##############################################################


def test_fval_function_XDP():

    test_state = Rushhour("START", 6, None, None, None)

    correct_fvals1 = [16, 19, 13]
    eps = 0.01    

    ##############################################################
    # TEST fval_function_XDP
    print("*************************************")
    print('Testing fval_function_XDP')

    solved1 = 0
    weights = [1, .3, 5.]
    for i in range(len(weights)):

        test_node = sNode(test_state, hval=10, fval_function=fval_function_XDP)

        fval = round(fval_function_XDP(test_node, weights[i]), 0)
        print('Test', str(i), 'calculated fval:', str(fval), 'correct:', str(correct_fvals1[i]))

        if fval > correct_fvals1[i] - eps and fval < correct_fvals1[i] + eps :
            solved1 += 1

    print("\n*************************************")
    print("Your fval_function_XDP calculated the correct fval for {} out of {} tests.".format(solved1, len(correct_fvals1)))
    print("*************************************\n")

    ##############################################################


def test_fval_function_XUP():

    test_state = Rushhour("START", 6, None, None, None)

    correct_fvals1 = [16.0, 49.0, 11.0]
    eps = 0.01    

    ##############################################################
    # TEST fval_function_XUP
    print("*************************************")
    print('Testing fval_function_XUP')

    solved1 = 0
    weights = [1, .3, 5.]
    for i in range(len(weights)):

        test_node = sNode(test_state, hval=10, fval_function=fval_function_XUP)

        fval = round(fval_function_XUP(test_node, weights[i]), 0)
        print('Test', str(i), 'calculated fval:', str(fval), 'correct:', str(correct_fvals1[i]))

        if fval > correct_fvals1[i] - eps and fval < correct_fvals1[i] + eps :
            solved1 += 1

    print("\n*************************************")
    print("Your fval_function_XUP calculated the correct fval for {} out of {} tests.".format(solved1, len(correct_fvals1)))
    print("*************************************\n")

    ##############################################################


def test_iterative_gbfs_fun():

    #for reference, solution lengths are here
    basic_dist_solns = [-99, 1, 1, 2, 3, 1, 1, 8, 1, 7, 15, 8, -99, -99, 2, 3, 2, -99, -99, 28]
    basicsolved = len([i for i in basic_dist_solns if i != -99])

    other_dist_solns = [10, 1, 1, 2, 3, 1, 1, 7, 1, 7, 37, -99, -99, -99, 2, 3, 2, 7, -99, 28]
    othersolved = len([i for i in other_dist_solns if i != -99])

    ##############################################################
    # TEST iterative GBFS
    print('Testing iterative GBFS')

    zerocount, solved, benchmark = 0, 0, 0;
    unsolved = [];
    for i in range(0, len(PROBLEMS)):
        print("*************************************")
        print("PROBLEM {}".format(i))

        s0 = PROBLEMS[i]  # Problems get a little harder as i gets bigger
        
        if heur_alternate(s0) == 0: 
            print('Heur alternate returned 0; is this what you really want?')
            zerocount += 1

        final, stats = iterative_gbfs(s0, heur_fn=heur_alternate, timebound=timebound)
        if final:
            if final.gval <= basic_dist_solns[i] or basic_dist_solns[i] == -99:  
                benchmark += 1
            solved += 1
        else:
            unsolved.append(i)

    if (zerocount == len(PROBLEMS)):
        print("You must implement a heuristic before your performance can be estimated.")
        return

    print("\n*************************************")
    print("Of {} initial problems, {} were solved in less than {} seconds by this solver.".format(len(PROBLEMS), solved,timebound))
    print("Of the {} problems that were solved, the cost of {} matched or outperformed the basic benchmark.".format(solved,benchmark))
    print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))
    print("The basic distance implementation solved {} out of the {} practice problems given {} seconds.".format(basicsolved, len(PROBLEMS), timebound))
    print("A second, improved heuristic solved {} out of the {} practice problems given {} seconds.".format(othersolved, len(PROBLEMS), timebound))
    print("*************************************\n")

def test_iterative_astar_fun():

    basic_dist_solns = [10, 1, 1, 2, 3, 1, 1, 8, 1, 7, -99, 8, -99, -99, 3, 4, 3, -99, -99, 28]
    basicsolved = len([i for i in basic_dist_solns if i != -99])

    other_dist_solns = [10, 1, 1, 2, 3, 1, 1, 7, 1, 7, -99, 8, -99, -99, 2, 4, 2, 7, -99, 28]
    othersolved = len([i for i in other_dist_solns if i != -99])

    ##############################################################
    # TEST iterative WEIGHTED A STAR
    print('Testing iterative Weighted A Star')

    solved, zerocount, benchmark = 0, 0, 0;
    unsolved = [];

    for i in range(0, len(PROBLEMS)):
        print("*************************************")
        print("PROBLEM {}".format(i))

        s0 = PROBLEMS[i]  # Problems get harder as i gets bigger
        print("*************************************")
        if heur_alternate(s0) == 0: 
            print('Heur alternate returned 0; is this what you really want?')
            zerocount += 1

        weight = 10  # note that if you want to over-ride this initial weight in your implementation, you are welcome to!
        final, stats = iterative_astar(s0, heur_fn=heur_alternate, weight=weight, timebound=timebound)
     
        if final:
            # final.print_path()
            if final.gval <= basic_dist_solns[i] or basic_dist_solns[i] == -99:
                benchmark += 1
            solved += 1
        else:
            unsolved.append(i)

    if (zerocount == len(PROBLEMS)):
        print("You must implement a heuristic before your performance can be estimated.")
        return

    print("\n*************************************")
    print("Of {} initial problems, {} were solved in less than {} seconds by this solver.".format(len(PROBLEMS), solved,
                                                                                                  timebound))
    print("Of the {} problems that were solved, the cost of {} matched or outperformed the benchmark.".format(solved,
                                                                                                              benchmark))
    print("Problems that remain unsolved in the set are Problems: {}".format(unsolved))
    print("The basic distance implementation solved {} out of the {} practice problems given {} seconds.".format(basicsolved, len(PROBLEMS), timebound))
    print("A second, improved heuristic solved {} out of the {} practice problems given {} seconds.".format(othersolved, len(PROBLEMS), timebound))
    print("*************************************\n")

    ##############################################################

def test_weighted_astar_fun():
    solved, score, total, zerocount = 0, 0, 0, 0
    weights = [10, 5, 2, 1]

    for j in range(3, 8):  
        m = PROBLEMS[j]  # Problems get harder as j gets bigger
        if heur_alternate(m) == 0: 
            print('Heur alternate returned 0; is this what you really want?')
            zerocount += 1
        state_counts = []
        gvals = []
        inds = []
        count = 0
        for weight in weights:
            final, stats = weighted_astar(m, heur_alternate, weight, timebound) #extra time added!
            if final:
                solved += 1 
                inds.append(count) #must solve one
                state_counts.append(stats.states_expanded)
                gvals.append(final.gval)
            else:
                state_counts.append(-99)
                gvals.append(-99)
            count += 1

        # now look at the state_counts and gvals
        if len(inds) > 1:
            total += 1 # points for solving more problems
            flag = True  # We didn't solve enough to make a good comparison here.
        else:
            flag = False

        for i in range(len(inds) - 1):  # check ordering of the solutions
            if state_counts[inds[i + 1]] < state_counts[inds[i]] or gvals[inds[i + 1]] > gvals[inds[i]]:  # state counts should be increasing and gvals decreasing
                flag = False # wha??
                        
        if flag: score += 1  # points for refinements in solutions. Assumes admissible heuristic! Why?  

    if (zerocount == 5):
        print("You must implement a heuristic before your performance can be estimated.")
        return

    print("\n*************************************")
    print("Of the 20 runs over 5 problems, {} solutions were found with weighted a star in the time allotted.".format(solved))
    print("Weighted a-star expanded more nodes as weights decreased {} of {} times".format(score, total))
    print("Estimated score is {} of 10.".format(total + score))
    print("THIS ESTIMATE IS ROUGH.  You will likely want to test further ...")
    print("*************************************\n")

def test_all():
    if test_goal: test_goal_fn()
    if test_time_astar: test_time_astar_fun()
    if test_time_gbfs: test_time_gbfs_fun()
    if test_mindist: test_mindist()
    if test_fval_function: test_fval_function_fun()
    if test_fvalXUP_function: test_fval_function_XUP()
    if test_fvalXDP_function: test_fval_function_XDP()
    if test_iterative_gbfs: test_iterative_gbfs_fun()
    if test_alternate: test_alternate_fun()
    if test_iterative_astar: test_iterative_astar_fun()
    if test_weighted_astar: test_weighted_astar_fun()

    for w in [1,1.25,1.5,1.75,2]:
        states_expanded, states_generated, solution_lengths = compare_weighted_astars(PROBLEMS[0],w)
        print("For the weight {} the respective number of states generated are {}, states expanded are {} and the respective final solution lengths are {}.".format(w, states_generated, states_expanded, solution_lengths))


if __name__=='__main__':
    test_all()

