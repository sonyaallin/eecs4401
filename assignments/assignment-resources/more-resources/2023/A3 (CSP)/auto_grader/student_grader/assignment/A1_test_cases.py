from dependencies.search import *
import itertools
import traceback
import gc

from utils.utilities import sortInnerMostLists, TO_exc, setTO, setMEM, resetMEM

import dependencies.solutions.rushhour as sol_rushhour

from utils.test_tools import max_grade

from .test_cases_helpers import *

#1200
DEFAULT_TIMEOUT = 20
RUSHHOUR = 'rushhour.py'

vs = [5*(i+1) for i in range(10)]
hs = [6*(i+1) for i in range(10)]
ws = [7*(i+1) for i in range(10)]

PROBLEMS = [sol_rushhour.make_rand_init_state(v,(h,w)) for (v,h,w) in zip(vs,hs,ws)]

PROBLEMS_THREE_GOALS = \
        [sol_rushhour.make_rand_init_state(v,(h,w),3) for (v,h,w) in zip(vs,hs,ws)]

PROBLEMS_SEARCH = [sol_rushhour.make_rand_init_state(5,(5,5))
                                                for i in range(10)] + \
                  [sol_rushhour.make_rand_init_state(5,(7,7),2)
                                                for i in range(10)] + \
                  [sol_rushhour.make_rand_init_state(10,(15,15))
                                                for i in range(10)]

FIVE_VEHICLES = [sol_rushhour.make_rand_init_state(5,(5,5)),
                 sol_rushhour.make_rand_init_state(5,(5,5))]


###### BEGIN EASY TESTS ######

@max_grade(2*len(PROBLEMS))
def test_make_init_board(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    score = 0
    timeout = DEFAULT_TIMEOUT

    details = set()

    for problem in PROBLEMS:
        board_size, goal_entrance, goal_direction = \
                problem.get_board_properties()
        vehicle_statuses = sorted(problem.get_vehicle_statuses())

        try:
            setTO(timeout)
            stu_problem = stu_rushhour.make_init_state(board_size,
                    vehicle_statuses, goal_entrance, goal_direction)

            stu_board_size, stu_goal_entrance, stu_goal_direction = \
                    stu_problem.get_board_properties()

            stu_vehicle_statuses = sorted(stu_problem.get_vehicle_statuses())

            setTO(0)

            failed = False

            if stu_board_size != board_size:
                failed = True
                details.add("Error in make_init_state: incorrect board size")

            if stu_goal_entrance != goal_entrance:
                failed = True
                details.add("Error in make_init_state: incorrect goal entrance location")

            if stu_goal_direction != goal_direction:
                failed = True
                details.add("Error in make_init_state: incorrect goal direction")

            if len(stu_vehicle_statuses) == len(vehicle_statuses):
                for i, vehicle in enumerate(vehicle_statuses):
                    stu_vehicle = stu_vehicle_statuses[i]

                    if tuple(stu_vehicle) != tuple(vehicle):
                        failed = True
                        detail.add("Error in make_init_state: incorrect vehicle status")
                        break
            else:
                failed = True
                detail.add("Error in make_init_state: incorrect number of vehicles")

            if not failed:
                score += 2

        except TO_exc:
            details.add("Got TIMEOUT while testing make_init_state")
        except:
            details.add("A runtime error occurred while testing make_init_state: %r" % traceback.format_exc())

    details = "\n".join(details)

    return score, details

@max_grade(2*len(PROBLEMS))
def test_make_init_state(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    score = 0

    details = set()

    for problem in PROBLEMS:
        board_size, goal_entrance, goal_direction = \
                problem.get_board_properties()
        vehicle_statuses = sorted(problem.get_vehicle_statuses())

        try:
            setTO(timeout)
            stu_problem = stu_rushhour.make_init_state(board_size,
                    vehicle_statuses, goal_entrance, goal_direction)
            setTO(0)

            failed = False

            if stu_problem.action != "START":
                failed = True
                details.add("Error in make_init_state: initial state has wrong action name")

            if stu_problem.gval != 0:
                failed = True
                details.add("Error in make_init_state: initial state has wrong g value")

            if stu_problem.parent is not None:
                failed = True
                details.add("Error in make_init_state: initial state has a parent")

            if not failed:
                score += 2

        except TO_exc:
            details.add("Got TIMEOUT while testing make_init_state")
        except:
            details.add("A runtime error occurred while testing make_init_state: %r" % traceback.format_exc())

    details = "\n".join(details)

    return score, details

@max_grade(20)
def test_successors_simple(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    passed = False
    details = ""

    board_size = (6,6)
    goal_entrance = (2,1)
    goal_direction = 'S'

    vehicles = [['G', (2,3), 2, False, True],
                ['X', (2,2), 2, True, False]]

    sol_problem = sol_rushhour.make_init_state(board_size, vehicles,
            goal_entrance, goal_direction)
    sol_successors = comparable_successors(sol_problem)

    try:
        setTO(timeout)

        stu_problem = stu_rushhour.make_init_state(board_size, vehicles,
                goal_entrance, goal_direction)
        stu_successors = comparable_successors(stu_problem)

        setTO(0)

        if stu_successors == sol_successors:
            passed = True
        else:
            details = "Error in successor generation (successors don't match expected results)"

    except TO_exc:
        details = "Got TIMEOUT while testing successor generation"
    except:
        details = "A runtime error occurred while testing successor generation: %r" % traceback.format_exc()

    return passed, details

@max_grade(5)
def test_successors_through_goal(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    passed = False
    details = ""

    try:
        board_size = (3,1)
        goal_entrance = (0,0)
        goal_direction = 'S'
        vehicles = [['G', (0,2), 1, False, True],
                    ['X', (0,1), 1, False, False]]

        sol_problem = sol_rushhour.make_init_state(board_size, vehicles,
                goal_entrance, goal_direction)
        sol_successors = comparable_successors(sol_problem)

        setTO(timeout)
        stu_problem = stu_rushhour.make_init_state(board_size, vehicles,
                goal_entrance, goal_direction)
        stu_successors = comparable_successors(stu_problem)
        setTO(0)

        if stu_successors == sol_successors:
            passed = True
        else:
            details =  "Error in successor generation (the goal is blocking vehicles?)"

    except TO_exc:
        details = "Got TIMEOUT while testing successor generation"
    except:
        details = "A runtime error occurred while testing successor generation: %r" % traceback.format_exc()

    return passed, details

@max_grade(5)
def test_successors_empty_name(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    passed = False
    details = ""

    board_size = (3,1)
    goal_entrance = (0,0)
    goal_direction = 'S'

    vehicles = [['.', (0,2), 1, False, True],
                ['', (0,1), 1, False, False]]

    sol_problem = sol_rushhour.make_init_state(board_size, vehicles,
            goal_entrance, goal_direction)
    sol_successors = comparable_successors(sol_problem)

    try:
        setTO(timeout)

        stu_problem = stu_rushhour.make_init_state(board_size, vehicles,
                goal_entrance, goal_direction)
        stu_successors = comparable_successors(stu_problem)

        setTO(0)

        if stu_successors == sol_successors:
            passed = True
        else:
            details =  "Error in successor generation (with vehicle with empty name or name starting with a period)"

    except TO_exc:
        details = "Got TIMEOUT while testing successor generation"
    except:
        details = "A runtime error occurred while testing successor generation: %r" % traceback.format_exc()

    return passed, details

@max_grade(len(PROBLEMS))
def test_successors_state_properties(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    score = 0

    details = set()

    for problem in PROBLEMS:
        board_size, goal_entrance, goal_direction = \
                problem.get_board_properties()
        vehicle_statuses = sorted(problem.get_vehicle_statuses())

        successors = sorted_successors(problem)

        try:
            setTO(timeout)
            stu_problem = stu_rushhour.make_init_state(board_size,
                    vehicle_statuses, goal_entrance, goal_direction)

            stu_successors = sorted_successors(stu_problem)

            failed = False

            if len(stu_successors) != len(successors):
                failed = True
                details.add("Error in successor generation: wrong number of successors")
            else:
                for i, succ in enumerate(successors):
                    stu_succ = stu_successors[i]

                    if stu_succ.parent != stu_problem:
                        failed = True
                        details.add("Error in successor generation: incorrect parent assignment")

                    ##XXX should I ignore capitalization? spaces?
                    #if stu_succ.action != succ.action:
                    #    failed = True
                    #    details.add("wrong action name?")

                    if stu_succ.gval != succ.gval:
                        failed = True
                        details.add("Error in successor generation: wrong g value")

            if not failed:
                score += 1

            setTO(0)
        except TO_exc:
            details.add("Got TIMEOUT while testing successor generation")
        except:
            details.add("A runtime error occurred while testing successor generation: %r" % traceback.format_exc())

    details = "\n".join(details)

    return score, details

@max_grade(20)
def test_goal_check_simple(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    details = set()
    score = 0

    board_size = (5,5)
    goal_entrance = (2,2)

    try:
        setTO(timeout)
        goal_direction = 'N'
        vehicles = [['G',(2,2),2,False,True]]
        state = stu_rushhour.make_init_state(board_size, vehicles,
                goal_entrance, goal_direction)
        if stu_rushhour.rushhour_goal_fn(state):
            score += 5
        else:
            details.add("Goal function failed (with 'N' goal)")

        goal_direction = 'S'
        vehicles = [['G',(2,1),2,False,True]]
        state = stu_rushhour.make_init_state(board_size, vehicles,
                goal_entrance, goal_direction)
        if stu_rushhour.rushhour_goal_fn(state):
            score += 5
        else:
            details.add("Goal function failed (with 'S' goal)")

        goal_direction = 'W'
        vehicles = [['G',(2,2),2,True,True]]
        state = stu_rushhour.make_init_state(board_size, vehicles,
                goal_entrance, goal_direction)
        if stu_rushhour.rushhour_goal_fn(state):
            score += 5
        else:
            details.add("Goal function failed (with 'W' goal)")

        goal_direction = 'E'
        vehicles = [['G',(1,2),2,True,True]]
        state = stu_rushhour.make_init_state(board_size, vehicles,
                goal_entrance, goal_direction)
        if stu_rushhour.rushhour_goal_fn(state):
            score += 5
        else:
            details.add("Goal function failed (with 'E' goal)")

        setTO(0)
    except TO_exc:
        details.add("Got TIMEOUT while testing goal function")
        passed = False
    except:
        details.add("A runtime error occurred while testing goal function: %r" % traceback.format_exc())
        passed = False

    details = "\n".join(details)
    return score, details

@max_grade(10)
def test_goal_check_blocked(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    details = ""
    passed = True

    board_size = (5,5)
    goal_entrance = (2,2)

    try:
        setTO(DEFAULT_TIMEOUT)
        goal_direction = 'N'
        vehicles = [['G',(2,2),2,False,True],
                    ['X',(2,1),1,False,False]]
        state = stu_rushhour.make_init_state(board_size, vehicles,
                goal_entrance, goal_direction)
        if not stu_rushhour.rushhour_goal_fn(state):
            passed = False

        goal_direction = 'S'
        vehicles = [['G',(2,1),2,False,True],
                    ['X',(2,3),1,False,False]]
        state = stu_rushhour.make_init_state(board_size, vehicles,
                goal_entrance, goal_direction)
        if not stu_rushhour.rushhour_goal_fn(state):
            passed = False

        goal_direction = 'W'
        vehicles = [['G',(2,2),2,True,True],
                    ['X',(1,2),1,False,False]]
        state = stu_rushhour.make_init_state(board_size, vehicles,
                goal_entrance, goal_direction)
        if not stu_rushhour.rushhour_goal_fn(state):
            passed = False

        goal_direction = 'E'
        vehicles = [['G',(1,2),2,True,True],
                    ['X',(3,2),1,True,True]]
        state = stu_rushhour.make_init_state(board_size, vehicles,
                goal_entrance, goal_direction)
        if not stu_rushhour.rushhour_goal_fn(state):
            passed = False
        setTO(0)

        if not passed:
            details = "Goal function failed (with a car parked behind the goal)"
    except TO_exc:
        details = "Got TIMEOUT while testing goal function"
        passed = False
    except:
        details = "A runtime error occurred while testing goal function: %r" % traceback.format_exc()
        passed = False

    return passed, details

@max_grade(10)
def test_hashable_state_basic_different(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    passed = False
    details = ""

    try:
        setTO(timeout)

        board_size, goal_entrance, goal_direction = \
                FIVE_VEHICLES[0].get_board_properties()
        vehicle_statuses = FIVE_VEHICLES[0].get_vehicle_statuses()
        first = stu_rushhour.make_init_state(board_size, vehicle_statuses,
                goal_entrance, goal_direction)

        board_size, goal_entrance, goal_direction = \
                FIVE_VEHICLES[1].get_board_properties()
        vehicle_statuses = FIVE_VEHICLES[1].get_vehicle_statuses()
        second = stu_rushhour.make_init_state(board_size, vehicle_statuses,
                goal_entrance, goal_direction)

        if first.hashable_state() != second.hashable_state():
            passed = True
        else:
            details = "Error in hashable_state: different states with same hash"

        setTO(0)
    except TO_exc:
        details = "Got TIMEOUT while testing hashable_state"
    except:
        details = "A runtime error occurred while testing hashable_state: %r" % traceback.format_exc()

    return passed, details

@max_grade(10)
def test_hashable_state_basic_equal(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    passed = False
    details = ""

    try:
        board_size, goal_entrance, goal_direction = \
                FIVE_VEHICLES[0].get_board_properties()
        vehicle_statuses = FIVE_VEHICLES[0].get_vehicle_statuses()

        setTO(timeout)

        first = stu_rushhour.make_init_state(board_size, vehicle_statuses,
                goal_entrance, goal_direction)

        second = stu_rushhour.make_init_state(board_size, vehicle_statuses,
                goal_entrance, goal_direction)

        if first.hashable_state() == second.hashable_state():
            passed = True
        else:
            details = "Error in hashable_state: identical states with different hash"

        setTO(0)
    except TO_exc:
        details = "Got TIMEOUT while testing hashable_state"
    except:
        details = "A runtime error occurred while testing hashable_state: %r" % traceback.format_exc()

    return passed, details

@max_grade(len(PROBLEMS))
def test_hashable_equivalent_states_with_different_properties(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    score = 0
    details = set()

    for problem in PROBLEMS:
        board_size, goal_entrance, goal_direction = \
                problem.get_board_properties()
        vehicle_statuses = problem.get_vehicle_statuses()

        try:
            setTO(timeout)
            stu_state = stu_rushhour.make_init_state(board_size,
                    vehicle_statuses, goal_entrance, goal_direction)
            stu_state_mod = stu_rushhour.make_init_state(board_size,
                    vehicle_statuses, goal_entrance, goal_direction)

            stu_state_mod.gval = 10
            stu_state_mod.action = 'arbitrary'
            stu_state_mod.index = 100

            if stu_state.hashable_state() == stu_state_mod.hashable_state():
                score += 1
            else:
                details.add("Error in hashable_state: equivalent states with different hash")

            setTO(0)
        except TO_exc:
            details.add("Got TIMEOUT while testing hashable_state")
        except:
            details.add("A runtime error occurred while testing hashable_state: %r" % traceback.format_exc())

    details = "\n".join(details)

    return score, details


@max_grade(10)
def test_hashable_with_vehicles_with_similar_names(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    passed = False
    details = ""

    board_size = (5,5)
    goal_entrance = (2,4)
    goal_direction = 'N'

#    ...2. ...1.
#    ..G2. ..G1.
#    ...1. ...2.
#    ...1. ...2.
#    ..N.. ..N..

    vehicles_first = [['carg',(2,1),1,False,True],
                      ['car1',(3,2),2,False,False],
                      ['car2',(3,0),2,False,False]]

    vehicles_second = [['carg',(2,1),1,False,True],
                       ['car1',(3,0),2,False,False],
                       ['car2',(3,2),2,False,False]]

    try:
        setTO(timeout)

        first = stu_rushhour.make_init_state(board_size, vehicles_first,
                    goal_entrance, goal_direction)
        second = stu_rushhour.make_init_state(board_size, vehicles_second,
                    goal_entrance, goal_direction)

        if first.hashable_state() != second.hashable_state():
            passed = True
        else:
            details = "Error in hashable_state: different states with similar vehicle names have same hash"

        setTO(0)
    except TO_exc:
        details = "Got TIMEOUT while testing hashable_state"
    except:
        details = "A runtime error occurred while testing hashable_state: %r" % traceback.format_exc()

    return passed, details

###### BEGIN HARD TESTS ######

@max_grade(5)
def test_successors_long_vehicle(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    passed = False
    details = ""

    board_size = (5,5)
    goal_entrance = (1,2)
    goal_direction = 'S'

    vehicles = [['g',(1,3),5,False,True],
                ['car',(3,4),2,True,False]]

    problem = sol_rushhour.make_init_state(board_size, vehicles,
                    goal_entrance, goal_direction)
    successors = comparable_successors(problem)

    try:
        setTO(timeout)

        stu_problem = stu_rushhour.make_init_state(board_size, vehicles,
                            goal_entrance, goal_direction)
        stu_successors = comparable_successors(stu_problem)

        if stu_successors == successors:
            passed = True
        else:
            details = "Error in successor generation (a very long vehicle is blocking itself?)"

        setTO(0)
    except TO_exc:
        details = "Got TIMEOUT while testing successor generation"
    except:
        details = "A runtime error occurred while testing successor generation: %r" % traceback.format_exc()

    return passed, details

@max_grade(5)
def test_successors_collision_similar_names(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    passed = False
    details = ""

    board_size = (5,5)
    goal_entrance = (1,2)
    goal_direction = 'S'

    vehicles = [['carg',(1,3),4,False,True],
                ['car1',(2,4),2,True,False]]

    problem = sol_rushhour.make_init_state(board_size, vehicles,
                    goal_entrance, goal_direction)
    successors = comparable_successors(problem)

    try:
        setTO(timeout)

        stu_problem = stu_rushhour.make_init_state(board_size, vehicles,
                            goal_entrance, goal_direction)
        stu_successors = comparable_successors(stu_problem)

        if stu_successors == successors:
            passed = True
        else:
            details = "Error in successor generation (vehicles with similar names are overlapping?)"

        setTO(0)
    except TO_exc:
        details = "Got TIMEOUT while testing successor generation"
    except:
        details = "A runtime error occurred while testing successor generation: %r" % traceback.format_exc()

    return passed, details

@max_grade(5)
def test_goal_through_boundary(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    passed = False
    details = ""

    board_size = (5,5)
    goal_entrance = (0,0)
    goal_direction = 'E'

    vehicles = [['g',(4,0),2,True,True]]

    problem = sol_rushhour.make_init_state(board_size, vehicles,
                    goal_entrance, goal_direction)

    try:
        setTO(timeout)

        stu_problem = stu_rushhour.make_init_state(board_size, vehicles,
                            goal_entrance, goal_direction)

        if stu_rushhour.rushhour_goal_fn(stu_problem):
            passed = True
        else:
            details = "Goal function failed (with car passing through boundary)"

        setTO(0)
    except TO_exc:
        details = "Got TIMEOUT while testing goal function"
    except:
        details = "A runtime error occurred while testing goal function: %r" % traceback.format_exc()

    return passed, details

@max_grade(5)
def test_goal_multiple_goals(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    passed = False
    details = ""

    board_size = (5,5)
    goal_entrance = (0,0)
    goal_direction = 'W'

    vehicles = [['g',(0,0),2,True,True],
                ['x',(2,0),2,True,True]]

    problem = sol_rushhour.make_init_state(board_size, vehicles,
                    goal_entrance, goal_direction)

    try:
        setTO(timeout)

        stu_problem = stu_rushhour.make_init_state(board_size, vehicles,
                            goal_entrance, goal_direction)

        if stu_rushhour.rushhour_goal_fn(stu_problem):
            passed = True
        else:
            details = "Goal function failed (with multiple goal cars)"

        setTO(0)
    except TO_exc:
        details = "Got TIMEOUT while testing goal function"
    except:
        details = "A runtime error occurred while testing goal function: %r" % traceback.format_exc()

    return passed, details

@max_grade(2*len(PROBLEMS))
def test_heuristic_simple(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    score = 0
    details = set()

    for problem in PROBLEMS:
        board_size, goal_entrance, goal_direction = \
                problem.get_board_properties()
        vehicle_statuses = problem.get_vehicle_statuses()

        try:
            setTO(timeout)

            stu_problem = stu_rushhour.make_init_state(board_size,
                    vehicle_statuses, goal_entrance, goal_direction)

            if stu_rushhour.heur_min_moves(stu_problem) == \
                    sol_rushhour.heur_min_moves(problem):
                score += 2
            else:
                details.add("Error in heuristic evaluation: output from heuristic function doesn't match expected values")

            setTO(0)
        except TO_exc:
            details.add("Got TIMEOUT while testing heuristic function")
        except:
            details.add("A runtime error occurred while testing heuristic function: %r" % traceback.format_exc())

    details = "\n".join(details)
    return score, details

@max_grade(2*len(PROBLEMS_THREE_GOALS))
def test_heuristic_multiple_goal_cars(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    score = 0
    details = set()

    for problem in PROBLEMS_THREE_GOALS:
        board_size, goal_entrance, goal_direction = \
                problem.get_board_properties()
        vehicle_statuses = problem.get_vehicle_statuses()

        try:
            setTO(timeout)

            stu_problem = stu_rushhour.make_init_state(board_size,
                    vehicle_statuses, goal_entrance, goal_direction)

            if stu_rushhour.heur_min_moves(stu_problem) == \
                    sol_rushhour.heur_min_moves(problem):
                score += 2
            else:
                details.add("Error in heuristic evaluation (with multiple goal vehicles)")

            setTO(0)
        except TO_exc:
            details.add("Got TIMEOUT while testing heuristic function")
        except:
            details.add("A runtime error occurred while testing heuristic function: %r" % traceback.format_exc())

    details = "\n".join(details)
    return score, details

@max_grade(len(PROBLEMS_SEARCH))
def test_search(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    score = 0
    details = set()

    for problem in PROBLEMS_SEARCH:
        board_size, goal_entrance, goal_direction = \
                problem.get_board_properties()
        vehicle_statuses = problem.get_vehicle_statuses()

        try:
            setMEM(2048)
            search_engine = SearchEngine('astar')

            goal_state = search_engine.search(problem,
                    sol_rushhour.rushhour_goal_fn, sol_rushhour.heur_min_moves)

            setTO(timeout)

            stu_problem = stu_rushhour.make_init_state(board_size,
                    vehicle_statuses, goal_entrance, goal_direction)

            stu_goal_state = search_engine.search(stu_problem,
                    stu_rushhour.rushhour_goal_fn, stu_rushhour.heur_min_moves)

            if stu_goal_state.gval == goal_state.gval:
                score += 1
            else:
                if stu_goal_state.gval < goal_state.gval:
                    details.add("Error in search: found a solution that was too short")
                elif stu_goal_state.gval > goal_state.gval:
                    details.add("Error in search: found a solution that was too long")
                else:
                    details.add("Search failed. Did not find a solution?")

            setTO(0)
            del search_engine
            resetMEM()
        except MemoryError:
            try:
                del search_engine
            except:
                pass
            resetMEM()
            details.add("Got MemoryError while doing search")
        except TO_exc:
            details.add("Got TIMEOUT while doing search")
        except:
            details.add("A runtime error occurred while doing search: %r: " % traceback.format_exc())

        gc.collect()

    gc.collect()
    details = "\n".join(details)
    return score, details

@max_grade(10)
def test_search_no_solution(student_modules):
    stu_rushhour = student_modules[RUSHHOUR]
    timeout = DEFAULT_TIMEOUT
    passed = False
    details = ""

    board_size = (5,5)
    goal_entrance = (2,3)
    goal_direction = 'S'

    vehicles = [['gv',(2,4),3,False,True],
                ['1',(4,1),4,False,False],
                ['2',(0,2),4,True,False],
                ['3',(0,3),4,True,False]]

    try:
        setMEM(2048)
        setTO(timeout)
        problem = stu_rushhour.make_init_state(board_size, vehicles,
                goal_entrance, goal_direction)

        search_engine = SearchEngine('astar')

        goal_state = search_engine.search(problem, stu_rushhour.rushhour_goal_fn, stu_rushhour.heur_min_moves)

        if goal_state is False:
            passed = True
        else:
            details = "Error in search: did not recognize unsolvable problem"
        setTO(0)
        del search_engine
        resetMEM()
    except MemoryError:
        try:
            del search_engine
        except:
            pass
        resetMEM()
        details = "Got MemoryError while doing search (with unsolvable problem)"
    except TO_exc:
        details = "Got TIMEOUT while doing search (with unsolvable problem)"
    except:
        details = "A runtime error occurred while doing search (with unsolvable problem): %r" % traceback.format_exc()

    try:
        del search_engine
    except:
        pass
    gc.collect()

    return passed, details
